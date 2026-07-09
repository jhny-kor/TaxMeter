"""카드 추천 안전성 검증.

benefit 조건이 partial/incomplete인 카드는 추천 승격이 금지되고
recommendation_status=reference_only, recommendation_scope=listing_only여야 한다.
"""
from __future__ import annotations

import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
CARD_EXPORT = REPO_ROOT / "ontology/exports/korea-card-products-ontology-2026.json"
def main() -> int:
    payload = json.loads(CARD_EXPORT.read_text(encoding="utf-8"))
    items = [*(payload.get("reference_items") or []), *(payload.get("items") or [])]
    cards = [item for item in items if item.get("type") == "card-product"]
    errors: list[str] = []
    unsafe = 0
    for card in cards:
        has_unparsed = any(
            isinstance(benefit, dict) and benefit.get("condition_completeness") in {"partial", "incomplete"}
            for benefit in card.get("benefits") or []
        )
        if not has_unparsed:
            continue
        unsafe += 1
        if card.get("recommendation_scope") != "listing_only":
            errors.append(f"{card['id']}: 조건 미완성인데 recommendation_scope={card.get('recommendation_scope')}")
        if card.get("recommendation_status") != "reference_only":
            errors.append(f"{card['id']}: 조건 미완성인데 recommendation_status={card.get('recommendation_status')}")
    for error in errors[:20]:
        print("FAIL:", error)
    if errors:
        print(f"FAILED: {len(errors)} violations")
        return 1
    print(f"OK: {unsafe} cards with unparsed conditions are all reference_only/listing-only ({len(cards)} cards total)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
