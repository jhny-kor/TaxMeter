#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

from apply_recommendation_verifications import OVERLAY_PATH, PRODUCT_TYPES, verification_errors


ROOT = Path(__file__).resolve().parents[1]
EXPORT_DIR = ROOT / "exports"
MANIFEST = EXPORT_DIR / "finance-ontology-manifest.json"
VALID_STATUSES = {
    "reference_only",
    "eligible_for_listing",
    "manual_review_candidate",
    "verified_recommendation_candidate",
}
VALID_SCOPES = {
    "listing_only",
    "comparison_only",
    "internal_verification_candidate",
    "public_recommendation",
}
VALID_VERIFICATION_STATUSES = {"not_verified", "pending", "verified", "expired", "source_changed", "rejected"}
EVIDENCE_REQUIRED_FIELDS = ("reviewer", "verified_at", "source_urls", "source_checksums", "verified_fields")
REQUIRED_CONTRACT_FIELDS = (
    "recommendation_status",
    "recommendation_scope",
    "verification_status",
    "recommendation_exclusion_reasons",
    "recommendation_basis_fields",
    "comparison_basis_fields",
    "quality_flags",
    "last_verified_at",
    "verification_evidence",
    "freshness_status",
    "recommendation_model_version",
)


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def export_items() -> list[tuple[str, dict[str, Any]]]:
    manifest = load_json(MANIFEST)
    loaded: list[tuple[str, dict[str, Any]]] = []
    for entry in manifest.get("exports") or []:
        path = ROOT.parent / str(entry.get("path"))
        if not path.exists():
            continue
        payload = load_json(path)
        for item in [*(payload.get("reference_items") or []), *(payload.get("items") or [])]:
            if isinstance(item, dict):
                loaded.append((str(entry.get("id") or path.name), item))
    return loaded


def validate_evidence(item: dict[str, Any]) -> list[str]:
    evidence = item.get("verification_evidence")
    if not isinstance(evidence, dict):
        return ["missing_verification_evidence"]
    errors = [f"verification_evidence_missing_{field}" for field in EVIDENCE_REQUIRED_FIELDS if not evidence.get(field)]
    if not evidence.get("expires_at"):
        errors.append("verification_evidence_missing_expires_at")
    return errors


def validate_contract() -> list[str]:
    errors: list[str] = []
    for export_id, item in export_items():
        if item.get("type") not in PRODUCT_TYPES:
            continue
        item_id = str(item.get("id") or "<missing>")
        status = item.get("recommendation_status")
        scope = item.get("recommendation_scope")
        verification_status = item.get("verification_status")
        for field in REQUIRED_CONTRACT_FIELDS:
            if field not in item:
                errors.append(f"{export_id}:{item_id}: missing contract field {field}")
        if status not in VALID_STATUSES:
            errors.append(f"{export_id}:{item_id}: invalid recommendation_status {status}")
        if scope not in VALID_SCOPES:
            errors.append(f"{export_id}:{item_id}: invalid recommendation_scope {scope}")
        if scope in {None, "", "unspecified"}:
            errors.append(f"{export_id}:{item_id}: recommendation_scope must not be unspecified")
        if verification_status not in VALID_VERIFICATION_STATUSES:
            errors.append(f"{export_id}:{item_id}: invalid verification_status {verification_status}")
        if status == "verified_recommendation_candidate":
            if scope != "public_recommendation":
                errors.append(f"{export_id}:{item_id}: verified candidate must use public_recommendation scope")
            errors.extend(f"{export_id}:{item_id}: {error}" for error in validate_evidence(item))
            if verification_status != "verified":
                errors.append(f"{export_id}:{item_id}: verified candidate must use verification_status verified")
        if scope == "public_recommendation" and verification_status != "verified":
            errors.append(f"{export_id}:{item_id}: public recommendation requires verified verification_status")
        if verification_status == "verified" and not item.get("verification_evidence"):
            errors.append(f"{export_id}:{item_id}: verified status requires verification evidence")
        if verification_status == "verified" and item.get("source_checksum") not in set((item.get("verification_evidence") or {}).get("source_checksums") or []):
            errors.append(f"{export_id}:{item_id}: verified status requires matching source checksum")
        if status == "reference_only" and scope == "public_recommendation":
            errors.append(f"{export_id}:{item_id}: reference_only cannot be public_recommendation")
    overlay = load_json(OVERLAY_PATH) if OVERLAY_PATH.exists() else {"verifications": []}
    for index, record in enumerate(overlay.get("verifications") or [], start=1):
        if not isinstance(record, dict):
            errors.append(f"overlay:{index}: verification record must be object")
            continue
        errors.extend(f"overlay:{index}: {error}" for error in verification_errors(record))
    return errors


def main() -> int:
    errors = validate_contract()
    if errors:
        print("Recommendation contract validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1
    print("Recommendation contract validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
