"""지원사업 신청 상태와 추천 상태의 정합성 검증.

application_status=unknown/closed → recommendation_status=reference_only (추천 후보 제외),
application_status=open → recommendation_candidate.
"""
from __future__ import annotations

import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SUPPORT_EXPORT = REPO_ROOT / "ontology/exports/korea-local-government-supports-ontology-2026.json"
OPEN_STATUSES = {"recommendation_candidate"}


def main() -> int:
    payload = json.loads(SUPPORT_EXPORT.read_text(encoding="utf-8"))
    items = [*(payload.get("reference_items") or []), *(payload.get("items") or [])]
    programs = [item for item in items if item.get("type") == "support-program"]
    errors: list[str] = []
    counts = {"open": 0, "closed": 0, "unknown": 0}
    for program in programs:
        application_status = str(program.get("application_status") or "unknown")
        recommendation_status = program.get("recommendation_status")
        counts[application_status if application_status in counts else "unknown"] += 1
        if application_status in {"unknown", "closed"} and recommendation_status != "reference_only":
            errors.append(
                f"{program['id']}: application_status={application_status}인데 recommendation_status={recommendation_status}"
            )
        if application_status == "open" and recommendation_status not in OPEN_STATUSES:
            errors.append(
                f"{program['id']}: application_status=open인데 recommendation_status={recommendation_status}"
            )
    for error in errors[:20]:
        print("FAIL:", error)
    if errors:
        print(f"FAILED: {len(errors)} violations")
        return 1
    print(f"OK: {len(programs)} support programs consistent (open={counts['open']}, closed={counts['closed']}, unknown={counts['unknown']})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
