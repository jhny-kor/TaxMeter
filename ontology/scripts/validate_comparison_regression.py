#!/usr/bin/env python3
from __future__ import annotations

import json
from copy import deepcopy
from datetime import date, timedelta
from pathlib import Path
from typing import Any

from product_comparison_engine import compare


ROOT = Path(__file__).resolve().parents[1]
GOLDEN_CASES = ROOT / "tests" / "comparison_golden_cases.json"


def run_case(case: dict[str, Any]) -> list[str]:
    items = deepcopy(case["items"])
    for item in items:
        item.setdefault("domain_gate_passed", True)
        item.setdefault("verification_status", "verified")
        item.setdefault("sales_verified_at", date.today().isoformat())
        item.setdefault("source_checksum", f"test-{item['id']}")
        item.setdefault("verification_evidence", {"source_checksums": [item["source_checksum"]], "expires_at": (date.today() + timedelta(days=1)).isoformat()})
    outputs = [compare(case["arguments"], items=items) for _ in range(int(case.get("repeat") or 1))]
    first = outputs[0]
    errors: list[str] = []
    if any(output != first for output in outputs[1:]):
        errors.append(f"{case['name']}: non-deterministic output")
    candidate_ids = [candidate["item_id"] for candidate in first["candidates"]]
    if candidate_ids != case["expected_candidate_ids"]:
        errors.append(f"{case['name']}: expected candidates {case['expected_candidate_ids']}, got {candidate_ids}")
    excluded = {item["item_id"]: item["reason"] for item in first["excluded"]}
    for item_id, reason in (case.get("expected_excluded") or {}).items():
        if excluded.get(item_id) != reason:
            errors.append(f"{case['name']}: expected {item_id} exclusion {reason}, got {excluded.get(item_id)}")
    rates = {candidate["item_id"]: candidate["achievable_rate_percent"] for candidate in first["candidates"]}
    for item_id, rate in (case.get("expected_achievable_rates") or {}).items():
        if rates.get(item_id) != rate:
            errors.append(f"{case['name']}: expected achievable rate {rate} for {item_id}, got {rates.get(item_id)}")
    for item_id, expected in (case.get("expected_interest_estimates") or {}).items():
        candidate = next((value for value in first["candidates"] if value["item_id"] == item_id), None)
        for field, value in expected.items():
            if candidate is None or candidate.get(field) != value:
                errors.append(f"{case['name']}: expected {field} {value} for {item_id}, got {candidate.get(field) if candidate else None}")
    if case.get("require_score_sources"):
        for candidate in first["candidates"]:
            if not candidate.get("score_components") or not candidate.get("source_urls"):
                errors.append(f"{case['name']}: missing score basis for {candidate['item_id']}")
    return errors


def main() -> int:
    cases = json.loads(GOLDEN_CASES.read_text(encoding="utf-8"))
    errors = [error for case in cases for error in run_case(case)]
    if errors:
        print("Comparison regression validation failed:")
        print(*[f"- {error}" for error in errors], sep="\n")
        return 1
    print(f"Comparison regression validation passed: {len(cases)} cases")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
