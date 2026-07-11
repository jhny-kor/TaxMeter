#!/usr/bin/env python3
"""Validate split finance ontology exports and manifest."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

from validate_recommendation_contract import validate_contract


ROOT = Path(__file__).resolve().parents[1]
EXPORT_DIR = ROOT / "exports"
MANIFEST = EXPORT_DIR / "finance-ontology-manifest.json"
SEARCH_INDEX = EXPORT_DIR / "finance-search-index-2026.json"
QUALITY_MANIFEST = EXPORT_DIR / "openfin-quality-manifest-2026.json"
SEARCH_REGRESSION_REPORT = EXPORT_DIR / "openfin-search-regression-report-2026.json"

REFERENCE_KEYS = ("parents", "children", "related", "terms", "deadlines", "sources")
PRODUCT_TYPES = {"card-product", "bank-product", "insurance-product"}
GENERIC_SEARCH_TYPES = {"category", "term", "domain", "source"}
TAX_DECISION_TYPES = {"tax-credit", "deduction"}
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
RECOMMENDATION_QUERY_RE = re.compile(r"(추천|골라|맞는\s*상품|recommend)", re.I)
NO_PREVIOUS_MONTH_SPEND_RE = re.compile(r"(No\s*전월실적|전월\s*실적\s*없음|전월\s*이용금액\s*조건\s*없음)", re.I)
NO_ANNUAL_FEE_RE = re.compile(r"(No\s*연회비|연회비\s*없음|연회비\s*면제)", re.I)
BENEFIT_RATE_RE = re.compile(r"\d+(?:\.\d+)?\s*%")
LOAN_VERIFIED_REQUIRED_FIELDS = (
    "loan_limit_krw",
    "loan_rate_min_percent",
    "loan_rate_max_percent",
    "rate_type",
    "repayment_method",
    "early_repayment_fee",
    "guarantee_fee",
    "eligible_borrower",
    "loan_purpose",
    "official_application_url",
    "last_verified_at",
)

# mcp_server.py / build_finance_ontology.py와 동일한 type 필터 그룹.
SEARCH_TYPE_GROUPS = {
    "tax": {
        "tax", "tax-credit", "tax-reduction", "deduction", "corporate-tax-support",
        "official-tax-item", "filing", "deadline", "required-document", "eligibility-rule",
    },
    "tax-support": {"required-document"},
    "tax-rule": {"eligibility-rule"},
}

SEARCH_REGRESSIONS = (
    {
        "query": "연말정산 의료비 세액공제 한도 대상",
        "expected_top_id": "credit.medical-expense",
    },
    {
        "query": "연말정산 의료비 세액공제 한도 대상",
        "type_filter": "tax",
        "expected_top_id": "credit.medical-expense",
    },
    {
        "query": "신용카드 소득공제 한도",
        "type_filter": "tax",
        "expected_top_id": "deduction.credit-card-use",
    },
    {
        "query": "월세 세액공제 조건",
        "expected_top_id": "credit.monthly-rent",
    },
    {
        "query": "교육비 세액공제 대상",
        "expected_top_id": "credit.education-expense",
    },
    {
        "query": "연금계좌 세액공제 한도",
        "expected_top_id": "credit.pension-account",
    },
    {
        "query": "신용카드 소득공제 한도",
        "expected_top_id": "deduction.credit-card-use",
    },
    {
        "query": "서울시 청년 월세 지원",
        "no_closed_support_results": True,
    },
    {
        "query": "청년 전세대출 추천",
        "expected_empty": True,
    },
    {"query": "전월실적 없는 체크카드 추천", "expected_empty": True},
    {"query": "보험 추천", "expected_empty": True},
    {"query": "정기예금 비교해", "expected_search_type": "deposit"},
    {"query": "적금 비교해", "expected_search_type": "saving"},
    {"query": "주택담보대출 비교해", "expected_search_type": "loan"},
    {
        "query": "finance.bank.deposit.0010001.wr0001b",
        "expected_top_id": "finance.deposit.deposit.0010001.wr0001b",
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
        if item.get("type") == "support-program" and item.get("status") in {"unknown", "closed"}:
            require(
                item.get("recommendation_status") == "reference_only",
                f"{export_id}:{item_id}: {item.get('status')} support must be recommendation_status reference_only",
                errors,
            )


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
                if "적립" in text:
                    require(benefit.get("benefit_type") == "point_accumulation", f"{export_id}:{item_id}: benefit #{index} 적립 benefit_type not normalized", errors)
                if BENEFIT_RATE_RE.search(text):
                    require(benefit.get("benefit_rate_percent") is not None, f"{export_id}:{item_id}: benefit #{index} % rate not normalized to benefit_rate_percent", errors)
            benefits_partial_or_incomplete = any(
                isinstance(benefit, dict) and benefit.get("condition_completeness") in {"partial", "incomplete"}
                for benefit in benefits
            )
            if benefits_partial_or_incomplete:
                require(
                    item.get("recommendation_scope") == "listing_only",
                    f"{export_id}:{item_id}: card with partial/incomplete benefit conditions must be recommendation_scope listing_only",
                    errors,
                )
        if item.get("type") == "insurance-product":
            coverage_incomplete = False
            for index, criterion in enumerate(criteria, start=1):
                if not isinstance(criterion, dict) or criterion.get("criteria_kind") != "coverage":
                    continue
                if criterion.get("condition_completeness") == "incomplete":
                    coverage_incomplete = True
                for field in ("coverage_name", "coverage_amount_krw", "premium_male_krw", "premium_female_krw", "renewal_type", "renewal_cycle_years", "waiting_period_days", "reduction_period_days", "condition_completeness"):
                    require(field in criterion, f"{export_id}:{item_id}: coverage #{index} missing {field}", errors)
            if coverage_incomplete:
                require(
                    item.get("recommendation_scope") == "listing_only",
                    f"{export_id}:{item_id}: insurance with incomplete coverage conditions must be recommendation_scope listing_only",
                    errors,
                )
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
    for field in ("release_status", "degraded_domains", "blocking_issues", "warning_issues"):
        require(field in payload, f"manifest missing {field}", errors)
    require(payload.get("semantic_validation_passed") is True, "manifest semantic_validation_passed must be true", errors)
    require(payload.get("id_compatibility_validation_passed") is True, "manifest id_compatibility_validation_passed must be true", errors)
    quality_exports = payload.get("quality_exports") or []
    require(len(quality_exports) >= 2, "manifest missing quality_exports", errors)
    for entry in quality_exports:
        path_text = entry.get("path")
        require(bool(path_text), f"{entry.get('id', '<missing>')}: missing quality export path", errors)
        if path_text:
            path = ROOT.parent / path_text
            require(path.exists(), f"{entry.get('id', '<missing>')}: missing quality export file {path_text}", errors)
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
    text = str(item.get("search_text") or " ".join(str(item.get(key) or "") for key in ("id", "title", "type", "description", "product_kind", "search_type", "status", "application_status")))
    aliases = " ".join(str(value) for key in ("legacy_ids", "search_aliases", "aliases") for value in item.get(key) or [])
    return f"{text} {aliases}".lower()


def matches_recommendation_domain(item: dict, query: str) -> bool:
    search_type = normalize_query(str(item.get("search_type") or item.get("product_kind") or ""))
    if "보험" in query:
        return item.get("type") == "insurance-product"
    if any(token in query for token in ("카드", "체크카드", "신용카드")):
        return item.get("type") == "card-product"
    if "대출" in query:
        return search_type == "loan"
    if "정기예금" in query or "예금" in query:
        return search_type == "deposit"
    if "적금" in query:
        return search_type == "saving"
    return True


def search_score(item: dict, raw_query: str) -> int:
    query = normalize_query(raw_query)
    title = normalize_query(str(item.get("title") or ""))
    item_id = normalize_query(str(item.get("id") or ""))
    search_type = normalize_query(str(item.get("search_type") or item.get("product_kind") or ""))
    status = normalize_query(str(item.get("status") or item.get("product_status") or ""))
    application_status = normalize_query(str(item.get("application_status") or ""))
    recommendation_status = normalize_query(str(item.get("recommendation_status") or ""))
    text = search_text(item)
    aliases = [normalize_query(str(alias)) for alias in item.get("search_aliases") or []]
    tokens = query_tokens(query)
    title_tokens = query_tokens(title)
    rate_intent = bool(RATE_QUERY_RE.search(query))

    if search_type == "deposit-protection" and rate_intent and not PROTECTION_QUERY_RE.search(query):
        return 0
    if RECOMMENDATION_QUERY_RE.search(query):
        intent_tokens = [token for token in tokens if not RECOMMENDATION_QUERY_RE.search(token)]
        if (
            recommendation_status != "verified_recommendation_candidate"
            or item.get("recommendation_scope") == "internal_verification_candidate"
            or not matches_recommendation_domain(item, query)
            or not intent_tokens
            or not all(token in text for token in intent_tokens)
        ):
            return 0
    if (
        item.get("type") == "support-program"
        and (status in {"closed", "ended"} or application_status == "closed" or recommendation_status == "reference_only")
        and not INACTIVE_QUERY_RE.search(query)
    ):
        return 0

    score = 0
    if query in aliases:
        score = 95
    elif item_id == query or title == query:
        score = 100
    elif query and item_id and query in item_id:
        score = 80
    elif title and title in query:
        base = 35 if item.get("type") in GENERIC_SEARCH_TYPES and len(title_tokens) < len(tokens) else 75
        score = base + len(title_tokens)
    elif query and title and query in title:
        score = 70
    elif query and query in text:
        score = 40

    if len(tokens) > 1:
        matched = [token for token in tokens if token in text]
        if item.get("type") in TAX_DECISION_TYPES and len(matched) >= min(2, len(tokens)):
            score = max(score, 60 + len(matched))
        if not score and len(matched) == len(tokens):
            score = 30 + len(matched)
        if not score and matched:
            score = 10 + len(matched)
    if score and rate_intent and search_type in {"deposit", "saving", "loan"}:
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
        type_filter = regression.get("type_filter")
        allowed_types = SEARCH_TYPE_GROUPS.get(type_filter, {type_filter}) if type_filter else None
        candidates = [item for item in items if not allowed_types or item.get("type") in allowed_types]
        ranked = sorted(
            ((search_score(item, query), item) for item in candidates),
            key=lambda entry: (-entry[0], str(entry[1].get("title") or "")),
        )
        results = [item for score, item in ranked if score > 0][:10]
        if regression.get("expected_empty"):
            require(not results, f"search regression '{query}' expected no recommendation results: {[item.get('id') for item in results]}", errors)
            continue
        require(bool(results), f"search regression '{query}' returned no results", errors)
        if not results:
            continue
        top_title = str(results[0].get("title") or "")
        if regression.get("expected_top_id"):
            require(results[0].get("id") == regression["expected_top_id"], f"search regression '{query}' top result is {results[0].get('id')} {top_title}", errors)
        if regression.get("expected_search_type"):
            require(results[0].get("search_type") == regression["expected_search_type"], f"search regression '{query}' top search_type is {results[0].get('search_type')}", errors)
        if regression.get("no_closed_support_results"):
            closed = [
                item.get("id")
                for item in results
                if item.get("type") == "support-program"
                and (item.get("status") == "closed" or item.get("application_status") == "closed")
            ]
            require(not closed, f"search regression '{query}' returned closed supports: {closed}", errors)
        if regression.get("verified_recommendation_candidates_only"):
            unsafe = [item.get("id") for item in results if item.get("recommendation_status") != "verified_recommendation_candidate"]
            intent_tokens = [token for token in query_tokens(query) if not RECOMMENDATION_QUERY_RE.search(token)]
            irrelevant = [item.get("id") for item in results if not all(token in search_text(item) for token in intent_tokens)]
            require(not unsafe, f"search regression '{query}' returned non-candidates: {unsafe}", errors)
            require(not irrelevant, f"search regression '{query}' returned intent-mismatched candidates: {irrelevant}", errors)
            require(
                any(item.get("type") == regression.get("expected_type") for item in results),
                f"search regression '{query}' returned no {regression.get('expected_type')} candidate",
                errors,
            )

    require(QUALITY_MANIFEST.exists(), f"missing {QUALITY_MANIFEST}", errors)
    require(SEARCH_REGRESSION_REPORT.exists(), f"missing {SEARCH_REGRESSION_REPORT}", errors)
    if SEARCH_REGRESSION_REPORT.exists():
        report = load_json(SEARCH_REGRESSION_REPORT)
        require(report.get("failed_count") == 0, "search regression report has failures", errors)
        require(report.get("test_count") >= 5, "search regression report missing P0 tax queries", errors)


def legacy_ids_for_item(item_id: str) -> list[str]:
    if item_id.startswith("finance.deposit.deposit."):
        return [item_id.replace("finance.deposit.deposit.", "finance.bank.deposit.", 1)]
    if item_id.startswith("finance.saving.saving."):
        return [item_id.replace("finance.saving.saving.", "finance.bank.saving.", 1)]
    if item_id.startswith("finance.loan."):
        return [item_id.replace("finance.loan.", "finance.bank.", 1)]
    return []


def validate_medical_expense_semantics(global_items: dict[str, dict], errors: list[str]) -> None:
    item = global_items.get("credit.medical-expense")
    require(item is not None, "missing credit.medical-expense", errors)
    if not item:
        return
    criteria = [criterion for criterion in item.get("criteria") or [] if isinstance(criterion, dict)]
    threshold = next((criterion for criterion in criteria if criterion.get("label") == "의료비 공제 문턱"), None)
    require(threshold is not None, "credit.medical-expense: missing medical threshold criterion", errors)
    if threshold:
        require(threshold.get("criteria_kind") == "threshold", "medical threshold must be criteria_kind=threshold", errors)
        require(threshold.get("threshold_type") == "gross_salary_ratio", "medical threshold missing gross_salary_ratio type", errors)
        require(threshold.get("threshold_rate_percent") == 3, "medical threshold_rate_percent must be 3", errors)
        require("rate_percent" not in threshold, "medical threshold must not expose rate_percent", errors)
        require("rate_label" not in threshold, "medical threshold must not expose rate_label", errors)
        require(threshold.get("amount_formula") == "max(0, medical_expense - gross_salary * 0.03)", "medical threshold formula must subtract gross salary threshold", errors)
    require(
        any(criterion.get("label") == "일반 의료비 세액공제율" and criterion.get("rate_percent") == 15 for criterion in criteria),
        "credit.medical-expense: missing 15% medical credit-rate criterion",
        errors,
    )


def validate_id_compatibility(loaded_exports: list[tuple[dict, list[dict]]], errors: list[str]) -> None:
    canonical_ids = {
        str(item.get("id"))
        for _, items in loaded_exports
        for item in items
        if item.get("id")
    }
    alias_to_id: dict[str, str] = {}
    for _, items in loaded_exports:
        for item in items:
            item_id = str(item.get("id") or "")
            if not item_id:
                continue
            expected_legacy_ids = legacy_ids_for_item(item_id)
            if expected_legacy_ids:
                legacy_ids = {str(value) for value in item.get("legacy_ids") or []}
                for legacy_id in expected_legacy_ids:
                    require(legacy_id in legacy_ids, f"{item_id}: missing legacy id {legacy_id}", errors)
            aliases = [
                str(value)
                for key in ("legacy_ids", "search_aliases", "aliases")
                for value in item.get(key) or []
            ]
            for alias in aliases:
                require(alias not in canonical_ids, f"{item_id}: alias collides with canonical id {alias}", errors)
                previous = alias_to_id.get(alias)
                require(previous in {None, item_id}, f"alias collision {alias}: {previous} vs {item_id}", errors)
                alias_to_id[alias] = item_id
    for _, items in loaded_exports:
        for item in items:
            for key in REFERENCE_KEYS:
                for target_id in item.get(key) or []:
                    require(target_id not in alias_to_id, f"{item.get('id')}: {key} references legacy alias {target_id}", errors)


def validate_semantic_gates(loaded_exports: list[tuple[dict, list[dict]]], global_items: dict[str, dict], errors: list[str]) -> None:
    validate_medical_expense_semantics(global_items, errors)
    validate_id_compatibility(loaded_exports, errors)
    for _, items in loaded_exports:
        for item in items:
            item_id = str(item.get("id") or "")
            if item.get("type") == "support-program" and item.get("application_open_from") and item.get("application_open_to"):
                require(item["application_open_to"] >= item["application_open_from"], f"{item_id}: support end date before start date", errors)
            if item.get("search_type") == "loan":
                if item.get("loan_limit_normalization_status") == "ambiguous":
                    require(item.get("loan_limit_krw") is None and item.get("limit_krw") is None, f"{item_id}: ambiguous loan limit must not expose KRW amount", errors)
                if item.get("recommendation_status") == "verified_recommendation_candidate":
                    missing = [field for field in LOAN_VERIFIED_REQUIRED_FIELDS if item.get(field) in {None, ""}]
                    require(not missing, f"{item_id}: verified loan candidate missing required fields {missing}", errors)
            if item.get("type") == "insurance-product":
                if item.get("recommendation_status") != "reference_only":
                    incomplete = [
                        criterion.get("label")
                        for criterion in item.get("criteria") or []
                        if isinstance(criterion, dict) and criterion.get("condition_completeness") == "incomplete"
                    ]
                    require(not incomplete, f"{item_id}: incomplete insurance coverage cannot be recommended", errors)
                for criterion in item.get("criteria") or []:
                    if not isinstance(criterion, dict) or criterion.get("criteria_kind") != "coverage":
                        continue
                    require(bool(criterion.get("condition_source_locator")), f"{item_id}: insurance coverage missing source locator", errors)
                    if criterion.get("coverage_amount_krw") is not None:
                        require(bool(criterion.get("coverage_amount_basis")), f"{item_id}: coverage amount value missing basis", errors)


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
    validate_semantic_gates(loaded_exports, global_items, errors)
    validate_search_regressions(errors)
    errors.extend(validate_contract())

    if errors:
        print("Finance ontology validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    print(f"Finance ontology validation passed: {len(exports)} exports")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
