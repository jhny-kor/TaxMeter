#!/usr/bin/env python3
from __future__ import annotations

from typing import Any

from recommendation_intent_parser import parse_query
from recommendation_policy import DISCOVERY_ENABLED_DOMAINS, DISCOVERY_ENGINE_VERSION, FIELD_EXTRACTOR_VERSION


ENGINE_VERSION = DISCOVERY_ENGINE_VERSION


def is_discovery_query(query: str) -> bool:
    return parse_query(query)["intent"] == "discovery"


def domain_for_item(item: dict[str, Any]) -> str | None:
    if item.get("type") == "card-product":
        return "card"
    if item.get("type") == "insurance-product":
        return "insurance"
    search_type = item.get("search_type")
    return str(search_type) if search_type in {"deposit", "saving", "loan"} else None


def values(item: dict[str, Any], field: str) -> list[Any]:
    direct = item.get(field)
    if direct not in (None, "", [], {}):
        return direct if isinstance(direct, list) else [direct]
    summary = item.get("structured_summary") or {}
    found: list[Any] = []
    for section in summary.values() if isinstance(summary, dict) else []:
        if isinstance(section, dict) and section.get(field) not in (None, "", [], {}):
            value = section[field]
            found.extend(value if isinstance(value, list) else [value])
    for option in item.get("comparison_options") or []:
        if isinstance(option, dict) and option.get(field) not in (None, "", [], {}):
            value = option[field]
            found.extend(value if isinstance(value, list) else [value])
    return found


def text(item: dict[str, Any]) -> str:
    return " ".join(str(value or "") for value in (item.get("title"), item.get("description"), item.get("product_kind"), item.get("search_text"), *(item.get("search_aliases") or []))).casefold()


def current_listed(item: dict[str, Any]) -> bool:
    return item.get("status") == "active" and item.get("product_status") == "active" and item.get("source_listing_status") == "listed" and item.get("source_freshness_status") != "stale" and bool(item.get("source_urls"))


def grade_data(item: dict[str, Any]) -> str:
    ratio = float(item.get("normalized_completeness_ratio") or item.get("completeness_ratio") or 0)
    if ratio >= 0.9:
        return "A"
    if ratio >= 0.7:
        return "B"
    if ratio >= 0.4:
        return "C"
    return "D"


def grade_verification(item: dict[str, Any]) -> str:
    if item.get("sales_verification_status") == "verified_active" and item.get("verification_status") == "verified" and float(item.get("verified_completeness_ratio") or 0) == 1:
        return "A"
    if item.get("verification_status") == "verified":
        return "B"
    if item.get("source_urls"):
        return "C"
    return "D"


def constraint_state(item: dict[str, Any], constraint: dict[str, Any]) -> str:
    field, expected = str(constraint["field"]), constraint["value"]
    if field == "product_kind":
        kind = str(item.get("product_kind") or "")
        if kind == expected or (expected == "rent-loan" and kind == "policy-loan" and "전세" in text(item)):
            return "matched"
        return "failed"
    if field == "employment_type":
        candidate_text = text(item)
        return "matched" if any(token in candidate_text for token in ("직장인", "재직자", "근로소득자")) else "unknown"
    if field == "term_months":
        terms = values(item, "term_months") or values(item, "terms")
        return "matched" if expected in terms or str(expected) in {str(value) for value in terms} else "unknown"
    if field in {"deposit_amount_krw", "monthly_payment_krw"}:
        limits = values(item, "maximum_deposit_krw") if field == "deposit_amount_krw" else values(item, "monthly_payment_max_krw")
        if not limits:
            return "unknown"
        return "matched" if any(isinstance(value, (int, float)) and value >= expected for value in limits) else "failed"
    candidates = values(item, field)
    if not candidates:
        return "unknown"
    if field == "renewal_type":
        return "matched" if expected in {str(value).replace("nonrenewable", "non_renewable") for value in candidates} else "failed"
    if expected == 0:
        return "matched" if 0 in candidates else "failed"
    return "matched" if expected in candidates else "failed"


def benefit_state(item: dict[str, Any], preference: str) -> str:
    candidate_text = text(item)
    tokens = {"마일리지": ("마일", "mileage"), "구독": ("구독", "subscription"), "교통": ("교통",), "쇼핑": ("쇼핑",), "온라인": ("온라인",)}
    return "matched" if any(token in candidate_text for token in tokens.get(preference, (preference,))) else "unknown"


def decision(item: dict[str, Any], parsed: dict[str, Any]) -> tuple[str, dict[str, Any]]:
    if not current_listed(item):
        return "excluded", {"reason": "inactive_or_unlisted"}
    if domain_for_item(item) != parsed["domain"]:
        return "excluded", {"reason": "domain_mismatch"}
    states = {str(constraint["field"]): constraint_state(item, constraint) for constraint in parsed["hard_constraints"]}
    preference_states = {preference: benefit_state(item, preference) for preference in parsed["soft_preferences"]}
    failed = [field for field, state in states.items() if state == "failed"]
    unknown = [field for field, state in {**states, **preference_states}.items() if state == "unknown"]
    matched = [field for field, state in {**states, **preference_states}.items() if state == "matched"]
    if failed:
        eligibility = "related_candidate" if "product_kind" in failed else "excluded"
    elif unknown:
        eligibility = "partial_candidate"
    else:
        eligibility = "exact_candidate"
    relevance = "A" if eligibility == "exact_candidate" else ("B" if eligibility == "partial_candidate" else "D")
    verification = grade_verification(item)
    overall = max(relevance, verification)
    if item.get("sales_verification_status") == "listed_unverified" or not item.get("domain_gate_passed") or float(item.get("verified_completeness_ratio") or 0) == 0:
        overall = max(overall, "C")
    why = [{"constraint": field, "matched_value": item.get("product_kind") if field == "product_kind" else field, "evidence_field": field} for field in matched]
    payload = {"mode": "discovery", "eligibility": eligibility, "decision_scope": "discovery_only", "score": len(matched) * 10 + round(float(item.get("normalized_completeness_ratio") or 0) * 10), "relevance_grade": relevance, "data_completeness_grade": grade_data(item), "verification_grade": verification, "overall_candidate_grade": overall, "matched_constraints": matched, "unknown_constraints": unknown, "failed_constraints": failed, "decision_reasons": why, "limitations": item.get("discovery_limitations") or ["sales_status_unverified"]}
    if eligibility == "excluded":
        payload["reason"] = "hard_constraint_failed"
    return eligibility, payload


def candidate(item: dict[str, Any], decision_data: dict[str, Any]) -> dict[str, Any]:
    return {"canonical_product_id": item.get("canonical_product_id") or item.get("id"), "id": item.get("id"), "title": item.get("title"), "provider": item.get("provider"), "product_kind": item.get("product_kind"), "catalog_recommendation_status": item.get("catalog_recommendation_status") or item.get("recommendation_status"), "catalog_recommendation_scope": item.get("catalog_recommendation_scope") or item.get("recommendation_scope"), "relevance_grade": decision_data["relevance_grade"], "data_completeness_grade": decision_data["data_completeness_grade"], "verification_grade": decision_data["verification_grade"], "overall_candidate_grade": decision_data["overall_candidate_grade"], "matched_constraints": decision_data["matched_constraints"], "unknown_constraints": decision_data["unknown_constraints"], "failed_constraints": decision_data["failed_constraints"], "why_included": decision_data["decision_reasons"], "limitations": decision_data["limitations"], "source_urls": item.get("source_urls") or [], "source_basis_dates": item.get("source_basis_dates") or [], "decision": decision_data}


def discover(query: str, items: list[dict[str, Any]], limit: int = 10) -> dict[str, Any]:
    parsed = parse_query(query)
    groups = {"exact_candidates": [], "partial_candidates": [], "related_candidates": []}
    if not DISCOVERY_ENABLED_DOMAINS.get(str(parsed["domain"]), False):
        return {"requested_intent": parsed["intent"], "executed_mode": "discovery", "fallback_reason": "discovery_domain_disabled", "parsed_query": parsed, **groups, "excluded_summary": {}, "warnings": ["이 도메인의 탐색은 현재 비활성화되어 있습니다."], "basis_date": None, "engine_version": ENGINE_VERSION, "field_extractor_version": FIELD_EXTRACTOR_VERSION}
    excluded: dict[str, int] = {}
    seen: set[str] = set()
    for item in items:
        eligibility, data = decision(item, parsed)
        if eligibility == "excluded":
            reason = str(data["reason"])
            excluded[reason] = excluded.get(reason, 0) + 1
            continue
        result = candidate(item, data)
        canonical_id = str(result["canonical_product_id"])
        if canonical_id in seen:
            excluded["duplicate_canonical_product"] = excluded.get("duplicate_canonical_product", 0) + 1
            continue
        seen.add(canonical_id)
        groups[f"{eligibility}s"].append(result)
    for values_ in groups.values():
        values_.sort(key=lambda value: (-int(value["decision"]["score"]), str(value["canonical_product_id"])))
        del values_[limit:]
    requested_intent = "recommend" if any(token in query for token in ("추천", "골라", "알려", "찾아")) else parsed["intent"]
    return {"requested_intent": requested_intent, "executed_mode": "discovery", "fallback_reason": "verified_recommendation_candidate_not_available" if requested_intent == "recommend" else None, "parsed_query": parsed, **groups, "excluded_summary": excluded, "warnings": ["탐색 결과는 최적 상품·승인·보험료·보장 적합성을 뜻하지 않습니다."], "basis_date": None, "engine_version": ENGINE_VERSION, "field_extractor_version": FIELD_EXTRACTOR_VERSION}
