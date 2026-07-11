"""카드 benefit 문자열을 구조화 조건 필드로 파싱한다.

"No전월실적 No연회비, 매월 최대 1만원 적립" 같은 혜택 원문에서
previous_month_spend_required, annual_fee_krw, monthly_benefit_limit_krw,
benefit_type, condition_parse_source 등을 채운다.
build_finance_ontology.py의 enrich 단계에서 호출된다.
"""
from __future__ import annotations

import re

EOK_RE = re.compile(r"(\d+(?:[,.]\d+)?)\s*억원")
CHEON_MAN_RE = re.compile(r"(\d+(?:[,.]\d+)?)\s*천만원")
COMPOUND_MONEY_RE = re.compile(r"(\d+(?:[,.]\d+)?)\s*만\s*(\d+(?:[,.]\d+)?)\s*천원")
MONEY_RE = re.compile(r"(\d+(?:[,.]\d+)?)\s*(만원|천원|원)")
BENEFIT_RATE_RE = re.compile(r"(\d+(?:\.\d+)?)\s*%")
BENEFIT_RATE_RANGE_RE = re.compile(r"(\d+(?:\.\d+)?)\s*(?:~|-|∼|～)\s*(\d+(?:\.\d+)?)\s*%")
# 공백 제거 후 매칭하는 조건 패턴
PREV_MONTH_SPEND_MIN_RE = re.compile(r"전월(?:카드)?(?:이용)?(?:실적|금액)(\d+(?:\.\d+)?)(만원|천원|원)이상")
ANNUAL_FEE_AMOUNT_RE = re.compile(r"연회비:?(\d+(?:\.\d+)?)(만원|천원|원)")
PER_TRANSACTION_RE = re.compile(r"(?:1?건당|회당)(\d+(?:\.\d+)?)(만원|천원|원)")
INTEGRATED_LIMIT_RE = re.compile(r"통합한도(?:월)?(\d+(?:\.\d+)?)(만원|천원|원)")


def parse_krw_amount(text: str) -> int | None:
    compact_text = text.replace(",", "")
    eok_match = EOK_RE.search(compact_text)
    if eok_match:
        try:
            return int(float(eok_match.group(1)) * 100_000_000)
        except ValueError:
            return None

    cheon_man_match = CHEON_MAN_RE.search(compact_text)
    if cheon_man_match:
        try:
            return int(float(cheon_man_match.group(1)) * 10_000_000)
        except ValueError:
            return None

    compound_match = COMPOUND_MONEY_RE.search(compact_text)
    if compound_match:
        man_text, cheon_text = compound_match.groups()
        try:
            return int(float(man_text) * 10000 + float(cheon_text) * 1000)
        except ValueError:
            return None

    match = MONEY_RE.search(compact_text)
    if not match:
        return None
    number_text, unit = match.groups()
    try:
        value = float(number_text)
    except ValueError:
        return None
    compact_unit = unit.replace(" ", "")
    if compact_unit == "만원":
        return int(value * 10000)
    if compact_unit == "천원":
        return int(value * 1000)
    return int(value)


def krw_amount(number_text: str, unit: str) -> int | None:
    try:
        value = float(number_text)
    except ValueError:
        return None
    if unit == "만원":
        return int(value * 10000)
    if unit == "천원":
        return int(value * 1000)
    return int(value)


def card_benefit_text(benefit: dict) -> str:
    return " ".join(
        str(benefit.get(key) or "")
        for key in ("kind", "label", "text", "benefit", "condition")
    )


def has_no_previous_month_spend(text: str) -> bool:
    compact = text.replace(" ", "").lower()
    return any(
        keyword in compact
        for keyword in (
            "no전월실적",
            "전월실적없이",
            "전월실적없음",
            "전월실적조건없이",
            "실적조건없고",
            "실적조건없음",
            "실적조건없이",
            "전월이용금액조건없음",
            "전월이용금액없음",
            "전월실적조건없음",
            "조건없이",
        )
    )


def has_no_annual_fee(text: str) -> bool:
    compact = text.replace(" ", "").lower()
    return any(keyword in compact for keyword in ("no연회비", "연회비없음", "연회비면제"))


def benefit_type(text: str) -> str | None:
    if any(keyword in text for keyword in ("적립", "포인트", "마일리지", "캐시백")):
        return "point_accumulation"
    if any(keyword in text for keyword in ("할인", "환급할인", "청구할인", "즉시할인")):
        return "discount"
    if "면제" in text:
        return "fee_waiver"
    return None


def monthly_benefit_limit_krw(text: str) -> int | None:
    compact = text.replace(" ", "")
    if "월" not in compact and "매월" not in compact:
        return None
    if not any(keyword in compact for keyword in ("최대", "한도")):
        return None
    return parse_krw_amount(text)


def has_unlimited_monthly_limit(text: str) -> bool:
    compact = text.replace(" ", "")
    return any(
        keyword in compact
        for keyword in (
            "한도없이",
            "한도없는",
            "한도도없는",
            "적립한도없",
            "할인한도없",
        )
    )


def card_benefit_rate_percent(text: str) -> float | None:
    match = BENEFIT_RATE_RE.search(text)
    return float(match.group(1)) if match else None


def card_benefit_rate_range(text: str) -> tuple[float, float] | None:
    match = BENEFIT_RATE_RANGE_RE.search(text)
    if not match:
        return None
    lower, upper = (float(value) for value in match.groups())
    return min(lower, upper), max(lower, upper)


def benefit_categories(text: str) -> list[str]:
    categories = []
    for keyword in (
        "커피",
        "점심",
        "저녁",
        "쇼핑",
        "학원",
        "영화",
        "대중교통",
        "병원",
        "약국",
        "주유",
        "백화점",
        "해외",
        "편의점",
        "다이소",
        "통신",
        "구독",
        "온라인",
        "서점",
        "외식",
        "카페",
    ):
        if keyword in text:
            categories.append(keyword)
    return categories


def excluded_spend(text: str) -> list[str]:
    if "제외" not in text.replace(" ", ""):
        return []
    return [
        category
        for category in ("상품권", "세금", "국세", "지방세", "공과금", "관리비")
        if category in text
    ]


def condition_source_url(item: dict) -> str | None:
    urls = [str(url) for url in item.get("source_urls") or [] if str(url).startswith("https://")]
    return next(
        (
            url
            for url in urls
            if re.search(r"(?:gdsno|cooperationcode|cardNo|cardCode)=", url, flags=re.IGNORECASE)
        ),
        next((url for url in urls if "cardDetail" in url), urls[0] if urls else None),
    )


def enrich_card_benefits(item: dict) -> None:
    if item.get("type") != "card-product":
        return
    source_url = condition_source_url(item)
    for benefit in item.get("benefits") or []:
        if not isinstance(benefit, dict):
            continue
        text = card_benefit_text(benefit)
        compact = text.replace(",", "").replace(" ", "")
        if has_no_previous_month_spend(text):
            benefit["previous_month_spend_required"] = False
            benefit["previous_month_spend_min_krw"] = 0
        elif (spend_match := PREV_MONTH_SPEND_MIN_RE.search(compact)):
            benefit["previous_month_spend_required"] = True
            benefit["previous_month_spend_min_krw"] = krw_amount(*spend_match.groups())
        else:
            benefit.setdefault("previous_month_spend_required", None)
        benefit.setdefault("previous_month_spend_min_krw", None)
        parsed_monthly_limit = monthly_benefit_limit_krw(text)
        if parsed_monthly_limit is None and (limit_match := INTEGRATED_LIMIT_RE.search(compact)):
            parsed_monthly_limit = krw_amount(*limit_match.groups())
        if parsed_monthly_limit is not None:
            benefit["monthly_benefit_limit_krw"] = parsed_monthly_limit
        else:
            benefit.setdefault("monthly_benefit_limit_krw", None)
        if has_no_annual_fee(text):
            benefit["annual_fee_required"] = False
            benefit["annual_fee_krw"] = 0
        elif (fee_match := ANNUAL_FEE_AMOUNT_RE.search(compact)):
            benefit["annual_fee_required"] = True
            benefit["annual_fee_krw"] = krw_amount(*fee_match.groups())
        else:
            benefit.setdefault("annual_fee_required", None)
        benefit.setdefault("annual_fee_krw", None)
        parsed_benefit_type = benefit_type(text)
        if parsed_benefit_type:
            benefit["benefit_type"] = parsed_benefit_type
        else:
            benefit.setdefault("benefit_type", None)
        parsed_rate = card_benefit_rate_percent(text)
        if parsed_rate is not None:
            benefit["benefit_rate_percent"] = parsed_rate
        else:
            benefit.setdefault("benefit_rate_percent", None)
        parsed_rate_range = card_benefit_rate_range(text)
        if parsed_rate_range is not None:
            benefit["benefit_rate_min_percent"] = parsed_rate_range[0]
            benefit["benefit_rate_max_percent"] = parsed_rate_range[1]
        else:
            benefit.setdefault("benefit_rate_min_percent", benefit.get("benefit_rate_percent"))
            benefit.setdefault("benefit_rate_max_percent", benefit.get("benefit_rate_percent"))
        if (per_tx_match := PER_TRANSACTION_RE.search(compact)):
            benefit["per_transaction_limit_krw"] = krw_amount(*per_tx_match.groups())
        benefit.setdefault("per_transaction_limit_krw", None)
        if has_unlimited_monthly_limit(text):
            benefit["monthly_benefit_limit_krw"] = None
            benefit["monthly_benefit_limit_unlimited"] = True
        else:
            benefit.setdefault("monthly_benefit_limit_unlimited", False)
        if benefit.get("benefit_type") in {"discount", "point_accumulation"} and parsed_monthly_limit is None:
            benefit.setdefault("fixed_benefit_amount_krw", parse_krw_amount(text))
        else:
            benefit.setdefault("fixed_benefit_amount_krw", None)
        benefit["benefit_categories"] = benefit_categories(text)
        parsed_excluded_spend = excluded_spend(text)
        if parsed_excluded_spend:
            benefit["excluded_spend"] = parsed_excluded_spend
        else:
            benefit.setdefault("excluded_spend", [])
        missing = []
        for key in ("previous_month_spend_min_krw", "monthly_benefit_limit_krw", "per_transaction_limit_krw", "excluded_spend"):
            if key == "monthly_benefit_limit_krw" and benefit.get("monthly_benefit_limit_unlimited") is True:
                continue
            value = benefit.get(key)
            if value is None or value == "" or value == []:
                missing.append(key)
        normalized = any(
            benefit.get(key) is not None and benefit.get(key) != "" and benefit.get(key) != []
            for key in ("previous_month_spend_min_krw", "monthly_benefit_limit_krw", "annual_fee_required", "benefit_type", "benefit_rate_percent")
        )
        benefit["condition_completeness"] = "partial" if missing and normalized else ("incomplete" if missing else "complete")
        benefit["missing_condition_fields"] = missing
        benefit["condition_parse_source"] = "benefit_text" if normalized else None
        benefit["condition_source_url"] = source_url
        benefit["condition_source_locator"] = item.get("source_record_id")


def apply_card_recommendation_scope(item: dict) -> None:
    if item.get("type") != "card-product":
        return
    partial_or_incomplete = any(
        isinstance(benefit, dict)
        and benefit.get("condition_completeness") in {"partial", "incomplete"}
        for benefit in item.get("benefits") or []
    )
    if partial_or_incomplete:
        item["recommendation_status"] = "reference_only"
        item["recommendation_scope"] = "listing_only"
        item["recommendation_exclusion_reasons"] = sorted({
            *(item.get("recommendation_exclusion_reasons") or []),
            "incomplete_card_benefit_conditions",
        })


def demo() -> None:
    benefit = {"kind": "main", "text": "No전월실적 No연회비, 매월 최대 1만원 적립"}
    item = {"type": "card-product", "benefits": [benefit]}
    enrich_card_benefits(item)
    assert benefit["previous_month_spend_required"] is False
    assert benefit["previous_month_spend_min_krw"] == 0
    assert benefit["annual_fee_required"] is False
    assert benefit["annual_fee_krw"] == 0
    assert benefit["monthly_benefit_limit_krw"] == 10000
    assert benefit["benefit_type"] == "point_accumulation"
    assert benefit["condition_completeness"] == "partial"
    assert benefit["condition_parse_source"] == "benefit_text"
    print("card_benefit_parser demo OK")


if __name__ == "__main__":
    demo()
