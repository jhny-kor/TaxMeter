#!/usr/bin/env python3
"""MCP stdio server for the standalone OpenTax vault.

The server intentionally has no third-party dependency. It exposes the
Obsidian vault and JSON export through read tools, and writes only through the
custom overlay file so the official generated baseline remains reviewable.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
SCRIPTS = ROOT / "scripts"
VAULT = ROOT / "vault"
CUSTOM_ITEMS_PATH = ROOT / "custom" / "items.json"
EXPORT_PATH = ROOT / "exports" / "korea-tax-ontology-2026.json"
PYTHON = sys.executable

sys.path.insert(0, str(SCRIPTS))

try:
    from .scripts.generate_vault import build_all_items, expected_note_path  # type: ignore
except ImportError:
    from generate_vault import build_all_items, expected_note_path  # type: ignore  # noqa: E402


REFERENCE_KEYS = ("parents", "children", "related", "terms", "deadlines", "sources")
ITEM_TYPES = {
    "domain",
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
    "source",
}


class ToolError(Exception):
    pass


def read_custom_payload() -> dict[str, Any]:
    if not CUSTOM_ITEMS_PATH.exists():
        return {"items": []}
    payload = json.loads(CUSTOM_ITEMS_PATH.read_text(encoding="utf-8"))
    if isinstance(payload, list):
        return {"items": payload}
    payload.setdefault("items", [])
    return payload


def write_custom_payload(payload: dict[str, Any]) -> None:
    CUSTOM_ITEMS_PATH.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = CUSTOM_ITEMS_PATH.with_suffix(".json.tmp")
    tmp_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    tmp_path.replace(CUSTOM_ITEMS_PATH)


def run_command(args: list[str]) -> subprocess.CompletedProcess[str]:
    env = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}
    return subprocess.run(
        args,
        cwd=ROOT.parent,
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )


def regenerate_and_validate() -> dict[str, str]:
    generate = run_command([PYTHON, str(SCRIPTS / "generate_vault.py")])
    if generate.returncode != 0:
        raise ToolError(f"generate_vault.py failed:\n{generate.stdout}\n{generate.stderr}".strip())
    validate = run_command([PYTHON, str(SCRIPTS / "validate_ontology.py")])
    if validate.returncode != 0:
        raise ToolError(f"validate_ontology.py failed:\n{validate.stdout}\n{validate.stderr}".strip())
    return {"generate": generate.stdout.strip(), "validate": validate.stdout.strip()}


def rollback_on_failure(previous_payload: dict[str, Any], operation) -> Any:
    try:
        result = operation()
        return result
    except Exception:
        write_custom_payload(previous_payload)
        try:
            regenerate_and_validate()
        except Exception:
            pass
        raise


def all_items() -> dict[str, dict[str, Any]]:
    return build_all_items()


def item_note_path(item: dict[str, Any]) -> Path:
    return expected_note_path(item)


def serialize_item(item: dict[str, Any]) -> dict[str, Any]:
    serialized = dict(item)
    note_path = item_note_path(item)
    if note_path.exists():
        serialized["note_path"] = str(note_path)
    return serialized


def get_item_or_error(item_id: str) -> dict[str, Any]:
    items = all_items()
    item = items.get(item_id)
    if not item:
        raise ToolError(f"Unknown ontology item id: {item_id}")
    return item


def read_note_text(path_or_id: str) -> tuple[Path, str]:
    items = all_items()
    if path_or_id in items:
        path = item_note_path(items[path_or_id])
    else:
        raw_path = Path(path_or_id)
        path = raw_path if raw_path.is_absolute() else ROOT.parent / raw_path
    resolved = path.resolve()
    vault_root = VAULT.resolve()
    if vault_root not in resolved.parents and resolved != vault_root:
        raise ToolError(f"Path is outside ontology vault: {path_or_id}")
    if not resolved.exists():
        raise ToolError(f"Note does not exist: {path_or_id}")
    return resolved, resolved.read_text(encoding="utf-8")


def search_items(query: str, type_filter: str | None = None, limit: int = 20) -> list[dict[str, Any]]:
    query_terms = [term.casefold() for term in query.split() if term.strip()]
    items = all_items()
    results: list[tuple[int, dict[str, Any]]] = []
    for item in items.values():
        if type_filter and item.get("type") != type_filter:
            continue
        haystack = " ".join(
            str(item.get(key, ""))
            for key in ("id", "title", "type", "description", "law_reference", "tags", "url")
        ).casefold()
        if query_terms and not all(term in haystack for term in query_terms):
            continue
        score = 0
        title = str(item.get("title", "")).casefold()
        item_id = str(item.get("id", "")).casefold()
        for term in query_terms:
            if term in title:
                score += 4
            if term in item_id:
                score += 3
            if term in haystack:
                score += 1
        results.append((score, item))
    results.sort(key=lambda pair: (-pair[0], pair[1]["id"]))
    return [serialize_item(item) for _, item in results[:limit]]


def neighbor_items(item_id: str, depth: int = 1) -> dict[str, Any]:
    items = all_items()
    start = items.get(item_id)
    if not start:
        raise ToolError(f"Unknown ontology item id: {item_id}")

    visited = {item_id}
    frontier = [item_id]
    nodes = {item_id: serialize_item(start)}
    edges: list[dict[str, str]] = []
    for _ in range(max(depth, 1)):
        next_frontier: list[str] = []
        for current_id in frontier:
            current = items[current_id]
            for key in ("parents", "children", "related", "terms", "deadlines", "sources"):
                for target_id in current.get(key) or []:
                    target = items.get(target_id)
                    if not target:
                        continue
                    edges.append({"from": current_id, "to": target_id, "relation": key})
                    if target_id not in visited:
                        visited.add(target_id)
                        nodes[target_id] = serialize_item(target)
                        next_frontier.append(target_id)
        frontier = next_frontier
    return {"center": item_id, "nodes": nodes, "edges": edges}


def validate_item_payload(item: dict[str, Any], existing_items: dict[str, dict[str, Any]]) -> dict[str, Any]:
    normalized = dict(item)
    required = ("id", "title", "type", "description")
    for key in required:
        if not normalized.get(key):
            raise ToolError(f"item.{key} is required")
    if normalized["type"] not in ITEM_TYPES:
        raise ToolError(f"Unsupported item type: {normalized['type']}")
    normalized.setdefault("folder", default_folder(normalized["type"]))
    for key in REFERENCE_KEYS + ("tags",):
        normalized.setdefault(key, [])
        if not isinstance(normalized[key], list):
            raise ToolError(f"item.{key} must be an array")
    normalized.setdefault("basis_year", None if normalized["type"] in {"source", "deadline"} else 2026)
    normalized.setdefault("effective_date", None)
    normalized.setdefault("expiration_date", None)
    normalized.setdefault("law_reference", "")
    if normalized["type"] == "source":
        for key in ("publisher", "url", "basis_date"):
            if not normalized.get(key):
                raise ToolError(f"source item requires {key}")
    elif not normalized["sources"]:
        raise ToolError("non-source item requires at least one source id")
    for key in REFERENCE_KEYS:
        for ref_id in normalized[key]:
            if ref_id not in existing_items and ref_id != normalized["id"]:
                raise ToolError(f"item.{key} references unknown id: {ref_id}")
    return normalized


def default_folder(item_type: str) -> str:
    return {
        "domain": "00_Index",
        "category": "00_Index",
        "tax": "10_Taxes/Custom",
        "deduction": "20_Deductions/IncomeDeductions",
        "tax-credit": "20_Deductions/TaxCredits",
        "tax-reduction": "20_Deductions/TaxReductions",
        "corporate-tax-support": "20_Deductions/CorporateTaxSupports",
        "support-program": "30_Supports",
        "filing": "50_Deadlines",
        "concept": "40_Terms/Concepts",
        "term": "40_Terms",
        "deadline": "50_Deadlines",
        "source": "90_Sources",
    }[item_type]


def upsert_custom_item(item: dict[str, Any]) -> dict[str, Any]:
    previous = read_custom_payload()

    def operation() -> dict[str, Any]:
        current_items = all_items()
        normalized = validate_item_payload(item, current_items)
        payload = read_custom_payload()
        custom_items = payload.setdefault("items", [])
        for index, existing in enumerate(custom_items):
            if existing.get("id") == normalized["id"]:
                custom_items[index] = normalized
                break
        else:
            custom_items.append(normalized)
        write_custom_payload(payload)
        logs = regenerate_and_validate()
        updated_item = get_item_or_error(normalized["id"])
        return {"item": serialize_item(updated_item), "logs": logs}

    return rollback_on_failure(previous, operation)


def patch_custom_item(item_id: str, patch: dict[str, Any]) -> dict[str, Any]:
    previous = read_custom_payload()

    def operation() -> dict[str, Any]:
        current_items = all_items()
        base = current_items.get(item_id)
        if not base:
            raise ToolError(f"Unknown ontology item id: {item_id}")
        merged = {**base, **patch, "id": item_id}
        normalized = validate_item_payload(merged, current_items)
        payload = read_custom_payload()
        custom_items = payload.setdefault("items", [])
        for index, existing in enumerate(custom_items):
            if existing.get("id") == item_id:
                custom_items[index] = {**existing, **patch, "id": item_id}
                break
        else:
            custom_items.append({**patch, "id": item_id})
        write_custom_payload(payload)
        logs = regenerate_and_validate()
        updated_item = get_item_or_error(item_id)
        return {"item": serialize_item(updated_item), "logs": logs}

    return rollback_on_failure(previous, operation)


def delete_custom_item(item_id: str) -> dict[str, Any]:
    previous = read_custom_payload()

    def operation() -> dict[str, Any]:
        payload = read_custom_payload()
        before = len(payload.get("items", []))
        payload["items"] = [item for item in payload.get("items", []) if item.get("id") != item_id]
        if len(payload["items"]) == before:
            raise ToolError(f"No custom overlay item found for id: {item_id}")
        write_custom_payload(payload)
        logs = regenerate_and_validate()
        return {"deleted_custom_item": item_id, "logs": logs}

    return rollback_on_failure(previous, operation)


def export_summary() -> dict[str, Any]:
    if not EXPORT_PATH.exists():
        regenerate_and_validate()
    data = json.loads(EXPORT_PATH.read_text(encoding="utf-8"))
    counts: dict[str, int] = {}
    for item in data["items"]:
        counts[item["type"]] = counts.get(item["type"], 0) + 1
    return {
        "path": str(EXPORT_PATH),
        "version": data["version"],
        "basis_date": data["basis_date"],
        "item_count": len(data["items"]),
        "counts_by_type": counts,
        "manifests": data["manifests"],
    }


TOOLS: dict[str, dict[str, Any]] = {
    "opentax_search": {
        "description": "Search OpenTax items by id, title, type, description, tag, law reference, or URL.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {"type": "string"},
                "type": {"type": "string"},
                "limit": {"type": "integer", "minimum": 1, "maximum": 100},
            },
            "required": ["query"],
        },
    },
    "opentax_get_item": {
        "description": "Get one ontology item by ontology id, including its generated note path.",
        "inputSchema": {
            "type": "object",
            "properties": {"id": {"type": "string"}},
            "required": ["id"],
        },
    },
    "opentax_read_note": {
        "description": "Read an Obsidian note by ontology id or vault-relative path.",
        "inputSchema": {
            "type": "object",
            "properties": {"path_or_id": {"type": "string"}},
            "required": ["path_or_id"],
        },
    },
    "opentax_neighbors": {
        "description": "Return parent, child, related, term, deadline, and source neighbors for an item.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "id": {"type": "string"},
                "depth": {"type": "integer", "minimum": 1, "maximum": 3},
            },
            "required": ["id"],
        },
    },
    "opentax_sources": {
        "description": "Return source notes and URLs linked to an ontology item.",
        "inputSchema": {
            "type": "object",
            "properties": {"id": {"type": "string"}},
            "required": ["id"],
        },
    },
    "opentax_validate": {
        "description": "Run the ontology validator and return its output.",
        "inputSchema": {"type": "object", "properties": {}},
    },
    "opentax_export_summary": {
        "description": "Return JSON export path, manifest sizes, and counts by type.",
        "inputSchema": {"type": "object", "properties": {}},
    },
    "opentax_add_or_update_item": {
        "description": "Add or replace an item in ontology/custom/items.json, then regenerate and validate the vault.",
        "inputSchema": {
            "type": "object",
            "properties": {"item": {"type": "object"}},
            "required": ["item"],
        },
    },
    "opentax_patch_item": {
        "description": "Patch a built-in or custom item through the custom overlay, then regenerate and validate the vault.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "id": {"type": "string"},
                "patch": {"type": "object"},
            },
            "required": ["id", "patch"],
        },
    },
    "opentax_delete_custom_item": {
        "description": "Delete a custom overlay item and regenerate. Built-in base items cannot be deleted with this tool.",
        "inputSchema": {
            "type": "object",
            "properties": {"id": {"type": "string"}},
            "required": ["id"],
        },
    },
}


PRIMARY_TOOL_PREFIX = "opentax_"
LEGACY_TOOL_PREFIX = "tax_ontology_"


for tool_name, definition in list(TOOLS.items()):
    if tool_name.startswith(PRIMARY_TOOL_PREFIX):
        legacy_name = LEGACY_TOOL_PREFIX + tool_name[len(PRIMARY_TOOL_PREFIX):]
        TOOLS[legacy_name] = {
            **definition,
            "description": f"Legacy alias for `{tool_name}`. {definition['description']}",
        }


def normalize_tool_name(name: str) -> str:
    if name.startswith(LEGACY_TOOL_PREFIX):
        return PRIMARY_TOOL_PREFIX + name[len(LEGACY_TOOL_PREFIX):]
    return name


def call_tool(name: str, arguments: dict[str, Any]) -> Any:
    if not isinstance(name, str):
        raise ToolError("Tool name must be a string")
    name = normalize_tool_name(name)
    if name == "opentax_search":
        return search_items(
            arguments.get("query", ""),
            arguments.get("type"),
            int(arguments.get("limit", 20)),
        )
    if name == "opentax_get_item":
        return serialize_item(get_item_or_error(arguments["id"]))
    if name == "opentax_read_note":
        path, text = read_note_text(arguments["path_or_id"])
        return {"path": str(path), "text": text}
    if name == "opentax_neighbors":
        return neighbor_items(arguments["id"], int(arguments.get("depth", 1)))
    if name == "opentax_sources":
        item = get_item_or_error(arguments["id"])
        items = all_items()
        return [serialize_item(items[source_id]) for source_id in item.get("sources") or [] if source_id in items]
    if name == "opentax_validate":
        return regenerate_and_validate()["validate"]
    if name == "opentax_export_summary":
        return export_summary()
    if name == "opentax_add_or_update_item":
        return upsert_custom_item(arguments["item"])
    if name == "opentax_patch_item":
        return patch_custom_item(arguments["id"], arguments["patch"])
    if name == "opentax_delete_custom_item":
        return delete_custom_item(arguments["id"])
    raise ToolError(f"Unknown tool: {name}")


def content_result(payload: Any, is_error: bool = False) -> dict[str, Any]:
    if isinstance(payload, str):
        text = payload
    else:
        text = json.dumps(payload, ensure_ascii=False, indent=2)
    return {"content": [{"type": "text", "text": text}], "isError": is_error}


def respond(message_id: Any, result: Any = None, error: dict[str, Any] | None = None) -> None:
    response: dict[str, Any] = {"jsonrpc": "2.0", "id": message_id}
    if error is not None:
        response["error"] = error
    else:
        response["result"] = result
    sys.stdout.write(json.dumps(response, ensure_ascii=False) + "\n")
    sys.stdout.flush()


def handle_request(message: dict[str, Any]) -> None:
    method = message.get("method")
    message_id = message.get("id")

    if method == "initialize":
        respond(
            message_id,
            {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}},
                "serverInfo": {"name": "opentax-mcp", "version": "0.1.0"},
            },
        )
        return

    if method == "ping":
        respond(message_id, {})
        return

    if method == "tools/list":
        respond(
            message_id,
            {"tools": [{"name": name, **definition} for name, definition in TOOLS.items()]},
        )
        return

    if method == "tools/call":
        params = message.get("params") or {}
        name = params.get("name")
        arguments = params.get("arguments") or {}
        try:
            payload = call_tool(name, arguments)
            respond(message_id, content_result(payload))
        except Exception as exc:
            respond(message_id, content_result(str(exc), is_error=True))
        return

    if message_id is not None:
        respond(message_id, error={"code": -32601, "message": f"Method not found: {method}"})


def main() -> None:
    for raw_line in sys.stdin:
        raw_line = raw_line.strip()
        if not raw_line:
            continue
        try:
            message = json.loads(raw_line)
            if "id" not in message and str(message.get("method", "")).startswith("notifications/"):
                continue
            handle_request(message)
        except Exception as exc:
            if "message" in locals() and isinstance(message, dict) and "id" in message:
                respond(message["id"], error={"code": -32603, "message": str(exc)})
            else:
                print(f"opentax-mcp error: {exc}", file=sys.stderr)


if __name__ == "__main__":
    main()
