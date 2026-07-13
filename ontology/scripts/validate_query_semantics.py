#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

from recommendation_intent_parser import parse_query


ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    errors: list[str] = []
    for case in json.loads((ROOT / "tests" / "query_parser_cases.json").read_text(encoding="utf-8")):
        parsed = parse_query(str(case["query"]))
        for key in ("intent", "domain", "product_kind"):
            if parsed.get(key) != case[key]:
                errors.append(f"{case['query']}: {key}={parsed.get(key)!r}")
        if case.get("constraint") and not any(constraint.get("field") == case["constraint"] for constraint in parsed.get("hard_constraints") or []):
            errors.append(f"{case['query']}: missing {case['constraint']}")
    if errors:
        print("Query semantics validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1
    print("Query semantics validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
