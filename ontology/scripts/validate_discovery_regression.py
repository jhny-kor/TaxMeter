#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

from discovery_recommendation_engine import discover
from search_index_loader import load_search_index_items


ROOT = Path(__file__).resolve().parents[1]
INDEX_PATH = ROOT / "exports" / "finance-search-index-2026.json"
GOLDEN_CASES = ROOT / "tests" / "discovery_golden_cases.json"


def candidate_domain(candidate: dict) -> str | None:
    product_kind = str(candidate.get("product_kind") or "")
    if product_kind in {"check-card", "credit-card"}:
        return "card"
    if product_kind in {"credit-loan", "rent-loan", "mortgage-loan", "policy-loan"}:
        return "loan"
    if product_kind in {"indemnity-health", "cancer", "accident", "disease", "term-life", "whole-life"}:
        return "insurance"
    if product_kind in {"deposit", "saving"}:
        return product_kind
    return None


def main() -> int:
    items = load_search_index_items(INDEX_PATH)
    cases = json.loads(GOLDEN_CASES.read_text(encoding="utf-8"))
    errors: list[str] = []
    for case in cases:
        result = discover(str(case["query"]), items=items)
        candidates = [*(result.get("exact_candidates") or []), *(result.get("partial_candidates") or []), *(result.get("related_candidates") or [])]
        if result.get("executed_mode") != "discovery":
            errors.append(f"{case['name']}: discovery mode was not selected")
        if not candidates:
            errors.append(f"{case['name']}: no discovery candidates")
            continue
        if not any(candidate_domain(candidate) == case["expected_domain"] for candidate in candidates):
            errors.append(f"{case['name']}: expected {case['expected_domain']} candidates")
        exact_candidates = result.get("exact_candidates") or []
        allowed_exact_kinds = set(case.get("allowed_exact_product_kinds") or [])
        required_exact_constraints = set(case.get("required_exact_constraints") or [])
        if not allowed_exact_kinds or not required_exact_constraints:
            errors.append(f"{case['name']}: semantic golden assertion is missing")
        for candidate in exact_candidates:
            if allowed_exact_kinds and candidate.get("product_kind") not in allowed_exact_kinds:
                errors.append(f"{case['name']}: exact candidate has invalid product kind {candidate.get('product_kind')}")
            matched = set(candidate.get("matched_constraints") or [])
            if required_exact_constraints and not required_exact_constraints.issubset(matched):
                errors.append(f"{case['name']}: exact candidate is missing evidence for {sorted(required_exact_constraints - matched)}")
            if candidate.get("unknown_constraints") or candidate.get("failed_constraints"):
                errors.append(f"{case['name']}: exact candidate discloses unknown or failed constraints")
        minimum_exact = int(case.get("minimum_exact_candidates") or 0)
        if len(exact_candidates) < minimum_exact:
            errors.append(f"{case['name']}: requires at least {minimum_exact} exact candidates")
        required_title = case.get("required_exact_title")
        if required_title and not any(candidate.get("title") == required_title for candidate in exact_candidates):
            errors.append(f"{case['name']}: required exact title is missing")
        disclosure = case.get("require_partial_disclosure")
        if disclosure and not any(disclosure in (candidate.get("unknown_constraints") or []) for candidate in (result.get("partial_candidates") or [])):
            errors.append(f"{case['name']}: partial candidates must disclose unknown {disclosure}")
        for candidate in candidates:
            if candidate.get("catalog_recommendation_status") in {"discovery_candidate", None}:
                errors.append(f"{case['name']}: runtime state overwrote catalog state")
            if not candidate.get("source_urls"):
                errors.append(f"{case['name']}: candidate lacks official source")
    if errors:
        print("Discovery regression validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1
    print(f"Discovery regression validation passed: {len(cases)} cases")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
