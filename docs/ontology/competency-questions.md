# OpenFin personal-finance competency questions

이 문서는 “상품을 하나 골라 주는 검색기”가 아니라, 출처가 확인된 개인 금융 의사결정 보조 계층이 답해야 하는 질문을 고정한다. 각 질문은 결정 단계와 회귀 테스트 ID를 함께 가진다. `recommendation` 단계는 공개적으로 비활성화되어 있으며, 현재 답변은 조회·비교·계산·시나리오·차단 사유를 우선한다.

| ID | 질문 | 단계 | 회귀 테스트 |
| --- | --- | --- | --- |
| CQ-001 | 현재 순자산은 얼마인가? | metrics | PF-NET-WORTH-001 |
| CQ-002 | 월 순현금흐름은 흑자인가? | metrics | PF-CASHFLOW-001 |
| CQ-003 | 저축률은 얼마인가? | metrics | PF-SAVINGS-RATE-001 |
| CQ-004 | 비상자금은 필수지출 몇 개월분인가? | metrics | PF-EMERGENCY-001 |
| CQ-005 | 부채상환비율은 얼마인가? | metrics | PF-DSR-001 |
| CQ-006 | 부채의 가중평균 금리는 얼마인가? | metrics | PF-DEBT-RATE-001 |
| CQ-007 | 명시한 유동성 필요액과 유동자산의 차이는 얼마인가? | metrics | PF-LIQUIDITY-GAP-001 |
| CQ-008 | 목표별 자금부족액은 얼마인가? | metrics | PF-GOAL-GAP-001 |
| CQ-009 | 자산군 집중도는 얼마인가? | metrics | PF-CONCENTRATION-001 |
| CQ-010 | 명시된 보장 필요액과 현재 보장액의 차이는 얼마인가? | metrics | PF-INSURANCE-GAP-001 |
| CQ-011 | 계산에 필요한 필드가 빠졌는가? | safety | PF-MISSING-001 |
| CQ-012 | 현금흐름 적자가 있으면 어떤 안정화가 먼저인가? | needs | PF-NEED-CASHFLOW-001 |
| CQ-013 | 고금리 부채가 있으면 상환 시나리오가 먼저인가? | needs | PF-NEED-DEBT-001 |
| CQ-014 | 비상자금 미달이면 원금·유동성 보호가 먼저인가? | needs | PF-NEED-EMERGENCY-001 |
| CQ-015 | 유동성 갭이 있으면 만기·잠금 상품을 제외하는가? | fit | PF-FIT-LIQUIDITY-001 |
| CQ-016 | 단기 목표는 유동성과 원금보존 기준을 갖는가? | needs | PF-NEED-SHORT-GOAL-001 |
| CQ-017 | 장기 목표와 단기 목표를 구분하는가? | needs | PF-NEED-LONG-GOAL-001 |
| CQ-018 | RiskTolerance와 RiskCapacity를 분리하는가? | risk | PF-RISK-SEPARATION-001 |
| CQ-019 | 상품 금리가 데이터에 없을 때 추정하지 않는가? | safety | PF-NO-INVENTED-RATE-001 |
| CQ-020 | 상품의 판매상태가 active/listed인가? | fit | PF-FIT-STATUS-001 |
| CQ-021 | 상품 출처가 공식 1차 출처인가? | evidence | PF-FIT-SOURCE-001 |
| CQ-022 | 상품 데이터가 stale이면 제외하는가? | fit | PF-FIT-STALE-001 |
| CQ-023 | 검증되지 않은 필드는 unknown으로 남는가? | fit | PF-FIT-UNKNOWN-001 |
| CQ-024 | hard filter 실패와 정보 부족을 구분하는가? | fit | PF-FIT-FAIL-VS-UNKNOWN-001 |
| CQ-025 | 적합성 평가는 추천과 다른 상태인가? | fit | PF-FIT-NOT-RECOMMENDATION-001 |
| CQ-026 | 점수 구성요소와 입력 근거를 반환하는가? | fit | PF-SCORE-LINEAGE-001 |
| CQ-027 | 사용자가 제공하지 않은 우대조건을 충족했다고 가정하지 않는가? | comparison | PF-NO-ASSUMED-CONDITION-001 |
| CQ-028 | 비교값은 최종 comparison object에서 계산되는가? | comparison | PF-COMPARISON-FINAL-OBJECT-001 |
| CQ-029 | 비교 결과에 data_as_of와 source가 있는가? | comparison | PF-COMPARISON-SOURCE-001 |
| CQ-030 | 고정기간이 아닌 지원사업 신청창을 날짜 하나로 강제하지 않는가? | evidence | PF-APPLICATION-WINDOW-001 |
| CQ-031 | 사용자 금융 상태는 원문 계좌·카드·식별자로 받지 않는가? | privacy | PF-SENSITIVE-INPUT-001 |
| CQ-032 | snapshot은 기본적으로 저장되지 않는가? | privacy | PF-TRANSIENT-SNAPSHOT-001 |
| CQ-033 | snapshot 쓰기는 owner와 명시 확인을 요구하는가? | governance | PF-OWNER-WRITE-001 |
| CQ-034 | 추천 공개 플래그가 꺼져 있으면 verified 후보도 빈 배열인가? | governance | PF-RECOMMENDATION-FAIL-CLOSED-001 |
| CQ-035 | 차단 응답에 decision_owner=user가 있는가? | governance | PF-DECISION-OWNER-001 |
| CQ-036 | 차단 응답에 missing_information과 limitations가 있는가? | governance | PF-SAFETY-CONTRACT-001 |
| CQ-037 | 추천 후보가 0이면 recommendation status가 ready가 아닌가? | governance | PF-NO-CANDIDATE-001 |
| CQ-038 | 추천 후보가 있더라도 공식 검증·만료·상태를 다시 확인하는가? | governance | PF-CANDIDATE-RECHECK-001 |
| CQ-039 | 설명이 포함·제외 이유와 tradeoff를 함께 말하는가? | explanation | PF-EXPLANATION-001 |
| CQ-040 | 설명에 확인되지 않은 금융 숫자를 생성하지 않는가? | explanation | PF-EXPLANATION-NO-INVENTION-001 |
| CQ-041 | 시나리오가 가정과 한계를 명시하는가? | scenario | PF-SCENARIO-ASSUMPTIONS-001 |
| CQ-042 | 시나리오가 상품 승인·수익을 보장한다고 말하지 않는가? | scenario | PF-SCENARIO-NO-PROMISE-001 |
| CQ-043 | named product 검색에서 provider가 공식명과 함께 확인되는가? | resolver | RESOLVE-EXACT-001 |
| CQ-044 | named product 검색에서 product type mismatch를 제외하는가? | resolver | RESOLVE-TYPE-001 |
| CQ-045 | named product 검색이 canonical product를 중복 반환하지 않는가? | resolver | RESOLVE-CANONICAL-001 |
| CQ-046 | 상품을 찾지 못하면 any-term 관련 상품으로 폴백하지 않는가? | resolver | RESOLVE-NOT-FOUND-001 |
| CQ-047 | prompt-injection suffix가 상품명 증거가 되지 않는가? | security | RESOLVE-PROMPT-INJECTION-001 |
| CQ-048 | provider 없는 동명 상품은 ambiguous로 남는가? | resolver | RESOLVE-AMBIGUOUS-001 |
| CQ-049 | 출처 assertion마다 source_id와 수집·검증 시각이 있는가? | evidence | SRC-ASSERTION-LINEAGE-001 |
| CQ-050 | collected_at ≤ normalized_at ≤ verified_at ≤ published_at 불변식을 검사하는가? | evidence | SRC-TIME-INVARIANT-001 |
| CQ-051 | source conflict는 ready recommendation으로 승격되지 않는가? | evidence | SRC-CONFLICT-001 |
| CQ-052 | stale evidence는 comparison/reference와 recommendation을 구분하는가? | evidence | SRC-STALE-001 |
| CQ-053 | PromotionReceipt 없이 recommendation candidate가 되는가? | governance | SRC-PROMOTION-RECEIPT-001 |
| CQ-054 | 공개 public 역할은 개인 snapshot을 조회하지 못하는가? | auth | AUTH-PUBLIC-PERSONAL-001 |
| CQ-055 | prompt injection이 시스템 지시를 덮어쓰지 못하는가? | security | AUTH-PROMPT-INJECTION-001 |
| CQ-056 | 품질 manifest가 live 실행·expected·passed·failed를 보존하는가? | release | REL-LIVE-QUALITY-001 |
| CQ-057 | live_case_count=0을 pass로 표시하지 않는가? | release | REL-LIVE-NONZERO-001 |
| CQ-058 | local/Worker 비교가 같은 최종 객체를 기준으로 하는가? | release | REL-PARITY-001 |
| CQ-059 | recommendation feature flag가 manifest와 runtime에서 일치하는가? | release | REL-FLAG-PARITY-001 |
| CQ-060 | 사용자가 최종 결정을 내린다는 사실이 모든 advice 응답에 남는가? | governance | REL-USER-DECISION-001 |

## 현재 활성 수준

- L1: 공식 출처 기반 조회 — 활성.
- L2: 예금·적금 조건 비교 — 검증된 현재 listing과 명시 입력에 한정.
- L3: owner-only 개인 snapshot pilot — 구조와 계산은 구현했지만 저장·공개 추천은 비활성.
- L4: 개인 금융 recommendation — `PUBLIC_RECOMMENDATION_ENABLED=false`로 차단.
- L5: 가입·결제·이체·주문 실행 — 범위 밖.
