#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

from recommendation_intent_parser import parse_query
from recommendation_policy import QUERY_PARSER_VERSION


ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    errors: list[str] = []
    for case in json.loads((ROOT / "tests" / "query_parser_cases.json").read_text(encoding="utf-8")):
        parsed = parse_query(str(case["query"]))
        if parsed.get("parser_version") != QUERY_PARSER_VERSION:
            errors.append(f"{case['query']}: parser version missing")
        for key in ("intent", "domain", "product_kind"):
            if parsed.get(key) != case[key]:
                errors.append(f"{case['query']}: {key}={parsed.get(key)!r}")
        if case.get("constraint") and not any(constraint.get("field") == case["constraint"] for constraint in parsed.get("hard_constraints") or []):
            errors.append(f"{case['query']}: missing {case['constraint']}")
        if "provider" in case and parsed.get("provider") != case["provider"]:
            errors.append(f"{case['query']}: provider={parsed.get('provider')!r}")
        if "name_tokens" in case and parsed.get("product_name_tokens") != case["name_tokens"]:
            errors.append(f"{case['query']}: product_name_tokens={parsed.get('product_name_tokens')!r}")
        if "unparsed_tokens" in case and parsed.get("unparsed_tokens") != case["unparsed_tokens"]:
            errors.append(f"{case['query']}: unparsed_tokens={parsed.get('unparsed_tokens')!r}")
    if errors:
        print("Query semantics validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1
    print("Query semantics validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
