#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

from search_index_loader import load_search_index_items

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "exports/finance-search-index-2026.json"


def main() -> int:
    items = load_search_index_items(INDEX)
    errors = [
        str(item.get("id"))
        for item in items
        if isinstance(item, dict)
        and item.get("type") in {"card-product", "bank-product", "insurance-product"}
        and item.get("sales_status") == "active"
        and item.get("sales_verification_status") != "verified_active"
    ]
    if errors:
        print("Sales status contract validation failed:")
        print(*[f"- {item_id}: active sales_status without verified_active evidence" for item_id in errors[:20]], sep="\n")
        return 1
    print("Sales status contract validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
