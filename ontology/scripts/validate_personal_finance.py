#!/usr/bin/env python3
"""Offline regression checks for the personal-finance decision-support layer."""

from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from personal_finance import (  # noqa: E402
    FinanceSnapshotError,
    calculate_finance_metrics,
    evaluate_product_fit,
    simulate_finance_scenario,
    validate_finance_advice,
)


def close(value: object, expected: float, tolerance: float = 0.0001) -> bool:
    return isinstance(value, (int, float)) and abs(float(value) - expected) <= tolerance


def main() -> int:
    snapshot = {
        "as_of": "2026-07-26",
        "currency": "KRW",
        "monthly_net_income_krw": 5_000_000,
        "essential_monthly_expenses_krw": 2_000_000,
        "discretionary_monthly_expenses_krw": 0,
        "liquid_assets_krw": 3_000_000,
        "investment_assets_krw": 10_000_000,
        "liabilities": [{"id": "loan-1", "balance_krw": 10_000_000, "annual_rate_percent": 18, "monthly_payment_krw": 300_000}],
        "liquidity_requirement": {"months": 3},
        "goals": [{"id": "goal-1", "name": "보증금", "target_amount_krw": 4_000_000, "current_funding_krw": 3_000_000, "liquidity_need": "short"}],
        "asset_allocation": {"cash": 3_000_000, "fund": 7_000_000},
        "insurance_coverage": {"required_coverage_krw": 8_000_000, "current_coverage_krw": 3_000_000},
    }
    metrics = calculate_finance_metrics(snapshot)["metrics"]
    expected = {
        "net_worth": 3_000_000,
        "monthly_surplus": 2_700_000,
        "savings_rate": 0.54,
        "emergency_fund_months": 1.5,
        "debt_service_ratio": 0.06,
        "weighted_debt_rate_percent": 18,
        "liquidity_gap": 3_000_000,
        "goal_funding_gap": 1_000_000,
        "asset_concentration": 0.7,
        "insurance_coverage_gap": 5_000_000,
    }
    failures: list[str] = []
    for name, value in expected.items():
        if not close(metrics[name]["value"], value):
            failures.append(f"{name}: expected {value}, got {metrics[name]['value']}")

    try:
        calculate_finance_metrics({"as_of": "2026-07-26", "password": "must-not-enter"})
        failures.append("sensitive input was accepted")
    except FinanceSnapshotError:
        pass

    fit = evaluate_product_fit(
        snapshot,
        {
            "id": "product-1",
            "title": "Stale product",
            "status": "active",
            "product_status": "active",
            "source_listing_status": "listed",
            "freshness_status": "stale",
            "verification_status": "verified",
            "source_urls": ["https://example.invalid/source"],
        },
        "deposit",
    )
    if fit["eligible"] or "stale_source" not in fit["failed_conditions"]:
        failures.append("stale product passed fit evaluation")

    scenario = simulate_finance_scenario(snapshot, {"months": 6, "additional_monthly_payment_krw": 500_000, "monthly_contribution_krw": 100_000})
    if scenario["after"]["debt_balance_krw"] != 7_000_000 or scenario["after"]["liquid_assets_krw"] != 3_600_000:
        failures.append("scenario did not apply declared inputs deterministically")

    blocked = {
        "mode": "decision_support",
        "status": "blocked",
        "reason_codes": ["PUBLIC_RECOMMENDATION_DISABLED"],
        "profile_as_of": None,
        "data_as_of": "2026-07-26",
        "assumptions": [],
        "missing_information": [],
        "financial_needs": [],
        "candidates": [],
        "decision_owner": "user",
        "limitations": [],
        "audit_id": "fin-test-001",
    }
    if not validate_finance_advice(blocked)["valid"]:
        failures.append("blocked safety response failed validation")

    for schema_name in ("personal-finance.schema.json", "product-offer.schema.json", "recommendation-case.schema.json"):
        try:
            json.loads((ROOT / "schema" / schema_name).read_text(encoding="utf-8"))
        except Exception as exc:  # pragma: no cover - diagnostic branch
            failures.append(f"invalid JSON schema {schema_name}: {exc}")

    if failures:
        for failure in failures:
            print(f"[FAIL] {failure}")
        return 1
    print("OK: personal-finance metrics, safety, fit, scenario, and schema checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
