#!/usr/bin/env python3
from __future__ import annotations

import json
from datetime import date, timedelta
from pathlib import Path
from typing import Any

from recommendation_policy import COMPARISON_ENABLED_DOMAINS, COMPARISON_ENGINE_VERSION


ROOT = Path(__file__).resolve().parents[1]
SEARCH_INDEX = ROOT / "exports" / "finance-search-index-2026.json"
MODEL_VERSION = "openfin-comparison-v0.1.0"


def load_items(path: Path = SEARCH_INDEX) -> list[dict[str, Any]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    return [item for item in payload.get("items") or [] if isinstance(item, dict)]


def index_basis_date(path: Path = SEARCH_INDEX) -> str:
    return str(json.loads(path.read_text(encoding="utf-8")).get("basis_date") or "")


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
    if item.get("domain_gate_passed") is not True:
        return "domain_gate_not_passed"
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
    if amount is not None and maximum is not None and int(amount) > int(maximum):
        return "amount_exceeds_limit"
    payment = arguments.get("monthly_payment_krw")
    monthly_maximum = option.get("monthly_payment_max_krw")
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
    maximum_rate = float(option.get("maximum_rate_percent") or base_rate)
    return min(base_rate + additional_rate, maximum_rate), matched, unmatched, unknown


def comparison_candidate(item: dict[str, Any], option: dict[str, Any], eligible_conditions: set[str]) -> dict[str, Any]:
    achievable, matched, unmatched, unknown = achievable_rate(option, eligible_conditions)
    base_rate = float(option["base_rate_percent"])
    return {
        "item_id": item["id"],
        "title": item.get("title"),
        "provider": item.get("provider"),
        "base_rate_percent": base_rate,
        "maximum_rate_percent": float(option.get("maximum_rate_percent") or base_rate),
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
        "missing_required_fields": item.get("missing_required_fields") or [],
    }


def compare(arguments: dict[str, Any], *, items: list[dict[str, Any]] | None = None, basis_date: str | None = None) -> dict[str, Any]:
    domain = str(arguments.get("domain") or "")
    if domain not in {"deposit", "saving"}:
        raise ValueError("Comparison supports only deposit and saving domains")
    if not COMPARISON_ENABLED_DOMAINS.get(domain, False):
        return {"domain": domain, "comparison_model_version": MODEL_VERSION, "comparison_engine_version": COMPARISON_ENGINE_VERSION, "result_count": 0, "candidates": [], "excluded": [], "warnings": ["Deposit and saving comparison is currently disabled."]}
    if type(arguments.get("term_months")) is not int or int(arguments["term_months"]) <= 0:
        raise ValueError("term_months must be a positive integer")
    for key in ("deposit_amount_krw", "monthly_payment_krw"):
        if key in arguments and type(arguments[key]) is not int:
            raise ValueError(f"{key} must be an integer")
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
        candidates.extend(comparison_candidate(item, option, eligible_conditions) for option in matching_options)
    candidates.sort(key=lambda candidate: (-float(candidate["achievable_rate_percent"]), str(candidate["item_id"])))
    limit = max(1, min(int(arguments.get("limit") or 10), 20))
    return {
        "domain": domain,
        "candidates": candidates[:limit],
        "excluded": sorted(excluded, key=lambda item: (item["item_id"], item["reason"])),
        "assumptions": ["Achievable rate includes only user-declared preferential conditions.", "Missing preferential conditions are not assumed to be satisfied."],
        "comparison_model_version": MODEL_VERSION,
        "comparison_engine_version": COMPARISON_ENGINE_VERSION,
        "basis_date": basis_date if basis_date is not None else (index_basis_date() if items is None else ""),
    }
