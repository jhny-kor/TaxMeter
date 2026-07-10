---
materialized_id: "finance.bank.policy-loan.kinfa.illegal-private-finance-prevention"
title: "서민금융진흥원 불법사금융예방대출"
type: "bank-product"
domain: "loan-products"
basis_year: 2026
reviewed_at: "2026-07-10"
source_export: "korea-loan-products-ontology-2026.json"
source_urls: ["https://www.kinfa.or.kr/financialProduct/smallLivingLoan.do"]
source_basis_dates: ["2026-07-10 수동 확인", "2026-07-03 확인"]
tags: ["graph-materialized", "loan-products", "finance-product", "manual-source-check", "policy-loan", "emergency-living-loan"]
---

# 서민금융진흥원 불법사금융예방대출

서민금융진흥원이 공시한 대부업 이용도 어려운 저신용·저소득자 생계비 정책서민금융 상품입니다.

> Graph-only materialization입니다. 원본 데이터는 JSON export가 authoritative source입니다.

## Metadata
- Materialized ID: `finance.bank.policy-loan.kinfa.illegal-private-finance-prevention`
- Type: `bank-product`
- provider: 서민금융진흥원

## Relations
- parents: [[95_FinanceGraph/DepositProducts/category/서민금융·정책대출 상품 0e019d9e26|서민금융·정책대출 상품]]
- related: `category.finance.source-health`, `finance.provider.52c6dad631a3`, `category.finance.financial-provider-registry`, `category.finance.benchmark-rates`, `finance.benchmark-rate.bok-base-rate`, `finance.benchmark-rate.cofix`
- terms: [[95_FinanceGraph/DepositProducts/term/신용점수 구간 a1f1aba325|신용점수 구간]], [[95_FinanceGraph/DepositProducts/term/대출 자금용도 b8aff106a3|대출 자금용도]], [[95_FinanceGraph/DepositProducts/term/대출 상환방식 48e83975b7|대출 상환방식]]
- sources: [[95_FinanceGraph/DepositProducts/source/불법사금융예방대출 46219e7569|불법사금융예방대출]]

## Source URLs
- https://www.kinfa.or.kr/financialProduct/smallLivingLoan.do
