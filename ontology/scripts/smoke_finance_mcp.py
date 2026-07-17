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
    ("search", {"query": "월세 세액공제 조건", "limit": 1}),
    ("fetch", {"id": "credit.monthly-rent"}),
    ("discover", {"query": "실손보험 추천", "limit": 1}),
    ("compare", {"domain": "deposit", "deposit_amount_krw": 10_000_000, "term_months": 12}),
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
    missing = {name for name, _ in SMOKE_CALLS} - names
    if missing:
        raise McpSmokeError(f"MCP tools/list is missing required tools: {sorted(missing)}")
    for name, arguments in SMOKE_CALLS:
        client.request("tools/call", {"name": name, "arguments": arguments})
        print(f"PASS {name}")
    print(f"OK: Finance MCP smoke passed ({args.mcp_url})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
