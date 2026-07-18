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

from support_deadline_parser import classify_deadline, parse_application_dates


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "custom" / "gov24-local-supports.generated.json"
API_URL = "https://plus.gov.kr/api/portal/v1.0/api/benefitPlus"
LIST_URL = "https://plus.gov.kr/portal/benefitV2/benefitTotalSrvcList"
DETAIL_URL = "https://plus.gov.kr/portal/benefitV2/benefitTotalSrvcList/benefitSrvcDtl"
SOURCE_ID = "source.gov24.benefit-plus.local-supports"
LOCAL_SUPPORT_CATEGORY_ID = "category.local-government-supports"

CURRENT_REGION_NAMES = (
    "서울특별시",
    "부산광역시",
    "대구광역시",
    "인천광역시",
    "대전광역시",
    "울산광역시",
    "세종특별자치시",
    "경기도",
    "강원특별자치도",
    "충청북도",
    "충청남도",
    "전북특별자치도",
    "전남광주통합특별시",
    "경상북도",
    "경상남도",
    "제주특별자치도",
)

REGION_ALIASES = {
    "광주광역시": "전남광주통합특별시",
    "전라남도": "전남광주통합특별시",
}
REGION_TRANSITION_SOURCE = "https://www.mois.go.kr/frt/bbs/type010/commonSelectBoardArticle.do?bbsId=BBSMSTR_000000000008&nttId=126845"


def region_metadata(region_name: str) -> dict[str, Any]:
    predecessors = sorted(alias for alias, current in REGION_ALIASES.items() if current == region_name)
    return {
        "region_code": region_name,
        "predecessor_region_codes": predecessors,
        "region_aliases": [region_name, *predecessors],
        "administrative_effective_from": "2026-07-01" if predecessors else None,
        "administrative_transition_source": REGION_TRANSITION_SOURCE if predecessors else None,
        "parent_jurisdiction_code": "대한민국",
        "administrative_history": [
            {
                "jurisdiction_code": alias,
                "effective_to": "2026-06-30",
                "source_url": REGION_TRANSITION_SOURCE,
            }
            for alias in predecessors
        ],
    }

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


def support_fields(detail: dict[str, Any]) -> tuple[list[str], list[str]]:
    text = " ".join(
        clean_text(detail.get(key))
        for key in ("svcNm", "svcIntrcnCts", "trgterIndvdl", "slctnCritCn", "sportFr")
    )
    target_group = [
        label
        for token, label in (("청년", "youth"), ("청소년", "youth"), ("신혼", "newlywed"), ("임산부", "pregnant"), ("장애", "disabled"), ("노인", "senior"), ("고령", "senior"), ("아동", "child"), ("한부모", "single_parent"), ("1인가구", "single_person_household"), ("저소득", "low_income"), ("구직", "job_seeker"), ("취업준비", "job_seeker"), ("피해", "victim"))
        if token in text
    ]
    support_category = [
        label
        for token, label in (("월세", "rent"), ("임차료", "rent"), ("전세", "lease_deposit"), ("주거", "housing"), ("임대", "housing"), ("보증금", "deposit_guarantee"), ("보증", "deposit_guarantee"), ("공급", "housing_supply"), ("수선", "housing_repair"), ("취업", "employment"), ("일자리", "employment"), ("창업", "business"), ("사업", "business"), ("출산", "family"), ("보육", "family"), ("의료", "health"), ("건강", "health"), ("교육", "education"), ("문화", "culture"), ("예술", "culture"), ("현금", "cash_support"), ("생활비", "cash_support"))
        if token in text
    ]
    if any(value in support_category for value in ("rent", "lease_deposit", "deposit_guarantee", "housing_supply", "housing_repair")):
        support_category.append("housing")
    return sorted(set(target_group)), sorted(set(support_category))


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


def fetch_conditions() -> tuple[list[dict[str, Any]], set[str]]:
    expected = set(CURRENT_REGION_NAMES)
    last_regions: list[dict[str, Any]] = []
    last_names: set[str] = set()
    for attempt in range(3):
        try:
            data = post_form({"apiDtlUrl": "selectSearchCndList", "wrkCd": "BNEF"})
        except RuntimeError:
            if attempt < 2:
                time.sleep(attempt + 1)
                continue
            raise
        if data.get("rspCode") != "0":
            raise RuntimeError(f"Gov24 search condition request failed: {data.get('rspMsg')}")
        regions = data.get("benefitCtprvnItmList") or []
        names = {clean_text(region.get("cdNm")) for region in regions}
        missing = expected - names
        if not missing:
            return regions, set()
        last_regions = regions
        last_names = names
        if attempt < 2:
            time.sleep(attempt + 1)
    if last_regions:
        return last_regions, expected - last_names
    raise RuntimeError("Gov24 search conditions returned no regions.")


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


def fetch_region_rows(region_name: str, max_pages: int | None = None, workers: int = 4) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    first = fetch_list_page(region_name, 1)
    if first.get("rspCode") != "0":
        raise RuntimeError(f"Gov24 list request failed for {region_name}: {first.get('rspMsg')}")
    source_total_pages = int(first.get("totalPages") or 1)
    total_pages = source_total_pages
    if max_pages:
        total_pages = min(total_pages, max_pages)
    rows = [dict(row, source_region=region_name) for row in first.get("benefitPbnsvcList") or []]
    if total_pages <= 1:
        return rows, {
            "region_code": region_name,
            "source_response_status": 200,
            "source_total_pages": source_total_pages,
            "collected_pages": 1,
            "list_row_count": len(rows),
        }
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
        future_map = {executor.submit(fetch_list_page, region_name, page): page for page in range(2, total_pages + 1)}
        for future in concurrent.futures.as_completed(future_map):
            data = future.result()
            rows.extend(dict(row, source_region=region_name) for row in data.get("benefitPbnsvcList") or [])
    return rows, {
        "region_code": region_name,
        "source_response_status": 200,
        "source_total_pages": source_total_pages,
        "collected_pages": total_pages,
        "list_row_count": len(rows),
    }


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
    return any(region in jurisdiction for region in (*CURRENT_REGION_NAMES, *REGION_ALIASES))


def detail_page_url(detail: dict[str, Any]) -> str:
    query = {
        "svcSeq": detail.get("svcSeq") or "",
        "bnefType": "all",
        "svcId": detail.get("svcId") or "",
    }
    return DETAIL_URL + "?" + urllib.parse.urlencode(query)


def support_status_fields(deadline_text: str, application_open_to: str | None, reviewed_at: str) -> dict[str, Any]:
    compact_deadline = deadline_text.replace(" ", "")
    if any(marker in compact_deadline for marker in ("신청불필요", "신청불요", "개인신청절차없음", "별도신청절차없음")):
        return {
            "status": "active",
            "application_status": "not_required",
            "status_reason": "정부24 원문에 별도 신청 절차가 필요 없다고 표시되어 있습니다.",
            "status_confidence": "derived",
        }
    if "상시" in compact_deadline:
        return {
            "status": "active",
            "application_status": "always_open",
            "status_reason": "정부24 신청기한이 상시신청으로 표시되어 있습니다.",
            "status_confidence": "confirmed",
        }
    if application_open_to:
        if application_open_to < reviewed_at:
            return {
                "status": "closed",
                "application_status": "closed",
                "status_reason": f"정부24 신청기한 {application_open_to}이 현재 검토일 {reviewed_at}보다 이전입니다.",
                "status_confidence": "derived",
            }
        return {
            "status": "active",
            "application_status": "open",
            "status_reason": f"정부24 신청기한 {application_open_to}이 현재 검토일 {reviewed_at} 이후입니다.",
            "status_confidence": "derived",
        }
    unknown_reason = classify_deadline(deadline_text)
    return {
        "status": "unknown",
        "application_status": "unknown",
        "status_reason": "신청기한 원문을 날짜 또는 상시신청으로 해석할 수 없어 원문 확인이 필요합니다.",
        "status_confidence": "unverified",
        "unknown_reason": unknown_reason,
    }


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
    regional_metadata = region_metadata(clean_text(detail.get("source_region")))
    target_group, support_category = support_fields(detail)
    application_open_from, application_open_to = parse_application_dates(deadline_text, collected_at)
    status_fields = support_status_fields(deadline_text, application_open_to, collected_at)
    abolition_status = {
        "active": "active",
        "closed": "sunset",
        "unknown": "unknown",
    }[status_fields["status"]]
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
        "expiration_date": application_open_to,
        "reviewed_at": collected_at,
        "source_urls": list(dict.fromkeys(source_urls)),
        "source_basis_dates": list(dict.fromkeys(source_basis_dates)),
        "abolition_status": abolition_status,
        "revision_status": "check_source",
        "parents": [LOCAL_SUPPORT_CATEGORY_ID],
        "related": [],
        "terms": ["term.local-government-support"],
        "sources": [SOURCE_ID],
        "criteria": build_criteria(detail),
        "tags": tags,
        "jurisdiction": jurisdiction,
        "jurisdiction_code": regional_metadata["region_code"],
        "jurisdiction_predecessor_codes": regional_metadata["predecessor_region_codes"],
        "jurisdiction_aliases": regional_metadata["region_aliases"],
        "parent_jurisdiction_code": regional_metadata["parent_jurisdiction_code"],
        "administrative_history": regional_metadata["administrative_history"],
        "administrative_effective_from": regional_metadata["administrative_effective_from"],
        "administrative_transition_source": regional_metadata["administrative_transition_source"],
        "gov24_service_id": service_id,
        "gov24_service_seq": service_seq,
        "source_record_id": service_seq,
        "source_modified_at": mod_date,
        "source_collected_at": collected_at,
        "effective_from": None,
        "effective_to": application_open_to if status_fields["status"] == "closed" else None,
        "application_open_from": application_open_from,
        "application_open_to": application_open_to,
        "last_verified_at": collected_at,
        "last_status_checked_at": collected_at,
        "target_group": target_group,
        "support_category": support_category,
        "collection_status": "collected_current",
        "last_successful_collected_at": collected_at,
        "current_refresh_attempted_at": collected_at,
        "current_refresh_succeeded": True,
        "freshness_status": "current",
        **status_fields,
        "status_check_url": status_url,
        "application_deadline_text": deadline_text,
        "application_method": application_method,
        "application_process": clean_text(detail.get("reqstProcss")),
        "receiving_agency": clean_text(detail.get("rcvOrgNm")),
        "contact": clean_text(detail.get("refrncNm")) or clean_text(detail.get("refrncTelNo")),
        "required_documents_text": clean_text(detail.get("posesPapers")),
        "legal_basis": legal_basis,
    }


def collect_rows(regions: list[dict[str, Any]], max_pages: int | None, limit: int | None = None, list_workers: int = 4) -> tuple[dict[str, dict[str, Any]], list[dict[str, Any]]]:
    rows_by_seq: dict[str, dict[str, Any]] = {}
    collection_evidence: list[dict[str, Any]] = []
    for region in regions:
        region_name = region["cdNm"]
        region_max_pages = max_pages
        if limit:
            remaining = max(limit - len(rows_by_seq), 0)
            if remaining == 0:
                return rows_by_seq, collection_evidence
            needed_pages = max(1, (remaining + 9) // 10)
            region_max_pages = min(region_max_pages, needed_pages) if region_max_pages else needed_pages
        region_rows, evidence = fetch_region_rows(region_name, max_pages=region_max_pages, workers=list_workers)
        collection_evidence.append({**region_metadata(region_name), **evidence})
        for row in region_rows:
            service_seq = str(row.get("svcSeq") or "")
            if service_seq and service_seq not in rows_by_seq:
                rows_by_seq[service_seq] = row
                if limit and len(rows_by_seq) >= limit:
                    return rows_by_seq, collection_evidence
    return rows_by_seq, collection_evidence


def collect_details(rows: list[dict[str, Any]], workers: int) -> list[dict[str, Any]]:
    details: list[dict[str, Any]] = []
    failures: list[str] = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
        future_map = {executor.submit(fetch_detail, row): row for row in rows}
        for future in concurrent.futures.as_completed(future_map):
            row = future_map[future]
            try:
                detail = future.result()
            except Exception as error:
                failures.append(f"svcSeq={row.get('svcSeq')}: {error}")
                continue
            if detail is None:
                failures.append(f"svcSeq={row.get('svcSeq')}: empty detail response")
                continue
            if detail and is_local_support(detail):
                details.append(detail)
    if failures:
        raise RuntimeError("Gov24 detail fetch failed; prior snapshot is retained: " + "; ".join(failures[:10]))
    return details


def preserved_items_for_missing_regions(output: Path, missing_regions: set[str]) -> list[dict[str, Any]]:
    if not missing_regions or not output.exists():
        return []
    try:
        existing = json.loads(output.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise RuntimeError(f"Cannot preserve Gov24 rows for unavailable regions from {output}") from error
    items = [
        item
        for item in existing.get("items") or []
        if item.get("jurisdiction_code") in missing_regions
    ]
    return items


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=OUTPUT)
    parser.add_argument("--collected-at", default=dt.date.today().isoformat())
    parser.add_argument("--max-pages-per-region", type=int)
    parser.add_argument("--limit", type=int, help="Limit unique list rows after region collection; intended for tests.")
    parser.add_argument("--list-workers", type=int, default=4)
    parser.add_argument("--workers", type=int, default=8)
    args = parser.parse_args()

    regions, missing_regions = fetch_conditions()
    if not regions:
        raise RuntimeError("No Gov24 region filters returned.")
    rows_by_seq, collection_evidence = collect_rows(regions, max_pages=args.max_pages_per_region, limit=args.limit, list_workers=args.list_workers)
    rows = sorted(rows_by_seq.values(), key=lambda row: int(row.get("svcSeq") or 0))
    details = collect_details(rows, workers=args.workers)
    items = [build_item(detail, args.collected_at) for detail in sorted(details, key=lambda value: int(value.get("svcSeq") or 0))]
    preserved_items = preserved_items_for_missing_regions(args.output, missing_regions)
    preserved_regions = {str(item.get("jurisdiction_code")) for item in preserved_items}
    for item in preserved_items:
        item.update(
            {
                "collection_status": "preserved_snapshot",
                "last_successful_collected_at": item.get("source_collected_at") or item.get("last_successful_collected_at"),
                "current_refresh_attempted_at": args.collected_at,
                "current_refresh_succeeded": False,
                "freshness_status": "stale",
                "recommendation_status": "reference_only",
            }
        )
    items = [*items, *preserved_items]
    payload = {
        "generated_at": args.collected_at,
        "source": LIST_URL,
        "source_api": API_URL,
        "region_count": len(regions) + len(missing_regions),
        "unique_list_rows": len(rows_by_seq),
        "imported_local_support_count": len(items),
        "source_refresh_missing_regions": sorted(missing_regions),
        "unpreserved_missing_regions": sorted(missing_regions - preserved_regions),
        "current_refresh_complete": not missing_regions,
        "preserved_from_previous_snapshot_count": len(preserved_items),
        "region_collection_evidence": collection_evidence,
        "items": items,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {len(items)} Gov24 local support nodes to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
