# OpenFin 금융정보 온톨로지 2026

기준일: 2026-07-07 (export basis_date 2026-07-04)

OpenFin은 세금(OpenTax), 지자체 지원금, 카드·은행·보험 금융상품, 금융
기준정보를 하나의 노드 스키마로 통합한 금융정보 온톨로지다. 원본 정의와
빌드는 `ontology/scripts/`에 있으며, 산출물은 `ontology/exports/`의 JSON
export와 `ontology/vault/`의 Obsidian 노트로 나온다. 이 문서는 현재 구조와
내용을 점검하고, 수집 방법과 보완 방향을 기록한다.

## 1. 현재 구조

### 계층

| 계층 | 위치 | 역할 |
| --- | --- | --- |
| 스키마 | `ontology/schema/node.schema.json` | 전 도메인 공용 노드 구조. 타입 30여 종, `criteria[]`(근거·조건·금액·금리·법령), 관계 배열(`parents/children/related/terms/deadlines/sources`) |
| 원천 스냅샷 | `ontology/custom/finance/*.generated.json` | FinLife·KDIC·KLIA·KINFA API 수집 원본. `raw` 필드에 API 응답 보존 |
| 빌드 | `import_finance_products.py` → `build_finance_ontology.py` | 수집 → 관계·criteria·운영상태(enrich) → export 생성 |
| 검증 | `validate_finance_ontology.py`, `validate_ontology.py` | 상품 필수필드, 관계 무결성, 상태 게이트, 검색 회귀 5종 |
| 배포 | `ontology/exports/` + `docs/opentax/` 미러 | 도메인 export 6종, 검색 인덱스, 품질 매니페스트 2종, checksum 7종 |
| 소비 | `ontology/mcp_server.py`, `cloudflare/opentax-mcp/` | `finance_search` 등 MCP 도구. custom overlay로 쓰기 분리 |
| 그래프 | `materialize_finance_graph_vault.py` → `vault/95_FinanceGraph/` | JSON export를 Obsidian 그래프 노드로 materialize (JSON이 authoritative) |

### 도메인 구성과 규모

| 도메인 | export | 항목 | 상품 | 비고 |
| --- | --- | ---: | ---: | --- |
| 세금 | korea-tax-ontology | 374 | - | OpenTax vault 378노트와 동기 |
| 지자체 지원금 | korea-local-government-supports | 7,820 | - | active 5,168 / closed 343 / unknown 2,309 |
| 카드 | korea-card-products | 1,028 | 1,005 | active 650, reference_only 355 |
| 은행 | korea-bank-products | 1,407 | 1,363 | 예금 430·적금 335·정책대출 320·신용 113·주담대 108·전세 57 |
| 보험 | korea-insurance-products | 1,079 | 1,061 | 전건 active, KLIA 공시 리스트 기반 |
| 기준정보 | korea-finance-reference | 9,651 | 0 | 예금자보호 레지스트리 9,380 + provider 216 + 기준금리·리스크 신호 |
| 검색 인덱스 | finance-search-index | 21,342 | - | MCP search 전용 경량 인덱스 |

2026-07-07 재분류: 예금자보호 등재 목록(KDIC 9,380건, 대부분 보험사 상품)은
은행 상품군이 아니라 소비자 보호 레지스트리이므로 `financial-product` 타입으로
finance-reference에 재배치했다. 은행 export는 실제 금리상품 1,363건만 남는다.

### 품질 체계 (작동 확인됨)

- 관계 무결성: broken_relation_count 0, export 간 교차참조 검증.
- 상태 게이트: `product_status/sales_status/status`, stale disclosure 차단,
  active-without-criteria 차단, 만료 지원금 active 차단.
- 검색 회귀: P0 세금 질의 5종 + closed 지원금 노출 차단 테스트.
- 출처 리스크 추적: `source_access_risks`에 403·키미비 출처를 상태별 기록,
  데이터를 지어내지 않고 대기 처리.
- provenance: 전 상품 `source_urls`, `source_basis_dates`, `source_api`, `raw` 보존.

검증 명령:

```sh
python3 ontology/scripts/validate_finance_ontology.py
python3 ontology/scripts/validate_ontology.py
```

## 2. 보완 필요 내용 (우선순위순)

| # | 내용 | 규모 | 원인/비고 |
| --- | --- | --- | --- |
| 1 | 보험 담보(coverage) 깊이 부족 | 1,055/1,061 incomplete | KLIA 공시실 리스트 표만 수집(상품명·보험료·갱신). 담보별 금액·면책·감액 없음. 실손·변액 API는 403 대기 |
| 2 | 보험 도메인 오분류 | 18건 | 보험사 대출상품(상업용부동산담보대출, SOHO운영자금대출 등)이 insurance-product로 들어감. product_kind 재판정 필요 |
| 3 | active 은행상품 criteria 공백 | 112건 (신용대출 108) | FinLife optionList가 빈 상품. 금리 미확인 상태로 active 노출 중 |
| 4 | 지자체 지원금 상태 unknown | 2,309건 | 정부24 원본에 신청기간 정보 없음. 상태 재확인 크롤 또는 unknown 표시 강화 필요 |
| 5 | 카드 혜택 조건 불완전 | 127건 / reference_only 355건 | 공시 텍스트 파싱 한계. 조건 정규화 규칙 추가 여지 |
| 6 | provider 레지스트리가 문자열 기반 | 216 노드 | 상품 provider 문자열 해시로 생성. FSC 금융회사 API로 공식 코드·주소·상태 매칭 필요 |
| 7 | 그래프 소스 노트 홈 폴더 임의성 | - | 공유 출처 노드가 특정 도메인 폴더에 생성돼 교차 링크됨. 링크는 정상, 표시상 문제 |

## 3. 수집 방법

### 현재 수집 경로

```sh
python3 ontology/scripts/import_finance_products.py   # FinLife·KDIC·KLIA·KINFA 수집 → custom/finance/*.generated.json
python3 ontology/scripts/build_finance_ontology.py    # export 6종 + 인덱스 + 매니페스트 재생성
python3 ontology/scripts/validate_finance_ontology.py # 게이트 통과 확인
python3 ontology/scripts/materialize_finance_graph_vault.py  # 그래프 vault 갱신
```

- FinLife(금융상품한눈에): `FINLIFE_API_KEY` 필요, 없으면 `--skip-finlife`.
- KDIC 예금자보호·KINFA 정책대출: `DATA_GO_KR_SERVICE_KEY` 필요.
- 판매중단 이력은 `--include-kdic-ended-products` 옵션으로만 수집.
- FinLife 공시월(dcls_month)이 월 단위이므로 **월 1회 재수집 → 빌드 → 검증 →
  그래프 materialize**를 기본 주기로 한다. 재수집 후 docs/opentax 미러 동기
  커밋까지가 한 사이클이다.

### 키·권한 확보 시 열리는 출처 (api_required_sources)

| 출처 | 필요 | 용도 |
| --- | --- | --- |
| BOK ECOS | `BOK_ECOS_API_KEY` (신규) | 기준금리·시장금리·환율 시계열. 현재 benchmark-rate 노드만 존재, 값 없음 |
| FSC 실손의료보험 | 서비스 권한 (현재 403) | 실손 유형·담보·성별연령 보험료 → 보완 #1 직접 해소 |
| FSC 변액보험 | 서비스 권한 (현재 403) | 펀드 기준가·순자산·운용사 |
| KINFA 취급기관·상담센터 | 서비스 권한 (현재 403) | 정책대출 취급기관 상세, 서민금융 지점망 |
| FSC 금융회사 기본·신용 | 활용신청 | provider 노드를 공식 코드·재무·상장상태와 매칭 → 보완 #6 해소 |
| FSC 펀드·퇴직연금·투자통계 | 활용신청 | 펀드/퇴직연금 신규 도메인 상품 행 |

### 공개 웹 수집 후보 (API 없이 가능)

- 은행연합회 소비자포털: 예대금리차, COFIX 최신값 (엑셀 스크레이프).
- 저축은행중앙회: 예·적금 상품별 금리표.
- KOFIA 펀드다모아: 펀드 상세, 운용사·판매사 연결.
- FSS 통합연금포털: 연금저축 수익률·수수료·위험등급.
- FSS FINE 포털: 숨은 금융자산, 소비자 보호 신호.

## 4. 방향성

### 단기 (키·권한 확보 즉시)

1. 실손·변액 403 해소 후 보험 담보 보강 — 보완 #1이 최대 품질 갭.
2. 보험 오분류 18건 재판정 규칙 추가 (`대출` 키워드 + 담보 부재 → 별도 분류).
3. criteria 공백 active 은행상품 112건을 unknown으로 강등하거나 재수집 확인.
4. BOK ECOS 키 확보로 기준금리 실값 주입 — 상품 금리 비교의 기준선.

### 중기

1. 펀드·퇴직연금 도메인 export 신설 (FSC API 활용신청 후). 기존 도메인과
   동일 패턴: generated 스냅샷 → 빌드 → 게이트 → 매니페스트 등록.
2. provider 레지스트리를 FSC 금융회사 코드와 매칭해 재무·신용 리스크를
   상품 추천 신호로 연결.
3. 지자체 지원금 unknown 2,309건 상태 재확인 파이프라인.
4. 서민금융상품기본정보(inclusive-finance) 수집으로 KINFA 상품과 중복 제거
   후 정책금융 커버리지 확대. 실적 데이터는 별도 metric export로 분리.

### 장기

1. 금리·수익률 시계열 관리 — 현재는 스냅샷 교체 방식이라 이력이 없다.
   disclosure_month 단위 이력 보존을 검토한다.
2. 세금↔금융 교차 추론 심화 — ISA·연금저축 세액공제(OpenTax)와 해당
   금융상품(OpenFin)을 criteria 수준에서 연결해 "세제혜택 계좌 추천" 같은
   질의를 온톨로지만으로 응답.
3. 상태 재검증 자동화 — last_verified_at 기반으로 오래된 노드를 주기적으로
   재확인 대상으로 뽑는 운영 루프.

## 5. 원칙

- JSON export가 authoritative source다. vault 그래프 노트와 docs 미러는
  파생물이며 빌드로만 갱신한다.
- 접근 불가 출처의 데이터는 만들지 않는다. `source_access_risks`에 대기
  상태로 기록하고 권한이 열리면 수집한다.
- 상품군과 참조 레지스트리를 구분한다. 상품 수(product_count)는 실제
  비교·추천 가능한 상품만 센다.
- 모든 수치·조건은 `criteria[]`에 근거(basis)·출처(source)·조회방법
  (basis_lookup)과 함께 기록한다.
