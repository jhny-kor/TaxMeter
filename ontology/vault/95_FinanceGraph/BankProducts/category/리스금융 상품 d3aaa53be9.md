---
materialized_id: "category.finance.lease-finance-products"
title: "리스금융 상품"
type: "category"
domain: "bank-products"
basis_year: 2026
reviewed_at: "2026-07-04"
source_export: "korea-bank-products-ontology-2026.json"
source_urls: ["https://gongsi.crefia.or.kr/portal/financialProdInfo/leaseProd", "https://gongsi.crefia.or.kr/portal/quota/quotaFinancingDisclosureDetail60?ifgcMode=60"]
source_basis_dates: ["2026-07-03 확인"]
tags: ["graph-materialized", "bank-products", "bank-products-ontology", "lease-finance", "candidate-import"]
---

# 리스금융 상품

자동차리스 등 리스금융 상품의 월리스료, 보증금·잔존가치, 실제 운영율, 중도해지수수료와 상세 안내 확인 항목을 관리합니다.

> Graph-only materialization입니다. 원본 데이터는 JSON export가 authoritative source입니다.

## Metadata
- Materialized ID: `category.finance.lease-finance-products`
- Type: `category`

## Relations
- parents: [[95_FinanceGraph/BankProducts/domain/예금·대출·여신금융상품 온톨로지 a9d7d99466|예금·대출·여신금융상품 온톨로지]]
- sources: [[95_FinanceGraph/BankProducts/source/리스할부상품 9a1e260fc7|리스할부상품]], [[95_FinanceGraph/BankProducts/source/자동차리스 상품 리스료 비교 조회 be9f1fa187|자동차리스 상품 리스료 비교 조회]]

## Source URLs
- https://gongsi.crefia.or.kr/portal/financialProdInfo/leaseProd
- https://gongsi.crefia.or.kr/portal/quota/quotaFinancingDisclosureDetail60?ifgcMode=60
