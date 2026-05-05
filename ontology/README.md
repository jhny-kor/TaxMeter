# OpenTax Obsidian Vault

이 디렉터리는 TaxMeter 앱과 분리된 OpenTax 작업 공간입니다.
앱 런타임 코드가 아니라 학습, 검증, 추후 앱 데이터 export를 위한 독립
지식베이스입니다.

## 사용 방법

1. vault 생성

   ```sh
   python3 ontology/scripts/generate_vault.py
   ```

2. Obsidian에서 열기

   Obsidian에서 `ontology/vault` 폴더를 vault로 엽니다.

3. 검증

   ```sh
   python3 ontology/scripts/validate_ontology.py
   ```

4. 앱이나 다른 도구용 JSON 확인

   ```text
   ontology/exports/korea-tax-ontology-2026.json
   ontology/exports/korea-local-government-supports-ontology-2026.json
   ontology/exports/finance-ontology-manifest.json
   ```

5. 금융상품 온톨로지 생성

   ```sh
   python3 ontology/scripts/import_finance_products.py --skip-finlife
   python3 ontology/scripts/build_finance_ontology.py
   python3 ontology/scripts/validate_finance_ontology.py
   ```

   금감원 금융상품한눈에 실상품 데이터까지 수집하려면 `FINLIFE_API_KEY`를
   설정하고 `--skip-finlife` 없이 실행합니다.

## MCP 사용

다른 LLM 클라이언트 연결과 패키지 설치 방법은
[MCP_INSTALL.md](MCP_INSTALL.md)를 봅니다.

로컬 MCP 서버 실행 파일:

```sh
python3 ontology/mcp_server.py
```

Codex 등록 예시:

```toml
[mcp_servers.finance]
command = "python3"
args = ["/path/to/TaxMeter/ontology/mcp_server.py"]
enabled = true
startup_timeout_sec = 10
```

제공 도구:

- `finance_search`: 항목 검색.
- `finance_get_item`: ID로 항목 메타데이터 조회.
- `finance_read_note`: ID 또는 vault 상대경로로 Obsidian 노트 읽기.
- `finance_neighbors`: 상위/하위/관련/용어/기한/출처 이웃 조회.
- `finance_sources`: 항목의 근거 출처와 URL 조회.
- `finance_validate`: vault 검증 실행.
- `finance_export_summary`: JSON export 요약.
- `finance_add_or_update_item`: custom overlay 항목 추가 또는 교체.
- `finance_patch_item`: built-in 또는 custom 항목을 custom overlay로 수정.
- `finance_delete_custom_item`: custom overlay 항목 삭제.

기존 클라이언트 호환을 위해 `opentax_*`, `tax_ontology_*` 도구명도 legacy alias로 유지합니다.

쓰기 도구는 기본 공식 데이터 정의를 직접 바꾸지 않고
`ontology/custom/items.json`에 overlay를 저장한 뒤 vault와 JSON export를
재생성하고 검증한다. 검증 실패 시 overlay를 이전 상태로 되돌린다.

## 완전성 기준

- 국세기본법 제2조의 국세 세목 12개를 `NATIONAL_TAX_IDS`로 고정합니다.
- 지방세기본법 제8조의 지방세 세목 11개를 `LOCAL_TAX_IDS`로 고정합니다.
- 국세청 법인세 공제감면 안내의 지원제도 항목을
  `CORPORATE_SUPPORT_IDS`로 고정합니다.
- 모든 항목은 설명과 공식/법률 출처를 가져야 합니다.
- `parents`, `children`, `related`, `terms`, `deadlines`, `sources`는 실제
  노트를 가리켜야 합니다.
- 부모/자식 연결은 양방향이어야 합니다.

## 편집 원칙

- 항목을 추가하거나 삭제하면 `ontology/scripts/generate_vault.py`의 매니페스트와
  데이터 정의를 먼저 수정하고 vault를 재생성합니다.
- 수작업으로 vault Markdown만 바꾸면 다음 생성 때 덮어써질 수 있습니다.
- 세법과 지원제도는 바뀔 수 있으므로 배포 또는 학습 자료 확정 전 공식 링크를
  다시 확인합니다.
