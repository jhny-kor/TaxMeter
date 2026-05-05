#!/usr/bin/env python3
"""Validate split finance ontology exports and manifest."""

from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EXPORT_DIR = ROOT / "exports"
MANIFEST = EXPORT_DIR / "finance-ontology-manifest.json"

REFERENCE_KEYS = ("parents", "children", "related", "terms", "deadlines", "sources")
PRODUCT_TYPES = {"card-product", "bank-product", "insurance-product"}
REQUIRED_PRODUCT_FIELDS = (
    "provider",
    "provider_code",
    "product_code",
    "product_kind",
    "product_status",
    "sales_status",
    "source_record_id",
    "source_urls",
    "source_basis_dates",
    "collected_at",
)


def require(condition: bool, message: str, errors: list[str]) -> None:
    if not condition:
        errors.append(message)


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def item_map(items: list[dict]) -> dict[str, dict]:
    result: dict[str, dict] = {}
    for item in items:
        item_id = item.get("id")
        if item_id:
            result[item_id] = item
    return result


def validate_item_basics(export_id: str, items: list[dict], errors: list[str]) -> None:
    ids = [item.get("id") for item in items]
    require(len(ids) == len(set(ids)), f"{export_id}: duplicate item ids", errors)
    by_id = item_map(items)
    for item in items:
        item_id = item.get("id", "<missing>")
        require(bool(item.get("title")), f"{export_id}:{item_id}: missing title", errors)
        require(bool(item.get("type")), f"{export_id}:{item_id}: missing type", errors)
        require(bool(item.get("description")), f"{export_id}:{item_id}: missing description", errors)
        require(isinstance(item.get("parents"), list), f"{export_id}:{item_id}: parents must be list", errors)
        require(isinstance(item.get("children"), list), f"{export_id}:{item_id}: children must be list", errors)
        if item.get("type") != "source":
            require(bool(item.get("sources")), f"{export_id}:{item_id}: missing sources", errors)
            require(bool(item.get("reviewed_at")), f"{export_id}:{item_id}: missing reviewed_at", errors)
            require(bool(item.get("source_urls")), f"{export_id}:{item_id}: missing source_urls", errors)
            require(bool(item.get("source_basis_dates")), f"{export_id}:{item_id}: missing source_basis_dates", errors)
        if item.get("type") == "source":
            require(bool(item.get("url")), f"{export_id}:{item_id}: source missing url", errors)
            require(bool(item.get("publisher")), f"{export_id}:{item_id}: source missing publisher", errors)
        for key in REFERENCE_KEYS:
            for target_id in item.get(key) or []:
                require(target_id in by_id, f"{export_id}:{item_id}: {key} references missing id {target_id}", errors)


def validate_products(export_id: str, items: list[dict], expected_product_count: int, errors: list[str]) -> None:
    products = [item for item in items if item.get("type") in PRODUCT_TYPES]
    require(len(products) == expected_product_count, f"{export_id}: product_count mismatch", errors)
    for item in products:
        item_id = item["id"]
        for field in REQUIRED_PRODUCT_FIELDS:
            require(bool(item.get(field)), f"{export_id}:{item_id}: missing {field}", errors)
        require(item.get("product_status") in {"active", "ended", "suspended", "unknown"}, f"{export_id}:{item_id}: invalid product_status", errors)
        require(item.get("sales_status") in {"active", "ended", "suspended", "unknown"}, f"{export_id}:{item_id}: invalid sales_status", errors)
        criteria = item.get("criteria") or []
        require(isinstance(criteria, list), f"{export_id}:{item_id}: criteria must be a list", errors)
        for index, criterion in enumerate(criteria, start=1):
            require(bool(criterion.get("source")), f"{export_id}:{item_id}: criteria #{index} missing source", errors)
            require(bool(criterion.get("basis_source")), f"{export_id}:{item_id}: criteria #{index} missing basis_source", errors)
            require(bool(criterion.get("basis_definition")), f"{export_id}:{item_id}: criteria #{index} missing basis_definition", errors)


def validate_manifest(errors: list[str]) -> list[dict]:
    require(MANIFEST.exists(), f"missing {MANIFEST}", errors)
    if not MANIFEST.exists():
        return []
    payload = load_json(MANIFEST)
    exports = payload.get("exports") or []
    require(payload.get("name") == "finance", "manifest name must be finance", errors)
    require(isinstance(exports, list) and bool(exports), "manifest exports must be a non-empty list", errors)
    ids = [entry.get("id") for entry in exports]
    require(len(ids) == len(set(ids)), "manifest duplicate export ids", errors)
    for entry in exports:
        export_id = entry.get("id", "<missing>")
        path_text = entry.get("path")
        require(bool(path_text), f"{export_id}: missing path", errors)
        if not path_text:
            continue
        require("ontology" in Path(path_text).name, f"{export_id}: export filename should include ontology", errors)
        path = ROOT.parent / path_text
        require(path.exists(), f"{export_id}: missing export file {path_text}", errors)
        require(bool(entry.get("url")), f"{export_id}: missing raw url", errors)
        require(bool(entry.get("web_url")), f"{export_id}: missing web url", errors)
    return exports


def main() -> int:
    errors: list[str] = []
    exports = validate_manifest(errors)
    for entry in exports:
        path_text = entry.get("path")
        if not path_text:
            continue
        path = ROOT.parent / path_text
        if not path.exists():
            continue
        payload = load_json(path)
        items = payload.get("items") or []
        if payload.get("reference_items"):
            items = [*(payload.get("reference_items") or []), *items]
        require(isinstance(items, list) and bool(items), f"{entry.get('id')}: export has no items", errors)
        validate_item_basics(entry.get("id", path.name), items, errors)
        validate_products(entry.get("id", path.name), items, int(entry.get("product_count") or 0), errors)

    if errors:
        print("Finance ontology validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    print(f"Finance ontology validation passed: {len(exports)} exports")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
