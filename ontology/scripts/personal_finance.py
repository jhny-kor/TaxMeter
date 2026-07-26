#!/usr/bin/env python3
"""Deterministic, privacy-preserving personal-finance decision support.

This module deliberately accepts only a transient, typed snapshot.  It does
not persist a user's financial state and it never turns incomplete product
data into a recommendation.  The MCP layer is responsible for the owner
authentication and write-confirmation boundary.
"""

from __future__ import annotations

import hashlib
import json
import math
from datetime import date
from typing import Any


POLICY_VERSION = "openfin-personal-finance-v1.0.0"
ADVICE_POLICY_VERSION = "openfin-advice-policy-v1.0.0"
MINIMUM_EMERGENCY_FUND_MONTHS = 3.0
HIGH_INTEREST_DEBT_RATE_PERCENT = 15.0

SENSITIVE_KEY_TOKENS = {
    "accountnumber",
    "bankaccount",
    "cardnumber",
    "creditcardnumber",
    "residentregistrationnumber",
    "rrn",
    "password",
    "passcode",
    "pin",
    "certificate",
    "privatekey",
    "apikey",
    "apitoken",
    "accesstoken",
    "refreshtoken",
    "secret",
    "ssn",
}


class FinanceSnapshotError(ValueError):
    """Raised when an input snapshot is unsafe or structurally invalid."""


def _key_token(value: object) -> str:
    return "".join(character for character in str(value).casefold() if character.isalnum())


def _scan_sensitive(value: object, path: str = "snapshot") -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            token = _key_token(key)
            if token in SENSITIVE_KEY_TOKENS or any(
                token.endswith(suffix) for suffix in ("password", "token", "secret", "privatekey")
            ):
                raise FinanceSnapshotError(f"sensitive field is not accepted: {path}.{key}")
            _scan_sensitive(child, f"{path}.{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            _scan_sensitive(child, f"{path}[{index}]")


def _number(value: object, field: str, *, allow_negative: bool = False) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise FinanceSnapshotError(f"{field} must be a number")
    numeric = float(value)
    if not math.isfinite(numeric) or (not allow_negative and numeric < 0):
        raise FinanceSnapshotError(f"{field} must be a finite {'non-negative ' if not allow_negative else ''}number")
    return round(numeric, 6)


def _optional_number(value: object, field: str, *, allow_negative: bool = False) -> float | None:
    if value in (None, ""):
        return None
    return _number(value, field, allow_negative=allow_negative)


def _first_number(source: dict[str, Any], keys: tuple[str, ...], field: str) -> float | None:
    for key in keys:
        if key in source and source[key] not in (None, ""):
            return _number(source[key], field)
    return None


def _normalize_liabilities(value: object) -> list[dict[str, Any]]:
    if value in (None, ""):
        return []
    raw_items: list[Any]
    if isinstance(value, dict):
        raw_items = [value]
    elif isinstance(value, list):
        raw_items = value
    else:
        raise FinanceSnapshotError("liabilities must be an array or object")
    normalized: list[dict[str, Any]] = []
    for index, raw in enumerate(raw_items):
        if not isinstance(raw, dict):
            raise FinanceSnapshotError(f"liabilities[{index}] must be an object")
        balance = _first_number(raw, ("balance_krw", "balance", "principal_krw"), f"liabilities[{index}].balance_krw")
        if balance is None:
            raise FinanceSnapshotError(f"liabilities[{index}].balance_krw is required")
        normalized.append(
            {
                "id": str(raw.get("id") or f"liability-{index + 1}"),
                "kind": str(raw.get("kind") or "unspecified"),
                "balance_krw": balance,
                "annual_rate_percent": _optional_number(
                    raw.get("annual_rate_percent", raw.get("rate_percent")),
                    f"liabilities[{index}].annual_rate_percent",
                ),
                "monthly_payment_krw": _optional_number(
                    raw.get("monthly_payment_krw", raw.get("monthly_payment")),
                    f"liabilities[{index}].monthly_payment_krw",
                ),
                "remaining_term_months": _optional_number(
                    raw.get("remaining_term_months"),
                    f"liabilities[{index}].remaining_term_months",
                ),
            }
        )
    return normalized


def _normalize_goals(value: object) -> list[dict[str, Any]]:
    if value in (None, ""):
        return []
    if not isinstance(value, list):
        raise FinanceSnapshotError("goals must be an array")
    normalized: list[dict[str, Any]] = []
    for index, raw in enumerate(value):
        if not isinstance(raw, dict):
            raise FinanceSnapshotError(f"goals[{index}] must be an object")
        target = _first_number(raw, ("target_amount_krw", "amount_krw", "amount"), f"goals[{index}].target_amount_krw")
        if target is None:
            raise FinanceSnapshotError(f"goals[{index}].target_amount_krw is required")
        current = _first_number(raw, ("current_funding_krw", "current_amount_krw", "current"), f"goals[{index}].current_funding_krw") or 0.0
        normalized.append(
            {
                "id": str(raw.get("id") or f"goal-{index + 1}"),
                "name": str(raw.get("name") or raw.get("title") or f"goal-{index + 1}"),
                "target_amount_krw": target,
                "current_funding_krw": current,
                "target_date": str(raw.get("target_date") or "") or None,
                "priority": str(raw.get("priority") or "normal"),
                "liquidity_need": str(raw.get("liquidity_need") or "unknown"),
            }
        )
    return normalized


def normalize_finance_snapshot(snapshot: dict[str, Any] | None) -> dict[str, Any]:
    """Validate and normalize a transient user snapshot without persisting it."""

    if snapshot is None:
        return {}
    if not isinstance(snapshot, dict):
        raise FinanceSnapshotError("snapshot must be an object")
    _scan_sensitive(snapshot)
    expenses = snapshot.get("expenses") if isinstance(snapshot.get("expenses"), dict) else {}
    normalized: dict[str, Any] = {
        "as_of": str(snapshot.get("as_of") or snapshot.get("profile_as_of") or "") or None,
        "currency": str(snapshot.get("currency") or "KRW").upper(),
        "monthly_net_income_krw": _first_number(
            snapshot,
            ("monthly_net_income_krw", "monthly_net_income", "monthly_income_krw", "monthly_income"),
            "monthly_net_income_krw",
        ),
        "essential_monthly_expenses_krw": _first_number(
            snapshot,
            ("essential_monthly_expenses_krw", "essential_expenses_krw", "essential_monthly_expenses"),
            "essential_monthly_expenses_krw",
        )
        if any(key in snapshot for key in ("essential_monthly_expenses_krw", "essential_expenses_krw", "essential_monthly_expenses"))
        else _first_number(expenses, ("essential_krw", "essential_monthly_krw", "essential"), "essential_monthly_expenses_krw"),
        "discretionary_monthly_expenses_krw": _first_number(
            snapshot,
            ("discretionary_monthly_expenses_krw", "optional_monthly_expenses_krw", "discretionary_expenses_krw"),
            "discretionary_monthly_expenses_krw",
        )
        if any(key in snapshot for key in ("discretionary_monthly_expenses_krw", "optional_monthly_expenses_krw", "discretionary_expenses_krw"))
        else _first_number(expenses, ("discretionary_krw", "optional_krw", "discretionary"), "discretionary_monthly_expenses_krw"),
        "liquid_assets_krw": _first_number(snapshot, ("liquid_assets_krw", "liquid_assets"), "liquid_assets_krw"),
        "investment_assets_krw": _first_number(snapshot, ("investment_assets_krw", "investment_assets"), "investment_assets_krw"),
        "other_assets_krw": _first_number(snapshot, ("other_assets_krw", "other_assets"), "other_assets_krw") or 0.0,
        "liabilities": _normalize_liabilities(snapshot.get("liabilities")),
        "goals": _normalize_goals(snapshot.get("goals")),
        "dependents": int(_number(snapshot.get("dependents", 0), "dependents")),
        "liquidity_requirement": snapshot.get("liquidity_requirement") if isinstance(snapshot.get("liquidity_requirement"), (dict, int, float)) else None,
        "risk_tolerance": str(snapshot.get("risk_tolerance") or "unknown"),
        "risk_capacity": str(snapshot.get("risk_capacity") or "unknown"),
        "constraints": dict(snapshot.get("constraints") or {}) if isinstance(snapshot.get("constraints"), dict) else {},
        "asset_allocation": dict(snapshot.get("asset_allocation") or {}) if isinstance(snapshot.get("asset_allocation"), dict) else {},
        "insurance_coverage": dict(snapshot.get("insurance_coverage") or {}) if isinstance(snapshot.get("insurance_coverage"), dict) else {},
    }
    if normalized["as_of"]:
        try:
            date.fromisoformat(str(normalized["as_of"]))
        except ValueError as exc:
            raise FinanceSnapshotError("as_of must use YYYY-MM-DD") from exc
    return normalized


def required_snapshot_fields(snapshot: dict[str, Any]) -> list[str]:
    required = (
        "as_of",
        "monthly_net_income_krw",
        "essential_monthly_expenses_krw",
        "liquid_assets_krw",
        "investment_assets_krw",
    )
    return [field for field in required if snapshot.get(field) in (None, "")]


def _metric(name: str, value: float | None, formula: str, inputs: dict[str, Any], assumptions: list[str], snapshot: dict[str, Any]) -> dict[str, Any]:
    return {
        "metric": name,
        "value": None if value is None else round(float(value), 6),
        "formula": formula,
        "inputs": inputs,
        "assumptions": assumptions,
        "calculated_at": snapshot.get("as_of") or "unspecified",
        "policy_version": POLICY_VERSION,
    }


def _debt_balance(snapshot: dict[str, Any]) -> float:
    return sum(float(item.get("balance_krw") or 0) for item in snapshot.get("liabilities") or [])


def _debt_service(snapshot: dict[str, Any]) -> float:
    return sum(float(item.get("monthly_payment_krw") or 0) for item in snapshot.get("liabilities") or [])


def calculate_net_worth(snapshot: dict[str, Any]) -> dict[str, Any]:
    assets = sum(float(snapshot.get(key) or 0) for key in ("liquid_assets_krw", "investment_assets_krw", "other_assets_krw"))
    debt = _debt_balance(snapshot)
    return _metric("net_worth", assets - debt, "liquid_assets + investment_assets + other_assets - liability_balances", {"assets_krw": assets, "liabilities_krw": debt}, [], snapshot)


def calculate_monthly_surplus(snapshot: dict[str, Any]) -> dict[str, Any]:
    income = snapshot.get("monthly_net_income_krw")
    essential = snapshot.get("essential_monthly_expenses_krw")
    discretionary = snapshot.get("discretionary_monthly_expenses_krw") or 0
    debt_service = _debt_service(snapshot)
    value = None if income is None or essential is None else float(income) - float(essential) - float(discretionary) - debt_service
    return _metric("monthly_surplus", value, "net_income - essential_expenses - discretionary_expenses - debt_service", {"income_krw": income, "essential_krw": essential, "discretionary_krw": discretionary, "debt_service_krw": debt_service}, [], snapshot)


def calculate_savings_rate(snapshot: dict[str, Any]) -> dict[str, Any]:
    income = snapshot.get("monthly_net_income_krw")
    surplus = calculate_monthly_surplus(snapshot)["value"]
    value = None if income in (None, 0) or surplus is None else float(surplus) / float(income)
    assumptions = ["income must be positive"] if income in (None, 0) else []
    return _metric("savings_rate", value, "monthly_surplus / monthly_net_income", {"income_krw": income, "surplus_krw": surplus}, assumptions, snapshot)


def calculate_emergency_fund_months(snapshot: dict[str, Any]) -> dict[str, Any]:
    liquid = snapshot.get("liquid_assets_krw")
    essential = snapshot.get("essential_monthly_expenses_krw")
    value = None if liquid is None or essential in (None, 0) else float(liquid) / float(essential)
    return _metric("emergency_fund_months", value, "liquid_assets / essential_monthly_expenses", {"liquid_assets_krw": liquid, "essential_krw": essential}, ["only liquid assets are counted"], snapshot)


def calculate_debt_service_ratio(snapshot: dict[str, Any]) -> dict[str, Any]:
    income = snapshot.get("monthly_net_income_krw")
    service = _debt_service(snapshot)
    value = None if income in (None, 0) else service / float(income)
    return _metric("debt_service_ratio", value, "monthly_debt_service / monthly_net_income", {"debt_service_krw": service, "income_krw": income}, [], snapshot)


def calculate_weighted_debt_rate(snapshot: dict[str, Any]) -> dict[str, Any]:
    liabilities = [item for item in snapshot.get("liabilities") or [] if item.get("annual_rate_percent") is not None]
    balance = sum(float(item.get("balance_krw") or 0) for item in liabilities)
    value = None if not liabilities or balance == 0 else sum(float(item["balance_krw"]) * float(item["annual_rate_percent"]) for item in liabilities) / balance
    return _metric("weighted_debt_rate_percent", value, "sum(balance * annual_rate) / sum(balance)", {"rate_known_balance_krw": balance, "liability_count": len(liabilities)}, ["liabilities without a known rate are excluded"], snapshot)


def _required_liquidity(snapshot: dict[str, Any]) -> tuple[float | None, list[str]]:
    requirement = snapshot.get("liquidity_requirement")
    if isinstance(requirement, (int, float)):
        return float(requirement), []
    if not isinstance(requirement, dict):
        return None, ["liquidity_requirement is missing"]
    if requirement.get("required_amount_krw") not in (None, ""):
        return _number(requirement["required_amount_krw"], "liquidity_requirement.required_amount_krw"), []
    if requirement.get("months") not in (None, "") and snapshot.get("essential_monthly_expenses_krw") is not None:
        return _number(requirement["months"], "liquidity_requirement.months") * float(snapshot["essential_monthly_expenses_krw"]), []
    return None, ["liquidity requirement needs required_amount_krw or months plus essential expenses"]


def calculate_liquidity_gap(snapshot: dict[str, Any]) -> dict[str, Any]:
    required, assumptions = _required_liquidity(snapshot)
    liquid = snapshot.get("liquid_assets_krw")
    value = None if required is None or liquid is None else max(0.0, required - float(liquid))
    return _metric("liquidity_gap", value, "max(0, required_liquidity - liquid_assets)", {"required_liquidity_krw": required, "liquid_assets_krw": liquid}, assumptions, snapshot)


def calculate_goal_funding_gap(snapshot: dict[str, Any]) -> dict[str, Any]:
    goals = snapshot.get("goals") or []
    value = sum(max(0.0, float(goal["target_amount_krw"]) - float(goal.get("current_funding_krw") or 0)) for goal in goals)
    return _metric("goal_funding_gap", value, "sum(max(0, target_amount - current_funding))", {"goal_count": len(goals)}, [], snapshot)


def calculate_asset_concentration(snapshot: dict[str, Any]) -> dict[str, Any]:
    allocation = {str(key): float(value) for key, value in (snapshot.get("asset_allocation") or {}).items() if value not in (None, "")}
    total = sum(allocation.values())
    value = None if not allocation or total <= 0 else max(allocation.values()) / total
    return _metric("asset_concentration", value, "max(asset_class_value) / total_allocated_asset_value", {"allocation": allocation, "allocation_total_krw": total}, ["asset allocation is required; a single investment_assets total is insufficient"], snapshot)


def calculate_insurance_coverage_gap(snapshot: dict[str, Any]) -> dict[str, Any]:
    coverage = snapshot.get("insurance_coverage") or {}
    required = _optional_number(coverage.get("required_coverage_krw"), "insurance_coverage.required_coverage_krw")
    current = _optional_number(coverage.get("current_coverage_krw"), "insurance_coverage.current_coverage_krw") or 0
    value = None if required is None else max(0.0, required - current)
    return _metric("insurance_coverage_gap", value, "max(0, required_coverage - current_coverage)", {"required_coverage_krw": required, "current_coverage_krw": current}, ["coverage need must be explicitly supplied"], snapshot)


METRIC_FUNCTIONS = {
    "net_worth": calculate_net_worth,
    "monthly_surplus": calculate_monthly_surplus,
    "savings_rate": calculate_savings_rate,
    "emergency_fund_months": calculate_emergency_fund_months,
    "debt_service_ratio": calculate_debt_service_ratio,
    "weighted_debt_rate_percent": calculate_weighted_debt_rate,
    "liquidity_gap": calculate_liquidity_gap,
    "goal_funding_gap": calculate_goal_funding_gap,
    "asset_concentration": calculate_asset_concentration,
    "insurance_coverage_gap": calculate_insurance_coverage_gap,
}


def calculate_finance_metrics(raw_snapshot: dict[str, Any] | None) -> dict[str, Any]:
    snapshot = normalize_finance_snapshot(raw_snapshot)
    metrics = {name: function(snapshot) for name, function in METRIC_FUNCTIONS.items()}
    missing = required_snapshot_fields(snapshot)
    return {
        "mode": "decision_support",
        "status": "insufficient_information" if missing else "ready",
        "reason_codes": ["MISSING_FINANCE_SNAPSHOT_FIELDS"] if missing else [],
        "metrics": metrics,
        "missing_information": missing,
        "financial_needs": [],
        "candidates": [],
        "profile_as_of": snapshot.get("as_of"),
        "data_as_of": snapshot.get("as_of"),
        "assumptions": ["deterministic formulas; missing inputs produce null metrics"],
        "currency": snapshot.get("currency", "KRW"),
        "decision_owner": "user",
        "limitations": ["metrics are educational and not financial advice"],
        "audit_id": finance_audit_id("metrics", snapshot),
        "policy_version": POLICY_VERSION,
    }


def prioritize_financial_needs(raw_snapshot: dict[str, Any] | None) -> dict[str, Any]:
    snapshot = normalize_finance_snapshot(raw_snapshot)
    calculated = calculate_finance_metrics(snapshot)
    metrics = calculated["metrics"]
    missing = list(calculated["missing_information"])
    needs: list[dict[str, Any]] = []
    if missing:
        needs.append({"need_type": "information_completion", "priority": 1, "status": "blocked", "evidence": missing, "action": "request_missing_finance_snapshot_fields"})
    surplus = metrics["monthly_surplus"]["value"]
    if surplus is not None and surplus < 0:
        needs.append({"need_type": "cashflow_stabilization", "priority": 1, "status": "active", "evidence": {"monthly_surplus_krw": surplus}, "action": "reduce_deficit_before_product_selection"})
    debt_rate = metrics["weighted_debt_rate_percent"]["value"]
    if debt_rate is not None and debt_rate >= HIGH_INTEREST_DEBT_RATE_PERCENT:
        needs.append({"need_type": "high_interest_debt", "priority": 2, "status": "active", "evidence": {"weighted_debt_rate_percent": debt_rate}, "action": "compare_debt_paydown_scenarios"})
    emergency = metrics["emergency_fund_months"]["value"]
    if emergency is not None and emergency < MINIMUM_EMERGENCY_FUND_MONTHS:
        needs.append({"need_type": "emergency_liquidity", "priority": 2, "status": "active", "evidence": {"emergency_fund_months": emergency, "target_months": MINIMUM_EMERGENCY_FUND_MONTHS}, "action": "protect_liquid_principal"})
    liquidity_gap = metrics["liquidity_gap"]["value"]
    if liquidity_gap is not None and liquidity_gap > 0:
        needs.append({"need_type": "liquidity_gap", "priority": 2, "status": "active", "evidence": {"liquidity_gap_krw": liquidity_gap}, "action": "avoid_locking_required_liquidity"})
    coverage_gap = metrics["insurance_coverage_gap"]["value"]
    if coverage_gap is not None and coverage_gap > 0:
        needs.append({"need_type": "insurance_coverage_gap", "priority": 3, "status": "active", "evidence": {"coverage_gap_krw": coverage_gap}, "action": "review_protection_gap_as_lookup_only"})
    for goal in snapshot.get("goals") or []:
        if goal.get("liquidity_need") in {"high", "short", "principal"}:
            needs.append({"need_type": "short_horizon_goal", "priority": 2, "status": "active", "evidence": {"goal_id": goal["id"], "target_date": goal.get("target_date")}, "action": "prefer_liquid_principal_preserving_options"})
        elif goal.get("liquidity_need") in {"low", "long", "growth"}:
            needs.append({"need_type": "long_horizon_goal", "priority": 4, "status": "active", "evidence": {"goal_id": goal["id"], "target_date": goal.get("target_date")}, "action": "separate_long_horizon_risk_discussion"})
    needs.sort(key=lambda item: (int(item["priority"]), str(item["need_type"])))
    return {
        "financial_needs": needs,
        "missing_information": missing,
        "metrics": metrics,
        "profile_as_of": snapshot.get("as_of"),
        "policy_version": ADVICE_POLICY_VERSION,
        "decision_owner": "user",
    }


def _product_state(item: dict[str, Any]) -> str:
    return str(item.get("recommendation_status") or item.get("status") or "unknown")


def evaluate_product_fit(raw_snapshot: dict[str, Any] | None, item: dict[str, Any], domain: str | None = None) -> dict[str, Any]:
    snapshot = normalize_finance_snapshot(raw_snapshot)
    if not isinstance(item, dict):
        raise FinanceSnapshotError("item must be an object")
    failed: list[str] = []
    unknown: list[str] = []
    if item.get("status") not in (None, "active") or item.get("product_status") not in (None, "active"):
        failed.append("product_not_active")
    if item.get("source_listing_status") not in (None, "listed"):
        failed.append("source_not_listed")
    if item.get("freshness_status") == "stale" or item.get("source_freshness_status") == "stale":
        failed.append("stale_source")
    if item.get("verification_status") not in (None, "verified"):
        failed.append("source_not_verified")
    if item.get("verification_status") is None:
        unknown.append("verification_status")
    if item.get("recommendation_status") in {"manual_review_candidate", "retired"}:
        failed.append("recommendation_state_not_eligible")
    constraints = snapshot.get("constraints") or {}
    provider = constraints.get("provider")
    if provider and item.get("provider") and str(provider) != str(item.get("provider")):
        failed.append("provider_constraint_failed")
    term_months = item.get("term_months")
    requirement = snapshot.get("liquidity_requirement")
    required_months = requirement.get("months") if isinstance(requirement, dict) else None
    if term_months is not None and required_months is not None and float(term_months) > float(required_months):
        failed.append("term_exceeds_liquidity_horizon")
    elif required_months is not None and term_months is None:
        unknown.append("term_months")
    risk_capacity = snapshot.get("risk_capacity")
    item_risk = item.get("risk_level")
    if risk_capacity != "unknown" and item_risk is not None:
        risk_order = {"low": 1, "medium": 2, "high": 3}
        if risk_order.get(str(item_risk), 99) > risk_order.get(str(risk_capacity), 0):
            failed.append("risk_capacity_exceeded")
    elif risk_capacity != "unknown" and item_risk is None:
        unknown.append("product_risk_level")
    score_components = {
        "source_verification": 30.0 if item.get("verification_status") == "verified" else 0.0,
        "current_listing": 20.0 if item.get("source_listing_status") == "listed" else 0.0,
        "liquidity_fit": 25.0 if "term_exceeds_liquidity_horizon" not in failed and "term_months" not in unknown else 0.0,
        "risk_fit": 25.0 if "risk_capacity_exceeded" not in failed and "product_risk_level" not in unknown else 0.0,
    }
    eligible = not failed and not unknown
    return {
        "mode": "decision_support",
        "status": "ready" if eligible else "insufficient_information",
        "reason_codes": [] if eligible else sorted(set(failed + unknown)),
        "profile_as_of": snapshot.get("as_of"),
        "item_id": item.get("id"),
        "domain": domain,
        "eligible": eligible,
        "decision": "fit" if eligible else "not_fit" if failed else "insufficient_information",
        "failed_conditions": sorted(set(failed)),
        "unknown_conditions": sorted(set(unknown)),
        "score": round(sum(score_components.values()), 6) if eligible else None,
        "score_components": score_components,
        "recommendation_state": _product_state(item),
        "sources": item.get("source_urls") or item.get("sources") or [],
        "as_of": item.get("last_verified_at") or item.get("source_basis_dates") or None,
        "data_as_of": item.get("last_verified_at") or item.get("source_basis_dates") or None,
        "assumptions": ["only explicit product fields and user constraints are evaluated"],
        "missing_information": sorted(set(unknown)),
        "financial_needs": [],
        "candidates": [{"item_id": item.get("id"), "eligible": True}] if eligible else [],
        "decision_owner": "user",
        "limitations": ["fit evaluation is not a recommendation", "user remains the decision owner"],
        "audit_id": finance_audit_id("fit", snapshot, item),
        "policy_version": ADVICE_POLICY_VERSION,
    }


def simulate_finance_scenario(raw_snapshot: dict[str, Any] | None, scenario: dict[str, Any] | None) -> dict[str, Any]:
    snapshot = normalize_finance_snapshot(raw_snapshot)
    scenario = scenario if isinstance(scenario, dict) else {}
    months = int(_number(scenario.get("months", 12), "scenario.months"))
    if months < 1 or months > 120:
        raise FinanceSnapshotError("scenario.months must be between 1 and 120")
    additional_payment = _number(scenario.get("additional_monthly_payment_krw", 0), "scenario.additional_monthly_payment_krw")
    contribution = _number(scenario.get("monthly_contribution_krw", 0), "scenario.monthly_contribution_krw")
    balance_before = _debt_balance(snapshot)
    interest_before = sum(balance_before * float(item.get("annual_rate_percent") or 0) / 100 / 12 for item in snapshot.get("liabilities") or [])
    debt_after = max(0.0, balance_before - additional_payment * months)
    weighted_rate = calculate_weighted_debt_rate(snapshot)["value"] or 0.0
    interest_after = max(0.0, debt_after * float(weighted_rate) / 100 / 12) if debt_after else 0.0
    liquid_before = float(snapshot.get("liquid_assets_krw") or 0)
    liquid_after = liquid_before + contribution * months
    return {
        "mode": "decision_support",
        "status": "ready",
        "reason_codes": [],
        "profile_as_of": snapshot.get("as_of"),
        "data_as_of": snapshot.get("as_of"),
        "missing_information": [],
        "financial_needs": [],
        "candidates": [],
        "decision_owner": "user",
        "scenario": {"months": months, "additional_monthly_payment_krw": additional_payment, "monthly_contribution_krw": contribution},
        "before": {"debt_balance_krw": round(balance_before, 6), "monthly_debt_interest_estimate_krw": round(interest_before, 6), "liquid_assets_krw": round(liquid_before, 6)},
        "after": {"debt_balance_krw": round(debt_after, 6), "monthly_debt_interest_estimate_krw": round(interest_after, 6), "liquid_assets_krw": round(liquid_after, 6)},
        "assumptions": ["simple monthly balance estimate", "no taxes, fees, compounding, new borrowing, or product-specific terms are inferred"],
        "limitations": ["scenario is educational and not a promise of future return or approval"],
        "audit_id": finance_audit_id("scenario", snapshot, scenario),
        "as_of": snapshot.get("as_of"),
        "policy_version": POLICY_VERSION,
    }


def explain_recommendation(candidate: dict[str, Any], raw_snapshot: dict[str, Any] | None = None) -> dict[str, Any]:
    if not isinstance(candidate, dict):
        raise FinanceSnapshotError("candidate must be an object")
    snapshot = normalize_finance_snapshot(raw_snapshot)
    eligible = candidate.get("eligible") is True
    return {
        "mode": "decision_support",
        "status": "ready" if eligible else "blocked",
        "candidate_id": candidate.get("item_id") or candidate.get("id"),
        "why_included": candidate.get("matched_conditions") or candidate.get("score_components") or [],
        "why_excluded": candidate.get("failed_conditions") or candidate.get("unknown_conditions") or [],
        "tradeoffs": candidate.get("tradeoffs") or ["source status, eligibility conditions, liquidity, and risk must be checked before the user decides"],
        "assumptions": candidate.get("assumptions") or [],
        "missing_information": candidate.get("unknown_conditions") or [],
        "sources": candidate.get("sources") or [],
        "data_as_of": candidate.get("as_of") or snapshot.get("as_of"),
        "decision_owner": "user",
        "limitations": ["explanation does not constitute financial advice or product approval"],
        "audit_id": finance_audit_id(candidate, snapshot),
    }


def validate_finance_advice(advice: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    required = ("mode", "status", "reason_codes", "profile_as_of", "data_as_of", "assumptions", "missing_information", "financial_needs", "candidates", "decision_owner", "limitations", "audit_id")
    for field in required:
        if field not in advice:
            errors.append(f"missing_{field}")
    if advice.get("decision_owner") != "user":
        errors.append("decision_owner_must_be_user")
    if advice.get("status") == "ready" and not advice.get("candidates"):
        errors.append("ready_requires_candidates")
    if advice.get("status") != "ready" and advice.get("candidates"):
        errors.append("blocked_or_insufficient_must_not_include_candidates")
    if advice.get("mode") == "recommendation" and advice.get("status") == "ready":
        for candidate in advice.get("candidates") or []:
            if candidate.get("recommendation_status") != "verified_recommendation_candidate":
                errors.append("recommendation_candidate_not_verified")
    return {"valid": not errors, "errors": errors, "policy_version": ADVICE_POLICY_VERSION}


def finance_audit_id(*values: object) -> str:
    payload = json.dumps(values, ensure_ascii=False, sort_keys=True, separators=(",", ":"), default=str)
    return "fin-" + hashlib.sha256(payload.encode("utf-8")).hexdigest()[:20]


def blocked_recommendation_case(domain: str, *, profile_as_of: str | None = None, data_as_of: str | None = None, missing_information: list[str] | None = None, financial_needs: list[dict[str, Any]] | None = None, reason_codes: list[str] | None = None, limitations: list[str] | None = None) -> dict[str, Any]:
    payload = {
        "mode": "decision_support",
        "status": "blocked",
        "reason_codes": reason_codes or ["PUBLIC_RECOMMENDATION_DISABLED", "NO_VERIFIED_RECOMMENDATION_CANDIDATE"],
        "profile_as_of": profile_as_of,
        "data_as_of": data_as_of,
        "assumptions": ["public recommendation feature flag is disabled", "only verified recommendation candidates could qualify"],
        "missing_information": missing_information or [],
        "financial_needs": financial_needs or [],
        "candidates": [],
        "decision_owner": "user",
        "limitations": limitations or ["use lookup, education, comparison, and scenario tools only until the owner pilot is enabled"],
        "audit_id": finance_audit_id("blocked-recommendation", domain, profile_as_of, data_as_of),
        "domain": domain,
        "domain_enabled": False,
        "result_count": 0,
        "recommendation_model_version": "openfin-recommendation-v0.1.0",
        "warnings": ["No verified public recommendation candidates are available for this domain."],
    }
    return payload
