#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import sys


SCRIPTS = (
    "validate_ontology.py",
    "validate_finance_ontology.py",
    "validate_recommendation_contract.py",
    "validate_runtime_catalog_consistency.py",
    "validate_canonical_product_merge.py",
    "validate_finance_golden_case_count.py",
    "validate_query_semantics.py",
    "validate_discovery_recommendation.py",
    "validate_discovery_regression.py",
    "validate_candidate_deduplication.py",
    "validate_confidence_grades.py",
    "validate_card_recommendation_safety.py",
    "validate_loan_recommendation_guard.py",
    "validate_insurance_recommendation_status.py",
    "validate_recommendation_regression.py",
    "validate_comparison_regression.py",
    "validate_verification_evidence.py",
    "validate_quality_release_policy.py",
    "validate_structured_summary.py",
)


def require_production_release_ready(root: Path) -> int:
    manifest_path = root.parent / "exports" / "openfin-quality-manifest-2026.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("release_status") == "ready":
        return 0
    reasons = manifest.get("blocking_reasons") or ["quality manifest is not ready"]
    print("FAIL: production deployment is blocked by the quality manifest:")
    for reason in reasons:
        print(f"- {reason}")
    return 1


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--build", action="store_true")
    parser.add_argument("--require-live", action="store_true")
    args = parser.parse_args()
    root = Path(__file__).resolve().parent
    if args.build:
        completed = subprocess.run([sys.executable, str(root / "build_finance_ontology.py")], check=False)
        if completed.returncode:
            return completed.returncode
    scripts = [*SCRIPTS, *( ["validate_quality_manifest_consistency.py"] if args.require_live else [])]
    for script in scripts:
        completed = subprocess.run([sys.executable, str(root / script)], check=False)
        if completed.returncode:
            return completed.returncode
    return require_production_release_ready(root)


if __name__ == "__main__":
    raise SystemExit(main())
