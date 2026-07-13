"""품질 manifest와 실제 export·회귀 리포트의 정합성 검증.

- 품질 manifest의 도메인 요약/체크섬이 실제 export 파일과 일치하는지
- 오프라인 회귀 리포트가 통과 상태인지, 실패가 있으면 failures 목록이 채워져 있는지
- 라이브 회귀 결과(live_search_regression)가 기록돼 있고 실패 사례 구조를 갖췄는지
"""
from __future__ import annotations

import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
EXPORT_DIR = REPO_ROOT / "ontology/exports"
QUALITY_MANIFEST = EXPORT_DIR / "openfin-quality-manifest-2026.json"
REGRESSION_REPORT = EXPORT_DIR / "openfin-search-regression-report-2026.json"
FINANCE_MANIFEST = EXPORT_DIR / "finance-ontology-manifest.json"
REQUIRED_RUNTIME_QUALITY_METRICS = {
    "catalog_status_counts", "runtime_discovery_eligible_count", "exact_discovery_candidate_count",
    "partial_discovery_candidate_count", "duplicate_canonical_product_count", "hard_constraint_violation_count",
    "grade_policy_violation_count", "verification_timestamp_violation_count", "empty_structured_summary_count",
    "empty_search_facets_count", "unmapped_existing_field_count", "sales_verification_status_counts",
    "verification_grade_counts", "relevance_grade_counts", "exact_query_precision", "product_kind_precision",
    "hard_constraint_precision", "duplicate_free_rate", "unknown_constraint_disclosure_rate",
}


def check_summary(errors: list[str], name: str, summary: dict) -> None:
    for key in ("test_count", "passed_count", "failed_count", "failures"):
        if key not in summary:
            errors.append(f"{name}: {key} 필드가 없습니다.")
    failures = summary.get("failures")
    if summary.get("failed_count"):
        if not failures:
            errors.append(f"{name}: 실패가 있는데 failures 목록이 비어 있습니다.")
        for failure in failures or []:
            for key in ("query", "expected", "actual"):
                if key not in failure:
                    errors.append(f"{name}: 실패 사례에 {key}가 없습니다.")
        if not summary.get("last_failed_at"):
            errors.append(f"{name}: 실패가 있는데 last_failed_at이 없습니다.")


def main() -> int:
    manifest = json.loads(QUALITY_MANIFEST.read_text(encoding="utf-8"))
    report = json.loads(REGRESSION_REPORT.read_text(encoding="utf-8"))
    errors: list[str] = []
    runtime_metrics = manifest.get("runtime_quality_metrics") or {}
    missing_runtime_metrics = REQUIRED_RUNTIME_QUALITY_METRICS - set(runtime_metrics)
    if missing_runtime_metrics:
        errors.append(f"runtime_quality_metrics 필드가 없습니다: {sorted(missing_runtime_metrics)}")
    for key in ("duplicate_canonical_product_count", "hard_constraint_violation_count", "grade_policy_violation_count", "verification_timestamp_violation_count"):
        if runtime_metrics.get(key, 0) != 0:
            errors.append(f"runtime_quality_metrics.{key} must be zero")
    for key in ("exact_query_precision", "product_kind_precision", "hard_constraint_precision", "duplicate_free_rate", "unknown_constraint_disclosure_rate"):
        if float(runtime_metrics.get(key, 0)) < 1:
            errors.append(f"runtime_quality_metrics.{key} must be 1.0")

    # 1) 오프라인 회귀 리포트와 manifest 요약 일치
    manifest_summary = (manifest.get("search_regression_report") or {}).get("quality_summary") or {}
    for key in ("test_count", "passed_count", "failed_count"):
        if manifest_summary.get(key) != report.get(key):
            errors.append(f"search_regression_report.{key}가 리포트({report.get(key)})와 manifest({manifest_summary.get(key)})에서 다릅니다.")
    check_summary(errors, "search_regression_report", manifest_summary)
    for test in report.get("tests") or []:
        for key in ("query", "expected_top_id", "actual_top_id", "passed"):
            if key not in test:
                errors.append(f"회귀 테스트에 {key} 필드가 없습니다: {test.get('query')}")

    # 2) 라이브 회귀 결과 존재 + 구조
    live = manifest.get("live_search_regression")
    if not live:
        errors.append("live_search_regression이 manifest에 없습니다. validate_search_regression_live.py를 먼저 실행하세요.")
    else:
        check_summary(errors, "live_search_regression", live)
        if not live.get("checked_at"):
            errors.append("live_search_regression.checked_at이 없습니다.")
        if live.get("failed_count"):
            errors.append("live_search_regression에 실패 사례가 있습니다.")
        finance_manifest = json.loads(FINANCE_MANIFEST.read_text(encoding="utf-8"))
        expected_search_checksum = (finance_manifest.get("search_index") or {}).get("export_checksum")
        if live.get("search_index_checksum") != expected_search_checksum:
            errors.append("live_search_regression.search_index_checksum이 현재 검색 인덱스와 다릅니다.")
        if live.get("runtime_search_index_checksum") != expected_search_checksum:
            errors.append("live_search_regression.runtime_search_index_checksum이 현재 검색 인덱스와 다릅니다.")
        required_live = [test for test in report.get("live_tests") or [] if str(test.get("validation_kind") or "").startswith("required_live_")]
        if len(required_live) != 14:
            errors.append(f"필수 라이브 회귀가 14건이 아닙니다: {len(required_live)}")
        for test in required_live:
            if test.get("validation_kind") == "required_live_discovery_contract":
                for key in ("parsed_query", "exact_candidates", "partial_candidates", "related_candidates", "candidate_counts", "top5_product_kinds", "duplicate_canonical_product_ids", "candidate_grades"):
                    if key not in test:
                        errors.append(f"필수 라이브 탐색 증적에 {key}가 없습니다: {test.get('query')}")
            if test.get("validation_kind") == "required_live_comparison_contract":
                for key in ("parsed_query", "comparison_arguments", "candidates", "candidate_count", "top5_product_kinds", "duplicate_product_ids"):
                    if key not in test:
                        errors.append(f"필수 라이브 비교 증적에 {key}가 없습니다: {test.get('query')}")

    # 3) 도메인 요약 체크섬이 실제 export와 일치
    for entry in manifest.get("domain_summaries") or []:
        export_id = entry.get("id")
        checksum = entry.get("export_checksum")
        if not checksum:
            continue
        candidates = list(EXPORT_DIR.glob(f"{export_id}*.json")) if export_id else []
        if not candidates:
            continue
        payload = json.loads(candidates[0].read_text(encoding="utf-8"))
        actual = payload.get("export_checksum")
        if actual and actual != checksum:
            errors.append(f"{export_id}: manifest 체크섬({checksum[:12]}…)과 export 체크섬({actual[:12]}…)이 다릅니다.")

    for error in errors[:20]:
        print("FAIL:", error)
    if errors:
        print(f"FAILED: {len(errors)} inconsistencies")
        return 1
    live_status = f"live {live.get('passed_count')}/{live.get('test_count')}" if live else "live 미기록"
    print(f"OK: manifest consistent (offline {report.get('passed_count')}/{report.get('test_count')}, {live_status})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
