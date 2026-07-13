#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

from discovery_recommendation_engine import discover


ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    items = json.loads((ROOT / "exports" / "finance-search-index-2026.json").read_text(encoding="utf-8")).get("items") or []
    errors: list[str] = []
    for query in ("마일리지 체크카드 추천", "신용대출 추천", "암보험 추천", "12개월 정기예금 추천"):
        payload = discover(query, items, limit=30)
        for group in ("exact_candidates", "partial_candidates", "related_candidates"):
            for candidate in payload.get(group) or []:
                decision = candidate.get("decision") or {}
                if decision.get("overall_candidate_grade") == "A" and (decision.get("verification_grade") != "A" or decision.get("relevance_grade") != "A"):
                    errors.append(f"{query}: invalid overall A")
    if errors:
        print("Confidence grade validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1
    print("Confidence grade validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
