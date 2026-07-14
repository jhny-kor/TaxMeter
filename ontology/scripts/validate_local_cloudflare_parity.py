#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
QUALITY = ROOT / "exports/openfin-quality-manifest-2026.json"


def main() -> int:
    manifest = json.loads(QUALITY.read_text(encoding="utf-8"))
    metrics = manifest.get("runtime_quality_metrics") or {}
    parity_errors = int(metrics.get("local_cloudflare_parity_error_count") or 0)
    if parity_errors:
        print(f"Local/Cloudflare parity validation failed: {parity_errors} errors")
        return 1
    if manifest.get("release_status") == "ready" and not manifest.get("live_search_regression"):
        print("Local/Cloudflare parity validation failed: ready release requires live_search_regression")
        return 1
    print("Local/Cloudflare parity validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
