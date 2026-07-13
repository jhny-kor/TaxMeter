#!/usr/bin/env python3
from __future__ import annotations

import argparse
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
)


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
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
