#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from recommendation_engine import recommend


ROOT = Path(__file__).resolve().parents[1]
GOLDEN_CASES = ROOT / "tests" / "recommendation_golden_cases.json"


def run_case(case: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    repeat = int(case.get("repeat") or 1)
    outputs = []
    for _ in range(repeat):
        outputs.append(
            recommend(
                str(case["domain"]),
                profile=case.get("profile") or {},
                constraints=case.get("constraints") or {},
                preferences=case.get("preferences") or {},
                limit=int(case.get("limit") or 5),
                items=case.get("items"),
            )
        )
    first = outputs[0]
    if repeat > 1 and any(output != first for output in outputs[1:]):
        errors.append(f"{case['name']}: non-deterministic output")
    if first["result_count"] != int(case["expected_result_count"]):
        errors.append(f"{case['name']}: expected {case['expected_result_count']} results, got {first['result_count']}")
    warning = case.get("expected_warning_contains")
    if warning and not any(str(warning) in str(value) for value in first.get("warnings") or []):
        errors.append(f"{case['name']}: missing warning {warning}")
    excluded = {item.get("item_id"): item.get("reason") for item in first.get("excluded_sample") or []}
    for item_id, reason in (case.get("expected_excluded") or {}).items():
        if excluded.get(item_id) != reason:
            errors.append(f"{case['name']}: expected exclusion {item_id}={reason}, got {excluded.get(item_id)}")
    unsafe = [
        candidate.get("item_id")
        for candidate in first.get("candidates") or []
        if candidate.get("recommendation_status") != "verified_recommendation_candidate"
        or candidate.get("recommendation_scope") != "public_recommendation"
    ]
    if unsafe:
        errors.append(f"{case['name']}: unsafe recommendation candidates {unsafe}")
    for candidate in first.get("candidates") or []:
        components = candidate.get("score_components") or {}
        if abs(float(candidate.get("score") or 0) - sum(float(value) for value in components.values())) > 0.000001:
            errors.append(f"{case['name']}: score component sum mismatch for {candidate.get('item_id')}")
        if not candidate.get("source_basis_dates"):
            errors.append(f"{case['name']}: missing source basis dates for {candidate.get('item_id')}")
        if not candidate.get("last_verified_at"):
            errors.append(f"{case['name']}: missing verified date for {candidate.get('item_id')}")
    return errors


def main() -> int:
    cases = json.loads(GOLDEN_CASES.read_text(encoding="utf-8"))
    errors: list[str] = []
    for case in cases:
        errors.extend(run_case(case))
    if errors:
        print("Recommendation regression validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1
    print(f"Recommendation regression validation passed: {len(cases)} cases")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
