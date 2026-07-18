#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = ROOT.parent
DEFAULT_SEARCH_INDEX = ROOT / "exports" / "finance-search-index-2026.json"
_METADATA_CACHE: dict[Path, dict[str, Any]] = {}
_ITEMS_CACHE: dict[Path, list[dict[str, Any]]] = {}


def _resolve_shard_path(index_path: Path, shard_path: str) -> Path:
    candidate = Path(shard_path)
    if candidate.is_absolute():
        return candidate
    if str(candidate).startswith("ontology/"):
        return REPO_ROOT / candidate
    return index_path.parent / candidate


def _parse_items(payload: Any, source: Path) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    if isinstance(payload, list):
        if any(not isinstance(item, dict) for item in payload):
            raise ValueError(f"search index array items must be objects: {source}")
        return {}, list(payload)
    if not isinstance(payload, dict):
        raise ValueError(f"search index must be an object or array: {source}")
    metadata = {key: value for key, value in payload.items() if key != "items"}
    raw_items = payload.get("items")
    if raw_items is not None:
        if not isinstance(raw_items, list):
            raise ValueError(f"search index items must be an array: {source}")
        if any(not isinstance(item, dict) for item in raw_items):
            raise ValueError(f"search index items must be objects: {source}")
        return metadata, list(raw_items)
    return metadata, []


def load_search_index_payload(path: Path = DEFAULT_SEARCH_INDEX) -> dict[str, Any]:
    resolved = path.resolve()
    if resolved not in _METADATA_CACHE or resolved not in _ITEMS_CACHE:
        root_metadata, inline_items = _parse_items(json.loads(resolved.read_text(encoding="utf-8")), resolved)
        if inline_items:
            items = inline_items
        else:
            shards = root_metadata.get("shards") or []
            items = []
            for shard in shards:
                if not isinstance(shard, dict) or not shard.get("path"):
                    raise ValueError(f"search index shard manifest entry is invalid: {resolved}")
                shard_path = _resolve_shard_path(resolved, str(shard["path"]))
                shard_metadata, shard_items = _parse_items(json.loads(shard_path.read_text(encoding="utf-8")), shard_path)
                declared_count = shard.get("item_count")
                if declared_count != len(shard_items):
                    raise ValueError(f"search index shard item_count mismatch: {shard_path}")
                items.extend(shard_items)
            if shards and root_metadata.get("item_count") != len(items):
                raise ValueError(f"search index item_count mismatch: {resolved}")
        declared_count = root_metadata.get("item_count")
        if declared_count is not None and not root_metadata.get("shards") and declared_count != len(items):
            raise ValueError(f"search index item_count mismatch: {resolved}")
        _METADATA_CACHE[resolved] = root_metadata
        _ITEMS_CACHE[resolved] = items
    return {**_METADATA_CACHE[resolved], "items": list(_ITEMS_CACHE[resolved])}


def load_search_index_items(path: Path = DEFAULT_SEARCH_INDEX) -> list[dict[str, Any]]:
    load_search_index_payload(path)
    return list(_ITEMS_CACHE[path.resolve()])


def search_index_basis_date(path: Path = DEFAULT_SEARCH_INDEX) -> str:
    return str(load_search_index_payload(path).get("basis_date") or "")


loadSearchItems = load_search_index_items
