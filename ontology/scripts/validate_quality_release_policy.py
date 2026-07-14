from build_finance_ontology import release_policy


def main() -> int:
    degraded = release_policy(
        [{"domain": "local-government-supports", "quality_summary": {"current_refresh_complete": False, "unpreserved_missing_regions": ["광주광역시"]}}],
        {"failed_count": 0},
    )
    assert degraded["release_status"] == "degraded"
    assert degraded["recommendation_enabled"] is False
    assert "local-government-supports" in degraded["degraded_domains"]

    incomplete_pilots = release_policy(
        [{"domain": "local-government-supports", "quality_summary": {"current_refresh_complete": True, "unpreserved_missing_regions": []}}],
        {"failed_count": 0},
    )
    assert incomplete_pilots["release_status"] == "degraded"
    assert "deposit-products verified pilot below 30" in incomplete_pilots["blocking_reasons"]
    print("OK: quality release policy blocks incomplete regional refreshes and missing verified pilots")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
