#!/usr/bin/env python3
from __future__ import annotations

import json
import math
from datetime import date, timedelta
from pathlib import Path
from typing import Any

from recommendation_policy import COMPARISON_ENABLED_DOMAINS
from search_index_loader import load_search_index_items, search_index_basis_date


ROOT = Path(__file__).resolve().parents[1]
SEARCH_INDEX = ROOT / "exports" / "finance-search-index-2026.json"
MODEL_VERSION = "openfin-comparison-v0.1.0"
RESPONSE_CONTRACT_VERSION = "openfin-comparison-v1.0.1"
DEFAULT_INTEREST_TAX_RATE_PERCENT = 15.4
EXCLUDED_SAMPLE_LIMIT = 10


def load_items(path: Path = SEARCH_INDEX) -> list[dict[str, Any]]:
    return load_search_index_items(path)


def index_basis_date(path: Path = SEARCH_INDEX) -> str:
    return search_index_basis_date(path)


def verification_evidence_blocker(item: dict[str, Any]) -> str | None:
    evidence = item.get("verification_evidence")
    if not isinstance(evidence, dict):
        return "missing_verification_evidence"
    source_checksums = {
        str(record.get("source_checksum"))
        for record in item.get("source_records") or []
        if isinstance(record, dict) and record.get("source_checksum")
    } or {str(item.get("source_checksum"))}
    if not source_checksums.issubset(set(str(value) for value in evidence.get("source_checksums") or [])):
        return "source_checksum_mismatch"
    expires_at = evidence.get("expires_at")
    if not isinstance(expires_at, str):
        return "verification_expired"
    try:
        if date.fromisoformat(expires_at) < date.today():
            return "verification_expired"
    except ValueError:
        return "verification_expired"
    return None


def comparison_blocker(item: dict[str, Any]) -> str | None:
    if item.get("comparison_exclusion_reasons"):
        return "comparison_excluded"
    if item.get("recommendation_scope") != "comparison_only":
        return "not_comparison_scope"
    if item.get("source_listing_status") != "listed":
        return "source_not_listed"
    if item.get("sales_verification_status") != "verified_active":
        return "sales_not_verified"
    if item.get("source_freshness_status") != "current":
        return "stale_source"
    verified_at = item.get("sales_verified_at")
    if not isinstance(verified_at, str):
        return "stale_source"
    try:
        verified_date = date.fromisoformat(verified_at)
    except ValueError:
        return "stale_source"
    if verified_date < date.today() - timedelta(days=31) or verified_date > date.today():
        return "stale_source"
    if item.get("verification_status") != "verified":
        return "not_verified"
    evidence_blocker = verification_evidence_blocker(item)
    if evidence_blocker:
        return evidence_blocker
    if item.get("comparison_engine_gate_passed") is not True:
        return "comparison_fields_not_verified"
    if item.get("status") in {"closed", "ended", "unknown", "suspended"}:
        return f"status_{item.get('status')}"
    return None


def option_blocker(option: dict[str, Any], arguments: dict[str, Any]) -> str | None:
    if int(option.get("term_months") or 0) != int(arguments["term_months"]):
        return "term_mismatch"
    channels = {str(channel).lower() for channel in arguments.get("join_channels") or []}
    option_channels = {str(channel).lower() for channel in option.get("join_channels") or []}
    if channels and option_channels and not channels.intersection(option_channels):
        return "join_channel_mismatch"
    amount = arguments.get("deposit_amount_krw")
    maximum = option.get("maximum_deposit_krw")
    minimum = option.get("minimum_deposit_krw")
    if amount is not None and minimum is not None and int(amount) < int(minimum):
        return "amount_below_minimum"
    if amount is not None and maximum is not None and int(amount) > int(maximum):
        return "amount_exceeds_limit"
    payment = arguments.get("monthly_payment_krw")
    monthly_maximum = option.get("monthly_payment_max_krw")
    monthly_minimum = option.get("monthly_payment_min_krw")
    if payment is not None and monthly_minimum is not None and int(payment) < int(monthly_minimum):
        return "monthly_payment_below_minimum"
    if payment is not None and monthly_maximum is not None and int(payment) > int(monthly_maximum):
        return "monthly_payment_exceeds_limit"
    saving_method = arguments.get("saving_method")
    if saving_method and option.get("saving_method") and saving_method != option.get("saving_method"):
        return "saving_method_mismatch"
    if not option.get("source_urls"):
        return "missing_source_url"
    return None


def achievable_rate(option: dict[str, Any], eligible_conditions: set[str]) -> tuple[float, list[str], list[str], list[str]]:
    base_rate = float(option["base_rate_percent"])
    matched: list[str] = []
    unmatched: list[str] = []
    unknown: list[str] = []
    additional_rate = 0.0
    for condition in option.get("preferential_rate_conditions") or []:
        condition_id = str(condition.get("condition_id") or "")
        if not condition_id:
            unknown.append(str(condition.get("description") or "unidentified_preferential_condition"))
        elif condition_id in eligible_conditions:
            matched.append(condition_id)
            additional_rate += float(condition.get("additional_rate_percent") or 0)
        else:
            unmatched.append(condition_id)
    maximum_rate = float(option["maximum_rate_percent"]) if isinstance(option.get("maximum_rate_percent"), (int, float)) else base_rate
    return min(base_rate + additional_rate, maximum_rate), matched, unmatched, unknown


def interest_estimate(domain: str, arguments: dict[str, Any], rate_percent: float) -> dict[str, Any]:
    term_months = int(arguments["term_months"])
    tax_rate_percent = float(arguments.get("tax_rate_percent", DEFAULT_INTEREST_TAX_RATE_PERCENT))
    if domain == "deposit":
        if arguments.get("deposit_amount_krw") is None:
            return {"principal_krw": None, "gross_interest_krw": None, "tax_rate_percent": tax_rate_percent, "tax_withheld_krw": None, "net_interest_krw": None, "calculation_assumption": "deposit_amount_required"}
        principal = int(arguments["deposit_amount_krw"])
        gross_interest = principal * rate_percent / 100 * term_months / 12
        assumption = "simple_interest_for_full_term_deposit"
    else:
        if arguments.get("monthly_payment_krw") is None:
            return {"principal_krw": None, "gross_interest_krw": None, "tax_rate_percent": tax_rate_percent, "tax_withheld_krw": None, "net_interest_krw": None, "calculation_assumption": "monthly_payment_required"}
        monthly_payment = int(arguments["monthly_payment_krw"])
        principal = monthly_payment * term_months
        gross_interest = monthly_payment * rate_percent / 100 * sum(range(1, term_months + 1)) / 12
        assumption = "simple_interest_with_each_month_paid_at_month_start"
    tax_withheld = gross_interest * tax_rate_percent / 100
    return {
        "principal_krw": principal,
        "gross_interest_krw": math.floor(gross_interest + 0.5),
        "tax_rate_percent": tax_rate_percent,
        "tax_withheld_krw": math.floor(tax_withheld + 0.5),
        "net_interest_krw": math.floor(gross_interest - tax_withheld + 0.5),
        "calculation_assumption": assumption,
    }


def reason_counts(excluded: list[dict[str, str]]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for item in excluded:
        reason = item["reason"]
        counts[reason] = counts.get(reason, 0) + 1
    return dict(sorted(counts.items()))


def comparison_blockers(domain: str, excluded_summary: dict[str, int]) -> list[dict[str, Any]]:
    sales_not_verified = excluded_summary.get("sales_not_verified", 0)
    label = "정기예금" if domain == "deposit" else "적금"
    blockers: list[dict[str, Any]] = []
    if sales_not_verified:
        blockers.append({
            "code": "SALES_NOT_VERIFIED",
            "count": sales_not_verified,
            "message": f"판매상태가 검증되지 않은 {label}입니다.",
        })
    field_blocked = excluded_summary.get("comparison_fields_not_verified", 0)
    if field_blocked:
        blockers.append({
            "code": "COMPARISON_FIELDS_NOT_VERIFIED",
            "count": field_blocked,
            "message": f"비교 필드 검증이 끝나지 않은 {label}입니다.",
        })
    return blockers


def comparison_candidate(item: dict[str, Any], option: dict[str, Any], eligible_conditions: set[str], arguments: dict[str, Any]) -> dict[str, Any]:
    achievable, matched, unmatched, unknown = achievable_rate(option, eligible_conditions)
    base_rate = float(option["base_rate_percent"])
    candidate = {
        "item_id": item["id"],
        "title": item.get("title"),
        "provider": item.get("provider"),
        "base_rate_percent": base_rate,
        "maximum_rate_percent": float(option["maximum_rate_percent"]) if isinstance(option.get("maximum_rate_percent"), (int, float)) else base_rate,
        "achievable_rate_percent": achievable,
        "matched_preferential_conditions": matched,
        "unmatched_preferential_conditions": unmatched,
        "unknown_preferential_conditions": unknown,
        "deposit_limit": option.get("maximum_deposit_krw"),
        "monthly_payment_limit": option.get("monthly_payment_max_krw"),
        "term_months": option["term_months"],
        "saving_method": option.get("saving_method"),
        "join_channel": option.get("join_channels") or [],
        "sales_verified_at": item.get("sales_verified_at"),
        "score_components": {"achievable_rate_percent": achievable, "source_verified": 1.0},
        "source_urls": option["source_urls"],
        "source_basis_dates": item.get("source_basis_dates") or [],
        "comparison_basis_fields": item.get("comparison_basis_fields") or [],
        "comparison_field_verification_status": item.get("comparison_field_verification_status"),
        "comparison_field_verification": item.get("comparison_field_verification") or {},
        "missing_required_fields": item.get("missing_required_fields") or [],
    }
    candidate.update(interest_estimate(str(item.get("search_type")), arguments, achievable))
    return candidate


def compare(arguments: dict[str, Any], *, items: list[dict[str, Any]] | None = None, basis_date: str | None = None) -> dict[str, Any]:
    domain = str(arguments.get("domain") or "")
    if domain not in {"deposit", "saving"}:
        raise ValueError("Comparison supports only deposit and saving domains")
    if not COMPARISON_ENABLED_DOMAINS.get(domain, False):
        return {"domain": domain, "comparison_model_version": MODEL_VERSION, "comparison_engine_version": RESPONSE_CONTRACT_VERSION, "result_count": 0, "candidate_count": 0, "candidates": [], "excluded_count": 0, "excluded_summary": {}, "excluded_sample": [], "warnings": ["Deposit and saving comparison is currently disabled."]}
    if type(arguments.get("term_months")) is not int or int(arguments["term_months"]) <= 0:
        raise ValueError("term_months must be a positive integer")
    for key in ("deposit_amount_krw", "monthly_payment_krw"):
        if key in arguments and (type(arguments[key]) is not int or int(arguments[key]) <= 0):
            raise ValueError(f"{key} must be a positive integer")
    tax_rate_percent = arguments.get("tax_rate_percent", DEFAULT_INTEREST_TAX_RATE_PERCENT)
    if type(tax_rate_percent) not in (int, float) or not 0 <= float(tax_rate_percent) <= 100:
        raise ValueError("tax_rate_percent must be between 0 and 100")
    source_items = items if items is not None else load_items()
    eligible_conditions = {str(value) for value in arguments.get("eligible_conditions") or []}
    candidates: list[dict[str, Any]] = []
    excluded: list[dict[str, str]] = []
    for item in source_items:
        if item.get("search_type") != domain:
            continue
        blocker = comparison_blocker(item)
        if blocker:
            excluded.append({"item_id": str(item.get("id")), "reason": blocker})
            continue
        matching_options: list[dict[str, Any]] = []
        option_reasons: list[str] = []
        for option in item.get("comparison_options") or []:
            reason = option_blocker(option, arguments)
            if reason:
                option_reasons.append(reason)
            else:
                matching_options.append(option)
        if not matching_options:
            excluded.append({"item_id": str(item.get("id")), "reason": sorted(option_reasons or ["missing_comparison_option"])[0]})
            continue
        candidates.extend(comparison_candidate(item, option, eligible_conditions, arguments) for option in matching_options)
    candidates.sort(key=lambda candidate: (-float(candidate["achievable_rate_percent"]), str(candidate["item_id"])))
    limit = max(1, min(int(arguments.get("limit") or 10), 20))
    sorted_excluded = sorted(excluded, key=lambda item: (item["item_id"], item["reason"]))
    excluded_summary = reason_counts(sorted_excluded)
    results = candidates[:limit]
    output_basis_date = basis_date if basis_date is not None else (index_basis_date() if items is None else "")
    return {
        "domain": domain,
        "candidates": results,
        "candidate_count": len(results),
        "result_count": len(results),
        "excluded_count": len(sorted_excluded),
        "excluded_summary": excluded_summary,
        "excluded_sample": sorted_excluded[:EXCLUDED_SAMPLE_LIMIT],
        "blockers": comparison_blockers(domain, excluded_summary),
        "assumptions": ["Achievable rate includes only user-declared preferential conditions.", "Missing preferential conditions are not assumed to be satisfied."],
        "requested_intent": arguments,
        "executed_mode": "deterministic_comparison",
        "comparison_model_version": MODEL_VERSION,
        "comparison_engine_version": RESPONSE_CONTRACT_VERSION,
        "ontology_basis_date": output_basis_date,
        "latest_product_collection_date": output_basis_date,
        "verification_basis_date": output_basis_date,
        "calculation_policy_basis_date": date.today().isoformat(),
        "executed_at": date.today().isoformat(),
    }
