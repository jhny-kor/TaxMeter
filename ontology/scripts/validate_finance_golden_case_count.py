#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
GOLDEN_CASE_FILES = (
    "comparison_golden_cases.json",
    "discovery_golden_cases.json",
    "recommendation_golden_cases.json",
)


def main() -> int:
    count = sum(
        len(json.loads((ROOT / "tests" / filename).read_text(encoding="utf-8")))
        for filename in GOLDEN_CASE_FILES
    )
    if count < 80:
        print(f"Finance golden case validation failed: expected at least 80, got {count}")
        return 1
    print(f"Finance golden case validation passed: {count} cases")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
