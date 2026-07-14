#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "exports/finance-search-index-2026.json"


def main() -> int:
    items = json.loads(INDEX.read_text(encoding="utf-8")).get("items") or []
    errors: list[str] = []
    for item in items:
        if not isinstance(item, dict) or item.get("type") != "support-program":
            continue
        text = " ".join(str(item.get(key) or "") for key in ("title", "description", "search_text"))
        categories = set(item.get("support_category") or [])
        targets = set(item.get("target_group") or [])
        if "월세" in text and not ({"housing", "rent"} & categories):
            errors.append(f"{item.get('id')}: monthly-rent text missing housing/rent category")
        if "청년" in text and "youth" not in targets:
            errors.append(f"{item.get('id')}: youth text missing youth target")
    if errors:
        print("Support relevance validation failed:")
        print(*[f"- {error}" for error in errors[:20]], sep="\n")
        return 1
    print("Support relevance validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
