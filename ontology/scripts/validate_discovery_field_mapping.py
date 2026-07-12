#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

from calculate_recommendation_completeness import source_field_value


ROOT = Path(__file__).resolve().parents[1]
CASES_PATH = ROOT / "tests" / "discovery_field_mapping_cases.json"


def main() -> int:
    errors: list[str] = []
    for case in json.loads(CASES_PATH.read_text(encoding="utf-8")):
        actual = source_field_value(dict(case["item"]), str(case["field"]))
        if actual != case["expected"]:
            errors.append(f"{case['name']}: expected {case['expected']!r}, got {actual!r}")
    if errors:
        print("Discovery field mapping validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1
    print("Discovery field mapping validation passed: 3 cases")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
