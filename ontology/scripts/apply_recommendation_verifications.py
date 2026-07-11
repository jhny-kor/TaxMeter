#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
OVERLAY_PATH = ROOT / "custom" / "finance" / "recommendation-verifications.json"
MODEL_VERSION = "openfin-recommendation-v0.1.0"
PRODUCT_TYPES = {"card-product", "bank-product", "insurance-product"}
VERIFICATION_REQUIRED_FIELDS = (
    "canonical_product_id",
    "verified_at",
    "reviewer",
    "source_urls",
    "source_checksums",
    "verified_fields",
)


def stable_checksum(value: Any) -> str:
    encoded = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def item_source_checksum(item: dict[str, Any]) -> str:
    source_payload = {
        "id": item.get("id"),
        "provider_code": item.get("provider_code"),
        "product_code": item.get("product_code"),
        "source_record_id": item.get("source_record_id"),
        "source_urls": item.get("source_urls") or [],
        "source_basis_dates": item.get("source_basis_dates") or [],
        "criteria": item.get("criteria") or [],
        "options": item.get("options") or [],
        "benefits": item.get("benefits") or [],
    }
    return stable_checksum(source_payload)


def load_overlay(path: Path = OVERLAY_PATH) -> dict[str, Any]:
    if not path.exists():
        return {"verifications": []}
    payload = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(payload, list):
        return {"verifications": payload}
    payload.setdefault("verifications", [])
    return payload


def verification_errors(record: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    for field in VERIFICATION_REQUIRED_FIELDS:
        if not record.get(field):
            errors.append(f"missing_{field}")
    if not record.get("expires_at") and not record.get("freshness_policy"):
        errors.append("missing_expires_at_or_freshness_policy")
    if record.get("product_name") and not record.get("canonical_product_id"):
        errors.append("product_name_only_match_forbidden")
    return errors


def overlay_by_product_id(payload: dict[str, Any]) -> dict[str, dict[str, Any]]:
    mapped: dict[str, dict[str, Any]] = {}
    for record in payload.get("verifications") or []:
        if isinstance(record, dict) and record.get("canonical_product_id"):
            mapped[str(record["canonical_product_id"])] = record
    return mapped


def apply_recommendation_verifications(items: list[dict[str, Any]], overlay_path: Path = OVERLAY_PATH) -> list[dict[str, Any]]:
    records = overlay_by_product_id(load_overlay(overlay_path))
    for item in items:
        if item.get("type") not in PRODUCT_TYPES:
            continue
        if item.get("recommendation_status") not in {
            "reference_only",
            "eligible_for_listing",
            "manual_review_candidate",
            "verified_recommendation_candidate",
        }:
            item["recommendation_status"] = "reference_only"
        if item.get("recommendation_scope") in {None, "", "unspecified"}:
            item["recommendation_scope"] = "listing_only"
        item["recommendation_model_version"] = MODEL_VERSION
        item["recommendation_basis_fields"] = item.get("recommendation_basis_fields") or []
        item["recommendation_exclusion_reasons"] = item.get("recommendation_exclusion_reasons") or []
        source_checksum = item_source_checksum(item)
        item["source_checksum"] = source_checksum
        record = records.get(str(item.get("id")))
        if not record:
            if item.get("recommendation_status") == "eligible_for_listing" and item.get("type") == "bank-product":
                item["recommendation_scope"] = "comparison_only"
            continue
        errors = verification_errors(record)
        matched_checksum = source_checksum in set(str(value) for value in record.get("source_checksums") or [])
        if errors or not matched_checksum:
            flags = [str(value) for value in item.get("quality_flags") or []]
            flags.append("verification_overlay_invalid" if errors else "verification_checksum_mismatch")
            item["quality_flags"] = sorted(set(flags))
            reasons = [str(value) for value in item.get("recommendation_exclusion_reasons") or []]
            reasons.extend(errors or ["source_checksum_mismatch"])
            item["recommendation_exclusion_reasons"] = sorted(set(reasons))
            continue
        item["recommendation_status"] = "verified_recommendation_candidate"
        item["recommendation_scope"] = "public_recommendation"
        item["last_verified_at"] = record["verified_at"]
        item["recommendation_basis_fields"] = record.get("verified_fields") or []
        item["verification_evidence"] = {
            "reviewer": record.get("reviewer"),
            "verified_at": record.get("verified_at"),
            "source_urls": record.get("source_urls") or [],
            "source_checksums": record.get("source_checksums") or [],
            "verified_fields": record.get("verified_fields") or [],
            "expires_at": record.get("expires_at"),
            "freshness_policy": record.get("freshness_policy"),
        }
    return items
