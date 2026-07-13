#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

from canonical_product_registry import merge_product_records


ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    errors: list[str] = []
    cases = json.loads((ROOT / "tests" / "canonical_product_merge_cases.json").read_text(encoding="utf-8"))
    for case in cases:
        merged = merge_product_records(case["items"])
        expected_merged_count = int(case.get("expected_merged_count") or 1)
        if len(merged) != expected_merged_count:
            errors.append(f"{case['name']}: expected {expected_merged_count} merged records, got {len(merged)}")
            continue
        expected_ids = case.get("expected_canonical_product_ids")
        if expected_ids:
            if sorted(item.get("canonical_product_id") for item in merged) != sorted(expected_ids):
                errors.append(f"{case['name']}: canonical product ids mismatch")
            continue
        item = merged[0]
        if item.get("canonical_product_id") != case["expected_canonical_product_id"]:
            errors.append(f"{case['name']}: canonical product id mismatch")
        if len(item.get("source_records") or []) != case.get("expected_source_record_count", 1):
            errors.append(f"{case['name']}: source record count mismatch")
        merged_field = case.get("expected_merged_field")
        if merged_field and not item.get("merged_fields", {}).get(merged_field):
            errors.append(f"{case['name']}: missing merged {merged_field}")
        conflict_field = case.get("expected_conflict_field")
        if conflict_field and conflict_field not in (item.get("field_conflicts") or {}):
            errors.append(f"{case['name']}: missing {conflict_field} conflict")
        forbidden_conflict_field = case.get("forbidden_conflict_field")
        if forbidden_conflict_field and forbidden_conflict_field in (item.get("field_conflicts") or {}):
            errors.append(f"{case['name']}: derived {forbidden_conflict_field} was recorded as a source conflict")
        public_exclusion = case.get("expected_public_exclusion")
        if public_exclusion and public_exclusion not in (item.get("public_recommendation_exclusion_reasons") or []):
            errors.append(f"{case['name']}: missing {public_exclusion} public exclusion")
    if errors:
        print("Canonical product merge validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1
    print(f"Canonical product merge validation passed: {len(cases)} cases")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
