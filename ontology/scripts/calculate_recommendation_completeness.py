#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from datetime import date, timedelta
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
EXPORT_DIR = ROOT / "exports"
PROTECTION_PATH = ROOT / "custom" / "finance" / "deposit-protection-products.generated.json"
REQUIRED_FIELDS = {
    "deposit": ("term_months", "base_rate_percent", "maximum_rate_percent", "preferential_rate_conditions", "minimum_deposit_krw", "maximum_deposit_krw", "join_member", "join_channel", "interest_method", "early_termination_condition", "deposit_protection_status", "sales_verification_status"),
    "saving": ("term_months", "saving_method", "monthly_payment_min_krw", "monthly_payment_max_krw", "base_rate_percent", "maximum_rate_percent", "preferential_rate_conditions", "join_member", "join_channel", "early_termination_condition", "deposit_protection_status", "sales_verification_status"),
    "card": ("annual_fee_krw", "previous_month_spend_min_krw", "benefit_type", "benefit_rate_or_amount", "monthly_benefit_limit_krw", "per_transaction_limit_krw", "benefit_categories", "excluded_spend", "performance_excluded_spend", "benefit_frequency_limit", "minimum_payment_amount", "sales_verification_status"),
    "loan": ("loan_rate_min_percent", "loan_rate_max_percent", "repayment_method", "loan_limit_krw", "early_repayment_fee", "eligible_borrower", "collateral_type", "rate_type"),
    "insurance": ("coverage_amount_krw", "renewal_type", "renewal_cycle_years", "waiting_period_days", "reduction_period_days", "claim_condition", "exclusion_condition", "payment_count_limit", "insured_age_min", "insured_age_max", "insurance_term", "payment_term", "surrender_refund_type", "premium_basis", "sales_verification_status"),
}
COMPARISON_FIELDS = {
    "deposit": ("term_months", "base_rate_percent", "maximum_rate_percent", "source_urls"),
    "saving": ("term_months", "base_rate_percent", "maximum_rate_percent", "source_urls"),
}
FIELD_ALIASES = {
    "benefit_type": ("benefit_type", "benefit", "kind"),
    "benefit_rate_or_amount": ("benefit_rate_percent", "rate_percent", "fixed_benefit_amount_krw"),
    "benefit_categories": ("benefit_categories", "category"),
    "loan_rate_min_percent": ("loan_rate_min_percent", "lend_rate_min", "rate_percent"),
    "loan_rate_max_percent": ("loan_rate_max_percent", "lend_rate_max", "rate_percent"),
    "loan_limit_krw": ("loan_limit_krw", "limit_krw", "loan_limit", "loan_limit_detl", "lnlmt"),
    "repayment_method": ("repayment_method", "rpay_type", "rpay_type_nm", "rdptMthd"),
    "early_repayment_fee": ("early_repayment_fee", "erly_rpay_fee", "rpymdCfe"),
    "rate_type": ("rate_type", "lend_rate_type", "lend_rate_type_nm", "irtCtg"),
    "eligible_borrower": ("eligible_borrower", "join_member", "target"),
    "coverage_amount_krw": ("coverage_amount_krw", "coverage_amount", "amount_krw"),
    "renewal_type": ("renewal_type", "renewal", "renewal_cycle_years"),
    "premium_basis": ("premium_basis", "premium", "premium_condition"),
}


def normalized(value: Any) -> str:
    return re.sub(r"[^0-9a-z가-힣]+", "", str(value or "").lower())


def protection_keys() -> set[tuple[str, str]]:
    if not PROTECTION_PATH.exists():
        return set()
    payload = json.loads(PROTECTION_PATH.read_text(encoding="utf-8"))
    keys: set[tuple[str, str]] = set()
    for item in payload.get("items") or []:
        options = item.get("options") or []
        if options and isinstance(options[0], dict):
            keys.add((normalized(item.get("provider")), normalized(options[0].get("product_name"))))
    return keys


def amount_from_text(text: str, labels: tuple[str, ...]) -> int | None:
    for label in labels:
        match = re.search(rf"{label}\s*[:：]?\s*([0-9,]+)\s*(억|만)?\s*원", text)
        if match:
            value = int(match.group(1).replace(",", ""))
            unit = match.group(2)
            return value * ({"억": 100_000_000, "만": 10_000}.get(unit, 1))
    return None


def join_channels(raw: dict[str, Any]) -> list[str]:
    text = str(raw.get("join_way") or "")
    aliases = {"인터넷": "online", "스마트폰": "online", "모바일": "online", "영업점": "branch", "전화": "phone", "텔레뱅킹": "phone"}
    return sorted({channel for token, channel in aliases.items() if token in text})


def rate_options(item: dict[str, Any]) -> list[dict[str, Any]]:
    raw = item.get("raw") or {}
    conditions_text = str(raw.get("spcl_cnd") or "").strip()
    conditions = [] if normalized(conditions_text) in {"", "해당사항없음", "없음"} else [{"description": conditions_text, "condition_status": "source_text"}]
    channels = join_channels(raw)
    options: list[dict[str, Any]] = []
    for option in item.get("options") or []:
        if not isinstance(option, dict) or option.get("save_trm") in (None, "") or option.get("intr_rate") in (None, ""):
            continue
        entry = {
            "term_months": int(option["save_trm"]),
            "base_rate_percent": float(option["intr_rate"]),
            "maximum_rate_percent": float(option.get("intr_rate2") or option["intr_rate"]),
            "preferential_rate_conditions": conditions,
            "join_channels": channels,
            "minimum_deposit_krw": amount_from_text(str(raw.get("etc_note") or ""), ("최소가입금액", "최저가입금액")),
            "maximum_deposit_krw": raw.get("max_limit"),
            "monthly_payment_min_krw": amount_from_text(str(raw.get("etc_note") or ""), ("최소가입금액", "최저가입금액")),
            "monthly_payment_max_krw": raw.get("max_limit"),
            "saving_method": {"F": "free", "S": "fixed"}.get(str(option.get("rsrv_type") or "")),
            "interest_method": option.get("intr_rate_type_nm"),
            "source_urls": item.get("source_urls") or [],
        }
        options.append(entry)
    deduplicated: dict[tuple[Any, ...], dict[str, Any]] = {}
    for option in options:
        key = (option["term_months"], option["base_rate_percent"], option["maximum_rate_percent"], option.get("saving_method"), tuple(option["join_channels"]))
        deduplicated[key] = option
    return list(deduplicated.values())


def field_present(value: Any) -> bool:
    if value in (None, "", [], {}, "unknown", "unverified", "listed_unverified"):
        return False
    if isinstance(value, str) and value.strip().lower() in {"-", "해당없음", "해당 사항 없음", "없음", "없음정보", "n/a", "na"}:
        return False
    return True


def nested_values(value: Any, names: set[str]) -> list[Any]:
    if isinstance(value, dict):
        values = [entry for key, entry in value.items() if key in names and field_present(entry)]
        for entry in value.values():
            values.extend(nested_values(entry, names))
        return values
    if isinstance(value, list):
        values: list[Any] = []
        for entry in value:
            values.extend(nested_values(entry, names))
        return values
    return []


def source_field_value(item: dict[str, Any], field: str) -> Any:
    direct = item.get(field)
    if field_present(direct):
        return direct
    names = set(FIELD_ALIASES.get(field, (field,)))
    values = nested_values(
        [item.get("criteria") or [], item.get("options") or [], item.get("benefits") or [], item.get("raw") or {}],
        names,
    )
    return values[0] if values else None


def product_domain(item: dict[str, Any]) -> str | None:
    if item.get("search_type") in {"deposit", "saving", "loan"}:
        return str(item["search_type"])
    if item.get("type") == "card-product":
        return "card"
    if item.get("type") == "insurance-product":
        return "insurance"
    return None


def enrich_product(item: dict[str, Any], protected: set[tuple[str, str]]) -> None:
    domain = product_domain(item)
    if domain not in REQUIRED_FIELDS:
        return
    if domain in {"deposit", "saving"}:
        options = rate_options(item)
        raw = item.get("raw") or {}
        item["comparison_options"] = options
        item["term_months"] = sorted({option["term_months"] for option in options})
        item["base_rate_percent"] = sorted({option["base_rate_percent"] for option in options})
        item["maximum_rate_percent"] = sorted({option["maximum_rate_percent"] for option in options})
        item["preferential_rate_conditions"] = options[0]["preferential_rate_conditions"] if options else None
        item["minimum_deposit_krw"] = next((option["minimum_deposit_krw"] for option in options if option["minimum_deposit_krw"] is not None), None)
        item["maximum_deposit_krw"] = raw.get("max_limit")
        item["monthly_payment_min_krw"] = next((option["monthly_payment_min_krw"] for option in options if option["monthly_payment_min_krw"] is not None), None)
        item["monthly_payment_max_krw"] = raw.get("max_limit")
        item["saving_method"] = sorted({option["saving_method"] for option in options if option.get("saving_method")})
        item["join_member"] = raw.get("join_member")
        item["join_channel"] = join_channels(raw)
        item["interest_method"] = sorted({str(option["interest_method"]) for option in options if option.get("interest_method")})
        item["early_termination_condition"] = raw.get("mid_termination_rate")
        item["deposit_protection_status"] = "listed" if (normalized(item.get("provider")), normalized(raw.get("fin_prdt_nm"))) in protected else "unknown"
        comparison_fields = COMPARISON_FIELDS[domain]
        option_status = all(
            any(field_present(option.get(field)) for option in options)
            for field in comparison_fields
        )
        item["comparison_field_verification_status"] = "verified" if option_status else "blocked"
        item["comparison_field_verification"] = {
            field: {
                "status": "verified" if any(field_present(option.get(field)) for option in options) else "unknown",
                "source": "official_finlife_option",
            }
            for field in comparison_fields
        }
        item["comparison_engine_gate_passed"] = option_status
    fresh = str(item.get("collected_at") or "") >= (date.today() - timedelta(days=31)).isoformat()
    item["source_listing_status"] = "listed" if item.get("product_status") == "active" and (item.get("source_record_id") or item.get("source_urls")) else "not_listed"
    if item.get("sales_status") != "ended":
        item["sales_status"] = "unknown"
    item["sales_verification_status"] = "listed_unverified"
    item["sales_verified_at"] = None
    item["condition_verification_status"] = "source_text" if item.get("criteria") else "not_collected"
    item["source_freshness_status"] = "current" if fresh else "stale"
    item["freshness_status"] = item["source_freshness_status"]
    item["last_source_checked_at"] = item.get("collected_at") or None
    item["last_reviewed_at"] = item.get("reviewed_at") or None
    item["last_verified_at"] = None
    required = REQUIRED_FIELDS[domain]
    source_values = {field: source_field_value(item, field) for field in required}
    if domain != "loan":
        for field, value in source_values.items():
            if field_present(value) and not field_present(item.get(field)):
                item[field] = value
    missing = [
        field
        for field in required
        if not (field == "preferential_rate_conditions" and item.get(field) == []) and not field_present(item.get(field))
    ]
    item["required_field_count"] = len(required)
    item["completed_field_count"] = len(required) - len(missing)
    item["completeness_ratio"] = round(item["completed_field_count"] / len(required), 4)
    source_completed = sum(1 for value in source_values.values() if field_present(value))
    item["source_completeness_ratio"] = round(source_completed / len(required), 4)
    item["normalized_completeness_ratio"] = item["completeness_ratio"]
    item["verified_completeness_ratio"] = round(
        sum(1 for field in required if field_present(item.get(field)) and item.get("sales_verification_status") == "verified_active") / len(required),
        4,
    )
    item["missing_in_source_fields"] = sorted(field for field, value in source_values.items() if not field_present(value))
    unmapped_existing_fields = [
        field for field, value in source_values.items() if field_present(value) and not field_present(item.get(field))
    ]
    if domain == "loan" and "loan_limit_krw" in unmapped_existing_fields:
        raw_limit = str(source_values["loan_limit_krw"])
        item["manual_review_required"] = True
        item["manual_review_reason"] = (
            "loan_limit_conditional_or_free_text"
            if any(marker in raw_limit for marker in ("조건", "한도 내", "범위", "~", "부터", "까지"))
            else "loan_limit_unit_ambiguous"
        )
        item["manual_review_fields"] = ["loan_limit_krw"]
        unmapped_existing_fields.remove("loan_limit_krw")
    item["unmapped_existing_fields"] = sorted(unmapped_existing_fields)
    item["unverified_fields"] = sorted(field for field in required if field_present(item.get(field)) and item.get("sales_verification_status") != "verified_active")
    item["discovery_evidence_fields"] = sorted(field for field, value in source_values.items() if field_present(value))
    item["missing_required_fields"] = sorted(set([*(item.get("missing_required_fields") or []), *missing]))
    item["domain_gate_passed"] = not missing and item["sales_verification_status"] == "verified_active" and item["source_freshness_status"] == "current"
    item["comparison_basis_fields"] = [field for field in required if field not in missing]


def enrich_products(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    protected = protection_keys()
    for item in items:
        enrich_product(item, protected)
    return items


def validate_exports() -> list[str]:
    errors: list[str] = []
    for path in (EXPORT_DIR / "korea-deposit-products-ontology-2026.json", EXPORT_DIR / "korea-saving-products-ontology-2026.json", EXPORT_DIR / "korea-card-products-ontology-2026.json", EXPORT_DIR / "korea-loan-products-ontology-2026.json", EXPORT_DIR / "korea-insurance-products-ontology-2026.json"):
        payload = json.loads(path.read_text(encoding="utf-8"))
        for item in payload.get("items") or []:
            domain = product_domain(item)
            if domain not in REQUIRED_FIELDS:
                continue
            item_id = str(item.get("id"))
            for field in ("required_field_count", "completed_field_count", "completeness_ratio", "source_completeness_ratio", "normalized_completeness_ratio", "verified_completeness_ratio", "missing_required_fields", "missing_in_source_fields", "unmapped_existing_fields", "unverified_fields", "discovery_evidence_fields", "domain_gate_passed", "source_listing_status", "sales_verification_status", "source_freshness_status"):
                if field not in item:
                    errors.append(f"{item_id}: missing {field}")
            if item.get("recommendation_scope") in {None, "", "unspecified"}:
                errors.append(f"{item_id}: missing recommendation_scope")
            if item.get("recommendation_scope") == "public_recommendation" and not item.get("domain_gate_passed"):
                errors.append(f"{item_id}: public recommendation without domain gate")
    return errors
