#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# ///
"""Fail deployment verification when the live Finance MCP cannot hydrate search items."""
from __future__ import annotations

import argparse
import json
import time
import urllib.error
import urllib.request
from collections.abc import Mapping
from typing import Final, TypeAlias

DEFAULT_MCP_URL: Final = "https://finance-mcp.y2kthr.workers.dev/mcp"
PROTOCOL_VERSION: Final = "2025-03-26"
JsonValue: TypeAlias = str | int | float | bool | None | list["JsonValue"] | dict[str, "JsonValue"]
McpParams: TypeAlias = dict[str, JsonValue]
SmokeCall: TypeAlias = tuple[str, McpParams]
SMOKE_CALLS: Final[tuple[SmokeCall, ...]] = (
    ("exports", {}),
    ("search", {"query": "월세 세액공제 조건", "limit": 1}),
    ("search_insurance_tax", {"query": "보험료 세액공제", "limit": 5}),
    ("support_search", {"query": "서울 청년 월세 지원", "region": "서울특별시", "limit": 5}),
    ("fetch", {"id": "credit.monthly-rent"}),
    ("discover_card", {"query": "마일리지 체크카드 추천", "limit": 5}),
    ("discover_insurance", {"query": "실손보험 추천", "limit": 5}),
    ("compare", {"domain": "deposit", "deposit_amount_krw": 10_000_000, "term_months": 12}),
    ("compare_saving", {"domain": "saving", "monthly_payment_krw": 500_000, "term_months": 12}),
    ("recommend", {"domain": "deposit", "limit": 1}),
)


class McpSmokeError(RuntimeError):
    pass


def parse_json_object(body: str) -> dict[str, JsonValue]:
    parsed = json.loads(body)
    if isinstance(parsed, dict):
        return parsed
    raise McpSmokeError("MCP response must be a JSON object")


def parse_sse_response(body: str) -> dict[str, JsonValue]:
    for line in body.splitlines():
        if line.startswith("data:"):
            return parse_json_object(line.removeprefix("data:").strip())
    if not body.strip():
        raise McpSmokeError("MCP response is empty")
    return parse_json_object(body)


def response_error(result: Mapping[str, JsonValue]) -> str | None:
    serialized = json.dumps(result, ensure_ascii=False)
    if result.get("isError") is True or result.get("is_error") is True or "TypeError" in serialized:
        return serialized
    return None


def tool_payload(result: Mapping[str, JsonValue]) -> Mapping[str, JsonValue]:
    structured = result.get("structuredContent")
    if isinstance(structured, Mapping):
        return structured
    content = result.get("content")
    if isinstance(content, list):
        for block in content:
            if isinstance(block, Mapping) and isinstance(text := block.get("text"), str):
                try:
                    parsed = json.loads(text)
                except json.JSONDecodeError:
                    continue
                if isinstance(parsed, Mapping):
                    return parsed
    return {}


def validate_tool_payload(label: str, payload: Mapping[str, JsonValue]) -> None:
    candidate_count = payload.get("candidate_count")
    candidates = payload.get("candidates")
    excluded_count = payload.get("excluded_count")
    excluded_summary = payload.get("excluded_summary")
    if isinstance(candidate_count, int) and isinstance(candidates, list) and candidate_count != len(candidates):
        raise McpSmokeError(f"{label}: candidate_count does not match candidates length")
    if isinstance(excluded_count, int) and isinstance(excluded_summary, Mapping) and sum(value for value in excluded_summary.values() if isinstance(value, int)) != excluded_count:
        raise McpSmokeError(f"{label}: excluded_summary does not sum to excluded_count")
    if isinstance(candidates, list):
        external_ids: dict[str, str] = {}
        for candidate in candidates:
            if not isinstance(candidate, Mapping):
                continue
            for external in candidate.get("external_product_ids", []) if isinstance(candidate.get("external_product_ids"), list) else []:
                if not isinstance(external, Mapping):
                    continue
                key = f"{external.get('namespace')}:{external.get('value')}"
                item_id = str(candidate.get("item_id") or candidate.get("id") or "")
                previous = external_ids.get(key)
                if previous and previous != item_id:
                    raise McpSmokeError(f"{label}: duplicate external product id {key}")
                external_ids[key] = item_id
    if label == "exports":
        runtime = payload.get("runtime")
        search_index = payload.get("search_index")
        if not isinstance(runtime, Mapping) or not all(isinstance(runtime.get(key), str) and runtime.get(key) for key in ("runtime_version", "deployment_commit", "manifest_version")):
            raise McpSmokeError("exports: runtime metadata is incomplete")
        if not isinstance(search_index, Mapping) or not isinstance(search_index.get("loaded_item_count"), int) or search_index.get("loaded_item_count", 0) <= 0:
            raise McpSmokeError("exports: hydrated search-index metadata is incomplete")
    if label == "support_search":
        if not all(key in payload for key in ("exact_results", "partial_results", "related_results", "parsed_query")):
            raise McpSmokeError("support_search: match-tier response fields are incomplete")
        parsed_query = payload.get("parsed_query")
        if not isinstance(parsed_query, Mapping) or parsed_query.get("region") != "서울특별시" or "youth" not in (parsed_query.get("target_groups") or []):
            raise McpSmokeError("support_search: parsed region/target group contract failed")
    readiness = payload.get("readiness")
    states = payload.get("readiness_states")
    if isinstance(readiness, Mapping) and isinstance(states, Mapping):
        public_count = readiness.get("public_recommendation_candidate_count")
        if states.get("public_recommendation") == "ready" and public_count != payload.get("result_count"):
            raise McpSmokeError(f"{label}: readiness public recommendation state mismatches result count")


class McpSmokeClient:
    def __init__(self, url: str) -> None:
        self.url = url
        self.request_id = 0
        self.session_id: str | None = None

    def post(self, payload: Mapping[str, JsonValue]) -> Mapping[str, JsonValue] | None:
        headers = {
            "content-type": "application/json",
            "accept": "application/json, text/event-stream",
            "user-agent": "openfin-mcp-smoke/1.0",
        }
        if self.session_id:
            headers["mcp-session-id"] = self.session_id
        for attempt in range(3):
            request = urllib.request.Request(
                self.url,
                data=json.dumps(payload).encode("utf-8"),
                headers=headers,
            )
            try:
                with urllib.request.urlopen(request, timeout=90) as response:
                    session_id = response.headers.get("mcp-session-id")
                    if session_id:
                        self.session_id = session_id
                    body = response.read().decode("utf-8")
            except urllib.error.HTTPError as error:
                if error.code < 500 or attempt == 2:
                    raise
                time.sleep(attempt + 1)
                continue
            if body.strip():
                return parse_sse_response(body)
            if attempt < 2:
                time.sleep(attempt + 1)
        return None

    def request(self, method: str, params: Mapping[str, JsonValue] | None = None) -> Mapping[str, JsonValue]:
        self.request_id += 1
        payload: McpParams = {"jsonrpc": "2.0", "id": self.request_id, "method": method}
        if params is not None:
            payload["params"] = dict(params)
        parsed = self.post(payload)
        if parsed is None:
            raise McpSmokeError(f"MCP {method} response is empty")
        if "error" in parsed:
            raise McpSmokeError(json.dumps(parsed["error"], ensure_ascii=False))
        result = parsed.get("result")
        if not isinstance(result, Mapping):
            raise McpSmokeError("MCP response is missing result")
        error = response_error(result)
        if error:
            raise McpSmokeError(error)
        return result

    def notify(self, method: str) -> None:
        self.post({"jsonrpc": "2.0", "method": method})


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mcp-url", default=DEFAULT_MCP_URL)
    args = parser.parse_args()
    client = McpSmokeClient(args.mcp_url)
    client.request("initialize", {
        "protocolVersion": PROTOCOL_VERSION,
        "capabilities": {},
        "clientInfo": {"name": "openfin-mcp-smoke", "version": "1.0"},
    })
    client.notify("notifications/initialized")
    listed = client.request("tools/list")
    tools = listed.get("tools")
    names = {
        name
        for tool in tools
        if isinstance(tool, Mapping) and isinstance(name := tool.get("name"), str)
    } if isinstance(tools, list) else set()
    missing = {"search", "fetch", "discover", "compare", "recommend"} - names
    if missing:
        raise McpSmokeError(f"MCP tools/list is missing required tools: {sorted(missing)}")
    for label, arguments in SMOKE_CALLS:
        name = "discover" if label.startswith("discover") else "search" if label in {"support_search", "search_insurance_tax"} else "compare" if label == "compare_saving" else label
        result = client.request("tools/call", {"name": name, "arguments": arguments})
        validate_tool_payload(label, tool_payload(result))
        print(f"PASS {label}")
    print(f"OK: Finance MCP smoke passed ({args.mcp_url})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
