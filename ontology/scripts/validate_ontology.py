#!/usr/bin/env python3
"""Validate the standalone Obsidian OpenTax vault."""

from __future__ import annotations

import json
import sys
from pathlib import Path

try:
    from .generate_vault import (
        CORPORATE_SUPPORT_IDS,
        LOCAL_TAX_IDS,
        NATIONAL_TAX_IDS,
        ROOT,
        VAULT,
    )
except ImportError:
    from generate_vault import (
        CORPORATE_SUPPORT_IDS,
        LOCAL_TAX_IDS,
        NATIONAL_TAX_IDS,
        ROOT,
        VAULT,
    )


REFERENCE_KEYS = ("parents", "children", "related", "terms", "deadlines", "sources")
REQUIRED_TYPES_WITH_SOURCES = {
    "category",
    "tax",
    "deduction",
    "tax-credit",
    "tax-reduction",
    "corporate-tax-support",
    "support-program",
    "filing",
    "concept",
    "term",
    "deadline",
}
CRITERIA_RANGE_PAIRS = (
    ("threshold_krw_min", "threshold_krw_max", "threshold"),
    ("rate_percent_min", "rate_percent_max", "rate percent"),
    ("age_min", "age_max", "age"),
    ("period_years_min", "period_years_max", "period years"),
    ("period_months_min", "period_months_max", "period months"),
    ("years_of_service_min", "years_of_service_max", "years of service"),
    ("deadline_months_after_month_end_min", "deadline_months_after_month_end_max", "deadline months after month end"),
)
ACTIONABLE_TYPES = {
    "tax",
    "deduction",
    "tax-credit",
    "tax-reduction",
    "corporate-tax-support",
    "filing",
}
CRITERIA_DETAIL_KEYS = {
    "threshold_krw",
    "threshold_krw_min",
    "threshold_krw_max",
    "amount_krw",
    "max_amount_krw",
    "deduction_krw",
    "base_deduction_krw",
    "per_year_deduction_krw",
    "limit_krw",
    "progressive_deduction_krw",
    "rate_percent",
    "rate_percent_min",
    "rate_percent_max",
    "rate_basis",
    "amount_formula",
    "amount_applicability",
    "unlimited_amount",
    "benefit",
    "age_min",
    "age_max",
    "household_size",
    "median_income_percent_max",
    "period_years",
    "period_years_min",
    "period_years_max",
    "period_months_min",
    "period_months_max",
    "years_of_service_min",
    "years_of_service_max",
    "deadline_month",
    "deadline_day",
    "deadline_start_month",
    "deadline_start_day",
    "deadline_end_month",
    "deadline_end_day",
    "deadline_days_after_event",
    "deadline_months_after_month_end",
    "deadline_months_after_month_end_min",
    "deadline_months_after_month_end_max",
    "deadline_relative",
    "deadline_rule",
}


def parse_frontmatter(path: Path) -> dict | None:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        raise ValueError(f"{path}: missing frontmatter")
    _, frontmatter, _ = text.split("---", 2)
    result: dict = {}
    for raw_line in frontmatter.strip().splitlines():
        if ": " not in raw_line:
            continue
        key, value = raw_line.split(": ", 1)
        try:
            result[key] = json.loads(value)
        except json.JSONDecodeError:
            result[key] = value
    if "id" not in result:
        return None
    result["_path"] = str(path.relative_to(ROOT))
    return result


def load_notes() -> dict[str, dict]:
    items: dict[str, dict] = {}
    for path in sorted(VAULT.rglob("*.md")):
        item = parse_frontmatter(path)
        if item is None:
            continue
        item_id = item["id"]
        if item_id in items:
            raise ValueError(f"duplicate id {item_id}: {items[item_id]['_path']} and {item['_path']}")
        items[item_id] = item
    return items


def require(condition: bool, message: str, errors: list[str]) -> None:
    if not condition:
        errors.append(message)


def validate_references(items: dict[str, dict], errors: list[str]) -> None:
    for item_id, item in items.items():
        for key in REFERENCE_KEYS:
            for target_id in item.get(key) or []:
                require(target_id in items, f"{item_id}: {key} references missing id {target_id}", errors)


def validate_criteria(items: dict[str, dict], errors: list[str]) -> None:
    for item_id, item in items.items():
        criteria = item.get("criteria") or []
        require(isinstance(criteria, list), f"{item_id}: criteria must be a list", errors)
        if not isinstance(criteria, list):
            continue
        for index, criterion in enumerate(criteria, start=1):
            if not isinstance(criterion, dict):
                errors.append(f"{item_id}: criteria #{index} must be an object")
                continue
            require(bool(criterion.get("label")), f"{item_id}: criteria #{index} missing label", errors)
            require(bool(criterion.get("basis")), f"{item_id}: criteria #{index} missing basis", errors)
            source_id = criterion.get("source")
            require(bool(source_id), f"{item_id}: criteria #{index} missing source", errors)
            if source_id:
                require(source_id in items, f"{item_id}: criteria #{index} references missing source {source_id}", errors)
            for minimum_key, maximum_key, label in CRITERIA_RANGE_PAIRS:
                minimum = criterion.get(minimum_key)
                maximum = criterion.get(maximum_key)
                if minimum is not None and maximum is not None:
                    require(minimum <= maximum, f"{item_id}: criteria #{index} {label} min exceeds max", errors)
            has_detail = any(key in criterion for key in CRITERIA_DETAIL_KEYS)
            require(has_detail, f"{item_id}: criteria #{index} has no structured amount/rate/period/detail field", errors)


def validate_required_metadata(items: dict[str, dict], errors: list[str]) -> None:
    for item_id, item in items.items():
        require(bool(item.get("title")), f"{item_id}: missing title", errors)
        require(bool(item.get("type")), f"{item_id}: missing type", errors)
        require(bool(item.get("description")), f"{item_id}: missing description", errors)
        if item.get("type") in REQUIRED_TYPES_WITH_SOURCES:
            require(bool(item.get("sources")), f"{item_id}: missing official/legal source", errors)
        if item.get("type") == "source":
            require(bool(item.get("url")), f"{item_id}: missing source url", errors)
            require(bool(item.get("publisher")), f"{item_id}: missing source publisher", errors)
        if item.get("type") not in {"source", "deadline"}:
            require(item.get("basis_year") is not None, f"{item_id}: missing basis_year", errors)
        if item.get("type") in ACTIONABLE_TYPES:
            require(bool(item.get("law_reference")), f"{item_id}: missing law_reference", errors)


def validate_bidirectional_links(items: dict[str, dict], errors: list[str]) -> None:
    for item_id, item in items.items():
        for child_id in item.get("children") or []:
            child = items.get(child_id)
            if child:
                require(item_id in (child.get("parents") or []), f"{item_id}: child {child_id} does not point back", errors)
        for parent_id in item.get("parents") or []:
            parent = items.get(parent_id)
            if parent:
                require(item_id in (parent.get("children") or []), f"{item_id}: parent {parent_id} does not point forward", errors)


def validate_manifests(items: dict[str, dict], errors: list[str]) -> None:
    for item_id in NATIONAL_TAX_IDS:
        require(item_id in items, f"missing national tax item {item_id}", errors)
        require("source.national-tax-framework-act.2026.article2" in (items.get(item_id, {}).get("sources") or []), f"{item_id}: missing national tax legal source", errors)
    for item_id in LOCAL_TAX_IDS:
        require(item_id in items, f"missing local tax item {item_id}", errors)
        require("source.local-tax-framework-act.2026.article8" in (items.get(item_id, {}).get("sources") or []), f"{item_id}: missing local tax legal source", errors)
    for item_id in CORPORATE_SUPPORT_IDS:
        require(item_id in items, f"missing corporate tax support item {item_id}", errors)
        require("source.nts.corporate-tax.reliefs" in (items.get(item_id, {}).get("sources") or []), f"{item_id}: missing NTS corporate relief source", errors)
    require(items.get("category.national-taxes", {}).get("children") == NATIONAL_TAX_IDS, "national tax manifest children are not exact", errors)
    require(set(items.get("category.local-taxes", {}).get("children") or []) >= {"category.local-ordinary-taxes", "category.local-purpose-taxes"}, "local tax category is missing child groups", errors)
    require(items.get("category.corporate-tax-supports", {}).get("children") == CORPORATE_SUPPORT_IDS, "corporate support manifest children are not exact", errors)


def main() -> int:
    items = load_notes()
    errors: list[str] = []
    validate_references(items, errors)
    validate_criteria(items, errors)
    validate_required_metadata(items, errors)
    validate_bidirectional_links(items, errors)
    validate_manifests(items, errors)

    if errors:
        print("Ontology validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    print(f"Ontology validation passed: {len(items)} notes")
    print(f"- national tax items: {len(NATIONAL_TAX_IDS)}")
    print(f"- local tax items: {len(LOCAL_TAX_IDS)}")
    print(f"- corporate tax support items: {len(CORPORATE_SUPPORT_IDS)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
