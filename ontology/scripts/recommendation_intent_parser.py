#!/usr/bin/env python3
from __future__ import annotations

import re

from recommendation_policy import QUERY_PARSER_VERSION


PRODUCT_KINDS = (
    ("check-card", "card", ("체크카드",)),
    ("credit-card", "card", ("신용카드",)),
    ("credit-loan", "loan", ("신용대출",)),
    ("rent-loan", "loan", ("전세대출", "월세대출")),
    ("mortgage-loan", "loan", ("주택담보대출",)),
    ("policy-loan", "loan", ("정책대출",)),
    ("indemnity-health", "insurance", ("실손보험", "실손의료보험", "실손의료비보험", "실비보험")),
    ("cancer", "insurance", ("암보험",)),
    ("accident", "insurance", ("상해보험",)),
    ("disease", "insurance", ("질병보험",)),
    ("term-life", "insurance", ("정기보험",)),
    ("whole-life", "insurance", ("종신보험",)),
    ("deposit", "deposit", ("정기예금", "예금")),
    ("saving", "saving", ("자유적금", "적금")),
)

# Provider aliases are deliberately small and explicit.  They are used only
# when the user names a provider; an omitted provider remains an unknown
# constraint instead of widening the candidate set.
PROVIDER_ALIASES = {
    "삼성카드": ("삼성카드", "삼성"),
    "BC바로카드": ("bc바로카드", "bc카드", "비씨카드"),
    "신한카드": ("신한카드", "신한"),
    "KB국민카드": ("kb국민카드", "kb국민", "국민카드", "kb"),
    "롯데카드": ("롯데카드", "롯데"),
}
GENERIC_PRODUCT_TOKENS = {
    "카드", "체크카드", "신용카드", "보험", "대출", "예금", "적금", "정기예금", "자유적금", "자유적립",
    "실손보험", "실비보험", "암보험", "상해보험", "질병보험", "정기보험", "종신보험", "신용대출", "전세대출", "월세대출", "정책대출", "주택담보대출",
    "상품", "추천", "추천해줘", "추천해주세요",
    "비교", "찾아줘", "찾아주세요", "알려줘", "알려주세요", "골라줘", "골라주세요",
    "후보", "순위", "없는", "무엇", "뭐", "비갱신형", "갱신형", "전월실적", "연회비", "교통", "쇼핑", "온라인", "할인", "적립", "마일리지", "구독", "직장인", "중도상환수수료", "낮은", "금리", "청년",
}


def compact_product_text(value: str) -> str:
    return re.sub(r"[^0-9a-z가-힣]", "", value.casefold())


def provider_for_query(query: str) -> str | None:
    compact = compact_product_text(query)
    matches = [provider for provider, aliases in PROVIDER_ALIASES.items() if any(compact_product_text(alias) in compact for alias in aliases)]
    if not matches:
        return None
    # Prefer the longest alias match so `KB국민카드` is not shadowed by `KB`.
    return max(matches, key=lambda provider: max(len(compact_product_text(alias)) for alias in PROVIDER_ALIASES[provider]))


def product_name_tokens(query: str, provider: str | None) -> list[str]:
    provider_aliases = {compact_product_text(alias) for alias in PROVIDER_ALIASES.get(provider or "", ())}
    tokens: list[str] = []
    for raw_token in re.findall(r"[0-9A-Za-z가-힣]+", query):
        token = raw_token.strip()
        compact = compact_product_text(token)
        if not compact or compact in {"월"} or re.fullmatch(r"\d+(?:\.\d+)?(?:천만원|억원|만원|천원|원)", compact):
            continue
        if compact in GENERIC_PRODUCT_TOKENS or compact in {compact_product_text(value) for value in provider_aliases}:
            continue
        if compact in {compact_product_text(value) for value in GENERIC_PRODUCT_TOKENS}:
            continue
        # A compound such as `삼성체크카드` is product-name evidence and must
        # not be split into a provider token plus a generic card token.
        if compact not in tokens:
            tokens.append(compact)
    return tokens


def parse_amount_krw(query: str) -> int | None:
    match = re.search(r"(\d+(?:\.\d+)?)\s*(천만원|억원|만원|천원|원)", query.replace(",", ""))
    if not match:
        return None
    value = float(match.group(1))
    unit = match.group(2)
    multipliers = {"억원": 100_000_000, "천만원": 10_000_000, "만원": 10_000, "천원": 1_000, "원": 1}
    return int(value * multipliers[unit])


def parse_query(query: str) -> dict:
    normalized = " ".join(query.split())
    product_kind = None
    domain = None
    for kind, kind_domain, aliases in PRODUCT_KINDS:
        if any(alias in normalized for alias in aliases):
            product_kind, domain = kind, kind_domain
            break
    if domain is None:
        domain = next((value for token, value in (("카드", "card"), ("대출", "loan"), ("보험", "insurance"), ("예금", "deposit"), ("적금", "saving")) if token in normalized), None)
    intent = "compare" if "비교" in normalized and not any(token in normalized for token in ("추천", "골라", "알려", "찾아")) else ("discovery" if any(token in normalized for token in ("추천", "골라", "알려", "찾아", "후보", "순위")) else "search")
    provider = provider_for_query(normalized)
    name_tokens = product_name_tokens(normalized, provider)
    hard_constraints: list[dict] = []
    if product_kind:
        hard_constraints.append({"field": "product_kind", "operator": "equals", "value": product_kind})
    if "전월실적 없는" in normalized:
        hard_constraints.append({"field": "previous_month_spend_min_krw", "operator": "equals", "value": 0})
    if "연회비 없는" in normalized:
        hard_constraints.append({"field": "annual_fee_krw", "operator": "equals", "value": 0})
    if "비갱신" in normalized or "갱신 안 되는" in normalized:
        hard_constraints.append({"field": "renewal_type", "operator": "equals", "value": "non_renewable"})
    elif "갱신형" in normalized:
        hard_constraints.append({"field": "renewal_type", "operator": "equals", "value": "renewable"})
    if "직장인" in normalized:
        hard_constraints.append({"field": "employment_type", "operator": "equals", "value": "employee"})
    if "중도상환수수료 없는" in normalized:
        hard_constraints.append({"field": "early_repayment_fee", "operator": "equals", "value": 0})
    if "구독" in normalized:
        hard_constraints.append({"field": "benefit_category", "operator": "contains", "value": "subscription"})
    if "자유적립" in normalized or "자유적금" in normalized:
        hard_constraints.append({"field": "saving_method", "operator": "equals", "value": "free"})
    term_match = re.search(r"(\d+)\s*개월", normalized)
    if term_match:
        hard_constraints.append({"field": "term_months", "operator": "equals", "value": int(term_match.group(1))})
    amount = parse_amount_krw(normalized)
    if amount is not None:
        hard_constraints.append({"field": "deposit_amount_krw" if domain == "deposit" else "monthly_payment_krw", "operator": "lte", "value": amount})
    soft_preferences = [token for token in ("마일리지", "교통", "쇼핑", "온라인", "우대금리", "낮은 금리", "높은 한도", "대한항공", "SKYPASS", "청년") if token.casefold() in normalized.casefold()]
    if provider:
        hard_constraints.append({"field": "provider", "operator": "equals", "value": provider})
    if name_tokens:
        hard_constraints.append({"field": "product_name_tokens", "operator": "contains", "value": name_tokens})
    return {"original_query": query, "parser_version": QUERY_PARSER_VERSION, "intent": intent, "domain": domain, "product_kind": product_kind, "provider": provider, "product_name_tokens": name_tokens, "hard_constraints": hard_constraints, "soft_preferences": soft_preferences, "negative_constraints": [], "numeric_constraints": [constraint for constraint in hard_constraints if isinstance(constraint["value"], int)], "unparsed_tokens": []}
