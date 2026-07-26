#!/usr/bin/env python3
"""Run the exact OpenFin 120-case JSONL suite offline or against the MCP endpoint.

The live mode deliberately treats an unavailable tool, an empty run, or an
unexpected exception as a failure.  Fixture output is never substituted for
live output.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import sys
import time
from typing import Any
import urllib.error
import urllib.request


REPO_ROOT = Path(__file__).resolve().parents[2]
GOLDEN = REPO_ROOT / "tests" / "golden" / "openfin-120.jsonl"
DEFAULT_REPORT = REPO_ROOT / "quality" / "openfin-live-report.json"
CATEGORY_COUNTS = {
    "exact_product": 30,
    "alias_ambiguity": 20,
    "comparison": 20,
    "support": 20,
    "personal_finance": 15,
    "stale_conflict": 10,
    "security_auth": 5,
}
SAFETY_FIELDS = (
    "mode",
    "status",
    "reason_codes",
    "profile_as_of",
    "data_as_of",
    "assumptions",
    "missing_information",
    "financial_needs",
    "candidates",
    "decision_owner",
    "limitations",
    "audit_id",
)


def load_cases() -> list[dict[str, Any]]:
    cases: list[dict[str, Any]] = []
    for line_number, line in enumerate(GOLDEN.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            raise ValueError(f"blank or skipped case at line {line_number}")
        case = json.loads(line)
        if not isinstance(case, dict):
            raise ValueError(f"case at line {line_number} is not an object")
        cases.append(case)
    if len(cases) != 120:
        raise ValueError(f"expected exactly 120 cases, got {len(cases)}")
    if len({case.get("case_id") for case in cases}) != 120:
        raise ValueError("case_id values must be unique")
    counts: dict[str, int] = {}
    for case in cases:
        category = str(case.get("category") or "unknown")
        counts[category] = counts.get(category, 0) + 1
    if counts != CATEGORY_COUNTS:
        raise ValueError(f"category counts do not match: {counts}")
    return cases


def structured_payload(result: Any) -> Any:
    if isinstance(result, dict) and "structuredContent" in result:
        return result["structuredContent"]
    if isinstance(result, dict) and "content" in result and result["content"]:
        text = result["content"][0].get("text")
        if isinstance(text, str):
            return json.loads(text)
    return result


def search_results(payload: Any) -> list[dict[str, Any]]:
    if isinstance(payload, list):
        return [item for item in payload if isinstance(item, dict)]
    if isinstance(payload, dict):
        return [item for item in payload.get("results") or [] if isinstance(item, dict)]
    return []


def candidate_list(payload: dict[str, Any]) -> list[dict[str, Any]]:
    return [item for item in payload.get("candidates") or [] if isinstance(item, dict)]


def fast_live_client(url: str, timeout_seconds: float = 15.0, attempts: int = 2) -> Any:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from validate_search_regression_live import McpClient, parse_mcp_response

    class FastMcpClient(McpClient):
        def _post(self, payload: dict) -> tuple[dict | None, dict]:
            headers = {
                "content-type": "application/json",
                "accept": "application/json, text/event-stream",
                "user-agent": "openfin-120-live-regression/1.0",
            }
            if self.session_id:
                headers["mcp-session-id"] = self.session_id
            request = urllib.request.Request(self.url, data=json.dumps(payload).encode("utf-8"), headers=headers)
            with urllib.request.urlopen(request, timeout=timeout_seconds) as response:
                session_id = response.headers.get("mcp-session-id")
                if session_id:
                    self.session_id = session_id
                body = response.read().decode("utf-8")
            return (parse_mcp_response(body) if body.strip() else None), {}

        def tool_call(self, name: str, arguments: dict, attempts: int | None = None) -> dict:
            call_attempts = attempts if attempts is not None else max(1, self.live_attempts)
            last_error: Exception | None = None
            for attempt in range(call_attempts):
                try:
                    result = self.request("tools/call", {"name": name, "arguments": arguments})
                    serialized = json.dumps(result)
                    if result.get("isError") is True or result.get("is_error") is True or "TypeError" in serialized:
                        raise ValueError(f"{name} returned an MCP error or TypeError: {serialized[:500]}")
                    return result
                except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError, OSError, ValueError) as exc:
                    last_error = exc
                    self.session_id = None
                    if attempt + 1 < call_attempts:
                        time.sleep(min(3.0, 0.75 * (attempt + 1)))
                        try:
                            self.initialize()
                        except Exception as initialize_error:  # noqa: BLE001
                            last_error = initialize_error
            raise ValueError(f"{name} live call failed: {last_error}") from last_error

    client = FastMcpClient(url)
    client.live_attempts = max(1, attempts)
    return client


def check_case(case: dict[str, Any], payload: Any, error_text: str | None, mode: str) -> list[str]:
    assertions = case.get("assertions") or {}
    errors: list[str] = []
    expected_error = assertions.get("error_contains")
    if expected_error:
        if not error_text:
            return [f"expected an error containing {expected_error!r}"]
        if str(expected_error).casefold() not in error_text.casefold():
            return [f"error does not contain {expected_error!r}: {error_text[:240]}"]
        return []
    if error_text:
        return [f"unexpected tool error: {error_text[:300]}"]

    payload = structured_payload(payload)
    if not isinstance(payload, (dict, list)):
        return [f"tool returned neither an object nor a list: {type(payload).__name__}"]

    if case["tool"].endswith("search"):
        results = search_results(payload)
        kind = assertions.get("kind")
        explicit_exact = (
            isinstance(payload, dict)
            and (payload.get("resolution") or {}).get("status") == "exact"
        ) or any(item.get("resolution_status") == "exact" for item in results)
        if kind == "exact":
            if not explicit_exact:
                errors.append("named product was not resolved as exact")
            expected_title = assertions.get("expected_title")
            if expected_title and not any(item.get("title") == expected_title for item in results):
                errors.append(f"expected exact title is absent: {expected_title}")
        elif kind == "not_exact" and explicit_exact:
            errors.append("ambiguous or generic query was resolved as exact")
        if assertions.get("no_unrelated_insurance") and any(item.get("type") == "insurance-product" for item in results):
            errors.append("named card query returned an insurance product")
        if assertions.get("support_window"):
            if not results:
                errors.append("support query returned no result")
            allowed = {"fixed", "rolling", "until_budget_exhausted", "periodic", "tbd", "unknown"}
            for item in results:
                window = item.get("application_window")
                if not isinstance(window, dict):
                    errors.append(f"support result has no application_window: {item.get('id')}")
                    continue
                if window.get("kind") not in allowed:
                    errors.append(f"unsupported application_window kind: {window.get('kind')}")
                if window.get("kind") != "fixed" and (window.get("starts_at") or window.get("ends_at")):
                    errors.append(f"non-fixed support window contains fixed dates: {item.get('id')}")
    elif case["tool"].endswith("compare"):
        if not isinstance(payload, dict):
            errors.append("comparison response must be an object")
        else:
            for key in assertions.get("required_keys") or []:
                if key not in payload:
                    errors.append(f"comparison response missing {key}")
            if assertions.get("final_comparison_object"):
                basis = payload.get("comparison_basis") or {}
                if basis.get("candidate_values_are_from_final_object") is not True:
                    errors.append("comparison statistics are not tied to the final comparison object")
                for candidate in candidate_list(payload):
                    if candidate.get("comparison_object_version") is None:
                        errors.append(f"comparison candidate missing object version: {candidate.get('item_id')}")
                    if candidate.get("data_as_of") is None:
                        errors.append(f"comparison candidate missing data_as_of: {candidate.get('item_id')}")
    if isinstance(payload, dict):
        for key in assertions.get("required_keys") or []:
            if key not in payload:
                errors.append(f"response missing {key}")
        expected_status = assertions.get("status")
        if expected_status is not None and payload.get("status") != expected_status:
            errors.append(f"expected status {expected_status}, got {payload.get('status')}")
        if assertions.get("candidates_empty") and candidate_list(payload):
            errors.append("blocked response contains candidates")
        if assertions.get("decision_owner") and payload.get("decision_owner") != assertions["decision_owner"]:
            errors.append("decision owner mismatch")
        if assertions.get("decision_owner") is None and case["category"] in {"personal_finance", "security_auth"}:
            if "decision_owner" in payload and payload.get("decision_owner") != "user":
                errors.append("decision owner must be user")
        if assertions.get("need"):
            needs = {item.get("need_type") for item in payload.get("financial_needs") or [] if isinstance(item, dict)}
            if assertions["need"] not in needs:
                errors.append(f"financial need is absent: {assertions['need']}")
        if assertions.get("metric"):
            metric = (payload.get("metrics") or {}).get(assertions["metric"])
            if not isinstance(metric, dict):
                errors.append(f"metric is absent: {assertions['metric']}")
            elif "metric_value" in assertions and metric.get("value") != assertions["metric_value"]:
                errors.append(f"metric value mismatch: expected {assertions['metric_value']}, got {metric.get('value')}")
        if assertions.get("unknown") and assertions["unknown"] not in (payload.get("unknown_conditions") or payload.get("missing_information") or []):
            errors.append(f"unknown condition is absent: {assertions['unknown']}")
        if assertions.get("failed") and assertions["failed"] not in (payload.get("failed_conditions") or []):
            fit = payload.get("fit") or {}
            if assertions["failed"] not in (fit.get("failed_conditions") or []):
                errors.append(f"failed condition is absent: {assertions['failed']}")
        if assertions.get("decreasing_debt"):
            before = (payload.get("after") or {}).get("debt_balance_krw")
            after = (payload.get("before") or {}).get("debt_balance_krw")
            if not isinstance(before, (int, float)) or not isinstance(after, (int, float)) or before > after:
                errors.append("scenario did not reduce debt balance")
        if "valid" in assertions:
            validation = payload.get("validation") if isinstance(payload.get("validation"), dict) else payload
            if validation.get("valid") is not assertions["valid"]:
                errors.append(f"advice validity mismatch: expected {assertions['valid']}, got {validation.get('valid')}")
        if case["tool"].endswith("recommend") or case["category"] == "personal_finance" and case["tool"] == "opentax_recommend":
            missing_safety = [field for field in SAFETY_FIELDS if field not in payload]
            errors.extend(f"recommendation response missing {field}" for field in missing_safety)
    return sorted(set(errors))


def invoke_offline(case: dict[str, Any]) -> tuple[Any, str | None]:
    sys.path.insert(0, str(REPO_ROOT / "ontology"))
    import mcp_server

    try:
        return mcp_server.call_tool(case["tool"], case.get("arguments") or {}), None
    except Exception as exc:  # noqa: BLE001 - the case decides whether an error is expected.
        return None, f"{type(exc).__name__}: {exc}"


def invoke_live(client: Any, case: dict[str, Any]) -> tuple[Any, str | None]:
    name = {
        "opentax_search": "search",
        "opentax_compare": "compare",
        "opentax_recommend": "recommend",
    }.get(case["tool"], case["tool"])
    try:
        return client.tool_call(name, case.get("arguments") or {}), None
    except Exception as exc:  # noqa: BLE001 - recorded as a live failure unless explicitly expected.
        return None, f"{type(exc).__name__}: {exc}"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=("offline", "live"), default="offline")
    parser.add_argument("--mcp-url", default="https://finance-mcp.y2kthr.workers.dev/mcp")
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--live-timeout", type=float, default=15.0)
    parser.add_argument("--live-attempts", type=int, default=2)
    parser.add_argument("--live-new-session-per-case", action="store_true", help="Use a fresh MCP session per case when a public edge limits long-lived sessions.")
    parser.add_argument("--case-start", type=int, default=0, help="Zero-based inclusive case index for a bounded live chunk.")
    parser.add_argument("--case-end", type=int, default=None, help="Zero-based exclusive case index for a bounded live chunk.")
    parser.add_argument("--append-report", action="store_true", help="Merge this chunk into an existing live report by case id.")
    parser.add_argument("--merge-reports", type=Path, nargs="+", help="Merge independently collected chunk reports into --report without invoking MCP.")
    args = parser.parse_args()
    cases = load_cases()
    if args.merge_reports:
        merged: dict[str, dict[str, Any]] = {}
        runtime: dict[str, Any] = {}
        for report_path in args.merge_reports:
            if not report_path.exists():
                continue
            payload = json.loads(report_path.read_text(encoding="utf-8"))
            runtime = payload.get("runtime") or runtime
            for result in payload.get("case_results") or []:
                if result.get("case_id"):
                    merged[str(result["case_id"])] = result
        case_results = [merged[case["case_id"]] for case in cases if case["case_id"] in merged]
        failures = [result for result in case_results if result.get("errors")]
        report = {"report_version": "openfin-live-120-v1", "mode": "live", "checked_at": datetime.now(timezone.utc).isoformat(timespec="seconds"), "endpoint": args.mcp_url, "fixture": str(GOLDEN.relative_to(REPO_ROOT)), "runtime": runtime, "test_count": len(case_results), "passed_count": len(case_results) - len(failures), "failed_count": len(failures), "skipped_count": len(cases) - len(case_results), "failures": failures, "case_results": case_results, "category_counts": CATEGORY_COUNTS, "fixture_output_is_not_live_evidence": False}
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(json.dumps({key: report[key] for key in ("mode", "test_count", "passed_count", "failed_count", "skipped_count")}, ensure_ascii=False))
        return 0 if len(case_results) == len(cases) and not failures else 1
    client = None
    runtime: dict[str, Any] = {}
    if args.mode == "live":
        client = fast_live_client(args.mcp_url, timeout_seconds=args.live_timeout, attempts=args.live_attempts)
        try:
            client.initialize()
            exports = client.exports()
            runtime = exports.get("runtime") or {}
        except Exception as exc:  # noqa: BLE001 - runtime evidence records the failure.
            runtime = {"initialize_or_exports_error": f"{type(exc).__name__}: {exc}"}

    case_end = args.case_end if args.case_end is not None else len(cases)
    if not 0 <= args.case_start < case_end <= len(cases):
        raise ValueError(f"invalid case range {args.case_start}:{case_end} for {len(cases)} cases")
    selected_cases = cases[args.case_start:case_end]
    prior_results: dict[str, dict[str, Any]] = {}
    if args.mode == "live" and args.append_report and args.report.exists():
        previous = json.loads(args.report.read_text(encoding="utf-8"))
        prior_results = {str(entry.get("case_id")): entry for entry in previous.get("case_results") or [] if entry.get("case_id")}
    for case in selected_cases:
        case_client = client
        if client and args.live_new_session_per_case:
            case_client = fast_live_client(args.mcp_url, timeout_seconds=args.live_timeout, attempts=args.live_attempts)
            try:
                case_client.initialize()
            except Exception as exc:  # noqa: BLE001 - recorded through the case result below.
                error_text = f"{type(exc).__name__}: {exc}"
                payload = None
            else:
                payload, error_text = invoke_live(case_client, case)
        else:
            payload, error_text = invoke_live(case_client, case) if case_client else invoke_offline(case)
        errors = check_case(case, payload, error_text, args.mode)
        prior_results[case["case_id"]] = {"case_id": case["case_id"], "tool": case["tool"], "errors": errors, "error": error_text}
    case_results = [prior_results[case["case_id"]] for case in cases if case["case_id"] in prior_results]
    failures = [result for result in case_results if result["errors"]]
    report = {
        "report_version": "openfin-live-120-v1",
        "mode": args.mode,
        "checked_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "endpoint": args.mcp_url if args.mode == "live" else None,
        "fixture": str(GOLDEN.relative_to(REPO_ROOT)),
        "runtime": runtime,
        "test_count": len(case_results),
        "passed_count": len(case_results) - len(failures),
        "failed_count": len(failures),
        "skipped_count": len(cases) - len(case_results),
        "failures": failures,
        "case_results": case_results,
        "category_counts": CATEGORY_COUNTS,
        "fixture_output_is_not_live_evidence": args.mode != "live",
    }
    if args.mode == "live":
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: report[key] for key in ("mode", "test_count", "passed_count", "failed_count", "skipped_count")}, ensure_ascii=False))
    if failures or len(case_results) != len(cases):
        for failure in failures[:20]:
            print(f"FAIL {failure['case_id']}: {'; '.join(failure['errors'])}")
        if len(case_results) != len(cases):
            print(f"INCOMPLETE: {len(case_results)}/{len(cases)} cases collected")
        return 1
    print(f"OpenFin {args.mode} golden validation passed: {len(cases)}/120, skip=0")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
