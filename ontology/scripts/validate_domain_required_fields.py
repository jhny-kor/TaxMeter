#!/usr/bin/env python3
from __future__ import annotations

from calculate_recommendation_completeness import validate_exports


def main() -> int:
    errors = validate_exports()
    if errors:
        print("Domain required-field validation failed:")
        print(*[f"- {error}" for error in errors], sep="\n")
        return 1
    print("Domain required-field validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
