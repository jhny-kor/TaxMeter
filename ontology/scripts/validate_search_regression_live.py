"""배포된 OpenFin MCP 워커(finance-mcp)에 실제 search 호출을 보내 회귀를 검증한다.

export 생성 단계의 오프라인 회귀와 달리, 라이브 워커 + 발행된 검색 인덱스 조합이
실제로 기대 결과를 반환하는지 type 파라미터 포함 케이스까지 1위 id 기준으로 확인한다.
결과는 openfin-search-regression-report-2026.json의 live_tests와
openfin-quality-manifest-2026.json의 live_search_regression에 기록한다.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_finance_ontology import (  # noqa: E402
    COMPARISON_SEARCH_REGRESSIONS,
    DISCOVERY_SEARCH_REGRESSIONS,
    RECOMMENDATION_SEARCH_REGRESSIONS,
    TAX_SEARCH_REGRESSIONS,
    payload_checksum,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
REGRESSION_REPORT = REPO_ROOT / "ontology/exports/openfin-search-regression-report-2026.json"
QUALITY_MANIFEST = REPO_ROOT / "ontology/exports/openfin-quality-manifest-2026.json"
DOCS_ROOT = REPO_ROOT / "docs/opentax"
SEARCH_INDEX = REPO_ROOT / "ontology/exports/finance-search-index-2026.json"
DEFAULT_MCP_URL = "https://finance-mcp.y2kthr.workers.dev/mcp"
PROTOCOL_VERSION = "2025-03-26"


def parse_mcp_response(body: str) -> dict:
    """streamable HTTP 응답은 SSE(text/event-stream) 또는 순수 JSON일 수 있다."""
    text = body.strip()
    if text.startswith("{"):
        return json.loads(text)
    for line in text.splitlines():
        if line.startswith("data:"):
            return json.loads(line[len("data:"):].strip())
    raise ValueError(f"MCP 응답을 해석할 수 없습니다: {text[:200]}")


class McpClient:
    def __init__(self, url: str):
        self.url = url
        self.session_id: str | None = None
        self._next_id = 0

    def _post(self, payload: dict) -> tuple[dict | None, dict]:
        headers = {
            "content-type": "application/json",
            "accept": "application/json, text/event-stream",
            # Cloudflare가 기본 Python-urllib UA를 403으로 차단한다.
            "user-agent": "openfin-live-regression/1.0",
        }
        if self.session_id:
            headers["mcp-session-id"] = self.session_id
        request = urllib.request.Request(self.url, data=json.dumps(payload).encode("utf-8"), headers=headers)
        attempts = 6
        for attempt in range(attempts):
            try:
                with urllib.request.urlopen(request, timeout=60) as response:
                    session_id = response.headers.get("mcp-session-id")
                    if session_id:
                        self.session_id = session_id
                    body = response.read().decode("utf-8")
                return (parse_mcp_response(body) if body.strip() else None), dict()
            except urllib.error.HTTPError as error:
                # 워커가 대용량 인덱스를 다시 적재할 때 간헐적으로 5xx를 반환한다.
                if error.code < 500 or attempt == attempts - 1:
                    raise
                time.sleep(3 * (attempt + 1))
        raise AssertionError("unreachable")

    def request(self, method: str, params: dict | None = None) -> dict:
        self._next_id += 1
        payload = {"jsonrpc": "2.0", "id": self._next_id, "method": method}
        if params is not None:
            payload["params"] = params
        parsed, _ = self._post(payload)
        if parsed is None:
            raise ValueError(f"{method} 응답이 비어 있습니다.")
        if "error" in parsed:
            raise ValueError(f"{method} 오류: {parsed['error']}")
        return parsed["result"]

    def notify(self, method: str) -> None:
        self._post({"jsonrpc": "2.0", "method": method})

    def initialize(self) -> None:
        self.request("initialize", {
            "protocolVersion": PROTOCOL_VERSION,
            "capabilities": {},
            "clientInfo": {"name": "validate-search-regression-live", "version": "1.0"},
        })
        self.notify("notifications/initialized")

    def search(self, query: str, type_filter: str | None, limit: int = 5) -> list[dict]:
        arguments: dict = {"query": query, "limit": limit}
        if type_filter:
            arguments["type"] = type_filter
        result = None
        for attempt in range(3):
            try:
                result = self.request("tools/call", {"name": "search", "arguments": arguments})
                break
            except urllib.error.HTTPError as error:
                if error.code < 500 or attempt == 2:
                    raise
                self.session_id = None
                time.sleep(10 * (attempt + 1))
                self.initialize()
            except ValueError as error:
                if "응답이 비어 있습니다" not in str(error) or attempt == 2:
                    raise
                self.session_id = None
                time.sleep(10 * (attempt + 1))
                self.initialize()
        if result is None:
            raise AssertionError("unreachable")
        structured = result.get("structuredContent")
        if not structured:
            structured = json.loads(result["content"][0]["text"])
        return structured.get("results") or []

    def discover(self, query: str, limit: int = 10) -> dict:
        result = self.request("tools/call", {"name": "discover", "arguments": {"query": query, "limit": limit}})
        structured = result.get("structuredContent")
        return structured or json.loads(result["content"][0]["text"])


def rewrite_with_checksum(path: Path, mutate) -> None:
    payload = json.loads(path.read_text(encoding="utf-8"))
    payload.pop("export_checksum", None)
    mutate(payload)
    payload["export_checksum"] = payload_checksum(payload)
    indent = None if path.name.startswith("finance-search-index") else 2
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=indent) + "\n", encoding="utf-8")


def mirror_live_reports() -> None:
    for path in (REGRESSION_REPORT, QUALITY_MANIFEST):
        (DOCS_ROOT / path.name).write_text(path.read_text(encoding="utf-8"), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mcp-url", default=DEFAULT_MCP_URL)
    parser.add_argument("--no-write", action="store_true", help="리포트/manifest 파일을 갱신하지 않고 검증만 한다.")
    args = parser.parse_args()

    client = McpClient(args.mcp_url)
    client.initialize()

    checked_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
    tests = []
    for query, expected_id, type_filter in TAX_SEARCH_REGRESSIONS:
        error_text = None
        try:
            results = client.search(query, type_filter)
            actual_id = results[0]["id"] if results else None
        except (urllib.error.HTTPError, urllib.error.URLError, ValueError) as error:
            actual_id = None
            error_text = str(error)
        passed = actual_id == expected_id
        status = "PASS" if passed else "FAIL"
        print(f"[{status}] type={type_filter} query={query!r} expected={expected_id} actual={actual_id}"
              + (f" error={error_text}" if error_text else ""))
        test = {
            "query": query,
            "type": type_filter,
            "expected_top_id": expected_id,
            "actual_top_id": actual_id,
            "passed": passed,
        }
        if error_text:
            test["error"] = error_text
        tests.append(test)
        time.sleep(1)

    for regression in RECOMMENDATION_SEARCH_REGRESSIONS:
        query = str(regression["query"])
        expected_id = str(regression["expected_top_id"])
        expected_type = str(regression["expected_type"])
        error_text = None
        try:
            results = client.search(query, None, limit=10)
            actual_id = results[0]["id"] if results else None
            candidate_only = bool(results) and all(
                item.get("recommendation_status") == "verified_recommendation_candidate"
                for item in results
            )
            expected_type_present = any(item.get("type") == expected_type for item in results)
        except (urllib.error.HTTPError, urllib.error.URLError, ValueError) as error:
            results = []
            actual_id = None
            candidate_only = False
            expected_type_present = False
            error_text = str(error)
        passed = actual_id == expected_id and candidate_only and expected_type_present
        status = "PASS" if passed else "FAIL"
        print(
            f"[{status}] recommendation query={query!r} expected={expected_id} actual={actual_id} "
            f"candidate_only={candidate_only}" + (f" error={error_text}" if error_text else "")
        )
        test = {
            "query": query,
            "type": None,
            "validation_kind": "verified_recommendation_candidate_only",
            "expected_top_id": expected_id,
            "actual_top_id": actual_id,
            "passed": passed,
            "verified_recommendation_candidates_only": candidate_only,
        }
        if error_text:
            test["error"] = error_text
        tests.append(test)
        time.sleep(1)

    for regression in DISCOVERY_SEARCH_REGRESSIONS:
        query = str(regression["query"])
        expected_search_type = str(regression["expected_search_type"])
        error_text = None
        try:
            discovery = client.discover(query)
            results = discovery.get("candidates") or []
            actual_id = results[0].get("id") if results else None
            candidate_only = bool(results) and all(
                item.get("recommendation_status") == "discovery_candidate"
                and item.get("recommendation_scope") == "discovery_only"
                and item.get("search_type") == expected_search_type
                for item in results
            )
        except (urllib.error.HTTPError, urllib.error.URLError, ValueError) as error:
            results = []
            actual_id = None
            candidate_only = False
            error_text = str(error)
        passed = candidate_only
        status = "PASS" if passed else "FAIL"
        print(
            f"[{status}] discovery query={query!r} expected_type={expected_search_type} actual={actual_id}"
            + (f" error={error_text}" if error_text else "")
        )
        test = {
            "query": query,
            "type": None,
            "validation_kind": "discovery_candidate_only",
            "expected_top_id": None,
            "actual_top_id": actual_id,
            "expected_search_type": expected_search_type,
            "discovery_candidates_only": candidate_only,
            "passed": passed,
        }
        if error_text:
            test["error"] = error_text
        tests.append(test)
        time.sleep(1)

    for regression in COMPARISON_SEARCH_REGRESSIONS:
        query = str(regression["query"])
        expected_search_type = str(regression["expected_search_type"])
        error_text = None
        try:
            results = client.search(query, None, limit=10)
            actual_id = results[0]["id"] if results else None
            actual_search_type = results[0].get("search_type") if results else None
        except (urllib.error.HTTPError, urllib.error.URLError, ValueError) as error:
            actual_id = None
            actual_search_type = None
            error_text = str(error)
        passed = actual_search_type == expected_search_type
        status = "PASS" if passed else "FAIL"
        print(
            f"[{status}] comparison query={query!r} expected_type={expected_search_type} "
            f"actual_type={actual_search_type}" + (f" error={error_text}" if error_text else "")
        )
        test = {
            "query": query,
            "type": None,
            "validation_kind": "comparison_search_type",
            "expected_top_id": None,
            "actual_top_id": actual_id,
            "expected_search_type": expected_search_type,
            "actual_search_type": actual_search_type,
            "passed": passed,
        }
        if error_text:
            test["error"] = error_text
        tests.append(test)
        time.sleep(1)

    failures = [
        {"query": t["query"], "type": t["type"], "expected": t["expected_top_id"], "actual": t["actual_top_id"]}
        for t in tests
        if not t["passed"]
    ]
    search_index = json.loads(SEARCH_INDEX.read_text(encoding="utf-8"))
    summary = {
        "mcp_url": args.mcp_url,
        "checked_at": checked_at,
        "search_index_version": search_index.get("version"),
        "search_index_checksum": search_index.get("export_checksum"),
        "test_count": len(tests),
        "passed_count": len(tests) - len(failures),
        "failed_count": len(failures),
        "failures": failures,
        "last_failed_at": checked_at if failures else None,
    }

    if not args.no_write:
        rewrite_with_checksum(REGRESSION_REPORT, lambda payload: payload.update({
            "live_tests": tests,
            "live_summary": summary,
        }))
        rewrite_with_checksum(QUALITY_MANIFEST, lambda payload: payload.update({
            "live_search_regression": summary,
        }))
        mirror_live_reports()
        print(f"라이브 결과를 기록했습니다: {REGRESSION_REPORT.name}, {QUALITY_MANIFEST.name}")

    if failures:
        print(f"FAILED: {len(failures)}/{len(tests)} live queries")
        return 1
    print(f"OK: {len(tests)} live queries all pass ({args.mcp_url})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
