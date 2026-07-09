"""대출 추천 가드 검증.

- 현재 운영 단계에서는 모든 대출이 reference_only여야 한다.
- 필수 필드 누락 대출은 missing_loan_required_fields와 exclusion reason을 가져야 한다.
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
    for loan in loans:
        recommendation_status = loan.get("recommendation_status")
        if recommendation_status != "reference_only":
            errors.append(f"{loan['id']}: 대출은 현재 reference_only여야 하는데 recommendation_status={recommendation_status}")
        missing = [
            field
            for field in LOAN_REQUIRED_FIELDS
            if loan.get(field) is None and not (field == "loan_limit_krw" and loan.get("loan_limit_text"))
        ]
        reasons = set(loan.get("recommendation_exclusion_reasons") or [])
        if "loan_recommendation_suspended_pending_required_field_review" not in reasons:
            errors.append(f"{loan['id']}: 대출 추천 보류 사유가 없습니다.")
        if missing and "incomplete_loan_required_fields" not in reasons:
            errors.append(f"{loan['id']}: 필수 필드 누락({missing})인데 incomplete_loan_required_fields 사유가 없습니다.")
    for error in errors[:20]:
        print("FAIL:", error)
    if errors:
        print(f"FAILED: {len(errors)} violations across {len(loans)} loans")
        return 1
    print(f"OK: {len(loans)} loans guarded as reference_only")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
