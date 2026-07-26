#!/usr/bin/env python3
"""Strict, deterministic resolution for named finance-product queries."""

from __future__ import annotations

from typing import Any

from recommendation_intent_parser import PROVIDER_ALIASES, compact_product_text, parse_query


def is_named_product_query(query: str) -> bool:
    parsed = parse_query(query)
    return bool(
        parsed.get("domain")
        and parsed.get("product_kind")
        and (parsed.get("provider") or parsed.get("product_name_tokens"))
    )


def _canonical_id(item: dict[str, Any]) -> str:
    return str(
        item.get("resolved_canonical_product_id")
        or item.get("canonical_product_id")
        or item.get("id")
    )


def _product_text(item: dict[str, Any]) -> str:
    values: list[str] = []
    for key in (
        "id",
        "title",
        "provider",
        "product_name",
        "product_kind",
        "search_type",
        "search_text",
        "search_aliases",
        "aliases",
    ):
        value = item.get(key)
        if isinstance(value, list):
            values.extend(str(entry) for entry in value)
        elif value not in (None, ""):
            values.append(str(value))
    return compact_product_text(" ".join(values))


def _provider_matches(item: dict[str, Any], provider: str) -> bool:
    haystack = _product_text(item)
    aliases = PROVIDER_ALIASES.get(provider, (provider,))
    return any(compact_product_text(alias) in haystack for alias in aliases)


def _kind_matches(item: dict[str, Any], product_kind: str) -> bool:
    item_kind = compact_product_text(str(item.get("product_kind") or ""))
    return item_kind == compact_product_text(product_kind)


def resolve_named_product_query(query: str, items: list[dict[str, Any]], limit: int = 20) -> dict[str, Any] | None:
    """Return a strict resolution payload, or ``None`` for generic queries.

    A named query never falls back to any-term matching.  Product/provider/type
    constraints are applied before ranking, and records sharing a canonical
    product id are returned once.
    """

    parsed = parse_query(query)
    if not is_named_product_query(query):
        return None
    provider = parsed.get("provider")
    product_kind = parsed.get("product_kind")
    name_tokens = [str(token) for token in parsed.get("product_name_tokens") or []]
    candidates: list[dict[str, Any]] = []
    for item in items:
        if item.get("recommendation_status") == "manual_review_candidate" or item.get("recommendation_scope") == "internal_verification_candidate":
            continue
        if not _kind_matches(item, str(product_kind)):
            continue
        if provider and not _provider_matches(item, str(provider)):
            continue
        text = _product_text(item)
        if any(compact_product_text(token) not in text for token in name_tokens):
            continue
        candidates.append(item)

    by_canonical: dict[str, dict[str, Any]] = {}
    for item in candidates:
        canonical = _canonical_id(item)
        current = by_canonical.get(canonical)
        if current is None:
            by_canonical[canonical] = item
            continue
        # Prefer the richer/current source record while keeping the canonical
        # identity stable.  This prevents duplicate provider feeds from
        # changing the answer order.
        current_key = (
            current.get("status") == "active",
            current.get("source_listing_status") == "listed",
            len(str(current.get("title") or "")),
            str(current.get("id") or ""),
        )
        candidate_key = (
            item.get("status") == "active",
            item.get("source_listing_status") == "listed",
            len(str(item.get("title") or "")),
            str(item.get("id") or ""),
        )
        if candidate_key > current_key:
            by_canonical[canonical] = item

    resolved = sorted(by_canonical.values(), key=lambda item: (str(item.get("title") or ""), str(item.get("id") or "")))[:limit]
    has_complete_identity = bool(provider and product_kind and name_tokens)
    if not resolved:
        resolution_status = "not_found"
    elif has_complete_identity and len(resolved) == 1:
        resolution_status = "exact"
    elif has_complete_identity:
        resolution_status = "ambiguous"
    else:
        resolution_status = "ambiguous"
    return {
        "query": query,
        "parsed_intent": parsed,
        "resolution": {
            "status": resolution_status,
            "provider_required": provider,
            "product_kind_required": product_kind,
            "name_tokens_required": name_tokens,
            "canonical_product_ids": [_canonical_id(item) for item in resolved],
            "candidate_count": len(resolved),
        },
        "items": resolved,
        "unparsed_tokens": parsed.get("unparsed_tokens") or [],
        "limitations": [
            "named product queries use provider, official product name evidence, and product type before ranking",
            "no partial or unrelated fallback is returned when a named product is not found",
        ],
    }
