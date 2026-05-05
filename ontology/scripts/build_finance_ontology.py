#!/usr/bin/env python3
"""Build split finance ontology exports.

The finance product surface is intentionally separated from the tax ontology:
product values change frequently, often require API keys, and must preserve
source-specific disclosure fields for later stale/closed-product checks.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable


REPO_ROOT = Path(__file__).resolve().parents[2]
ROOT = Path(__file__).resolve().parents[1]
EXPORT_DIR = ROOT / "exports"
CUSTOM_FINANCE_DIR = ROOT / "custom" / "finance"
DOCS_ROOT = REPO_ROOT / "docs" / "opentax"

CURRENT_REVIEW_DATE = "2026-05-05"
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
        "2026-05-05 확인",
    ),
    "source.fss.finlife.web": source_node(
        "source.fss.finlife.web",
        "금융상품통합비교공시 금융상품한눈에",
        "금융감독원",
        "https://finlife.fss.or.kr/",
        "예금, 적금, 대출, 연금저축 등 금융상품 비교공시를 제공하는 금융감독원 공식 웹 표면입니다.",
        "2026-05-05 확인",
    ),
    "source.crefia.card-products": source_node(
        "source.crefia.card-products",
        "카드상품 공시",
        "여신금융협회",
        "https://gongsi.crefia.or.kr/portal/financialProdInfo/cardProd",
        "신용카드와 체크카드 상품의 기본 공시 및 카드상품 비교 원천입니다.",
        "2026-05-05 확인",
    ),
    "source.crefia.carddamoa": source_node(
        "source.crefia.carddamoa",
        "카드다모아",
        "여신금융협회",
        "https://gongsi.crefia.or.kr/portal/carddamoa/carddamoaList",
        "카드사별 신용카드·체크카드 혜택, 전월실적, 할인·적립 조건을 비교하기 위한 공식 카드 비교 표면입니다.",
        "2026-05-05 확인",
    ),
    "source.einsmarket.insurance": source_node(
        "source.einsmarket.insurance",
        "온라인 보험슈퍼마켓 보험다모아",
        "보험다모아",
        "https://www.e-insmarket.or.kr/",
        "자동차보험, 실손의료보험, 여행자보험, 연금 등 보험상품 보험료 비교를 제공하는 공식 보험 비교 표면입니다.",
        "2026-05-05 확인",
    ),
    "source.klia.insurance-disclosure": source_node(
        "source.klia.insurance-disclosure",
        "생명보험협회 공시실",
        "생명보험협회",
        "https://pub.insure.or.kr/",
        "생명보험 상품 공시와 보장성 상품·변액보험 등 생명보험 상품 정보를 확인하는 공식 공시실입니다.",
        "2026-05-05 확인",
    ),
    "source.knia.insurance-disclosure": source_node(
        "source.knia.insurance-disclosure",
        "손해보험협회 공시실",
        "손해보험협회",
        "https://kpub.knia.or.kr/",
        "손해보험 상품 공시, 보험료 비교, 판매상태 확인을 위한 손해보험 업권 공시 원천입니다.",
        "2026-05-05 확인",
    ),
    "source.easylaw.finance-product-disclosure": source_node(
        "source.easylaw.finance-product-disclosure",
        "금융상품 비교공시 범위",
        "찾기쉬운 생활법령정보",
        "https://www.easylaw.go.kr/CSP/CnpClsMainBtr.laf?ccfNo=1&cciNo=1&cnpClsNo=1&csmSeq=1771",
        "금융상품 비교공시 항목에 이자율, 보험료, 수수료, 중도상환수수료율, 위험등급, 공시시점 등이 포함된다는 근거입니다.",
        "2026-05-05 확인",
    ),
}


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
            "신용카드·체크카드의 전월실적, 할인·적립률, 월 한도, 제외 조건, 연회비, 판매상태를 구조화하는 금융상품 온톨로지입니다.",
            children=["category.finance.credit-cards", "category.finance.check-cards"],
            sources=["source.crefia.card-products", "source.crefia.carddamoa", "source.easylaw.finance-product-disclosure"],
            tags=["finance-ontology", "card-products-ontology"],
        ),
        node(
            "category.finance.credit-cards",
            "신용카드 상품",
            "category",
            "신용공여 기능이 있는 카드상품의 연회비, 전월실적, 할인·적립 혜택, 한도와 제외조건을 관리합니다.",
            parents=["finance.card-products-ontology"],
            sources=["source.crefia.card-products", "source.crefia.carddamoa"],
            tags=["card-products-ontology", "credit-card"],
        ),
        node(
            "category.finance.check-cards",
            "체크카드 상품",
            "category",
            "결제계좌 잔액 범위에서 쓰는 체크카드 상품의 캐시백, 할인, 전월실적, 월 한도와 제외조건을 관리합니다.",
            parents=["finance.card-products-ontology"],
            sources=["source.crefia.card-products", "source.crefia.carddamoa"],
            tags=["card-products-ontology", "check-card"],
        ),
        node(
            "term.card.previous-month-spend",
            "전월실적",
            "term",
            "카드 혜택 적용 여부를 판단할 때 카드사가 정한 직전 월 이용금액 기준입니다. 실적 제외 항목이 별도로 존재할 수 있습니다.",
            sources=["source.crefia.card-products", "source.crefia.carddamoa"],
            tags=["card-products-ontology", "benefit-criterion"],
        ),
        node(
            "term.card.monthly-benefit-limit",
            "월 혜택 한도",
            "term",
            "할인, 캐시백, 포인트 적립 등 카드 혜택이 한 달에 적용되는 최대 금액 또는 횟수입니다.",
            sources=["source.crefia.card-products", "source.crefia.carddamoa"],
            tags=["card-products-ontology", "benefit-limit"],
        ),
        node(
            "term.card.excluded-spend",
            "실적·혜택 제외 항목",
            "term",
            "세금, 공과금, 상품권, 아파트관리비, 보험료 등 카드사가 실적 또는 혜택 산정에서 제외할 수 있는 항목입니다.",
            sources=["source.crefia.card-products", "source.crefia.carddamoa"],
            tags=["card-products-ontology", "exclusion"],
        ),
    ]
    items.extend(generated)
    return attach_source_metadata([*items, SOURCES["source.crefia.card-products"], SOURCES["source.crefia.carddamoa"], SOURCES["source.easylaw.finance-product-disclosure"]])


def bank_items() -> list[dict]:
    generated = load_generated("bank")
    items = [
        node(
            "finance.bank-products-ontology",
            "은행상품 온톨로지",
            "domain",
            "정기예금, 적금, 주택담보대출, 전세자금대출, 개인신용대출의 금리, 우대조건, 가입한도, 수수료, 판매상태를 구조화하는 금융상품 온톨로지입니다.",
            children=[
                "category.finance.deposit-products",
                "category.finance.savings-products",
                "category.finance.mortgage-loan-products",
                "category.finance.rent-loan-products",
                "category.finance.credit-loan-products",
            ],
            sources=["source.fss.finlife.api", "source.fss.finlife.web", "source.easylaw.finance-product-disclosure"],
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
    ]
    items.extend(generated)
    return attach_source_metadata([*items, SOURCES["source.fss.finlife.api"], SOURCES["source.fss.finlife.web"], SOURCES["source.easylaw.finance-product-disclosure"]])


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
    payload = {
        "version": version,
        "basis_date": CURRENT_REVIEW_DATE,
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
    }


def export_entry(id_: str, domain: str, path: str, item_count: int, product_count: int, description: str) -> dict:
    return {
        "id": id_,
        "domain": domain,
        "path": path,
        "url": f"{RAW_BASE_URL}/{path}",
        "web_url": f"{WEB_BASE_URL}/{Path(path).name}",
        "item_count": item_count,
        "product_count": product_count,
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
        "version": "KR-FINANCE-ONTOLOGY-MANIFEST-2026.05.05.1",
        "basis_date": CURRENT_REVIEW_DATE,
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
            ),
            export_entry(
                "bank-products-ontology",
                "bank-products",
                results["bank"]["path"],
                results["bank"]["item_count"],
                results["bank"]["product_count"],
                "예금·적금·대출 금리, 한도, 수수료, 우대조건 온톨로지입니다.",
            ),
            export_entry(
                "insurance-products-ontology",
                "insurance-products",
                results["insurance"]["path"],
                results["insurance"]["item_count"],
                results["insurance"]["product_count"],
                "보험료, 보장, 면책, 갱신, 약관 출처 온톨로지입니다.",
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
            "KR-CARD-PRODUCTS-ONTOLOGY-2026.05.05.1",
            "card-products",
            card_items(),
            "card-product",
            "card",
        ),
        "bank": write_export(
            BANK_EXPORT,
            "KR-BANK-PRODUCTS-ONTOLOGY-2026.05.05.1",
            "bank-products",
            bank_items(),
            "bank-product",
            "bank",
        ),
        "insurance": write_export(
            INSURANCE_EXPORT,
            "KR-INSURANCE-PRODUCTS-ONTOLOGY-2026.05.05.1",
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
