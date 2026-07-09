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
    "monthly_benefit_limit_unlimited",
    "benefit_type",
    "benefit_rate_min_percent",
    "benefit_rate_max_percent",
    "fixed_benefit_amount_krw",
    "benefit_categories",
    "condition_completeness",
    "condition_parse_source",
    "missing_condition_fields",
)
NO_SPEND_MARKERS = ("no전월실적", "전월실적없이", "실적조건없고", "실적조건없이", "조건없이")
UNLIMITED_LIMIT_MARKERS = ("한도없이", "한도없는", "한도도없는", "적립한도없", "할인한도없")


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
            if benefit.get("benefit_rate_min_percent") and benefit.get("benefit_rate_max_percent"):
                if benefit["benefit_rate_min_percent"] > benefit["benefit_rate_max_percent"]:
                    errors.append(f"{card['id']}: benefit_rate_min_percent가 max보다 큽니다.")
            text = " ".join(str(benefit.get(key) or "") for key in ("text", "benefit", "condition"))
            compact = text.replace(" ", "").lower()
            if any(marker in compact for marker in NO_SPEND_MARKERS) and benefit.get("previous_month_spend_required") is not False:
                errors.append(f"{card['id']}: 전월실적 없음 문구가 있는데 previous_month_spend_required가 false가 아닙니다.")
            if any(marker in compact for marker in UNLIMITED_LIMIT_MARKERS) and benefit.get("monthly_benefit_limit_unlimited") is not True:
                errors.append(f"{card['id']}: 한도 없음 문구가 있는데 monthly_benefit_limit_unlimited가 true가 아닙니다.")
            fixed_amount = benefit.get("fixed_benefit_amount_krw")
            monthly_limit = benefit.get("monthly_benefit_limit_krw")
            if fixed_amount is not None and fixed_amount == monthly_limit and any(marker in compact for marker in ("월최대", "매월최대", "월한도")):
                errors.append(f"{card['id']}: 월 한도를 fixed_benefit_amount_krw로 중복 기록했습니다.")
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
