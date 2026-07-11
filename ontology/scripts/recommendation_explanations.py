#!/usr/bin/env python3
from __future__ import annotations

from typing import Any


def basis_dates(item: dict[str, Any]) -> list[str]:
    return [str(value) for value in item.get("source_basis_dates") or [] if value]


def recommendation_warning(item: dict[str, Any]) -> str | None:
    status = item.get("recommendation_status")
    scope = item.get("recommendation_scope")
    if status != "verified_recommendation_candidate":
        return f"blocked: recommendation_status={status or 'missing'}"
    if scope != "public_recommendation":
        return f"blocked: recommendation_scope={scope or 'missing'}"
    if not item.get("verification_evidence"):
        return "blocked: verification_evidence missing"
    return None


def result_explanation(item: dict[str, Any], score_components: dict[str, float]) -> dict[str, Any]:
    return {
        "item_id": item.get("id"),
        "title": item.get("title"),
        "provider": item.get("provider"),
        "recommendation_status": item.get("recommendation_status"),
        "recommendation_scope": item.get("recommendation_scope"),
        "score_components": score_components,
        "source_basis_dates": basis_dates(item),
        "last_verified_at": item.get("last_verified_at"),
        "recommendation_model_version": item.get("recommendation_model_version"),
    }
