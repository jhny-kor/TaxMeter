"""지원사업 신청 상태 → 추천 상태 매핑과 export 후처리.

application_status=open and current source data → recommendation_candidate (추천 후보)
application_status=closed/unknown → reference_only (조회 전용, 추천 제외)

generate_vault.py의 지원사업 enrich 단계가 이 매핑을 사용하고,
직접 실행하면 기존 export 파일에 매핑을 재적용한다(전체 vault 재생성 불필요).
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SUPPORT_EXPORT = REPO_ROOT / "ontology/exports/korea-local-government-supports-ontology-2026.json"

STATUS_TO_RECOMMENDATION = {
    "open": "recommendation_candidate",
    "active": "recommendation_candidate",
    "closed": "reference_only",
    "not_required": "reference_only",
    "unknown": "reference_only",
}


def resolve_recommendation_status(
    status: str,
    freshness_status: str | None = None,
    collection_status: str | None = None,
) -> str:
    if freshness_status not in {None, "current"} or collection_status == "preserved_snapshot":
        return "reference_only"
    return STATUS_TO_RECOMMENDATION.get(str(status), "reference_only")


def payload_checksum(payload: dict) -> str:
    encoded = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def main() -> int:
    payload = json.loads(SUPPORT_EXPORT.read_text(encoding="utf-8"))
    payload.pop("export_checksum", None)
    changed = 0
    counts = {"recommendation_candidate": 0, "reference_only": 0}
    for item in [*(payload.get("reference_items") or []), *(payload.get("items") or [])]:
        if item.get("type") != "support-program":
            continue
        resolved = resolve_recommendation_status(
            item.get("application_status") or "unknown",
            item.get("freshness_status"),
            item.get("collection_status"),
        )
        if item.get("recommendation_status") != resolved:
            item["recommendation_status"] = resolved
            changed += 1
        counts[resolved] = counts.get(resolved, 0) + 1
    summary = payload.get("quality_summary")
    if isinstance(summary, dict):
        summary["recommendation_candidates"] = counts.get("recommendation_candidate", 0)
        summary["recommendation_reference_only"] = counts.get("reference_only", 0)
    payload["export_checksum"] = payload_checksum(payload)
    SUPPORT_EXPORT.write_text(json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8")
    print(f"OK: {changed} programs updated (candidate={counts.get('recommendation_candidate', 0)}, reference_only={counts.get('reference_only', 0)})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
