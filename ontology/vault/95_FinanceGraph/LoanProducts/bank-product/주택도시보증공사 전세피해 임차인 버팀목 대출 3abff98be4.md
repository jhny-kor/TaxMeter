---
materialized_id: "finance.bank.policy-loan.kinfa-api.200"
title: "주택도시보증공사 전세피해 임차인 버팀목 대출"
type: "bank-product"
domain: "loan-products"
basis_year: 2026
reviewed_at: "2026-07-18"
source_export: "korea-loan-products-ontology-2026.json"
source_urls: ["https://www.data.go.kr/data/15106208/openapi.do?recommendDataYn=Y", "https://nhuf.molit.go.kr/"]
source_basis_dates: ["2026-07-18 수집", "공공데이터포털 연 1회 업데이트", "2026-07-03 확인"]
tags: ["graph-materialized", "loan-products", "finance-product", "generated", "bank", "policy-loan", "kinfa", "1", "주거"]
---

# 주택도시보증공사 전세피해 임차인 버팀목 대출

서민금융진흥원 대출상품한눈에 API에 공시된 정책대출 상품 '전세피해 임차인 버팀목 대출'입니다.

> Graph-only materialization입니다. 원본 데이터는 JSON export가 authoritative source입니다.

## Metadata
- Materialized ID: `finance.bank.policy-loan.kinfa-api.200`
- Type: `bank-product`
- provider: 주택도시보증공사

## Relations
- parents: [[95_FinanceGraph/DepositProducts/category/서민금융·정책대출 상품 0e019d9e26|서민금융·정책대출 상품]]
- related: `category.finance.source-health`, `finance.provider.af06cb7789b5`, `category.finance.financial-provider-registry`, `category.finance.benchmark-rates`, `finance.benchmark-rate.bok-base-rate`, `finance.benchmark-rate.cofix`
- terms: [[95_FinanceGraph/DepositProducts/term/대출 자금용도 b8aff106a3|대출 자금용도]], [[95_FinanceGraph/DepositProducts/term/대출 상환방식 48e83975b7|대출 상환방식]]
- sources: [[95_FinanceGraph/DepositProducts/source/서민금융진흥원 대출상품한눈에 정보 서비스 8899de302b|서민금융진흥원 대출상품한눈에 정보 서비스]]

## Source URLs
- https://www.data.go.kr/data/15106208/openapi.do?recommendDataYn=Y
- https://nhuf.molit.go.kr/
