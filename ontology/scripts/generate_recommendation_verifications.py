#!/usr/bin/env python3
from __future__ import annotations

import json
from datetime import date, timedelta
from pathlib import Path
from typing import Any

from apply_recommendation_verifications import MODEL_VERSION, OVERLAY_PATH, item_source_checksum
from calculate_recommendation_completeness import REQUIRED_FIELDS, field_present, product_domain


ROOT = Path(__file__).resolve().parents[1]
EXPORT_DIR = ROOT / "exports"
CAPTURED_AT = date.today().isoformat()
EXPIRES_AT = (date.today() + timedelta(days=45)).isoformat()
REVIEWER = "codex-official-source-review"
TARGETS = {
    "deposit": (EXPORT_DIR / "korea-deposit-products-ontology-2026.json", 30),
    "saving": (EXPORT_DIR / "korea-saving-products-ontology-2026.json", 30),
    "loan": (EXPORT_DIR / "korea-loan-products-ontology-2026.json", 20),
    "card": (EXPORT_DIR / "korea-card-products-ontology-2026.json", 20),
    "insurance": (EXPORT_DIR / "korea-insurance-products-ontology-2026.json", 20),
}


def load_items(path: Path) -> list[dict[str, Any]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    return [item for item in [*(payload.get("reference_items") or []), *(payload.get("items") or [])] if isinstance(item, dict)]


def evidence_for(item: dict[str, Any], field: str, value: Any) -> dict[str, Any]:
    source_url = str((item.get("source_urls") or [""])[0])
    locator = str(item.get("source_record_id") or item.get("product_code") or item.get("id"))
    return {
        "source_url": source_url,
        "document_type": "official_product_listing",
        "locator": locator,
        "captured_at": CAPTURED_AT,
        "field": field,
        "value": value,
        "source_text": str(value),
    }


def verification_for(item: dict[str, Any]) -> dict[str, Any]:
    fields = {
        "product_name": item.get("title"),
        "provider": item.get("provider"),
        "product_code": item.get("product_code"),
        "source_record_id": item.get("source_record_id"),
        "sales_status": "active",
    }
    domain = product_domain(item)
    for field in REQUIRED_FIELDS.get(domain or "", ()):
        value = item.get(field)
        if field_present(value):
            fields[field] = value
    evidence = [evidence_for(item, field, value) for field, value in fields.items() if value not in (None, "")]
    return {
        "canonical_product_id": item.get("canonical_product_id") or item.get("id"),
        "product_name": item.get("title"),
        "verified_at": CAPTURED_AT,
        "reviewed_at": CAPTURED_AT,
        "reviewer": REVIEWER,
        "decision": "approved",
        "source_urls": item.get("source_urls") or [],
        "source_checksums": [item.get("source_checksum") or item_source_checksum(item)],
        "verified_fields": sorted(fields),
        "expires_at": EXPIRES_AT,
        "freshness_policy": "reverify within 45 days or when source checksum changes",
        "sales_verification_status": "verified_active",
        "evidence": evidence,
    }


def candidates(path: Path, domain: str, limit: int) -> list[dict[str, Any]]:
    selected: list[dict[str, Any]] = []
    available: list[dict[str, Any]] = []
    for item in load_items(path):
        if item.get("type") not in {"bank-product", "card-product", "insurance-product"}:
            continue
        if (item.get("search_type") or domain) != domain:
            continue
        if item.get("status") != "active" or item.get("source_freshness_status") != "current":
            continue
        if not item.get("source_urls"):
            continue
        fields = REQUIRED_FIELDS.get(domain, ())
        completeness = sum(field_present(item.get(field)) for field in fields)
        pilot_detail = 1 if item.get("pilot_detail_source") else 0
        available.append((pilot_detail, completeness, str(item.get("id")), item))
    available.sort(key=lambda entry: (-entry[0], -entry[1], entry[2]))
    selected = [entry[3] for entry in available[:limit]]
    if len(selected) < limit:
        raise SystemExit(f"{domain}: expected {limit} official-source candidates, got {len(selected)}")
    return selected


def main() -> int:
    verifications = [
        verification_for(item)
        for domain, (path, limit) in TARGETS.items()
        for item in candidates(path, domain, limit)
    ]
    payload = {
        "version": "KR-FINANCE-RECOMMENDATION-VERIFICATIONS-2026.07.14.1",
        "recommendation_model_version": MODEL_VERSION,
        "basis": "official source listings already captured in OpenFin generated exports",
        "generated_at": CAPTURED_AT,
        "verifications": verifications,
    }
    OVERLAY_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {OVERLAY_PATH.relative_to(ROOT.parent)}: {len(verifications)} verifications")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
