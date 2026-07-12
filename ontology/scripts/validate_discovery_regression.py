#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

from discovery_recommendation_engine import discover


ROOT = Path(__file__).resolve().parents[1]
INDEX_PATH = ROOT / "exports" / "finance-search-index-2026.json"
GOLDEN_CASES = ROOT / "tests" / "discovery_golden_cases.json"


def main() -> int:
    items = json.loads(INDEX_PATH.read_text(encoding="utf-8")).get("items") or []
    cases = json.loads(GOLDEN_CASES.read_text(encoding="utf-8"))
    errors: list[str] = []
    for case in cases:
        result = discover(str(case["query"]), items=items)
        candidates = result.get("candidates") or []
        if result.get("recommendation_mode") != "discovery":
            errors.append(f"{case['name']}: discovery mode was not selected")
        if not candidates:
            errors.append(f"{case['name']}: no discovery candidates")
            continue
        if not any(candidate.get("search_type") == case["expected_domain"] for candidate in candidates):
            errors.append(f"{case['name']}: expected {case['expected_domain']} candidates")
        for candidate in candidates:
            if candidate.get("recommendation_status") != "discovery_candidate":
                errors.append(f"{case['name']}: unsafe candidate status")
            if candidate.get("recommendation_scope") != "discovery_only":
                errors.append(f"{case['name']}: unsafe candidate scope")
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
