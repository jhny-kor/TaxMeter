#!/usr/bin/env python3
from __future__ import annotations

import json
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "exports/finance-ontology-manifest.json"


def main() -> int:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    errors: list[str] = []
    for entry in manifest.get("exports") or []:
        path = ROOT.parent / str(entry.get("path"))
        if not path.exists():
            continue
        payload = json.loads(path.read_text(encoding="utf-8"))
        for item in [*(payload.get("reference_items") or []), *(payload.get("items") or [])]:
            evidence = item.get("verification_evidence") if isinstance(item, dict) else None
            if not isinstance(evidence, dict):
                continue
            expires_at = evidence.get("expires_at")
            try:
                expired = not isinstance(expires_at, str) or date.fromisoformat(expires_at) < date.today()
            except ValueError:
                expired = True
            if expired and item.get("recommendation_scope") in {"public_recommendation", "comparison_only"}:
                errors.append(f"{item.get('id')}: expired verification exposed in {item.get('recommendation_scope')}")
    if errors:
        print("Verification expiration validation failed:")
        print(*[f"- {error}" for error in errors[:20]], sep="\n")
        return 1
    print("Verification expiration validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
