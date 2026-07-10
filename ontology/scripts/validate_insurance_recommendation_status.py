from __future__ import annotations

import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
INSURANCE_EXPORT = REPO_ROOT / "ontology/exports/korea-insurance-products-ontology-2026.json"
LOAN_EXPORT = REPO_ROOT / "ontology/exports/korea-loan-products-ontology-2026.json"
GENERATED_INSURANCE = REPO_ROOT / "ontology/custom/finance/insurance-products.generated.json"
REQUIRED_COVERAGE_FIELDS = (
    "coverage_amount_basis",
    "claim_condition",
    "exclusion_condition",
    "condition_source_url",
    "condition_source_locator",
)


def main() -> int:
    payload = json.loads(INSURANCE_EXPORT.read_text(encoding="utf-8"))
    loan_payload = json.loads(LOAN_EXPORT.read_text(encoding="utf-8"))
    generated_payload = json.loads(GENERATED_INSURANCE.read_text(encoding="utf-8"))
    items = [*(payload.get("reference_items") or []), *(payload.get("items") or [])]
    loan_items = [*(loan_payload.get("reference_items") or []), *(loan_payload.get("items") or [])]
    products = [item for item in items if item.get("type") == "insurance-product"]
    errors: list[str] = []
    incomplete_products = 0
    loan_ids = {item.get("id") for item in loan_items}
    loans_by_id = {item.get("id"): item for item in loan_items}
    generated_insurance_loans = [
        item
        for item in generated_payload.get("items") or []
        if isinstance(item.get("raw"), dict) and (item["raw"].get("loan_type") or "대출" in str(item["raw"].get("fin_prdt_type_nm") or ""))
    ]
    for item in generated_insurance_loans:
        expected_id = str(item.get("id") or "").replace("finance.insurance.annuity-saving.", "finance.bank.insurer-loan.")
        if expected_id not in loan_ids:
            errors.append(f"{item.get('id')}: 보험 export에서 제외된 대출 행이 loan export로 재분류되지 않았습니다.")
            continue
        reclassified = loans_by_id[expected_id]
        if reclassified.get("recommendation_status") != "reference_only":
            errors.append(f"{expected_id}: 재분류된 보험사 대출은 필드 검증 전 reference_only여야 합니다.")
        if "source_domain_reclassified" not in (reclassified.get("quality_flags") or []):
            errors.append(f"{expected_id}: source_domain_reclassified 품질 플래그가 없습니다.")
    for product in products:
        raw = product.get("raw") if isinstance(product.get("raw"), dict) else {}
        if raw.get("loan_type") or "대출" in str(raw.get("fin_prdt_type_nm") or ""):
            errors.append(f"{product['id']}: 대출 공시 행이 insurance-product로 분류됐습니다.")
        coverage_criteria = [
            criterion
            for criterion in product.get("criteria") or []
            if isinstance(criterion, dict) and criterion.get("criteria_kind") == "coverage"
        ]
        for criterion in product.get("criteria") or []:
            if not isinstance(criterion, dict) or criterion.get("criteria_kind") != "coverage":
                continue
            for field in REQUIRED_COVERAGE_FIELDS:
                if field not in criterion:
                    errors.append(f"{product['id']}: coverage에 {field} 필드가 없습니다.")
            if criterion.get("source") == "source.klia.insurance-disclosure" and criterion.get("coverage_amount_krw") is not None:
                errors.append(f"{product['id']}: 협회 보험료 기준 가입금액을 개별 담보 보장금액으로 사용할 수 없습니다.")
            if criterion.get("disclosed_insured_amount_krw") is not None and criterion.get("disclosed_insured_amount_basis") != "association_premium_basis_amount":
                errors.append(f"{product['id']}: 공시 가입금액 근거가 association_premium_basis_amount가 아닙니다.")
            if not str(criterion.get("condition_source_url") or "").startswith("https://"):
                errors.append(f"{product['id']}: coverage condition_source_url이 없습니다.")
            if not criterion.get("condition_source_locator"):
                errors.append(f"{product['id']}: coverage condition_source_locator가 없습니다.")
        incomplete = any(
            criterion.get("condition_completeness") == "incomplete"
            for criterion in coverage_criteria
        )
        if coverage_criteria and not incomplete:
            continue
        incomplete_products += 1
        if product.get("recommendation_status") != "reference_only":
            errors.append(f"{product['id']}: 핵심 조건 미비인데 recommendation_status={product.get('recommendation_status')}입니다.")
        if product.get("recommendation_scope") != "listing_only":
            errors.append(f"{product['id']}: 핵심 조건 미비인데 recommendation_scope={product.get('recommendation_scope')}")
        if product.get("recommendation_status") == "recommendation_candidate":
            errors.append(f"{product['id']}: 약관 핵심 조건 미비 보험이 추천 후보로 열렸습니다.")
    for error in errors[:20]:
        print("FAIL:", error)
    if errors:
        print(f"FAILED: {len(errors)} violations")
        return 1
    print(f"OK: {incomplete_products} incomplete-coverage products are all reference_only/listing-only ({len(products)} products total)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
