from __future__ import annotations

import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SUPPORT_EXPORT = REPO_ROOT / "ontology/exports/korea-local-government-supports-ontology-2026.json"
OPEN_STATUSES = {"eligible_for_listing"}
NON_ACTIONABLE_STATUSES = {
    "budget_exhaustion", "announcement_based", "agency_contact_required", "schedule_pending",
    "recurring_monthly", "recurring_quarterly", "recurring_annual",
    "agency_schedule_varies", "source_schedule_ambiguous",
}


def main() -> int:
    payload = json.loads(SUPPORT_EXPORT.read_text(encoding="utf-8"))
    refresh_complete = payload.get("current_refresh_complete") is True
    items = [*(payload.get("reference_items") or []), *(payload.get("items") or [])]
    programs = [item for item in items if item.get("type") == "support-program"]
    errors: list[str] = []
    counts: dict[str, int] = {}
    for program in programs:
        application_status = str(program.get("application_status") or "unknown")
        recommendation_status = program.get("recommendation_status")
        counts[application_status] = counts.get(application_status, 0) + 1
        if application_status in ({"unknown", "closed", "not_required"} | NON_ACTIONABLE_STATUSES) and recommendation_status != "reference_only":
            errors.append(
                f"{program['id']}: application_status={application_status}인데 recommendation_status={recommendation_status}"
            )
        if application_status in {"open", "always_open"} and refresh_complete and recommendation_status not in OPEN_STATUSES:
            errors.append(
                f"{program['id']}: application_status=open인데 recommendation_status={recommendation_status}"
            )
        if application_status in {"open", "always_open"} and not refresh_complete and recommendation_status != "reference_only":
            errors.append(
                f"{program['id']}: 부분 수집 중 open 지원사업은 reference_only여야 합니다."
            )
    if counts.get("unknown", 0) > 500:
        errors.append(f"application_status=unknown exceeds 500 ({counts['unknown']})")
    for error in errors[:20]:
        print("FAIL:", error)
    if errors:
        print(f"FAILED: {len(errors)} violations")
        return 1
    print(
        f"OK: {len(programs)} support programs consistent "
        f"(open={counts.get('open', 0)}, always_open={counts.get('always_open', 0)}, closed={counts.get('closed', 0)}, "
        f"not_required={counts.get('not_required', 0)}, unknown={counts.get('unknown', 0)}, "
        f"non_actionable={sum(counts.get(status, 0) for status in NON_ACTIONABLE_STATUSES)})"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
