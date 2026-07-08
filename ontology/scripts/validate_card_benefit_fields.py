"""카드 benefit 조건 필드화 검증.

모든 card-product benefit이 구조화 필드를 갖고, 파싱된 값이 서로 모순되지 않는지 확인한다.
"""
from __future__ import annotations

import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
CARD_EXPORT = REPO_ROOT / "ontology/exports/korea-card-products-ontology-2026.json"

REQUIRED_KEYS = (
    "previous_month_spend_required",
    "previous_month_spend_min_krw",
    "annual_fee_required",
    "annual_fee_krw",
    "monthly_benefit_limit_krw",
    "benefit_type",
    "condition_completeness",
    "condition_parse_source",
    "missing_condition_fields",
)


def main() -> int:
    payload = json.loads(CARD_EXPORT.read_text(encoding="utf-8"))
    items = [*(payload.get("reference_items") or []), *(payload.get("items") or [])]
    cards = [item for item in items if item.get("type") == "card-product"]
    errors: list[str] = []
    benefit_count = 0
    for card in cards:
        for benefit in card.get("benefits") or []:
            if not isinstance(benefit, dict):
                continue
            benefit_count += 1
            for key in REQUIRED_KEYS:
                if key not in benefit:
                    errors.append(f"{card['id']}: benefit에 {key} 필드가 없습니다.")
            if benefit.get("previous_month_spend_required") is False and benefit.get("previous_month_spend_min_krw") not in (0, None):
                errors.append(f"{card['id']}: 전월실적 불필요인데 최소실적이 {benefit.get('previous_month_spend_min_krw')}원입니다.")
            if benefit.get("previous_month_spend_required") is True and not benefit.get("previous_month_spend_min_krw"):
                errors.append(f"{card['id']}: 전월실적 필요인데 최소실적 금액이 없습니다.")
            if benefit.get("annual_fee_required") is False and benefit.get("annual_fee_krw") not in (0, None):
                errors.append(f"{card['id']}: 연회비 없음인데 annual_fee_krw={benefit.get('annual_fee_krw')}입니다.")
            if benefit.get("condition_completeness") not in {"complete", "partial", "incomplete"}:
                errors.append(f"{card['id']}: condition_completeness 값이 잘못되었습니다.")
    for error in errors[:20]:
        print("FAIL:", error)
    if errors:
        print(f"FAILED: {len(errors)} violations in {benefit_count} benefits")
        return 1
    print(f"OK: {benefit_count} card benefits across {len(cards)} cards all structured")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
