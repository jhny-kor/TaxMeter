#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "exports" / "finance-ontology-manifest.json"


def main() -> int:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    errors: list[str] = []
    for entry in manifest.get("exports") or []:
        path = ROOT.parent / str(entry.get("path") or "")
        if not path.exists():
            continue
        for item in json.loads(path.read_text(encoding="utf-8")).get("items") or []:
            if item.get("type") not in {"card-product", "bank-product", "insurance-product"}:
                continue
            item_id = str(item.get("id"))
            for field in ("canonical_product_id", "catalog_recommendation_status", "catalog_recommendation_scope", "last_source_checked_at", "last_reviewed_at", "public_recommendation_exclusion_reasons", "comparison_exclusion_reasons", "discovery_limitations", "structured_summary", "search_facets"):
                if field not in item:
                    errors.append(f"{item_id}: missing {field}")
            if item.get("verification_status") == "not_verified" and item.get("last_verified_at") is not None:
                errors.append(f"{item_id}: unverified item has last_verified_at")
            if item.get("canonical_product_id") != item.get("id"):
                errors.append(f"{item_id}: unsupported canonical id")
    if errors:
        print("Runtime/catalog consistency validation failed:")
        for error in errors[:30]:
            print(f"- {error}")
        return 1
    print("Runtime/catalog consistency validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
