from build_finance_ontology import release_policy


def main() -> int:
    degraded = release_policy(
        [{"domain": "local-government-supports", "quality_summary": {"current_refresh_complete": False, "unpreserved_missing_regions": ["광주광역시"]}}],
        {"failed_count": 0},
    )
    assert degraded["release_status"] == "degraded"
    assert degraded["recommendation_enabled"] is False
    assert "local-government-supports" in degraded["degraded_domains"]

    ready = release_policy(
        [{"domain": "local-government-supports", "quality_summary": {"current_refresh_complete": True, "unpreserved_missing_regions": []}}],
        {"failed_count": 0},
    )
    assert ready["release_status"] == "ready"
    print("OK: quality release policy blocks incomplete regional refreshes")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
