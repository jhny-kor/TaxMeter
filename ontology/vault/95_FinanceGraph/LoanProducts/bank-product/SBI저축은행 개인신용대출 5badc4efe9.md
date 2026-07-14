---
materialized_id: "finance.loan.credit-loan.0010370.151014"
title: "SBI저축은행 개인신용대출"
type: "bank-product"
domain: "loan-products"
basis_year: 2026
reviewed_at: "2026-07-14"
source_export: "korea-loan-products-ontology-2026.json"
source_urls: ["https://finlife.fss.or.kr/", "https://finlife.fss.or.kr/finlifeapi/creditLoanProductsSearch.json", "https://finlife.fss.or.kr/finlifeapi/"]
source_basis_dates: ["2026-07-14 수집", "202606", "2026-07-03 확인"]
tags: ["graph-materialized", "loan-products", "finance-product", "generated", "loan", "credit-loan", "030300"]
---

# SBI저축은행 개인신용대출

SBI저축은행의 개인신용대출 상품 '개인신용대출' 공시 정보입니다.

> Graph-only materialization입니다. 원본 데이터는 JSON export가 authoritative source입니다.

## Metadata
- Materialized ID: `finance.loan.credit-loan.0010370.151014`
- Type: `bank-product`
- provider: SBI저축은행
- source_modified_at: 202606

## Relations
- parents: [[95_FinanceGraph/DepositProducts/category/개인신용대출 상품 9363553c74|개인신용대출 상품]]
- related: `category.finance.source-health`, `finance.provider.816a18214977`, `category.finance.financial-provider-registry`, `category.finance.benchmark-rates`, `finance.benchmark-rate.bok-base-rate`, `finance.benchmark-rate.cofix`
- sources: [[95_FinanceGraph/DepositProducts/source/금융감독원 금융상품통합비교공시 금융상품한눈에 API 873a2ddd6d|금융감독원 금융상품통합비교공시 금융상품한눈에 API]]

## Source URLs
- https://finlife.fss.or.kr/
- https://finlife.fss.or.kr/finlifeapi/creditLoanProductsSearch.json
- https://finlife.fss.or.kr/finlifeapi/
