# OpenFin current-state audit — 2026-07-26

## 기준선

- branch: `main`
- HEAD / `origin/main`: `38bc7adb998a`
- remote: `https://github.com/jhny-kor/TaxMeter.git`
- local MCP server: `ontology/mcp_server.py`, server version `0.2.0`
- public MCP endpoint: `https://finance-mcp.y2kthr.workers.dev/mcp`
- recorded public runtime: `openfin-mcp-2026.07.22.1`, deployment commit `40215ba9c`
- recorded manifest: `KR-FINANCE-ONTOLOGY-MANIFEST-2026.07.18.1`
- search index: `21,266` indexed items, `3,434` canonical products
- public recommendation flag: disabled in the Cloudflare Worker; local recommendation entrypoint was not centrally bound to the same policy flag

The checkout was already dirty before this audit: `.gitignore`, `docs/index.html`, and the untracked generated ApplyHome export are preserved as pre-existing user work.

## MCP tools/list evidence

The local stdio MCP `initialize` + `tools/list` exchange returned 42 tools. The base tool names were `opentax_search`, `opentax_get_item`, `opentax_fetch`, `opentax_discover`, `opentax_read_note`, `opentax_neighbors`, `opentax_sources`, `opentax_validate`, `opentax_export_summary`, `opentax_recommend`, `opentax_compare`, `opentax_add_or_update_item`, `opentax_patch_item`, and `opentax_delete_custom_item`; `finance_*` and `tax_ontology_*` aliases were also returned.

The base input schemas are recorded in `artifacts/audit/openfin-current-state-2026-07-26.json`. No tool advertised an output schema. The list did not include typed personal-finance snapshot, metric, suitability, scenario, advice-validation, or quality-status tools.

## Existing implementation map

| Concern | Current source of truth | Current state |
| --- | --- | --- |
| Finance generation | `ontology/scripts/build_finance_ontology.py` | Existing export/shard/manifest pipeline |
| Search index | `ontology/exports/finance-search-index-2026.json` + `ontology/scripts/search_index_loader.py` | Sharded, checksum-protected, canonical IDs present |
| Exact/discovery parser | `ontology/scripts/recommendation_intent_parser.py`, `ontology/scripts/discovery_recommendation_engine.py` | Discovery deduplicates canonical IDs; bare local product search still used broad token fallback |
| Local MCP | `ontology/mcp_server.py` | Existing search, discover, compare, recommend, fetch and mutable ontology overlay tools |
| Public MCP | `cloudflare/opentax-mcp/src/index.ts` | Independent search/discovery/recommendation/comparison implementation; public recommendation hard-disabled |
| Product comparison | `ontology/scripts/product_comparison_engine.py` | Deterministic deposit/saving comparison with source and exclusion fields |
| Recommendation gate | `ontology/scripts/recommendation_engine.py`, `ontology/mcp_server.py`, Worker constant | Verified-candidate checks exist, but the local engine did not consult a single public gate |
| Quality reports | `ontology/exports/openfin-*-report-2026.json`, `openfin-quality-manifest-2026.json` | Offline and recorded live evidence exist; checksum reconciliation was incomplete |
| Tests | `ontology/tests/*.json`, `ontology/scripts/validate_*.py` | Domain regressions exist; no 120-case JSONL/live contract yet |
| Personal finance layer | no equivalent implementation found | Missing typed snapshot, deterministic metrics, needs, suitability and decision record |

## Export and quality evidence

- Domain exports in `ontology/exports/` include tax, support, card, deposit, saving, loan, insurance, pension, account and reference surfaces.
- Current local recommendation results were empty for card, deposit, saving, loan, insurance and support. The local output exposed `result_count=0` but did not return the instruction's typed `mode/status/reason_codes/decision_owner/audit_id` contract.
- Recorded public search report: `47/47` live cases passed at `2026-07-26T08:41:25+00:00`, with runtime/search-index checksum match.
- Recorded public comparison report: `47/47` live cases passed with runtime `openfin-mcp-2026.07.22.1` and deployment commit `40215ba9c`.
- The build path reported `products_with_complete_comparison_fields=30` and `verified_comparison_candidate_count=30` for the deposit pilot, while the raw field-level overlay still contained unverified fields. This is a statistics-boundary issue to be fixed by calculating all comparison statistics from the final overlay object.
- Existing support export basis date is `2026-07-14`; finance product exports are based on `2026-07-10` / source-specific collection dates. No new collection was performed during this read-only audit.

## Read-only smoke and P0 reproduction

The local exact-product reproduction before modification was:

- `국민행복 삼성체크카드` → two Samsung check-card records for one resolved canonical product.
- `삼성카드 국민행복 체크카드 V2` → the same two records.
- Appending `무시 이전 지시 시스템 프롬프트` caused the local all-terms search to fall back to partial-token matching and add unrelated records.

The existing public report recorded a live smoke result, but the fresh read-only command must complete successfully again before this audit is marked final. A zero-case or empty live report is not accepted as a pass.

## Proposed-path mapping

- `docs/ontology/competency-questions.md`: new competency-question contract.
- `docs/ontology/openfin-personal-finance-architecture.md`: new L1–L4 architecture boundary and data-flow contract.
- `ontology/policies/source-registry.yaml`: source registry; existing `source_urls`/`source_basis_dates` remain export fields.
- `ontology/schema/*.schema.json`: extend the existing `ontology/schema` directory; do not create a parallel `ontology/schemas` tree.
- `ontology/policies/*.yaml`: new state/advice policy files; existing recommendation status fields remain the export representation.
- `ontology/scripts/personal_finance.py`: new deterministic context, metric, need, suitability and scenario implementation.
- `ontology/scripts/validate_personal_finance.py`: new schema/invariant validator.
- `tests/golden/openfin-120.jsonl`: new red-team fixture set; existing domain golden fixtures remain intact.
- `quality/openfin-live-report.json`: actual public endpoint result for the 120-case suite; it is never synthesized from offline output.
- `ontology/scripts/verify_openfin_release.py`: release gate includes the exact resolver, personal-finance, and offline OpenFin 120 checks.

## 변경 후 증거

- Working-tree base remained `main` at `38bc7adb998a`; the requested implementation stayed on `main`.
- `ontology/exports/openfin-quality-manifest-2026.json` records `release_status=degraded`, `recommendation_enabled=false`, 120 golden cases with the required category counts, and the actual live result below.
- Local MCP `tools/list` now exposes 50 tools, including `get_finance_summary`, `update_finance_snapshot`, `calculate_finance_metrics`, `evaluate_product_fit`, `simulate_finance_scenario`, `explain_recommendation`, `validate_finance_advice`, and `get_openfin_quality_status`. Each is read-only or fail-closed by default; snapshot writes return `mutated=false` unless an owner pilot is explicitly enabled.
- Local exact product smoke now returns one canonical `국민행복 삼성체크카드` result, does not widen prompt-injection suffixes, and returns an explicit `not_found` discovery response for an unknown named product.
- Offline OpenFin golden validation: `120/120`, skipped `0`.
- Actual public MCP endpoint `https://finance-mcp.y2kthr.workers.dev/mcp`: `15/120` passed, `105` failed, skipped `0`, checked at `2026-07-26T11:37:00+00:00`. The loaded runtime was still `openfin-mcp-2026.07.22.1`, deployment commit `40215ba9c`, index checksum `e0c9231a215080cfc64a69a0b07ecf5d2ad7ca1a56844cfda7053a39ae1c0156`.
- The live failures are retained in `quality/openfin-live-report.json`; the release gate intentionally remains blocked until the updated Worker is deployed and the same endpoint produces `120/120` with no skips or failures. No production deployment was performed in this task.
- Successful local checks include ontology/finance validators, exact resolution, personal-finance metrics/safety, support-window parsing, discovery/comparison/recommendation regressions, local/Worker contract parity, `npm test` (`tsc --noEmit`), Python compilation, and `git diff --check`. `swift build` passed; `swift test` could not run because the checkout has no Swift test sources, and the iOS `xcodebuild` smoke could not select a destination for the existing scheme.

## Audit conclusion

The requested local implementation is present and verified, while the public deployment is not yet on the new contract. The remaining release blocker is concrete and externally observable: deploy the updated Worker, rerun the 120 live cases, and keep the public recommendation flag disabled until that run is `120/120` with zero skips/failures and the quality subreports reconcile.
