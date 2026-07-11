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
    candidate_count = 0
    for loan in loans:
        missing = [
            field
            for field in LOAN_REQUIRED_FIELDS
            if loan.get(field) is None
        ]
        reasons = set(loan.get("recommendation_exclusion_reasons") or [])
        is_candidate = is_recommendation_ready_loan(loan)
        if is_candidate:
            candidate_count += 1
            if loan.get("recommendation_status") != "manual_review_candidate":
                errors.append(f"{loan['id']}: 필수 필드가 완전한 active 대출이 manual_review_candidate가 아닙니다.")
            if loan.get("recommendation_scope") != "internal_verification_candidate":
                errors.append(f"{loan['id']}: 검증 후보의 recommendation_scope가 internal_verification_candidate가 아닙니다.")
            if "incomplete_loan_required_fields" in reasons:
                errors.append(f"{loan['id']}: 완전한 후보에 incomplete_loan_required_fields 사유가 남아 있습니다.")
            if loan.get("operating_period_status") != "confirmed_open":
                errors.append(f"{loan['id']}: 운영기간이 확인되지 않은 대출이 추천 후보입니다.")
            if loan.get("loan_limit_normalization_status") != "verified":
                errors.append(f"{loan['id']}: 한도 단위가 검증되지 않은 대출이 추천 후보입니다.")
            continue
        if loan.get("recommendation_status") != "reference_only":
            errors.append(f"{loan['id']}: 불완전하거나 비활성인 대출은 reference_only여야 합니다.")
        if loan.get("status") == "active" and not loan.get("criteria") and "missing_loan_criteria" not in set(loan.get("quality_flags") or []):
            errors.append(f"{loan['id']}: criteria 없는 active 대출에 missing_loan_criteria가 없습니다.")
        if missing and "incomplete_loan_required_fields" not in reasons:
            errors.append(f"{loan['id']}: 필수 필드 누락({missing})인데 incomplete_loan_required_fields 사유가 없습니다.")
    for error in errors[:20]:
        print("FAIL:", error)
    if errors:
        print(f"FAILED: {len(errors)} violations across {len(loans)} loans")
        return 1
    if candidate_count == 0:
        print("FAILED: no recommendation-ready loan candidates")
        return 1
    print(f"OK: {candidate_count} manual review candidates; {len(loans) - candidate_count} loans remain reference_only")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
