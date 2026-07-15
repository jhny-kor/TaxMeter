#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = ROOT.parent
DEFAULT_SEARCH_INDEX = ROOT / "exports" / "finance-search-index-2026.json"


def load_search_index_payload(path: Path = DEFAULT_SEARCH_INDEX) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload.get("items") is not None:
        return payload
    items: list[dict[str, Any]] = []
    for shard in payload.get("shards") or []:
        if not isinstance(shard, dict) or not shard.get("path"):
            continue
        shard_path = REPO_ROOT / str(shard["path"])
        shard_payload = json.loads(shard_path.read_text(encoding="utf-8"))
        items.extend(item for item in shard_payload.get("items") or [] if isinstance(item, dict))
    return {**payload, "items": items}


def load_search_index_items(path: Path = DEFAULT_SEARCH_INDEX) -> list[dict[str, Any]]:
    return [item for item in load_search_index_payload(path).get("items") or [] if isinstance(item, dict)]


def search_index_basis_date(path: Path = DEFAULT_SEARCH_INDEX) -> str:
    return str(load_search_index_payload(path).get("basis_date") or "")
