#!/usr/bin/env python3
from __future__ import annotations

import argparse
import concurrent.futures
import json
import re
import urllib.request
from copy import deepcopy
from html import unescape
from pathlib import Path
from typing import Any

from card_benefit_parser import enrich_card_benefits
from calculate_recommendation_completeness import enrich_product


ROOT = Path(__file__).resolve().parents[1]
CARD_PATH = ROOT / "custom" / "finance" / "card-products.generated.json"
CARD_FIELDS = (
    "annual_fee_krw",
    "previous_month_spend_min_krw",
    "benefit_type",
    "benefit_categories",
    "benefit_rate_percent",
    "benefit_amount_krw",
    "monthly_benefit_limit_krw",
    "per_transaction_limit_krw",
    "benefit_frequency_limit",
    "minimum_payment_amount",
    "excluded_spend",
    "performance_excluded_spend",
)


def detail_url(item: dict[str, Any]) -> str | None:
    return next(
        (
            str(url)
            for url in item.get("source_urls") or []
            if "bccard.com/app/card/" in str(url) and "CardMain" in str(url)
        ),
        None,
    )


def fetch_detail(item: dict[str, Any], timeout: int) -> tuple[int, str, str | None]:
    url = detail_url(item)
    if not url:
        return -1, str(item.get("id")), None
    try:
        request = urllib.request.Request(url, headers={"User-Agent": "OpenFin-official-detail-enricher/1.0"})
        with urllib.request.urlopen(request, timeout=timeout) as response:
            payload = response.read().decode("utf-8", errors="replace")
        text = unescape(re.sub(r"<[^>]+>", " ", payload))
        text = re.sub(r"\s+", " ", text).strip()
        candidate = deepcopy(item)
        candidate["sales_verification_status"] = "verified_active"
        candidate["benefits"] = [*(candidate.get("benefits") or []), {"kind": "official_detail", "text": text}]
        enrich_card_benefits(candidate)
        enrich_product(candidate, set())
        for benefit in candidate.get("benefits") or []:
            if isinstance(benefit, dict) and benefit.get("performance_excluded_spend"):
                candidate["performance_excluded_spend"] = benefit["performance_excluded_spend"]
                break
        score = sum(candidate.get(field) not in (None, "", [], {}, "unknown", "unverified", "listed_unverified") for field in CARD_FIELDS)
        return score, str(item.get("id")), text
    except (OSError, ValueError, UnicodeError):
        return -1, str(item.get("id")), None


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--timeout", type=int, default=20)
    parser.add_argument("--workers", type=int, default=12)
    parser.add_argument("--limit", type=int, default=20)
    args = parser.parse_args()
    payload = json.loads(CARD_PATH.read_text(encoding="utf-8"))
    items = payload.get("items") or []
    candidates = [item for item in items if detail_url(item)]
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as executor:
        results = list(executor.map(lambda item: fetch_detail(item, args.timeout), candidates))
    selected = sorted((result for result in results if result[0] >= 0), key=lambda result: (-result[0], result[1]))[:args.limit]
    selected_ids = {item_id for _, item_id, _ in selected}
    details = {item_id: text for score, item_id, text in selected if text}
    for item in items:
        if item.get("id") not in selected_ids:
            continue
        existing = [benefit for benefit in item.get("benefits") or [] if isinstance(benefit, dict) and benefit.get("kind") != "official_detail"]
        item["benefits"] = [*existing, {"kind": "official_detail", "text": details[item["id"]]}]
        item["pilot_detail_source"] = "official_bccard_detail"
    payload["items"] = items
    payload["item_count"] = len(items)
    payload["version"] = f"{payload.get('version', 'CARD')}-DETAIL-PILOT"
    CARD_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"enriched={len(selected)} candidates={len(candidates)} scores={[score for score, _, _ in selected]}")
    return 0 if len(selected) >= args.limit else 1


if __name__ == "__main__":
    raise SystemExit(main())
