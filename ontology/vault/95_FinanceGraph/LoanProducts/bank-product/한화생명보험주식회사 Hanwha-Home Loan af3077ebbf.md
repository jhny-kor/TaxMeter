---
materialized_id: "finance.loan.rent-loan.0010593.303030"
title: "한화생명보험주식회사 Hanwha-Home Loan"
type: "bank-product"
domain: "loan-products"
basis_year: 2026
reviewed_at: "2026-07-10"
source_export: "korea-loan-products-ontology-2026.json"
source_urls: ["https://finlife.fss.or.kr/", "https://finlife.fss.or.kr/finlifeapi/rentHouseLoanProductsSearch.json", "https://finlife.fss.or.kr/finlifeapi/"]
source_basis_dates: ["2026-07-10 수집", "202606", "2026-07-03 확인"]
tags: ["graph-materialized", "loan-products", "finance-product", "generated", "loan", "rent-loan", "050000"]
---

# 한화생명보험주식회사 Hanwha-Home Loan

한화생명보험주식회사의 전세자금대출 상품 'Hanwha-Home Loan' 공시 정보입니다.

> Graph-only materialization입니다. 원본 데이터는 JSON export가 authoritative source입니다.

## Metadata
- Materialized ID: `finance.loan.rent-loan.0010593.303030`
- Type: `bank-product`
- provider: 한화생명보험주식회사
- source_modified_at: 202606

## Relations
- parents: [[95_FinanceGraph/DepositProducts/category/전세자금대출 상품 ad4153ff61|전세자금대출 상품]]
- related: `category.finance.source-health`, `finance.provider.2be85fd06101`, `category.finance.financial-provider-registry`, `category.finance.benchmark-rates`, `finance.benchmark-rate.bok-base-rate`, `finance.benchmark-rate.cofix`
- sources: [[95_FinanceGraph/DepositProducts/source/금융감독원 금융상품통합비교공시 금융상품한눈에 API 873a2ddd6d|금융감독원 금융상품통합비교공시 금융상품한눈에 API]]

## Source URLs
- https://finlife.fss.or.kr/
- https://finlife.fss.or.kr/finlifeapi/rentHouseLoanProductsSearch.json
- https://finlife.fss.or.kr/finlifeapi/
