#!/usr/bin/env python3
from __future__ import annotations

import re
from collections import defaultdict
from copy import deepcopy
from typing import Any
from urllib.parse import parse_qs, urlparse


PRODUCT_TYPES = {"card-product", "bank-product", "insurance-product"}
IDENTIFIER_QUERY_KEYS = ("product_code", "productCode", "gdsno", "prodNo", "productId")
RECORD_METADATA_FIELDS = {
    "id",
    "canonical_product_id",
    "source_records",
    "preferred_source",
    "merged_fields",
    "field_provenance",
    "field_conflicts",
}
DERIVED_FIELDS = {
    "export_id",
    "search_text",
    "search_aliases",
    "aliases",
    "search_facets",
    "structured_summary",
    "source_checksum",
    "quality_flags",
    "completeness_ratio",
    "source_completeness_ratio",
    "normalized_completeness_ratio",
    "verified_completeness_ratio",
    "required_field_count",
    "completed_field_count",
}


def slug(value: Any) -> str:
    return re.sub(r"[^0-9a-z가-힣]+", "-", str(value or "").casefold()).strip("-")


def official_url_identifier(item: dict[str, Any]) -> str:
    for raw_url in item.get("source_urls") or []:
        parsed = urlparse(str(raw_url))
        query = parse_qs(parsed.query)
        for key in IDENTIFIER_QUERY_KEYS:
            values = query.get(key)
            if values and slug(values[0]):
                return slug(values[0])
        path_parts = [slug(part) for part in parsed.path.split("/") if slug(part)]
        if path_parts and any(character.isdigit() for character in path_parts[-1]):
            return path_parts[-1]
    return ""


def canonical_product_id(item: dict[str, Any]) -> str:
    provider = slug(item.get("provider_code") or item.get("provider"))
    product = slug(item.get("product_code"))
    registry = slug(item.get("source_record_id"))
    url_identifier = official_url_identifier(item)
    title = slug(item.get("title")).replace("-", "")
    category = slug(item.get("product_kind") or item.get("search_type"))
    product_identity = ".".join(part for part in (product, category) if part)
    identity = product_identity or url_identifier or ".".join(part for part in (registry, title) if part) or title or slug(item.get("id"))
    return ".".join(part for part in ("finance", "canonical", provider or "unknown", identity or "unknown") if part)


def is_meaningful(value: Any) -> bool:
    return value not in (None, "", [], {})


def source_record(item: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": item.get("id"),
        "source_record_id": item.get("source_record_id"),
        "provider_code": item.get("provider_code"),
        "product_code": item.get("product_code"),
        "source_urls": list(item.get("source_urls") or []),
        "source_basis_dates": list(item.get("source_basis_dates") or []),
        "collected_at": item.get("collected_at"),
        "source_checksum": item.get("source_checksum"),
    }


def source_id(item: dict[str, Any]) -> str:
    return str(item.get("id") or item.get("source_record_id") or "unknown")


def record_priority(item: dict[str, Any]) -> tuple[int, int, str]:
    verified = int(item.get("verification_status") == "verified")
    populated = sum(is_meaningful(value) for key, value in item.items() if key not in RECORD_METADATA_FIELDS)
    return verified, populated, str(item.get("id") or "")


def combined_list(values: list[list[Any]]) -> list[Any]:
    merged: list[Any] = []
    for value_list in values:
        for value in value_list:
            if value not in merged:
                merged.append(value)
    return merged


def canonicalize_product_records(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    for item in items:
        if item.get("type") not in PRODUCT_TYPES:
            continue
        item["canonical_product_id"] = canonical_product_id(item)
        item["source_records"] = [source_record(item)]
        item["preferred_source"] = source_id(item)
        item["merged_fields"] = {}
        item["field_provenance"] = {
            key: [source_id(item)]
            for key, value in item.items()
            if key not in RECORD_METADATA_FIELDS and is_meaningful(value)
        }
        item["field_conflicts"] = {}
    return items


def merge_product_records(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    passthrough: list[dict[str, Any]] = []
    for item in items:
        if item.get("type") not in PRODUCT_TYPES:
            passthrough.append(deepcopy(item))
            continue
        record = deepcopy(item)
        record["canonical_product_id"] = str(record.get("canonical_product_id") or canonical_product_id(record))
        grouped[record["canonical_product_id"]].append(record)

    merged: list[dict[str, Any]] = []
    for canonical_id, records in sorted(grouped.items()):
        ordered = sorted(records, key=record_priority, reverse=True)
        preferred = deepcopy(ordered[0])
        preferred["canonical_product_id"] = canonical_id
        preferred["source_records"] = [source_record(record) for record in ordered]
        preferred["preferred_source"] = source_id(ordered[0])
        preferred["merged_fields"] = {}
        preferred["field_provenance"] = {}
        preferred["field_conflicts"] = {}
        fields = {
            key
            for record in ordered
            for key, value in record.items()
            if key not in RECORD_METADATA_FIELDS | DERIVED_FIELDS and is_meaningful(value)
        }
        for field in sorted(fields):
            preferred_has_value = is_meaningful(preferred.get(field))
            values = [(source_id(record), record[field]) for record in ordered if is_meaningful(record.get(field))]
            if not values:
                continue
            preferred["field_provenance"][field] = [record_id for record_id, _ in values]
            field_values = [value for _, value in values]
            if all(isinstance(value, list) for value in field_values):
                combined = combined_list(field_values)
                preferred[field] = combined
                if len(field_values) > 1 or not preferred_has_value:
                    preferred["merged_fields"][field] = combined
                continue
            if len({repr(value) for value in field_values}) > 1:
                preferred["field_conflicts"][field] = [
                    {"source_record_id": record_id, "value": value}
                    for record_id, value in values
                ]
            preferred[field] = field_values[0]
            if len(field_values) > 1 or not preferred_has_value:
                preferred["merged_fields"][field] = field_values[0]
        if preferred["field_conflicts"]:
            public_reasons = set(str(value) for value in preferred.get("public_recommendation_exclusion_reasons") or [])
            comparison_reasons = set(str(value) for value in preferred.get("comparison_exclusion_reasons") or [])
            public_reasons.add("canonical_field_conflict")
            comparison_reasons.add("canonical_field_conflict")
            preferred["public_recommendation_exclusion_reasons"] = sorted(public_reasons)
            preferred["comparison_exclusion_reasons"] = sorted(comparison_reasons)
        merged.append(preferred)
    return [*passthrough, *merged]
