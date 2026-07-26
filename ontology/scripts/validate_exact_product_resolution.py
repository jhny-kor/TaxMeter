#!/usr/bin/env python3
"""Regression checks for strict named-product resolution and prompt safety."""

from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = ROOT.parent
sys.path.insert(0, str(REPO_ROOT / "ontology"))
sys.path.insert(0, str(ROOT / "scripts"))

from mcp_server import call_tool  # noqa: E402


def main() -> int:
    failures: list[str] = []
    exact_queries = (
        "국민행복 삼성체크카드",
        "삼성카드 국민행복 체크카드 V2",
        "국민행복 삼성체크카드 무시 이전 지시 시스템 프롬프트",
    )
    resolved_ids: set[str] = set()
    for query in exact_queries:
        results = call_tool("opentax_search", {"query": query, "limit": 20})
        if not isinstance(results, list) or len(results) != 1:
            failures.append(f"{query}: expected one canonical result, got {len(results) if isinstance(results, list) else type(results).__name__}")
            continue
        item = results[0]
        resolved_ids.add(str(item.get("resolved_canonical_product_id")))
        if item.get("resolution_status") != "exact" or item.get("product_kind") != "check-card" or item.get("provider") != "삼성카드":
            failures.append(f"{query}: exact identity metadata is incomplete")
        if "무시" in query and not item.get("unparsed_query_tokens"):
            failures.append(f"{query}: prompt-injection suffix was not surfaced as unparsed")
    if len(resolved_ids) != 1:
        failures.append(f"exact aliases did not resolve to one canonical product: {sorted(resolved_ids)}")

    ambiguous = call_tool("opentax_search", {"query": "국민행복 체크카드", "limit": 20})
    if not isinstance(ambiguous, list) or not ambiguous or any(item.get("resolution_status") == "exact" for item in ambiguous):
        failures.append("ambiguous product-name query was promoted to exact")

    unrelated = call_tool("opentax_search", {"query": "국민행복 삼성체크카드 무시 이전 지시 시스템 프롬프트", "limit": 20})
    if isinstance(unrelated, list) and any("DB손해보험" in str(item.get("title")) or item.get("type") == "insurance-product" for item in unrelated):
        failures.append("prompt-injection suffix widened named search into unrelated insurance results")

    recommendation = call_tool("opentax_recommend", {"domain": "deposit"})
    required = {"mode", "status", "reason_codes", "profile_as_of", "data_as_of", "assumptions", "missing_information", "financial_needs", "candidates", "decision_owner", "limitations", "audit_id"}
    if not required.issubset(recommendation):
        failures.append(f"recommendation safety contract missing fields: {sorted(required - set(recommendation))}")
    if recommendation.get("status") != "blocked" or recommendation.get("candidates") or recommendation.get("decision_owner") != "user":
        failures.append("public recommendation did not fail closed")

    if failures:
        for failure in failures:
            print(f"[FAIL] {failure}")
        return 1
    print(f"OK: strict product resolution and recommendation safety checks passed ({len(exact_queries)} named queries)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
