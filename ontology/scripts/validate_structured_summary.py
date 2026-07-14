#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TAX_EXPORT = ROOT / "exports" / "korea-tax-ontology-2026.json"
SUPPORT_EXPORT = ROOT / "exports" / "korea-local-government-supports-ontology-2026.json"
TAX_TYPES = {"tax", "deduction", "tax-credit", "tax-reduction", "corporate-tax-support", "filing"}


def main() -> int:
    tax_items = json.loads(TAX_EXPORT.read_text(encoding="utf-8")).get("items") or []
    support_items = json.loads(SUPPORT_EXPORT.read_text(encoding="utf-8")).get("items") or []
    errors: list[str] = []
    tax_count = 0
    for item in tax_items:
        if item.get("type") not in TAX_TYPES or not item.get("criteria"):
            continue
        tax_count += 1
        summary = item.get("structured_summary") or {}
        facets = item.get("search_facets") or {}
        if not summary.get("tax"):
            errors.append(f"{item.get('id')}: missing tax structured_summary")
        if facets.get("tax_type") != item.get("type"):
            errors.append(f"{item.get('id')}: missing tax_type facet")
    support_count = 0
    for item in support_items:
        if item.get("type") != "support-program":
            continue
        support_count += 1
        for field in ("parent_jurisdiction_code", "target_group", "support_category", "last_status_checked_at"):
            if field not in item:
                errors.append(f"{item.get('id')}: missing {field}")
    if errors:
        print("Structured summary validation failed:")
        for error in errors[:20]:
            print(f"- {error}")
        return 1
    print(f"Structured summary validation passed: {tax_count} tax and {support_count} support records")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
