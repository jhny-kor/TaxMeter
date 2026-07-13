#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

from discovery_recommendation_engine import discover


ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    items = json.loads((ROOT / "exports" / "finance-search-index-2026.json").read_text(encoding="utf-8")).get("items") or []
    errors: list[str] = []
    for query in ("마일리지 체크카드 추천", "직장인 신용대출 추천", "비갱신 암보험 추천", "12개월 정기예금 추천"):
        payload = discover(query, items)
        for field in ("requested_intent", "executed_mode", "parsed_query", "exact_candidates", "partial_candidates", "related_candidates", "excluded_summary", "engine_version"):
            if field not in payload:
                errors.append(f"{query}: missing {field}")
        for candidate in payload.get("exact_candidates") or []:
            if candidate.get("decision", {}).get("eligibility") != "exact_candidate":
                errors.append(f"{query}: invalid exact candidate")
            if candidate.get("canonical_product_id") in {None, ""}:
                errors.append(f"{query}: missing canonical id")
    if errors:
        print("Discovery recommendation validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1
    print("Discovery recommendation validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
