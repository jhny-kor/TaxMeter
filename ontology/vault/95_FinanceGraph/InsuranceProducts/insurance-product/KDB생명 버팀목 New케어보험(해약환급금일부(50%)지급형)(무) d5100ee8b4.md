---
materialized_id: "finance.insurance.klia.term-life.kdb생명.l330246000102460003nnn024700020244000102440001000202440001000200010244000100020001000212365"
title: "KDB생명 버팀목 New케어보험(해약환급금일부(50%)지급형)(무)"
type: "insurance-product"
domain: "insurance-products"
basis_year: 2026
reviewed_at: "2026-07-18"
source_export: "korea-insurance-products-ontology-2026.json"
source_urls: ["https://pub.insure.or.kr/compareDis/prodCompare/assurance/listNew.do?search_prodGroup=024400010002&pageIndex=1&pageUnit=20", "https://www.kdblife.co.kr/ajax.do?scrId=HDLMA002M02P", "https://pub.insure.or.kr/"]
source_basis_dates: ["2026-07-18 수집", "2026-01-01", "2026-07-03 확인"]
tags: ["graph-materialized", "insurance-products", "finance-product", "generated", "insurance", "klia", "term-life", "024400010002"]
---

# KDB생명 버팀목 New케어보험(해약환급금일부(50%)지급형)(무)

생명보험협회 공시실에 등재된 KDB생명의 정기보험 상품 '버팀목 New케어보험(해약환급금일부(50%)지급형)(무)'입니다.

> Graph-only materialization입니다. 원본 데이터는 JSON export가 authoritative source입니다.

## Metadata
- Materialized ID: `finance.insurance.klia.term-life.kdb생명.l330246000102460003nnn024700020244000102440001000202440001000200010244000100020001000212365`
- Type: `insurance-product`
- provider: KDB생명
- source_modified_at: 2026-01-01

## Relations
- parents: [[95_FinanceGraph/InsuranceProducts/category/보장성 보험 상품 65d154bf21|보장성 보험 상품]]
- related: `category.finance.source-health`, `finance.provider.0e0ff14d3971`, `category.finance.financial-provider-registry`, `category.finance.insurance-risk-signals`, `finance.risk-signal.insurance-nonpayment-rate`, `finance.risk-signal.insurance-mis-selling-rate`, `term.finance.provider-risk`
- terms: [[95_FinanceGraph/InsuranceProducts/term/보장 항목 de4e05125d|보장 항목]], [[95_FinanceGraph/InsuranceProducts/term/갱신 조건 9c8724f26d|갱신 조건]]
- sources: [[95_FinanceGraph/InsuranceProducts/source/생명보험협회 공시실 5340e15bea|생명보험협회 공시실]]

## Source URLs
- https://pub.insure.or.kr/compareDis/prodCompare/assurance/listNew.do?search_prodGroup=024400010002&pageIndex=1&pageUnit=20
- https://www.kdblife.co.kr/ajax.do?scrId=HDLMA002M02P
- https://pub.insure.or.kr/
