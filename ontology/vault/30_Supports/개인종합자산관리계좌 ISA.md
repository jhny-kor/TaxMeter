---
id: "support.isa"
title: "개인종합자산관리계좌 ISA"
type: "support-program"
description: "개인이 예·적금, 펀드, 파생결합증권 등을 한 계좌에서 운용하며 세제혜택을 받을 수 있는 정책성 금융계좌입니다."
basis_year: 2026
reviewed_at: "2026-05-04"
source_urls: ["https://www.fsc.go.kr/po020201/27339", "https://www.korea.kr/briefing/actuallyView.do?newsId=148874193"]
source_basis_dates: ["2026-05-02 확인", "2026-05-03 확인"]
abolition_status: "active"
revision_status: "none_announced"
parents: ["category.policy-supports"]
children: []
related: ["tax.income"]
terms: ["term.tax-credit"]
deadlines: []
sources: ["source.fsc.isa.policy", "source.moef.isa.tax-benefit"]
criteria: [{"label": "연 납입한도", "basis": "ISA 납입금", "condition": "연간 납입한도", "limit_krw": 20000000, "source": "source.fsc.isa.policy", "criteria_kind": "limit", "basis_category": "limit", "basis_definition": "지원상품 또는 세제혜택에서 신청·납입·보증·비과세가 허용되는 최대 금액 기준입니다.", "basis_lookup": "상품 약관, 신청기관 상품설명서, 정책보도자료, 세제지원 안내에서 확인합니다.", "selection_rule": "limit_krw 또는 max_amount_krw를 초과하는 부분은 지원·비과세·공제 대상에서 제외하거나 별도 과세합니다.", "basis_source": "source.fsc.isa.policy"}, {"label": "총 납입한도", "basis": "ISA 납입금", "condition": "5년 누적 한도", "limit_krw": 100000000, "source": "source.fsc.isa.policy", "criteria_kind": "limit", "basis_category": "limit", "basis_definition": "지원상품 또는 세제혜택에서 신청·납입·보증·비과세가 허용되는 최대 금액 기준입니다.", "basis_lookup": "상품 약관, 신청기관 상품설명서, 정책보도자료, 세제지원 안내에서 확인합니다.", "selection_rule": "limit_krw 또는 max_amount_krw를 초과하는 부분은 지원·비과세·공제 대상에서 제외하거나 별도 과세합니다.", "basis_source": "source.fsc.isa.policy"}, {"label": "일반형 비과세", "basis": "계좌 순소득", "condition": "일반형 ISA", "limit_krw": 2000000, "benefit": "한도 내 비과세", "source": "source.moef.isa.tax-benefit", "criteria_kind": "limit", "basis_category": "limit", "basis_definition": "지원상품 또는 세제혜택에서 신청·납입·보증·비과세가 허용되는 최대 금액 기준입니다.", "basis_lookup": "상품 약관, 신청기관 상품설명서, 정책보도자료, 세제지원 안내에서 확인합니다.", "selection_rule": "limit_krw 또는 max_amount_krw를 초과하는 부분은 지원·비과세·공제 대상에서 제외하거나 별도 과세합니다.", "basis_source": "source.moef.isa.tax-benefit"}, {"label": "서민·농어민형 비과세", "basis": "계좌 순소득", "condition": "서민·농어민형 ISA", "limit_krw": 4000000, "benefit": "한도 내 비과세", "source": "source.moef.isa.tax-benefit", "criteria_kind": "limit", "basis_category": "limit", "basis_definition": "지원상품 또는 세제혜택에서 신청·납입·보증·비과세가 허용되는 최대 금액 기준입니다.", "basis_lookup": "상품 약관, 신청기관 상품설명서, 정책보도자료, 세제지원 안내에서 확인합니다.", "selection_rule": "limit_krw 또는 max_amount_krw를 초과하는 부분은 지원·비과세·공제 대상에서 제외하거나 별도 과세합니다.", "basis_source": "source.moef.isa.tax-benefit"}, {"label": "비과세 초과분 분리과세", "basis": "비과세 한도 초과 순소득", "condition": "비과세 한도 초과분", "rate_percent": 9, "rate_label": "분리과세율", "amount_formula": "비과세 한도 초과 순소득 × 9%", "source": "source.moef.isa.tax-benefit", "criteria_kind": "rate", "rate_basis": "비과세 한도 초과 순소득", "basis_category": "limit", "basis_definition": "지원상품 또는 세제혜택에서 신청·납입·보증·비과세가 허용되는 최대 금액 기준입니다.", "basis_lookup": "상품 약관, 신청기관 상품설명서, 정책보도자료, 세제지원 안내에서 확인합니다.", "selection_rule": "limit_krw 또는 max_amount_krw를 초과하는 부분은 지원·비과세·공제 대상에서 제외하거나 별도 과세합니다.", "basis_source": "source.moef.isa.tax-benefit"}]
law_reference: ""
tags: ["policy-finance", "tax-preferred-account"]
---

# 개인종합자산관리계좌 ISA

개인이 예·적금, 펀드, 파생결합증권 등을 한 계좌에서 운용하며 세제혜택을 받을 수 있는 정책성 금융계좌입니다.

## 최신성 메타데이터

- **기준연도**: 2026
- **확인일**: 2026-05-04
- **폐지 여부**: active
- **개정 예정 여부**: none_announced
- **출처 URL**: https://www.fsc.go.kr/po020201/27339, https://www.korea.kr/briefing/actuallyView.do?newsId=148874193
- **출처 확인일**: 2026-05-02 확인, 2026-05-03 확인

## 기준 내역

- **연 납입한도**: 기준 유형: limit; 기준항목: ISA 납입금; 선정기준 분류: limit; 조건: 연간 납입한도; 선정기준 설명: 지원상품 또는 세제혜택에서 신청·납입·보증·비과세가 허용되는 최대 금액 기준입니다.; 확인 방법: 상품 약관, 신청기관 상품설명서, 정책보도자료, 세제지원 안내에서 확인합니다.; 선정 규칙: limit_krw 또는 max_amount_krw를 초과하는 부분은 지원·비과세·공제 대상에서 제외하거나 별도 과세합니다.; 한도: 20,000,000원; 출처: [[90_Sources/ISA 정책문답|ISA 정책문답]]
- **총 납입한도**: 기준 유형: limit; 기준항목: ISA 납입금; 선정기준 분류: limit; 조건: 5년 누적 한도; 선정기준 설명: 지원상품 또는 세제혜택에서 신청·납입·보증·비과세가 허용되는 최대 금액 기준입니다.; 확인 방법: 상품 약관, 신청기관 상품설명서, 정책보도자료, 세제지원 안내에서 확인합니다.; 선정 규칙: limit_krw 또는 max_amount_krw를 초과하는 부분은 지원·비과세·공제 대상에서 제외하거나 별도 과세합니다.; 한도: 100,000,000원; 출처: [[90_Sources/ISA 정책문답|ISA 정책문답]]
- **일반형 비과세**: 기준 유형: limit; 기준항목: 계좌 순소득; 선정기준 분류: limit; 조건: 일반형 ISA; 선정기준 설명: 지원상품 또는 세제혜택에서 신청·납입·보증·비과세가 허용되는 최대 금액 기준입니다.; 확인 방법: 상품 약관, 신청기관 상품설명서, 정책보도자료, 세제지원 안내에서 확인합니다.; 선정 규칙: limit_krw 또는 max_amount_krw를 초과하는 부분은 지원·비과세·공제 대상에서 제외하거나 별도 과세합니다.; 한도: 2,000,000원; 혜택: 한도 내 비과세; 출처: [[90_Sources/ISA 세제혜택 설명|ISA 세제혜택 설명]]
- **서민·농어민형 비과세**: 기준 유형: limit; 기준항목: 계좌 순소득; 선정기준 분류: limit; 조건: 서민·농어민형 ISA; 선정기준 설명: 지원상품 또는 세제혜택에서 신청·납입·보증·비과세가 허용되는 최대 금액 기준입니다.; 확인 방법: 상품 약관, 신청기관 상품설명서, 정책보도자료, 세제지원 안내에서 확인합니다.; 선정 규칙: limit_krw 또는 max_amount_krw를 초과하는 부분은 지원·비과세·공제 대상에서 제외하거나 별도 과세합니다.; 한도: 4,000,000원; 혜택: 한도 내 비과세; 출처: [[90_Sources/ISA 세제혜택 설명|ISA 세제혜택 설명]]
- **비과세 초과분 분리과세**: 기준 유형: rate; 기준항목: 비과세 한도 초과 순소득; 선정기준 분류: limit; 조건: 비과세 한도 초과분; 선정기준 설명: 지원상품 또는 세제혜택에서 신청·납입·보증·비과세가 허용되는 최대 금액 기준입니다.; 확인 방법: 상품 약관, 신청기관 상품설명서, 정책보도자료, 세제지원 안내에서 확인합니다.; 선정 규칙: limit_krw 또는 max_amount_krw를 초과하는 부분은 지원·비과세·공제 대상에서 제외하거나 별도 과세합니다.; 분리과세율: 9%; 비율 기준: 비과세 한도 초과 순소득; 금액·적용 산식: 비과세 한도 초과 순소득 × 9%; 출처: [[90_Sources/ISA 세제혜택 설명|ISA 세제혜택 설명]]

## 상위 항목

- [[30_Supports/정책지원금·세제지원 계좌|정책지원금·세제지원 계좌]]

## 관련 항목

- [[10_Taxes/National/소득세|소득세]]

## 관련 용어

- [[40_Terms/세액공제|세액공제]]

## 근거·출처

- [[90_Sources/ISA 정책문답|ISA 정책문답]]: https://www.fsc.go.kr/po020201/27339
- [[90_Sources/ISA 세제혜택 설명|ISA 세제혜택 설명]]: https://www.korea.kr/briefing/actuallyView.do?newsId=148874193

## 온톨로지 ID

`support.isa`
