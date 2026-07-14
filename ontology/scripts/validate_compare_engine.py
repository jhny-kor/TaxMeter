#!/usr/bin/env python3
from __future__ import annotations

from product_comparison_engine import compare


def main() -> int:
    payload = compare({"domain": "deposit", "term_months": 12, "deposit_amount_krw": 10_000_000, "limit": 1})
    errors: list[str] = []
    if "excluded" in payload:
        errors.append("compare response exposes full excluded list")
    if len(payload.get("excluded_sample") or []) > 10:
        errors.append("excluded_sample exceeds 10")
    if int(payload.get("excluded_count") or 0) < len(payload.get("excluded_sample") or []):
        errors.append("excluded_count is smaller than excluded_sample")
    for key in ("excluded_summary", "blockers", "ontology_basis_date", "latest_product_collection_date", "verification_basis_date", "calculation_policy_basis_date", "executed_at"):
        if key not in payload:
            errors.append(f"missing compare field {key}")
    if errors:
        print("Compare engine validation failed:")
        print(*[f"- {error}" for error in errors], sep="\n")
        return 1
    print("Compare engine validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
