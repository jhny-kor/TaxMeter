#!/usr/bin/env python3
"""Import finance products from official disclosure sources.

The first supported source is the Financial Supervisory Service FinLife API.
Set FINLIFE_API_KEY to crawl all supported pages and emit generated ontology
items under ontology/custom/finance/.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import tempfile
import time
from http.cookiejar import CookieJar
import urllib.parse
import urllib.request
from datetime import date
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]
ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "custom" / "finance"
FINLIFE_API_BASE = "https://finlife.fss.or.kr/finlifeapi"
CARDDAMOA_PAGE_URL = "https://gongsi.crefia.or.kr/portal/carddamoa/carddamoaList"
CARDDAMOA_LIST_URL = "https://gongsi.crefia.or.kr/portal/carddamoa/carddamoaList/schList"
COLLECTED_AT = date.today().isoformat()


FINLIFE_GROUPS = {
    "020000": "은행",
    "030200": "여신전문",
    "030300": "저축은행",
    "050000": "보험",
    "060000": "금융투자",
}


FINLIFE_ENDPOINTS = (
    {
        "endpoint": "depositProductsSearch",
        "domain": "bank",
        "product_kind": "deposit",
        "product_type": "bank-product",
        "category": "category.finance.deposit-products",
        "group_codes": ("020000", "030300"),
        "title": "정기예금",
    },
    {
        "endpoint": "savingProductsSearch",
        "domain": "bank",
        "product_kind": "saving",
        "product_type": "bank-product",
        "category": "category.finance.savings-products",
        "group_codes": ("020000", "030300"),
        "title": "적금",
    },
    {
        "endpoint": "mortgageLoanProductsSearch",
        "domain": "bank",
        "product_kind": "mortgage-loan",
        "product_type": "bank-product",
        "category": "category.finance.mortgage-loan-products",
        "group_codes": ("020000", "030200", "030300", "050000"),
        "title": "주택담보대출",
    },
    {
        "endpoint": "rentHouseLoanProductsSearch",
        "domain": "bank",
        "product_kind": "rent-loan",
        "product_type": "bank-product",
        "category": "category.finance.rent-loan-products",
        "group_codes": ("020000", "030200", "030300", "050000"),
        "title": "전세자금대출",
    },
    {
        "endpoint": "creditLoanProductsSearch",
        "domain": "bank",
        "product_kind": "credit-loan",
        "product_type": "bank-product",
        "category": "category.finance.credit-loan-products",
        "group_codes": ("020000", "030200", "030300", "050000"),
        "title": "개인신용대출",
    },
    {
        "endpoint": "annuitySavingProductsSearch",
        "domain": "insurance",
        "product_kind": "annuity-saving",
        "product_type": "insurance-product",
        "category": "category.finance.annuity-insurance-products",
        "group_codes": ("050000", "060000"),
        "title": "연금저축",
    },
)


def slug(value: str) -> str:
    normalized = re.sub(r"[^0-9a-zA-Z가-힣]+", "-", value.strip().lower())
    normalized = re.sub(r"-+", "-", normalized).strip("-")
    return normalized or "unknown"


def unique(values: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        if value and value not in seen:
            seen.add(value)
            result.append(value)
    return result


def fetch_json(endpoint: str, api_key: str, group_code: str, page_no: int, timeout: int) -> dict[str, Any]:
    params = urllib.parse.urlencode(
        {
            "auth": api_key,
            "topFinGrpNo": group_code,
            "pageNo": str(page_no),
        }
    )
    url = f"{FINLIFE_API_BASE}/{endpoint}.json?{params}"
    request = urllib.request.Request(
        url,
        headers={
            "accept": "application/json",
            "user-agent": "opentax-finance-ontology-importer/1.0",
        },
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))


def carddamoa_json(card_type: str, timeout: int) -> dict[str, Any]:
    try:
        return carddamoa_json_with_urllib(card_type, timeout)
    except Exception as exc:
        return carddamoa_json_with_curl(card_type, timeout, exc)


def carddamoa_json_with_urllib(card_type: str, timeout: int) -> dict[str, Any]:
    cookie_jar = CookieJar()
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cookie_jar))
    page_request = urllib.request.Request(
        CARDDAMOA_PAGE_URL,
        headers={
            "accept": "text/html",
            "user-agent": "opentax-finance-ontology-importer/1.0",
        },
    )
    with opener.open(page_request, timeout=timeout) as response:
        html = response.read().decode("utf-8", errors="replace")
    token_match = re.search(r"name=[\"']_csrf[\"']\s+value=[\"']([^\"']+)", html)
    if not token_match:
        raise RuntimeError("Carddamoa CSRF token was not found")
    data = urllib.parse.urlencode({"cardType": card_type}).encode("utf-8")
    list_request = urllib.request.Request(
        CARDDAMOA_LIST_URL,
        data=data,
        headers={
            "accept": "application/json",
            "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
            "user-agent": "opentax-finance-ontology-importer/1.0",
            "x-csrf-token": token_match.group(1),
            "x-requested-with": "XMLHttpRequest",
        },
        method="POST",
    )
    with opener.open(list_request, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))


def carddamoa_json_with_curl(card_type: str, timeout: int, cause: Exception) -> dict[str, Any]:
    with tempfile.TemporaryDirectory() as tmp_dir:
        cookie_path = Path(tmp_dir) / "cookies.txt"
        html = subprocess.run(
            [
                "curl",
                "-sSL",
                "--max-time",
                str(timeout),
                "-c",
                str(cookie_path),
                CARDDAMOA_PAGE_URL,
            ],
            text=True,
            capture_output=True,
            check=False,
        )
        if html.returncode != 0:
            raise RuntimeError(f"Carddamoa page fetch failed after urllib error {cause}: {html.stderr.strip()}")
        token_match = re.search(r"name=[\"']_csrf[\"']\s+value=[\"']([^\"']+)", html.stdout)
        if not token_match:
            raise RuntimeError("Carddamoa CSRF token was not found")
        response = subprocess.run(
            [
                "curl",
                "-sSL",
                "--max-time",
                str(timeout),
                "-b",
                str(cookie_path),
                "-H",
                f"X-CSRF-TOKEN: {token_match.group(1)}",
                "-H",
                "X-Requested-With: XMLHttpRequest",
                "-H",
                "Content-Type: application/x-www-form-urlencoded; charset=UTF-8",
                "-X",
                "POST",
                CARDDAMOA_LIST_URL,
                "-d",
                f"cardType={card_type}",
            ],
            text=True,
            capture_output=True,
            check=False,
        )
        if response.returncode != 0:
            raise RuntimeError(f"Carddamoa list fetch failed: {response.stderr.strip()}")
        return json.loads(response.stdout)


def result_lists(payload: dict[str, Any]) -> tuple[dict[str, Any], list[dict[str, Any]], list[dict[str, Any]]]:
    result = payload.get("result") or {}
    base_list = result.get("baseList") or result.get("baseInfo") or result.get("baseinfo") or []
    option_list = result.get("optionList") or result.get("options") or []
    if isinstance(base_list, dict):
        base_list = [base_list]
    if isinstance(option_list, dict):
        option_list = [option_list]
    return result, list(base_list), list(option_list)


def number_or_none(value: Any) -> float | int | None:
    if value in (None, ""):
        return None
    if isinstance(value, (int, float)):
        return value
    text = str(value).replace(",", "").strip()
    try:
        number = float(text)
    except ValueError:
        return None
    if number.is_integer():
        return int(number)
    return number


def amount_or_none(value: Any) -> int | None:
    number = number_or_none(value)
    if isinstance(number, (int, float)):
        return int(number)
    return None


def rate_criteria(option: dict[str, Any], source_id: str) -> list[dict[str, Any]]:
    criteria: list[dict[str, Any]] = []
    for key, label in (
        ("intr_rate", "기본금리"),
        ("intr_rate2", "최고우대금리"),
        ("lend_rate_min", "최저금리"),
        ("lend_rate_max", "최고금리"),
        ("avg_rate", "평균금리"),
    ):
        rate = number_or_none(option.get(key))
        if rate is None:
            continue
        criteria.append(
            {
                "label": label,
                "basis": option.get("save_trm") or option.get("rpay_type_nm") or option.get("crdt_prdt_type_nm") or "공시 옵션",
                "condition": f"{label} {rate}%",
                "source": source_id,
                "criteria_kind": "rate",
                "basis_category": "금융상품 공시 금리",
                "basis_definition": "금융감독원 금융상품한눈에 API의 상품 옵션 금리 필드입니다.",
                "basis_lookup": "finlifeapi optionList에서 상품코드와 옵션 조건을 기준으로 확인합니다.",
                "selection_rule": "동일 상품의 기간, 상환방식, 금리유형별 옵션으로 분리합니다.",
                "basis_source": source_id,
                "rate_percent": rate,
                "rate_label": label,
                "rate_basis": option.get("intr_rate_type_nm") or option.get("lend_rate_type_nm") or "공시 옵션",
            }
        )
    return criteria


def benefit_criteria(text: str, source_id: str) -> list[dict[str, Any]]:
    cleaned = re.sub(r"\s+", " ", text or "").strip()
    if not cleaned:
        return []
    criterion: dict[str, Any] = {
        "label": "카드 혜택",
        "basis": "카드다모아 주요혜택",
        "condition": cleaned,
        "source": source_id,
        "criteria_kind": "product-benefit",
        "basis_category": "카드상품 혜택",
        "basis_definition": "여신금융협회 카드다모아가 카드사 주력상품별로 공시한 주요 혜택 설명입니다.",
        "basis_lookup": "카드다모아 resultList의 itemBenefit 필드입니다.",
        "selection_rule": "동일 카드상품의 혜택 설명을 원문 중심으로 보존하고, 퍼센트가 명시된 경우 rate_percent도 함께 기록합니다.",
        "basis_source": source_id,
        "benefit": cleaned,
    }
    rate_match = re.search(r"(\d+(?:\.\d+)?)\s*%", cleaned)
    if rate_match:
        criterion["rate_percent"] = float(rate_match.group(1))
        criterion["rate_label"] = "혜택률"
        criterion["rate_basis"] = "카드다모아 주요혜택 문구"
    return [criterion]


def limit_criteria(base: dict[str, Any], source_id: str) -> list[dict[str, Any]]:
    criteria: list[dict[str, Any]] = []
    max_limit = amount_or_none(base.get("max_limit") or base.get("loan_lmt"))
    if max_limit is not None:
        criteria.append(
            {
                "label": "가입·대출 한도",
                "basis": "금융상품 공시 한도",
                "condition": f"최고 한도 {max_limit:,}원",
                "source": source_id,
                "criteria_kind": "limit",
                "basis_category": "금융상품 한도",
                "basis_definition": "금융상품별 가입금액 또는 대출금액 상한입니다.",
                "basis_lookup": "finlifeapi baseList의 max_limit 또는 loan_lmt 필드입니다.",
                "selection_rule": "상품별 공시 한도를 그대로 보존합니다.",
                "basis_source": source_id,
                "limit_krw": max_limit,
            }
        )
    return criteria


def status_from_base(base: dict[str, Any]) -> str:
    end_day = str(base.get("dcls_end_day") or "").strip()
    if end_day and end_day not in {"99991231", "99999999"}:
        return "ended"
    return "active"


def item_from_finlife(config: dict[str, Any], group_code: str, base: dict[str, Any], options: list[dict[str, Any]]) -> dict:
    product_code = str(base.get("fin_prdt_cd") or base.get("fin_prdt_nm") or "unknown")
    provider_code = str(base.get("fin_co_no") or "unknown")
    provider = str(base.get("kor_co_nm") or "금융회사 미상")
    product_name = str(base.get("fin_prdt_nm") or "상품명 미상")
    source_id = "source.fss.finlife.api"
    item_id = f"finance.{config['domain']}.{config['product_kind']}.{slug(provider_code)}.{slug(product_code)}"
    criteria: list[dict[str, Any]] = limit_criteria(base, source_id)
    for option in options:
        criteria.extend(rate_criteria(option, source_id))
    if base.get("join_member"):
        criteria.append(
            {
                "label": "가입대상",
                "basis": "금융상품 공시 가입대상",
                "condition": str(base["join_member"]),
                "source": source_id,
                "criteria_kind": "eligibility",
                "basis_category": "가입대상",
                "basis_definition": "금융상품 판매사가 공시한 가입 가능 대상입니다.",
                "basis_lookup": "finlifeapi baseList의 join_member 필드입니다.",
                "selection_rule": "상품 가입 가능 여부의 기본 요건으로 사용합니다.",
                "basis_source": source_id,
                "benefit": str(base["join_member"]),
            }
        )
    return {
        "id": item_id,
        "title": f"{provider} {product_name}",
        "type": config["product_type"],
        "description": f"{provider}의 {config['title']} 상품 '{product_name}' 공시 정보입니다.",
        "basis_year": int(COLLECTED_AT[:4]),
        "reviewed_at": COLLECTED_AT,
        "abolition_status": "active" if status_from_base(base) == "active" else "sunset",
        "revision_status": "check_source",
        "parents": [config["category"]],
        "children": [],
        "related": [],
        "terms": [],
        "deadlines": [],
        "sources": [source_id],
        "tags": unique(["finance-product", "generated", config["domain"], config["product_kind"], group_code]),
        "criteria": criteria,
        "provider": provider,
        "provider_code": provider_code,
        "financial_sector": FINLIFE_GROUPS.get(group_code, group_code),
        "product_code": product_code,
        "product_kind": config["product_kind"],
        "product_status": status_from_base(base),
        "sales_status": status_from_base(base),
        "disclosure_month": base.get("dcls_month"),
        "collected_at": COLLECTED_AT,
        "source_api": f"{FINLIFE_API_BASE}/{config['endpoint']}.json",
        "source_record_id": f"{config['endpoint']}:{group_code}:{provider_code}:{product_code}",
        "source_urls": ["https://finlife.fss.or.kr/", f"{FINLIFE_API_BASE}/{config['endpoint']}.json"],
        "source_basis_dates": [f"{COLLECTED_AT} 수집", str(base.get("dcls_month") or "")],
        "raw": base,
        "options": options,
    }


def item_from_carddamoa(card_type: str, record: dict[str, Any]) -> dict:
    product_kind = "credit-card" if card_type == "01" else "check-card"
    product_type_label = "신용카드" if card_type == "01" else "체크카드"
    category_id = "category.finance.credit-cards" if card_type == "01" else "category.finance.check-cards"
    provider = str(record.get("companyNm") or "카드사 미상").strip()
    item_name = str(record.get("itemName") or "카드상품명 미상").strip()
    provider_code = slug(provider)
    product_code = slug(item_name)
    source_id = "source.crefia.carddamoa"
    criteria = benefit_criteria(str(record.get("itemBenefit") or ""), source_id)
    if record.get("itemCharacteristic"):
        criteria.extend(benefit_criteria(str(record.get("itemCharacteristic")), source_id))
    return {
        "id": f"finance.card.{product_kind}.{provider_code}.{product_code}",
        "title": f"{provider} {item_name}",
        "type": "card-product",
        "description": f"여신금융협회 카드다모아에 공시된 {provider}의 {product_type_label} 상품 '{item_name}'입니다.",
        "basis_year": int(COLLECTED_AT[:4]),
        "reviewed_at": COLLECTED_AT,
        "abolition_status": "active",
        "revision_status": "check_source",
        "parents": [category_id],
        "children": [],
        "related": [],
        "terms": ["term.card.previous-month-spend", "term.card.monthly-benefit-limit", "term.card.excluded-spend"],
        "deadlines": [],
        "sources": [source_id, "source.crefia.card-products"],
        "tags": ["finance-product", "generated", "card-products", product_kind],
        "criteria": criteria,
        "provider": provider,
        "provider_code": provider_code,
        "financial_sector": "카드",
        "product_code": product_code,
        "product_kind": product_kind,
        "product_status": "active",
        "sales_status": "active",
        "disclosure_month": None,
        "collected_at": COLLECTED_AT,
        "source_api": CARDDAMOA_LIST_URL,
        "source_record_id": f"carddamoa:{card_type}:{provider_code}:{product_code}",
        "source_urls": [CARDDAMOA_PAGE_URL, str(record.get("itemLink") or "")],
        "source_basis_dates": [f"{COLLECTED_AT} 수집"],
        "benefits": [
            {"kind": "main", "text": record.get("itemBenefit")},
            {"kind": "characteristic", "text": record.get("itemCharacteristic")},
        ],
        "raw": record,
    }


def crawl_carddamoa(timeout: int) -> list[dict]:
    items: dict[str, dict] = {}
    for card_type in ("01", "02"):
        payload = carddamoa_json(card_type, timeout)
        for record in payload.get("resultList") or []:
            item = item_from_carddamoa(card_type, record)
            items[item["id"]] = item
    return sorted(items.values(), key=lambda item: item["id"])


def crawl_finlife(api_key: str, *, timeout: int, sleep_seconds: float, limit_pages: int | None) -> dict[str, list[dict]]:
    by_domain: dict[str, dict[str, dict]] = {"bank": {}, "insurance": {}}
    for config in FINLIFE_ENDPOINTS:
        for group_code in config["group_codes"]:
            page_no = 1
            while True:
                payload = fetch_json(config["endpoint"], api_key, group_code, page_no, timeout)
                result, base_list, option_list = result_lists(payload)
                err_cd = str(result.get("err_cd") or "000")
                if err_cd not in {"000", "0"}:
                    raise RuntimeError(f"{config['endpoint']} {group_code} page {page_no}: {err_cd} {result.get('err_msg')}")
                options_by_key: dict[tuple[str, str], list[dict[str, Any]]] = {}
                for option in option_list:
                    key = (str(option.get("fin_co_no") or ""), str(option.get("fin_prdt_cd") or ""))
                    options_by_key.setdefault(key, []).append(option)
                for base in base_list:
                    key = (str(base.get("fin_co_no") or ""), str(base.get("fin_prdt_cd") or ""))
                    item = item_from_finlife(config, group_code, base, options_by_key.get(key, []))
                    by_domain[config["domain"]][item["id"]] = item
                max_page = int(result.get("max_page_no") or page_no)
                if page_no >= max_page:
                    break
                if limit_pages is not None and page_no >= limit_pages:
                    break
                page_no += 1
                if sleep_seconds:
                    time.sleep(sleep_seconds)
    return {domain: sorted(items.values(), key=lambda item: item["id"]) for domain, items in by_domain.items()}


def write_generated(domain: str, items: list[dict]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    path = OUT_DIR / f"{domain}-products.generated.json"
    payload = {
        "version": f"FINLIFE-{domain.upper()}-PRODUCTS-{COLLECTED_AT}",
        "source": "https://finlife.fss.or.kr/finlifeapi/",
        "collected_at": COLLECTED_AT,
        "item_count": len(items),
        "items": items,
    }
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {path.relative_to(REPO_ROOT)} ({len(items)} items)")


def main() -> int:
    parser = argparse.ArgumentParser(description="Import finance products from official disclosure APIs")
    parser.add_argument("--limit-pages", type=int, default=None, help="Limit pages per endpoint/group for smoke tests")
    parser.add_argument("--timeout", type=int, default=30)
    parser.add_argument("--sleep", type=float, default=0.2)
    parser.add_argument("--skip-carddamoa", action="store_true", help="Skip 여신금융협회 카드다모아 crawl")
    parser.add_argument("--skip-finlife", action="store_true", help="Skip 금융감독원 FinLife API crawl")
    args = parser.parse_args()

    imported_any = False
    if not args.skip_carddamoa:
        card_items = crawl_carddamoa(args.timeout)
        write_generated("card", card_items)
        imported_any = True

    api_key = os.environ.get("FINLIFE_API_KEY", "").strip()
    if not args.skip_finlife and api_key:
        imported = crawl_finlife(api_key, timeout=args.timeout, sleep_seconds=args.sleep, limit_pages=args.limit_pages)
        write_generated("bank", imported.get("bank", []))
        write_generated("insurance", imported.get("insurance", []))
        imported_any = True
    elif not args.skip_finlife:
        print("FINLIFE_API_KEY is not set; skipped Financial Supervisory Service FinLife API crawl.", file=sys.stderr)

    if not imported_any:
        print("No finance source was imported.", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
