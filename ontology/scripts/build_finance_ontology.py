#!/usr/bin/env python3
"""Build split finance ontology exports.

The finance product surface is intentionally separated from the tax ontology:
product values change frequently, often require API keys, and must preserve
source-specific disclosure fields for later stale/closed-product checks.
"""
# allow: SIZE_OK -- source/category data table kept together for deterministic split exports.

from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable


REPO_ROOT = Path(__file__).resolve().parents[2]
ROOT = Path(__file__).resolve().parents[1]
EXPORT_DIR = ROOT / "exports"
CUSTOM_FINANCE_DIR = ROOT / "custom" / "finance"
DOCS_ROOT = REPO_ROOT / "docs" / "opentax"

CURRENT_REVIEW_DATE = "2026-07-02"
CURRENT_BASIS_YEAR = 2026
RAW_BASE_URL = "https://raw.githubusercontent.com/jhny-kor/TaxMeter/main"
WEB_BASE_URL = "https://jhny-kor.github.io/TaxMeter/opentax"

CARD_EXPORT = EXPORT_DIR / "korea-card-products-ontology-2026.json"
BANK_EXPORT = EXPORT_DIR / "korea-bank-products-ontology-2026.json"
INSURANCE_EXPORT = EXPORT_DIR / "korea-insurance-products-ontology-2026.json"
MANIFEST_EXPORT = EXPORT_DIR / "finance-ontology-manifest.json"

GENERATED_FILES = {
    "card": CUSTOM_FINANCE_DIR / "card-products.generated.json",
    "bank": CUSTOM_FINANCE_DIR / "bank-products.generated.json",
    "policy_loan": CUSTOM_FINANCE_DIR / "policy-loan-products.generated.json",
    "insurance": CUSTOM_FINANCE_DIR / "insurance-products.generated.json",
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
        "2026-07-02 확인",
    ),
    "source.fss.finlife.web": source_node(
        "source.fss.finlife.web",
        "금융상품통합비교공시 금융상품한눈에",
        "금융감독원",
        "https://finlife.fss.or.kr/",
        "예금, 적금, 대출, 연금저축 등 금융상품 비교공시를 제공하는 금융감독원 공식 웹 표면입니다.",
        "2026-07-02 확인",
    ),
    "source.fsc.business-loan-comparison": source_node(
        "source.fsc.business-loan-comparison",
        "개인사업자 대출상품 비교공시 서비스 개시",
        "금융위원회",
        "https://www.fsc.go.kr/no010101/83693",
        "금융상품 한눈에의 개인사업자 대출상품 비교공시 신설, 자금용도·가입대상·대출종류·필요금액 등 검색조건과 상세정보 제공 근거입니다.",
        "2026-07-02 확인",
    ),
    "source.data.go.kr.kinfa-loan-products": source_node(
        "source.data.go.kr.kinfa-loan-products",
        "서민금융진흥원 대출상품한눈에 정보 서비스",
        "공공데이터포털",
        "https://www.data.go.kr/data/15106208/openapi.do?recommendDataYn=Y",
        "서민금융·정책금융 대출상품의 대출한도, 금리구분, 대출용도, 총 대출기간, 취급기관 등을 비교 조회하는 공공데이터 API 후보입니다.",
        "2026-07-02 확인",
    ),
    "source.kinfa.hessal-loan-youth": source_node(
        "source.kinfa.hessal-loan-youth",
        "햇살론유스",
        "서민금융진흥원",
        "https://www.kinfa.or.kr/financialProduct/hessalLoanYoos.do",
        "청년·대학생 대상 햇살론유스의 지원대상, 보증한도, 보증기간, 대출금리와 보증료율 공식 안내입니다.",
        "2026-07-02 확인",
    ),
    "source.kinfa.illegal-private-finance-prevention-loan": source_node(
        "source.kinfa.illegal-private-finance-prevention-loan",
        "불법사금융예방대출",
        "서민금융진흥원",
        "https://www.kinfa.or.kr/financialProduct/smallLivingLoan.do",
        "대부업 이용도 어려운 저신용·저소득자 생계비 대출의 지원대상, 금리, 한도, 상환방식 공식 안내입니다.",
        "2026-07-02 확인",
    ),
    "source.myhome.support-lease-loan": source_node(
        "source.myhome.support-lease-loan",
        "버팀목전세대출",
        "마이홈포털",
        "https://www.myhome.go.kr/hws/portal/cont/selectSupLeaseLoanView.do",
        "근로자·서민 주거 안정을 위한 버팀목전세대출의 대상, 금리, 한도, 기간, 우대금리 공식 안내입니다.",
        "2026-07-02 확인",
    ),
    "source.hf.bogeumjari-loan": source_node(
        "source.hf.bogeumjari-loan",
        "보금자리론 상품소개",
        "한국주택금융공사",
        "https://www.hf.go.kr/ko/sub01/sub01_01_02.do",
        "보금자리론의 신청대상, 대출요건, 한도, 만기, 상환방식과 특성별 상품 공식 안내입니다.",
        "2026-07-02 확인",
    ),
    "source.crefia.card-lending-products": source_node(
        "source.crefia.card-lending-products",
        "카드대출상품",
        "여신금융협회",
        "https://gongsi.crefia.or.kr/portal/financialProdInfo/cardLendingProd",
        "단기카드대출(현금서비스)과 장기카드대출(카드론)의 기간, 한도, 이용방법, 수수료율과 유의사항을 설명하는 공식 공시입니다.",
        "2026-07-02 확인",
    ),
    "source.crefia.card-loan-revolving-rates": source_node(
        "source.crefia.card-loan-revolving-rates",
        "카드대출·결제성 리볼빙 신용점수별 수수료율",
        "여신금융협회",
        "https://gongsi.crefia.or.kr/portal/creditcard/creditcardDisclosureDetail20?cgcMode=20",
        "현금서비스, 카드론, 결제성 리볼빙의 신용점수별 금리·수수료율 비교공시 표면입니다.",
        "2026-07-02 확인",
    ),
    "source.fsc.revolving-service-improvement": source_node(
        "source.fsc.revolving-service-improvement",
        "신용카드 결제성 리볼빙 서비스 개선방안",
        "금융위원회",
        "https://www.fsc.go.kr/no010101/78357",
        "결제성 리볼빙 서비스의 설명의무, 수수료율 안내·공시 강화, 건전한 이용 유도 기준을 정리한 금융위원회 보도자료입니다.",
        "2026-07-02 확인",
    ),
    "source.crefia.lease-installment-products": source_node(
        "source.crefia.lease-installment-products",
        "리스할부상품",
        "여신금융협회",
        "https://gongsi.crefia.or.kr/portal/financialProdInfo/leaseProd",
        "자동차리스와 자동차·주택·가전·기계류·기타 할부 상품 공시 범위를 설명하는 공식 금융상품정보 표면입니다.",
        "2026-07-02 확인",
    ),
    "source.crefia.auto-lease-disclosure": source_node(
        "source.crefia.auto-lease-disclosure",
        "자동차리스 상품 리스료 비교 조회",
        "여신금융협회",
        "https://gongsi.crefia.or.kr/portal/quota/quotaFinancingDisclosureDetail60?ifgcMode=60",
        "자동차리스 금융상품의 리스료, 보증금·잔존가치 조건, 중도해지수수료 비교공시 표면입니다.",
        "2026-07-02 확인",
    ),
    "source.crefia.credit-loan-products": source_node(
        "source.crefia.credit-loan-products",
        "신용대출상품",
        "여신금융협회",
        "https://gongsi.crefia.or.kr/portal/financialProdInfo/creditLendingProd",
        "여신전문금융회사 신용대출과 민간중금리대출의 의미, 요건, 이용방법을 설명하는 공식 금융상품정보 표면입니다.",
        "2026-07-02 확인",
    ),
    "source.crefia.credit-loan-rate-disclosure": source_node(
        "source.crefia.credit-loan-rate-disclosure",
        "신용대출상품 신용점수별 평균금리현황",
        "여신금융협회",
        "https://gongsi.crefia.or.kr/portal/creditloan/creditloanDisclosureDetail11",
        "여신전문금융회사 신용대출상품의 신용점수 구간별 평균금리 비교공시 표면입니다.",
        "2026-07-02 확인",
    ),
    "source.crefia.card-products": source_node(
        "source.crefia.card-products",
        "카드상품 공시",
        "여신금융협회",
        "https://gongsi.crefia.or.kr/portal/financialProdInfo/cardProd",
        "신용카드와 체크카드 상품의 기본 공시 및 카드상품 비교 원천입니다.",
        "2026-07-02 확인",
    ),
    "source.crefia.carddamoa": source_node(
        "source.crefia.carddamoa",
        "카드다모아",
        "여신금융협회",
        "https://gongsi.crefia.or.kr/portal/carddamoa/carddamoaList",
        "카드사별 신용카드·체크카드 혜택, 전월실적, 할인·적립 조건을 비교하기 위한 공식 카드 비교 표면입니다.",
        "2026-07-02 확인",
    ),
    "source.kbcard.card-list": source_node(
        "source.kbcard.card-list",
        "KB국민카드 카드한눈에보기",
        "KB국민카드",
        "https://card.kbcard.com/CRD/DVIEW/HCAM0101",
        "KB국민카드 신용카드·체크카드 상품명, 상품코드, 주요혜택, 상세페이지 링크를 제공하는 발급사 공식 카드 목록입니다.",
        "2026-07-02 확인",
    ),
    "source.bccard.credit-card-list": source_node(
        "source.bccard.credit-card-list",
        "비씨카드 신용카드 상품",
        "비씨카드",
        "https://www.bccard.com/app/card/CreditCardMain.do",
        "비씨카드와 회원사의 신용카드 상품명, 발급사, 상품코드, 주요혜택을 제공하는 공식 카드 목록입니다.",
        "2026-07-02 확인",
    ),
    "source.bccard.check-card-list": source_node(
        "source.bccard.check-card-list",
        "비씨카드 체크카드 상품",
        "비씨카드",
        "https://www.bccard.com/app/card/CheckCardMain.do",
        "비씨카드와 회원사의 체크카드 상품명, 발급사, 상품코드, 주요혜택을 제공하는 공식 카드 목록입니다.",
        "2026-07-02 확인",
    ),
    "source.samsungcard.credit-card-list": source_node(
        "source.samsungcard.credit-card-list",
        "삼성카드 신용카드 상품",
        "삼성카드",
        "https://www.samsungcard.com/home/card/cardinfo/PGHPPDCCardCardinfoRecommendPC001",
        "삼성카드 신용카드 상품명, 상품코드, 주요혜택, 카드 이미지와 상세페이지 링크를 제공하는 공식 WCMS 카드 목록입니다.",
        "2026-07-02 확인",
    ),
    "source.samsungcard.check-card-list": source_node(
        "source.samsungcard.check-card-list",
        "삼성카드 체크카드 상품",
        "삼성카드",
        "https://www.samsungcard.com/home/card/cardinfo/PGHPPCCCardCardinfoCheckcard001",
        "삼성카드 체크카드 상품명, 상품코드, 주요혜택, 카드 이미지와 상세페이지 링크를 제공하는 공식 WCMS 카드 목록입니다.",
        "2026-07-02 확인",
    ),
    "source.einsmarket.insurance": source_node(
        "source.einsmarket.insurance",
        "온라인 보험슈퍼마켓 보험다모아",
        "보험다모아",
        "https://www.e-insmarket.or.kr/",
        "자동차보험, 실손의료보험, 여행자보험, 연금 등 보험상품 보험료 비교를 제공하는 공식 보험 비교 표면입니다.",
        "2026-07-02 확인",
    ),
    "source.klia.insurance-disclosure": source_node(
        "source.klia.insurance-disclosure",
        "생명보험협회 공시실",
        "생명보험협회",
        "https://pub.insure.or.kr/",
        "생명보험 상품 공시와 보장성 상품·변액보험 등 생명보험 상품 정보를 확인하는 공식 공시실입니다.",
        "2026-07-02 확인",
    ),
    "source.knia.insurance-disclosure": source_node(
        "source.knia.insurance-disclosure",
        "손해보험협회 공시실",
        "손해보험협회",
        "https://kpub.knia.or.kr/",
        "손해보험 상품 공시, 보험료 비교, 판매상태 확인을 위한 손해보험 업권 공시 원천입니다.",
        "2026-07-02 확인",
    ),
    "source.easylaw.finance-product-disclosure": source_node(
        "source.easylaw.finance-product-disclosure",
        "금융상품 비교공시 범위",
        "찾기쉬운 생활법령정보",
        "https://www.easylaw.go.kr/CSP/CnpClsMainBtr.laf?ccfNo=1&cciNo=1&cnpClsNo=1&csmSeq=1771",
        "금융상품 비교공시 항목에 이자율, 보험료, 수수료, 중도상환수수료율, 위험등급, 공시시점 등이 포함된다는 근거입니다.",
        "2026-07-02 확인",
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
    generated = load_generated("bank")
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
                "category.finance.specialized-credit-loan-products",
                "category.finance.installment-finance-products",
                "category.finance.lease-finance-products",
            ],
            sources=[
                "source.fss.finlife.api",
                "source.fss.finlife.web",
                "source.fsc.business-loan-comparison",
                "source.data.go.kr.kinfa-loan-products",
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
            tags=["finance-ontology", "bank-products-ontology"],
        ),
        node(
            "category.finance.deposit-products",
            "정기예금 상품",
            "category",
            "예치기간별 기본금리, 최고우대금리, 가입한도와 가입대상 조건을 관리합니다.",
            parents=["finance.bank-products-ontology"],
            sources=["source.fss.finlife.api"],
            tags=["bank-products-ontology", "deposit"],
        ),
        node(
            "category.finance.savings-products",
            "적금 상품",
            "category",
            "정액적립·자유적립 방식, 기간별 기본금리, 최고우대금리, 납입한도와 우대조건을 관리합니다.",
            parents=["finance.bank-products-ontology"],
            sources=["source.fss.finlife.api"],
            tags=["bank-products-ontology", "saving"],
        ),
        node(
            "category.finance.mortgage-loan-products",
            "주택담보대출 상품",
            "category",
            "금리유형, 상환방식, 최저·최고금리, 중도상환수수료, 대출한도 조건을 관리합니다.",
            parents=["finance.bank-products-ontology"],
            sources=["source.fss.finlife.api"],
            tags=["bank-products-ontology", "mortgage-loan"],
        ),
        node(
            "category.finance.rent-loan-products",
            "전세자금대출 상품",
            "category",
            "전세자금 대출의 금리, 보증·담보 조건, 대출한도, 상환방식과 신청대상을 관리합니다.",
            parents=["finance.bank-products-ontology"],
            sources=["source.fss.finlife.api"],
            tags=["bank-products-ontology", "rent-loan"],
        ),
        node(
            "category.finance.credit-loan-products",
            "개인신용대출 상품",
            "category",
            "개인신용대출의 신용점수 구간별 금리, 평균금리, 대출한도, 상환방식을 관리합니다.",
            parents=["finance.bank-products-ontology"],
            sources=["source.fss.finlife.api"],
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
        SOURCES["source.fsc.business-loan-comparison"],
        SOURCES["source.data.go.kr.kinfa-loan-products"],
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
            sources=["source.einsmarket.insurance", "source.klia.insurance-disclosure"],
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
        SOURCES["source.knia.insurance-disclosure"],
        SOURCES["source.easylaw.finance-product-disclosure"],
    ])


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
    normalized = normalize_links(items)
    product_count = product_counts(normalized, product_type)
    product_collection_dates = sorted({
        item["collected_at"]
        for item in normalized
        if item.get("type") == product_type and item.get("collected_at")
    })
    payload = {
        "version": version,
        "basis_date": CURRENT_REVIEW_DATE,
        "source_review_date": CURRENT_REVIEW_DATE,
        "product_collection_dates": product_collection_dates,
        "domain": domain,
        "ontology_kind": f"{domain}-ontology",
        **generated_status(generated_domain, product_count),
        "items": normalized,
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return {
        "path": str(path.relative_to(REPO_ROOT)),
        "item_count": len(normalized),
        "product_count": product_count,
        "product_collection_dates": product_collection_dates,
    }


def export_entry(
    id_: str,
    domain: str,
    path: str,
    item_count: int,
    product_count: int,
    description: str,
    product_collection_dates: list[str] | None = None,
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
        "description": description,
    }


def existing_export_count(path: Path) -> int:
    if not path.exists():
        return 0
    payload = json.loads(path.read_text(encoding="utf-8"))
    return int(payload.get("item_count") or len(payload.get("items") or []))


def write_manifest(results: dict[str, dict]) -> None:
    tax_path = "ontology/exports/korea-tax-ontology-2026.json"
    local_path = "ontology/exports/korea-local-government-supports-ontology-2026.json"
    manifest = {
        "version": "KR-FINANCE-ONTOLOGY-MANIFEST-2026.07.02.1",
        "basis_date": CURRENT_REVIEW_DATE,
        "source_review_date": CURRENT_REVIEW_DATE,
        "name": "finance",
        "description": "Cloudflare finance MCP가 세금, 지자체 지원금, 카드, 은행, 보험 온톨로지를 통합 로딩하기 위한 manifest입니다.",
        "exports": [
            export_entry(
                "tax-ontology",
                "tax",
                tax_path,
                existing_export_count(REPO_ROOT / tax_path),
                0,
                "세금, 공제, 신고기한, 중앙 정책지원 핵심 온톨로지입니다.",
            ),
            export_entry(
                "local-government-supports-ontology",
                "local-government-supports",
                local_path,
                existing_export_count(REPO_ROOT / local_path),
                0,
                "정부24 보조금24 기준 지자체 지원금 대용량 온톨로지입니다.",
            ),
            export_entry(
                "card-products-ontology",
                "card-products",
                results["card"]["path"],
                results["card"]["item_count"],
                results["card"]["product_count"],
                "신용카드·체크카드 혜택, 전월실적, 한도, 제외조건 온톨로지입니다.",
                results["card"]["product_collection_dates"],
            ),
            export_entry(
                "bank-products-ontology",
                "bank-products",
                results["bank"]["path"],
                results["bank"]["item_count"],
                results["bank"]["product_count"],
                "예금·적금·주택담보·전세·개인신용·개인사업자·정책대출 금리, 한도, 수수료, 우대조건 온톨로지입니다.",
                results["bank"]["product_collection_dates"],
            ),
            export_entry(
                "insurance-products-ontology",
                "insurance-products",
                results["insurance"]["path"],
                results["insurance"]["item_count"],
                results["insurance"]["product_count"],
                "보험료, 보장, 면책, 갱신, 약관 출처 온톨로지입니다.",
                results["insurance"]["product_collection_dates"],
            ),
        ],
    }
    MANIFEST_EXPORT.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    DOCS_ROOT.mkdir(parents=True, exist_ok=True)
    for path in (CARD_EXPORT, BANK_EXPORT, INSURANCE_EXPORT, MANIFEST_EXPORT):
        (DOCS_ROOT / path.name).write_text(path.read_text(encoding="utf-8"), encoding="utf-8")


def main() -> int:
    results = {
        "card": write_export(
            CARD_EXPORT,
            "KR-CARD-PRODUCTS-ONTOLOGY-2026.07.02.1",
            "card-products",
            card_items(),
            "card-product",
            "card",
        ),
        "bank": write_export(
            BANK_EXPORT,
            "KR-BANK-PRODUCTS-ONTOLOGY-2026.07.02.1",
            "bank-products",
            bank_items(),
            "bank-product",
            "bank",
        ),
        "insurance": write_export(
            INSURANCE_EXPORT,
            "KR-INSURANCE-PRODUCTS-ONTOLOGY-2026.07.02.1",
            "insurance-products",
            insurance_items(),
            "insurance-product",
            "insurance",
        ),
    }
    write_manifest(results)
    print(f"Exported {CARD_EXPORT}")
    print(f"Exported {BANK_EXPORT}")
    print(f"Exported {INSURANCE_EXPORT}")
    print(f"Exported {MANIFEST_EXPORT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
