#!/usr/bin/env python3
from __future__ import annotations

import re
from collections import defaultdict
from copy import deepcopy
from typing import Any
from urllib.parse import parse_qs, urlparse


PRODUCT_TYPES = {"card-product", "bank-product", "insurance-product"}
IDENTIFIER_QUERY_KEYS = (
    "product_code", "productCode", "productCodeNo", "fin_prdt_cd", "finPrdtCd",
    "gdsno", "mbkNo", "prodNo", "productId", "code", "product_id", "productId",
)
IDENTIFIER_NAMESPACES = {
    "product_code": "official_product_code",
    "productCode": "official_product_code",
    "productCodeNo": "official_product_code",
    "fin_prdt_cd": "finlife_product_code",
    "finPrdtCd": "finlife_product_code",
    "gdsno": "bc_card_gdsno",
    "prodNo": "official_product_id",
    "productId": "official_product_id",
    "product_id": "official_product_id",
    "code": "disclosure_product_code",
}
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


def _external_id(namespace: str, value: Any) -> dict[str, str] | None:
    compact = str(value or "").strip()
    if not compact:
        return None
    return {"namespace": namespace, "value": compact}


def external_product_ids(item: dict[str, Any]) -> list[dict[str, str]]:
    identifiers: list[dict[str, str]] = []

    def add(namespace: str, value: Any) -> None:
        if value in (None, "", [], {}):
            return
        if namespace in {"official_product_code", "finlife_product_code"} and item.get("type") == "bank-product":
            value = f"{slug(item.get('provider_code') or item.get('provider'))}:{slug(item.get('product_kind') or item.get('search_type'))}:{value}"
        entry = _external_id(namespace, value)
        if entry and entry not in identifiers:
            identifiers.append(entry)

    for identifier in item.get("external_product_ids") or []:
        if isinstance(identifier, dict):
            add(str(identifier.get("namespace") or ""), identifier.get("value"))

    for key, namespace in IDENTIFIER_NAMESPACES.items():
        add(namespace, item.get(key))
    add("official_source_record_id", item.get("source_record_id"))
    add("insurance_product_code", item.get("insurance_product_code"))
    add("public_data_product_id", item.get("public_data_product_id"))
    for record in item.get("source_records") or []:
        if not isinstance(record, dict):
            continue
        for key, namespace in IDENTIFIER_NAMESPACES.items():
            add(namespace, record.get(key))
        add("official_source_record_id", record.get("source_record_id"))
    for raw_url in item.get("source_urls") or []:
        parsed = urlparse(str(raw_url))
        query = parse_qs(parsed.query)
        for key, namespace in IDENTIFIER_NAMESPACES.items():
            for value in query.get(key) or []:
                add(namespace, value)
    return identifiers


def provider_external_ids(item: dict[str, Any]) -> list[dict[str, str]]:
    identifiers: list[dict[str, str]] = []

    def add(namespace: str, value: Any) -> None:
        entry = _external_id(namespace, value)
        if entry and entry not in identifiers:
            identifiers.append(entry)

    add("financial_company_code", item.get("provider_code"))
    for raw_url in item.get("source_urls") or []:
        query = parse_qs(urlparse(str(raw_url)).query)
        for value in query.get("mbkNo") or []:
            add("bc_card_issuer_code", value)
    return identifiers


def canonical_product_id(item: dict[str, Any]) -> str:
    provider = slug(item.get("provider_code") or item.get("provider"))
    product = slug(item.get("product_code") or item.get("fin_prdt_cd"))
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
        "roles": list(item.get("source_roles") or []),
    }


def source_id(item: dict[str, Any]) -> str:
    return str(item.get("id") or item.get("source_record_id") or "unknown")


def external_merge_key(item: dict[str, Any]) -> str | None:
    product_type = str(item.get("type") or "")
    provider = slug(item.get("provider_code") or item.get("provider"))
    for identifier in item.get("external_product_ids") or []:
        if not isinstance(identifier, dict):
            continue
        namespace = str(identifier.get("namespace") or "")
        value = slug(identifier.get("value"))
        if not value:
            continue
        if product_type == "card-product" and namespace in {"bc_card_gdsno", "disclosure_product_code"}:
            return f"product:{namespace}:{value}"
        if product_type == "bank-product" and namespace in {"finlife_product_code", "official_product_code"}:
            return f"product:{product_type}:{slug(item.get('product_kind') or item.get('search_type'))}:{provider}:{namespace}:{value}"
        if product_type == "insurance-product" and namespace == "official_product_code":
            return f"product:{product_type}:{slug(item.get('product_kind') or item.get('search_type'))}:{provider}:{namespace}:{value}"
    return None


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
        item["external_product_ids"] = external_product_ids(item)
        item["provider_external_ids"] = provider_external_ids(item)
        item["provider_roles"] = list(item.get("provider_roles") or ["issuer"])
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
        record["external_product_ids"] = external_product_ids(record)
        record["provider_external_ids"] = provider_external_ids(record)
        grouped[external_merge_key(record) or record["canonical_product_id"]].append(record)

    merged: list[dict[str, Any]] = []
    for _, records in sorted(grouped.items()):
        ordered = sorted(records, key=record_priority, reverse=True)
        preferred = deepcopy(ordered[0])
        canonical_id = str(ordered[0].get("canonical_product_id") or canonical_product_id(ordered[0]))
        preferred["canonical_product_id"] = canonical_id
        preferred["source_records"] = [source_record(record) for record in ordered]
        preferred["external_product_ids"] = []
        preferred["provider_external_ids"] = []
        for record in ordered:
            for identifier in record.get("external_product_ids") or []:
                if identifier not in preferred["external_product_ids"]:
                    preferred["external_product_ids"].append(identifier)
            for identifier in record.get("provider_external_ids") or []:
                if identifier not in preferred["provider_external_ids"]:
                    preferred["provider_external_ids"].append(identifier)
        preferred["provider_roles"] = sorted({role for record in ordered for role in record.get("provider_roles") or ["issuer"]})
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
