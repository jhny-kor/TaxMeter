#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

from discovery_recommendation_engine import discover


ROOT = Path(__file__).resolve().parents[1]
QUERIES = ("마일리지 체크카드 추천", "직장인 신용대출 추천", "암보험 추천", "실손보험 추천", "12개월 정기예금 추천", "자유적립식 적금 추천")


def main() -> int:
    items = json.loads((ROOT / "exports" / "finance-search-index-2026.json").read_text(encoding="utf-8")).get("items") or []
    errors: list[str] = []
    for query in QUERIES:
        payload = discover(query, items, limit=50)
        candidates = [*(payload.get("exact_candidates") or []), *(payload.get("partial_candidates") or []), *(payload.get("related_candidates") or [])]
        ids = [candidate.get("canonical_product_id") for candidate in candidates]
        if len(ids) != len(set(ids)):
            errors.append(f"{query}: duplicate canonical product")
        for candidate in payload.get("exact_candidates") or []:
            decision = candidate.get("decision") or {}
            if decision.get("unknown_constraints") or decision.get("failed_constraints"):
                errors.append(f"{query}: exact candidate has unresolved hard constraint")
    if errors:
        print("Candidate deduplication validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1
    print(f"Candidate deduplication validation passed: {len(QUERIES)} queries")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
