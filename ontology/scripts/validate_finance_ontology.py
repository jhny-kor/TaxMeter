#!/usr/bin/env python3
"""Validate split finance ontology exports and manifest."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EXPORT_DIR = ROOT / "exports"
MANIFEST = EXPORT_DIR / "finance-ontology-manifest.json"
SEARCH_INDEX = EXPORT_DIR / "finance-search-index-2026.json"

REFERENCE_KEYS = ("parents", "children", "related", "terms", "deadlines", "sources")
PRODUCT_TYPES = {"card-product", "bank-product", "insurance-product"}
VALID_OPERATIONAL_STATUSES = {"active", "closed", "ended", "suspended", "unknown"}
VALID_BANK_SEARCH_TYPES = {"deposit", "saving", "loan", "deposit-protection", "lease-finance", "installment-finance"}
DISCLOSURE_STALE_BEFORE = "202401"
REQUIRED_PRODUCT_FIELDS = (
    "provider",
    "provider_code",
    "product_code",
    "product_kind",
    "product_status",
    "sales_status",
    "source_record_id",
    "source_urls",
    "source_basis_dates",
    "collected_at",
)
REQUIRED_OPERATIONAL_FIELDS = (
    "status",
    "status_reason",
    "status_confidence",
    "last_verified_at",
    "recommendation_status",
)
RATE_QUERY_RE = re.compile(r"(금리|최고금리|중도해지|정기예금|적금|대출|개월)", re.I)
PROTECTION_QUERY_RE = re.compile(r"(예금자보호|보호대상|보호상품|kdic|보호)", re.I)
INACTIVE_QUERY_RE = re.compile(r"(종료|판매중단|중단|만료|마감|지난|unknown|closed|ended|reference|보류|불확실)", re.I)
NO_PREVIOUS_MONTH_SPEND_RE = re.compile(r"(No\s*전월실적|전월\s*실적\s*없음|전월\s*이용금액\s*조건\s*없음)", re.I)
NO_ANNUAL_FEE_RE = re.compile(r"(No\s*연회비|연회비\s*없음|연회비\s*면제)", re.I)

SEARCH_REGRESSIONS = (
    {
        "query": "연말정산 의료비 세액공제 한도 대상",
        "top_title_contains": "의료비",
        "top_title_excludes": "부가가치세",
    },
    {
        "query": "서울시 청년 월세 지원",
        "no_closed_support_results": True,
    },
)


def require(condition: bool, message: str, errors: list[str]) -> None:
    if not condition:
        errors.append(message)


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def item_map(items: list[dict]) -> dict[str, dict]:
    result: dict[str, dict] = {}
    for item in items:
        item_id = item.get("id")
        if item_id:
            result[item_id] = item
    return result


def benefit_text(benefit: dict) -> str:
    return " ".join(
        str(benefit.get(key) or "")
        for key in ("kind", "label", "text", "benefit", "condition")
    )


def validate_item_basics(export_id: str, items: list[dict], global_items: dict[str, dict], errors: list[str]) -> None:
    ids = [item.get("id") for item in items]
    require(len(ids) == len(set(ids)), f"{export_id}: duplicate item ids", errors)
    for item in items:
        item_id = item.get("id", "<missing>")
        require(bool(item.get("title")), f"{export_id}:{item_id}: missing title", errors)
        require(bool(item.get("type")), f"{export_id}:{item_id}: missing type", errors)
        require(bool(item.get("description")), f"{export_id}:{item_id}: missing description", errors)
        require(isinstance(item.get("parents"), list), f"{export_id}:{item_id}: parents must be list", errors)
        require(isinstance(item.get("children"), list), f"{export_id}:{item_id}: children must be list", errors)
        if item.get("type") != "source":
            require(bool(item.get("sources")), f"{export_id}:{item_id}: missing sources", errors)
            require(bool(item.get("reviewed_at")), f"{export_id}:{item_id}: missing reviewed_at", errors)
            require(bool(item.get("source_urls")), f"{export_id}:{item_id}: missing source_urls", errors)
            require(bool(item.get("source_basis_dates")), f"{export_id}:{item_id}: missing source_basis_dates", errors)
        if item.get("type") == "source":
            require(bool(item.get("url")), f"{export_id}:{item_id}: source missing url", errors)
            require(bool(item.get("publisher")), f"{export_id}:{item_id}: source missing publisher", errors)
        for key in REFERENCE_KEYS:
            for target_id in item.get(key) or []:
                require(target_id in global_items, f"{export_id}:{item_id}: {key} references missing id {target_id}", errors)


def validate_products(export_id: str, items: list[dict], expected_product_count: int, errors: list[str]) -> None:
    products = [item for item in items if item.get("type") in PRODUCT_TYPES]
    require(len(products) == expected_product_count, f"{export_id}: product_count mismatch", errors)
    for item in products:
        item_id = item["id"]
        for field in REQUIRED_PRODUCT_FIELDS:
            require(bool(item.get(field)), f"{export_id}:{item_id}: missing {field}", errors)
        for field in REQUIRED_OPERATIONAL_FIELDS:
            require(item.get(field) not in {None, ""}, f"{export_id}:{item_id}: missing {field}", errors)
        require(item.get("product_status") in {"active", "ended", "suspended", "unknown"}, f"{export_id}:{item_id}: invalid product_status", errors)
        require(item.get("sales_status") in {"active", "ended", "suspended", "unknown"}, f"{export_id}:{item_id}: invalid sales_status", errors)
        require(item.get("status") in VALID_OPERATIONAL_STATUSES, f"{export_id}:{item_id}: invalid status", errors)
        criteria = item.get("criteria") or []
        options = item.get("options") or []
        benefits = item.get("benefits") or []
        require(isinstance(criteria, list), f"{export_id}:{item_id}: criteria must be a list", errors)
        require(isinstance(options, list), f"{export_id}:{item_id}: options must be a list when present", errors)
        if item.get("status") == "active":
            require(bool(criteria or options or benefits), f"{export_id}:{item_id}: active product has no criteria/options/benefits", errors)
            require(bool(item.get("related")), f"{export_id}:{item_id}: active product has no semantic related links", errors)
        if item.get("type") == "insurance-product" and item.get("status") == "active":
            require(bool(criteria), f"{export_id}:{item_id}: active insurance product has empty criteria", errors)
        if item.get("type") == "bank-product":
            require(item.get("search_type") in VALID_BANK_SEARCH_TYPES, f"{export_id}:{item_id}: invalid search_type", errors)
        if item.get("type") == "card-product":
            for index, benefit in enumerate(benefits, start=1):
                if not isinstance(benefit, dict):
                    errors.append(f"{export_id}:{item_id}: benefit #{index} must be an object")
                    continue
                for field in ("previous_month_spend_min_krw", "monthly_benefit_limit_krw", "per_transaction_limit_krw", "excluded_spend", "condition_completeness"):
                    require(field in benefit, f"{export_id}:{item_id}: benefit #{index} missing {field}", errors)
                text = benefit_text(benefit)
                if NO_PREVIOUS_MONTH_SPEND_RE.search(text):
                    require(benefit.get("previous_month_spend_required") is False, f"{export_id}:{item_id}: benefit #{index} No전월실적 not normalized", errors)
                    require(benefit.get("previous_month_spend_min_krw") == 0, f"{export_id}:{item_id}: benefit #{index} No전월실적 min spend must be 0", errors)
                if NO_ANNUAL_FEE_RE.search(text):
                    require(benefit.get("annual_fee_required") is False, f"{export_id}:{item_id}: benefit #{index} No연회비 not normalized", errors)
        if item.get("type") == "insurance-product":
            for index, criterion in enumerate(criteria, start=1):
                if not isinstance(criterion, dict) or criterion.get("criteria_kind") != "coverage":
                    continue
                for field in ("coverage_name", "coverage_amount_krw", "premium_male_krw", "premium_female_krw", "renewal_type", "renewal_cycle_years", "waiting_period_days", "reduction_period_days", "condition_completeness"):
                    require(field in criterion, f"{export_id}:{item_id}: coverage #{index} missing {field}", errors)
        disclosure_months = []
        if item.get("disclosure_month"):
            disclosure_months.append(str(item["disclosure_month"]))
        for option in options:
            if isinstance(option, dict) and option.get("dcls_month"):
                disclosure_months.append(str(option["dcls_month"]))
        if item.get("status") == "active" and disclosure_months:
            require(max(disclosure_months) >= DISCLOSURE_STALE_BEFORE, f"{export_id}:{item_id}: active product has stale disclosure month", errors)
        for index, criterion in enumerate(criteria, start=1):
            require(bool(criterion.get("source")), f"{export_id}:{item_id}: criteria #{index} missing source", errors)
            require(bool(criterion.get("basis_source")), f"{export_id}:{item_id}: criteria #{index} missing basis_source", errors)
            require(bool(criterion.get("basis_definition")), f"{export_id}:{item_id}: criteria #{index} missing basis_definition", errors)


def validate_manifest(errors: list[str]) -> list[dict]:
    require(MANIFEST.exists(), f"missing {MANIFEST}", errors)
    if not MANIFEST.exists():
        return []
    payload = load_json(MANIFEST)
    exports = payload.get("exports") or []
    require(payload.get("name") == "finance", "manifest name must be finance", errors)
    require(isinstance(exports, list) and bool(exports), "manifest exports must be a non-empty list", errors)
    search_index = payload.get("search_index") or {}
    search_index_path = search_index.get("path")
    require(bool(search_index_path), "manifest missing search_index path", errors)
    if search_index_path:
        path = ROOT.parent / search_index_path
        require(path.exists(), f"search_index missing export file {search_index_path}", errors)
        if path.exists():
            index_payload = load_json(path)
            require(index_payload.get("item_count") == len(index_payload.get("items") or []), "search_index item_count mismatch", errors)
            require(bool(search_index.get("web_url")), "search_index missing web url", errors)
    quality_summary = payload.get("quality_summary") or {}
    require(bool(quality_summary.get("search_regression_tests")), "manifest missing search_regression_tests", errors)
    ids = [entry.get("id") for entry in exports]
    require(len(ids) == len(set(ids)), "manifest duplicate export ids", errors)
    for entry in exports:
        export_id = entry.get("id", "<missing>")
        path_text = entry.get("path")
        require(bool(path_text), f"{export_id}: missing path", errors)
        if not path_text:
            continue
        require("ontology" in Path(path_text).name, f"{export_id}: export filename should include ontology", errors)
        path = ROOT.parent / path_text
        require(path.exists(), f"{export_id}: missing export file {path_text}", errors)
        require(bool(entry.get("url")), f"{export_id}: missing raw url", errors)
        require(bool(entry.get("web_url")), f"{export_id}: missing web url", errors)
        if entry.get("domain", "").endswith("products"):
            require(bool(entry.get("quality_summary")), f"{export_id}: missing quality_summary", errors)
            require(bool(entry.get("export_checksum")), f"{export_id}: missing export_checksum", errors)
    return exports


def normalize_query(value: str) -> str:
    return value.strip().lower()


def query_tokens(query: str) -> list[str]:
    return [token for token in normalize_query(query).split() if token]


def search_text(item: dict) -> str:
    return str(item.get("search_text") or " ".join(str(item.get(key) or "") for key in ("id", "title", "type", "description", "product_kind", "search_type", "status", "application_status"))).lower()


def search_score(item: dict, raw_query: str) -> int:
    query = normalize_query(raw_query)
    title = normalize_query(str(item.get("title") or ""))
    item_id = normalize_query(str(item.get("id") or ""))
    search_type = normalize_query(str(item.get("search_type") or item.get("product_kind") or ""))
    status = normalize_query(str(item.get("status") or item.get("product_status") or ""))
    application_status = normalize_query(str(item.get("application_status") or ""))
    recommendation_status = normalize_query(str(item.get("recommendation_status") or ""))
    text = search_text(item)
    tokens = query_tokens(query)
    rate_intent = bool(RATE_QUERY_RE.search(query))

    if search_type == "deposit-protection" and rate_intent and not PROTECTION_QUERY_RE.search(query):
        return 0
    if (
        item.get("type") == "support-program"
        and (status in {"closed", "ended"} or application_status == "closed" or recommendation_status == "reference_only")
        and not INACTIVE_QUERY_RE.search(query)
    ):
        return 0

    score = 0
    if item_id == query or title == query:
        score = 100
    elif query and item_id and query in item_id:
        score = 80
    elif title and title in query:
        score = 75 + len(query_tokens(title))
    elif query and title and query in title:
        score = 70
    elif query and query in text:
        score = 40

    if len(tokens) > 1:
        matched = [token for token in tokens if token in text]
        if not score and len(matched) == len(tokens):
            score = 30 + len(matched)
        if not score and matched:
            score = 10 + len(matched)
    if rate_intent and search_type in {"deposit", "saving", "loan"}:
        score += 20
    return score


def validate_search_regressions(errors: list[str]) -> None:
    require(SEARCH_INDEX.exists(), f"missing {SEARCH_INDEX}", errors)
    if not SEARCH_INDEX.exists():
        return
    payload = load_json(SEARCH_INDEX)
    items = payload.get("items") or []
    for regression in SEARCH_REGRESSIONS:
        query = regression["query"]
        ranked = sorted(
            ((search_score(item, query), item) for item in items),
            key=lambda entry: (-entry[0], str(entry[1].get("title") or "")),
        )
        results = [item for score, item in ranked if score > 0][:10]
        require(bool(results), f"search regression '{query}' returned no results", errors)
        if not results:
            continue
        top_title = str(results[0].get("title") or "")
        if regression.get("top_title_contains"):
            require(str(regression["top_title_contains"]) in top_title, f"search regression '{query}' top result is {top_title}", errors)
        if regression.get("top_title_excludes"):
            require(str(regression["top_title_excludes"]) not in top_title, f"search regression '{query}' incorrectly returned {top_title}", errors)
        if regression.get("no_closed_support_results"):
            closed = [
                item.get("id")
                for item in results
                if item.get("type") == "support-program"
                and (item.get("status") == "closed" or item.get("application_status") == "closed")
            ]
            require(not closed, f"search regression '{query}' returned closed supports: {closed}", errors)


def main() -> int:
    errors: list[str] = []
    exports = validate_manifest(errors)
    loaded_exports: list[tuple[dict, list[dict]]] = []
    global_items: dict[str, dict] = {}
    for entry in exports:
        path_text = entry.get("path")
        if not path_text:
            continue
        path = ROOT.parent / path_text
        if not path.exists():
            continue
        payload = load_json(path)
        items = payload.get("items") or []
        if payload.get("reference_items"):
            items = [*(payload.get("reference_items") or []), *items]
        require(isinstance(items, list) and bool(items), f"{entry.get('id')}: export has no items", errors)
        loaded_exports.append((entry, items))
        global_items.update(item_map(items))

    for entry, items in loaded_exports:
        path = ROOT.parent / str(entry.get("path"))
        validate_item_basics(entry.get("id", path.name), items, global_items, errors)
        validate_products(entry.get("id", path.name), items, int(entry.get("product_count") or 0), errors)
    validate_search_regressions(errors)

    if errors:
        print("Finance ontology validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    print(f"Finance ontology validation passed: {len(exports)} exports")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
