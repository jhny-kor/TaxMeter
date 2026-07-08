---
materialized_id: "finance.bank.credit-loan.0010006.wr0002f"
title: "한국씨티은행 장기카드대출"
type: "bank-product"
domain: "loan-products"
basis_year: 2026
reviewed_at: "2026-07-04"
source_export: "korea-loan-products-ontology-2026.json"
source_urls: ["https://finlife.fss.or.kr/", "https://finlife.fss.or.kr/finlifeapi/creditLoanProductsSearch.json", "https://finlife.fss.or.kr/finlifeapi/"]
source_basis_dates: ["2026-07-04 수집", "202606", "2026-07-03 확인"]
tags: ["graph-materialized", "loan-products", "finance-product", "generated", "bank", "credit-loan", "020000"]
---

# 한국씨티은행 장기카드대출

한국씨티은행의 개인신용대출 상품 '장기카드대출' 공시 정보입니다.

> Graph-only materialization입니다. 원본 데이터는 JSON export가 authoritative source입니다.

## Metadata
- Materialized ID: `finance.bank.credit-loan.0010006.wr0002f`
- Type: `bank-product`
- provider: 한국씨티은행
- source_modified_at: 202606

## Relations
- parents: [[95_FinanceGraph/LoanProducts/category/개인신용대출 상품 9363553c74|개인신용대출 상품]]
- related: `category.finance.source-health`, `finance.provider.02541e54dbbe`, `category.finance.financial-provider-registry`, `category.finance.benchmark-rates`, `finance.benchmark-rate.bok-base-rate`, `finance.benchmark-rate.cofix`
- sources: [[95_FinanceGraph/InsuranceProducts/source/금융감독원 금융상품통합비교공시 금융상품한눈에 API 873a2ddd6d|금융감독원 금융상품통합비교공시 금융상품한눈에 API]]

## Source URLs
- https://finlife.fss.or.kr/
- https://finlife.fss.or.kr/finlifeapi/creditLoanProductsSearch.json
- https://finlife.fss.or.kr/finlifeapi/
