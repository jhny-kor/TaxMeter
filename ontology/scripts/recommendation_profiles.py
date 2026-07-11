#!/usr/bin/env python3
from __future__ import annotations

from typing import Any


VALID_DOMAINS = {"deposit", "saving", "card", "loan", "insurance", "support"}


def normalize_domain(domain: str) -> str:
    normalized = domain.strip().lower().replace("_", "-")
    aliases = {
        "bank-deposit": "deposit",
        "time-deposit": "deposit",
        "savings": "saving",
        "credit-card": "card",
        "check-card": "card",
        "policy-loan": "loan",
        "local-support": "support",
    }
    normalized = aliases.get(normalized, normalized)
    if normalized not in VALID_DOMAINS:
        raise ValueError(f"unsupported recommendation domain: {domain}")
    return normalized


def normalize_profile(profile: dict[str, Any] | None) -> dict[str, Any]:
    if not profile:
        return {}
    normalized: dict[str, Any] = {}
    for key, value in profile.items():
        if value is not None and value != "" and value != []:
            normalized[str(key)] = value
    return normalized
