"""보험 coverage 조건 필드화와 추천 승격 금지 가드.

보장금액·갱신주기·면책기간·감액기간이 비어 있는(incomplete) coverage를 가진 상품은
eligible_for_recommendation이 될 수 없고 listing_only 범위로 제한된다.
"""
from __future__ import annotations

import re

from card_benefit_parser import parse_krw_amount

RENEWAL_CYCLE_RE = re.compile(r"(\d+)\s*년\s*갱신")


def premium_basis_amount(options: list[dict]) -> int | None:
    amounts = [
        amount
        for option in options
        if isinstance(option, dict)
        and (amount := parse_krw_amount(str(option.get("premium_amount") or ""))) is not None
    ]
    return max(amounts) if amounts else None


def renewal_cycle_years(renewal_text: str, renewal_type: str | None) -> int | None:
    if renewal_type == "non_renewable":
        return 0
    match = RENEWAL_CYCLE_RE.search(renewal_text)
    return int(match.group(1)) if match else None


def enrich_insurance_coverage(item: dict) -> None:
    if item.get("type") != "insurance-product":
        return
    options = [option for option in item.get("options") or [] if isinstance(option, dict)]
    criteria = [criterion for criterion in item.get("criteria") or [] if isinstance(criterion, dict)]
    premium = next((criterion for criterion in criteria if criterion.get("criteria_kind") == "premium"), {})
    renewal = next((criterion for criterion in criteria if criterion.get("criteria_kind") == "renewal"), {})
    renewal_text = str(renewal.get("condition") or "")
    renewal_type = None
    if "비갱신" in renewal_text:
        renewal_type = "non_renewable"
    elif "갱신" in renewal_text:
        renewal_type = "renewable"
    amount = premium_basis_amount(options)
    cycle_years = renewal_cycle_years(renewal_text, renewal_type)
    source_urls = [str(url) for url in item.get("source_urls") or [] if str(url).startswith("https://")]
    source_url = source_urls[0] if source_urls else None
    for criterion in criteria:
        if criterion.get("criteria_kind") != "coverage":
            continue
        criterion.setdefault("coverage_name", criterion.get("benefit") or criterion.get("condition") or criterion.get("label"))
        criterion.setdefault("coverage_amount_krw", None)
        criterion.setdefault("coverage_amount_basis", None)
        criterion.setdefault("disclosed_insured_amount_krw", amount)
        criterion.setdefault("disclosed_insured_amount_basis", "association_premium_basis_amount" if amount is not None else None)
        criterion.setdefault("premium_male_krw", premium.get("premium_male_krw"))
        criterion.setdefault("premium_female_krw", premium.get("premium_female_krw"))
        criterion.setdefault("renewal_type", renewal_type)
        criterion.setdefault("renewal_cycle_years", cycle_years)
        criterion.setdefault("waiting_period_days", None)
        criterion.setdefault("reduction_period_days", None)
        criterion.setdefault("claim_condition", None)
        criterion.setdefault("exclusion_condition", None)
        criterion.setdefault("condition_source_url", source_url)
        criterion.setdefault("condition_source_locator", item.get("source_record_id"))
        missing = [
            key
            for key in (
                "coverage_amount_krw",
                "renewal_cycle_years",
                "waiting_period_days",
                "reduction_period_days",
                "claim_condition",
                "exclusion_condition",
            )
            if criterion.get(key) is None
        ]
        criterion["condition_completeness"] = "incomplete" if missing else "complete"
        criterion["missing_condition_fields"] = missing


def apply_insurance_recommendation_guard(item: dict) -> None:
    if item.get("type") != "insurance-product":
        return
    coverage_criteria = [
        criterion
        for criterion in item.get("criteria") or []
        if isinstance(criterion, dict) and criterion.get("criteria_kind") == "coverage"
    ]
    incomplete = any(
        criterion.get("condition_completeness") == "incomplete"
        for criterion in coverage_criteria
    )
    if item.get("status") == "active" and coverage_criteria and not incomplete:
        item["recommendation_status"] = "recommendation_candidate"
        item["recommendation_scope"] = "criteria_match_only"
        return
    item["recommendation_scope"] = "listing_only"
    item["recommendation_exclusion_reasons"] = sorted({
        *(item.get("recommendation_exclusion_reasons") or []),
        "incomplete_insurance_coverage_conditions" if coverage_criteria else "missing_insurance_coverage_criteria",
    })
    # 핵심 조건(보장금액·갱신주기·면책·감액)이 비어 있으면 추천 승격을 금지한다.
    item["recommendation_status"] = "reference_only"
