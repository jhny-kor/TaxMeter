#!/usr/bin/env python3
"""Build split finance ontology exports.

The finance product surface is intentionally separated from the tax ontology:
product values change frequently, often require API keys, and must preserve
source-specific disclosure fields for later stale/closed-product checks.
"""
# allow: SIZE_OK -- source/category data table kept together for deterministic split exports.

from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
import re
from pathlib import Path
from typing import Iterable


REPO_ROOT = Path(__file__).resolve().parents[2]
ROOT = Path(__file__).resolve().parents[1]
EXPORT_DIR = ROOT / "exports"
CUSTOM_FINANCE_DIR = ROOT / "custom" / "finance"
DOCS_ROOT = REPO_ROOT / "docs" / "opentax"

CURRENT_REVIEW_DATE = "2026-07-04"
CURRENT_BASIS_YEAR = 2026
DISCLOSURE_STALE_BEFORE = "202401"
RAW_BASE_URL = "https://raw.githubusercontent.com/jhny-kor/TaxMeter/main"
WEB_BASE_URL = "https://jhny-kor.github.io/TaxMeter/opentax"

CARD_EXPORT = EXPORT_DIR / "korea-card-products-ontology-2026.json"
DEPOSIT_EXPORT = EXPORT_DIR / "korea-deposit-products-ontology-2026.json"
SAVING_EXPORT = EXPORT_DIR / "korea-saving-products-ontology-2026.json"
LOAN_EXPORT = EXPORT_DIR / "korea-loan-products-ontology-2026.json"
INSURANCE_EXPORT = EXPORT_DIR / "korea-insurance-products-ontology-2026.json"
REFERENCE_EXPORT = EXPORT_DIR / "korea-finance-reference-ontology-2026.json"
MANIFEST_EXPORT = EXPORT_DIR / "finance-ontology-manifest.json"
SEARCH_INDEX_EXPORT = EXPORT_DIR / "finance-search-index-2026.json"
QUALITY_MANIFEST_EXPORT = EXPORT_DIR / "openfin-quality-manifest-2026.json"
SEARCH_REGRESSION_REPORT_EXPORT = EXPORT_DIR / "openfin-search-regression-report-2026.json"
REFERENCE_KEYS = ("parents", "children", "related", "terms", "deadlines", "sources")
GENERIC_SEARCH_TYPES = {"category", "term", "domain", "source"}
TAX_DECISION_TYPES = {"tax-credit", "deduction"}
# type 필터 그룹: type=tax는 세부 결정 타입까지 포함해야 typed 검색이
# 의료비 세액공제 대신 부가가치세로 새지 않는다. mcp_server.py와 동일하게 유지한다.
SEARCH_TYPE_GROUPS = {
    "tax": {
        "tax", "tax-credit", "tax-reduction", "deduction", "corporate-tax-support",
        "official-tax-item", "filing", "deadline", "required-document", "eligibility-rule",
    },
    "tax-support": {"required-document"},
    "tax-rule": {"eligibility-rule"},
}
TAX_SEARCH_REGRESSIONS = (
    ("연말정산 의료비 세액공제 한도 대상", "credit.medical-expense", None),
    ("연말정산 의료비 세액공제 한도 대상", "credit.medical-expense", "tax"),
    ("월세 세액공제 조건", "credit.monthly-rent", None),
    ("월세 세액공제 조건", "credit.monthly-rent", "tax"),
    ("교육비 세액공제 대상", "credit.education-expense", None),
    ("교육비 세액공제 대상", "credit.education-expense", "tax"),
    ("연금계좌 세액공제 한도", "credit.pension-account", None),
    ("연금계좌 세액공제 한도", "credit.pension-account", "tax"),
    ("신용카드 소득공제 한도", "deduction.credit-card-use", None),
    ("신용카드 소득공제 한도", "deduction.credit-card-use", "tax"),
)
TAX_SEARCH_ALIASES = {
    "credit.medical-expense": ("연말정산 의료비 세액공제 한도 대상", "의료비 세액공제 한도 대상"),
    "credit.monthly-rent": ("월세 세액공제 조건", "월세액 세액공제 조건"),
    "credit.education-expense": ("교육비 세액공제 대상",),
    "credit.pension-account": ("연금계좌 세액공제 한도",),
    "deduction.credit-card-use": ("신용카드 소득공제 한도", "신용카드 등 사용금액 소득공제 한도"),
}

GENERATED_FILES = {
    "card": CUSTOM_FINANCE_DIR / "card-products.generated.json",
    "deposit": CUSTOM_FINANCE_DIR / "deposit-products.generated.json",
    "saving": CUSTOM_FINANCE_DIR / "saving-products.generated.json",
    "loan": CUSTOM_FINANCE_DIR / "loan-products.generated.json",
    "policy_loan": CUSTOM_FINANCE_DIR / "policy-loan-products.generated.json",
    "deposit_protection": CUSTOM_FINANCE_DIR / "deposit-protection-products.generated.json",
    "insurance": CUSTOM_FINANCE_DIR / "insurance-products.generated.json",
    "reference": CUSTOM_FINANCE_DIR / "finance-reference.generated.json",
}


def unique(values: Iterable[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        if value and value not in seen:
            seen.add(value)
            result.append(value)
    return result


def node(
    id_: str,
    title: str,
    type_: str,
    description: str,
    *,
    parents: list[str] | None = None,
    children: list[str] | None = None,
    related: list[str] | None = None,
    terms: list[str] | None = None,
    sources: list[str] | None = None,
    tags: list[str] | None = None,
    basis_year: int | None = CURRENT_BASIS_YEAR,
    **extra: object,
) -> dict:
    item = {
        "id": id_,
        "title": title,
        "type": type_,
        "description": description,
        "basis_year": basis_year,
        "reviewed_at": CURRENT_REVIEW_DATE,
        "abolition_status": "active",
        "revision_status": "check_source",
        "parents": parents or [],
        "children": children or [],
        "related": related or [],
        "terms": terms or [],
        "deadlines": [],
        "sources": sources or [],
        "tags": unique(tags or []),
    }
    item.update(extra)
    return item


def source_node(id_: str, title: str, publisher: str, url: str, description: str, basis_date: str) -> dict:
    return {
        "id": id_,
        "title": title,
        "type": "source",
        "description": description,
        "basis_year": None,
        "parents": [],
        "children": [],
        "related": [],
        "terms": [],
        "deadlines": [],
        "sources": [],
        "tags": ["official-source", "finance-source"],
        "publisher": publisher,
        "url": url,
        "basis_date": basis_date,
        "source_urls": [url],
        "source_basis_dates": [basis_date],
    }


SOURCES = {
    "source.fss.finlife.api": source_node(
        "source.fss.finlife.api",
        "금융감독원 금융상품통합비교공시 금융상품한눈에 API",
        "금융감독원",
        "https://finlife.fss.or.kr/finlifeapi/",
        "금융회사, 정기예금, 적금, 연금저축, 주택담보대출, 전세자금대출, 개인신용대출 상품의 공식 비교공시 API 원천입니다.",
        "2026-07-03 확인",
    ),
    "source.fss.finlife.web": source_node(
        "source.fss.finlife.web",
        "금융상품통합비교공시 금융상품한눈에",
        "금융감독원",
        "https://finlife.fss.or.kr/",
        "예금, 적금, 대출, 연금저축 등 금융상품 비교공시를 제공하는 금융감독원 공식 웹 표면입니다.",
        "2026-07-03 확인",
    ),
    "source.fsc.business-loan-comparison": source_node(
        "source.fsc.business-loan-comparison",
        "개인사업자 대출상품 비교공시 서비스 개시",
        "금융위원회",
        "https://www.fsc.go.kr/no010101/83693",
        "금융상품 한눈에의 개인사업자 대출상품 비교공시 신설, 자금용도·가입대상·대출종류·필요금액 등 검색조건과 상세정보 제공 근거입니다.",
        "2026-07-03 확인",
    ),
    "source.fsc.financial-company-basic": source_node(
        "source.fsc.financial-company-basic",
        "금융위원회 금융회사기본정보",
        "공공데이터포털",
        "https://www.data.go.kr/data/15043232/openapi.do",
        "금융회사명, 대표자명, 사업자등록번호, 설립일자, 주소, 전화번호, 상장·폐지일자, 회계감사의견 등 금융회사 개요 정보를 제공하는 공식 API 후보입니다.",
        "2026-07-03 확인",
    ),
    "source.fsc.financial-company-credit": source_node(
        "source.fsc.financial-company-credit",
        "금융위원회 금융회사재무신용정보",
        "공공데이터포털",
        "https://www.data.go.kr/data/15059594/openapi.do",
        "금융회사 재무·신용 정보를 상품 제공자 리스크 축으로 연결하기 위한 공식 API 후보입니다.",
        "2026-07-03 확인",
    ),
    "source.fss.fine.portal": source_node(
        "source.fss.fine.portal",
        "금융소비자 정보포털 파인",
        "금융감독원",
        "https://fine.fss.or.kr/",
        "계좌·보험금·증권 등 숨은 금융자산 조회와 금융소비자 보호 정보를 연결하기 위한 금융감독원 공식 포털입니다.",
        "2026-07-04 확인",
    ),
    "source.fsc.rate-disclosure-guide": source_node(
        "source.fsc.rate-disclosure-guide",
        "금리정보 공시 안내",
        "금융위원회",
        "https://www.fsc.go.kr/edu/cardnews?cnId=1796",
        "은행의 대출금리, 예금금리, 예대금리차를 한눈에 비교하는 금리정보 공시 제도 안내입니다.",
        "2026-07-04 확인",
    ),
    "source.kfb.consumer-portal": source_node(
        "source.kfb.consumer-portal",
        "은행연합회 소비자포털",
        "은행연합회",
        "https://portal.kfb.or.kr/",
        "은행별 예금·대출 금리, 수수료, 예대금리차와 COFIX 등 은행권 비교공시를 확인하는 공식 포털입니다.",
        "2026-07-04 확인",
    ),
    "source.fsc.domestic-bank-statistics": source_node(
        "source.fsc.domestic-bank-statistics",
        "금융위원회 금융통계국내은행정보",
        "공공데이터포털",
        "https://www.data.go.kr/data/15061304/openapi.do",
        "국내은행 일반현황, 재무현황, 주요 경영지표, 주요 영업활동을 제공하는 공식 API 후보입니다.",
        "2026-07-03 확인",
    ),
    "source.fsb.savings-bank-deposit-rates": source_node(
        "source.fsb.savings-bank-deposit-rates",
        "저축은행중앙회 예·적금 금리공시",
        "저축은행중앙회",
        "https://www.fsb.or.kr/ratedepo_0100.act",
        "저축은행 정기예금·적금의 가입기간, 가입방법, 기본금리, 최고우대금리와 상품별 비교를 제공하는 공식 공시 표면입니다.",
        "2026-07-04 확인",
    ),
    "source.bok.ecos": source_node(
        "source.bok.ecos",
        "한국은행 ECOS Open API",
        "한국은행",
        "https://ecos.bok.or.kr/api/",
        "기준금리, 시장금리, 환율 등 금융상품 비교에 필요한 기준 지표를 제공하는 한국은행 경제통계 Open API입니다.",
        "2026-07-03 확인",
    ),
    "source.fsc.cofix-overview": source_node(
        "source.fsc.cofix-overview",
        "COFIX 공시와 자금조달비용지수 설명",
        "금융위원회",
        "https://www.fsc.go.kr/po010101/70494",
        "COFIX가 은행 자금조달 관련 정보를 기초로 산출되고 주택담보대출 등에 활용된다는 기준금리 해석 근거입니다.",
        "2026-07-03 확인",
    ),
    "source.data.go.kr.kinfa-loan-products": source_node(
        "source.data.go.kr.kinfa-loan-products",
        "서민금융진흥원 대출상품한눈에 정보 서비스",
        "공공데이터포털",
        "https://www.data.go.kr/data/15106208/openapi.do?recommendDataYn=Y",
        "서민금융·정책금융 대출상품의 대출한도, 금리구분, 대출용도, 총 대출기간, 취급기관 등을 비교 조회하는 공공데이터 API입니다.",
        "2026-07-03 확인",
    ),
    "source.fsc.inclusive-finance-products": source_node(
        "source.fsc.inclusive-finance-products",
        "금융위원회 서민금융상품기본정보",
        "공공데이터포털",
        "https://www.data.go.kr/data/15094787/openapi.do",
        "서민금융 한눈에 기반의 서민금융 대출상품, 자산형성상품, 사회적 금융 상품 명칭·지원대상·금리·한도·상환방식 API 후보입니다.",
        "2026-07-03 확인",
    ),
    "source.fsc.inclusive-finance-performance": source_node(
        "source.fsc.inclusive-finance-performance",
        "금융위원회 서민금융지원실적정보",
        "공공데이터포털",
        "https://www.data.go.kr/data/15094801/openapi.do",
        "미소금융·햇살론 등 정책서민금융상품의 지원금액, 이용자 수, 지역·성별·연령대별 실적 API 후보입니다.",
        "2026-07-03 확인",
    ),
    "source.hf.bogeumjari-openapi": source_node(
        "source.hf.bogeumjari-openapi",
        "한국주택금융공사 u-보금자리론대출정보",
        "공공데이터포털",
        "https://www.data.go.kr/data/15082039/openapi.do?recommendDataYn=Y",
        "u-보금자리론 대출정보를 정책 주택담보대출 상품의 API 후보로 보존합니다.",
        "2026-07-03 확인",
    ),
    "source.data.go.kr.kinfa-loan-handling-agencies": source_node(
        "source.data.go.kr.kinfa-loan-handling-agencies",
        "서민금융진흥원 서민대출상품 취급기관 정보 서비스",
        "공공데이터포털",
        "https://www.data.go.kr/data/15074508/openapi.do",
        "서민대출상품별 기관명, 법인번호, 금융기관주소, 상품명 등 취급기관 정보를 제공하는 API 후보입니다.",
        "2026-07-03 확인",
    ),
    "source.data.go.kr.kinfa-support-centers": source_node(
        "source.data.go.kr.kinfa-support-centers",
        "서민금융진흥원 서민금융통합지원센터 현황",
        "공공데이터포털",
        "https://www.data.go.kr/data/15037733/openapi.do",
        "서민금융통합지원센터와 미소금융 지점의 지역, 지점명, 주소, 전화번호를 제공하는 API 후보입니다.",
        "2026-07-03 확인",
    ),
    "source.kdic.insured-products": source_node(
        "source.kdic.insured-products",
        "예금보험공사 예금자보호 금융상품",
        "공공데이터포털",
        "https://www.data.go.kr/data/3037352/openapi.do?recommendDataYn=Y",
        "금융회사별 예금자보호 대상 금융상품명, 금융회사명, 상품판매중단일자, 등록일을 제공하는 예금자보호 리스크 보강 API 후보입니다.",
        "2026-07-03 확인",
    ),
    "source.kinfa.hessal-loan-youth": source_node(
        "source.kinfa.hessal-loan-youth",
        "햇살론유스",
        "서민금융진흥원",
        "https://www.kinfa.or.kr/financialProduct/hessalLoanYoos.do",
        "청년·대학생 대상 햇살론유스의 지원대상, 보증한도, 보증기간, 대출금리와 보증료율 공식 안내입니다.",
        "2026-07-03 확인",
    ),
    "source.kinfa.illegal-private-finance-prevention-loan": source_node(
        "source.kinfa.illegal-private-finance-prevention-loan",
        "불법사금융예방대출",
        "서민금융진흥원",
        "https://www.kinfa.or.kr/financialProduct/smallLivingLoan.do",
        "대부업 이용도 어려운 저신용·저소득자 생계비 대출의 지원대상, 금리, 한도, 상환방식 공식 안내입니다.",
        "2026-07-03 확인",
    ),
    "source.myhome.support-lease-loan": source_node(
        "source.myhome.support-lease-loan",
        "버팀목전세대출",
        "마이홈포털",
        "https://www.myhome.go.kr/hws/portal/cont/selectSupLeaseLoanView.do",
        "근로자·서민 주거 안정을 위한 버팀목전세대출의 대상, 금리, 한도, 기간, 우대금리 공식 안내입니다.",
        "2026-07-03 확인",
    ),
    "source.hf.bogeumjari-loan": source_node(
        "source.hf.bogeumjari-loan",
        "보금자리론 상품소개",
        "한국주택금융공사",
        "https://www.hf.go.kr/ko/sub01/sub01_01_02.do",
        "보금자리론의 신청대상, 대출요건, 한도, 만기, 상환방식과 특성별 상품 공식 안내입니다.",
        "2026-07-03 확인",
    ),
    "source.crefia.card-lending-products": source_node(
        "source.crefia.card-lending-products",
        "카드대출상품",
        "여신금융협회",
        "https://gongsi.crefia.or.kr/portal/financialProdInfo/cardLendingProd",
        "단기카드대출(현금서비스)과 장기카드대출(카드론)의 기간, 한도, 이용방법, 수수료율과 유의사항을 설명하는 공식 공시입니다.",
        "2026-07-03 확인",
    ),
    "source.crefia.card-loan-revolving-rates": source_node(
        "source.crefia.card-loan-revolving-rates",
        "카드대출·결제성 리볼빙 신용점수별 수수료율",
        "여신금융협회",
        "https://gongsi.crefia.or.kr/portal/creditcard/creditcardDisclosureDetail20?cgcMode=20",
        "현금서비스, 카드론, 결제성 리볼빙의 신용점수별 금리·수수료율 비교공시 표면입니다.",
        "2026-07-03 확인",
    ),
    "source.fsc.revolving-service-improvement": source_node(
        "source.fsc.revolving-service-improvement",
        "신용카드 결제성 리볼빙 서비스 개선방안",
        "금융위원회",
        "https://www.fsc.go.kr/no010101/78357",
        "결제성 리볼빙 서비스의 설명의무, 수수료율 안내·공시 강화, 건전한 이용 유도 기준을 정리한 금융위원회 보도자료입니다.",
        "2026-07-03 확인",
    ),
    "source.crefia.lease-installment-products": source_node(
        "source.crefia.lease-installment-products",
        "리스할부상품",
        "여신금융협회",
        "https://gongsi.crefia.or.kr/portal/financialProdInfo/leaseProd",
        "자동차리스와 자동차·주택·가전·기계류·기타 할부 상품 공시 범위를 설명하는 공식 금융상품정보 표면입니다.",
        "2026-07-03 확인",
    ),
    "source.crefia.auto-lease-disclosure": source_node(
        "source.crefia.auto-lease-disclosure",
        "자동차리스 상품 리스료 비교 조회",
        "여신금융협회",
        "https://gongsi.crefia.or.kr/portal/quota/quotaFinancingDisclosureDetail60?ifgcMode=60",
        "자동차리스 금융상품의 리스료, 보증금·잔존가치 조건, 중도해지수수료 비교공시 표면입니다.",
        "2026-07-03 확인",
    ),
    "source.crefia.credit-loan-products": source_node(
        "source.crefia.credit-loan-products",
        "신용대출상품",
        "여신금융협회",
        "https://gongsi.crefia.or.kr/portal/financialProdInfo/creditLendingProd",
        "여신전문금융회사 신용대출과 민간중금리대출의 의미, 요건, 이용방법을 설명하는 공식 금융상품정보 표면입니다.",
        "2026-07-03 확인",
    ),
    "source.crefia.credit-loan-rate-disclosure": source_node(
        "source.crefia.credit-loan-rate-disclosure",
        "신용대출상품 신용점수별 평균금리현황",
        "여신금융협회",
        "https://gongsi.crefia.or.kr/portal/creditloan/creditloanDisclosureDetail11",
        "여신전문금융회사 신용대출상품의 신용점수 구간별 평균금리 비교공시 표면입니다.",
        "2026-07-03 확인",
    ),
    "source.crefia.card-products": source_node(
        "source.crefia.card-products",
        "카드상품 공시",
        "여신금융협회",
        "https://gongsi.crefia.or.kr/portal/financialProdInfo/cardProd",
        "신용카드와 체크카드 상품의 기본 공시 및 카드상품 비교 원천입니다.",
        "2026-07-03 확인",
    ),
    "source.crefia.carddamoa": source_node(
        "source.crefia.carddamoa",
        "카드다모아",
        "여신금융협회",
        "https://gongsi.crefia.or.kr/portal/carddamoa/carddamoaList",
        "카드사별 신용카드·체크카드 혜택, 전월실적, 할인·적립 조건을 비교하기 위한 공식 카드 비교 표면입니다.",
        "2026-07-03 확인",
    ),
    "source.kbcard.card-list": source_node(
        "source.kbcard.card-list",
        "KB국민카드 카드한눈에보기",
        "KB국민카드",
        "https://card.kbcard.com/CRD/DVIEW/HCAM0101",
        "KB국민카드 신용카드·체크카드 상품명, 상품코드, 주요혜택, 상세페이지 링크를 제공하는 발급사 공식 카드 목록입니다.",
        "2026-07-03 확인",
    ),
    "source.bccard.credit-card-list": source_node(
        "source.bccard.credit-card-list",
        "비씨카드 신용카드 상품",
        "비씨카드",
        "https://www.bccard.com/app/card/CreditCardMain.do",
        "비씨카드와 회원사의 신용카드 상품명, 발급사, 상품코드, 주요혜택을 제공하는 공식 카드 목록입니다.",
        "2026-07-03 확인",
    ),
    "source.bccard.check-card-list": source_node(
        "source.bccard.check-card-list",
        "비씨카드 체크카드 상품",
        "비씨카드",
        "https://www.bccard.com/app/card/CheckCardMain.do",
        "비씨카드와 회원사의 체크카드 상품명, 발급사, 상품코드, 주요혜택을 제공하는 공식 카드 목록입니다.",
        "2026-07-03 확인",
    ),
    "source.samsungcard.credit-card-list": source_node(
        "source.samsungcard.credit-card-list",
        "삼성카드 신용카드 상품",
        "삼성카드",
        "https://www.samsungcard.com/home/card/cardinfo/PGHPPDCCardCardinfoRecommendPC001",
        "삼성카드 신용카드 상품명, 상품코드, 주요혜택, 카드 이미지와 상세페이지 링크를 제공하는 공식 WCMS 카드 목록입니다.",
        "2026-07-03 확인",
    ),
    "source.samsungcard.check-card-list": source_node(
        "source.samsungcard.check-card-list",
        "삼성카드 체크카드 상품",
        "삼성카드",
        "https://www.samsungcard.com/home/card/cardinfo/PGHPPCCCardCardinfoCheckcard001",
        "삼성카드 체크카드 상품명, 상품코드, 주요혜택, 카드 이미지와 상세페이지 링크를 제공하는 공식 WCMS 카드 목록입니다.",
        "2026-07-03 확인",
    ),
    "source.einsmarket.insurance": source_node(
        "source.einsmarket.insurance",
        "온라인 보험슈퍼마켓 보험다모아",
        "보험다모아",
        "https://www.e-insmarket.or.kr/",
        "자동차보험, 실손의료보험, 여행자보험, 연금 등 보험상품 보험료 비교를 제공하는 공식 보험 비교 표면입니다.",
        "2026-07-03 확인",
    ),
    "source.klia.insurance-disclosure": source_node(
        "source.klia.insurance-disclosure",
        "생명보험협회 공시실",
        "생명보험협회",
        "https://pub.insure.or.kr/",
        "생명보험 상품 공시와 보장성 상품·변액보험 등 생명보험 상품 정보를 확인하는 공식 공시실입니다.",
        "2026-07-03 확인",
    ),
    "source.fsc.medical-reimbursement-insurance": source_node(
        "source.fsc.medical-reimbursement-insurance",
        "금융위원회 실손보험정보",
        "공공데이터포털",
        "https://www.data.go.kr/data/15094797/openapi.do",
        "생명보험협회 및 손해보험협회에서 제공하는 실손의료보험 유형, 담보, 성별·연령별 기준 보험료 API 후보입니다.",
        "2026-07-03 확인",
    ),
    "source.fsc.variable-insurance-info": source_node(
        "source.fsc.variable-insurance-info",
        "금융위원회 변액보험기본정보",
        "공공데이터포털",
        "https://www.data.go.kr/data/15094793/openapi.do",
        "생명보험협회 변액보험 펀드별 기준가, 순자산, 설정일자, 운용회사 정보를 제공하는 API 후보입니다.",
        "2026-07-03 확인",
    ),
    "source.fss.integrated-pension-portal": source_node(
        "source.fss.integrated-pension-portal",
        "통합연금포털",
        "금융감독원",
        "https://100lifeplan.fss.or.kr/",
        "연금저축 비교공시, 개인·퇴직연금 조회, 상품 유형별 수익률·수수료·위험등급 비교를 연결하기 위한 금융감독원 공식 포털입니다.",
        "2026-07-04 확인",
    ),
    "source.kofia.fund-oneclick": source_node(
        "source.kofia.fund-oneclick",
        "펀드정보 One-Click 시스템",
        "금융투자협회",
        "https://fund.kofia.or.kr/",
        "금감원, 금융투자협회, 운용사, 평가사 등의 펀드 관련 정보를 연결하는 금융투자협회 공식 펀드 정보 표면입니다.",
        "2026-07-04 확인",
    ),
    "source.fsc.funddamoa-guide": source_node(
        "source.fsc.funddamoa-guide",
        "펀드다모아 비교공시 안내",
        "금융위원회",
        "https://www.fsc.go.kr/no010101/72549",
        "공모펀드의 수익률, 위험도, 투자지역, 설정액, 총보수, 투자설명서와 판매사 정보를 비교하는 펀드다모아 공시 근거입니다.",
        "2026-07-04 확인",
    ),
    "source.fsc.fund-products-basic": source_node(
        "source.fsc.fund-products-basic",
        "금융위원회 펀드상품기본정보",
        "공공데이터포털",
        "https://www.data.go.kr/data/15094792/openapi.do",
        "금융투자협회 펀드표준코드 기반의 펀드 명칭, 코드, 운용사, 펀드유형 정보를 제공하는 공식 API 후보입니다.",
        "2026-07-03 확인",
    ),
    "source.fsc.financial-investment-statistics": source_node(
        "source.fsc.financial-investment-statistics",
        "금융위원회 금융투자협회종합통계정보",
        "공공데이터포털",
        "https://www.data.go.kr/data/15094809/openapi.do",
        "펀드 순자산, CMA 잔고, 신용공여 잔고, 증시자금 추이 등 자본시장 통계 API 후보입니다.",
        "2026-07-04 확인",
    ),
    "source.fsc.retirement-pension-basic": source_node(
        "source.fsc.retirement-pension-basic",
        "금융위원회 퇴직연금기본정보",
        "공공데이터포털",
        "https://www.data.go.kr/data/15094798/openapi.do",
        "퇴직연금 상품·운용 관련 기본정보를 투자상품 축으로 연결하기 위한 공식 API 후보입니다.",
        "2026-07-03 확인",
    ),
    "source.knia.insurance-disclosure": source_node(
        "source.knia.insurance-disclosure",
        "손해보험협회 공시실",
        "손해보험협회",
        "https://kpub.knia.or.kr/",
        "손해보험 상품 공시, 보험료 비교, 판매상태 확인을 위한 손해보험 업권 공시 원천입니다.",
        "2026-07-03 확인",
    ),
    "source.knia.claim-nonpayment": source_node(
        "source.knia.claim-nonpayment",
        "손해보험협회 보험금부지급률/청구이후 해지비율",
        "손해보험협회",
        "https://consumer.knia.or.kr/disclosure/item/07.do",
        "손해보험사별 보험금 부지급률과 청구 이후 해지비율을 보험상품 리스크 신호로 연결하기 위한 공식 공시 표면입니다.",
        "2026-07-03 확인",
    ),
    "source.knia.mis-selling": source_node(
        "source.knia.mis-selling",
        "손해보험협회 불완전판매비율",
        "손해보험협회",
        "https://consumer.knia.or.kr/disclosure/item/04.do",
        "손해보험사별·상품별 불완전판매비율을 판매채널 리스크 신호로 연결하기 위한 공식 공시 표면입니다.",
        "2026-07-03 확인",
    ),
    "source.easylaw.finance-product-disclosure": source_node(
        "source.easylaw.finance-product-disclosure",
        "금융상품 비교공시 범위",
        "찾기쉬운 생활법령정보",
        "https://www.easylaw.go.kr/CSP/CnpClsMainBtr.laf?ccfNo=1&cciNo=1&cnpClsNo=1&csmSeq=1771",
        "금융상품 비교공시 항목에 이자율, 보험료, 수수료, 중도상환수수료율, 위험등급, 공시시점 등이 포함된다는 근거입니다.",
        "2026-07-03 확인",
    ),
}

CARD_SOURCE_IDS = [
    "source.crefia.card-products",
    "source.crefia.carddamoa",
    "source.kbcard.card-list",
    "source.bccard.credit-card-list",
    "source.bccard.check-card-list",
    "source.samsungcard.credit-card-list",
    "source.samsungcard.check-card-list",
]


def attach_source_metadata(items: list[dict]) -> list[dict]:
    by_id = {item["id"]: item for item in items}
    for item in items:
        if item["type"] == "source":
            continue
        source_urls: list[str] = []
        source_basis_dates: list[str] = []
        for source_id in item.get("sources") or []:
            source = by_id.get(source_id) or SOURCES.get(source_id)
            if not source:
                continue
            if source.get("url"):
                source_urls.append(str(source["url"]))
            if source.get("basis_date"):
                source_basis_dates.append(str(source["basis_date"]))
        item["source_urls"] = unique((item.get("source_urls") or []) + source_urls)
        item["source_basis_dates"] = unique((item.get("source_basis_dates") or []) + source_basis_dates)
    return items


def load_generated(domain: str) -> list[dict]:
    path = GENERATED_FILES[domain]
    if not path.exists():
        return []
    payload = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(payload, dict):
        raw_items = payload.get("items") or []
    elif isinstance(payload, list):
        raw_items = payload
    else:
        raise ValueError(f"{path}: generated payload must be a list or object with items")
    return [dict(item) for item in raw_items]


def generated_status(domain: str, product_count: int) -> dict:
    generated_path = GENERATED_FILES[domain]
    return {
        "generated_from": str(generated_path.relative_to(REPO_ROOT)),
        "generated_file_exists": generated_path.exists(),
        "product_count": product_count,
        "crawl_status": "loaded" if product_count else "awaiting_official_api_or_scrape",
        "crawl_note": (
            "금융상품 실데이터는 공식 API 키 또는 공시 페이지 스크레이프 결과가 있을 때 생성됩니다. "
            "상품 노드가 생성되면 provider, product_code, product_status, collected_at, source_record_id, "
            "source_urls, source_basis_dates 필드를 필수로 보존합니다."
        ),
    }


def product_counts(items: list[dict], product_type: str) -> int:
    return sum(1 for item in items if item.get("type") == product_type)


PRODUCT_TYPES = {"card-product", "bank-product", "insurance-product"}
PRODUCT_EXPORTS = (CARD_EXPORT, DEPOSIT_EXPORT, SAVING_EXPORT, LOAN_EXPORT, INSURANCE_EXPORT)
REFERENCE_SOURCE_IDS = [
    "source.fsc.financial-company-basic",
    "source.fsc.financial-company-credit",
    "source.fss.fine.portal",
    "source.fsc.rate-disclosure-guide",
    "source.kfb.consumer-portal",
    "source.fsc.domestic-bank-statistics",
    "source.fsb.savings-bank-deposit-rates",
    "source.bok.ecos",
    "source.fsc.cofix-overview",
    "source.knia.claim-nonpayment",
    "source.knia.mis-selling",
    "source.fss.integrated-pension-portal",
    "source.kofia.fund-oneclick",
    "source.fsc.funddamoa-guide",
    "source.fsc.fund-products-basic",
    "source.fsc.financial-investment-statistics",
    "source.fsc.retirement-pension-basic",
    "source.fsc.inclusive-finance-products",
    "source.fsc.inclusive-finance-performance",
    "source.hf.bogeumjari-openapi",
    "source.data.go.kr.kinfa-loan-products",
    "source.data.go.kr.kinfa-loan-handling-agencies",
    "source.data.go.kr.kinfa-support-centers",
]


def load_product_export_items() -> list[dict]:
    items: list[dict] = []
    for path in PRODUCT_EXPORTS:
        if not path.exists():
            continue
        payload = json.loads(path.read_text(encoding="utf-8"))
        items.extend(
            dict(item)
            for item in payload.get("items") or []
            if item.get("type") in PRODUCT_TYPES
        )
    return items


def provider_id(provider: str) -> str:
    digest = hashlib.sha1(provider.encode("utf-8")).hexdigest()[:12]
    return f"finance.provider.{digest}"


def semantic_product_related(item: dict) -> list[str]:
    related: list[str] = ["category.finance.source-health"]
    provider = str(item.get("provider") or "").strip()
    if provider:
        related.extend([provider_id(provider), "category.finance.financial-provider-registry"])

    if item.get("type") == "card-product":
        related.extend([
            "term.card.previous-month-spend",
            "term.card.monthly-benefit-limit",
            "term.card.excluded-spend",
        ])
    elif item.get("type") == "bank-product":
        product_context = " ".join([
            str(item.get("product_kind") or "").lower(),
            " ".join(str(tag).lower() for tag in item.get("tags") or []),
            str(item.get("title") or "").lower(),
        ])
        related.extend(["category.finance.benchmark-rates", "finance.benchmark-rate.bok-base-rate"])
        if any(keyword in product_context for keyword in ("loan", "대출", "mortgage", "주택", "전세", "credit", "신용")):
            related.append("finance.benchmark-rate.cofix")
    elif item.get("type") == "insurance-product":
        related.extend([
            "category.finance.insurance-risk-signals",
            "finance.risk-signal.insurance-nonpayment-rate",
            "finance.risk-signal.insurance-mis-selling-rate",
            "term.finance.provider-risk",
        ])
    return unique(related)


def bank_search_type(item: dict) -> str | None:
    if item.get("type") != "bank-product":
        return None
    kind = str(item.get("product_kind") or "").lower()
    tags = {str(tag).lower() for tag in item.get("tags") or []}
    if kind == "deposit-protection" or "deposit-protection" in tags:
        return "deposit-protection"
    if kind in {"deposit", "time-deposit"} or "deposit" in tags:
        return "deposit"
    if kind in {"saving", "savings"} or "saving" in tags:
        return "saving"
    if "loan" in kind or any("loan" in tag for tag in tags):
        return "loan"
    return kind or None


COMPOUND_MONEY_RE = re.compile(r"(\d+(?:[,.]\d+)?)\s*만\s*(\d+(?:[,.]\d+)?)\s*천원")
MONEY_RE = re.compile(r"(\d+(?:[,.]\d+)?)\s*(만원|천원|원)")


def parse_krw_amount(text: str) -> int | None:
    compact_text = text.replace(",", "")
    compound_match = COMPOUND_MONEY_RE.search(compact_text)
    if compound_match:
        man_text, cheon_text = compound_match.groups()
        try:
            return int(float(man_text) * 10000 + float(cheon_text) * 1000)
        except ValueError:
            return None

    match = MONEY_RE.search(compact_text)
    if not match:
        return None
    number_text, unit = match.groups()
    try:
        value = float(number_text)
    except ValueError:
        return None
    compact_unit = unit.replace(" ", "")
    if compact_unit == "만원":
        return int(value * 10000)
    if compact_unit == "천원":
        return int(value * 1000)
    return int(value)


def card_benefit_text(benefit: dict) -> str:
    return " ".join(
        str(benefit.get(key) or "")
        for key in ("kind", "label", "text", "benefit", "condition")
    )


def has_no_previous_month_spend(text: str) -> bool:
    compact = text.replace(" ", "").lower()
    return any(
        keyword in compact
        for keyword in (
            "no전월실적",
            "전월실적없음",
            "전월이용금액조건없음",
            "전월이용금액없음",
            "전월실적조건없음",
        )
    )


def has_no_annual_fee(text: str) -> bool:
    compact = text.replace(" ", "").lower()
    return any(keyword in compact for keyword in ("no연회비", "연회비없음", "연회비면제"))


def benefit_type(text: str) -> str | None:
    if any(keyword in text for keyword in ("적립", "포인트", "마일리지", "캐시백")):
        return "point_accumulation"
    if "할인" in text:
        return "discount"
    return None


def monthly_benefit_limit_krw(text: str) -> int | None:
    compact = text.replace(" ", "")
    if "월" not in compact and "매월" not in compact:
        return None
    if not any(keyword in compact for keyword in ("최대", "한도")):
        return None
    return parse_krw_amount(text)


BENEFIT_RATE_RE = re.compile(r"(\d+(?:\.\d+)?)\s*%")
# 카드 benefit 문자열 조건 필드화 패턴 (공백 제거 후 매칭)
PREV_MONTH_SPEND_MIN_RE = re.compile(r"전월(?:카드)?(?:이용)?(?:실적|금액)(\d+(?:\.\d+)?)(만원|천원|원)이상")
ANNUAL_FEE_AMOUNT_RE = re.compile(r"연회비:?(\d+(?:\.\d+)?)(만원|천원|원)")
PER_TRANSACTION_RE = re.compile(r"(?:1?건당|회당)(\d+(?:\.\d+)?)(만원|천원|원)")
INTEGRATED_LIMIT_RE = re.compile(r"통합한도(?:월)?(\d+(?:\.\d+)?)(만원|천원|원)")


def krw_amount(number_text: str, unit: str) -> int | None:
    try:
        value = float(number_text)
    except ValueError:
        return None
    if unit == "만원":
        return int(value * 10000)
    if unit == "천원":
        return int(value * 1000)
    return int(value)


def card_benefit_rate_percent(text: str) -> float | None:
    match = BENEFIT_RATE_RE.search(text)
    return float(match.group(1)) if match else None


def enrich_card_benefits(item: dict) -> None:
    if item.get("type") != "card-product":
        return
    for benefit in item.get("benefits") or []:
        if not isinstance(benefit, dict):
            continue
        text = card_benefit_text(benefit)
        compact = text.replace(",", "").replace(" ", "")
        if has_no_previous_month_spend(text):
            benefit["previous_month_spend_required"] = False
            benefit["previous_month_spend_min_krw"] = 0
        elif (spend_match := PREV_MONTH_SPEND_MIN_RE.search(compact)):
            benefit["previous_month_spend_required"] = True
            benefit["previous_month_spend_min_krw"] = krw_amount(*spend_match.groups())
        else:
            benefit.setdefault("previous_month_spend_required", None)
        benefit.setdefault("previous_month_spend_min_krw", None)
        parsed_monthly_limit = monthly_benefit_limit_krw(text)
        if parsed_monthly_limit is None and (limit_match := INTEGRATED_LIMIT_RE.search(compact)):
            parsed_monthly_limit = krw_amount(*limit_match.groups())
        if parsed_monthly_limit is not None:
            benefit["monthly_benefit_limit_krw"] = parsed_monthly_limit
        else:
            benefit.setdefault("monthly_benefit_limit_krw", None)
        if has_no_annual_fee(text):
            benefit["annual_fee_required"] = False
            benefit["annual_fee_krw"] = 0
        elif (fee_match := ANNUAL_FEE_AMOUNT_RE.search(compact)):
            benefit["annual_fee_required"] = True
            benefit["annual_fee_krw"] = krw_amount(*fee_match.groups())
        else:
            benefit.setdefault("annual_fee_required", None)
        benefit.setdefault("annual_fee_krw", None)
        parsed_benefit_type = benefit_type(text)
        if parsed_benefit_type:
            benefit["benefit_type"] = parsed_benefit_type
        else:
            benefit.setdefault("benefit_type", None)
        parsed_rate = card_benefit_rate_percent(text)
        if parsed_rate is not None:
            benefit["benefit_rate_percent"] = parsed_rate
        else:
            benefit.setdefault("benefit_rate_percent", None)
        if (per_tx_match := PER_TRANSACTION_RE.search(compact)):
            benefit["per_transaction_limit_krw"] = krw_amount(*per_tx_match.groups())
        benefit.setdefault("per_transaction_limit_krw", None)
        benefit.setdefault("excluded_spend", [])
        missing = []
        for key in ("previous_month_spend_min_krw", "monthly_benefit_limit_krw", "per_transaction_limit_krw", "excluded_spend"):
            value = benefit.get(key)
            if value is None or value == "" or value == []:
                missing.append(key)
        normalized = any(
            benefit.get(key) is not None and benefit.get(key) != "" and benefit.get(key) != []
            for key in ("previous_month_spend_min_krw", "monthly_benefit_limit_krw", "annual_fee_required", "benefit_type", "benefit_rate_percent")
        )
        benefit["condition_completeness"] = "partial" if missing and normalized else ("incomplete" if missing else "complete")
        benefit["missing_condition_fields"] = missing
        benefit["condition_parse_source"] = "benefit_text" if normalized else None


def enrich_insurance_coverage(item: dict) -> None:
    if item.get("type") != "insurance-product":
        return
    criteria = [criterion for criterion in item.get("criteria") or [] if isinstance(criterion, dict)]
    premium = next((criterion for criterion in criteria if criterion.get("criteria_kind") == "premium"), {})
    renewal = next((criterion for criterion in criteria if criterion.get("criteria_kind") == "renewal"), {})
    renewal_text = str(renewal.get("condition") or "")
    renewal_type = None
    if "비갱신" in renewal_text:
        renewal_type = "non_renewable"
    elif "갱신" in renewal_text:
        renewal_type = "renewable"
    for criterion in criteria:
        if criterion.get("criteria_kind") != "coverage":
            continue
        criterion.setdefault("coverage_name", criterion.get("benefit") or criterion.get("condition") or criterion.get("label"))
        criterion.setdefault("coverage_amount_krw", None)
        criterion.setdefault("premium_male_krw", premium.get("premium_male_krw"))
        criterion.setdefault("premium_female_krw", premium.get("premium_female_krw"))
        criterion.setdefault("renewal_type", renewal_type)
        criterion.setdefault("renewal_cycle_years", None)
        criterion.setdefault("waiting_period_days", None)
        criterion.setdefault("reduction_period_days", None)
        missing = [
            key
            for key in ("coverage_amount_krw", "renewal_cycle_years", "waiting_period_days", "reduction_period_days")
            if criterion.get(key) is None
        ]
        criterion["condition_completeness"] = "incomplete" if missing else "complete"
        criterion["missing_condition_fields"] = missing


def apply_recommendation_scope(item: dict) -> None:
    if item.get("type") == "insurance-product":
        incomplete = any(
            isinstance(criterion, dict)
            and criterion.get("criteria_kind") == "coverage"
            and criterion.get("condition_completeness") == "incomplete"
            for criterion in item.get("criteria") or []
        )
        if incomplete:
            item["recommendation_scope"] = "listing_only"
            item["recommendation_exclusion_reasons"] = unique([
                *(item.get("recommendation_exclusion_reasons") or []),
                "incomplete_insurance_coverage_conditions",
            ])
            # 핵심 조건(보장금액·갱신주기·면책·감액)이 비어 있으면 추천 승격을 금지한다.
            if item.get("recommendation_status") == "eligible_for_recommendation":
                item["recommendation_status"] = "eligible_for_listing"
    if item.get("type") == "card-product":
        partial_or_incomplete = any(
            isinstance(benefit, dict)
            and benefit.get("condition_completeness") in {"partial", "incomplete"}
            for benefit in item.get("benefits") or []
        )
        if partial_or_incomplete:
            item["recommendation_scope"] = "listing_only"
            item["recommendation_exclusion_reasons"] = unique([
                *(item.get("recommendation_exclusion_reasons") or []),
                "incomplete_card_benefit_conditions",
            ])


LOAN_REQUIRED_FIELDS = (
    "loan_rate_min_percent",
    "loan_rate_max_percent",
    "repayment_method",
    "loan_limit_krw",
    "early_repayment_fee",
    "eligible_borrower",
    "collateral_type",
)
RATE_NUMBER_RE = re.compile(r"(\d+(?:\.\d+)?)")


def synthesize_credit_loan_rate_criteria(item: dict) -> None:
    """신용대출은 FSS optionList의 등급별 금리만 있고 criteria가 비어 있다.
    공시된 대출금리(crdt_grad_*)의 최저·최고값을 rate criteria로 옮겨 담는다."""
    if item.get("product_kind") != "credit-loan" or item.get("criteria"):
        return
    rates = [
        value
        for option in item.get("options") or []
        if isinstance(option, dict) and option.get("crdt_lend_rate_type_nm") == "대출금리"
        for key, value in option.items()
        if key.startswith("crdt_grad_") and isinstance(value, (int, float))
    ]
    if not rates:
        return
    item["criteria"] = [
        {
            "label": label,
            "basis": "신용등급별 대출금리",
            "condition": f"{label} {value}%",
            "source": "source.fss.finlife.api",
            "criteria_kind": "rate",
            "basis_category": "금융상품 공시 금리",
            "basis_definition": "금융감독원 금융상품한눈에 API의 신용대출 등급별 금리 필드입니다.",
            "basis_lookup": "creditLoanProductsSearch optionList의 crdt_grad_* 필드에서 확인합니다.",
            "selection_rule": "공시된 신용등급별 대출금리의 최저·최고값입니다.",
            "basis_source": "source.fss.finlife.api",
            "rate_percent": value,
            "rate_label": label,
            "rate_basis": "신용등급별",
        }
        for label, value in (("최저금리", min(rates)), ("최고금리", max(rates)))
    ]


def normalize_loan_product(item: dict) -> None:
    if item.get("type") != "bank-product" or item.get("search_type") != "loan":
        return
    synthesize_credit_loan_rate_criteria(item)
    raw = item.get("raw") if isinstance(item.get("raw"), dict) else {}
    options = [option for option in item.get("options") or [] if isinstance(option, dict)]
    criteria = [criterion for criterion in item.get("criteria") or [] if isinstance(criterion, dict)]

    rates = [criterion["rate_percent"] for criterion in criteria if isinstance(criterion.get("rate_percent"), (int, float))]
    rates += [option[key] for option in options for key in ("lend_rate_min", "lend_rate_max") if isinstance(option.get(key), (int, float))]
    if not rates:
        rates = [float(value) for value in RATE_NUMBER_RE.findall(str(raw.get("irt") or ""))]
    item["loan_rate_min_percent"] = min(rates) if rates else None
    item["loan_rate_max_percent"] = max(rates) if rates else None

    repayment = unique([str(option["rpay_type_nm"]) for option in options if option.get("rpay_type_nm")])
    if not repayment and raw.get("rdptmthd") and str(raw["rdptmthd"]) not in {"-", ""}:
        repayment = [str(raw["rdptmthd"])]
    item["repayment_method"] = ", ".join(repayment) if repayment else None

    limit_text = str(raw.get("loan_lmt") or raw.get("lnlmt") or "").strip()
    limit_krw = None
    if limit_text.isdigit():
        # 서민금융진흥원 lnlmt는 만원 단위 숫자 문자열이다.
        limit_krw = int(limit_text) * 10000
    elif limit_text:
        limit_krw = parse_krw_amount(limit_text)
    item["loan_limit_krw"] = limit_krw
    item["loan_limit_text"] = limit_text or None

    fee_text = str(raw.get("erly_rpay_fee") or "").strip()
    item["early_repayment_fee"] = fee_text or None

    borrower = str(raw.get("trgt") or raw.get("crdt_prdt_type_nm") or "").strip()
    item["eligible_borrower"] = borrower or None

    collateral = unique([str(option["mrtg_type_nm"]) for option in options if option.get("mrtg_type_nm")])
    if collateral:
        item["collateral_type"] = ", ".join(collateral)
    elif item.get("product_kind") == "credit-loan":
        item["collateral_type"] = "신용(무담보)"
    else:
        item["collateral_type"] = None

    missing = [
        field
        for field in LOAN_REQUIRED_FIELDS
        if item.get(field) is None and not (field == "loan_limit_krw" and item.get("loan_limit_text"))
    ]
    item["missing_loan_required_fields"] = missing

    if item.get("status") == "active" and not item.get("criteria"):
        item["recommendation_status"] = "reference_only"
        item["status_reason"] = "대출 비교·추천에 필요한 criteria가 비어 있어 참조 전용으로만 노출합니다."
        item["quality_flags"] = unique([*(item.get("quality_flags") or []), "missing_loan_criteria"])
    if missing:
        item["recommendation_scope"] = "listing_only"
        item["recommendation_exclusion_reasons"] = unique([
            *(item.get("recommendation_exclusion_reasons") or []),
            "incomplete_loan_required_fields",
        ])
        item["quality_flags"] = unique([*(item.get("quality_flags") or []), "missing_loan_required_fields"])
        if item.get("recommendation_status") == "eligible_for_recommendation":
            item["recommendation_status"] = "eligible_for_listing"


def provider_registry_nodes(products: list[dict]) -> list[dict]:
    providers: dict[str, dict] = {}
    for product in products:
        provider = str(product.get("provider") or "").strip()
        if not provider:
            continue
        entry = providers.setdefault(
            provider,
            {
                "count": 0,
                "sectors": set(),
                "kinds": set(),
                "statuses": set(),
                "samples": [],
            },
        )
        entry["count"] += 1
        for key, target in (
            ("financial_sector", "sectors"),
            ("product_kind", "kinds"),
            ("status", "statuses"),
        ):
            value = product.get(key)
            if value:
                entry[target].add(str(value))
        if len(entry["samples"]) < 5 and product.get("id"):
            entry["samples"].append(str(product["id"]))

    return [
        node(
            provider_id(provider),
            provider,
            "financial-provider",
            f"OpenFin 상품 export에서 {data['count']}개 금융상품의 제공자로 확인된 금융회사·기관입니다.",
            parents=["category.finance.financial-provider-registry"],
            sources=["source.fsc.financial-company-basic", "source.fsc.financial-company-credit"],
            tags=["finance-reference-ontology", "financial-provider"],
            covered_product_count=data["count"],
            covered_product_sectors=sorted(data["sectors"]),
            covered_product_kinds=sorted(data["kinds"]),
            observed_product_statuses=sorted(data["statuses"]),
            sample_product_ids=data["samples"],
        )
        for provider, data in sorted(providers.items(), key=lambda item: (-item[1]["count"], item[0]))
    ]


def finance_reference_items() -> list[dict]:
    products = load_product_export_items()
    deposit_protection_generated = load_generated("deposit_protection")
    for dp_item in deposit_protection_generated:
        # 예금자보호 등재 목록은 은행 상품군이 아니라 소비자 보호 레지스트리(참조 데이터)로 취급한다.
        # PRODUCT_TYPES 밖의 기존 타입으로 재분류해 상품 검증·상품 수 집계 대상에서 제외한다.
        dp_item["type"] = "financial-product"
        dp_item.setdefault("search_type", "deposit-protection")
        dp_item.setdefault("rate_search_eligible", False)
    items = [
        node(
            "finance.reference-ontology",
            "금융 기준정보 온톨로지",
            "domain",
            "금융상품을 한 MCP에서 비교·판정하기 위해 금융회사, 기준금리, 보험 리스크, 투자상품 후보, 정책금융 출처 상태를 묶는 기준정보 온톨로지입니다.",
            children=[
                "category.finance.financial-provider-registry",
                "category.finance.benchmark-rates",
                "category.finance.bank-rate-disclosure",
                "category.finance.insurance-risk-signals",
                "category.finance.investment-products",
                "category.finance.pension-products",
                "category.finance.consumer-protection-signals",
                "category.finance.policy-finance-reference",
                "category.finance.source-health",
            ],
            sources=REFERENCE_SOURCE_IDS,
            tags=["finance-reference-ontology", "openfin-ontology"],
        ),
        node(
            "category.finance.financial-provider-registry",
            "금융회사 레지스트리",
            "category",
            "상품 제공자 문자열을 금융회사 개요·재무·신용정보와 연결하기 위한 기준 축입니다.",
            parents=["finance.reference-ontology"],
            sources=["source.fsc.financial-company-basic", "source.fsc.financial-company-credit", "source.fsc.domestic-bank-statistics"],
            terms=["term.finance.provider-risk"],
            tags=["finance-reference-ontology", "provider-registry"],
        ),
        node(
            "category.finance.benchmark-rates",
            "기준금리·시장지표",
            "category",
            "예금·대출·투자상품 수익률을 설명할 때 기준선으로 쓰는 한국은행 기준금리, 시장금리, COFIX, 환율 지표입니다.",
            parents=["finance.reference-ontology"],
            sources=["source.bok.ecos", "source.fsc.cofix-overview", "source.kfb.consumer-portal"],
            tags=["finance-reference-ontology", "benchmark-rate"],
        ),
        node(
            "category.finance.bank-rate-disclosure",
            "은행권 금리·예대금리차 공시",
            "category",
            "은행별 대출금리, 예금금리, 예대금리차, COFIX와 저축은행 예·적금 금리공시를 상품 비교의 기준 지표로 묶는 축입니다.",
            parents=["finance.reference-ontology"],
            sources=[
                "source.fsc.rate-disclosure-guide",
                "source.kfb.consumer-portal",
                "source.fsb.savings-bank-deposit-rates",
            ],
            terms=["term.finance.loan-deposit-spread", "term.finance.benchmark-rate"],
            tags=["finance-reference-ontology", "bank-rate-disclosure", "risk-control"],
        ),
        node(
            "category.finance.insurance-risk-signals",
            "보험 리스크 신호",
            "category",
            "보험상품 추천 전 확인해야 하는 불완전판매율, 보험금 부지급률, 청구 이후 해지비율, 손해보험 공시 출처입니다.",
            parents=["finance.reference-ontology"],
            sources=["source.knia.claim-nonpayment", "source.knia.mis-selling", "source.knia.insurance-disclosure"],
            terms=["term.finance.provider-risk"],
            tags=["finance-reference-ontology", "insurance-risk"],
        ),
        node(
            "category.finance.investment-products",
            "투자상품 후보",
            "category",
            "펀드, 퇴직연금, 변액보험 펀드처럼 예금·대출·보험과 함께 비교될 수 있는 투자성 금융상품 후보입니다.",
            parents=["finance.reference-ontology"],
            sources=[
                "source.fsc.fund-products-basic",
                "source.fsc.retirement-pension-basic",
                "source.fsc.variable-insurance-info",
                "source.kofia.fund-oneclick",
                "source.fsc.funddamoa-guide",
                "source.fsc.financial-investment-statistics",
            ],
            tags=["finance-reference-ontology", "investment-products", "candidate-import"],
        ),
        node(
            "category.finance.pension-products",
            "연금저축·퇴직연금 상품",
            "category",
            "연금저축, 퇴직연금, IRP, 연금보험의 수익률, 수수료, 위험등급, 판매사별 적립금과 운용상품 정보를 연결하는 축입니다.",
            parents=["finance.reference-ontology", "category.finance.investment-products"],
            sources=[
                "source.fss.integrated-pension-portal",
                "source.fss.finlife.api",
                "source.fsc.retirement-pension-basic",
                "source.fsc.fund-products-basic",
            ],
            terms=["term.finance.pension-savings-return-fee", "term.finance.fund-risk-grade"],
            tags=["finance-reference-ontology", "pension", "retirement-pension", "candidate-import"],
        ),
        node(
            "category.finance.consumer-protection-signals",
            "금융소비자 보호 신호",
            "category",
            "숨은 금융자산, 예금자보호, 금융회사 리스크, 보험 부지급·불완전판매처럼 상품 선택 전 확인해야 하는 소비자 보호 신호입니다.",
            parents=["finance.reference-ontology"],
            sources=[
                "source.fss.fine.portal",
                "source.kdic.insured-products",
                "source.knia.claim-nonpayment",
                "source.knia.mis-selling",
            ],
            terms=["term.finance.provider-risk", "term.finance.deposit-protection-status", "term.finance.hidden-financial-assets"],
            tags=["finance-reference-ontology", "consumer-protection", "risk-control"],
        ),
        node(
            "category.finance.deposit-protection-products",
            "예금자보호 금융상품",
            "category",
            "예금보험공사 보호대상 금융상품 API에서 상품명, 금융회사명, 등록일을 수집한 소비자 보호 레지스트리입니다. 은행 상품군이 아니라 예금자보호 대상 여부를 확인하는 참조 데이터로 분류합니다. 상품판매중단일자가 있는 행은 기본 운영 export에서 제외합니다.",
            parents=["category.finance.consumer-protection-signals"],
            sources=["source.kdic.insured-products"],
            terms=["term.finance.deposit-protection-status", "term.finance.source-approval-risk"],
            tags=["finance-reference-ontology", "deposit-protection", "consumer-protection", "risk-control", "api-import-ready"],
        ),
        node(
            "term.finance.deposit-protection-status",
            "예금자보호 여부",
            "term",
            "예금보험공사 보호대상 금융상품 목록에 등재됐는지와 상품판매중단일자가 있는지를 확인하는 소비자 보호 기준입니다.",
            sources=["source.kdic.insured-products"],
            tags=["finance-reference-ontology", "deposit-protection", "consumer-protection"],
        ),
        node(
            "category.finance.policy-finance-reference",
            "정책금융 기준정보",
            "category",
            "서민금융상품, 정책 주택대출, 취급기관, 상담센터, 지원실적을 기존 대출상품과 연결하기 위한 기준 축입니다.",
            parents=["finance.reference-ontology"],
            sources=[
                "source.fsc.inclusive-finance-products",
                "source.fsc.inclusive-finance-performance",
                "source.hf.bogeumjari-openapi",
                "source.data.go.kr.kinfa-loan-products",
                "source.data.go.kr.kinfa-loan-handling-agencies",
                "source.data.go.kr.kinfa-support-centers",
            ],
            tags=["finance-reference-ontology", "policy-finance"],
        ),
        node(
            "category.finance.source-health",
            "출처 접근 상태",
            "category",
            "API 활용신청, 403, endpoint mapping, WAF, 수집 성공일을 상품 노드와 분리해 추적하는 운영 기준 축입니다.",
            parents=["finance.reference-ontology"],
            sources=REFERENCE_SOURCE_IDS,
            tags=["finance-reference-ontology", "source-health", "risk-control"],
        ),
        node(
            "term.finance.provider-risk",
            "금융회사 리스크",
            "term",
            "상품 제공자의 재무·신용, 경영지표, 불완전판매, 부지급률, 제재·폐지 여부를 상품 비교 전에 확인하는 리스크 축입니다.",
            sources=["source.fsc.financial-company-basic", "source.fsc.financial-company-credit", "source.knia.claim-nonpayment", "source.knia.mis-selling"],
            tags=["finance-reference-ontology", "risk-signal"],
        ),
        node(
            "term.finance.benchmark-rate",
            "기준금리",
            "term",
            "상품 금리나 수익률을 단독 숫자가 아니라 시점별 시장 기준선과 함께 해석하기 위한 비교 기준입니다.",
            sources=["source.bok.ecos", "source.fsc.cofix-overview"],
            tags=["finance-reference-ontology", "benchmark-rate"],
        ),
        node(
            "term.finance.status-event",
            "상품 상태 변경 이벤트",
            "term",
            "신규, 조건변경, 판매중단, 만료, 폐지처럼 금융상품의 현재 추천 가능성을 바꾸는 상태 전이입니다.",
            sources=REFERENCE_SOURCE_IDS,
            tags=["finance-reference-ontology", "status-event"],
        ),
        node(
            "term.finance.loan-deposit-spread",
            "예대금리차",
            "term",
            "은행의 대출금리에서 저축성 수신금리를 뺀 차이로, 은행권 금리 경쟁과 소비자 비용을 함께 점검하는 지표입니다.",
            sources=["source.fsc.rate-disclosure-guide", "source.kfb.consumer-portal"],
            tags=["finance-reference-ontology", "bank-rate-disclosure"],
        ),
        node(
            "term.finance.fund-risk-grade",
            "펀드·ETF 위험등급",
            "term",
            "펀드와 ETF의 투자 위험 수준을 상품 비교 화면에서 직관적으로 확인하기 위한 등급 정보입니다.",
            sources=["source.fss.integrated-pension-portal", "source.fsc.funddamoa-guide"],
            tags=["finance-reference-ontology", "investment-risk", "pension"],
        ),
        node(
            "term.finance.total-expense-ratio",
            "총보수·수수료",
            "term",
            "펀드, 연금저축, 퇴직연금 상품의 장기 수익률을 비교할 때 함께 봐야 하는 운용보수와 판매수수료 기준입니다.",
            sources=["source.kofia.fund-oneclick", "source.fss.integrated-pension-portal"],
            tags=["finance-reference-ontology", "fee", "investment-products"],
        ),
        node(
            "term.finance.pension-savings-return-fee",
            "연금저축 수익률·수수료율",
            "term",
            "연금저축 상품군별 수익률과 수수료율을 함께 비교해 장기 납입 비용과 성과를 판단하는 기준입니다.",
            sources=["source.fss.integrated-pension-portal"],
            tags=["finance-reference-ontology", "pension", "fee", "return"],
        ),
        node(
            "term.finance.sales-channel-balance",
            "판매사별 적립금",
            "term",
            "연금저축상품을 판매·관리하는 금융회사별 적립금 규모로, 판매사 선택과 운용 성과 비교에 쓰는 보조 지표입니다.",
            sources=["source.fss.integrated-pension-portal"],
            tags=["finance-reference-ontology", "pension", "sales-channel"],
        ),
        node(
            "term.finance.hidden-financial-assets",
            "숨은 금융자산",
            "term",
            "장기간 찾지 않은 예금, 보험금, 증권 등 금융자산을 금융소비자 정보포털과 계좌정보 조회 서비스에서 확인하는 소비자 보호 항목입니다.",
            sources=["source.fss.fine.portal"],
            tags=["finance-reference-ontology", "consumer-protection"],
        ),
        node(
            "finance.benchmark-rate.bok-base-rate",
            "한국은행 기준금리",
            "benchmark-rate",
            "예금·대출 금리와 금융시장 금리 해석의 기준선으로 쓰는 한국은행 정책금리 지표입니다.",
            parents=["category.finance.benchmark-rates"],
            sources=["source.bok.ecos"],
            terms=["term.finance.benchmark-rate"],
            tags=["finance-reference-ontology", "benchmark-rate", "bok"],
        ),
        node(
            "finance.benchmark-rate.cofix",
            "COFIX",
            "benchmark-rate",
            "은행 자금조달비용을 기초로 산출되어 주택담보대출 등 변동금리 대출의 기준으로 쓰이는 지표입니다.",
            parents=["category.finance.benchmark-rates"],
            sources=["source.fsc.cofix-overview"],
            terms=["term.finance.benchmark-rate"],
            tags=["finance-reference-ontology", "benchmark-rate", "loan-rate"],
        ),
        node(
            "finance.metric.loan-deposit-spread",
            "예대금리차",
            "risk-signal",
            "은행의 대출금리와 저축성 수신금리 차이를 매월 비교해 은행권 금리 운용을 점검하는 지표입니다.",
            parents=["category.finance.bank-rate-disclosure"],
            sources=["source.fsc.rate-disclosure-guide", "source.kfb.consumer-portal"],
            terms=["term.finance.loan-deposit-spread", "term.finance.provider-risk"],
            tags=["finance-reference-ontology", "bank-rate-disclosure", "loan-deposit-spread"],
        ),
        node(
            "finance.benchmark-rate.krw-exchange-rate",
            "원화 환율 지표",
            "benchmark-rate",
            "외화예금, 해외카드, 해외투자상품 비교에서 필요한 원화 기준 환율 지표입니다.",
            parents=["category.finance.benchmark-rates"],
            sources=["source.bok.ecos"],
            terms=["term.finance.benchmark-rate"],
            tags=["finance-reference-ontology", "benchmark-rate", "fx"],
        ),
        node(
            "finance.risk-signal.insurance-nonpayment-rate",
            "보험금 부지급률",
            "risk-signal",
            "보험회사별 보험금 부지급률과 청구 이후 해지비율을 상품 상세의 제공자 리스크로 연결하기 위한 신호입니다.",
            parents=["category.finance.insurance-risk-signals"],
            sources=["source.knia.claim-nonpayment"],
            terms=["term.finance.provider-risk"],
            tags=["finance-reference-ontology", "insurance-risk"],
        ),
        node(
            "finance.risk-signal.insurance-mis-selling-rate",
            "보험 불완전판매비율",
            "risk-signal",
            "채널별·상품별 불완전판매비율을 보험상품 추천 전 확인하는 판매품질 신호입니다.",
            parents=["category.finance.insurance-risk-signals"],
            sources=["source.knia.mis-selling"],
            terms=["term.finance.provider-risk"],
            tags=["finance-reference-ontology", "insurance-risk"],
        ),
        node(
            "finance.metric.fund-return-risk",
            "펀드 수익률·위험등급",
            "risk-signal",
            "공모펀드와 ETF를 수익률, 위험도, 투자지역, 설정액, 총보수, 투자설명서 기준으로 비교하기 위한 투자상품 지표입니다.",
            parents=["category.finance.investment-products"],
            sources=["source.kofia.fund-oneclick", "source.fsc.funddamoa-guide", "source.fsc.fund-products-basic"],
            terms=["term.finance.fund-risk-grade", "term.finance.total-expense-ratio"],
            tags=["finance-reference-ontology", "fund", "investment-risk"],
        ),
        node(
            "finance.metric.pension-savings-return-fee",
            "연금저축 수익률·수수료",
            "risk-signal",
            "연금저축 신탁·펀드·ETF·보험을 상품 유형별 수익률 기준, 수수료율, 위험등급, 판매사별 적립금으로 비교하기 위한 지표입니다.",
            parents=["category.finance.pension-products"],
            sources=["source.fss.integrated-pension-portal", "source.fsc.retirement-pension-basic"],
            terms=["term.finance.pension-savings-return-fee", "term.finance.sales-channel-balance"],
            tags=["finance-reference-ontology", "pension", "fee", "return"],
        ),
    ]
    items.extend(provider_registry_nodes(products))
    items.extend(deposit_protection_generated)
    return attach_source_metadata([*items, *(SOURCES[source_id] for source_id in REFERENCE_SOURCE_IDS), SOURCES["source.knia.insurance-disclosure"], SOURCES["source.fsc.variable-insurance-info"], SOURCES["source.kdic.insured-products"]])


def card_items() -> list[dict]:
    generated = load_generated("card")
    items = [
        node(
            "finance.card-products-ontology",
            "카드상품 온톨로지",
            "domain",
            "신용카드·체크카드·카드대출·결제성 리볼빙의 전월실적, 혜택조건, 연회비, 금리·수수료율, 판매상태를 구조화하는 금융상품 온톨로지입니다. 카드다모아 대표상품과 발급사 공식 전체 목록을 함께 보존합니다.",
            children=[
                "category.finance.credit-cards",
                "category.finance.check-cards",
                "category.finance.card-lending-products",
                "category.finance.card-revolving-services",
            ],
            sources=[
                *CARD_SOURCE_IDS,
                "source.crefia.card-lending-products",
                "source.crefia.card-loan-revolving-rates",
                "source.fsc.revolving-service-improvement",
                "source.easylaw.finance-product-disclosure",
            ],
            tags=["finance-ontology", "card-products-ontology"],
        ),
        node(
            "category.finance.credit-cards",
            "신용카드 상품",
            "category",
            "신용공여 기능이 있는 카드상품의 연회비, 전월실적, 할인·적립 혜택, 한도와 제외조건을 관리합니다.",
            parents=["finance.card-products-ontology"],
            sources=CARD_SOURCE_IDS,
            tags=["card-products-ontology", "credit-card"],
        ),
        node(
            "category.finance.check-cards",
            "체크카드 상품",
            "category",
            "결제계좌 잔액 범위에서 쓰는 체크카드 상품의 캐시백, 할인, 전월실적, 월 한도와 제외조건을 관리합니다.",
            parents=["finance.card-products-ontology"],
            sources=CARD_SOURCE_IDS,
            tags=["card-products-ontology", "check-card"],
        ),
        node(
            "category.finance.card-lending-products",
            "카드대출 상품",
            "category",
            "단기카드대출(현금서비스)과 장기카드대출(카드론)의 신용점수별 금리, 한도, 기간, 이용방법, 수수료율과 유의사항을 관리합니다. 상품 행은 카드대출 비교공시 수집기가 추가될 때 카드사별로 생성합니다.",
            parents=["finance.card-products-ontology"],
            sources=["source.crefia.card-lending-products", "source.crefia.card-loan-revolving-rates"],
            tags=["card-products-ontology", "card-loan", "candidate-import"],
        ),
        node(
            "category.finance.card-revolving-services",
            "결제성 리볼빙 서비스",
            "category",
            "일부결제금액이월약정의 최소결제비율, 이월잔액, 수수료율, 신용점수별 공시와 설명의무 확인 항목을 관리합니다.",
            parents=["finance.card-products-ontology"],
            sources=["source.crefia.card-loan-revolving-rates", "source.fsc.revolving-service-improvement"],
            tags=["card-products-ontology", "revolving", "candidate-import"],
        ),
        node(
            "term.card.previous-month-spend",
            "전월실적",
            "term",
            "카드 혜택 적용 여부를 판단할 때 카드사가 정한 직전 월 이용금액 기준입니다. 실적 제외 항목이 별도로 존재할 수 있습니다.",
            sources=CARD_SOURCE_IDS,
            tags=["card-products-ontology", "benefit-criterion"],
        ),
        node(
            "term.card.monthly-benefit-limit",
            "월 혜택 한도",
            "term",
            "할인, 캐시백, 포인트 적립 등 카드 혜택이 한 달에 적용되는 최대 금액 또는 횟수입니다.",
            sources=CARD_SOURCE_IDS,
            tags=["card-products-ontology", "benefit-limit"],
        ),
        node(
            "term.card.excluded-spend",
            "실적·혜택 제외 항목",
            "term",
            "세금, 공과금, 상품권, 아파트관리비, 보험료 등 카드사가 실적 또는 혜택 산정에서 제외할 수 있는 항목입니다.",
            sources=CARD_SOURCE_IDS,
            tags=["card-products-ontology", "exclusion"],
        ),
        node(
            "term.card.short-term-card-loan",
            "단기카드대출(현금서비스)",
            "term",
            "신용카드 한도 내에서 서류 없이 1~2개월 정도 이용하는 단기 금융서비스입니다. 편의성이 높지만 일반대출보다 수수료율이 높을 수 있습니다.",
            sources=["source.crefia.card-lending-products"],
            tags=["card-products-ontology", "card-loan", "cash-advance"],
        ),
        node(
            "term.card.long-term-card-loan",
            "장기카드대출(카드론)",
            "term",
            "카드 회원의 신용도와 카드이용실적에 따라 카드사가 신용카드 한도와 별도로 산정하는 2개월 이상 대출상품입니다.",
            sources=["source.crefia.card-lending-products", "source.crefia.card-loan-revolving-rates"],
            tags=["card-products-ontology", "card-loan", "loan-rate"],
        ),
        node(
            "term.card.revolving-minimum-payment",
            "리볼빙 최소결제비율",
            "term",
            "신용카드대금 중 일정 금액 이상만 결제하면 잔여대금 상환이 이월되는 일부결제금액이월약정의 최소 결제 기준입니다.",
            sources=["source.crefia.card-loan-revolving-rates", "source.fsc.revolving-service-improvement"],
            tags=["card-products-ontology", "revolving", "fee"],
        ),
        node(
            "term.card.card-loan-credit-score-rate",
            "카드대출 신용점수별 금리",
            "term",
            "현금서비스, 카드론, 결제성 리볼빙의 공시년월별·신용점수 구간별 평균 금리 또는 수수료율입니다.",
            sources=["source.crefia.card-loan-revolving-rates"],
            tags=["card-products-ontology", "loan-rate", "credit-score"],
        ),
    ]
    items.extend(generated)
    return attach_source_metadata([
        *items,
        *(SOURCES[source_id] for source_id in CARD_SOURCE_IDS),
        SOURCES["source.crefia.card-lending-products"],
        SOURCES["source.crefia.card-loan-revolving-rates"],
        SOURCES["source.fsc.revolving-service-improvement"],
        SOURCES["source.easylaw.finance-product-disclosure"],
    ])


def bank_items() -> list[dict]:
    generated = load_generated("deposit") + load_generated("saving") + load_generated("loan")
    policy_generated = load_generated("policy_loan")
    items = [
        node(
            "finance.bank-products-ontology",
            "예금·대출·여신금융상품 온톨로지",
            "domain",
            "정기예금, 적금, 주택담보대출, 전세자금대출, 개인신용대출, 개인사업자대출, 정책대출, 여신전문금융회사 신용대출·리스·할부의 금리, 우대조건, 가입한도, 수수료, 판매상태를 구조화하는 금융상품 온톨로지입니다.",
            children=[
                "category.finance.deposit-products",
                "category.finance.savings-products",
                "category.finance.mortgage-loan-products",
                "category.finance.rent-loan-products",
                "category.finance.credit-loan-products",
                "category.finance.business-loan-products",
                "category.finance.policy-loan-products",
                "category.finance.policy-loan-service-network",
                "category.finance.source-risk-controls",
                "category.finance.specialized-credit-loan-products",
                "category.finance.installment-finance-products",
                "category.finance.lease-finance-products",
            ],
            sources=[
                "source.fss.finlife.api",
                "source.fss.finlife.web",
                "source.fsc.rate-disclosure-guide",
                "source.kfb.consumer-portal",
                "source.fsb.savings-bank-deposit-rates",
                "source.fsc.business-loan-comparison",
                "source.data.go.kr.kinfa-loan-products",
                "source.fsc.inclusive-finance-products",
                "source.data.go.kr.kinfa-loan-handling-agencies",
                "source.data.go.kr.kinfa-support-centers",
                "source.kinfa.hessal-loan-youth",
                "source.kinfa.illegal-private-finance-prevention-loan",
                "source.myhome.support-lease-loan",
                "source.hf.bogeumjari-loan",
                "source.crefia.credit-loan-products",
                "source.crefia.credit-loan-rate-disclosure",
                "source.crefia.lease-installment-products",
                "source.crefia.auto-lease-disclosure",
                "source.easylaw.finance-product-disclosure",
            ],
            terms=["term.finance.source-approval-risk"],
            tags=["finance-ontology", "bank-products-ontology", "source-risk-tracked"],
        ),
        node(
            "category.finance.deposit-products",
            "정기예금 상품",
            "category",
            "예치기간별 기본금리, 최고우대금리, 가입한도와 가입대상 조건을 관리합니다.",
            parents=["finance.bank-products-ontology"],
            sources=["source.fss.finlife.api", "source.fsb.savings-bank-deposit-rates", "source.kfb.consumer-portal"],
            tags=["bank-products-ontology", "deposit"],
        ),
        node(
            "category.finance.savings-products",
            "적금 상품",
            "category",
            "정액적립·자유적립 방식, 기간별 기본금리, 최고우대금리, 납입한도와 우대조건을 관리합니다.",
            parents=["finance.bank-products-ontology"],
            sources=["source.fss.finlife.api", "source.fsb.savings-bank-deposit-rates", "source.kfb.consumer-portal"],
            tags=["bank-products-ontology", "saving"],
        ),
        node(
            "category.finance.mortgage-loan-products",
            "주택담보대출 상품",
            "category",
            "금리유형, 상환방식, 최저·최고금리, 중도상환수수료, 대출한도 조건을 관리합니다.",
            parents=["finance.bank-products-ontology"],
            sources=["source.fss.finlife.api", "source.kfb.consumer-portal"],
            tags=["bank-products-ontology", "mortgage-loan"],
        ),
        node(
            "category.finance.rent-loan-products",
            "전세자금대출 상품",
            "category",
            "전세자금 대출의 금리, 보증·담보 조건, 대출한도, 상환방식과 신청대상을 관리합니다.",
            parents=["finance.bank-products-ontology"],
            sources=["source.fss.finlife.api", "source.kfb.consumer-portal"],
            tags=["bank-products-ontology", "rent-loan"],
        ),
        node(
            "category.finance.credit-loan-products",
            "개인신용대출 상품",
            "category",
            "개인신용대출의 신용점수 구간별 금리, 평균금리, 대출한도, 상환방식을 관리합니다.",
            parents=["finance.bank-products-ontology"],
            sources=["source.fss.finlife.api", "source.kfb.consumer-portal"],
            tags=["bank-products-ontology", "credit-loan"],
        ),
        node(
            "category.finance.business-loan-products",
            "개인사업자 대출상품",
            "category",
            "개인사업자의 자금용도, 가입대상, 대출종류, 상품구분, 필요금액별 비교공시와 상세정보를 관리합니다. 상품 행은 FinLife 개인사업자대출 API 접근이 가능해질 때 추가합니다.",
            parents=["finance.bank-products-ontology"],
            sources=["source.fsc.business-loan-comparison", "source.fss.finlife.web"],
            tags=["bank-products-ontology", "business-loan", "pending-product-import"],
        ),
        node(
            "category.finance.policy-loan-products",
            "서민금융·정책대출 상품",
            "category",
            "서민금융진흥원과 정책금융기관의 대출한도, 금리구분, 대출용도, 총 대출기간, 취급기관 정보를 관리합니다. DATA_GO_KR_SERVICE_KEY가 있으면 대출상품한눈에 API 상품 행을 생성합니다.",
            parents=["finance.bank-products-ontology"],
            sources=[
                "source.data.go.kr.kinfa-loan-products",
                "source.kinfa.hessal-loan-youth",
                "source.kinfa.illegal-private-finance-prevention-loan",
                "source.myhome.support-lease-loan",
                "source.hf.bogeumjari-loan",
                "source.fss.finlife.web",
            ],
            tags=["bank-products-ontology", "policy-loan", "api-import-ready"],
        ),
        node(
            "category.finance.policy-loan-service-network",
            "정책대출 취급기관·상담센터",
            "category",
            "정책대출 상품 자체가 아니라 취급기관, 주소, 상담센터, 미소금융 지점 정보를 보강하는 후보입니다. 활용신청 완료 후에도 현재 키는 관련 공공데이터 API에서 403이므로 권한 전파가 확인될 때까지 상품 상세에 섞지 않습니다.",
            parents=["finance.bank-products-ontology", "category.finance.policy-loan-products"],
            sources=["source.data.go.kr.kinfa-loan-handling-agencies", "source.data.go.kr.kinfa-support-centers"],
            terms=["term.finance.source-approval-risk"],
            tags=["bank-products-ontology", "policy-loan", "service-network", "candidate-import", "live-403", "risk-control"],
        ),
        node(
            "category.finance.source-risk-controls",
            "금융 데이터 수집 리스크 통제",
            "category",
            "API 활용신청, 403 응답, 업데이트 주기, 상품 수 급감, 출처 수집일 누락을 추적하는 운영 노드입니다. 승인되지 않은 API는 상품 수에 섞지 않고 후보 출처와 manifest 리스크에 남깁니다.",
            parents=["finance.bank-products-ontology"],
            sources=[
                "source.fss.finlife.api",
                "source.data.go.kr.kinfa-loan-products",
                "source.fsc.inclusive-finance-products",
                "source.fsc.inclusive-finance-performance",
                "source.data.go.kr.kinfa-loan-handling-agencies",
                "source.data.go.kr.kinfa-support-centers",
                "source.kdic.insured-products",
            ],
            terms=["term.finance.source-approval-risk"],
            tags=["bank-products-ontology", "data-quality", "risk-control", "source-access"],
        ),
        node(
            "category.finance.specialized-credit-loan-products",
            "여신전문금융 신용대출 상품",
            "category",
            "카드사·캐피탈사 등 여신전문금융회사의 신용대출과 민간중금리대출의 신용점수별 평균금리, 적용금리대별 회원분포, 상품 운영현황을 관리합니다.",
            parents=["finance.bank-products-ontology"],
            sources=["source.crefia.credit-loan-products", "source.crefia.credit-loan-rate-disclosure"],
            tags=["bank-products-ontology", "specialized-credit-finance", "credit-loan", "candidate-import"],
        ),
        node(
            "category.finance.installment-finance-products",
            "할부금융 상품",
            "category",
            "자동차·주택·가전·기계류·기타 할부금융의 적용금리, 취급회사, 신용정보회사, 중도상환수수료와 비교공시 조건을 관리합니다.",
            parents=["finance.bank-products-ontology"],
            sources=["source.crefia.lease-installment-products"],
            tags=["bank-products-ontology", "installment-finance", "candidate-import"],
        ),
        node(
            "category.finance.lease-finance-products",
            "리스금융 상품",
            "category",
            "자동차리스 등 리스금융 상품의 월리스료, 보증금·잔존가치, 실제 운영율, 중도해지수수료와 상세 안내 확인 항목을 관리합니다.",
            parents=["finance.bank-products-ontology"],
            sources=["source.crefia.lease-installment-products", "source.crefia.auto-lease-disclosure"],
            tags=["bank-products-ontology", "lease-finance", "candidate-import"],
        ),
        node(
            "term.bank.base-interest-rate",
            "기본금리",
            "term",
            "우대조건을 적용하기 전 금융상품에 표시되는 기본 이자율입니다.",
            sources=["source.fss.finlife.api"],
            tags=["bank-products-ontology", "rate"],
        ),
        node(
            "term.bank.preferential-interest-rate",
            "우대금리",
            "term",
            "급여이체, 자동이체, 카드실적, 마케팅 동의 등 조건 충족 시 더해질 수 있는 이자율입니다.",
            sources=["source.fss.finlife.api"],
            tags=["bank-products-ontology", "rate"],
        ),
        node(
            "term.bank.early-repayment-fee",
            "중도상환수수료",
            "term",
            "대출 만기 전 원금을 상환할 때 적용될 수 있는 수수료율 또는 산식입니다.",
            sources=["source.fss.finlife.api", "source.easylaw.finance-product-disclosure"],
            tags=["bank-products-ontology", "fee"],
        ),
        node(
            "term.bank.credit-score-band",
            "신용점수 구간",
            "term",
            "개인신용대출과 개인사업자대출의 평균금리, 기준금리, 가산금리 등을 비교할 때 쓰는 신용점수 등급별 구간입니다.",
            sources=[
                "source.fss.finlife.api",
                "source.fsc.business-loan-comparison",
                "source.crefia.credit-loan-rate-disclosure",
            ],
            tags=["bank-products-ontology", "loan-rate", "credit-score"],
        ),
        node(
            "term.bank.loan-purpose",
            "대출 자금용도",
            "term",
            "창업, 운영, 대환 등 대출 신청 목적을 구분하는 검색·비교 기준입니다.",
            sources=["source.fsc.business-loan-comparison", "source.data.go.kr.kinfa-loan-products"],
            tags=["bank-products-ontology", "business-loan", "policy-loan"],
        ),
        node(
            "term.bank.repayment-method",
            "대출 상환방식",
            "term",
            "분할상환, 만기일시상환 등 대출 원리금 상환 구조를 비교하는 기준입니다.",
            sources=["source.fss.finlife.api", "source.fsc.business-loan-comparison"],
            tags=["bank-products-ontology", "loan-detail"],
        ),
        node(
            "term.finance.medium-interest-credit-loan",
            "민간중금리대출",
            "term",
            "여신전문금융회사가 취급하는 중금리대 신용대출 중 감독규정상 외부 개인신용평점과 금리상한 요건을 충족하는 신용대출입니다.",
            sources=["source.crefia.credit-loan-products"],
            tags=["bank-products-ontology", "credit-loan", "medium-interest-loan"],
        ),
        node(
            "term.finance.installment-finance",
            "할부금융",
            "term",
            "상품 구입대금을 할부기간에 걸쳐 분할 상환하는 여신전문금융 상품군입니다. 자동차, 주택, 가전, 기계류, 기타 할부 공시로 세분합니다.",
            sources=["source.crefia.lease-installment-products"],
            tags=["bank-products-ontology", "installment-finance"],
        ),
        node(
            "term.finance.operating-lease",
            "운용리스",
            "term",
            "리스회사가 이용자에게 물건을 일정 기간 이용하게 하고 리스기간 종료 시 반환하도록 하는 리스금융 거래입니다.",
            sources=["source.crefia.lease-installment-products", "source.crefia.auto-lease-disclosure"],
            tags=["bank-products-ontology", "lease-finance"],
        ),
        node(
            "term.finance.early-termination-fee",
            "중도해지수수료",
            "term",
            "리스·할부금융 계약을 약정 기간 전에 종료하거나 상환할 때 적용될 수 있는 수수료율 또는 산식입니다.",
            sources=["source.crefia.auto-lease-disclosure", "source.easylaw.finance-product-disclosure"],
            tags=["bank-products-ontology", "fee", "lease-finance", "installment-finance"],
        ),
        node(
            "term.finance.source-approval-risk",
            "공공데이터 API 승인 리스크",
            "term",
            "공공데이터포털 API가 자동승인으로 표시되더라도 서비스별 활용신청이 없으면 403 또는 인증 오류가 날 수 있어, 승인 전에는 후보 출처로만 보존하는 운영 리스크입니다.",
            sources=[
                "source.data.go.kr.kinfa-loan-products",
                "source.fsc.inclusive-finance-products",
                "source.data.go.kr.kinfa-loan-handling-agencies",
                "source.data.go.kr.kinfa-support-centers",
                "source.kdic.insured-products",
            ],
            tags=["bank-products-ontology", "data-quality", "source-access", "risk-control"],
        ),
        node(
            "finance.bank.policy-loan.kinfa.hessal-loan-youth",
            "서민금융진흥원 햇살론유스",
            "bank-product",
            "서민금융진흥원이 공시한 청년·대학생 대상 정책서민금융 보증부 대출 상품입니다.",
            parents=["category.finance.policy-loan-products"],
            sources=["source.kinfa.hessal-loan-youth"],
            terms=["term.bank.loan-purpose", "term.bank.repayment-method"],
            tags=["finance-product", "manual-source-check", "policy-loan", "youth-loan"],
            provider="서민금융진흥원",
            provider_code="KINF",
            financial_sector="정책금융",
            product_kind="policy-loan",
            product_status="active",
            sales_status="active",
            product_code="KINF-HESSAL-YOUTH",
            collected_at=CURRENT_REVIEW_DATE,
            source_record_id="kinfa:hessalLoanYoos",
            source_basis_dates=[f"{CURRENT_REVIEW_DATE} 수동 확인"],
            options=[
                {
                    "eligibility": "19세~34세이면서 연소득 3,500만원 이하 청년, 취업준비생, 사회초년생, 청년사업자 등",
                    "loan_limit": "동일인 1인 최대 1,200만원",
                    "purpose": "일반생활자금, 특정용도자금(학업·취업준비비, 사업운용비, 의료비, 주거비·임차료)",
                    "rate": "취업준비생·사회초년생·청년사업자 적용금리 5.0%, 국민취업제도 성공자 4.5%, 사회적배려 대상자 2.0%",
                    "repayment_method": "최장 거치기간 후 원금균등분할상환",
                    "maturity": "최장 보증기간은 대상별 10~15년",
                }
            ],
        ),
        node(
            "finance.bank.policy-loan.kinfa.illegal-private-finance-prevention",
            "서민금융진흥원 불법사금융예방대출",
            "bank-product",
            "서민금융진흥원이 공시한 대부업 이용도 어려운 저신용·저소득자 생계비 정책서민금융 상품입니다.",
            parents=["category.finance.policy-loan-products"],
            sources=["source.kinfa.illegal-private-finance-prevention-loan"],
            terms=["term.bank.credit-score-band", "term.bank.loan-purpose", "term.bank.repayment-method"],
            tags=["finance-product", "manual-source-check", "policy-loan", "emergency-living-loan"],
            provider="서민금융진흥원",
            provider_code="KINF",
            financial_sector="정책금융",
            product_kind="policy-loan",
            product_status="active",
            sales_status="active",
            product_code="KINF-IPFL",
            collected_at=CURRENT_REVIEW_DATE,
            source_record_id="kinfa:smallLivingLoan",
            source_basis_dates=[f"{CURRENT_REVIEW_DATE} 수동 확인"],
            options=[
                {
                    "eligibility": "신용평점 하위 20%이면서 연소득 3,500만원 이하",
                    "loan_limit": "1인당 최대 100만원",
                    "purpose": "생계비, 의료·주거·교육비 등 특정용도 증빙 가능",
                    "rate": "일반 연 12.5%, 사회적배려대상자 연 9.9%, 완제 후 재대출 연 4.5%",
                    "repayment_method": "2년 원리금균등분할상환",
                    "fee": "중도상환수수료 면제",
                }
            ],
        ),
        node(
            "finance.bank.rent-loan.myhome.support-lease-loan",
            "주택도시기금 버팀목전세대출",
            "bank-product",
            "마이홈포털이 공시한 근로자·서민 주거안정 전세자금 정책대출 상품입니다.",
            parents=["category.finance.rent-loan-products", "category.finance.policy-loan-products"],
            sources=["source.myhome.support-lease-loan"],
            terms=["term.bank.loan-purpose", "term.bank.repayment-method"],
            tags=["finance-product", "manual-source-check", "rent-loan", "policy-loan", "housing-loan"],
            provider="주택도시기금",
            provider_code="NHUF",
            financial_sector="정책금융",
            product_kind="rent-loan",
            product_status="active",
            sales_status="active",
            product_code="MYHOME-BUTTIMOK-LEASE",
            collected_at=CURRENT_REVIEW_DATE,
            source_record_id="myhome:selectSupLeaseLoanView",
            source_basis_dates=[f"{CURRENT_REVIEW_DATE} 수동 확인"],
            options=[
                {
                    "eligibility": "성년 세대주, 무주택자, 부부합산 연소득 5천만원 이하, 순자산가액 3.45억원 이하 등",
                    "loan_limit": "최고 8천만원 이내, 수도권은 1.2억원 이내",
                    "purpose": "전월세 보증금 대출",
                    "rate": "연 2.5%~3.5%",
                    "repayment_method": "기금 전세자금대출 약정에 따른 상환",
                    "maturity": "2년, 최장 10년 이용 가능",
                }
            ],
        ),
        node(
            "finance.bank.mortgage-loan.hf.bogeumjari-loan",
            "한국주택금융공사 보금자리론",
            "bank-product",
            "한국주택금융공사가 공시한 장기 고정금리 주택담보 정책대출 상품입니다.",
            parents=["category.finance.mortgage-loan-products", "category.finance.policy-loan-products"],
            sources=["source.hf.bogeumjari-loan"],
            terms=["term.bank.loan-purpose", "term.bank.repayment-method"],
            tags=["finance-product", "manual-source-check", "mortgage-loan", "policy-loan", "housing-loan"],
            provider="한국주택금융공사",
            provider_code="HF",
            financial_sector="정책금융",
            product_kind="mortgage-loan",
            product_status="active",
            sales_status="active",
            product_code="HF-BOGEUMJARI",
            collected_at=CURRENT_REVIEW_DATE,
            source_record_id="hf:bogeumjariLoan",
            source_basis_dates=[f"{CURRENT_REVIEW_DATE} 수동 확인"],
            options=[
                {
                    "eligibility": "민법상 성년 대한민국 국민, 한국신용정보원 신용정보관리규약 해당사항 없음, CB점수 271점 이상",
                    "loan_limit": "최대 3.6억원, 다자녀·전세사기피해자 4억원, 생애최초 4.2억원",
                    "purpose": "구입, 보전, 상환 용도",
                    "rate": "대출 받은 날부터 만기까지 고정금리 적용",
                    "repayment_method": "원리금 균등, 원금 균등, 체증식 분할상환",
                    "maturity": "10, 15, 20, 30, 40, 50년",
                    "ltv_dti": "LTV 최대 70%, DTI 최대 60%; 생애최초 보금자리론은 최대 LTV 80%(4.2억원 한도)",
                }
            ],
        ),
    ]
    items.extend(generated)
    items.extend(policy_generated)
    return attach_source_metadata([
        *items,
        SOURCES["source.fss.finlife.api"],
        SOURCES["source.fss.finlife.web"],
        SOURCES["source.fsc.rate-disclosure-guide"],
        SOURCES["source.kfb.consumer-portal"],
        SOURCES["source.fsb.savings-bank-deposit-rates"],
        SOURCES["source.fsc.business-loan-comparison"],
        SOURCES["source.data.go.kr.kinfa-loan-products"],
        SOURCES["source.fsc.inclusive-finance-products"],
        SOURCES["source.fsc.inclusive-finance-performance"],
        SOURCES["source.data.go.kr.kinfa-loan-handling-agencies"],
        SOURCES["source.data.go.kr.kinfa-support-centers"],
        SOURCES["source.kinfa.hessal-loan-youth"],
        SOURCES["source.kinfa.illegal-private-finance-prevention-loan"],
        SOURCES["source.myhome.support-lease-loan"],
        SOURCES["source.hf.bogeumjari-loan"],
        SOURCES["source.crefia.credit-loan-products"],
        SOURCES["source.crefia.credit-loan-rate-disclosure"],
        SOURCES["source.crefia.lease-installment-products"],
        SOURCES["source.crefia.auto-lease-disclosure"],
        SOURCES["source.easylaw.finance-product-disclosure"],
    ])


# 은행 노드 정의는 bank_items() 하나로 유지하고, export는 예금/적금/대출 3개 팩으로
# 나눈다. 공유 참조 노드(도메인·카테고리·용어·출처)는 각 팩에 포함되며 검색 인덱스가
# id 기준으로 중복 제거한다. bank_items()를 팩마다 새로 호출해 dict 공유 변이를 피한다.
BANK_PACK_KINDS = {
    "deposit": {"deposit"},
    "saving": {"saving"},
    "loan": {"mortgage-loan", "rent-loan", "credit-loan", "policy-loan", "business-loan"},
}


def bank_pack_items(pack: str) -> list[dict]:
    kinds = BANK_PACK_KINDS[pack]
    return [
        item
        for item in bank_items()
        if item.get("type") != "bank-product" or item.get("product_kind") in kinds
    ]


def insurance_items() -> list[dict]:
    generated = load_generated("insurance")
    items = [
        node(
            "finance.insurance-products-ontology",
            "보험상품 온톨로지",
            "domain",
            "자동차보험, 실손의료보험, 여행자보험, 연금·보장성 보험의 보험료, 보장, 면책, 갱신, 판매상태를 구조화하는 금융상품 온톨로지입니다.",
            children=[
                "category.finance.auto-insurance-products",
                "category.finance.indemnity-health-insurance-products",
                "category.finance.travel-insurance-products",
                "category.finance.annuity-insurance-products",
                "category.finance.protection-insurance-products",
            ],
            sources=[
                "source.einsmarket.insurance",
                "source.klia.insurance-disclosure",
                "source.knia.insurance-disclosure",
                "source.fss.integrated-pension-portal",
                "source.easylaw.finance-product-disclosure",
            ],
            tags=["finance-ontology", "insurance-products-ontology"],
        ),
        node(
            "category.finance.auto-insurance-products",
            "자동차보험 상품",
            "category",
            "차량·운전자 조건별 보험료, 담보, 할인·할증 조건, 가입 가능 여부를 관리합니다.",
            parents=["finance.insurance-products-ontology"],
            sources=["source.einsmarket.insurance", "source.knia.insurance-disclosure"],
            tags=["insurance-products-ontology", "auto-insurance"],
        ),
        node(
            "category.finance.indemnity-health-insurance-products",
            "실손의료보험 상품",
            "category",
            "급여·비급여 보장, 자기부담금, 면책, 갱신주기, 보험료 조건을 관리합니다.",
            parents=["finance.insurance-products-ontology"],
            sources=["source.einsmarket.insurance", "source.klia.insurance-disclosure", "source.knia.insurance-disclosure"],
            tags=["insurance-products-ontology", "indemnity-health"],
        ),
        node(
            "category.finance.travel-insurance-products",
            "여행자보험 상품",
            "category",
            "국내·해외 여행 보장, 의료비, 휴대품 손해, 배상책임, 가입기간별 보험료를 관리합니다.",
            parents=["finance.insurance-products-ontology"],
            sources=["source.einsmarket.insurance", "source.knia.insurance-disclosure"],
            tags=["insurance-products-ontology", "travel-insurance"],
        ),
        node(
            "category.finance.annuity-insurance-products",
            "연금보험 상품",
            "category",
            "연금 개시연령, 납입기간, 공시이율, 수수료, 세제 관련 확인 항목을 관리합니다.",
            parents=["finance.insurance-products-ontology"],
            sources=["source.einsmarket.insurance", "source.klia.insurance-disclosure", "source.fss.integrated-pension-portal"],
            tags=["insurance-products-ontology", "annuity-insurance"],
        ),
        node(
            "category.finance.protection-insurance-products",
            "보장성 보험 상품",
            "category",
            "질병, 암, 상해, 사망 등 보장성 보험의 담보, 보험료, 면책·감액기간, 갱신 여부를 관리합니다.",
            parents=["finance.insurance-products-ontology"],
            sources=["source.einsmarket.insurance", "source.klia.insurance-disclosure", "source.knia.insurance-disclosure"],
            tags=["insurance-products-ontology", "protection-insurance"],
        ),
        node(
            "term.insurance.coverage",
            "보장 항목",
            "term",
            "보험계약이 사고·질병·손해 발생 시 지급 대상으로 삼는 담보 또는 급부 항목입니다.",
            sources=["source.einsmarket.insurance", "source.klia.insurance-disclosure", "source.knia.insurance-disclosure"],
            tags=["insurance-products-ontology", "coverage"],
        ),
        node(
            "term.insurance.exclusion",
            "면책 사항",
            "term",
            "보험사가 보험금을 지급하지 않는 사유 또는 기간입니다. 약관 URL과 함께 확인해야 합니다.",
            sources=["source.einsmarket.insurance", "source.klia.insurance-disclosure", "source.knia.insurance-disclosure"],
            tags=["insurance-products-ontology", "exclusion"],
        ),
        node(
            "term.insurance.renewal",
            "갱신 조건",
            "term",
            "보험기간 종료 후 보험료와 보장이 재산정되는지, 갱신주기와 갱신 가능 연령이 무엇인지 설명하는 조건입니다.",
            sources=["source.einsmarket.insurance", "source.klia.insurance-disclosure", "source.knia.insurance-disclosure"],
            tags=["insurance-products-ontology", "renewal"],
        ),
    ]
    items.extend(generated)
    return attach_source_metadata([
        *items,
        SOURCES["source.fss.finlife.api"],
        SOURCES["source.fss.finlife.web"],
        SOURCES["source.einsmarket.insurance"],
        SOURCES["source.klia.insurance-disclosure"],
        SOURCES["source.fsc.medical-reimbursement-insurance"],
        SOURCES["source.fsc.variable-insurance-info"],
        SOURCES["source.fss.integrated-pension-portal"],
        SOURCES["source.knia.insurance-disclosure"],
        SOURCES["source.easylaw.finance-product-disclosure"],
    ])


def disclosure_months(item: dict) -> list[str]:
    months: list[str] = []
    disclosure_month = item.get("disclosure_month")
    if disclosure_month:
        months.append(str(disclosure_month))
    for option in item.get("options") or []:
        if isinstance(option, dict) and option.get("dcls_month"):
            months.append(str(option["dcls_month"]))
    return sorted({month for month in months if month})


def has_product_conditions(item: dict) -> bool:
    return bool(item.get("criteria") or item.get("options") or item.get("benefits"))


def active_status_reason(item: dict) -> str:
    source_dates = ", ".join(str(value) for value in item.get("source_basis_dates") or [])
    if source_dates:
        return f"공식 출처 수집 기준으로 판매·공시 상태를 확인했습니다: {source_dates}"
    return "공식 출처 수집 기준으로 판매·공시 상태를 확인했습니다."


def enrich_operational_status(items: list[dict]) -> list[dict]:
    for item in items:
        item_type = item.get("type")
        if item_type not in {"card-product", "bank-product", "insurance-product"}:
            continue

        raw_status = str(item.get("product_status") or item.get("sales_status") or item.get("status") or "unknown")
        status = raw_status if raw_status in {"active", "ended", "suspended", "unknown"} else "unknown"
        status_reason = item.get("status_reason") or active_status_reason(item)
        status_confidence = item.get("status_confidence") or "confirmed"
        flags = list(item.get("quality_flags") or [])
        missing_fields = list(item.get("missing_required_fields") or [])
        months = disclosure_months(item)

        if status == "active" and not has_product_conditions(item):
            status = "unknown"
            status_reason = "상품 비교·추천에 필요한 criteria/options/benefits가 비어 있어 현재 판매 중으로 단정하지 않습니다."
            status_confidence = "insufficient"
            flags.append("missing_product_conditions")
            missing_fields.append("criteria_or_options")

        if item_type == "insurance-product":
            if status == "active" and not item.get("criteria"):
                status = "unknown"
                status_reason = "보험상품은 보장·보험료·면책·갱신 등 판단 기준이 비어 있어 active로 노출하지 않습니다."
                status_confidence = "insufficient"
                flags.append("missing_insurance_criteria")
                missing_fields.append("criteria")
            latest_month = max(months) if months else ""
            if status == "active" and latest_month and latest_month < DISCLOSURE_STALE_BEFORE:
                status = "unknown"
                status_reason = f"최신 공시월이 {latest_month}로 오래되어 현재 판매 중으로 단정하지 않습니다."
                status_confidence = "stale"
                flags.append("stale_disclosure_month")

        if status == "ended" or item.get("effective_to"):
            item["product_status"] = "ended"
            item["sales_status"] = "ended"
            item["status"] = "closed"
            item["status_reason"] = item.get("status_reason") or "공식 출처에 종료일 또는 판매중단일자가 있어 기본 검색·추천 대상에서 제외합니다."
            item["status_confidence"] = item.get("status_confidence") or "confirmed"
            item["recommendation_status"] = "reference_only"
        elif status == "active":
            item["product_status"] = "active"
            item["sales_status"] = "active"
            item["status"] = "active"
            item["status_reason"] = status_reason
            item["status_confidence"] = status_confidence
            item["recommendation_status"] = "eligible_for_listing"
        else:
            item["product_status"] = status
            item["sales_status"] = status
            item["status"] = status
            item["status_reason"] = status_reason
            item["status_confidence"] = status_confidence
            item["recommendation_status"] = "reference_only"

        item["effective_from"] = item.get("effective_from")
        item["effective_to"] = item.get("effective_to")
        item["application_open_from"] = item.get("application_open_from")
        item["application_open_to"] = item.get("application_open_to")
        item["last_verified_at"] = item.get("last_verified_at") or CURRENT_REVIEW_DATE
        item["source_modified_at"] = item.get("source_modified_at") or (max(months) if months else None)
        item["quality_flags"] = unique([str(flag) for flag in flags])
        item["missing_required_fields"] = unique([str(field) for field in missing_fields])
        item["related"] = unique([*(item.get("related") or []), *semantic_product_related(item)])
        search_type = bank_search_type(item)
        if search_type:
            item["search_type"] = search_type
            item["rate_search_eligible"] = search_type != "deposit-protection"
        enrich_card_benefits(item)
        enrich_insurance_coverage(item)
        apply_recommendation_scope(item)
        normalize_loan_product(item)
    return items


def export_quality_summary(items: list[dict], product_type: str) -> dict:
    products = [item for item in items if item.get("type") == product_type]
    status_counts: dict[str, int] = {}
    for product in products:
        status = str(product.get("status") or product.get("product_status") or "unknown")
        status_counts[status] = status_counts.get(status, 0) + 1
    stale_count = sum(1 for product in products if "stale_disclosure_month" in (product.get("quality_flags") or []))
    return {
        "product_count": len(products),
        "status_counts": dict(sorted(status_counts.items())),
        "active_products_without_criteria": sum(
            1 for product in products
            if product.get("status") == "active" and not product.get("criteria")
        ),
        "active_products_without_conditions": sum(
            1 for product in products
            if product.get("status") == "active" and not has_product_conditions(product)
        ),
        "products_without_related": sum(1 for product in products if not product.get("related")),
        "active_products_without_related": sum(
            1 for product in products
            if product.get("status") == "active" and not product.get("related")
        ),
        "card_benefits_with_incomplete_conditions": sum(
            1
            for product in products
            for benefit in product.get("benefits") or []
            if isinstance(benefit, dict) and benefit.get("condition_completeness") == "incomplete"
        ),
        "insurance_coverages_with_incomplete_conditions": sum(
            1
            for product in products
            for criterion in product.get("criteria") or []
            if isinstance(criterion, dict)
            and criterion.get("criteria_kind") == "coverage"
            and criterion.get("condition_completeness") == "incomplete"
        ),
        "deposit_protection_products": sum(1 for product in products if product.get("search_type") == "deposit-protection"),
        "active_loans_without_criteria": sum(
            1 for product in products
            if product.get("search_type") == "loan" and product.get("status") == "active" and not product.get("criteria")
        ),
        "loans_missing_required_fields": sum(
            1 for product in products
            if product.get("search_type") == "loan" and product.get("missing_loan_required_fields")
        ),
        "active_insurance_without_criteria": sum(
            1 for product in products
            if product.get("type") == "insurance-product" and product.get("status") == "active" and not product.get("criteria")
        ),
        "stale_disclosure_products": stale_count,
        "reference_only_products": sum(1 for product in products if product.get("recommendation_status") == "reference_only"),
        "recommendation_listing_only_products": sum(1 for product in products if product.get("recommendation_scope") == "listing_only"),
        "quality_gate": {
            "expired_active_local_supports": "validated in korea-local-government-supports export",
            "active_insurance_without_criteria_must_be_zero": True,
            "active_products_without_conditions_must_be_zero": True,
            "active_products_without_related_must_be_zero": True,
            "stale_active_disclosure_products_must_be_zero": True,
        },
    }


def payload_checksum(payload: dict) -> str:
    encoded = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def normalize_links(items: list[dict]) -> list[dict]:
    by_id = {item["id"]: item for item in items}
    for item in items:
        for child_id in item.get("children") or []:
            child = by_id.get(child_id)
            if child:
                child["parents"] = unique((child.get("parents") or []) + [item["id"]])
        for parent_id in item.get("parents") or []:
            parent = by_id.get(parent_id)
            if parent:
                parent["children"] = unique((parent.get("children") or []) + [item["id"]])
    return sorted(by_id.values(), key=lambda item: item["id"])


def write_export(path: Path, version: str, domain: str, items: list[dict], product_type: str, generated_domain: str) -> dict:
    normalized = normalize_links(enrich_operational_status(items))
    product_count = product_counts(normalized, product_type)
    product_collection_dates = sorted({
        item["collected_at"]
        for item in normalized
        if item.get("type") == product_type and item.get("collected_at")
    })
    quality_summary = export_quality_summary(normalized, product_type)
    payload = {
        "version": version,
        "basis_date": CURRENT_REVIEW_DATE,
        "source_review_date": CURRENT_REVIEW_DATE,
        "product_collection_dates": product_collection_dates,
        "domain": domain,
        "ontology_kind": f"{domain}-ontology",
        **generated_status(generated_domain, product_count),
        "quality_summary": quality_summary,
        "items": normalized,
    }
    payload["export_checksum"] = payload_checksum(payload)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8")
    return {
        "path": str(path.relative_to(REPO_ROOT)),
        "item_count": len(normalized),
        "product_count": product_count,
        "product_collection_dates": product_collection_dates,
        "quality_summary": quality_summary,
        "export_checksum": payload["export_checksum"],
    }


def export_entry(
    id_: str,
    domain: str,
    path: str,
    item_count: int,
    product_count: int,
    description: str,
    product_collection_dates: list[str] | None = None,
    quality_summary: dict | None = None,
    export_checksum: str | None = None,
) -> dict:
    return {
        "id": id_,
        "domain": domain,
        "path": path,
        "url": f"{RAW_BASE_URL}/{path}",
        "web_url": f"{WEB_BASE_URL}/{Path(path).name}",
        "item_count": item_count,
        "product_count": product_count,
        "source_review_date": CURRENT_REVIEW_DATE,
        "product_collection_dates": product_collection_dates or [],
        "quality_summary": quality_summary or {},
        "export_checksum": export_checksum,
        "description": description,
    }


SEARCH_NESTED_FIELDS = (
    "label",
    "condition",
    "text",
    "benefit",
    "coverage_name",
    "rate_type",
    "save_trm",
    "intr_rate",
    "intr_rate2",
    "rsrv_type_nm",
    "rpay_type_nm",
    "crdt_prdt_type_nm",
)


def compact_nested_text(values: object) -> str:
    if not isinstance(values, list):
        return ""
    parts: list[str] = []
    for entry in values[:6]:
        if not isinstance(entry, dict):
            continue
        for key in SEARCH_NESTED_FIELDS:
            value = entry.get(key)
            if value is not None and value != "" and value != []:
                parts.append(str(value)[:120])
    return " ".join(parts)


def item_search_text(item: dict) -> str:
    parts: list[str] = []
    for key in (
        "id",
        "title",
        "type",
        "description",
        "law_reference",
        "url",
        "publisher",
        "provider",
        "provider_code",
        "financial_sector",
        "product_code",
        "product_kind",
        "search_type",
        "product_status",
        "sales_status",
        "status",
        "status_reason",
        "recommendation_status",
        "application_status",
        "is_currently_applicable",
        "application_deadline_text",
        "application_open_from",
        "application_open_to",
        "jurisdiction",
    ):
        value = item.get(key)
        if value:
            parts.append(str(value))
    for key in ("tags", "sources", "source_urls"):
        parts.extend(str(value) for value in item.get(key) or [] if value)
    for key in ("criteria", "options", "benefits"):
        values = item.get(key) or []
        if values:
            parts.append(compact_nested_text(values))
    if item.get("search_type") in {"deposit", "saving", "loan"}:
        parts.append("금리 최고금리 개월 12개월 24개월 36개월 중도해지")
    return " ".join(parts).lower()


def search_index_item(item: dict, export_id: str) -> dict:
    aliases = list(TAX_SEARCH_ALIASES.get(str(item.get("id")), ()))
    search_text = " ".join([item_search_text(item), *aliases]).strip()
    return {
        "id": item.get("id"),
        "title": item.get("title"),
        "type": item.get("type"),
        "description": item.get("description"),
        "provider": item.get("provider"),
        "product_kind": item.get("product_kind"),
        "search_type": item.get("search_type"),
        "product_status": item.get("product_status"),
        "sales_status": item.get("sales_status"),
        "status": item.get("status"),
        "status_reason": item.get("status_reason"),
        "recommendation_status": item.get("recommendation_status"),
        "application_status": item.get("application_status"),
        "is_currently_applicable": item.get("is_currently_applicable"),
        "application_open_from": item.get("application_open_from"),
        "application_open_to": item.get("application_open_to"),
        "search_aliases": aliases,
        "export_id": export_id,
        "search_text": search_text,
    }


def query_tokens(query: str) -> list[str]:
    return [token for token in query.strip().lower().split() if token]


def score_search_index_item(item: dict, query: str) -> int:
    normalized_query = query.strip().lower()
    title = str(item.get("title") or "").strip().lower()
    item_id = str(item.get("id") or "").strip().lower()
    text = str(item.get("search_text") or "").lower()
    aliases = [str(alias).strip().lower() for alias in item.get("search_aliases") or []]
    tokens = query_tokens(normalized_query)
    title_tokens = query_tokens(title)
    item_type = str(item.get("type") or "")

    score = 0
    if normalized_query in aliases:
        score = 95
    elif item_id == normalized_query or title == normalized_query:
        score = 100
    elif normalized_query and item_id and normalized_query in item_id:
        score = 80
    elif title and title in normalized_query:
        base = 35 if item_type in GENERIC_SEARCH_TYPES and len(title_tokens) < len(tokens) else 75
        score = base + len(title_tokens)
    elif normalized_query and title and normalized_query in title:
        score = 70
    elif normalized_query and normalized_query in text:
        score = 40

    if len(tokens) > 1:
        matched = [token for token in tokens if token in text]
        if item_type in TAX_DECISION_TYPES and len(matched) >= min(2, len(tokens)):
            score = max(score, 60 + len(matched))
        if not score and len(matched) == len(tokens):
            score = 30 + len(matched)
        if not score and matched:
            score = 10 + len(matched)
    return score


def load_export_items(path: Path) -> list[dict]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    return [*(payload.get("reference_items") or []), *(payload.get("items") or [])]


def existing_export_quality_summary(path: Path) -> dict:
    if not path.exists():
        return {}
    payload = json.loads(path.read_text(encoding="utf-8"))
    return payload.get("quality_summary") or {}


def existing_export_checksum(path: Path) -> str | None:
    if not path.exists():
        return None
    payload = json.loads(path.read_text(encoding="utf-8"))
    return payload.get("export_checksum") or payload_checksum(payload)


def broken_relation_count(path_texts: list[str]) -> int:
    items: list[dict] = []
    known_ids: set[str] = set()
    for path_text in path_texts:
        path = REPO_ROOT / path_text
        if not path.exists():
            continue
        loaded = load_export_items(path)
        items.extend(loaded)
        known_ids.update(str(item["id"]) for item in loaded if isinstance(item, dict) and item.get("id"))

    broken = 0
    for item in items:
        if not isinstance(item, dict):
            continue
        for key in REFERENCE_KEYS:
            for target_id in item.get(key) or []:
                if target_id not in known_ids:
                    broken += 1
    return broken


def write_search_index(export_paths: list[tuple[str, str]]) -> dict:
    indexed: list[dict] = []
    seen: set[str] = set()
    for export_id, path_text in export_paths:
        path = REPO_ROOT / path_text
        if not path.exists():
            continue
        for item in load_export_items(path):
            item_id = item.get("id")
            if not item_id or item_id in seen:
                continue
            seen.add(item_id)
            indexed.append(search_index_item(item, export_id))
    payload = {
        "version": "KR-FINANCE-SEARCH-INDEX-2026.07.04.1",
        "basis_date": CURRENT_REVIEW_DATE,
        "source_review_date": CURRENT_REVIEW_DATE,
        "ontology_kind": "finance-search-index",
        "description": "MCP search가 대용량 원본 export를 모두 적재하지 않고 검색할 수 있도록 만든 경량 인덱스입니다.",
        "item_count": len(indexed),
        "items": sorted(indexed, key=lambda item: item["id"]),
    }
    payload["export_checksum"] = payload_checksum(payload)
    SEARCH_INDEX_EXPORT.write_text(json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8")
    return {
        "path": str(SEARCH_INDEX_EXPORT.relative_to(REPO_ROOT)),
        "item_count": len(indexed),
        "product_count": 0,
        "export_checksum": payload["export_checksum"],
    }


def write_search_regression_report() -> dict:
    index_payload = json.loads(SEARCH_INDEX_EXPORT.read_text(encoding="utf-8"))
    items = index_payload.get("items") or []
    tests = []
    for query, expected_id, type_filter in TAX_SEARCH_REGRESSIONS:
        allowed_types = SEARCH_TYPE_GROUPS.get(type_filter, {type_filter}) if type_filter else None
        candidates = [item for item in items if not allowed_types or item.get("type") in allowed_types]
        ranked = sorted(
            (
                {
                    "id": item.get("id"),
                    "title": item.get("title"),
                    "type": item.get("type"),
                    "score": score_search_index_item(item, query),
                }
                for item in candidates
            ),
            key=lambda item: (-(item["score"] or 0), str(item.get("title") or "")),
        )
        results = [item for item in ranked if item["score"] > 0][:5]
        top = results[0] if results else {}
        tests.append({
            "query": query,
            "type_filter": type_filter,
            "expected_top_id": expected_id,
            "actual_top_id": top.get("id"),
            "passed": top.get("id") == expected_id,
            "top_results": results,
        })

    payload = {
        "version": "OPENFIN-SEARCH-REGRESSION-REPORT-2026.07.04.1",
        "basis_date": CURRENT_REVIEW_DATE,
        "source_review_date": CURRENT_REVIEW_DATE,
        "ontology_kind": "openfin-search-regression-report",
        "search_index_path": str(SEARCH_INDEX_EXPORT.relative_to(REPO_ROOT)),
        "test_count": len(tests),
        "passed_count": sum(1 for test in tests if test["passed"]),
        "failed_count": sum(1 for test in tests if not test["passed"]),
        "tests": tests,
    }
    payload["export_checksum"] = payload_checksum(payload)
    SEARCH_REGRESSION_REPORT_EXPORT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return {
        "path": str(SEARCH_REGRESSION_REPORT_EXPORT.relative_to(REPO_ROOT)),
        "item_count": len(tests),
        "product_count": 0,
        "export_checksum": payload["export_checksum"],
        "quality_summary": {
            "test_count": payload["test_count"],
            "passed_count": payload["passed_count"],
            "failed_count": payload["failed_count"],
            "failures": [
                {
                    "query": test["query"],
                    "type": test["type_filter"],
                    "expected": test["expected_top_id"],
                    "actual": test["actual_top_id"],
                }
                for test in tests
                if not test["passed"]
            ],
            "last_failed_at": CURRENT_REVIEW_DATE if any(not test["passed"] for test in tests) else None,
        },
    }


def existing_export_count(path: Path) -> int:
    if not path.exists():
        return 0
    payload = json.loads(path.read_text(encoding="utf-8"))
    return int(payload.get("item_count") or len(payload.get("items") or []))


def write_quality_manifest(manifest: dict, search_report: dict) -> dict:
    exports = manifest.get("exports") or []
    payload = {
        "version": "OPENFIN-QUALITY-MANIFEST-2026.07.04.1",
        "basis_date": CURRENT_REVIEW_DATE,
        "source_review_date": CURRENT_REVIEW_DATE,
        "built_at": manifest.get("built_at"),
        "ontology_kind": "openfin-quality-manifest",
        "domain_summaries": [
            {
                "id": entry.get("id"),
                "domain": entry.get("domain"),
                "item_count": entry.get("item_count"),
                "product_count": entry.get("product_count"),
                "quality_summary": entry.get("quality_summary") or {},
                "export_checksum": entry.get("export_checksum"),
            }
            for entry in exports
        ],
        "search_regression_report": search_report,
        "source_access_risks": manifest.get("source_access_risks") or [],
        "api_required_sources": manifest.get("api_required_sources") or [],
        "export_audit": (manifest.get("quality_summary") or {}).get("export_audit") or {},
    }
    payload["export_checksum"] = payload_checksum(payload)
    QUALITY_MANIFEST_EXPORT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return {
        "path": str(QUALITY_MANIFEST_EXPORT.relative_to(REPO_ROOT)),
        "item_count": len(payload["domain_summaries"]),
        "product_count": 0,
        "export_checksum": payload["export_checksum"],
        "quality_summary": payload["export_audit"],
    }


def write_manifest(results: dict[str, dict], search_index: dict, search_report: dict) -> None:
    tax_path = "ontology/exports/korea-tax-ontology-2026.json"
    local_path = "ontology/exports/korea-local-government-supports-ontology-2026.json"
    full_export_paths = [
        tax_path,
        local_path,
        results["card"]["path"],
        results["deposit"]["path"],
        results["saving"]["path"],
        results["loan"]["path"],
        results["insurance"]["path"],
        results["reference"]["path"],
    ]
    built_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    manifest = {
        "version": "KR-FINANCE-ONTOLOGY-MANIFEST-2026.07.04.1",
        "basis_date": CURRENT_REVIEW_DATE,
        "source_review_date": CURRENT_REVIEW_DATE,
        "built_at": built_at,
        "name": "finance",
        "description": "Cloudflare finance MCP가 세금, 지자체 지원금, 카드, 은행, 보험, 금융 기준정보 온톨로지를 통합 로딩하기 위한 manifest입니다.",
        "quality_summary": {
            "export_audit": {
                "built_at": built_at,
                "domain_export_count": len(full_export_paths),
                "search_index_item_count": search_index["item_count"],
                "checksum_covered_export_count": sum(
                    1
                    for value in (*results.values(), search_index)
                    if value.get("export_checksum")
                ) + int(existing_export_checksum(REPO_ROOT / tax_path) is not None) + int(existing_export_checksum(REPO_ROOT / local_path) is not None),
                "broken_relation_count": broken_relation_count(full_export_paths),
                "collection_failure_sources": "see source_access_risks",
            },
            "search_regression_tests": search_report.get("quality_summary", {}),
            "committee_remediation": {
                "status_fields_added": True,
                "expired_local_support_active_gate": True,
                "active_insurance_without_criteria_gate": True,
                "status_aware_search_required": True,
                "cross_export_reference_validation": True,
                "semantic_product_related_edges_added": True,
            },
            "finance_exports": {
                key: value.get("quality_summary", {})
                for key, value in results.items()
            },
        },
        "source_access_risks": [
            {
                "source_id": "source.kdic.insured-products",
                "status": "live_imported",
                "last_checked": CURRENT_REVIEW_DATE,
                "last_observed_result": "HTTP 200 NORMAL SERVICE; totalCount 45292; current rows imported into deposit-protection generated snapshot",
                "mitigation": "상품판매중단일자가 있는 행은 기본 운영 export에서 제외하고 --include-kdic-ended-products 옵션으로만 이력 수집합니다.",
            },
            {
                "source_id": "source.klia.insurance-disclosure",
                "status": "live_imported",
                "last_checked": CURRENT_REVIEW_DATE,
                "last_observed_result": f"HTTP 200 public disclosure table; active insurance products imported: {results['insurance']['product_count']}",
                "mitigation": "상품 상세 약관 파일은 내려받지 않고 리스트 표의 상품명·담보·보험료·갱신여부·판매일자만 운영 export에 반영합니다.",
            },
            {
                "source_id": "source.fsc.medical-reimbursement-insurance",
                "status": "approved_by_user_but_live_403",
                "last_checked": CURRENT_REVIEW_DATE,
                "last_observed_result": "HTTP 403 with current DATA_GO_KR_SERVICE_KEY at GetMedicalReimbursementInsuranceInfoService/getInsuranceInfo",
                "mitigation": "권한이 열릴 때까지 실손보험 API 행은 생성하지 않고 생명보험협회 공시실 수집분만 보험상품으로 노출합니다.",
            },
            {
                "source_id": "source.fsc.variable-insurance-info",
                "status": "approved_by_user_but_live_403",
                "last_checked": CURRENT_REVIEW_DATE,
                "last_observed_result": "HTTP 403 with current DATA_GO_KR_SERVICE_KEY at GetVariableInsuranceInfoService/getFundInfo",
                "mitigation": "권한이 열릴 때까지 변액보험 펀드별 정보는 상품 노드가 아닌 대기 출처로만 기록합니다.",
            },
            {
                "source_id": "source.data.go.kr.kinfa-loan-handling-agencies",
                "status": "approved_by_user_but_live_403",
                "last_checked": CURRENT_REVIEW_DATE,
                "last_observed_result": "HTTP 403 with current DATA_GO_KR_SERVICE_KEY",
                "mitigation": "권한 전파 또는 서비스별 키 매핑이 정상화될 때까지 기존 policy-loan 상품의 취급기관 상세에 섞지 않습니다.",
            },
            {
                "source_id": "source.data.go.kr.kinfa-support-centers",
                "status": "approved_by_user_but_live_403",
                "last_checked": CURRENT_REVIEW_DATE,
                "last_observed_result": "HTTP 403 with current DATA_GO_KR_SERVICE_KEY",
                "mitigation": "권한 전파 또는 서비스별 키 매핑이 정상화될 때까지 상담센터·미소금융 지점 노드 생성을 보류합니다.",
            },
            {
                "source_id": "source.fsc.inclusive-finance-products",
                "status": "approved_by_user_endpoint_mapping_pending",
                "last_checked": CURRENT_REVIEW_DATE,
                "last_observed_result": "official metadata reviewed; endpoint mapping still pending",
                "mitigation": "서민금융상품기본정보 활용신청 및 Swagger endpoint 확인 후 기존 KINFA 상품과 중복 제거합니다.",
            },
            {
                "source_id": "source.fsc.inclusive-finance-performance",
                "status": "approved_by_user_metric_source",
                "last_checked": CURRENT_REVIEW_DATE,
                "last_observed_result": "official metadata reviewed; not a product-row source",
                "mitigation": "상품 노드가 아니라 실적·커버리지 지표로 별도 metric export를 만들 때 사용합니다.",
            },
            {
                "source_id": "source.bok.ecos",
                "status": "reference_source_added_key_required",
                "last_checked": CURRENT_REVIEW_DATE,
                "last_observed_result": "official ECOS Open API source reviewed; BOK API key is separate from DATA_GO_KR_SERVICE_KEY",
                "mitigation": "기준금리·시장금리 값은 BOK API 키가 준비될 때까지 benchmark-rate 기준 노드로만 노출합니다.",
            },
            {
                "source_id": "source.fsc.financial-company-basic",
                "status": "reference_source_added",
                "last_checked": CURRENT_REVIEW_DATE,
                "last_observed_result": "official metadata reviewed; provider registry currently derived from existing product exports",
                "mitigation": "금융회사 API 실데이터 수집 전에도 상품 provider 문자열을 financial-provider 노드로 묶어 MCP 검색성을 확보합니다.",
            },
        ],
        "api_required_sources": [
            {
                "source_id": "source.bok.ecos",
                "required_secret": "BOK_ECOS_API_KEY",
                "status": "missing_key",
                "needed_for": "한국은행 기준금리, 시장금리, 환율 등 시계열 기준지표 값 수집",
            },
            {
                "source_id": "source.fsc.financial-company-basic",
                "required_secret": "DATA_GO_KR_SERVICE_KEY + service_application",
                "status": "application_or_endpoint_mapping_required",
                "needed_for": "상품 provider 문자열을 공식 금융회사 코드·주소·설립일·상장폐지 상태와 매칭",
            },
            {
                "source_id": "source.fsc.financial-company-credit",
                "required_secret": "DATA_GO_KR_SERVICE_KEY + service_application",
                "status": "application_or_endpoint_mapping_required",
                "needed_for": "금융회사 재무·신용 리스크 지표를 provider 노드에 연결",
            },
            {
                "source_id": "source.fsc.domestic-bank-statistics",
                "required_secret": "DATA_GO_KR_SERVICE_KEY + service_application",
                "status": "application_or_endpoint_mapping_required",
                "needed_for": "은행 일반현황, 재무현황, 경영지표를 은행상품 provider 리스크에 연결",
            },
            {
                "source_id": "source.fsc.fund-products-basic",
                "required_secret": "DATA_GO_KR_SERVICE_KEY + service_application",
                "status": "application_required",
                "needed_for": "펀드표준코드, 펀드명, 운용사, 펀드유형 상품 행 생성",
            },
            {
                "source_id": "source.fsc.retirement-pension-basic",
                "required_secret": "DATA_GO_KR_SERVICE_KEY + service_application",
                "status": "application_required",
                "needed_for": "퇴직연금 펀드별 기준일자, 순자산금액, 운용 현황 수집",
            },
            {
                "source_id": "source.fsc.financial-investment-statistics",
                "required_secret": "DATA_GO_KR_SERVICE_KEY + service_application",
                "status": "application_required",
                "needed_for": "펀드 순자산, CMA 잔고, 신용공여 잔고, 증시자금 추이 지표 수집",
            },
            {
                "source_id": "source.fsc.medical-reimbursement-insurance",
                "required_secret": "DATA_GO_KR_SERVICE_KEY service_permission",
                "status": "approved_by_user_but_live_403",
                "needed_for": "실손의료보험 유형, 담보, 성별·연령별 보험료 상품 행 생성",
            },
            {
                "source_id": "source.fsc.variable-insurance-info",
                "required_secret": "DATA_GO_KR_SERVICE_KEY service_permission",
                "status": "approved_by_user_but_live_403",
                "needed_for": "변액보험 펀드 기준가, 순자산, 설정일자, 운용회사 정보 수집",
            },
            {
                "source_id": "source.data.go.kr.kinfa-loan-handling-agencies",
                "required_secret": "DATA_GO_KR_SERVICE_KEY service_permission",
                "status": "approved_by_user_but_live_403",
                "needed_for": "정책대출별 취급기관, 주소, 기관 코드 상세 연결",
            },
            {
                "source_id": "source.data.go.kr.kinfa-support-centers",
                "required_secret": "DATA_GO_KR_SERVICE_KEY service_permission",
                "status": "approved_by_user_but_live_403",
                "needed_for": "서민금융통합지원센터, 미소금융 지점 지역·주소·전화번호 노드 생성",
            },
        ],
        "public_web_collection_candidates": [
            {
                "source_id": "source.kfb.consumer-portal",
                "collection_mode": "public_web_or_excel_scrape",
                "needed_for": "은행권 예금·대출 금리, 예대금리차, COFIX 최신 공시값",
            },
            {
                "source_id": "source.fsb.savings-bank-deposit-rates",
                "collection_mode": "public_web_or_excel_scrape",
                "needed_for": "저축은행 정기예금·적금 상품별 금리표",
            },
            {
                "source_id": "source.kofia.fund-oneclick",
                "collection_mode": "public_web_scrape",
                "needed_for": "펀드 상세, 운용사·판매사 연결, 투자설명서·운용보고서 링크",
            },
            {
                "source_id": "source.fss.integrated-pension-portal",
                "collection_mode": "public_web_scrape_or_future_api",
                "needed_for": "연금저축 수익률·수수료·위험등급·판매사별 적립금",
            },
            {
                "source_id": "source.fss.fine.portal",
                "collection_mode": "public_web_reference",
                "needed_for": "숨은 금융자산, 소비자 보호 안내, 금융생활 위험 신호 연결",
            },
        ],
        "search_index": export_entry(
            "finance-search-index",
            "search-index",
            search_index["path"],
            search_index["item_count"],
            0,
            "MCP search 전용 경량 인덱스입니다.",
            [],
            {},
            search_index.get("export_checksum"),
        ),
        "quality_exports": [
            export_entry(
                "openfin-search-regression-report",
                "quality",
                search_report["path"],
                search_report["item_count"],
                0,
                "세금 검색 P0 질의가 올바른 노드로 가는지 검증한 회귀테스트 결과입니다.",
                [],
                search_report.get("quality_summary"),
                search_report.get("export_checksum"),
            ),
        ],
        "exports": [
            export_entry(
                "tax-ontology",
                "tax",
                tax_path,
                existing_export_count(REPO_ROOT / tax_path),
                0,
                "세금, 공제, 신고기한, 중앙 정책지원 핵심 온톨로지입니다.",
                [],
                existing_export_quality_summary(REPO_ROOT / tax_path),
                existing_export_checksum(REPO_ROOT / tax_path),
            ),
            export_entry(
                "local-government-supports-ontology",
                "local-government-supports",
                local_path,
                existing_export_count(REPO_ROOT / local_path),
                0,
                "정부24 보조금24 기준 지자체 지원금 대용량 온톨로지입니다.",
                [],
                existing_export_quality_summary(REPO_ROOT / local_path),
                existing_export_checksum(REPO_ROOT / local_path),
            ),
            export_entry(
                "card-products-ontology",
                "card-products",
                results["card"]["path"],
                results["card"]["item_count"],
                results["card"]["product_count"],
                "신용카드·체크카드 혜택, 전월실적, 한도, 제외조건 온톨로지입니다.",
                results["card"]["product_collection_dates"],
                results["card"].get("quality_summary"),
                results["card"].get("export_checksum"),
            ),
            export_entry(
                "deposit-products-ontology",
                "deposit-products",
                results["deposit"]["path"],
                results["deposit"]["item_count"],
                results["deposit"]["product_count"],
                "정기예금 팩: 예치기간별 금리, 최고우대금리, 가입한도, 우대조건 온톨로지입니다.",
                results["deposit"]["product_collection_dates"],
                results["deposit"].get("quality_summary"),
                results["deposit"].get("export_checksum"),
            ),
            export_entry(
                "saving-products-ontology",
                "saving-products",
                results["saving"]["path"],
                results["saving"]["item_count"],
                results["saving"]["product_count"],
                "적금 팩: 적립방식, 기간별 금리, 납입한도, 우대조건 온톨로지입니다.",
                results["saving"]["product_collection_dates"],
                results["saving"].get("quality_summary"),
                results["saving"].get("export_checksum"),
            ),
            export_entry(
                "loan-products-ontology",
                "loan-products",
                results["loan"]["path"],
                results["loan"]["item_count"],
                results["loan"]["product_count"],
                "대출 팩: 주택담보·전세·개인신용·정책대출 금리, 한도, 상환방식, 수수료 온톨로지입니다.",
                results["loan"]["product_collection_dates"],
                results["loan"].get("quality_summary"),
                results["loan"].get("export_checksum"),
            ),
            export_entry(
                "insurance-products-ontology",
                "insurance-products",
                results["insurance"]["path"],
                results["insurance"]["item_count"],
                results["insurance"]["product_count"],
                "보험료, 보장, 면책, 갱신, 약관 출처 온톨로지입니다.",
                results["insurance"]["product_collection_dates"],
                results["insurance"].get("quality_summary"),
                results["insurance"].get("export_checksum"),
            ),
            export_entry(
                "finance-reference-ontology",
                "finance-reference",
                results["reference"]["path"],
                results["reference"]["item_count"],
                results["reference"]["product_count"],
                "금융회사, 기준금리, 보험 리스크, 투자상품 후보, 정책금융 출처 상태, 예금자보호 등재 레지스트리를 묶은 기준정보 온톨로지입니다.",
                results["reference"]["product_collection_dates"],
                results["reference"].get("quality_summary"),
                results["reference"].get("export_checksum"),
            ),
        ],
    }
    quality_manifest = write_quality_manifest(manifest, search_report)
    manifest["quality_exports"].insert(
        0,
        export_entry(
            "openfin-quality-manifest",
            "quality",
            quality_manifest["path"],
            quality_manifest["item_count"],
            0,
            "도메인별 품질 요약, 검색 회귀테스트, 출처 리스크, checksum을 모은 운영 감사 manifest입니다.",
            [],
            quality_manifest.get("quality_summary"),
            quality_manifest.get("export_checksum"),
        ),
    )
    MANIFEST_EXPORT.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    DOCS_ROOT.mkdir(parents=True, exist_ok=True)
    for path in (CARD_EXPORT, DEPOSIT_EXPORT, SAVING_EXPORT, LOAN_EXPORT, INSURANCE_EXPORT, REFERENCE_EXPORT, SEARCH_INDEX_EXPORT, MANIFEST_EXPORT, QUALITY_MANIFEST_EXPORT, SEARCH_REGRESSION_REPORT_EXPORT):
        (DOCS_ROOT / path.name).write_text(path.read_text(encoding="utf-8"), encoding="utf-8")


def main() -> int:
    results = {
        "card": write_export(
            CARD_EXPORT,
            "KR-CARD-PRODUCTS-ONTOLOGY-2026.07.04.1",
            "card-products",
            card_items(),
            "card-product",
            "card",
        ),
        "deposit": write_export(
            DEPOSIT_EXPORT,
            "KR-DEPOSIT-PRODUCTS-ONTOLOGY-2026.07.04.1",
            "deposit-products",
            bank_pack_items("deposit"),
            "bank-product",
            "deposit",
        ),
        "saving": write_export(
            SAVING_EXPORT,
            "KR-SAVING-PRODUCTS-ONTOLOGY-2026.07.04.1",
            "saving-products",
            bank_pack_items("saving"),
            "bank-product",
            "saving",
        ),
        "loan": write_export(
            LOAN_EXPORT,
            "KR-LOAN-PRODUCTS-ONTOLOGY-2026.07.04.1",
            "loan-products",
            bank_pack_items("loan"),
            "bank-product",
            "loan",
        ),
        "insurance": write_export(
            INSURANCE_EXPORT,
            "KR-INSURANCE-PRODUCTS-ONTOLOGY-2026.07.04.1",
            "insurance-products",
            insurance_items(),
            "insurance-product",
            "insurance",
        ),
    }
    results["reference"] = write_export(
        REFERENCE_EXPORT,
        "KR-FINANCE-REFERENCE-ONTOLOGY-2026.07.04.1",
        "finance-reference",
        finance_reference_items(),
        "finance-reference",
        "reference",
    )
    search_index = write_search_index([
        ("tax-ontology", "ontology/exports/korea-tax-ontology-2026.json"),
        ("local-government-supports-ontology", "ontology/exports/korea-local-government-supports-ontology-2026.json"),
        ("card-products-ontology", results["card"]["path"]),
        ("deposit-products-ontology", results["deposit"]["path"]),
        ("saving-products-ontology", results["saving"]["path"]),
        ("loan-products-ontology", results["loan"]["path"]),
        ("insurance-products-ontology", results["insurance"]["path"]),
        ("finance-reference-ontology", results["reference"]["path"]),
    ])
    search_report = write_search_regression_report()
    write_manifest(results, search_index, search_report)
    print(f"Exported {CARD_EXPORT}")
    print(f"Exported {DEPOSIT_EXPORT}")
    print(f"Exported {SAVING_EXPORT}")
    print(f"Exported {LOAN_EXPORT}")
    print(f"Exported {INSURANCE_EXPORT}")
    print(f"Exported {REFERENCE_EXPORT}")
    print(f"Exported {MANIFEST_EXPORT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
