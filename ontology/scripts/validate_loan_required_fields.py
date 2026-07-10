"""대출 상품 필수 필드 검증.

active인데 criteria가 없는 대출은 reference_only여야 하고,
필수 필드(금리 min/max, 상환방식, 한도, 중도상환수수료, 대출대상, 담보유형, 금리유형)가
하나라도 없으면 recommendation_status=reference_only여야 한다.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from loan_product_normalizer import LOAN_REQUIRED_FIELDS, is_recommendation_ready_loan  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[2]
LOAN_EXPORT = REPO_ROOT / "ontology/exports/korea-loan-products-ontology-2026.json"


def main() -> int:
    payload = json.loads(LOAN_EXPORT.read_text(encoding="utf-8"))
    items = [*(payload.get("reference_items") or []), *(payload.get("items") or [])]
    loans = [item for item in items if item.get("type") == "bank-product" and item.get("search_type") == "loan"]
    errors: list[str] = []
    fully_fielded = 0
    for loan in loans:
        if loan.get("status") == "active" and not loan.get("criteria") and loan.get("recommendation_status") != "reference_only":
            errors.append(f"{loan['id']}: active인데 criteria가 없고 recommendation_status={loan.get('recommendation_status')}")
        if "missing_loan_required_fields" not in loan:
            errors.append(f"{loan['id']}: missing_loan_required_fields 필드가 없습니다(정규화 누락).")
            continue
        missing = [
            field
            for field in LOAN_REQUIRED_FIELDS
            if loan.get(field) is None
        ]
        if sorted(missing) != sorted(loan.get("missing_loan_required_fields") or []):
            errors.append(f"{loan['id']}: missing_loan_required_fields가 실제 누락({missing})과 다릅니다.")
        if missing:
            if loan.get("recommendation_status") != "reference_only":
                errors.append(f"{loan['id']}: 필수 필드 누락({missing})인데 recommendation_status={loan.get('recommendation_status')}")
        elif is_recommendation_ready_loan(loan):
            fully_fielded += 1
        elif loan.get("recommendation_status") != "reference_only":
            errors.append(f"{loan['id']}: 의미 검증을 통과하지 못한 대출은 reference_only여야 합니다.")
    for error in errors[:20]:
        print("FAIL:", error)
    if errors:
        print(f"FAILED: {len(errors)} violations across {len(loans)} loans")
        return 1
    print(f"OK: {len(loans)} loans validated (required fields: {len(LOAN_REQUIRED_FIELDS)}, fully fielded: {fully_fielded})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
