"""대출 상품 필수 조건 필드 정규화.

FSS 금융상품한눈에·서민금융진흥원 공시 원문(criteria/options/raw)에서
금리·상환방식·한도·중도상환수수료·대출대상·담보유형·금리유형을 최상위 필드로 옮기고,
필수 필드가 하나라도 없으면 추천·목록 승격을 금지(reference_only)한다.
"""
from __future__ import annotations

import datetime as dt
import re
from typing import assert_never

from card_benefit_parser import parse_krw_amount

LOAN_REQUIRED_FIELDS = (
    "loan_rate_min_percent",
    "loan_rate_max_percent",
    "repayment_method",
    "loan_limit_krw",
    "early_repayment_fee",
    "eligible_borrower",
    "collateral_type",
    "rate_type",
    "total_loan_period",
    "handling_institution",
    "operating_period_status",
    "loan_limit_normalization_status",
    "loan_grace_period",
    "guarantee_fee",
    "loan_purpose",
    "official_application_url",
)
RATE_NUMBER_RE = re.compile(r"(\d+(?:\.\d+)?)")
LOAN_LIMIT_AMOUNT_RE = re.compile(r"(\d+(?:[,.]\d+)?)\s*(억원|천만원|만원|천원|원)")
EMPTY_TEXTS = {"", "-", "해당없음", "없음정보"}
CONDITIONAL_LOAN_LIMIT_MARKERS = ("담보", "보증금", "평가액", "소득", "비율", "%", "수도권", "지방", "신혼", "자녀")
OPERATING_PERIOD_DATE_RE = re.compile(r"(20\d{2})\s*[.\-/년]\s*(\d{1,2})\s*[.\-/월]\s*(\d{1,2})")
OPERATING_PERIOD_YEAR_RE = re.compile(r"(20\d{2})\s*년")


def unique(values) -> list[str]:
    return [value for value in dict.fromkeys(values) if value]


def raw_text(raw: dict, *keys: str) -> str | None:
    for key in keys:
        value = str(raw.get(key) or "").strip()
        if value and value not in EMPTY_TEXTS:
            return value
    return None


def option_text(options: list[dict], key: str) -> str | None:
    values = unique(str(option.get(key) or "").strip() for option in options)
    values = [value for value in values if value and value not in EMPTY_TEXTS]
    return ", ".join(values) if values else None


def parse_loan_limit_krw(text: str) -> int | None:
    values = []
    compact = text.replace(",", "")
    for number_text, unit in LOAN_LIMIT_AMOUNT_RE.findall(compact):
        try:
            value = float(number_text)
        except ValueError:
            continue
        match unit:
            case "억원":
                values.append(int(value * 100_000_000))
            case "천만원":
                values.append(int(value * 10_000_000))
            case "만원":
                values.append(int(value * 10_000))
            case "천원":
                values.append(int(value * 1_000))
            case "원":
                values.append(int(value))
            case unreachable:
                assert_never(unreachable)
    return max(values) if values else parse_krw_amount(text)


def rate_values_from_text(text: str) -> list[float]:
    return [float(value) for value in RATE_NUMBER_RE.findall(text)]


def rate_type_from_text(text: str) -> str | None:
    if "고정" in text:
        return "고정금리"
    if "변동" in text:
        return "변동금리"
    if "%" in text and any(keyword in text for keyword in ("대상", "구간", "~", "별", "차등")):
        return "대상별 차등금리"
    return None


def operating_period_status(text: str | None, reviewed_at: str | None) -> str:
    compact = str(text or "").replace(" ", "")
    if not compact:
        return "unverified"
    if "상시" in compact:
        return "confirmed_open"
    try:
        review_date = dt.date.fromisoformat(str(reviewed_at or ""))
    except ValueError:
        return "unverified"
    dates: list[dt.date] = []
    for year_text, month_text, day_text in OPERATING_PERIOD_DATE_RE.findall(compact):
        try:
            dates.append(dt.date(int(year_text), int(month_text), int(day_text)))
        except ValueError:
            continue
    if len(dates) >= 2:
        start_date, end_date = min(dates), max(dates)
        if end_date < review_date:
            return "expired"
        if start_date <= review_date <= end_date:
            return "confirmed_open"
    years = [int(year) for year in OPERATING_PERIOD_YEAR_RE.findall(compact)]
    if len(years) >= 2:
        start_year, end_year = min(years), max(years)
        if end_year < review_date.year:
            return "expired"
        if start_year <= review_date.year <= end_year:
            return "confirmed_open"
    return "unverified"


def operating_period_end(text: str | None) -> str | None:
    compact = str(text or "").replace(" ", "")
    dates: list[dt.date] = []
    for year_text, month_text, day_text in OPERATING_PERIOD_DATE_RE.findall(compact):
        try:
            dates.append(dt.date(int(year_text), int(month_text), int(day_text)))
        except ValueError:
            continue
    return max(dates).isoformat() if len(dates) >= 2 else None


def official_application_url(raw: dict) -> str | None:
    source_text = raw_text(raw, "rltsite", "relatedSite", "siteUrl")
    if not source_text:
        return None
    match = re.search(r"https?://[^\s,)]+|www\.[^\s,)]+", source_text)
    if not match:
        return None
    url = match.group(0)
    return url if url.startswith("http") else f"https://{url}"


def is_recommendation_ready_loan(item: dict) -> bool:
    return (
        item.get("status") == "active"
        and bool(item.get("criteria"))
        and not item.get("missing_loan_required_fields")
        and item.get("operating_period_status") == "confirmed_open"
        and item.get("loan_limit_normalization_status") == "verified"
        and "source_domain_reclassified" not in (item.get("quality_flags") or [])
    )


def collateral_type_from_product(item: dict, options: list[dict]) -> str | None:
    product_kind = str(item.get("product_kind") or "")
    title = str(item.get("title") or "")
    guarantee_institution = raw_text(item.get("raw") if isinstance(item.get("raw"), dict) else {}, "grninst")
    if product_kind == "credit-loan":
        return "신용(무담보)"
    if product_kind == "mortgage-loan" or "주택담보" in title or "보금자리론" in title:
        return "주택담보"
    if product_kind == "rent-loan" or "전세" in title:
        return "전세보증금"
    if guarantee_institution:
        return f"보증부({guarantee_institution})"
    if option_text(options, "eligibility") and "햇살론" in title:
        return "보증부(정책금융)"
    return None


def synthesize_credit_loan_rate_criteria(item: dict) -> None:
    """신용대출은 FSS optionList의 등급별 금리만 있고 criteria가 비어 있다.
    공시된 대출금리(crdt_grad_*)의 최저·최고값을 rate criteria로 옮겨 담는다."""
    if item.get("product_kind") != "credit-loan" or item.get("criteria"):
        return
    rates = [
        value
        for option in item.get("options") or []
        if isinstance(option, dict) and option.get("crdt_lend_rate_type_nm") == "대출금리"
        for key, value in option.items()
        if key.startswith("crdt_grad_") and isinstance(value, (int, float))
    ]
    if not rates:
        return
    item["criteria"] = [
        {
            "label": label,
            "basis": "신용등급별 대출금리",
            "condition": f"{label} {value}%",
            "source": "source.fss.finlife.api",
            "criteria_kind": "rate",
            "basis_category": "금융상품 공시 금리",
            "basis_definition": "금융감독원 금융상품한눈에 API의 신용대출 등급별 금리 필드입니다.",
            "basis_lookup": "creditLoanProductsSearch optionList의 crdt_grad_* 필드에서 확인합니다.",
            "selection_rule": "공시된 신용등급별 대출금리의 최저·최고값입니다.",
            "basis_source": "source.fss.finlife.api",
            "rate_percent": value,
            "rate_label": label,
            "rate_basis": "신용등급별",
        }
        for label, value in (("최저금리", min(rates)), ("최고금리", max(rates)))
    ]


def normalize_loan_product(item: dict) -> None:
    if item.get("type") != "bank-product" or item.get("search_type") != "loan":
        return
    synthesize_credit_loan_rate_criteria(item)
    raw = item.get("raw") if isinstance(item.get("raw"), dict) else {}
    options = [option for option in item.get("options") or [] if isinstance(option, dict)]
    criteria = [criterion for criterion in item.get("criteria") or [] if isinstance(criterion, dict)]

    rates = [criterion["rate_percent"] for criterion in criteria if isinstance(criterion.get("rate_percent"), (int, float))]
    rates += [option[key] for option in options for key in ("lend_rate_min", "lend_rate_max") if isinstance(option.get(key), (int, float))]
    if not rates:
        rates = [float(value) for value in RATE_NUMBER_RE.findall(str(raw.get("irt") or ""))]
    if not rates:
        rates = [
            value
            for option in options
            if (rate_text := str(option.get("rate") or ""))
            for value in rate_values_from_text(rate_text)
        ]
    item["loan_rate_min_percent"] = min(rates) if rates else None
    item["loan_rate_max_percent"] = max(rates) if rates else None

    rate_types = unique([str(option["lend_rate_type_nm"]) for option in options if option.get("lend_rate_type_nm")])
    if not rate_types:
        rate_type = raw_text(raw, "lend_rate_type")
        if rate_type:
            rate_types = [rate_type]
    if not rate_types:
        rate_types = unique([str(option["crdt_lend_rate_type_nm"]) for option in options if option.get("crdt_lend_rate_type_nm")])
    if not rate_types:
        irt_category = raw_text(raw, "irtCtg", "irtctg")
        if irt_category:
            rate_types = [irt_category]
    if not rate_types:
        rate_type = rate_type_from_text(option_text(options, "rate") or "")
        if rate_type:
            rate_types = [rate_type]
    item["rate_type"] = ", ".join(rate_types) if rate_types else None

    repayment = unique([str(option["rpay_type_nm"]) for option in options if option.get("rpay_type_nm")])
    if not repayment:
        repayment_text = raw_text(raw, "rpay_type")
        if repayment_text:
            repayment = [repayment_text]
    if not repayment:
        repayment_text = raw_text(raw, "rdptmthd")
        if repayment_text:
            repayment = [repayment_text]
    if not repayment:
        repayment_text = option_text(options, "repayment_method")
        if repayment_text:
            repayment = [repayment_text]
    item["repayment_method"] = ", ".join(repayment) if repayment else None

    kinfa_limit_text = raw_text(raw, "lnlmt") or ""
    limit_text = raw_text(raw, "loan_lmt") or kinfa_limit_text or option_text(options, "loan_limit") or ""
    if limit_text == "기타":
        limit_text = raw_text(raw, "loan_limit_detl") or limit_text
    limit_krw = None
    limit_unit = None
    limit_normalization_status = "unverified"
    limit_normalization_source = None
    if kinfa_limit_text and kinfa_limit_text.isdigit():
        # 서민금융진흥원 lnlmt는 만원 단위 숫자 문자열이다.
        limit_krw = int(kinfa_limit_text) * 10000
        limit_unit = "만원"
        limit_normalization_status = "verified"
        limit_normalization_source = "official_api_schema"
    elif limit_text.isdigit():
        limit_normalization_status = "ambiguous"
    elif limit_text:
        limit_krw = parse_loan_limit_krw(limit_text)
        amount_values = LOAN_LIMIT_AMOUNT_RE.findall(limit_text.replace(",", ""))
        has_multiple_limits = len({amount for amount, _ in amount_values}) > 1
        limit_normalization_status = (
            "ambiguous"
            if limit_krw is not None and (
                has_multiple_limits or any(marker in limit_text for marker in CONDITIONAL_LOAN_LIMIT_MARKERS)
            )
            else "verified" if limit_krw is not None else "unverified"
        )
    if limit_normalization_status != "verified":
        limit_krw = None
    item["loan_limit_krw"] = limit_krw
    item["loan_limit_text"] = limit_text or None
    item["loan_limit_unit"] = limit_unit
    item["loan_limit_normalization_status"] = limit_normalization_status
    item["loan_limit_normalization_source"] = limit_normalization_source
    item["limit_raw"] = limit_text or None
    item["limit_unit"] = limit_unit
    item["limit_krw"] = limit_krw
    item["normalization_status"] = limit_normalization_status
    item["normalization_source"] = limit_normalization_source

    item["early_repayment_fee"] = raw_text(raw, "erly_rpay_fee", "rpymdcfe") or option_text(options, "fee")

    eligible_borrower = raw_text(raw, "trgt", "crdt_prdt_type_nm", "join_deny_detl") or option_text(options, "eligibility")
    item["eligible_borrower"] = None if eligible_borrower in {"제한없음", "-"} else eligible_borrower

    collateral = unique([str(option["mrtg_type_nm"]) for option in options if option.get("mrtg_type_nm")])
    if collateral:
        item["collateral_type"] = ", ".join(collateral)
    else:
        item["collateral_type"] = collateral_type_from_product(item, options)

    item["total_loan_period"] = raw_text(raw, "maxTotLnTrm") or option_text(options, "total_loan_period_years")
    item["loan_grace_period"] = raw_text(raw, "maxDfrmTrm", "maxdfrmtrm")
    item["guarantee_fee"] = raw_text(raw, "lnicdcst", "guarantee_fee") or option_text(options, "guarantee_fee")
    item["loan_purpose"] = raw_text(raw, "usge", "purpose") or option_text(options, "purpose")
    item["official_application_url"] = official_application_url(raw)
    item["handling_institution"] = raw_text(raw, "hdlInst") or option_text(options, "handling_institution")
    item["operating_period_text"] = raw_text(raw, "prdOprPrid") or option_text(options, "operating_period")
    item["operating_period_status"] = operating_period_status(item["operating_period_text"], item.get("reviewed_at"))

    if item["operating_period_status"] == "expired":
        item["status"] = "closed"
        item["product_status"] = "ended"
        item["sales_status"] = "ended"
        item["status_reason"] = "공식 정책대출 운영기간이 현재 검토일보다 이전이어서 추천·기본 검색에서 제외합니다."
        item["status_confidence"] = "derived"
        item["effective_to"] = operating_period_end(item["operating_period_text"])

    missing = [
        field
        for field in LOAN_REQUIRED_FIELDS
        if item.get(field) is None
    ]
    item["missing_loan_required_fields"] = missing

    if item.get("status") == "active" and not item.get("criteria"):
        item["recommendation_status"] = "reference_only"
        item["status_reason"] = "대출 비교·추천에 필요한 criteria가 비어 있어 참조 전용으로만 노출합니다."
        item["quality_flags"] = unique([*(item.get("quality_flags") or []), "missing_loan_criteria"])
    if is_recommendation_ready_loan(item):
        item["recommendation_status"] = "manual_review_candidate"
        item["recommendation_scope"] = "internal_verification_candidate"
        item["recommendation_basis_fields"] = list(LOAN_REQUIRED_FIELDS)
        item["recommendation_exclusion_reasons"] = [
            reason
            for reason in item.get("recommendation_exclusion_reasons") or []
            if reason not in {"incomplete_loan_required_fields", "loan_recommendation_suspended_pending_required_field_review"}
        ]
    else:
        item["recommendation_status"] = "reference_only"
        item["recommendation_scope"] = "listing_only"
    if missing:
        item["recommendation_exclusion_reasons"] = unique([
            *(item.get("recommendation_exclusion_reasons") or []),
            "incomplete_loan_required_fields",
        ])
        item["quality_flags"] = unique([*(item.get("quality_flags") or []), "missing_loan_required_fields"])
    if item["operating_period_status"] == "unverified":
        item["recommendation_exclusion_reasons"] = unique([
            *(item.get("recommendation_exclusion_reasons") or []),
            "unverified_loan_operating_period",
        ])
        item["quality_flags"] = unique([*(item.get("quality_flags") or []), "unverified_loan_operating_period"])
    if item["loan_limit_normalization_status"] != "verified":
        item["recommendation_exclusion_reasons"] = unique([
            *(item.get("recommendation_exclusion_reasons") or []),
            "ambiguous_loan_limit_normalization",
        ])
        item["quality_flags"] = unique([*(item.get("quality_flags") or []), "ambiguous_loan_limit_normalization"])


def demo() -> None:
    assert operating_period_status("상시", "2026-07-10") == "confirmed_open"
    assert operating_period_status("2025-01-01~2025-12-31", "2026-07-10") == "expired"
    assert operating_period_status("2008.7.1~별도 통보시", "2026-07-10") == "unverified"
    assert operating_period_status("2022.09.20.~한도 소진시까지", "2026-07-10") == "unverified"
    assert operating_period_end("2025-01-01~2025-12-31") == "2025-12-31"
    assert operating_period_status("기관 문의", "2026-07-10") == "unverified"
    print("loan_product_normalizer demo OK")


if __name__ == "__main__":
    demo()
