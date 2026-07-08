"""type=tax 필터를 건 typed 검색이 조세 결정 노드를 1순위로 반환하는지 검증한다.

검색 인덱스(finance-search-index-2026.json)에 대해 build_finance_ontology와
동일한 스코어링·타입 그룹으로 상위 결과를 재현한다.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_finance_ontology import SEARCH_TYPE_GROUPS, score_search_index_item  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[2]
SEARCH_INDEX = REPO_ROOT / "ontology/exports/finance-search-index-2026.json"

TYPED_REGRESSIONS = (
    ("연말정산 의료비 세액공제 한도 대상", "tax", "credit.medical-expense"),
    ("월세 세액공제 조건", "tax", "credit.monthly-rent"),
    ("교육비 세액공제 대상", "tax", "credit.education-expense"),
    ("연금계좌 세액공제 한도", "tax", "credit.pension-account"),
    ("신용카드 소득공제 한도", "tax", "deduction.credit-card-use"),
)


def main() -> int:
    items = json.loads(SEARCH_INDEX.read_text(encoding="utf-8"))["items"]
    failures = []
    for query, type_filter, expected_id in TYPED_REGRESSIONS:
        allowed = SEARCH_TYPE_GROUPS.get(type_filter, {type_filter})
        ranked = sorted(
            ((score_search_index_item(item, query), item) for item in items if item.get("type") in allowed),
            key=lambda pair: (-pair[0], str(pair[1].get("title") or "")),
        )
        top = ranked[0][1] if ranked and ranked[0][0] > 0 else {}
        actual_id = top.get("id")
        status = "PASS" if actual_id == expected_id else "FAIL"
        print(f"[{status}] type={type_filter} query={query!r} expected={expected_id} actual={actual_id}")
        if actual_id != expected_id:
            failures.append(query)
    if failures:
        print(f"FAILED: {len(failures)}/{len(TYPED_REGRESSIONS)} typed queries")
        return 1
    print(f"OK: {len(TYPED_REGRESSIONS)} typed queries all pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
