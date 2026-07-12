#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import date
from pathlib import Path
from typing import Any

from recommendation_explanations import recommendation_warning, result_explanation
from recommendation_profiles import normalize_domain, normalize_profile


ROOT = Path(__file__).resolve().parents[1]
SEARCH_INDEX = ROOT / "exports" / "finance-search-index-2026.json"
MODEL_VERSION = "openfin-recommendation-v0.1.0"

DOMAIN_TYPES = {
    "deposit": {"search_type": {"deposit"}, "type": {"bank-product"}},
    "saving": {"search_type": {"saving"}, "type": {"bank-product"}},
    "card": {"type": {"card-product"}},
    "loan": {"search_type": {"loan"}, "type": {"bank-product"}},
    "insurance": {"type": {"insurance-product"}},
    "support": {"type": {"support-program"}},
}


def load_search_items(path: Path = SEARCH_INDEX) -> list[dict[str, Any]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    return [item for item in payload.get("items") or [] if isinstance(item, dict)]


def matches_domain(item: dict[str, Any], domain: str) -> bool:
    spec = DOMAIN_TYPES[domain]
    allowed_types = spec.get("type")
    allowed_search_types = spec.get("search_type")
    if allowed_types and item.get("type") not in allowed_types:
        return False
    if allowed_search_types and item.get("search_type") not in allowed_search_types:
        return False
    return True


def public_recommendation_blocker(item: dict[str, Any]) -> str | None:
    if item.get("recommendation_status") != "verified_recommendation_candidate":
        return "not_verified_recommendation_candidate"
    if item.get("recommendation_scope") != "public_recommendation":
        return "not_public_recommendation_scope"
    if item.get("verification_status") != "verified":
        return "verification_not_verified"
    evidence = item.get("verification_evidence")
    if not isinstance(evidence, dict):
        return "missing_verification_evidence"
    if item.get("source_checksum") not in set(str(value) for value in evidence.get("source_checksums") or []):
        return "source_checksum_mismatch"
    expires_at = evidence.get("expires_at")
    if not isinstance(expires_at, str):
        return "verification_expired"
    try:
        expires = date.fromisoformat(expires_at)
    except ValueError:
        return "verification_expired"
    if expires < date.today():
        return "verification_expired"
    if item.get("freshness_status") == "stale":
        return "stale_source"
    if item.get("status") in {"closed", "ended", "unknown", "suspended"}:
        return f"status_{item.get('status')}"
    return None


def score_candidate(item: dict[str, Any], profile: dict[str, Any]) -> tuple[float, dict[str, float]]:
    components: dict[str, float] = {"verification": 50.0}
    if profile.get("provider") and str(profile["provider"]) == str(item.get("provider")):
        components["provider_match"] = 10.0
    if item.get("freshness_status") == "current":
        components["freshness"] = 10.0
    score = sum(components.values())
    return score, components


def recommend(
    domain: str,
    profile: dict[str, Any] | None = None,
    constraints: dict[str, Any] | None = None,
    preferences: dict[str, Any] | None = None,
    limit: int = 5,
    items: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    normalized_domain = normalize_domain(domain)
    normalized_profile = normalize_profile(profile)
    source_items = items if items is not None else load_search_items()
    candidates = [item for item in source_items if matches_domain(item, normalized_domain)]

    if normalized_domain in {"card", "loan", "insurance"}:
        return {
            "domain": normalized_domain,
            "recommendation_model_version": MODEL_VERSION,
            "profile": normalized_profile,
            "constraints": constraints or {},
            "preferences": preferences or {},
            "result_count": 0,
            "candidates": [],
            "excluded_count": len(candidates),
            "excluded_sample": [{"item_id": str(item.get("id")), "reason": "domain_recommendation_not_enabled"} for item in candidates[:20]],
            "warnings": ["No verified public recommendation candidates are available for this domain."],
        }

    excluded: list[dict[str, str]] = []
    results: list[dict[str, Any]] = []
    for item in candidates:
        blocker = public_recommendation_blocker(item)
        if blocker:
            excluded.append({"item_id": str(item.get("id")), "reason": blocker})
            continue
        score, components = score_candidate(item, normalized_profile)
        explanation = result_explanation(item, components)
        results.append({
            **explanation,
            "eligible": True,
            "score": score,
            "matched_conditions": [],
            "failed_conditions": [],
            "unknown_conditions": [],
            "warnings": [warning for warning in [recommendation_warning(item)] if warning],
        })

    results.sort(key=lambda result: (-float(result["score"]), str(result["item_id"])))
    warnings = []
    if not results:
        warnings.append("No verified public recommendation candidates are available for this domain.")
    return {
        "domain": normalized_domain,
        "recommendation_model_version": MODEL_VERSION,
        "profile": normalized_profile,
        "constraints": constraints or {},
        "preferences": preferences or {},
        "result_count": len(results[:limit]),
        "candidates": results[:limit],
        "excluded_count": len(excluded),
        "excluded_sample": excluded[:20],
        "warnings": warnings,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--domain", required=True)
    parser.add_argument("--limit", type=int, default=5)
    parser.add_argument("--profile-json", default="{}")
    args = parser.parse_args()
    profile = json.loads(args.profile_json)
    payload = recommend(args.domain, profile=profile, limit=args.limit)
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
