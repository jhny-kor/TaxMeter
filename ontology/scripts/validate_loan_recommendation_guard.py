"""대출 추천 가드 검증.

- 필수 필드를 모두 갖춘 active 대출만 eligible_for_listing이 될 수 있다.
- 필수 필드 누락 대출은 reference_only여야 한다.
- 개인 조건 기반 추천(eligible_for_recommendation)은 별도 심사 전이므로 어떤 대출에도 금지된다.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from loan_product_normalizer import LOAN_REQUIRED_FIELDS  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[2]
LOAN_EXPORT = REPO_ROOT / "ontology/exports/korea-loan-products-ontology-2026.json"


def main() -> int:
    payload = json.loads(LOAN_EXPORT.read_text(encoding="utf-8"))
    items = [*(payload.get("reference_items") or []), *(payload.get("items") or [])]
    loans = [item for item in items if item.get("type") == "bank-product" and item.get("search_type") == "loan"]
    errors: list[str] = []
    listed = 0
    for loan in loans:
        recommendation_status = loan.get("recommendation_status")
        if recommendation_status == "eligible_for_recommendation":
            errors.append(f"{loan['id']}: 대출은 별도 심사 없이 eligible_for_recommendation이 될 수 없습니다.")
        missing = [
            field
            for field in LOAN_REQUIRED_FIELDS
            if loan.get(field) is None and not (field == "loan_limit_krw" and loan.get("loan_limit_text"))
        ]
        if recommendation_status == "eligible_for_listing":
            listed += 1
            if missing:
                errors.append(f"{loan['id']}: 필수 필드 누락({missing})인데 eligible_for_listing입니다.")
            if loan.get("status") != "active":
                errors.append(f"{loan['id']}: status={loan.get('status')}인데 eligible_for_listing입니다.")
    for error in errors[:20]:
        print("FAIL:", error)
    if errors:
        print(f"FAILED: {len(errors)} violations across {len(loans)} loans")
        return 1
    print(f"OK: {len(loans)} loans guarded (eligible_for_listing: {listed}, 나머지 reference_only)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
