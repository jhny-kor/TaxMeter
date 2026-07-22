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
from search_index_loader import load_search_index_payload  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[2]
REGRESSION_REPORT = REPO_ROOT / "ontology/exports/openfin-search-regression-report-2026.json"
QUALITY_MANIFEST = REPO_ROOT / "ontology/exports/openfin-quality-manifest-2026.json"
LIVE_REPORTS = tuple(REPO_ROOT / f"ontology/exports/{name}" for name in (
    "openfin-semantic-duplicate-report-2026.json",
    "openfin-comparison-regression-report-2026.json",
    "openfin-recommendation-safety-report-2026.json",
    "openfin-support-relevance-report-2026.json",
    "openfin-local-cloudflare-parity-report-2026.json",
))
DOCS_ROOT = REPO_ROOT / "docs/opentax"
SEARCH_INDEX = REPO_ROOT / "ontology/exports/finance-search-index-2026.json"
DEFAULT_MCP_URL = "https://finance-mcp.y2kthr.workers.dev/mcp"
PROTOCOL_VERSION = "2025-03-26"
LIVE_DISCOVERY_CASES = (
    {"query": "마일리지 체크카드 추천", "kind": "check-card", "exact": ["product_kind", "마일리지"]},
    {"query": "대한항공 SKYPASS 체크카드 추천", "kind": "check-card", "exact": ["product_kind", "대한항공", "SKYPASS"], "first_exact_title": "광주은행 대한항공 SKYPASS 체크카드"},
    {"query": "전월실적 없는 체크카드 추천", "kind": "check-card", "exact": ["product_kind", "previous_month_spend_min_krw"], "partial": "previous_month_spend_min_krw"},
    {"query": "구독 할인 체크카드 추천", "kind": "check-card", "exact": ["product_kind", "benefit_category"]},
    {"query": "직장인 신용대출 추천", "kind": "credit-loan", "exact": ["product_kind", "employment_type"]},
    {"query": "청년 전세대출 추천", "kinds": ["policy-loan", "rent-loan"], "exact": ["product_kind", "청년"]},
    {"query": "암보험 추천", "kind": "cancer", "exact": ["product_kind"]},
    {"query": "비갱신 암보험 추천", "kind": "cancer", "exact": ["product_kind", "renewal_type"]},
    {"query": "실손보험 추천", "kind": "indemnity-health", "exact": ["product_kind"]},
    {"query": "갱신형 실손보험 추천", "kind": "indemnity-health", "exact": ["product_kind", "renewal_type"]},
    {"query": "12개월 정기예금 추천", "kind": "deposit", "exact": ["product_kind", "term_months"]},
    {"query": "월 30만원 적금 추천", "kind": "saving", "exact": ["product_kind", "monthly_payment_krw"]},
    {"query": "자유적립식 적금 추천", "kind": "saving", "exact": ["product_kind", "saving_method"]},
)
LIVE_COMPARISON_CASES = (
    {"query": "1천만원 12개월 예금 비교", "arguments": {"domain": "deposit", "deposit_amount_krw": 10_000_000, "term_months": 12}, "allow_empty_blocked": True},
)
LIVE_PRODUCT_DISCOVERY_CASES = (
    ("국민행복 삼성체크카드", "삼성카드 국민행복 삼성체크카드 V2"),
    ("삼성카드 국민행복 체크카드 V2", "삼성카드 국민행복 삼성체크카드 V2"),
    ("페이북 머니 체크카드", "BC바로카드 페이북 머니 체크카드"),
    ("신한 SOL트래블 체크카드", "신한카드 신한카드 SOL트래블 체크"),
    ("KB 노리2 체크카드", "KB국민카드 노리2(Global)체크카드"),
    ("롯데 LIKIT ON 체크카드", "롯데카드 LIKIT ON 체크카드"),
)


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
        result = self.tool_call("search", arguments)
        structured = result.get("structuredContent")
        if not structured:
            structured = json.loads(result["content"][0]["text"])
        return structured.get("results") or []

    def tool_call(self, name: str, arguments: dict, attempts: int = 6) -> dict:
        for attempt in range(attempts):
            try:
                result = self.request("tools/call", {"name": name, "arguments": arguments})
                serialized = json.dumps(result, ensure_ascii=False)
                if result.get("isError") is True or result.get("is_error") is True or "TypeError" in serialized:
                    raise ValueError(f"{name} returned an MCP error or TypeError: {serialized[:500]}")
                return result
            except urllib.error.HTTPError as error:
                if error.code < 500 or attempt == attempts - 1:
                    raise
            except ValueError as error:
                if "응답이 비어 있습니다" not in str(error) or attempt == attempts - 1:
                    raise
            self.session_id = None
            time.sleep(3 * (attempt + 1))
            self.initialize()
        raise AssertionError("unreachable")

    def discover(self, query: str, limit: int = 10) -> dict:
        result = self.tool_call("discover", {"query": query, "limit": limit})
        structured = result.get("structuredContent")
        return structured or json.loads(result["content"][0]["text"])

    def compare(self, arguments: dict) -> dict:
        result = self.tool_call("compare", arguments)
        structured = result.get("structuredContent")
        return structured or json.loads(result["content"][0]["text"])

    def fetch(self, item_id: str) -> dict:
        result = self.tool_call("fetch", {"id": item_id})
        structured = result.get("structuredContent")
        return structured or json.loads(result["content"][0]["text"])

    def recommend(self, arguments: dict) -> dict:
        result = self.tool_call("recommend", arguments)
        structured = result.get("structuredContent")
        return structured or json.loads(result["content"][0]["text"])

    def support_search(self, arguments: dict) -> dict:
        result = self.tool_call("search", arguments)
        structured = result.get("structuredContent")
        return structured or json.loads(result["content"][0]["text"])

    def exports(self) -> dict:
        result = self.tool_call("exports", {})
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
    for path in (REGRESSION_REPORT, QUALITY_MANIFEST, *LIVE_REPORTS):
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
    search_index = load_search_index_payload(SEARCH_INDEX)
    expected_checksum = search_index.get("export_checksum")
    runtime_exports = client.exports()
    actual_checksum = (runtime_exports.get("search_index") or {}).get("export_checksum")
    checksum_passed = actual_checksum == expected_checksum
    tests.append({
        "query": "runtime search-index checksum",
        "type": None,
        "validation_kind": "runtime_search_index_checksum",
        "expected_top_id": expected_checksum,
        "actual_top_id": actual_checksum,
        "passed": checksum_passed,
    })
    print(f"[{'PASS' if checksum_passed else 'FAIL'}] runtime search-index checksum expected={expected_checksum} actual={actual_checksum}")
    required_cases: list[dict] = []

    def record_required_case(query: str, validation_kind: str, passed: bool, actual: dict, error_text: str | None = None) -> None:
        test = {
            "query": query,
            "type": None,
            "validation_kind": validation_kind,
            "expected_top_id": None,
            "actual_top_id": None,
            "passed": passed,
            "payload_summary": actual,
        }
        if error_text:
            test["error"] = error_text
        required_cases.append(test)
        print(f"[{'PASS' if passed else 'FAIL'}] required {validation_kind} query={query!r}" + (f" error={error_text}" if error_text else ""))

    record_required_case("exports", "required_live_exports_contract", checksum_passed and bool(runtime_exports.get("runtime")), {"search_index": runtime_exports.get("search_index"), "runtime": runtime_exports.get("runtime")})

    try:
        fetched = client.fetch("credit.insurance-premium")
        fetched_item = fetched.get("item") or fetched.get("result") or (fetched if fetched.get("id") else {})
        fetch_ok = bool(fetched_item) and fetched.get("found", True) is not False
        record_required_case("credit.insurance-premium", "required_live_fetch_contract", fetch_ok, {
            "found": fetched.get("found"),
            "item_id": fetched_item.get("id") if isinstance(fetched_item, dict) else None,
        })
    except (urllib.error.HTTPError, urllib.error.URLError, ValueError, KeyError) as error:
        record_required_case("credit.insurance-premium", "required_live_fetch_contract", False, {}, str(error))

    try:
        support = client.support_search({"query": "청년 월세 지원", "type": "support-program", "region": "서울", "limit": 5})
        parsed_query = support.get("parsed_query") or {}
        exact = support.get("exact_results") or []
        partial = support.get("partial_results") or []
        related = support.get("related_results") or []
        support_ok = (
            parsed_query.get("intent") == "find-support"
            and parsed_query.get("region") == "서울특별시"
            and "youth" in (parsed_query.get("target_groups") or [])
            and {"housing", "rent"}.issubset(set(parsed_query.get("support_categories") or []))
            and isinstance(support.get("excluded_summary"), dict)
            and bool(exact or partial or related)
            and all(candidate.get("type") == "support-program" for candidate in [*exact, *partial, *related])
        )
        record_required_case("청년 월세 지원", "required_live_support_search_contract", support_ok, {
            "parsed_query": parsed_query,
            "exact_count": len(exact),
            "partial_count": len(partial),
            "related_count": len(related),
            "excluded_summary": support.get("excluded_summary"),
        })
    except (urllib.error.HTTPError, urllib.error.URLError, ValueError, KeyError) as error:
        record_required_case("청년 월세 지원", "required_live_support_search_contract", False, {}, str(error))

    try:
        tax_results = client.search("보험료 세액공제", "tax", limit=5)
        tax_ok = bool(tax_results) and all(result.get("type") in {"tax", "tax-credit", "deduction", "tax-reduction", "official-tax-item"} for result in tax_results)
        record_required_case("보험료 세액공제", "required_live_tax_search_contract", tax_ok, {"result_count": len(tax_results), "top": tax_results[:3]})
    except (urllib.error.HTTPError, urllib.error.URLError, ValueError, KeyError) as error:
        record_required_case("보험료 세액공제", "required_live_tax_search_contract", False, {}, str(error))

    try:
        open_support = client.support_search({"query": "서울 청년 월세 지원", "type": "support-program", "region": "서울", "application_status": "open", "limit": 5})
        open_results = [*(open_support.get("exact_results") or []), *(open_support.get("partial_results") or []), *(open_support.get("related_results") or [])]
        open_support_ok = bool(open_results) and all(result.get("type") == "support-program" for result in open_results)
        record_required_case("서울·open 청년 월세 지원", "required_live_open_support_search_contract", open_support_ok, {"result_count": len(open_results), "parsed_query": open_support.get("parsed_query"), "excluded_summary": open_support.get("excluded_summary")})
    except (urllib.error.HTTPError, urllib.error.URLError, ValueError, KeyError) as error:
        record_required_case("서울·open 청년 월세 지원", "required_live_open_support_search_contract", False, {}, str(error))

    for query, expected_title in LIVE_PRODUCT_DISCOVERY_CASES:
        try:
            discovery = client.discover(query, limit=10)
            exact = discovery.get("exact_candidates") or []
            exact_titles = [candidate.get("title") for candidate in exact]
            product_ok = bool(exact) and exact[0].get("title") == expected_title and len({candidate.get("canonical_product_id") for candidate in exact if candidate.get("canonical_product_id")}) == len([candidate for candidate in exact if candidate.get("canonical_product_id")])
            record_required_case(query, "required_live_product_name_discovery", product_ok, {"expected_title": expected_title, "exact_titles": exact_titles[:5], "parsed_query": discovery.get("parsed_query")})
        except (urllib.error.HTTPError, urllib.error.URLError, ValueError, KeyError) as error:
            record_required_case(query, "required_live_product_name_discovery", False, {}, str(error))

    try:
        saving = client.compare({"domain": "saving", "monthly_payment_krw": 300_000, "term_months": 12, "saving_method": "free"})
        candidates = saving.get("candidates") or []
        excluded = saving.get("excluded_summary") or {}
        excluded_count = saving.get("excluded_count")
        saving_ok = (
            isinstance(excluded, dict)
            and isinstance(excluded_count, int)
            and sum(value for value in excluded.values() if isinstance(value, int)) == excluded_count
            and all(candidate.get("term_months") == 12 for candidate in candidates)
        )
        record_required_case("300,000원 자유적립식 12개월 적금 비교", "required_live_saving_comparison_contract", saving_ok, {
            "candidate_count": len(candidates),
            "excluded_count": excluded_count,
            "excluded_summary": excluded,
        })
    except (urllib.error.HTTPError, urllib.error.URLError, ValueError, KeyError) as error:
        record_required_case("300,000원 자유적립식 12개월 적금 비교", "required_live_saving_comparison_contract", False, {}, str(error))

    try:
        deposit = client.compare({"domain": "deposit", "deposit_amount_krw": 10_000_000, "term_months": 12})
        deposit_excluded = deposit.get("excluded_summary") or {}
        deposit_ok = (
            sum(value for value in deposit_excluded.values() if isinstance(value, int)) == deposit.get("excluded_count")
            and deposit.get("candidate_count", 0) + deposit.get("excluded_count", 0) == deposit.get("comparison_target_count")
            and deposit.get("latest_product_collection_date") == deposit.get("verification_basis_date")
        )
        record_required_case("1,000만원 12개월 예금 비교", "required_live_deposit_comparison_contract", deposit_ok, {"candidate_count": deposit.get("candidate_count"), "result_count": deposit.get("result_count"), "excluded_count": deposit.get("excluded_count"), "comparison_target_count": deposit.get("comparison_target_count"), "excluded_summary": deposit_excluded, "latest_product_collection_date": deposit.get("latest_product_collection_date"), "verification_basis_date": deposit.get("verification_basis_date")})
    except (urllib.error.HTTPError, urllib.error.URLError, ValueError, KeyError) as error:
        record_required_case("1,000만원 12개월 예금 비교", "required_live_deposit_comparison_contract", False, {}, str(error))

    try:
        recommendation = client.recommend({
            "domain": "deposit",
            "profile": {"deposit_amount_krw": 10_000_000, "term_months": 12},
            "constraints": {"term_months": 12},
            "limit": 1,
        })
        readiness = recommendation.get("readiness") or {}
        actions = recommendation.get("next_required_actions") or []
        action_codes = {action.get("code") for action in actions if isinstance(action, dict)}
        recommendation_ok = (
            recommendation.get("result_count") == 0
            and readiness.get("comparison_engine_product_count", 0) > 0
            and "VERIFY_RECOMMENDATION_FIELDS" in action_codes
        )
        record_required_case("10,000,000원 12개월 예금 추천", "required_live_recommendation_contract", recommendation_ok, {
            "result_count": recommendation.get("result_count"),
            "readiness": readiness,
            "next_required_actions": actions,
        })
    except (urllib.error.HTTPError, urllib.error.URLError, ValueError, KeyError) as error:
        record_required_case("10,000,000원 12개월 예금 추천", "required_live_recommendation_contract", False, {}, str(error))

    tests.extend(required_cases)
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
            results = [*(discovery.get("exact_candidates") or []), *(discovery.get("partial_candidates") or [])]
            actual_id = results[0].get("id") if results else None
            candidate_only = bool(results) and all(
                item.get("decision", {}).get("decision_scope") == "discovery_only"
                and item.get("catalog_recommendation_status") != "discovery_candidate"
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

    for regression in LIVE_DISCOVERY_CASES:
        query = str(regression["query"])
        error_text = None
        allowed_kinds = set(regression.get("kinds") or [regression["kind"]])
        exact: list[dict] = []
        partial: list[dict] = []
        all_candidates: list[dict] = []
        try:
            discovery = client.discover(query)
            exact = discovery.get("exact_candidates") or []
            partial = discovery.get("partial_candidates") or []
            all_candidates = [*exact, *partial, *(discovery.get("related_candidates") or [])]
            required_exact = set(regression.get("exact") or [])
            exact_ok = bool(exact) and all(
                candidate.get("product_kind") in allowed_kinds
                and required_exact.issubset(set(candidate.get("matched_constraints") or []))
                and not candidate.get("unknown_constraints")
                and not candidate.get("failed_constraints")
                for candidate in exact
            )
            first_exact_title = regression.get("first_exact_title")
            first_exact_ok = not first_exact_title or bool(exact) and exact[0].get("title") == first_exact_title
            partial_field = regression.get("partial")
            partial_ok = bool(partial_field) and any(
                candidate.get("product_kind") in allowed_kinds and partial_field in (candidate.get("unknown_constraints") or [])
                for candidate in partial
            ) if partial_field else True
            fields_present = all(
                key in discovery for key in ("parsed_query", "exact_candidates", "partial_candidates", "related_candidates")
            )
            actual_id = (exact or partial or all_candidates)[0].get("id") if (exact or partial or all_candidates) else None
            passed = fields_present and exact_ok and first_exact_ok and partial_ok
        except (urllib.error.HTTPError, urllib.error.URLError, ValueError) as error:
            discovery = {}
            exact = partial = []
            actual_id = None
            passed = False
            error_text = str(error)
        test = {
            "query": query,
            "type": None,
            "validation_kind": "required_live_discovery_contract",
            "expected_top_id": None,
            "actual_top_id": actual_id,
            "expected_product_kinds": sorted(allowed_kinds),
            "required_exact_constraints": sorted(regression.get("exact") or []),
            "required_partial_disclosure": regression.get("partial"),
            "parsed_query": discovery.get("parsed_query"),
            "exact_candidates": exact[:5],
            "partial_candidates": partial[:5],
            "related_candidates": (discovery.get("related_candidates") or [])[:5],
            "candidate_counts": {"exact": len(exact), "partial": len(partial), "related": len(discovery.get("related_candidates") or [])},
            "top5_product_kinds": {
                "exact": [candidate.get("product_kind") for candidate in exact[:5]],
                "partial": [candidate.get("product_kind") for candidate in partial[:5]],
                "related": [candidate.get("product_kind") for candidate in (discovery.get("related_candidates") or [])[:5]],
            },
            "duplicate_canonical_product_ids": len({candidate.get("canonical_product_id") for candidate in all_candidates if candidate.get("canonical_product_id")}) != len([candidate for candidate in all_candidates if candidate.get("canonical_product_id")]),
            "candidate_grades": [{"id": candidate.get("id"), "relevance_grade": candidate.get("relevance_grade"), "verification_grade": candidate.get("verification_grade"), "overall_candidate_grade": candidate.get("overall_candidate_grade")} for candidate in all_candidates[:5]],
            "passed": passed,
        }
        if error_text:
            test["error"] = error_text
        tests.append(test)
        print(f"[{'PASS' if passed else 'FAIL'}] required discovery query={query!r} actual={actual_id}" + (f" error={error_text}" if error_text else ""))
        time.sleep(1)

    for regression in LIVE_COMPARISON_CASES:
        query = str(regression["query"])
        error_text = None
        try:
            comparison = client.compare(dict(regression["arguments"]))
            candidates = comparison.get("candidates") or []
            actual_id = candidates[0].get("item_id") if candidates else None
            deposit_amount = regression["arguments"].get("deposit_amount_krw")
            candidates_ok = bool(candidates) and all(
                candidate.get("term_months") == regression["arguments"]["term_months"]
                and (deposit_amount is None or candidate.get("deposit_limit") is None or candidate.get("deposit_limit") >= deposit_amount)
                for candidate in candidates
            )
            blocked = comparison.get("excluded_sample") or []
            passed = candidates_ok or bool(regression.get("allow_empty_blocked")) and not candidates and bool(blocked)
        except (urllib.error.HTTPError, urllib.error.URLError, ValueError) as error:
            comparison = {}
            candidates = []
            actual_id = None
            passed = False
            error_text = str(error)
        test = {
            "query": query,
            "type": None,
            "validation_kind": "required_live_comparison_contract",
            "expected_top_id": None,
            "actual_top_id": actual_id,
            "comparison_arguments": regression["arguments"],
            "parsed_query": {"original_query": query, "domain": regression["arguments"]["domain"], "hard_constraints": regression["arguments"]},
            "candidates": candidates[:5],
            "excluded_sample": blocked[:10],
            "excluded_count": comparison.get("excluded_count"),
            "excluded_summary": comparison.get("excluded_summary") or {},
            "safe_empty_blocked": bool(regression.get("allow_empty_blocked")) and not candidates and bool(blocked),
            "candidate_count": len(candidates),
            "top5_product_kinds": [candidate.get("product_kind") for candidate in candidates[:5]],
            "duplicate_product_ids": len({candidate.get("item_id") for candidate in candidates if candidate.get("item_id")}) != len([candidate for candidate in candidates if candidate.get("item_id")]),
            "passed": passed,
        }
        if error_text:
            test["error"] = error_text
        tests.append(test)
        print(f"[{'PASS' if passed else 'FAIL'}] required comparison query={query!r} actual={actual_id}" + (f" error={error_text}" if error_text else ""))
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
    summary = {
        "mcp_url": args.mcp_url,
        "live_status": "executed",
        "live_not_executed_reason": None,
        "checked_at": checked_at,
        "runtime_version": (runtime_exports.get("runtime") or {}).get("runtime_version"),
        "deployment_commit": (runtime_exports.get("runtime") or {}).get("deployment_commit"),
        "manifest_version": (runtime_exports.get("runtime") or {}).get("manifest_version"),
        "search_index_version": search_index.get("version"),
        "search_index_checksum": search_index.get("export_checksum"),
        "runtime_search_index_checksum": actual_checksum,
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
        for path in LIVE_REPORTS:
            rewrite_with_checksum(path, lambda payload: payload.update({
                "live_tested_at": checked_at,
                "live_status": "executed",
                "live_not_executed_reason": None,
                "runtime_version": runtime_exports.get("runtime", {}).get("runtime_version"),
                "deployment_commit": runtime_exports.get("runtime", {}).get("deployment_commit"),
                "manifest_version": runtime_exports.get("runtime", {}).get("manifest_version"),
                "live_case_count": len(tests),
                "live_passed_count": len(tests) - len(failures),
                "live_failed_count": len(failures),
                "live_failures": failures,
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
