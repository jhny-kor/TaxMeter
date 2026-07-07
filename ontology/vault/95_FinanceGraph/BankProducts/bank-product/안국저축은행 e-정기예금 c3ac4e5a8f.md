---
materialized_id: "finance.bank.deposit.0010448.24-0002"
title: "안국저축은행 e-정기예금"
type: "bank-product"
domain: "bank-products"
basis_year: 2026
reviewed_at: "2026-07-04"
source_export: "korea-bank-products-ontology-2026.json"
source_urls: ["https://finlife.fss.or.kr/", "https://finlife.fss.or.kr/finlifeapi/depositProductsSearch.json", "https://finlife.fss.or.kr/finlifeapi/"]
source_basis_dates: ["2026-07-04 수집", "202606", "2026-07-03 확인"]
tags: ["graph-materialized", "bank-products", "finance-product", "generated", "bank", "deposit", "030300"]
---

# 안국저축은행 e-정기예금

안국저축은행의 정기예금 상품 'e-정기예금' 공시 정보입니다.

> Graph-only materialization입니다. 원본 데이터는 JSON export가 authoritative source입니다.

## Metadata
- Materialized ID: `finance.bank.deposit.0010448.24-0002`
- Type: `bank-product`
- provider: 안국저축은행
- source_modified_at: 202606

## Relations
- parents: [[95_FinanceGraph/BankProducts/category/정기예금 상품 5405e10cd5|정기예금 상품]]
- related: `category.finance.source-health`, `finance.provider.9403def1a0f6`, `category.finance.financial-provider-registry`, `category.finance.benchmark-rates`, `finance.benchmark-rate.bok-base-rate`
- sources: [[95_FinanceGraph/InsuranceProducts/source/금융감독원 금융상품통합비교공시 금융상품한눈에 API 873a2ddd6d|금융감독원 금융상품통합비교공시 금융상품한눈에 API]]

## Source URLs
- https://finlife.fss.or.kr/
- https://finlife.fss.or.kr/finlifeapi/depositProductsSearch.json
- https://finlife.fss.or.kr/finlifeapi/
