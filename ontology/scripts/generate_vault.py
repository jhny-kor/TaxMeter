#!/usr/bin/env python3
"""Generate the standalone Korean tax ontology Obsidian vault.

The generated Markdown files are intentionally separate from the TaxMeter app.
Obsidian is the human-facing study surface; the frontmatter is the machine-
readable ontology surface.
"""

from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VAULT = ROOT / "vault"
EXPORT_PATH = ROOT / "exports" / "korea-tax-ontology-2026.json"
CUSTOM_ITEMS_PATH = ROOT / "custom" / "items.json"


SOURCES = {
    "source.national-tax-framework-act.2026.article2": {
        "title": "국세기본법 제2조",
        "publisher": "국가법령정보센터",
        "url": "https://www.law.go.kr/lsLawLinkInfo.do?chrClsCd=010202&lsJoLnkSeq=900637068",
        "basis_date": "시행 2026-01-01",
        "description": "국세 세목, 세법, 원천징수, 과세기간, 과세표준 등 국세 기본 용어의 법률상 근거입니다.",
    },
    "source.local-tax-framework-act.2026.article8": {
        "title": "지방세기본법 제8조",
        "publisher": "국가법령정보센터",
        "url": "https://www.law.go.kr/lsLawLinkInfo.do?chrClsCd=010202&lsJoLnkSeq=1000903169",
        "basis_date": "시행 2026-02-05",
        "description": "특별시세, 광역시세, 도세, 구세, 시·군세, 특별자치시·특별자치도세의 세목 근거입니다.",
    },
    "source.customs-act.2026.article14": {
        "title": "관세법 제14조",
        "publisher": "국가법령정보센터",
        "url": "https://law.go.kr/lsLawLinkInfo.do?chrClsCd=010202&lsJoLnkSeq=900015991",
        "basis_date": "시행 2026-01-01",
        "description": "수입물품에 관세를 부과한다는 관세의 과세물건 근거입니다.",
    },
    "source.nts.year-end-settlement.calculation": {
        "title": "연말정산 세액계산방법",
        "publisher": "국세청",
        "url": "https://www.nts.go.kr/nts/cm/cntnts/cntntsView.do?cntntsId=7870&mi=2312",
        "basis_date": "2026-05-02 확인",
        "description": "연말정산 계산 단계와 인적공제, 연금보험료공제, 특별소득공제, 세액감면, 세액공제의 구조 근거입니다.",
    },
    "source.nts.year-end-settlement.deduction-limit": {
        "title": "근로소득 과세표준과 산출세액",
        "publisher": "국세청",
        "url": "https://www.nts.go.kr/nts/cm/cntnts/cntntsView.do?cntntsId=7873&mi=6594",
        "basis_date": "2026-05-02 확인",
        "description": "소득공제 종합한도와 종합한도 적용 특별소득공제 등 항목의 근거입니다.",
    },
    "source.nts.year-end-settlement.special-credit": {
        "title": "근로소득 특별세액공제",
        "publisher": "국세청",
        "url": "https://kids.nts.go.kr/nts/cm/cntnts/cntntsView.do?cntntsId=7874&mi=6438",
        "basis_date": "2026-05-02 확인",
        "description": "보험료, 의료비, 교육비, 기부금 등 특별세액공제 항목의 근거입니다.",
    },
    "source.nts.monthly-rent-credit": {
        "title": "월세액 세액공제",
        "publisher": "국세청",
        "url": "https://www.nts.go.kr/nts/cm/cntnts/cntntsView.do?cntntsId=239025",
        "basis_date": "2026-05-02 확인",
        "description": "월세액 세액공제의 총급여, 종합소득금액, 주택, 전입신고, 한도 조건 근거입니다.",
    },
    "source.nts.credit-card-deduction": {
        "title": "신용카드 등 사용금액 소득공제",
        "publisher": "국세청",
        "url": "https://www.nts.go.kr/nts/cm/cntnts/cntntsView.do?cntntsId=7794&mi=2202",
        "basis_date": "2026-05-02 확인",
        "description": "신용카드, 직불카드, 현금영수증 사용액 소득공제와 총급여 25% 기준의 근거입니다.",
    },
    "source.nts.income-tax.deadline": {
        "title": "종합소득세 신고납부기한",
        "publisher": "국세청",
        "url": "https://www.nts.go.kr/nts/cm/cntnts/cntntsView.do?cntntsId=7665&mi=2225",
        "basis_date": "2026-05-02 확인",
        "description": "2025년 귀속 종합소득세 신고·납부 기한과 기한의 특례 근거입니다.",
    },
    "source.nts.vat.overview": {
        "title": "부가가치세 개요",
        "publisher": "국세청",
        "url": "https://www.nts.go.kr/nts/cm/cntnts/cntntsView.do?cntntsId=7693&mi=2272",
        "basis_date": "2026-05-02 확인",
        "description": "부가가치세 구조와 일반과세자·간이과세자 구분 기준의 근거입니다.",
    },
    "source.nts.corporate-tax.reliefs": {
        "title": "법인세 공제감면",
        "publisher": "국세청",
        "url": "https://www.nts.go.kr/nts/cm/cntnts/cntntsView.do?cntntsId=7987&mi=6561",
        "basis_date": "2026-05-02 확인",
        "description": "중소기업, 모든 기업, 법인세법상 공제·감면과 과세이연 지원제도의 공식 목록 근거입니다.",
    },
    "source.nts.eitc.intro": {
        "title": "근로장려금 소개",
        "publisher": "국세청",
        "url": "https://www.nts.go.kr/nts/cm/cntnts/cntntsView.do?cntntsId=7781&mi=2450",
        "basis_date": "2026-05-02 확인",
        "description": "근로장려금 제도 취지, 가구 유형별 소득 기준, 최대지급액 근거입니다.",
    },
    "source.nts.ctc.intro": {
        "title": "자녀장려금 소개",
        "publisher": "국세청",
        "url": "https://www.nts.go.kr/nts/cm/cntnts/cntntsView.do?cntntsId=7782&mi=2451",
        "basis_date": "2026-05-02 확인",
        "description": "자녀장려금의 부양자녀, 총소득, 자녀 1인당 지급액 근거입니다.",
    },
    "source.nts.grant.eligibility": {
        "title": "근로·자녀장려금 신청자격",
        "publisher": "국세청",
        "url": "https://www.nts.go.kr/nts/cm/cntnts/cntntsView.do?cntntsId=7783&mi=2452",
        "basis_date": "2026-05-02 확인",
        "description": "2025년 소득요건, 2025년 6월 1일 재산요건, 신청제외자 기준의 근거입니다.",
    },
    "source.nts.grant.deadline": {
        "title": "근로·자녀장려금 심사 및 지급",
        "publisher": "국세청",
        "url": "https://www.nts.go.kr/nts/cm/cntnts/cntntsView.do?cntntsId=7784&mi=2453",
        "basis_date": "2026-05-02 확인",
        "description": "정기신청분, 기한 후 신청분, 반기신청분의 심사와 지급기한 근거입니다.",
    },
    "source.nts.tax-calendar.2026": {
        "title": "2026년 국세청 세무일정",
        "publisher": "국세청",
        "url": "https://www.nts.go.kr/nts/ad/taxSchdul/selectList.do?mi=135747&taxYear=2026",
        "basis_date": "2026-05-02 확인",
        "description": "월별 신고·납부 일정과 기한의 특례 확인용 공식 일정입니다.",
    },
    "source.kinfa.youth-leap": {
        "title": "청년도약계좌 상품 안내",
        "publisher": "서민금융진흥원",
        "url": "https://ylaccount.kinfa.or.kr/main",
        "basis_date": "2026-05-02 확인",
        "description": "청년도약계좌 가입 연령, 개인소득, 가구소득, 금융소득종합과세 이력 제한 근거입니다.",
    },
    "source.fsc.isa.policy": {
        "title": "ISA 정책문답",
        "publisher": "금융위원회",
        "url": "https://www.fsc.go.kr/po020201/27339",
        "basis_date": "2026-05-02 확인",
        "description": "개인종합자산관리계좌(ISA)의 세제지원과 가입 제한을 이해하기 위한 정책 근거입니다.",
    },
}


NATIONAL_TAX_IDS = [
    "tax.income",
    "tax.corporate",
    "tax.inheritance-and-gift",
    "tax.comprehensive-real-estate",
    "tax.value-added",
    "tax.individual-consumption",
    "tax.transport-energy-environment",
    "tax.liquor",
    "tax.stamp",
    "tax.securities-transaction",
    "tax.education",
    "tax.special-rural-development",
]

LOCAL_TAX_IDS = [
    "local.acquisition",
    "local.registration-license",
    "local.leisure",
    "local.tobacco-consumption",
    "local.local-consumption",
    "local.resident",
    "local.local-income",
    "local.property",
    "local.automobile",
    "local.regional-resource-facility",
    "local.local-education",
]

CORPORATE_SUPPORT_IDS = [
    "corporate.support.startup-sme-reduction",
    "corporate.support.sme-special-reduction",
    "corporate.support.tech-transfer-reduction",
    "corporate.support.winwin-payment-credit",
    "corporate.support.wage-increase-credit",
    "corporate.support.performance-sharing-credit",
    "corporate.support.employment-maintenance-credit",
    "corporate.support.social-insurance-credit",
    "corporate.support.minimum-tax-preference",
    "corporate.support.cooperation-credit",
    "corporate.support.rnd-credit",
    "corporate.support.rnd-grant-deferral",
    "corporate.support.rnd-zone-reduction",
    "corporate.support.ma-credit",
    "corporate.support.facility-investment-credit",
    "corporate.support.local-relocation-reduction",
    "corporate.support.agricultural-corporation-reduction",
    "corporate.support.industrial-complex-reduction",
    "corporate.support.social-enterprise-reduction",
    "corporate.support.jeju-zone-reduction",
    "corporate.support.enterprise-city-reduction",
    "corporate.support.e-filing-credit",
    "corporate.support.restructuring-deferral",
    "corporate.support.local-relocation-deferral",
    "corporate.support.good-landlord-credit",
    "corporate.support.crisis-area-startup-reduction",
    "corporate.support.disaster-loss-credit",
    "corporate.support.foreign-tax-paid-credit",
]


def node(
    id_: str,
    title: str,
    type_: str,
    description: str,
    folder: str,
    *,
    basis_year: int | None = 2026,
    effective_date: str | None = None,
    expiration_date: str | None = None,
    parents: list[str] | None = None,
    children: list[str] | None = None,
    related: list[str] | None = None,
    terms: list[str] | None = None,
    deadlines: list[str] | None = None,
    sources: list[str] | None = None,
    law_reference: str = "",
    tags: list[str] | None = None,
) -> dict:
    return {
        "id": id_,
        "title": title,
        "type": type_,
        "description": description,
        "folder": folder,
        "basis_year": basis_year,
        "effective_date": effective_date,
        "expiration_date": expiration_date,
        "parents": parents or [],
        "children": children or [],
        "related": related or [],
        "terms": terms or [],
        "deadlines": deadlines or [],
        "sources": sources or [],
        "law_reference": law_reference,
        "tags": tags or [],
    }


def national_tax(id_: str, title: str, description: str, **kwargs) -> dict:
    sources = kwargs.pop("sources", ["source.national-tax-framework-act.2026.article2"])
    terms = kwargs.pop("terms", ["term.national-tax", "term.tax-law"])
    tags = kwargs.pop("tags", ["national-tax"])
    return node(
        id_,
        title,
        "tax",
        description,
        "10_Taxes/National",
        parents=["category.national-taxes"],
        sources=sources,
        effective_date="2026-01-01",
        law_reference="국세기본법 제2조 제1호",
        terms=terms,
        tags=tags,
        **kwargs,
    )


def local_tax(id_: str, title: str, description: str, parent: str, **kwargs) -> dict:
    return node(
        id_,
        title,
        "tax",
        description,
        "10_Taxes/Local",
        parents=[parent],
        sources=["source.local-tax-framework-act.2026.article8"],
        effective_date="2026-02-05",
        law_reference="지방세기본법 제8조",
        terms=["term.local-tax"],
        tags=["local-tax"],
        **kwargs,
    )


def deduction(id_: str, title: str, description: str, parent: str, **kwargs) -> dict:
    sources = kwargs.pop("sources", ["source.nts.year-end-settlement.calculation"])
    terms = kwargs.pop("terms", ["term.income-deduction", "term.tax-base"])
    tags = kwargs.pop("tags", ["income-deduction"])
    return node(
        id_,
        title,
        "deduction",
        description,
        "20_Deductions/IncomeDeductions",
        parents=[parent],
        sources=sources,
        terms=terms,
        tags=tags,
        **kwargs,
    )


def credit(id_: str, title: str, description: str, parent: str = "category.tax-credits", **kwargs) -> dict:
    sources = kwargs.pop("sources", ["source.nts.year-end-settlement.special-credit"])
    terms = kwargs.pop("terms", ["term.tax-credit"])
    tags = kwargs.pop("tags", ["tax-credit"])
    return node(
        id_,
        title,
        "tax-credit",
        description,
        "20_Deductions/TaxCredits",
        parents=[parent],
        sources=sources,
        terms=terms,
        tags=tags,
        **kwargs,
    )


def corporate_support(id_: str, title: str, description: str, **kwargs) -> dict:
    sources = kwargs.pop("sources", ["source.nts.corporate-tax.reliefs"])
    terms = kwargs.pop("terms", ["term.tax-credit", "term.tax-reduction"])
    tags = kwargs.pop("tags", ["corporate-tax-support"])
    return node(
        id_,
        title,
        "corporate-tax-support",
        description,
        "20_Deductions/CorporateTaxSupports",
        parents=["category.corporate-tax-supports"],
        sources=sources,
        terms=terms,
        tags=tags,
        **kwargs,
    )


TERMS = {
    "term.national-tax": ("국세", "국가가 부과하는 조세 중 국세기본법 제2조가 열거한 세목입니다.", ["source.national-tax-framework-act.2026.article2"]),
    "term.local-tax": ("지방세", "지방자치단체가 과세권을 가지며 지방세기본법상 세목과 자치단체 세목 배분에 따라 관리되는 세금입니다.", ["source.local-tax-framework-act.2026.article8"]),
    "term.tax-law": ("세법", "국세의 종목과 세율을 정하는 법률과 국세기본법이 세법으로 묶는 관련 법률 체계입니다.", ["source.national-tax-framework-act.2026.article2"]),
    "term.withholding": ("원천징수", "소득을 지급하는 자가 세법에 따라 세금을 미리 징수해 납부하는 방식입니다.", ["source.national-tax-framework-act.2026.article2", "source.nts.year-end-settlement.calculation"]),
    "term.tax-period": ("과세기간", "세법에 따라 과세표준 계산의 기초가 되는 기간입니다.", ["source.national-tax-framework-act.2026.article2"]),
    "term.tax-base": ("과세표준", "세율 적용과 세액 산출의 기준이 되는 과세대상의 수량 또는 가액입니다.", ["source.national-tax-framework-act.2026.article2", "source.nts.year-end-settlement.calculation"]),
    "term.deadline": ("법정신고기한", "세법에 따라 과세표준신고서를 제출할 기한입니다.", ["source.national-tax-framework-act.2026.article2"]),
    "term.income-deduction": ("소득공제", "과세표준 계산 전에 소득금액에서 차감하는 공제입니다.", ["source.nts.year-end-settlement.calculation", "source.nts.year-end-settlement.deduction-limit"]),
    "term.tax-credit": ("세액공제", "산출세액에서 직접 차감하는 공제입니다.", ["source.nts.year-end-settlement.calculation", "source.nts.year-end-settlement.special-credit"]),
    "term.tax-reduction": ("세액감면", "정책 목적에 따라 산출세액 또는 납부할 세액을 줄여 주는 조세지원입니다.", ["source.nts.year-end-settlement.calculation", "source.nts.corporate-tax.reliefs"]),
    "term.deduction-limit": ("소득공제 종합한도", "과도한 소득공제 적용을 배제하기 위해 일정 소득공제 항목 합계에 적용되는 한도입니다.", ["source.nts.year-end-settlement.deduction-limit"]),
    "term.total-income": ("총소득", "근로·자녀장려금 자격 판정에서 근로, 사업, 종교인, 기타, 이자·배당·연금소득을 합산한 금액입니다.", ["source.nts.grant.eligibility"]),
    "term.gross-pay": ("총급여액 등", "장려금 지급액 결정과 홑벌이·맞벌이 구분 등에 쓰이는 근로, 사업, 종교인소득의 합계 기준입니다.", ["source.nts.grant.eligibility"]),
    "term.property-requirement": ("재산요건", "근로·자녀장려금에서 가구원 재산 합계액으로 판정하는 요건입니다.", ["source.nts.grant.eligibility"]),
    "term.simple-vat-taxpayer": ("간이과세자", "부가가치세에서 직전 1년 매출액이 10,400만원 미만인 개인사업자 유형입니다.", ["source.nts.vat.overview"]),
    "term.deadline-special-rule": ("기한의 특례", "신고·납부 기한일이 공휴일, 토요일 또는 근로자의 날이면 그 다음 날을 기한으로 보는 규칙입니다.", ["source.nts.tax-calendar.2026", "source.nts.income-tax.deadline"]),
    "term.customs": ("관세", "수입물품에 부과되는 조세입니다.", ["source.customs-act.2026.article14"]),
}


DEADLINES = {
    "deadline.income-tax.2025-return": {
        "title": "2025년 귀속 종합소득세 확정신고",
        "description": "2025년 귀속 종합소득세 일반 신고·납부는 2026년 5월 1일부터 2026년 6월 1일까지입니다. 성실신고확인서 제출자는 2026년 6월 30일까지입니다.",
        "basis_year": 2025,
        "start_date": "2026-05-01",
        "end_date": "2026-06-01",
        "sources": ["source.nts.income-tax.deadline"],
    },
    "deadline.year-end-settlement": {
        "title": "근로소득 연말정산",
        "description": "계속 근로자는 다음연도 2월분 근로소득 지급 시, 중도 퇴직자는 퇴직하는 달의 근로소득 지급 시 연말정산을 실시합니다.",
        "basis_year": None,
        "start_date": None,
        "end_date": None,
        "sources": ["source.nts.year-end-settlement.calculation"],
    },
    "deadline.withholding.monthly": {
        "title": "원천세 신고 납부",
        "description": "매월분 원천세는 다음 달 10일까지 신고·납부하는 반복 기한으로 관리합니다.",
        "basis_year": 2026,
        "start_date": None,
        "end_date": None,
        "sources": ["source.nts.tax-calendar.2026"],
    },
    "deadline.vat.periodic": {
        "title": "부가가치세 신고 납부",
        "description": "일반과세자는 예정·확정 신고 구조를 따르며, 2026년 세무일정상 1기 예정신고 납부는 2026년 4월 27일, 2기 예정신고 납부는 2026년 10월 26일로 관리합니다.",
        "basis_year": 2026,
        "start_date": None,
        "end_date": None,
        "sources": ["source.nts.vat.overview", "source.nts.tax-calendar.2026"],
    },
    "deadline.grant.regular.2025-income": {
        "title": "2025년 귀속 근로·자녀장려금 정기신청",
        "description": "2025년 귀속 근로·자녀장려금 정기신청은 2026년 5월 신청 흐름으로 관리하고, 2026년에는 6월 1일까지로 기한의 특례를 반영합니다.",
        "basis_year": 2025,
        "start_date": "2026-05-01",
        "end_date": "2026-06-01",
        "sources": ["source.nts.grant.eligibility", "source.nts.grant.deadline"],
    },
    "deadline.grant.semiannual.2026": {
        "title": "2026년 근로장려금 반기신청분 지급",
        "description": "2026년 상반기분은 2026년 12월 30일, 하반기분은 2027년 6월 30일 지급기한으로 관리합니다.",
        "basis_year": 2026,
        "start_date": "2026-12-30",
        "end_date": "2027-06-30",
        "sources": ["source.nts.grant.deadline"],
    },
}


NODES = [
    node(
        "kr-tax-system",
        "대한민국 세금 온톨로지",
        "domain",
        "대한민국의 세금, 공제, 감면, 정책지원금, 신고·납부 기한을 Obsidian 지식 그래프로 학습하기 위한 최상위 항목입니다.",
        "00_Index",
        children=["category.national-taxes", "category.customs", "category.local-taxes", "category.deductions-and-reliefs", "category.policy-supports", "category.filing-calendar"],
        sources=["source.national-tax-framework-act.2026.article2", "source.local-tax-framework-act.2026.article8"],
        terms=["term.national-tax", "term.local-tax", "term.tax-law"],
        tags=["root"],
    ),
    node("category.national-taxes", "국세", "category", "국가가 부과하는 조세 중 국세기본법 제2조가 열거한 세목 전체입니다.", "10_Taxes/National", parents=["kr-tax-system"], children=NATIONAL_TAX_IDS, sources=["source.national-tax-framework-act.2026.article2"], terms=["term.national-tax"], law_reference="국세기본법 제2조 제1호", tags=["complete-manifest"]),
    node("category.customs", "관세 영역", "category", "국세기본법 제2조의 국세 열거와 별개로 관세법에 근거해 수입물품에 부과되는 조세 영역입니다.", "10_Taxes/Customs", parents=["kr-tax-system"], children=["tax.customs"], sources=["source.customs-act.2026.article14"], terms=["term.customs"], law_reference="관세법 제14조"),
    node("category.local-taxes", "지방세", "category", "지방자치단체가 과세권을 가지는 지방세기본법 제8조상 세목 전체입니다.", "10_Taxes/Local", parents=["kr-tax-system"], children=["category.local-ordinary-taxes", "category.local-purpose-taxes"], sources=["source.local-tax-framework-act.2026.article8"], terms=["term.local-tax"], law_reference="지방세기본법 제8조", tags=["complete-manifest"]),
    node("category.local-ordinary-taxes", "지방 보통세", "category", "지방세 중 특정 목적세가 아닌 보통세 세목 묶음입니다.", "10_Taxes/Local", parents=["category.local-taxes"], children=["local.acquisition", "local.registration-license", "local.leisure", "local.tobacco-consumption", "local.local-consumption", "local.resident", "local.local-income", "local.property", "local.automobile"], sources=["source.local-tax-framework-act.2026.article8"], terms=["term.local-tax"]),
    node("category.local-purpose-taxes", "지방 목적세", "category", "지방세 중 특정 재원 목적을 위해 부과되는 목적세 세목 묶음입니다.", "10_Taxes/Local", parents=["category.local-taxes"], children=["local.regional-resource-facility", "local.local-education"], sources=["source.local-tax-framework-act.2026.article8"], terms=["term.local-tax"]),
    node("category.deductions-and-reliefs", "공제·감면", "category", "과세표준을 줄이는 소득공제, 산출세액에서 차감하는 세액공제, 정책 목적의 세액감면과 법인세 조세지원 항목입니다.", "20_Deductions", parents=["kr-tax-system"], children=["category.income-deductions", "category.tax-credits", "category.tax-reductions", "category.corporate-tax-supports"], sources=["source.nts.year-end-settlement.calculation", "source.nts.corporate-tax.reliefs"], terms=["term.income-deduction", "term.tax-credit", "term.tax-reduction"]),
    node("category.policy-supports", "정책지원금·세제지원 계좌", "category", "국세청 현금성 지원금과 세제지원 금융상품을 학습용으로 묶은 항목입니다.", "30_Supports", parents=["kr-tax-system"], children=["support.earned-income-tax-credit", "support.child-tax-credit", "support.youth-leap-account", "support.isa"], sources=["source.nts.eitc.intro", "source.nts.ctc.intro", "source.kinfa.youth-leap", "source.fsc.isa.policy"], terms=["term.total-income", "term.gross-pay", "term.property-requirement"]),
    node("category.filing-calendar", "신고·납부·신청 기한", "category", "세목과 지원제도에 연결되는 기준연도별 기한입니다.", "50_Deadlines", parents=["kr-tax-system"], children=["filing.income-tax-return", "filing.year-end-settlement", "filing.withholding-tax", "filing.vat-return", "filing.grant-application"], sources=["source.nts.income-tax.deadline", "source.nts.tax-calendar.2026", "source.nts.grant.deadline"], terms=["term.deadline", "term.deadline-special-rule"]),
    national_tax("tax.income", "소득세", "개인의 소득에 과세되는 국세입니다. 종합소득, 퇴직소득, 양도소득 흐름으로 세부 학습 노드를 둡니다.", children=["tax.income.comprehensive", "tax.income.retirement", "tax.income.capital-gains"], related=["category.income-deductions", "category.tax-credits"], deadlines=["deadline.income-tax.2025-return", "deadline.year-end-settlement"]),
    national_tax("tax.corporate", "법인세", "법인의 각 사업연도 소득 등에 과세되는 국세이며 법인세 공제·감면 지원제도와 직접 연결됩니다.", related=["category.corporate-tax-supports"]),
    national_tax("tax.inheritance-and-gift", "상속세와 증여세", "상속 또는 증여로 이전되는 재산에 과세되는 국세입니다.", children=["tax.inheritance", "tax.gift"]),
    national_tax("tax.comprehensive-real-estate", "종합부동산세", "일정 기준을 넘는 주택·토지 보유에 대해 과세되는 국세입니다."),
    national_tax("tax.value-added", "부가가치세", "재화 또는 용역의 공급 과정에서 생긴 부가가치에 과세되는 국세입니다.", children=["concept.simple-vat-taxpayer"], sources=["source.national-tax-framework-act.2026.article2", "source.nts.vat.overview"], deadlines=["deadline.vat.periodic"], terms=["term.national-tax", "term.tax-period", "term.simple-vat-taxpayer"]),
    national_tax("tax.individual-consumption", "개별소비세", "특정 물품, 장소, 행위 등에 개별적으로 부과되는 국세입니다."),
    national_tax("tax.transport-energy-environment", "교통·에너지·환경세", "교통시설, 에너지, 환경 관련 재원 목적의 국세입니다."),
    national_tax("tax.liquor", "주세", "주류에 과세되는 국세입니다."),
    national_tax("tax.stamp", "인지세", "과세문서 작성에 대해 부과되는 국세입니다."),
    national_tax("tax.securities-transaction", "증권거래세", "주권 등의 양도 거래에 과세되는 국세입니다.", related=["tax.income.capital-gains"]),
    national_tax("tax.education", "교육세", "교육재정 확충을 위한 목적세 성격의 국세입니다.", related=["local.local-education"]),
    national_tax("tax.special-rural-development", "농어촌특별세", "농어촌 경쟁력 강화 재원 등을 위해 부과되는 목적세 성격의 국세입니다."),
    node("tax.customs", "관세", "tax", "수입물품에 부과되는 조세입니다. 국세기본법 제2조의 국세 열거와 별도로 관세법 제14조를 근거로 관리합니다.", "10_Taxes/Customs", parents=["category.customs"], sources=["source.customs-act.2026.article14"], terms=["term.customs", "term.tax-base"], law_reference="관세법 제14조", basis_year=2026),
    node("tax.income.comprehensive", "종합소득세", "tax", "이자·배당·사업·근로·연금·기타소득 등 종합소득금액에 대해 확정신고하는 소득세 흐름입니다.", "10_Taxes/National", parents=["tax.income"], sources=["source.nts.income-tax.deadline"], deadlines=["deadline.income-tax.2025-return"], terms=["term.tax-base", "term.deadline-special-rule"], basis_year=2025),
    node("tax.income.retirement", "퇴직소득세", "tax", "퇴직으로 받는 소득에 대해 별도 계산 구조를 가지는 소득세입니다.", "10_Taxes/National", parents=["tax.income"], sources=["source.national-tax-framework-act.2026.article2"], terms=["term.withholding"], basis_year=2026),
    node("tax.income.capital-gains", "양도소득세", "tax", "부동산, 주식 등 자산 양도차익에 대해 과세되는 소득세입니다.", "10_Taxes/National", parents=["tax.income"], related=["tax.securities-transaction"], sources=["source.national-tax-framework-act.2026.article2"], terms=["term.tax-base"], basis_year=2026),
    node("tax.inheritance", "상속세", "tax", "사망으로 이전되는 재산에 과세되는 세금입니다.", "10_Taxes/National", parents=["tax.inheritance-and-gift"], sources=["source.national-tax-framework-act.2026.article2"], terms=["term.tax-base"], basis_year=2026),
    node("tax.gift", "증여세", "tax", "무상 이전되는 재산에 과세되는 세금입니다.", "10_Taxes/National", parents=["tax.inheritance-and-gift"], sources=["source.national-tax-framework-act.2026.article2"], terms=["term.tax-base"], basis_year=2026),
    local_tax("local.acquisition", "취득세", "부동산, 차량 등 과세물건 취득에 대해 과세되는 지방 보통세입니다.", "category.local-ordinary-taxes"),
    local_tax("local.registration-license", "등록면허세", "재산권 등 등록 또는 각종 면허에 대해 과세되는 지방 보통세입니다.", "category.local-ordinary-taxes"),
    local_tax("local.leisure", "레저세", "경륜·경정·경마 등 승자투표권 발매 등에 과세되는 지방 보통세입니다.", "category.local-ordinary-taxes"),
    local_tax("local.tobacco-consumption", "담배소비세", "담배 반출 또는 반입에 대해 과세되는 지방 보통세입니다.", "category.local-ordinary-taxes"),
    local_tax("local.local-consumption", "지방소비세", "부가가치세와 연결되는 지방 보통세입니다.", "category.local-ordinary-taxes", related=["tax.value-added"]),
    local_tax("local.resident", "주민세", "개인, 사업소, 종업원 등 지역 구성원에게 과세되는 지방 보통세입니다.", "category.local-ordinary-taxes"),
    local_tax("local.local-income", "지방소득세", "소득세·법인세 과세표준이 되는 소득과 연결되는 지방 보통세입니다.", "category.local-ordinary-taxes", related=["tax.income", "tax.corporate"]),
    local_tax("local.property", "재산세", "토지, 건축물, 주택 등 재산 보유에 대해 과세되는 지방 보통세입니다.", "category.local-ordinary-taxes"),
    local_tax("local.automobile", "자동차세", "자동차 보유 또는 주행 등에 과세되는 지방 보통세입니다.", "category.local-ordinary-taxes"),
    local_tax("local.regional-resource-facility", "지역자원시설세", "지역자원 보호, 안전관리 등 특정 재원 목적의 지방 목적세입니다.", "category.local-purpose-taxes"),
    local_tax("local.local-education", "지방교육세", "지방교육재정 확충을 위해 다른 지방세에 부가되는 지방 목적세입니다.", "category.local-purpose-taxes", related=["tax.education"]),
    node("category.income-deductions", "소득공제", "category", "근로소득 연말정산에서 과세표준 전 단계에 반영되는 공제 묶음입니다.", "20_Deductions/IncomeDeductions", parents=["category.deductions-and-reliefs"], children=["deduction.personal", "deduction.pension-insurance", "deduction.special-income", "deduction.other-income"], sources=["source.nts.year-end-settlement.calculation", "source.nts.year-end-settlement.deduction-limit"], terms=["term.income-deduction", "term.deduction-limit"]),
    node("deduction.personal", "인적공제", "deduction", "기본공제와 추가공제로 구성되는 소득공제입니다.", "20_Deductions/IncomeDeductions", parents=["category.income-deductions"], children=["deduction.personal.basic", "deduction.personal.additional"], sources=["source.nts.year-end-settlement.calculation"], terms=["term.income-deduction"]),
    deduction("deduction.personal.basic", "기본공제", "본인, 배우자, 부양가족 등 기본공제 대상자에 대한 인적공제입니다.", "deduction.personal"),
    deduction("deduction.personal.additional", "추가공제", "경로우대, 장애인, 부녀자, 한부모 등 추가 요건에 따른 인적공제입니다.", "deduction.personal"),
    deduction("deduction.pension-insurance", "연금보험료공제", "공적연금의 근로자 부담금을 차감소득금액 계산에 반영하는 공제입니다.", "category.income-deductions"),
    node("deduction.special-income", "특별소득공제", "deduction", "근로소득 연말정산 계산 구조에서 차감소득금액을 산출할 때 반영되는 특별소득공제 묶음입니다.", "20_Deductions/IncomeDeductions", parents=["category.income-deductions"], children=["deduction.health-insurance-premium", "deduction.housing-funds"], sources=["source.nts.year-end-settlement.calculation", "source.nts.year-end-settlement.deduction-limit"], terms=["term.income-deduction", "term.deduction-limit"]),
    deduction("deduction.health-insurance-premium", "보험료공제", "국민건강보험료, 고용보험료 등 법정 보험료 납부액을 특별소득공제로 반영하는 항목입니다.", "deduction.special-income"),
    deduction("deduction.housing-funds", "주택자금공제", "주택임차차입금 원리금상환액과 장기주택저당차입금 이자상환액 등 주택자금 관련 소득공제입니다.", "deduction.special-income", sources=["source.nts.year-end-settlement.deduction-limit"]),
    node("deduction.other-income", "그 밖의 소득공제", "deduction", "과세표준 계산 전 추가로 반영되는 소득공제 항목 묶음입니다.", "20_Deductions/IncomeDeductions", parents=["category.income-deductions"], children=["deduction.personal-pension-savings", "deduction.small-business-mutual-aid", "deduction.housing-savings", "deduction.investment-association", "deduction.credit-card-use", "deduction.employee-stock-ownership", "deduction.employment-maintenance-worker", "deduction.long-term-fund", "deduction.youth-long-term-fund"], sources=["source.nts.year-end-settlement.deduction-limit"], terms=["term.income-deduction", "term.deduction-limit"]),
    deduction("deduction.personal-pension-savings", "개인연금저축 소득공제", "연금저축 세액공제와 구분되는 개인연금저축 관련 소득공제 항목입니다.", "deduction.other-income", sources=["source.nts.year-end-settlement.calculation"]),
    deduction("deduction.small-business-mutual-aid", "소기업·소상공인 공제부금", "노란우산 등 소기업·소상공인 공제부금에 대한 소득공제입니다.", "deduction.other-income", sources=["source.nts.year-end-settlement.deduction-limit"]),
    deduction("deduction.housing-savings", "주택마련저축", "청약저축, 주택청약종합저축, 근로자우대저축 등 주택마련저축 소득공제입니다.", "deduction.other-income", sources=["source.nts.year-end-settlement.deduction-limit"]),
    deduction("deduction.investment-association", "중소기업창업투자조합 출자 등", "중소기업창업투자조합 출자 등 투자 관련 소득공제입니다.", "deduction.other-income", sources=["source.nts.year-end-settlement.deduction-limit"]),
    deduction("deduction.credit-card-use", "신용카드 등 사용금액", "신용카드, 직불카드, 현금영수증 등 사용금액에 대한 소득공제입니다.", "deduction.other-income", sources=["source.nts.credit-card-deduction", "source.nts.year-end-settlement.deduction-limit"]),
    deduction("deduction.employee-stock-ownership", "우리사주조합 출연금", "우리사주조합 출연금 관련 소득공제입니다.", "deduction.other-income", sources=["source.nts.year-end-settlement.deduction-limit"]),
    deduction("deduction.employment-maintenance-worker", "고용유지중소기업 근로자 소득공제", "고용유지 중소기업 근로자에게 적용되는 소득공제 항목입니다.", "deduction.other-income", sources=["source.nts.year-end-settlement.calculation"]),
    deduction("deduction.long-term-fund", "장기집합투자증권저축", "장기집합투자증권저축에 대한 소득공제입니다.", "deduction.other-income", sources=["source.nts.year-end-settlement.deduction-limit"]),
    deduction("deduction.youth-long-term-fund", "청년형 장기집합투자증권저축", "청년형 장기집합투자증권저축에 대한 소득공제입니다.", "deduction.other-income", sources=["source.nts.year-end-settlement.calculation"]),
    node("category.tax-credits", "세액공제", "category", "산출세액에서 직접 차감하는 공제 항목 묶음입니다.", "20_Deductions/TaxCredits", parents=["category.deductions-and-reliefs"], children=["credit.earned-income", "credit.child", "credit.pension-account", "credit.special-tax", "credit.monthly-rent", "credit.foreign-tax-paid", "credit.research-and-development", "credit.integrated-employment"], sources=["source.nts.year-end-settlement.calculation", "source.nts.year-end-settlement.special-credit", "source.nts.corporate-tax.reliefs"], terms=["term.tax-credit"]),
    credit("credit.earned-income", "근로소득 세액공제", "근로소득자의 산출세액에서 차감되는 세액공제입니다.", sources=["source.nts.year-end-settlement.calculation"]),
    credit("credit.child", "자녀 세액공제", "자녀 수 등 요건에 따라 산출세액에서 차감되는 세액공제입니다.", related=["support.child-tax-credit"], sources=["source.nts.year-end-settlement.calculation"]),
    credit("credit.pension-account", "연금계좌 세액공제", "연금저축, 퇴직연금계좌 납입액 등에 대한 세액공제입니다.", sources=["source.nts.year-end-settlement.calculation"]),
    node("credit.special-tax", "특별세액공제", "tax-credit", "근로소득자가 해당 과세기간에 지출한 일정 비용을 산출세액에서 공제하는 항목 묶음입니다.", "20_Deductions/TaxCredits", parents=["category.tax-credits"], children=["credit.insurance-premium", "credit.medical-expense", "credit.education-expense", "credit.donation"], sources=["source.nts.year-end-settlement.special-credit"], terms=["term.tax-credit"]),
    credit("credit.insurance-premium", "보험료 세액공제", "보장성보험료, 장애인전용 보장성보험료 등에 대한 특별세액공제입니다.", "credit.special-tax"),
    credit("credit.medical-expense", "의료비 세액공제", "총급여액의 일정 비율 초과 의료비 등에 대한 특별세액공제입니다.", "credit.special-tax"),
    credit("credit.education-expense", "교육비 세액공제", "본인과 기본공제대상자 교육비 등에 대한 특별세액공제입니다.", "credit.special-tax"),
    credit("credit.donation", "기부금 세액공제", "정치자금, 고향사랑, 특례, 우리사주조합, 일반기부금 등 공제한도 내 기부금에 대한 특별세액공제입니다.", "credit.special-tax"),
    credit("credit.monthly-rent", "월세액 세액공제", "무주택, 총급여·종합소득금액, 주택 요건 등을 충족한 월세액에 대한 세액공제입니다.", sources=["source.nts.monthly-rent-credit"]),
    credit("credit.foreign-tax-paid", "외국납부세액공제", "국외원천소득에 대한 이중과세 조정을 위한 세액공제입니다.", sources=["source.nts.corporate-tax.reliefs"]),
    credit("credit.research-and-development", "연구·인력개발비 세액공제", "일반, 신성장·원천기술, 국가전략기술 연구개발비 등에 대한 조세지원입니다.", sources=["source.nts.corporate-tax.reliefs"], related=["corporate.support.rnd-credit"]),
    credit("credit.integrated-employment", "통합고용세액공제", "고용 증가, 청년·장애인·경력단절자 등 정책 대상 고용에 대한 세액공제입니다.", sources=["source.nts.corporate-tax.reliefs"]),
    node("category.tax-reductions", "세액감면", "category", "정책 목적에 따라 산출세액 또는 납부할 세액을 줄여 주는 감면 항목 묶음입니다.", "20_Deductions/TaxReductions", parents=["category.deductions-and-reliefs"], children=["reduction.sme-employment-income", "reduction.startup-sme", "reduction.sme-special", "reduction.good-landlord"], sources=["source.nts.year-end-settlement.calculation", "source.nts.corporate-tax.reliefs"], terms=["term.tax-reduction"]),
    node("reduction.sme-employment-income", "중소기업 취업자 소득세 감면", "tax-reduction", "청년 등 중소기업 취업자의 소득세를 일정 요건에서 감면하는 항목입니다.", "20_Deductions/TaxReductions", parents=["category.tax-reductions"], sources=["source.nts.year-end-settlement.calculation"], terms=["term.tax-reduction"]),
    node("reduction.startup-sme", "창업중소기업 등에 대한 세액감면", "tax-reduction", "창업중소기업 등의 최초 소득발생 과세연도와 이후 일정 기간에 적용되는 세액감면입니다.", "20_Deductions/TaxReductions", parents=["category.tax-reductions"], sources=["source.nts.corporate-tax.reliefs"], terms=["term.tax-reduction"], related=["corporate.support.startup-sme-reduction"]),
    node("reduction.sme-special", "중소기업특별세액감면", "tax-reduction", "제조업 등 일정 업종 중소기업 소득에 대한 세액감면입니다.", "20_Deductions/TaxReductions", parents=["category.tax-reductions"], sources=["source.nts.corporate-tax.reliefs"], terms=["term.tax-reduction"], related=["corporate.support.sme-special-reduction"]),
    node("reduction.good-landlord", "착한임대인 세액공제 제도", "tax-reduction", "상가건물 임대료 인하액에 적용되는 세액공제 제도입니다.", "20_Deductions/TaxReductions", parents=["category.tax-reductions"], sources=["source.nts.corporate-tax.reliefs"], terms=["term.tax-credit", "term.tax-reduction"], related=["corporate.support.good-landlord-credit"]),
    node("category.corporate-tax-supports", "법인세 공제·감면 지원제도", "category", "국세청 법인세 공제감면 안내가 열거한 중소기업, 모든 기업, 법인세법상 조세지원 항목 전체 목록입니다.", "20_Deductions/CorporateTaxSupports", parents=["category.deductions-and-reliefs"], children=CORPORATE_SUPPORT_IDS, sources=["source.nts.corporate-tax.reliefs"], terms=["term.tax-credit", "term.tax-reduction"], tags=["complete-manifest"]),
]


NODES.extend([
    corporate_support("corporate.support.startup-sme-reduction", "창업중소기업 등에 대한 세액감면", "창업중소기업 등의 최초 소득발생 과세연도와 이후 일정 기간에 적용되는 법인세 조세지원입니다.", related=["reduction.startup-sme"]),
    corporate_support("corporate.support.sme-special-reduction", "중소기업특별세액감면", "제조업 등 일정 업종 중소기업 소득에 대한 법인세 감면입니다.", related=["reduction.sme-special"]),
    corporate_support("corporate.support.tech-transfer-reduction", "기술이전·대여 세액감면", "기술이전 및 기술취득 등에 대한 과세특례입니다."),
    corporate_support("corporate.support.winwin-payment-credit", "상생결제 지급금액 세액공제", "상생결제제도를 통해 구매대금을 지급한 경우 적용되는 세액공제입니다."),
    corporate_support("corporate.support.wage-increase-credit", "근로소득을 증대시킨 기업에 대한 세액공제", "임금 증가와 정규직 전환 근로자 임금 증가 등에 대한 세액공제입니다."),
    corporate_support("corporate.support.performance-sharing-credit", "성과공유 중소기업의 경영성과급 세액공제", "중소기업이 요건을 충족한 경영성과급을 지급하는 경우 적용되는 세액공제입니다."),
    corporate_support("corporate.support.employment-maintenance-credit", "고용유지 중소기업 등에 대한 과세특례", "임금 감소와 시간당 임금 보전액 등을 기준으로 적용되는 세액공제입니다."),
    corporate_support("corporate.support.social-insurance-credit", "사회보험료 세액공제", "고용증가인원의 사회보험료 상당액에 적용되는 세액공제입니다."),
    corporate_support("corporate.support.minimum-tax-preference", "최저한세 적용한도 우대", "중소기업 등에게 일반법인보다 우대되는 최저한세율을 적용하는 지원입니다."),
    corporate_support("corporate.support.cooperation-credit", "상생협력에 대한 조세지원", "협력중소기업 지원 목적 출연금과 유형고정자산 무상임대 등에 대한 조세지원입니다."),
    corporate_support("corporate.support.rnd-credit", "연구·인력개발비 세액공제", "일반, 신성장·원천기술, 국가전략기술 연구개발비에 대한 세액공제입니다.", related=["credit.research-and-development"]),
    corporate_support("corporate.support.rnd-grant-deferral", "연구개발 관련 출연금등의 과세이연", "연구개발출연금 등에 대한 익금불산입 지원입니다."),
    corporate_support("corporate.support.rnd-zone-reduction", "연구개발특구 입주 기업 감면", "첨단기술 및 연구소기업 등에 적용되는 법인세 감면입니다."),
    corporate_support("corporate.support.ma-credit", "M&A 활성화 지원", "기술혁신형 합병·주식취득 인수가액 중 기술가치 금액에 대한 법인세 공제입니다."),
    corporate_support("corporate.support.facility-investment-credit", "시설투자 등에 대한 세액공제", "각종 시설투자 금액과 투자 증가분에 적용되는 세액공제입니다."),
    corporate_support("corporate.support.local-relocation-reduction", "공장·본사 등 지방이전 세액감면", "수도권과밀억제권역 본사·공장 지방 이전 등에 적용되는 세액감면입니다."),
    corporate_support("corporate.support.agricultural-corporation-reduction", "영농조합법인 등에 대한 감면", "영농조합법인, 영어조합법인, 농업회사법인 등의 농어업소득 등에 대한 감면입니다."),
    corporate_support("corporate.support.industrial-complex-reduction", "농공단지 등 입주 기업 감면", "농공단지 등 입주 후 최초 소득발생 과세연도와 이후 일정 기간에 적용되는 감면입니다."),
    corporate_support("corporate.support.social-enterprise-reduction", "사회적기업 등에 대한 감면", "사회적기업 인증 법인과 장애인 표준사업장 등에 적용되는 감면입니다."),
    corporate_support("corporate.support.jeju-zone-reduction", "제주첨단과학기술단지 등 입주 감면", "제주첨단과학기술단지 또는 제주투자진흥지구 입주기업 감면입니다."),
    corporate_support("corporate.support.enterprise-city-reduction", "기업도시개발구역 창업기업 등 감면", "기업도시개발구역 창업 또는 사업장 신설 기업에 적용되는 감면입니다."),
    corporate_support("corporate.support.e-filing-credit", "전자신고 세액공제", "법인이 직접 법인세를 전자신고할 때 적용되는 세액공제입니다."),
    corporate_support("corporate.support.restructuring-deferral", "구조조정 및 재무구조개선 과세이연", "양도차익 등에 대한 손금산입 또는 익금불산입 등 구조조정 지원입니다."),
    corporate_support("corporate.support.local-relocation-deferral", "지방이전 촉진 과세이연", "지방이전 등을 촉진하기 위한 양도차익 등의 손금산입 또는 익금불산입 지원입니다."),
    corporate_support("corporate.support.good-landlord-credit", "상가임대료 인하 임대사업자 세액공제", "상가건물 임대료 인하액에 적용되는 세액공제입니다.", related=["reduction.good-landlord"]),
    corporate_support("corporate.support.crisis-area-startup-reduction", "위기지역 창업기업 감면", "위기지역 지정 또는 선포 기간에 창업하거나 사업장을 신설한 기업에 대한 감면입니다."),
    corporate_support("corporate.support.disaster-loss-credit", "재해손실세액공제", "천재지변 등 재해로 사업용 총자산가액의 20% 이상을 상실한 경우 적용되는 법인세법상 세액공제입니다."),
    corporate_support("corporate.support.foreign-tax-paid-credit", "외국납부세액공제", "국외원천소득에 대한 이중과세 조정을 위한 법인세법상 세액공제입니다.", related=["credit.foreign-tax-paid"]),
    node("support.earned-income-tax-credit", "근로장려금", "support-program", "근로·사업·종교인소득이 있는 저소득 가구의 근로를 장려하기 위해 지급하는 국세청 지원금입니다. 2025년 귀속 소득 기준은 단독 2,200만원, 홑벌이 3,200만원, 맞벌이 4,400만원 미만입니다.", "30_Supports", parents=["category.policy-supports"], related=["tax.income.comprehensive"], terms=["term.total-income", "term.gross-pay", "term.property-requirement"], deadlines=["deadline.grant.regular.2025-income", "deadline.grant.semiannual.2026"], sources=["source.nts.eitc.intro", "source.nts.grant.eligibility", "source.nts.grant.deadline"], basis_year=2025, tags=["cash-support"]),
    node("support.child-tax-credit", "자녀장려금", "support-program", "18세 미만 부양자녀가 있는 저소득 가구의 자녀양육을 지원하는 국세청 지원금입니다. 2025년 귀속 총소득 기준은 홑벌이·맞벌이 7,000만원 미만입니다.", "30_Supports", parents=["category.policy-supports"], related=["credit.child"], terms=["term.total-income", "term.property-requirement"], deadlines=["deadline.grant.regular.2025-income"], sources=["source.nts.ctc.intro", "source.nts.grant.eligibility", "source.nts.grant.deadline"], basis_year=2025, tags=["cash-support"]),
    node("support.youth-leap-account", "청년도약계좌", "support-program", "청년의 중장기 자산형성을 지원하는 정책금융 상품입니다. 세금 세목은 아니지만 소득 요건, 금융소득종합과세 이력 제한, 비과세·정부기여금 학습 항목으로 연결합니다.", "30_Supports", parents=["category.policy-supports"], related=["tax.income"], terms=["term.total-income"], sources=["source.kinfa.youth-leap"], tags=["policy-finance"]),
    node("support.isa", "개인종합자산관리계좌 ISA", "support-program", "개인이 예·적금, 펀드, 파생결합증권 등을 한 계좌에서 운용하며 세제혜택을 받을 수 있는 정책성 금융계좌입니다.", "30_Supports", parents=["category.policy-supports"], related=["tax.income"], sources=["source.fsc.isa.policy"], terms=["term.tax-credit"], tags=["policy-finance", "tax-preferred-account"]),
    node("filing.income-tax-return", "종합소득세 확정신고", "filing", "종합소득이 있는 개인이 다음연도 5월 신고·납부하는 절차입니다.", "50_Deadlines", parents=["category.filing-calendar"], related=["tax.income.comprehensive"], terms=["term.deadline", "term.deadline-special-rule"], deadlines=["deadline.income-tax.2025-return"], sources=["source.nts.income-tax.deadline"], basis_year=2025),
    node("filing.year-end-settlement", "연말정산", "filing", "원천징수의무자가 근로자의 해당 과세기간 근로소득세를 확정하는 절차입니다.", "50_Deadlines", parents=["category.filing-calendar"], related=["category.deductions-and-reliefs"], terms=["term.withholding", "term.income-deduction", "term.tax-credit"], deadlines=["deadline.year-end-settlement"], sources=["source.nts.year-end-settlement.calculation"]),
    node("filing.withholding-tax", "원천세 신고 납부 절차", "filing", "원천징수의무자가 원천징수한 세액을 신고·납부하는 절차입니다.", "50_Deadlines", parents=["category.filing-calendar"], terms=["term.withholding", "term.deadline-special-rule"], deadlines=["deadline.withholding.monthly"], sources=["source.nts.tax-calendar.2026"]),
    node("filing.vat-return", "부가가치세 신고 납부 절차", "filing", "부가가치세 과세사업자가 과세기간별 매출세액과 매입세액을 신고·납부하는 절차입니다.", "50_Deadlines", parents=["category.filing-calendar"], related=["tax.value-added", "concept.simple-vat-taxpayer"], terms=["term.tax-period", "term.simple-vat-taxpayer", "term.deadline-special-rule"], deadlines=["deadline.vat.periodic"], sources=["source.nts.vat.overview", "source.nts.tax-calendar.2026"]),
    node("filing.grant-application", "근로·자녀장려금 신청", "filing", "국세청 근로·자녀장려금 정기·반기·기한 후 신청 및 심사 흐름입니다.", "50_Deadlines", parents=["category.filing-calendar"], related=["support.earned-income-tax-credit", "support.child-tax-credit"], terms=["term.total-income", "term.property-requirement"], deadlines=["deadline.grant.regular.2025-income", "deadline.grant.semiannual.2026"], sources=["source.nts.grant.eligibility", "source.nts.grant.deadline"], basis_year=2025),
    node("concept.simple-vat-taxpayer", "간이과세자 기준", "concept", "부가가치세에서 1년 매출액 10,400만원 미만 개인사업자에게 적용되는 납세 유형 기준입니다.", "40_Terms/Concepts", parents=["tax.value-added"], terms=["term.simple-vat-taxpayer"], sources=["source.nts.vat.overview"]),
])


def title_by_id(all_items: dict[str, dict], id_: str) -> str:
    return all_items[id_]["title"]


def obsidian_link(all_items: dict[str, dict], id_: str) -> str:
    item = all_items[id_]
    target = f"{item['folder']}/{slug(item['title'])}"
    return f"[[{target}|{item['title']}]]"


def unique(values: list[str]) -> list[str]:
    result: list[str] = []
    for value in values:
        if value not in result:
            result.append(value)
    return result


def normalize_graph(nodes: list[dict]) -> None:
    by_id = {item["id"]: item for item in nodes}
    for item in nodes:
        for child_id in list(item["children"]):
            if child_id in by_id and item["id"] not in by_id[child_id]["parents"]:
                by_id[child_id]["parents"].append(item["id"])
        for parent_id in list(item["parents"]):
            if parent_id in by_id and item["id"] not in by_id[parent_id]["children"]:
                by_id[parent_id]["children"].append(item["id"])
        for related_id in list(item["related"]):
            if related_id in by_id and item["id"] not in by_id[related_id]["related"]:
                by_id[related_id]["related"].append(item["id"])
    for item in nodes:
        for key in ("parents", "children", "related", "terms", "deadlines", "sources", "tags"):
            item[key] = unique(item[key])


def normalize_items(items: dict[str, dict]) -> None:
    for item in items.values():
        for child_id in list(item.get("children") or []):
            child = items.get(child_id)
            if child and item["id"] not in (child.get("parents") or []):
                child.setdefault("parents", []).append(item["id"])
        for parent_id in list(item.get("parents") or []):
            parent = items.get(parent_id)
            if parent and item["id"] not in (parent.get("children") or []):
                parent.setdefault("children", []).append(item["id"])
        for related_id in list(item.get("related") or []):
            related = items.get(related_id)
            if related and item["id"] not in (related.get("related") or []):
                related.setdefault("related", []).append(item["id"])

    for item in items.values():
        for key in ("parents", "children", "related", "terms", "deadlines", "sources", "tags"):
            item[key] = unique(item.get(key) or [])


def frontmatter(fields: dict) -> str:
    lines = ["---"]
    for key in [
        "id",
        "title",
        "type",
        "description",
        "basis_year",
        "effective_date",
        "expiration_date",
        "parents",
        "children",
        "related",
        "terms",
        "deadlines",
        "sources",
        "law_reference",
        "tags",
        "publisher",
        "url",
        "basis_date",
        "start_date",
        "end_date",
    ]:
        value = fields.get(key)
        if value is not None:
            lines.append(f"{key}: {json.dumps(value, ensure_ascii=False)}")
    lines.append("---")
    return "\n".join(lines)


def slug(title: str) -> str:
    return re.sub(r'[\\/:*?"<>|]', " ", title).strip()


def render_note(item: dict, all_items: dict[str, dict]) -> str:
    body = [frontmatter(item), "", f"# {item['title']}", "", item["description"], ""]
    if item.get("law_reference"):
        body.extend(["## 근거 조항", "", item["law_reference"], ""])
    for heading, key in [
        ("상위 항목", "parents"),
        ("하위 항목", "children"),
        ("관련 항목", "related"),
        ("관련 용어", "terms"),
        ("기한", "deadlines"),
        ("근거·출처", "sources"),
    ]:
        values = item.get(key, [])
        if values:
            body.extend([f"## {heading}", ""])
            for value in values:
                if key == "sources":
                    url = all_items[value].get("url")
                    if url:
                        body.append(f"- {obsidian_link(all_items, value)}: {url}")
                    else:
                        body.append(f"- {obsidian_link(all_items, value)}")
                else:
                    body.append(f"- {obsidian_link(all_items, value)}")
            body.append("")
    body.extend(["## 온톨로지 ID", "", f"`{item['id']}`", ""])
    return "\n".join(body)


def render_source(source_id: str, source: dict) -> dict:
    return {
        "id": source_id,
        "title": source["title"],
        "type": "source",
        "description": source["description"],
        "folder": "90_Sources",
        "basis_year": None,
        "effective_date": None,
        "expiration_date": None,
        "parents": [],
        "children": [],
        "related": [],
        "terms": [],
        "deadlines": [],
        "sources": [],
        "law_reference": "",
        "tags": ["official-source", source["publisher"]],
        "publisher": source["publisher"],
        "url": source["url"],
        "basis_date": source["basis_date"],
    }


def render_source_note(item: dict) -> str:
    fields = {key: item.get(key) for key in [
        "id", "title", "type", "description", "basis_year", "effective_date", "expiration_date",
        "parents", "children", "related", "terms", "deadlines", "sources", "law_reference",
        "tags", "publisher", "url", "basis_date"
    ]}
    body = [
        frontmatter(fields),
        "",
        f"# {item['title']}",
        "",
        item["description"],
        "",
        "## 발행기관",
        "",
        item["publisher"],
        "",
        "## 기준일",
        "",
        item["basis_date"],
        "",
        "## 링크",
        "",
        item["url"],
        "",
        "## 온톨로지 ID",
        "",
        f"`{item['id']}`",
        "",
    ]
    return "\n".join(body)


def default_item_fields(item: dict) -> dict:
    result = {
        "basis_year": item.get("basis_year"),
        "effective_date": item.get("effective_date"),
        "expiration_date": item.get("expiration_date"),
        "parents": item.get("parents") or [],
        "children": item.get("children") or [],
        "related": item.get("related") or [],
        "terms": item.get("terms") or [],
        "deadlines": item.get("deadlines") or [],
        "sources": item.get("sources") or [],
        "law_reference": item.get("law_reference") or "",
        "tags": item.get("tags") or [],
    }
    return {**item, **result}


def load_custom_items() -> list[dict]:
    if not CUSTOM_ITEMS_PATH.exists():
        return []

    payload = json.loads(CUSTOM_ITEMS_PATH.read_text(encoding="utf-8"))
    if isinstance(payload, list):
        raw_items = payload
    else:
        raw_items = payload.get("items", [])
    if not isinstance(raw_items, list):
        raise ValueError(f"{CUSTOM_ITEMS_PATH} must contain an items array")
    return [dict(item) for item in raw_items]


def build_all_items() -> dict[str, dict]:
    nodes = [dict(item) for item in NODES]
    normalize_graph(nodes)

    items: dict[str, dict] = {item["id"]: item for item in nodes}
    for term_id, (title, description, sources) in TERMS.items():
        items[term_id] = node(
            term_id,
            title,
            "term",
            description,
            "40_Terms",
            basis_year=2026,
            sources=sources,
            tags=["term"],
        )
    for deadline_id, deadline in DEADLINES.items():
        items[deadline_id] = node(
            deadline_id,
            deadline["title"],
            "deadline",
            deadline["description"],
            "50_Deadlines",
            basis_year=deadline["basis_year"],
            sources=deadline["sources"],
            tags=["deadline"],
        )
        items[deadline_id]["start_date"] = deadline["start_date"]
        items[deadline_id]["end_date"] = deadline["end_date"]
    for source_id, source in SOURCES.items():
        items[source_id] = render_source(source_id, source)
    for custom_item in load_custom_items():
        item_id = custom_item["id"]
        if item_id in items:
            merged = {**items[item_id], **custom_item}
            merged["tags"] = unique((items[item_id].get("tags") or []) + (custom_item.get("tags") or []) + ["custom-overlay"])
            items[item_id] = default_item_fields(merged)
        else:
            custom_item["tags"] = unique((custom_item.get("tags") or []) + ["custom-overlay"])
            items[item_id] = default_item_fields(custom_item)
    normalize_items(items)
    return items


def expected_note_path(item: dict) -> Path:
    return VAULT / item["folder"] / f"{slug(item['title'])}.md"


def generated_note_id(path: Path) -> str | None:
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return None
    if not text.startswith("---\n"):
        return None
    try:
        _, frontmatter_text, _ = text.split("---", 2)
    except ValueError:
        return None
    for raw_line in frontmatter_text.strip().splitlines():
        if raw_line.startswith("id: "):
            return json.loads(raw_line.split(": ", 1)[1])
    return None


def is_custom_overlay_note(path: Path) -> bool:
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return False
    if not text.startswith("---\n"):
        return False
    try:
        _, frontmatter_text, _ = text.split("---", 2)
    except ValueError:
        return False
    return "custom-overlay" in frontmatter_text


def remove_stale_generated_notes(items: dict[str, dict]) -> None:
    expected_paths = {expected_note_path(item).resolve() for item in items.values()}
    item_ids = set(items)
    for path in VAULT.rglob("*.md"):
        note_id = generated_note_id(path)
        if note_id in item_ids and path.resolve() not in expected_paths:
            path.unlink()
        elif note_id not in item_ids and is_custom_overlay_note(path):
            path.unlink()


def write_markdown(items: dict[str, dict]) -> None:
    VAULT.mkdir(parents=True, exist_ok=True)
    remove_stale_generated_notes(items)
    for item in items.values():
        path = expected_note_path(item)
        path.parent.mkdir(parents=True, exist_ok=True)
        if item["type"] == "source":
            text = render_source_note(item)
        else:
            text = render_note(item, items)
        path.write_text(text, encoding="utf-8")


def write_index(items: dict[str, dict]) -> None:
    index = VAULT / "00_Index" / "대한민국 세금 온톨로지.md"
    root = items["kr-tax-system"]
    index.write_text(render_note(root, items), encoding="utf-8")


def write_export(items: dict[str, dict]) -> None:
    EXPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    export = {
        "version": "KR-TAX-OBSIDIAN-ONTOLOGY-2026.05.02",
        "basis_date": "2026-05-02",
        "manifests": {
            "national_tax_ids": NATIONAL_TAX_IDS,
            "local_tax_ids": LOCAL_TAX_IDS,
            "corporate_support_ids": CORPORATE_SUPPORT_IDS,
        },
        "items": sorted(items.values(), key=lambda item: item["id"]),
    }
    EXPORT_PATH.write_text(json.dumps(export, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    items = build_all_items()
    write_markdown(items)
    write_index(items)
    write_export(items)
    print(f"Generated {len(items)} ontology notes into {VAULT}")
    print(f"Exported {EXPORT_PATH}")


if __name__ == "__main__":
    main()
