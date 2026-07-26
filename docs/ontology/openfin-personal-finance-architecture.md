# OpenFin 개인 금융 의사결정 보조 아키텍처

## 결정 경계

```text
transient snapshot
  -> schema / sensitive-field validation
  -> deterministic metrics
  -> primary financial need
  -> source-backed discovery
  -> hard eligibility filter
  -> fit evaluation (unknown stays unknown)
  -> comparison from final comparison object
  -> explanation / scenario
  -> recommendation case only in owner pilot
```

현재 공개 런타임은 마지막 단계에서 `PUBLIC_RECOMMENDATION_ENABLED=false`를 적용한다. 따라서 verified product metadata가 존재하더라도 public `recommend`는 `status=blocked`, `candidates=[]`, `decision_owner=user`를 반환한다. 사용자가 제공한 snapshot은 호출 중에만 정규화하고 기본적으로 저장하지 않는다.

## 핵심 엔티티와 관계

- `Person` — `Household` — `ConsentRecord`
- `Household` — `FinancialSnapshot` — `IncomeStream`, `ExpenseProfile`, `AssetPosition`, `LiabilityPosition`
- `FinancialSnapshot` — `InsuranceCoverage`, `CardSpendingProfile`, `TaxContext`, `FinancialGoal`, `LiquidityRequirement`, `RiskTolerance`, `RiskCapacity`
- `FinancialGoal` — `FinancialNeed` — `SuitabilityEvaluation` — `RecommendationCase`
- `ProductOffer` — `ProductVariant` — `Provider` — `SourceAssertion` — `PromotionReceipt`

`RiskTolerance`는 선호·감내 수준이고 `RiskCapacity`는 손실을 감당할 재무 여력이다. 한 필드를 다른 필드의 대리값으로 사용하지 않는다.

## 데이터와 증거

모든 상품·지원·비교 값은 `source_id`, `source_url`, `locator`, `collected_at`, `source_checksum`, `verification_status`, `valid_from`, `valid_to`를 가진 assertion으로 추적한다. `source-registry.yaml`은 authority class, refresh SLA, parser, 이용조건, 활성화와 추천 적격성을 함께 관리하며, 집계 사이트는 보조 조회로만 분류한다. 시간 순서는 `collected_at <= normalized_at <= verified_at <= published_at`를 검사한다. `fixed`가 아닌 지원 신청창은 `rolling`, `until_budget_exhausted`, `periodic`, `tbd`, `unknown`으로 보존한다.

공식 1차 출처가 없는 항목은 `reference_only` 또는 `comparison_candidate`까지만 허용한다. 추천 승격에는 공식 primary evidence, 현재 판매상태, 모든 hard filter 해소, 만료 유효성, `PromotionReceipt`가 필요하다.

## API 안전 계약

`recommend`와 `RecommendationCase`의 최소 응답은 다음 필드를 반드시 보존한다.

```json
{
  "mode": "education|decision_support|recommendation",
  "status": "blocked|insufficient_information|ready",
  "reason_codes": [],
  "profile_as_of": null,
  "data_as_of": null,
  "assumptions": [],
  "missing_information": [],
  "financial_needs": [],
  "candidates": [],
  "decision_owner": "user",
  "limitations": [],
  "audit_id": "fin-..."
}
```

모든 MCP tool output은 이 도메인 계약과 별개로 `as_of`, `source`, `confidence`, `limitations`를 포함한 provenance envelope를 가진다. 공개 `recommend`는 원문 `profile`, `constraints`, `preferences`를 반사하지 않고 허용된 필드명 요약만 남긴다.

## 운영 수용 기준

1. named product는 provider·공식 상품명·product type을 먼저 확인하고 canonical ID로 dedupe한다.
2. 이름 검색 실패는 any-term 관련 상품으로 폴백하지 않는다.
3. `unknown`은 hard filter 통과가 아니다.
4. 비교 통계는 실제 최종 비교 객체에서만 산출한다.
5. local/Worker 응답은 같은 safety contract와 source/as-of 의미를 사용한다.
6. offline 120 golden cases와 live 실행 결과를 분리 기록하며, live `case_count=0`은 pass가 아니다.
7. 공개 추천 플래그를 켜기 전에는 owner auth, 회귀, source freshness, rollback, reviewer receipt를 모두 확인한다.
8. 배포 전 검증은 offline 계약과 정적 검사만 수행하고, 새 Worker 배포 뒤 live 120/120·매니페스트 정합성·공개 smoke를 별도 post-deploy gate로 판정한다.
