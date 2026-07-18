#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
from datetime import date
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
OVERLAY_PATH = ROOT / "custom" / "finance" / "recommendation-verifications.json"
MODEL_VERSION = "openfin-recommendation-v0.1.0"
PRODUCT_TYPES = {"card-product", "bank-product", "insurance-product"}
COMPARISON_DOMAINS = {"deposit", "saving"}
VERIFICATION_REQUIRED_FIELDS = (
    "canonical_product_id",
    "verified_at",
    "reviewed_at",
    "reviewer",
    "source_checksums",
    "verified_fields",
    "expires_at",
    "sales_verification_status",
    "evidence",
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
        "title": item.get("title"),
        "sales_status": item.get("sales_status"),
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
    expires_at = record.get("expires_at")
    if not isinstance(expires_at, str):
        errors.append("missing_expires_at")
    else:
        try:
            date.fromisoformat(expires_at)
        except ValueError:
            errors.append("invalid_expires_at")
    for field in ("verified_at", "reviewed_at"):
        value = record.get(field)
        if not isinstance(value, str):
            errors.append(f"invalid_{field}")
            continue
        try:
            if date.fromisoformat(value) > date.today():
                errors.append(f"future_{field}")
        except ValueError:
            errors.append(f"invalid_{field}")
    if record.get("product_name") and not record.get("canonical_product_id"):
        errors.append("product_name_only_match_forbidden")
    if record.get("decision") not in {"approved", "verified"}:
        errors.append("decision_must_be_approved")
    if record.get("sales_verification_status") != "verified_active":
        errors.append("sales_verification_status_must_be_verified_active")
    if not isinstance(record.get("evidence"), list) or not record.get("evidence"):
        errors.append("missing_evidence")
    else:
        for index, evidence in enumerate(record["evidence"], start=1):
            if not isinstance(evidence, dict):
                errors.append(f"evidence_{index}_must_be_object")
                continue
            for field in ("source_url", "document_type", "locator", "captured_at"):
                if not isinstance(evidence.get(field), str) or not evidence[field].strip():
                    errors.append(f"evidence_{index}_missing_{field}")
            captured_at = evidence.get("captured_at")
            if isinstance(captured_at, str):
                try:
                    if date.fromisoformat(captured_at) > date.today():
                        errors.append(f"evidence_{index}_future_captured_at")
                except ValueError:
                    errors.append(f"evidence_{index}_invalid_captured_at")
            if not any(isinstance(evidence.get(field), str) and evidence[field].strip() for field in ("field", "verified_field")):
                errors.append(f"evidence_{index}_missing_field")
            has_value = evidence.get("value") not in (None, "")
            has_source_text = isinstance(evidence.get("source_text"), str) and bool(evidence["source_text"].strip())
            if not has_value and not has_source_text:
                errors.append(f"evidence_{index}_missing_value")
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
        item["canonical_product_id"] = str(item.get("canonical_product_id") or item.get("id") or "")
        item["recommendation_basis_fields"] = item.get("recommendation_basis_fields") or []
        item["recommendation_exclusion_reasons"] = item.get("recommendation_exclusion_reasons") or []
        item["public_recommendation_exclusion_reasons"] = list(item["recommendation_exclusion_reasons"])
        item["comparison_exclusion_reasons"] = []
        item["discovery_limitations"] = ["sales_status_unverified"]
        item["verification_status"] = "not_verified"
        item["verification_evidence"] = None
        item["last_verified_at"] = None
        source_checksum = item_source_checksum(item)
        item["source_checksum"] = source_checksum
        comparison_ready = item.get("search_type") in COMPARISON_DOMAINS and item.get("comparison_field_verification_status") == "verified"
        item["comparison_engine_gate_passed"] = bool(comparison_ready and item.get("sales_verification_status") == "verified_active")
        record = records.get(str(item["canonical_product_id"]))
        if not record:
            if item.get("recommendation_status") == "eligible_for_listing" and item.get("type") == "bank-product":
                item["recommendation_scope"] = "comparison_only"
            item["catalog_recommendation_status"] = item["recommendation_status"]
            item["catalog_recommendation_scope"] = item["recommendation_scope"]
            continue
        errors = verification_errors(record)
        matched_checksum = source_checksum in set(str(value) for value in record.get("source_checksums") or [])
        expires_at = str(record.get("expires_at") or "")
        is_expired = bool(expires_at and expires_at < date.today().isoformat())
        if errors or not matched_checksum or is_expired:
            flags = [str(value) for value in item.get("quality_flags") or []]
            flags.append("verification_overlay_invalid" if errors else "verification_checksum_mismatch")
            item["quality_flags"] = sorted(set(flags))
            reasons = [str(value) for value in item.get("recommendation_exclusion_reasons") or []]
            reasons.extend(errors or (["verification_expired"] if is_expired else ["source_checksum_mismatch"]))
            item["recommendation_exclusion_reasons"] = sorted(set(reasons))
            item["verification_status"] = "expired" if is_expired else ("source_changed" if not matched_checksum else "rejected")
            item["catalog_recommendation_status"] = item["recommendation_status"]
            item["catalog_recommendation_scope"] = item["recommendation_scope"]
            continue
        item["verification_evidence"] = {
            "reviewer": record.get("reviewer"),
            "verified_at": record.get("verified_at"),
            "reviewed_at": record.get("reviewed_at"),
            "source_urls": record.get("source_urls") or [entry.get("source_url") for entry in record.get("evidence") or [] if isinstance(entry, dict) and entry.get("source_url")],
            "source_checksums": record.get("source_checksums") or [],
            "verified_fields": record.get("verified_fields") or [],
            "expires_at": record.get("expires_at"),
            "freshness_policy": record.get("freshness_policy"),
            "evidence": record.get("evidence") or [],
        }
        item["sales_status"] = "active"
        item["sales_verification_status"] = "verified_active"
        item["sales_verified_at"] = record.get("verified_at")
        item["condition_verification_status"] = "verified"
        item["last_verified_at"] = record.get("verified_at")
        item["verified_completeness_ratio"] = item.get("completeness_ratio", 0)
        item["domain_gate_passed"] = (
            not item.get("missing_required_fields")
            and item.get("source_freshness_status") == "current"
            and item.get("sales_verification_status") == "verified_active"
        )
        item["comparison_engine_gate_passed"] = bool(
            comparison_ready
            or (item.get("search_type") == "loan" and not item.get("missing_required_fields"))
        )
        item["verification_status"] = "verified"
        if not item.get("domain_gate_passed"):
            item["verification_status"] = "verified"
            item["recommendation_scope"] = "comparison_only" if item.get("type") == "bank-product" else "listing_only"
            item["recommendation_exclusion_reasons"] = sorted(set([*item["recommendation_exclusion_reasons"], "domain_gate_not_passed"]))
            item["public_recommendation_exclusion_reasons"] = list(item["recommendation_exclusion_reasons"])
            item["catalog_recommendation_status"] = item["recommendation_status"]
            item["catalog_recommendation_scope"] = item["recommendation_scope"]
            continue
        if item.get("type") == "bank-product":
            if item.get("recommendation_status") != "manual_review_candidate":
                item["recommendation_status"] = "reference_only"
            item["recommendation_scope"] = "internal_verification_candidate" if item.get("recommendation_status") == "manual_review_candidate" else "comparison_only"
            item["recommendation_exclusion_reasons"] = sorted(set([*item["recommendation_exclusion_reasons"], "public_recommendation_pending_approval"]))
            item["public_recommendation_exclusion_reasons"] = list(item["recommendation_exclusion_reasons"])
            item["discovery_limitations"] = ["public_recommendation_pending_approval"]
            item["catalog_recommendation_status"] = item["recommendation_status"]
            item["catalog_recommendation_scope"] = item["recommendation_scope"]
            continue
        if item.get("type") == "card-product":
            item["recommendation_status"] = "manual_review_candidate"
            item["recommendation_scope"] = "listing_only"
            item["recommendation_exclusion_reasons"] = sorted(set([*item["recommendation_exclusion_reasons"], "public_recommendation_pending_approval"]))
            item["public_recommendation_exclusion_reasons"] = list(item["recommendation_exclusion_reasons"])
            item["discovery_limitations"] = ["public_recommendation_pending_approval"]
            item["catalog_recommendation_status"] = item["recommendation_status"]
            item["catalog_recommendation_scope"] = item["recommendation_scope"]
            continue
        item["recommendation_status"] = "reference_only"
        item["recommendation_scope"] = "listing_only"
        item["recommendation_exclusion_reasons"] = sorted(set([*item["recommendation_exclusion_reasons"], "public_recommendation_pending_approval"]))
        item["public_recommendation_exclusion_reasons"] = list(item["recommendation_exclusion_reasons"])
        item["discovery_limitations"] = ["public_recommendation_pending_approval"]
        item["catalog_recommendation_status"] = item["recommendation_status"]
        item["catalog_recommendation_scope"] = item["recommendation_scope"]
        continue
        item["recommendation_status"] = "verified_recommendation_candidate"
        item["recommendation_scope"] = "public_recommendation"
        item["verification_status"] = "verified"
        item["recommendation_basis_fields"] = record.get("verified_fields") or []
        item["public_recommendation_exclusion_reasons"] = []
        item["discovery_limitations"] = []
        item["catalog_recommendation_status"] = item["recommendation_status"]
        item["catalog_recommendation_scope"] = item["recommendation_scope"]
    return items
