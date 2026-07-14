#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "exports/finance-search-index-2026.json"
QUALITY = ROOT / "exports/openfin-quality-manifest-2026.json"


def main() -> int:
    items = json.loads(INDEX.read_text(encoding="utf-8")).get("items") or []
    seen: dict[str, str] = {}
    duplicates: list[str] = []
    for item in items:
        if not isinstance(item, dict):
            continue
        for external_id in item.get("external_product_ids") or []:
            if not isinstance(external_id, dict):
                continue
            key = f"{external_id.get('namespace')}:{external_id.get('value')}"
            if key in seen and seen[key] != item.get("canonical_product_id"):
                duplicates.append(key)
            else:
                seen[key] = str(item.get("canonical_product_id") or item.get("id"))
    metrics = json.loads(QUALITY.read_text(encoding="utf-8")).get("runtime_quality_metrics") or {}
    for key in ("external_id_duplicate_count", "duplicate_candidate_response_count"):
        if int(metrics.get(key) or 0):
            duplicates.append(f"{key}={metrics.get(key)}")
    if duplicates:
        print("Semantic duplicate validation failed:")
        print(*[f"- {error}" for error in sorted(set(duplicates))[:20]], sep="\n")
        return 1
    print("Semantic duplicate validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
