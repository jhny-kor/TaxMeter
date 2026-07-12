#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ALIASES_PATH = ROOT / "custom" / "finance" / "search-aliases.json"
ACTION_RE = re.compile(r"추천|알려줘|골라줘|찾아줘|괜찮은|좋은|후보|비교|순위|해줘|해주세요")
DOMAIN_TOKENS = {
    "card": ("카드", "체크카드", "신용카드", "마일리지", "구독"),
    "loan": ("대출", "신용대출", "전세대출", "월세대출"),
    "insurance": ("보험", "실손", "실비", "암보험", "비갱신"),
    "deposit": ("예금", "정기예금"),
    "saving": ("적금", "자유적금"),
}


def normalize_text(value: str) -> str:
    return re.sub(r"[\s\[\](){}<>_\-—–/\\]+", "", value.casefold())


def load_aliases() -> dict[str, dict[str, list[str]]]:
    return json.loads(ALIASES_PATH.read_text(encoding="utf-8"))


def domain_for_item(item: dict[str, Any]) -> str | None:
    if item.get("type") == "card-product":
        return "card"
    if item.get("type") == "insurance-product":
        return "insurance"
    search_type = str(item.get("search_type") or "")
    if search_type in {"deposit", "saving", "loan"}:
        return search_type
    return None


def domain_for_query(query: str) -> str | None:
    normalized = normalize_text(query)
    for domain, tokens in DOMAIN_TOKENS.items():
        if any(normalize_text(token) in normalized for token in tokens):
            return domain
    return None


def core_query(query: str, domain: str | None) -> str:
    stripped = ACTION_RE.sub(" ", query)
    if domain:
        for token in DOMAIN_TOKENS[domain]:
            stripped = stripped.replace(token, " ")
    return " ".join(stripped.split())


def is_discovery_query(query: str) -> bool:
    return bool(ACTION_RE.search(query))


def item_text(item: dict[str, Any]) -> str:
    values = [
        item.get("id"), item.get("title"), item.get("provider"), item.get("product_kind"),
        item.get("search_type"), item.get("search_text"), item.get("description"),
        *(item.get("search_aliases") or []), *(item.get("aliases") or []),
    ]
    return normalize_text(" ".join(str(value or "") for value in values))


def has_official_source(item: dict[str, Any]) -> bool:
    return bool(item.get("source_urls")) and item.get("source_listing_status") in {None, "listed"}


def is_current_active(item: dict[str, Any]) -> bool:
    return item.get("product_status") == "active" and item.get("status") == "active" and item.get("source_freshness_status") != "stale"


def structured_values(item: dict[str, Any]) -> list[Any]:
    return [item.get("criteria") or [], item.get("options") or [], item.get("benefits") or [], item.get("structured_summary") or {}]


def has_discovery_fields(item: dict[str, Any], domain: str) -> bool:
    evidence = set(str(value) for value in item.get("discovery_evidence_fields") or [])
    values = structured_values(item)
    if domain == "card":
        return bool(item.get("title") and item.get("provider") and item.get("product_kind") and (evidence & {"benefit_type", "benefit_rate_or_amount", "benefit_categories"} or item.get("benefits") or item.get("criteria")))
    if domain == "loan":
        has_terms = bool(evidence & {"loan_rate_min_percent", "loan_rate_max_percent", "loan_limit_krw"} or item.get("criteria") or item.get("options"))
        has_numeric = bool(evidence & {"loan_rate_min_percent", "loan_rate_max_percent", "loan_limit_krw"}) or any(item.get(key) not in (None, "", [], {}) for key in ("loan_rate_min_percent", "loan_rate_max_percent", "loan_limit_krw"))
        return bool(item.get("provider") and item.get("product_kind") and has_terms and has_numeric)
    if domain == "insurance":
        has_basis = bool(evidence & {"coverage_amount_krw", "premium_basis", "renewal_type"}) or any(item.get(key) not in (None, "", [], {}) for key in ("coverage_amount_krw", "premium_basis", "renewal_type"))
        return bool(item.get("product_kind") and (has_basis or item.get("criteria") or item.get("benefits")) and (has_basis or values))
    return bool(item.get("comparison_options") or item.get("options"))


def alias_terms(query: str, domain: str) -> list[str]:
    normalized = normalize_text(query)
    matches: list[str] = []
    for alias, terms in load_aliases().get(domain, {}).items():
        if normalize_text(alias) in normalized:
            matches.extend(str(term) for term in terms)
    return matches


def confidence_grade(item: dict[str, Any]) -> str:
    ratio = float(item.get("normalized_completeness_ratio") or item.get("completeness_ratio") or 0)
    if ratio >= 0.8:
        return "A"
    if ratio >= 0.5:
        return "B"
    if ratio >= 0.25:
        return "C"
    return "D"


def candidate(item: dict[str, Any], domain: str, query: str) -> dict[str, Any] | None:
    if domain_for_item(item) != domain or not is_current_active(item) or not has_official_source(item) or not has_discovery_fields(item, domain):
        return None
    text = item_text(item)
    title = normalize_text(str(item.get("title") or ""))
    terms = [normalize_text(term) for term in core_query(query, domain).split() if term]
    aliases = [normalize_text(term) for term in alias_terms(query, domain)]
    matched = [term for term in terms if term in text]
    alias_matched = [term for term in aliases if term in text]
    score = 35 + min(20, len(matched) * 10) + min(20, len(alias_matched) * 10)
    if any(term and term in title for term in aliases):
        score += 10
    score += round(float(item.get("normalized_completeness_ratio") or item.get("completeness_ratio") or 0) * 10)
    if item.get("source_freshness_status") == "current":
        score += 5
    unknown = terms if not matched else [term for term in terms if term not in matched]
    limitations = ["탐색 후보이며 개인 적합성·승인·보험료·최적 상품을 판단하지 않습니다."]
    if item.get("sales_verification_status") != "verified_active":
        limitations.append("공식 목록 기반 후보이므로 실제 판매·가입 가능 여부는 상세 페이지에서 재확인해야 합니다.")
    return {
        "id": item.get("id"), "title": item.get("title"), "provider": item.get("provider"), "product_kind": item.get("product_kind"),
        "search_type": domain, "recommendation_status": "discovery_candidate", "recommendation_scope": "discovery_only",
        "confidence_grade": confidence_grade(item), "discovery_score": score, "matched_conditions": matched or ["product_domain"],
        "unmatched_conditions": [], "unknown_conditions": unknown, "missing_required_fields": item.get("missing_required_fields") or [],
        "why_included": "공식 출처의 현재 상품이며 탐색에 필요한 최소 구조 필드를 보유했습니다.", "limitations": limitations,
        "source_urls": item.get("source_urls") or [], "basis_dates": item.get("source_basis_dates") or [],
        "source_listing_status": item.get("source_listing_status"), "sales_verification_status": item.get("sales_verification_status"),
        "source_freshness_status": item.get("source_freshness_status"), "source_completeness_ratio": item.get("source_completeness_ratio"),
        "normalized_completeness_ratio": item.get("normalized_completeness_ratio") or item.get("completeness_ratio"),
        "verified_completeness_ratio": item.get("verified_completeness_ratio"),
    }


def discover(query: str, items: list[dict[str, Any]], limit: int = 10) -> dict[str, Any]:
    domain = domain_for_query(query)
    if domain is None:
        return {"recommendation_mode": "discovery", "label": "탐색 결과", "query": query, "domain": None, "candidates": [], "excluded_count": 0, "warnings": ["상품 유형을 특정할 수 없어 탐색 후보를 만들지 않았습니다."]}
    candidates = [result for item in items if (result := candidate(item, domain, query))]
    candidates.sort(key=lambda value: (-int(value["discovery_score"]), -float(value.get("normalized_completeness_ratio") or 0), str(value["id"])))
    return {"recommendation_mode": "discovery", "label": "탐색 후보", "query": query, "domain": domain, "candidates": candidates[:limit], "excluded_count": sum(1 for item in items if domain_for_item(item) == domain) - len(candidates), "warnings": ["결과는 탐색용 후보입니다. 최적·승인·보험료·보장 적합성을 뜻하지 않습니다."]}
