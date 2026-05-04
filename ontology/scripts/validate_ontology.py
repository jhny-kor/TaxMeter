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
    "scenario",
    "life-expense",
    "life-income",
    "life-event",
    "eligibility-rule",
    "required-document",
    "application-channel",
    "conflict-rule",
    "concept",
    "term",
    "deadline",
}
LIFE_MAPPING_TYPES = {"life-expense", "life-income", "life-event"}
LIFE_SUPPORT_TYPES = {"eligibility-rule", "required-document", "application-channel", "conflict-rule"}
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
CRITERIA_KINDS = {
    "threshold",
    "rate",
    "limit",
    "deduction",
    "formula",
    "eligibility",
    "deadline",
    "period",
    "person",
    "reference",
}
CRITERIA_REQUIRED_EXPLANATION_KEYS = (
    "criteria_kind",
    "basis_category",
    "basis_definition",
    "basis_lookup",
    "selection_rule",
    "basis_source",
)
DEADLINE_RECURRENCE_FREQUENCIES = {
    "annual",
    "semiannual",
    "quarterly",
    "monthly",
    "event-based",
    "one-time",
}
LOCAL_GOV_SUPPORT_REQUIRED_FIELDS = (
    "jurisdiction",
    "gov24_service_id",
    "gov24_service_seq",
    "source_record_id",
    "source_modified_at",
    "source_collected_at",
    "status_check_url",
)
LOCAL_SUPPORT_EXPORT_PATH = ROOT / "exports" / "korea-local-government-supports-2026.json"


def parse_frontmatter(path: Path) -> dict | None:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        raise ValueError(f"{path}: missing frontmatter")
    parts = text.split("\n---\n", 1)
    if len(parts) != 2:
        raise ValueError(f"{path}: missing closing frontmatter")
    frontmatter = parts[0][4:]
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
            for key in CRITERIA_REQUIRED_EXPLANATION_KEYS:
                require(bool(criterion.get(key)), f"{item_id}: criteria #{index} missing {key}", errors)
            criteria_kind = criterion.get("criteria_kind")
            if criteria_kind:
                require(criteria_kind in CRITERIA_KINDS, f"{item_id}: criteria #{index} invalid criteria_kind {criteria_kind}", errors)
            basis_source = criterion.get("basis_source")
            if basis_source:
                require(basis_source in items, f"{item_id}: criteria #{index} references missing basis_source {basis_source}", errors)


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


def validate_freshness_metadata(items: dict[str, dict], errors: list[str]) -> None:
    valid_abolition = {"active", "abolished", "sunset", "unknown"}
    valid_revision = {"none_announced", "planned", "temporary", "check_source"}
    for item_id, item in items.items():
        item_type = item.get("type")
        if item_type != "source":
            require(bool(item.get("reviewed_at")), f"{item_id}: missing reviewed_at", errors)
            require(item.get("abolition_status") in valid_abolition, f"{item_id}: invalid abolition_status", errors)
            require(item.get("revision_status") in valid_revision, f"{item_id}: invalid revision_status", errors)
        if item_type in REQUIRED_TYPES_WITH_SOURCES:
            require(bool(item.get("source_urls")), f"{item_id}: missing source_urls", errors)
            require(bool(item.get("source_basis_dates")), f"{item_id}: missing source_basis_dates", errors)
        if item_type == "source":
            require(bool(item.get("source_urls")), f"{item_id}: source missing source_urls", errors)
            require(bool(item.get("source_basis_dates")), f"{item_id}: source missing source_basis_dates", errors)


def validate_deadline_recurrence(items: dict[str, dict], errors: list[str]) -> None:
    for item_id, item in items.items():
        if item.get("type") != "deadline":
            continue
        recurrence = item.get("recurrence")
        require(isinstance(recurrence, dict), f"{item_id}: deadline missing recurrence object", errors)
        if not isinstance(recurrence, dict):
            continue
        frequency = recurrence.get("frequency")
        require(frequency in DEADLINE_RECURRENCE_FREQUENCIES, f"{item_id}: invalid recurrence frequency {frequency}", errors)
        require(bool(recurrence.get("anchor")), f"{item_id}: recurrence missing anchor", errors)
        require(bool(recurrence.get("due_rule")), f"{item_id}: recurrence missing due_rule", errors)


def validate_scenario_paths(items: dict[str, dict], errors: list[str]) -> None:
    scenarios = [item for item in items.values() if item.get("type") == "scenario"]
    require(bool(scenarios), "missing scenario nodes", errors)
    for item in scenarios:
        item_id = item["id"]
        steps = item.get("path_steps") or []
        require(isinstance(steps, list) and bool(steps), f"{item_id}: scenario missing path_steps", errors)
        if not isinstance(steps, list):
            continue
        expected_orders = list(range(1, len(steps) + 1))
        actual_orders = [step.get("order") for step in steps if isinstance(step, dict)]
        require(actual_orders == expected_orders, f"{item_id}: path_steps order must be sequential from 1", errors)
        for index, step in enumerate(steps, start=1):
            if not isinstance(step, dict):
                errors.append(f"{item_id}: path step #{index} must be an object")
                continue
            target_id = step.get("target")
            require(bool(step.get("label")), f"{item_id}: path step #{index} missing label", errors)
            require(bool(step.get("reason")), f"{item_id}: path step #{index} missing reason", errors)
            require(bool(target_id), f"{item_id}: path step #{index} missing target", errors)
            if target_id:
                require(target_id in items, f"{item_id}: path step #{index} references missing target {target_id}", errors)


def validate_life_language_mapping(items: dict[str, dict], errors: list[str]) -> None:
    life_nodes = [item for item in items.values() if item.get("type") in LIFE_MAPPING_TYPES]
    require(bool(life_nodes), "missing life-language mapping nodes", errors)
    for item in life_nodes:
        item_id = item["id"]
        phrases = item.get("life_phrases") or []
        candidates = item.get("official_candidates") or []
        questions = item.get("eligibility_questions") or []
        require(isinstance(phrases, list) and bool(phrases), f"{item_id}: missing life_phrases", errors)
        require(isinstance(candidates, list) and bool(candidates), f"{item_id}: missing official_candidates", errors)
        require(isinstance(questions, list) and bool(questions), f"{item_id}: missing eligibility_questions", errors)
        for index, candidate in enumerate(candidates, start=1):
            if not isinstance(candidate, dict):
                errors.append(f"{item_id}: official candidate #{index} must be an object")
                continue
            target_id = candidate.get("target")
            confidence = candidate.get("confidence")
            require(bool(target_id), f"{item_id}: official candidate #{index} missing target", errors)
            if target_id:
                require(target_id in items, f"{item_id}: official candidate #{index} references missing target {target_id}", errors)
            require(isinstance(confidence, (int, float)) and 0 <= confidence <= 1, f"{item_id}: official candidate #{index} invalid confidence", errors)
            require(bool(candidate.get("reason")), f"{item_id}: official candidate #{index} missing reason", errors)
            require(bool(candidate.get("required_checks")), f"{item_id}: official candidate #{index} missing required_checks", errors)
        expected_orders = list(range(1, len(questions) + 1))
        actual_orders = [question.get("order") for question in questions if isinstance(question, dict)]
        require(actual_orders == expected_orders, f"{item_id}: eligibility_questions order must be sequential from 1", errors)
        for index, question in enumerate(questions, start=1):
            if not isinstance(question, dict):
                errors.append(f"{item_id}: eligibility question #{index} must be an object")
                continue
            require(bool(question.get("question")), f"{item_id}: eligibility question #{index} missing question", errors)
            target_id = question.get("target")
            if target_id:
                require(target_id in items, f"{item_id}: eligibility question #{index} references missing target {target_id}", errors)

    for item_id, item in items.items():
        if item.get("type") in LIFE_SUPPORT_TYPES:
            require(bool(item.get("related")), f"{item_id}: support node should relate to an official item or life node", errors)


def validate_local_government_supports(items: dict[str, dict], errors: list[str]) -> None:
    local_supports = [
        item for item in items.values()
        if item.get("type") == "support-program" and "local-government-support" in (item.get("tags") or [])
    ]
    for item in local_supports:
        item_id = item["id"]
        require("category.local-government-supports" in (item.get("parents") or []), f"{item_id}: missing local-government support category parent", errors)
        require("source.gov24.benefit-plus.local-supports" in (item.get("sources") or []), f"{item_id}: missing Gov24 Benefit Plus source", errors)
        for field in LOCAL_GOV_SUPPORT_REQUIRED_FIELDS:
            require(bool(item.get(field)), f"{item_id}: missing {field}", errors)
        status_url = item.get("status_check_url") or ""
        require(status_url.startswith("https://plus.gov.kr/portal/benefitV2/benefitTotalSrvcList/benefitSrvcDtl"), f"{item_id}: invalid status_check_url", errors)
        source_urls = item.get("source_urls") or []
        require(status_url in source_urls, f"{item_id}: status_check_url must be included in source_urls", errors)
        require(item.get("revision_status") in {"check_source", "temporary"}, f"{item_id}: local support should require future source checking", errors)


def validate_local_government_support_split(items: dict[str, dict], errors: list[str]) -> None:
    main_local_supports = [
        item_id for item_id, item in items.items()
        if item.get("type") == "support-program" and "local-government-support" in (item.get("tags") or [])
    ]
    require(not main_local_supports, f"main ontology should not include local-government support nodes: {len(main_local_supports)} found", errors)
    require(LOCAL_SUPPORT_EXPORT_PATH.exists(), f"missing local support split export {LOCAL_SUPPORT_EXPORT_PATH}", errors)
    if not LOCAL_SUPPORT_EXPORT_PATH.exists():
        return

    payload = json.loads(LOCAL_SUPPORT_EXPORT_PATH.read_text(encoding="utf-8"))
    local_items = payload.get("items") or []
    reference_items = payload.get("reference_items") or []
    require(isinstance(local_items, list) and bool(local_items), "local support export has no items", errors)
    require(payload.get("item_count") == len(local_items), "local support export item_count mismatch", errors)
    local_by_id = {item["id"]: item for item in local_items if isinstance(item, dict) and item.get("id")}
    reference_by_id = {item["id"]: item for item in reference_items if isinstance(item, dict) and item.get("id")}
    require(len(local_by_id) == len(local_items), "local support export has duplicate or invalid item ids", errors)
    merged = {**items, **reference_by_id, **local_by_id}
    validate_references(merged, errors)
    validate_local_government_supports(merged, errors)


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
    validate_freshness_metadata(items, errors)
    validate_deadline_recurrence(items, errors)
    validate_scenario_paths(items, errors)
    validate_life_language_mapping(items, errors)
    validate_local_government_support_split(items, errors)
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
