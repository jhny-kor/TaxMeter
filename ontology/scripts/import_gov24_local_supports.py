#!/usr/bin/env python3
"""Import local-government support programs from Gov24 Benefit Plus.

The generated file is intentionally source-first. Each support node keeps the
Gov24 detail URL, service identifiers, source modified date, collection date,
jurisdiction, application deadline text, and law/local-ordinance links when
Gov24 exposes them. This lets future refreshes detect removed or changed local
support programs without relying on ungrounded summaries.
"""

from __future__ import annotations

import argparse
import concurrent.futures
import datetime as dt
import html
import json
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "custom" / "gov24-local-supports.generated.json"
API_URL = "https://plus.gov.kr/api/portal/v1.0/api/benefitPlus"
LIST_URL = "https://plus.gov.kr/portal/benefitV2/benefitTotalSrvcList"
DETAIL_URL = "https://plus.gov.kr/portal/benefitV2/benefitTotalSrvcList/benefitSrvcDtl"
SOURCE_ID = "source.gov24.benefit-plus.local-supports"
LOCAL_SUPPORT_CATEGORY_ID = "category.local-government-supports"

LOCAL_REGION_NAMES = (
    "서울특별시",
    "부산광역시",
    "대구광역시",
    "인천광역시",
    "광주광역시",
    "대전광역시",
    "울산광역시",
    "세종특별자치시",
    "경기도",
    "강원특별자치도",
    "충청북도",
    "충청남도",
    "전북특별자치도",
    "전라남도",
    "경상북도",
    "경상남도",
    "제주특별자치도",
)

REQUEST_METHOD_LABELS = {
    "00": "온라인",
    "01": "온오프라인",
    "02": "방문",
    "03": "기타",
}


def clean_text(value: Any) -> str:
    if value is None:
        return ""
    text = html.unescape(str(value))
    text = re.sub(r"<br\s*/?>", "\n", text, flags=re.IGNORECASE)
    text = re.sub(r"<[^>]+>", " ", text)
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def post_form(params: dict[str, str], retries: int = 3, timeout: int = 30) -> dict[str, Any]:
    body = urllib.parse.urlencode(params).encode("utf-8")
    request = urllib.request.Request(
        API_URL,
        data=body,
        headers={
            "Content-Type": "application/x-www-form-urlencoded",
            "User-Agent": "OpenTax/1.0 Gov24 local-support importer",
            "Referer": LIST_URL,
        },
        method="POST",
    )
    last_error: Exception | None = None
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:
                return json.loads(response.read().decode("utf-8"))
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as error:
            last_error = error
            time.sleep(0.5 * (attempt + 1))
    raise RuntimeError(f"Gov24 API request failed: {params}") from last_error


def fetch_conditions() -> list[dict[str, Any]]:
    data = post_form({"apiDtlUrl": "selectSearchCndList", "wrkCd": "BNEF"})
    if data.get("rspCode") != "0":
        raise RuntimeError(f"Gov24 search condition request failed: {data.get('rspMsg')}")
    return data.get("benefitCtprvnItmList") or []


def fetch_list_page(region_name: str, page: int) -> dict[str, Any]:
    return post_form(
        {
            "apiDtlUrl": "selectPbnsvcList",
            "srchwrd": "",
            "sggNm": region_name,
            "svcFdCd": "",
            "sittnCd": "",
            "pageIndex": str(page),
            "srtOdr": "KO",
        }
    )


def fetch_region_rows(region_name: str, max_pages: int | None = None, workers: int = 4) -> list[dict[str, Any]]:
    first = fetch_list_page(region_name, 1)
    if first.get("rspCode") != "0":
        raise RuntimeError(f"Gov24 list request failed for {region_name}: {first.get('rspMsg')}")
    total_pages = int(first.get("totalPages") or 1)
    if max_pages:
        total_pages = min(total_pages, max_pages)
    rows = [dict(row, source_region=region_name) for row in first.get("benefitPbnsvcList") or []]
    if total_pages <= 1:
        return rows
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
        future_map = {executor.submit(fetch_list_page, region_name, page): page for page in range(2, total_pages + 1)}
        for future in concurrent.futures.as_completed(future_map):
            data = future.result()
            rows.extend(dict(row, source_region=region_name) for row in data.get("benefitPbnsvcList") or [])
    return rows


def fetch_detail(row: dict[str, Any]) -> dict[str, Any] | None:
    params = {
        "apiDtlUrl": "selectBnefReqstDtl",
        "svcSeq": str(row["svcSeq"]),
        "bnefType": "all",
    }
    if row.get("svcId"):
        params["svcId"] = str(row["svcId"])
    data = post_form(params)
    details = data.get("benefitBnefRequsDtlList") or []
    if not details:
        return None
    detail = details[0]
    detail["source_region"] = row.get("source_region") or ""
    return detail


def is_local_support(detail: dict[str, Any]) -> bool:
    jurisdiction = clean_text(detail.get("jrsdOrg"))
    return any(region in jurisdiction for region in LOCAL_REGION_NAMES)


def detail_page_url(detail: dict[str, Any]) -> str:
    query = {
        "svcSeq": detail.get("svcSeq") or "",
        "bnefType": "all",
        "svcId": detail.get("svcId") or "",
    }
    return DETAIL_URL + "?" + urllib.parse.urlencode(query)


def parse_expiration_date(text: str) -> str | None:
    candidates = re.findall(r"(20\d{2})[.\-/년 ]\s*(\d{1,2})[.\-/월 ]\s*(\d{1,2})", text)
    if not candidates:
        return None
    year, month, day = candidates[-1]
    try:
        return dt.date(int(year), int(month), int(day)).isoformat()
    except ValueError:
        return None


def criterion(label: str, basis: str, condition: str, *, kind: str, detail_key: str, detail_value: str) -> dict[str, Any]:
    result = {
        "label": label,
        "basis": basis,
        "condition": condition or "정부24 상세 원문 확인",
        "source": SOURCE_ID,
        "criteria_kind": kind,
        "basis_category": "local-government-support",
        "basis_definition": "지방자치단체가 보조금24에 등록한 지원금의 대상, 선정기준, 신청기한, 지원내용 기준입니다.",
        "basis_lookup": "정부24 보조금24 상세 페이지의 지원대상, 선정기준, 신청기한, 지원내용, 제출서류, 관할기관, 수정일을 확인합니다.",
        "selection_rule": "사용자 조건이 지원대상과 선정기준에 맞고 신청기한 내 필요서류를 제출할 수 있으면 후보 지원금으로 분류합니다.",
        "basis_source": SOURCE_ID,
    }
    result[detail_key] = detail_value
    return result


def build_criteria(detail: dict[str, Any]) -> list[dict[str, Any]]:
    criteria: list[dict[str, Any]] = []
    target = clean_text(detail.get("sportTg"))
    if target:
        criteria.append(
            criterion(
                "지원대상",
                "지원대상",
                target,
                kind="eligibility",
                detail_key="amount_applicability",
                detail_value="지원대상 자체는 정액 금액 기준이 아니며, 금액은 지원내용 원문을 확인합니다.",
            )
        )
    selection = clean_text(detail.get("slctnStdr"))
    if selection:
        criteria.append(
            criterion(
                "선정기준",
                "선정기준",
                selection,
                kind="eligibility",
                detail_key="amount_applicability",
                detail_value="선정기준 자체는 정액 금액 기준이 아니며, 세부 기준은 원문 문구를 확인합니다.",
            )
        )
    deadline = clean_text(detail.get("reqstTmlmt"))
    if deadline:
        criteria.append(
            criterion(
                "신청기한",
                "신청기한",
                deadline,
                kind="deadline",
                detail_key="deadline_rule",
                detail_value=deadline,
            )
        )
    benefit = clean_text(detail.get("svcCts")) or clean_text(detail.get("svcIntrcnCts"))
    support_type = clean_text(detail.get("sportFr"))
    benefit_condition = benefit or support_type or "정부24 상세 원문 확인"
    criteria.append(
        criterion(
            "지원내용",
            "지원내용",
            benefit_condition,
            kind="reference",
            detail_key="amount_applicability",
            detail_value="정액·정률·한도 금액은 지자체 원문 지원내용에 명시된 경우에만 적용합니다.",
        )
    )
    return criteria


def build_legal_basis(detail: dict[str, Any]) -> list[dict[str, str]]:
    result: list[dict[str, str]] = []
    for basis in detail.get("benefitLsBasis") or []:
        title = clean_text(basis.get("lsKoNm"))
        url = clean_text(basis.get("extrlLinkUrl"))
        if not title and not url:
            continue
        entry = {
            "title": title or url,
            "kind": clean_text(basis.get("lsKndNm")) or "법령·자치법규",
            "url": url,
            "promulgation_date": clean_text(basis.get("ancDt")),
        }
        result.append(entry)
    return result


def build_item(detail: dict[str, Any], collected_at: str) -> dict[str, Any]:
    service_seq = clean_text(detail.get("svcSeq"))
    service_id = clean_text(detail.get("svcId"))
    jurisdiction = clean_text(detail.get("jrsdOrg"))
    name = clean_text(detail.get("svcNm"))
    title = f"{name} ({jurisdiction})" if jurisdiction else name
    status_url = detail_page_url(detail)
    legal_basis = build_legal_basis(detail)
    source_urls = [status_url]
    for basis in legal_basis:
        if basis.get("url"):
            source_urls.append(basis["url"])
    esite_url = clean_text(detail.get("esiteUrl"))
    if esite_url.startswith("http"):
        source_urls.append(esite_url)
    mod_date = clean_text(detail.get("modDh"))
    deadline_text = clean_text(detail.get("reqstTmlmt"))
    application_method = clean_text(detail.get("reqstProcssType")) or REQUEST_METHOD_LABELS.get(clean_text(detail.get("reqstMeanCls")), "")
    intro = clean_text(detail.get("svcIntrcnCts"))
    description = f"{jurisdiction} 관할 지자체 지원금입니다. {intro}" if intro else f"{jurisdiction} 관할 지자체 지원금입니다."
    source_basis_dates = [f"정부24 원문 수정일 {mod_date}" if mod_date else f"정부24 원문 수집일 {collected_at}", f"수집일 {collected_at}"]
    support_type = clean_text(detail.get("sportFr"))
    tags = ["local-government-support", "gov24", "generated"]
    if support_type:
        tags.append(support_type)
    return {
        "id": f"support.local-gov.gov24.{service_seq}",
        "title": title,
        "type": "support-program",
        "description": description,
        "folder": "30_Supports/LocalGovernment",
        "basis_year": 2026,
        "expiration_date": parse_expiration_date(deadline_text),
        "reviewed_at": collected_at,
        "source_urls": list(dict.fromkeys(source_urls)),
        "source_basis_dates": list(dict.fromkeys(source_basis_dates)),
        "abolition_status": "active",
        "revision_status": "check_source",
        "parents": [LOCAL_SUPPORT_CATEGORY_ID],
        "related": [LOCAL_SUPPORT_CATEGORY_ID],
        "terms": ["term.local-government-support"],
        "sources": [SOURCE_ID],
        "criteria": build_criteria(detail),
        "tags": tags,
        "jurisdiction": jurisdiction,
        "jurisdiction_code": clean_text(detail.get("source_region")),
        "gov24_service_id": service_id,
        "gov24_service_seq": service_seq,
        "source_record_id": service_seq,
        "source_modified_at": mod_date,
        "source_collected_at": collected_at,
        "status_check_url": status_url,
        "application_deadline_text": deadline_text,
        "application_method": application_method,
        "application_process": clean_text(detail.get("reqstProcss")),
        "receiving_agency": clean_text(detail.get("rcvOrgNm")),
        "contact": clean_text(detail.get("refrncNm")) or clean_text(detail.get("refrncTelNo")),
        "required_documents_text": clean_text(detail.get("posesPapers")),
        "legal_basis": legal_basis,
    }


def collect_rows(regions: list[dict[str, Any]], max_pages: int | None, limit: int | None = None, list_workers: int = 4) -> dict[str, dict[str, Any]]:
    rows_by_seq: dict[str, dict[str, Any]] = {}
    for region in regions:
        region_name = region["cdNm"]
        region_max_pages = max_pages
        if limit:
            remaining = max(limit - len(rows_by_seq), 0)
            if remaining == 0:
                return rows_by_seq
            needed_pages = max(1, (remaining + 9) // 10)
            region_max_pages = min(region_max_pages, needed_pages) if region_max_pages else needed_pages
        for row in fetch_region_rows(region_name, max_pages=region_max_pages, workers=list_workers):
            service_seq = str(row.get("svcSeq") or "")
            if service_seq and service_seq not in rows_by_seq:
                rows_by_seq[service_seq] = row
                if limit and len(rows_by_seq) >= limit:
                    return rows_by_seq
    return rows_by_seq


def collect_details(rows: list[dict[str, Any]], workers: int) -> list[dict[str, Any]]:
    details: list[dict[str, Any]] = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
        future_map = {executor.submit(fetch_detail, row): row for row in rows}
        for future in concurrent.futures.as_completed(future_map):
            row = future_map[future]
            try:
                detail = future.result()
            except Exception as error:
                print(f"warning: detail fetch failed for svcSeq={row.get('svcSeq')}: {error}")
                continue
            if detail and is_local_support(detail):
                details.append(detail)
    return details


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=OUTPUT)
    parser.add_argument("--collected-at", default=dt.date.today().isoformat())
    parser.add_argument("--max-pages-per-region", type=int)
    parser.add_argument("--limit", type=int, help="Limit unique list rows after region collection; intended for tests.")
    parser.add_argument("--list-workers", type=int, default=4)
    parser.add_argument("--workers", type=int, default=8)
    args = parser.parse_args()

    regions = fetch_conditions()
    if not regions:
        raise RuntimeError("No Gov24 region filters returned.")
    rows_by_seq = collect_rows(regions, max_pages=args.max_pages_per_region, limit=args.limit, list_workers=args.list_workers)
    rows = sorted(rows_by_seq.values(), key=lambda row: int(row.get("svcSeq") or 0))
    details = collect_details(rows, workers=args.workers)
    items = [build_item(detail, args.collected_at) for detail in sorted(details, key=lambda value: int(value.get("svcSeq") or 0))]
    payload = {
        "generated_at": args.collected_at,
        "source": LIST_URL,
        "source_api": API_URL,
        "region_count": len(regions),
        "unique_list_rows": len(rows_by_seq),
        "imported_local_support_count": len(items),
        "items": items,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {len(items)} Gov24 local support nodes to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
