#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

from search_index_loader import load_search_index_items

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "exports/finance-search-index-2026.json"
QUALITY = ROOT / "exports/openfin-quality-manifest-2026.json"


def main() -> int:
    items = load_search_index_items(INDEX)
    seen: dict[str, str] = {}
    duplicates: list[str] = []
    redirect_failures: list[str] = []
    redirect_cycles: list[str] = []
    golden_external_ids = {"bc_card_gdsno:101681", "disclosure_product_code:ABP1689"}
    grouped: dict[str, list[dict]] = {}
    for item in items:
        if not isinstance(item, dict):
            continue
        for external_id in item.get("external_product_ids") or []:
            if not isinstance(external_id, dict):
                continue
            key = f"{external_id.get('namespace')}:{external_id.get('value')}"
            resolved_id = item.get("resolved_canonical_product_id") or item.get("canonical_product_id") or item.get("id")
            grouped.setdefault(key, []).append(item)
            if key in seen and seen[key] != resolved_id:
                duplicates.append(key)
            else:
                seen[key] = str(resolved_id)
    metrics = json.loads(QUALITY.read_text(encoding="utf-8")).get("runtime_quality_metrics") or {}
    for key in ("external_id_duplicate_count", "duplicate_candidate_response_count"):
        if int(metrics.get(key) or 0):
            duplicates.append(f"{key}={metrics.get(key)}")
    if duplicates:
        print("Semantic duplicate validation failed:")
        print(*[f"- {error}" for error in sorted(set(duplicates))[:20]], sep="\n")
        return 1
    for key in golden_external_ids:
        records = grouped.get(key, [])
        resolved = {str(item.get("resolved_canonical_product_id") or item.get("canonical_product_id") or item.get("id")) for item in records}
        if len(resolved) != 1:
            redirect_failures.append(f"{key}: canonical_count={len(resolved)}")
            continue
        canonical_id = next(iter(resolved))
        winner = next((item for item in items if str(item.get("resolved_canonical_product_id") or item.get("canonical_product_id") or item.get("id")) == canonical_id), None)
        aliases = {str(value) for value in (winner or {}).get("legacy_ids") or []}
        for record in records:
            if record.get("id") != (winner or {}).get("id") and str(record.get("id")) not in aliases:
                redirect_failures.append(f"{key}: missing legacy redirect for {record.get('id')}")
        if canonical_id in aliases:
            redirect_cycles.append(f"{key}: canonical id appears in legacy_ids")
    if redirect_failures or redirect_cycles:
        print("Semantic duplicate validation failed:")
        print(*[f"- {error}" for error in [*redirect_failures, *redirect_cycles]], sep="\n")
        return 1
    print("Semantic duplicate validation passed (canonical redirect checks: 101681, ABP1689)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
