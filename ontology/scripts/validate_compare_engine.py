#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

from product_comparison_engine import compare


EXPORT_DIR = Path(__file__).resolve().parents[1] / "exports"


def main() -> int:
    errors: list[str] = []
    payloads = {
        "deposit": compare({"domain": "deposit", "term_months": 12, "deposit_amount_krw": 10_000_000, "limit": 20}),
        "saving": compare({"domain": "saving", "term_months": 12, "monthly_payment_krw": 500_000, "limit": 20}),
    }
    for domain, payload in payloads.items():
        if int(payload.get("candidate_count") or 0) < 10:
            errors.append(f"{domain}: expected at least 10 comparison candidates")
        if sum(int(value) for value in (payload.get("excluded_summary") or {}).values()) != int(payload.get("excluded_count") or 0):
            errors.append(f"{domain}: blocker counts do not sum to excluded_count")
        if (payload.get("filter_exclusions") or {}) != (payload.get("excluded_summary") or {}):
            errors.append(f"{domain}: filter_exclusions differs from excluded_summary")
        if int(payload.get("candidate_count") or 0) + int(payload.get("excluded_count") or 0) != int(payload.get("comparison_target_count") or 0):
            errors.append(f"{domain}: candidate_count + excluded_count does not equal comparison_target_count")
    for domain, payload in payloads.items():
        if "excluded" in payload:
            errors.append(f"{domain}: compare response exposes full excluded list")
        if len(payload.get("excluded_sample") or []) > 10:
            errors.append(f"{domain}: excluded_sample exceeds 10")
        if int(payload.get("excluded_count") or 0) < len(payload.get("excluded_sample") or []):
            errors.append(f"{domain}: excluded_count is smaller than excluded_sample")
        for key in ("excluded_summary", "blockers", "ontology_basis_date", "latest_product_collection_date", "verification_basis_date", "calculation_policy_basis_date", "executed_at"):
            if key not in payload:
                errors.append(f"{domain}: missing compare field {key}")
        if payload.get("latest_product_collection_date") != payload.get("verification_basis_date"):
            errors.append(f"{domain}: collection and verification basis dates differ")
        for candidate in payload.get("candidates") or []:
            if candidate.get("comparison_field_verification_status") == "verified_active" and "sales_verification_status" in (candidate.get("missing_required_fields") or []):
                errors.append(f"{domain}: verified candidate still lists sales_verification_status as missing")
    for domain, filename in {
        "deposit": "korea-deposit-products-ontology-2026.json",
        "saving": "korea-saving-products-ontology-2026.json",
    }.items():
        payload = json.loads((EXPORT_DIR / filename).read_text(encoding="utf-8"))
        for item in payload.get("items") or []:
            if (
                item.get("sales_verification_status") == "verified_active"
                and item.get("verification_status") == "verified"
                and item.get("comparison_engine_gate_passed") is True
                and "sales_verification_status" in (item.get("missing_required_fields") or [])
            ):
                errors.append(f"{domain}: exported verified candidate still lists sales_verification_status as missing: {item.get('id')}")
    if errors:
        print("Compare engine validation failed:")
        print(*[f"- {error}" for error in errors], sep="\n")
        return 1
    print("Compare engine validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
