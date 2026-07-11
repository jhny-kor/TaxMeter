from import_gov24_local_supports import REGION_ALIASES, region_metadata
from build_finance_ontology import score_search_index_item, search_index_item


def main() -> int:
    metadata = region_metadata("전남광주통합특별시")
    assert metadata["region_code"] == "전남광주통합특별시"
    assert metadata["predecessor_region_codes"] == ["광주광역시", "전라남도"]
    assert REGION_ALIASES["광주광역시"] == "전남광주통합특별시"
    assert REGION_ALIASES["전라남도"] == "전남광주통합특별시"
    indexed = search_index_item({"id": "support.test", "jurisdiction_aliases": metadata["region_aliases"]}, "support")
    assert "광주광역시" in indexed["search_text"]
    assert score_search_index_item(indexed, "광주광역시") >= 95
    print("OK: 전남광주통합특별시 source key and predecessor aliases verified")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
