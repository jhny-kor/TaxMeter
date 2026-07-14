#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

from discovery_recommendation_engine import discover


ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "exports/finance-search-index-2026.json"
CASES = ROOT / "tests/discovery_golden_cases.json"


def main() -> int:
    items = json.loads(INDEX.read_text(encoding="utf-8")).get("items") or []
    cases = json.loads(CASES.read_text(encoding="utf-8"))
    errors: list[str] = []
    for case in cases:
        payload = discover(str(case["query"]), items)
        for group in ("exact_candidates", "partial_candidates", "related_candidates"):
            for candidate in payload.get(group) or []:
                expected = max(str(candidate.get("relevance_grade") or "D"), str(candidate.get("data_completeness_grade") or "D"), str(candidate.get("verification_grade") or "D"))
                if str(candidate.get("overall_candidate_grade") or "D") < expected:
                    errors.append(f"{case['query']}: {candidate.get('id')} overall grade exceeds component floor")
                for reason in candidate.get("why_included") or []:
                    if reason.get("matched_value") == reason.get("constraint"):
                        errors.append(f"{case['query']}: {candidate.get('id')} returns field name as matched value")
    if errors:
        print("Grade policy validation failed:")
        print(*[f"- {error}" for error in errors[:20]], sep="\n")
        return 1
    print("Grade policy validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
