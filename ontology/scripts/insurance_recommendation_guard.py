"""보험 coverage 조건 필드화와 추천 승격 금지 가드.

보장금액·갱신주기·면책기간·감액기간이 비어 있는(incomplete) coverage를 가진 상품은
eligible_for_recommendation이 될 수 없고 listing_only 범위로 제한된다.
"""
from __future__ import annotations


def enrich_insurance_coverage(item: dict) -> None:
    if item.get("type") != "insurance-product":
        return
    criteria = [criterion for criterion in item.get("criteria") or [] if isinstance(criterion, dict)]
    premium = next((criterion for criterion in criteria if criterion.get("criteria_kind") == "premium"), {})
    renewal = next((criterion for criterion in criteria if criterion.get("criteria_kind") == "renewal"), {})
    renewal_text = str(renewal.get("condition") or "")
    renewal_type = None
    if "비갱신" in renewal_text:
        renewal_type = "non_renewable"
    elif "갱신" in renewal_text:
        renewal_type = "renewable"
    for criterion in criteria:
        if criterion.get("criteria_kind") != "coverage":
            continue
        criterion.setdefault("coverage_name", criterion.get("benefit") or criterion.get("condition") or criterion.get("label"))
        criterion.setdefault("coverage_amount_krw", None)
        criterion.setdefault("premium_male_krw", premium.get("premium_male_krw"))
        criterion.setdefault("premium_female_krw", premium.get("premium_female_krw"))
        criterion.setdefault("renewal_type", renewal_type)
        criterion.setdefault("renewal_cycle_years", None)
        criterion.setdefault("waiting_period_days", None)
        criterion.setdefault("reduction_period_days", None)
        missing = [
            key
            for key in ("coverage_amount_krw", "renewal_cycle_years", "waiting_period_days", "reduction_period_days")
            if criterion.get(key) is None
        ]
        criterion["condition_completeness"] = "incomplete" if missing else "complete"
        criterion["missing_condition_fields"] = missing


def apply_insurance_recommendation_guard(item: dict) -> None:
    if item.get("type") != "insurance-product":
        return
    incomplete = any(
        isinstance(criterion, dict)
        and criterion.get("criteria_kind") == "coverage"
        and criterion.get("condition_completeness") == "incomplete"
        for criterion in item.get("criteria") or []
    )
    if not incomplete:
        return
    item["recommendation_scope"] = "listing_only"
    item["recommendation_exclusion_reasons"] = sorted({
        *(item.get("recommendation_exclusion_reasons") or []),
        "incomplete_insurance_coverage_conditions",
    })
    # 핵심 조건(보장금액·갱신주기·면책·감액)이 비어 있으면 추천 승격을 금지한다.
    if item.get("recommendation_status") == "eligible_for_recommendation":
        item["recommendation_status"] = "eligible_for_listing"
