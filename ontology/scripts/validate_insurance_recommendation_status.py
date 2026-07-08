"""보험 추천 상태 검증.

보장금액·갱신주기·면책기간·감액기간이 비어 있는(incomplete) coverage를 가진 상품은
eligible_for_recommendation이 될 수 없고, listing_only 범위여야 한다.
"""
from __future__ import annotations

import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
INSURANCE_EXPORT = REPO_ROOT / "ontology/exports/korea-insurance-products-ontology-2026.json"


def main() -> int:
    payload = json.loads(INSURANCE_EXPORT.read_text(encoding="utf-8"))
    items = [*(payload.get("reference_items") or []), *(payload.get("items") or [])]
    products = [item for item in items if item.get("type") == "insurance-product"]
    errors: list[str] = []
    incomplete_products = 0
    for product in products:
        incomplete = any(
            isinstance(criterion, dict)
            and criterion.get("criteria_kind") == "coverage"
            and criterion.get("condition_completeness") == "incomplete"
            for criterion in product.get("criteria") or []
        )
        if not incomplete:
            continue
        incomplete_products += 1
        if product.get("recommendation_status") == "eligible_for_recommendation":
            errors.append(f"{product['id']}: 핵심 조건 미비인데 eligible_for_recommendation입니다.")
        if product.get("recommendation_scope") != "listing_only":
            errors.append(f"{product['id']}: 핵심 조건 미비인데 recommendation_scope={product.get('recommendation_scope')}")
    for error in errors[:20]:
        print("FAIL:", error)
    if errors:
        print(f"FAILED: {len(errors)} violations")
        return 1
    print(f"OK: {incomplete_products} incomplete-coverage products are all listing-only ({len(products)} products total)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
