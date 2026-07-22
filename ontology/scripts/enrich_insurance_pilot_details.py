#!/usr/bin/env python3
from __future__ import annotations

import argparse
import concurrent.futures
import json
import re
import subprocess
import tempfile
import urllib.request
from datetime import date
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
INSURANCE_PATH = ROOT / "custom" / "finance" / "insurance-products.generated.json"
DETAILS_PATH = ROOT / "custom" / "finance" / "insurance-pilot-details.json"
REQUIRED_FIELDS = (
    "coverage_names", "coverage_amount_krw", "claim_condition", "exclusion_condition",
    "insured_age_min", "insured_age_max", "insurance_term", "payment_term", "premium_basis",
    "renewal_type", "waiting_period_days", "reduction_period_days", "surrender_refund_type",
)


def present(value: Any) -> bool:
    return value not in (None, "", [], {}, "unknown", "unverified", "listed_unverified")


def unique(values: list[str]) -> list[str]:
    return list(dict.fromkeys(value for value in values if value))


def section(text: str) -> str:
    match = re.search(r"보험기간.{0,80}(?:보험료|피보험자)", text)
    return text[match.start(): match.start() + 30000] if match else text[:30000]


def parse_days(text: str, label: str) -> int | None:
    match = re.search(rf"{label}[\s\S]{{0,120}}?(\d+)\s*(일|개월|년)", text)
    if match:
        value = int(match.group(1))
        return value * {"일": 1, "개월": 30, "년": 365}[match.group(2)]
    if re.search(rf"{label}[\s\S]{{0,120}}?(?:없음|없습니다|적용하지 않)", text):
        return 0
    return None


def parse_pdf(text: str) -> dict[str, Any]:
    table = section(text)
    ages = [
        (int(start), int(end))
        for start, end in re.findall(r"(?:만\s*)?(\d+)\s*(?:세)?\s*[~∼-]\s*(?:만\s*)?(\d+)\s*세", table)
        if int(start) <= int(end)
    ]
    age_section = text[text.find("가입나이"):] if "가입나이" in text else table
    if not ages:
        minimum = re.search(r"가입최저나이[^\d]{0,40}(\d+)\s*세", age_section)
        nearby = re.findall(r"(\d+)\s*세", age_section[:4000])
        if minimum and nearby:
            ages = [(int(minimum.group(1)), max(int(value) for value in nearby))]
    terms = unique(re.findall(r"(?:\d+\s*세|종신)(?=\s|$)", table))
    payment_terms = unique([f"{value}년납" for value in re.findall(r"(\d+)\s*년납", table)] + (["전기납"] if "전기납" in table else []))
    exclusions: list[str] = []
    for pattern in (r"보험금을 지급하지 않는 사유", r"보험금 지급제한 사유", r"보험금을 지급하지 않는 보험사고", r"보장하지 않는", r"보장하지 아니하는", r"면책사유"):
        match = re.search(pattern, text)
        if match:
            excerpt = re.sub(r"\s+", " ", text[match.start(): match.start() + 500]).strip()
            exclusions.append(excerpt)
            break
    fields: dict[str, Any] = {}
    if ages:
        fields["insured_age_min"] = min(start for start, _ in ages)
        fields["insured_age_max"] = max(end for _, end in ages)
    if terms:
        fields["insurance_term"] = " / ".join(terms)
    if payment_terms:
        fields["payment_term"] = " / ".join(payment_terms)
    if exclusions:
        fields["exclusion_condition"] = exclusions[0]
    coverage_amount = re.search(r"(?:보험가입금액|가입금액|보장금액|보험금액)[^\d]{0,30}([\d,]+)\s*(만원|억원|원)", text)
    if coverage_amount:
        amount = int(coverage_amount.group(1).replace(",", ""))
        fields["coverage_amount_krw"] = amount * {"만원": 10_000, "억원": 100_000_000, "원": 1}[coverage_amount.group(2)]
    claim = re.search(r"(?:보험금 지급사유|보험금 지급조건|지급사유|보장내용)[\s:：-]{0,20}([^\n]{10,240})", text)
    if claim:
        fields["claim_condition"] = re.sub(r"\s+", " ", claim.group(1)).strip()
    premium = re.search(r"(?:보험료 산출기초|보험료 납입|보험료)[\s:：-]{0,20}([^\n]{10,240})", text)
    if premium:
        fields["premium_basis"] = re.sub(r"\s+", " ", premium.group(1)).strip()
    if "갱신형" in text:
        fields["renewal_type"] = "renewable"
    elif "비갱신형" in text or "갱신되지" in text:
        fields["renewal_type"] = "non_renewable"
    coverage_lines = []
    for line in re.split(r"\n+", text):
        compact = re.sub(r"\s+", " ", line).strip()
        if 4 <= len(compact) <= 100 and any(token in compact for token in ("사망", "진단", "수술", "입원", "장해", "치료")):
            coverage_lines.append(compact)
    if coverage_lines:
        fields["coverage_names"] = unique(coverage_lines[:12])
    refund = re.search(r"해약환급금\s*(미지급|일부지급|보증|미보증)[^\n]{0,20}", text)
    if refund:
        fields["surrender_refund_type"] = refund.group(0).strip()
    waiting = parse_days(text, "면책기간")
    reduction = parse_days(text, "감액기간")
    if waiting is not None:
        fields["waiting_period_days"] = waiting
    if reduction is not None:
        fields["reduction_period_days"] = reduction
    return fields


def fetch_and_parse(item: dict[str, Any], timeout: int) -> dict[str, Any] | None:
    url = str(item.get("official_document_url") or "")
    if not url:
        return None
    try:
        request = urllib.request.Request(url, headers={"User-Agent": "OpenFin-official-detail-enricher/1.0"})
        with urllib.request.urlopen(request, timeout=timeout) as response:
            data = response.read()
        with tempfile.TemporaryDirectory(prefix="openfin-insurance-") as directory:
            pdf = Path(directory) / "source.pdf"
            text_path = Path(directory) / "source.txt"
            pdf.write_bytes(data)
            subprocess.run(["pdftotext", "-layout", str(pdf), str(text_path)], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            text = text_path.read_text(encoding="utf-8", errors="replace")
        return {
            "id": item["id"],
            "source": "official_klia_product_summary_pdf",
            "source_url": url,
            "captured_at": date.today().isoformat(),
            "fields": parse_pdf(text),
        }
    except (OSError, ValueError, subprocess.SubprocessError, urllib.error.URLError):
        return None


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--timeout", type=int, default=30)
    parser.add_argument("--workers", type=int, default=8)
    parser.add_argument("--limit", type=int, default=20)
    args = parser.parse_args()
    payload = json.loads(INSURANCE_PATH.read_text(encoding="utf-8"))
    items = [item for item in payload.get("items") or [] if item.get("type") == "insurance-product"]
    fields = REQUIRED_FIELDS
    candidates = sorted(
        items,
        key=lambda item: (sum(present(item.get(field)) for field in fields), str(item.get("id"))),
    )[: args.limit]
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as executor:
        details = [detail for detail in executor.map(lambda item: fetch_and_parse(item, args.timeout), candidates) if detail]
    if len(details) < args.limit:
        raise SystemExit(f"official insurance PDF parse pilot incomplete: {len(details)}/{args.limit}")
    DETAILS_PATH.write_text(json.dumps({
        "version": "KR-FINANCE-INSURANCE-PILOT-DETAILS-2026.07.18.1",
        "source": "생명보험협회 상품요약서 PDF",
        "items": details,
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {DETAILS_PATH.relative_to(ROOT.parent)}: {len(details)} official PDF details")
    print("parsed_field_counts=" + json.dumps({field: sum(field in detail["fields"] for detail in details) for field in fields}, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
