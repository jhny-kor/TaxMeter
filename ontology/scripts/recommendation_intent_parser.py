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
    return {"original_query": query, "parser_version": QUERY_PARSER_VERSION, "intent": intent, "domain": domain, "product_kind": product_kind, "hard_constraints": hard_constraints, "soft_preferences": soft_preferences, "negative_constraints": [], "numeric_constraints": [constraint for constraint in hard_constraints if isinstance(constraint["value"], int)], "unparsed_tokens": []}
