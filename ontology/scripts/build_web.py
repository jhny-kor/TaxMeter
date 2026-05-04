#!/usr/bin/env python3
"""Build the static web guide for OpenTax."""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from textwrap import dedent


REPO_ROOT = Path(__file__).resolve().parents[2]
ONTOLOGY_ROOT = REPO_ROOT / "ontology"
EXPORT_PATH = ONTOLOGY_ROOT / "exports" / "korea-tax-ontology-2026.json"
WEB_ROOT = REPO_ROOT / "docs" / "opentax"


TYPE_LABELS = {
    "domain": "도메인",
    "category": "카테고리",
    "tax": "세목",
    "deduction": "소득공제",
    "tax-credit": "세액공제",
    "tax-reduction": "세액감면",
    "corporate-tax-support": "법인세 지원",
    "support-program": "정책지원",
    "filing": "신고 절차",
    "scenario": "사용자 경로",
    "life-expense": "생활비 표현",
    "life-income": "생활소득 표현",
    "life-event": "생활사건 표현",
    "official-tax-item": "공식 항목",
    "eligibility-rule": "요건 규칙",
    "required-document": "필요서류",
    "application-channel": "신청 경로",
    "conflict-rule": "충돌 규칙",
    "concept": "판정 개념",
    "term": "용어",
    "deadline": "기한",
    "source": "공식 출처",
}


MAJOR_NODES = [
    ("category.national-taxes", "national", "국세", "12 세목"),
    ("category.local-taxes", "local", "지방세", "11 세목"),
    ("category.customs", "customs", "관세", "별도 영역"),
    ("category.deductions-and-reliefs", "relief", "공제·감면", "소득·세액·법인"),
    ("category.policy-supports", "support", "정책지원", "장려금·계좌·금융"),
    ("category.business-tax-compliance", "business", "사업자 세무", "등록·VAT·원천세"),
    ("category.filing-calendar", "filing", "신고기한", "신청·납부·지급"),
]


def load_export() -> dict:
    return json.loads(EXPORT_PATH.read_text(encoding="utf-8"))


def summarize(data: dict) -> dict:
    items = data["items"]
    counts = Counter(item["type"] for item in items)
    relation_count = sum(
        len(item.get(key, []))
        for item in items
        for key in ("parents", "children", "related", "terms", "deadlines", "sources")
    )
    return {
        "item_count": len(items),
        "source_count": counts["source"],
        "term_count": counts["term"],
        "category_count": counts["category"],
        "deadline_count": counts["deadline"],
        "scenario_count": counts["scenario"],
        "life_language_count": counts["life-expense"] + counts["life-income"] + counts["life-event"],
        "rule_count": counts["eligibility-rule"] + counts["conflict-rule"],
        "support_count": counts["support-program"],
        "business_count": 4,
        "relation_count": relation_count,
        "national_tax_count": len(data["manifests"]["national_tax_ids"]),
        "local_tax_count": len(data["manifests"]["local_tax_ids"]),
        "corporate_support_count": len(data["manifests"]["corporate_support_ids"]),
        "type_counts": dict(sorted(counts.items())),
    }


def item_map(data: dict) -> dict[str, dict]:
    return {item["id"]: item for item in data["items"]}


def child_count(items_by_id: dict[str, dict], item_id: str) -> int:
    return len(items_by_id.get(item_id, {}).get("children", []))


def graph_node_html(item_id: str, class_name: str, label: str, meta: str) -> str:
    return (
        f'<button class="graph-node {class_name}" type="button" data-select-item="{item_id}">'
        f"<strong>{label}</strong><span>{meta}</span></button>"
    )


def build_html(data: dict, summary: dict) -> str:
    version = data["version"]
    basis_date = data["basis_date"]
    items_by_id = item_map(data)
    major_nodes = "\n".join(graph_node_html(*node) for node in MAJOR_NODES)
    policy_count = child_count(items_by_id, "category.policy-supports")
    filing_count = child_count(items_by_id, "category.filing-calendar")
    business_count = child_count(items_by_id, "category.business-tax-compliance")

    return dedent(
        f"""\
        <!doctype html>
        <html lang="ko">
        <head>
          <meta charset="utf-8">
          <meta name="viewport" content="width=device-width, initial-scale=1">
          <title>OpenTax</title>
          <meta name="description" content="대한민국 세금, 공제, 정책지원, 사업자 세무, 신고기한을 연결한 검증형 OpenTax 웹 가이드">
          <link rel="stylesheet" href="./styles.css">
        </head>
        <body>
          <header class="site-header">
            <a class="brand" href="#top" aria-label="OpenTax 홈">
              <span class="brand-mark" aria-hidden="true">
                <svg viewBox="0 0 32 32" role="img">
                  <path d="M16 3.5 27 9.8v12.4l-11 6.3-11-6.3V9.8L16 3.5Z" fill="none" stroke="currentColor" stroke-width="2"/>
                  <path d="M10 16h12M16 10v12" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
                </svg>
              </span>
              <span>OpenTax</span>
            </a>
            <nav class="top-nav" aria-label="주요 섹션">
              <a href="#overview">개요</a>
              <a href="#graph">그래프</a>
              <a href="#flow">데이터 흐름</a>
              <a href="#roadmap">로드맵</a>
              <a href="#browser">탐색</a>
            </nav>
          </header>

          <main id="top">
            <section class="hero section" id="overview">
              <div class="hero-copy">
                <h1>OpenTax</h1>
                <p class="hero-lede">
                  흩어진 세법, 국세청 안내, 정책지원, 사업자 세무, 신고기한을
                  <strong>검증 가능한 지식 그래프</strong>로 묶어 OpenTax가 바로 탐색하고
                  재사용할 수 있는 데이터 표면으로 만듭니다.
                </p>
                <div class="hero-actions">
                  <a class="button primary" href="#graph">그래프 탐색</a>
                  <button class="button secondary" type="button" data-download-json>JSON export</button>
                </div>
                <dl class="hero-meta">
                  <div><dt>version</dt><dd>{version}</dd></div>
                  <div><dt>basis date</dt><dd>{basis_date}</dd></div>
                </dl>
              </div>

              <div class="graph-panel hero-graph" aria-label="온톨로지 상위 그래프">
                <button class="graph-node root" type="button" data-select-item="kr-tax-system">
                  <strong>OpenTax</strong>
                  <span>{summary["item_count"]} nodes</span>
                </button>
                {major_nodes}
                <svg class="graph-lines" viewBox="0 0 720 460" aria-hidden="true">
                  <path d="M360 224 C280 112 217 82 114 82"/>
                  <path d="M360 224 C356 95 448 72 574 82"/>
                  <path d="M360 224 C205 198 154 202 78 228"/>
                  <path d="M360 224 C500 184 552 188 642 222"/>
                  <path d="M360 224 C236 300 184 342 108 374"/>
                  <path d="M360 224 C365 348 430 384 574 374"/>
                  <path d="M360 224 C470 292 520 314 650 330"/>
                </svg>
              </div>
            </section>

            <section class="metrics section" aria-label="온톨로지 요약 수치">
              <div><strong>{summary["item_count"]}</strong><span>검증 노드</span></div>
              <div><strong>{summary["national_tax_count"]}</strong><span>국세 세목</span></div>
              <div><strong>{summary["local_tax_count"]}</strong><span>지방세 세목</span></div>
              <div><strong>{summary["corporate_support_count"]}</strong><span>법인세 지원</span></div>
              <div><strong>{summary["scenario_count"]}</strong><span>사용자 경로</span></div>
              <div><strong>{summary["life_language_count"]}</strong><span>생활어</span></div>
              <div><strong>{summary["source_count"]}</strong><span>공식 출처</span></div>
            </section>

            <section class="section split-section" aria-labelledby="why-title">
              <div class="section-heading">
                <h2 id="why-title">흩어진 세금 정보 vs 그래프</h2>
                <p>레퍼런스 사이트의 핵심처럼, 이 페이지도 단순 소개가 아니라 “왜 필요한지”와 “어떻게 쓰는지”를 먼저 보여줍니다.</p>
              </div>
              <div class="comparison-grid">
                <article>
                  <h3>흩어진 정보</h3>
                  <ul>
                    <li>세목, 공제, 지원금, 신고기한이 기관별 페이지에 분산됩니다.</li>
                    <li>금액 기준과 적용 대상이 본문 안에 숨어 있어 앱에서 재사용하기 어렵습니다.</li>
                    <li>법령·행정안내의 변경 시점과 출처 확인이 수작업으로 남습니다.</li>
                  </ul>
                </article>
                <article>
                  <h3>온톨로지 표면</h3>
                  <ul>
                    <li>세목, 제도, 용어, 기한, 출처를 ID 기반 노드로 분해합니다.</li>
                    <li>상위·하위·관련·용어·출처 링크로 설명 가능한 탐색 경로를 만듭니다.</li>
                    <li>Obsidian vault, MCP 검색, JSON export, 웹 UI가 같은 데이터를 씁니다.</li>
                  </ul>
                </article>
              </div>
            </section>

            <section class="section graph-section" id="graph" aria-labelledby="graph-title">
              <div class="section-heading">
                <h2 id="graph-title">큰 노드 그래프</h2>
                <p>현재 루트가 직접 연결하는 주요 카테고리입니다. 각 노드를 누르면 아래 탐색기의 상세 패널로 이동합니다.</p>
              </div>
              <div class="major-map">
                <div class="map-core">
                  <strong>kr-tax-system</strong>
                  <span>OpenTax</span>
                </div>
                <button class="map-node national" data-select-item="category.national-taxes"><strong>국세</strong><span>{summary["national_tax_count"]} 세목</span></button>
                <button class="map-node local" data-select-item="category.local-taxes"><strong>지방세</strong><span>{summary["local_tax_count"]} 세목</span></button>
                <button class="map-node customs" data-select-item="category.customs"><strong>관세</strong><span>수입물품 조세</span></button>
                <button class="map-node relief" data-select-item="category.deductions-and-reliefs"><strong>공제·감면</strong><span>4개 묶음</span></button>
                <button class="map-node support" data-select-item="category.policy-supports"><strong>정책지원</strong><span>{policy_count} 항목</span></button>
                <button class="map-node business" data-select-item="category.business-tax-compliance"><strong>사업자 세무</strong><span>{business_count} 흐름</span></button>
                <button class="map-node filing" data-select-item="category.filing-calendar"><strong>신고기한</strong><span>{filing_count} 기한</span></button>
                <svg viewBox="0 0 980 460" aria-hidden="true">
                  <path d="M490 220 172 90"/>
                  <path d="M490 220 490 68"/>
                  <path d="M490 220 812 90"/>
                  <path d="M490 220 160 360"/>
                  <path d="M490 220 402 382"/>
                  <path d="M490 220 624 382"/>
                  <path d="M490 220 824 354"/>
                </svg>
              </div>
            </section>

            <section class="section intro-grid" aria-labelledby="what-you-get">
              <div class="section-heading">
                <h2 id="what-you-get">What You Get</h2>
                <p>현재 export 기준으로 웹에 노출해야 할 핵심 표면을 다시 정리했습니다.</p>
              </div>
              <div class="feature-grid">
                <article class="feature-card">
                  <span class="feature-icon" aria-hidden="true">01</span>
                  <h3>완전성 매니페스트</h3>
                  <p>국세 12개, 지방세 11개, 법인세 지원 28개는 검증기에서 고정 목록으로 확인합니다.</p>
                </article>
                <article class="feature-card">
                  <span class="feature-icon" aria-hidden="true">02</span>
                  <h3>정책지원 확장</h3>
                  <p>근로·자녀장려금뿐 아니라 주거, 금융, 채무조정, 자산형성 지원까지 지원제도 묶음을 넓혔습니다.</p>
                </article>
                <article class="feature-card">
                  <span class="feature-icon" aria-hidden="true">03</span>
                  <h3>사업자 세무 흐름</h3>
                  <p>사업자등록, 간이과세, 부가가치세, 원천세처럼 실무자가 먼저 확인하는 절차 노드를 별도 축으로 둡니다.</p>
                </article>
                <article class="feature-card">
                  <span class="feature-icon" aria-hidden="true">04</span>
                  <h3>기준 내역과 출처</h3>
                  <p>금액, 세율, 한도 같은 기준은 상세 패널에서 criteria로 노출하고, 각 기준은 출처 노드로 추적합니다.</p>
                </article>
              </div>
            </section>

            <section class="section flow" id="flow" aria-labelledby="flow-title">
              <div class="section-heading">
                <h2 id="flow-title">데이터 흐름</h2>
                <p>레퍼런스의 아키텍처 섹션처럼, 이 사이트도 “어디서 와서 어디에 쓰이는지”를 명시합니다.</p>
              </div>
              <div class="pipeline">
                <div><strong>Definition</strong><span>generate_vault.py + custom overlay</span></div>
                <div><strong>Vault</strong><span>Obsidian notes + graph links</span></div>
                <div><strong>Validation</strong><span>manifest, source, bidirectional links</span></div>
                <div><strong>Export</strong><span>JSON, MCP, Web, App seed</span></div>
              </div>
              <div class="type-table-wrap">
                <table class="type-table">
                  <thead>
                    <tr><th>노드 타입</th><th>개수</th><th>역할</th></tr>
                  </thead>
                  <tbody data-type-table></tbody>
                </table>
              </div>
            </section>

            <section class="section roadmap" id="roadmap" aria-labelledby="roadmap-title">
              <div class="section-heading">
                <h2 id="roadmap-title">검증된 확장 표면</h2>
                <p>세율·한도, 반복기한, 사용자 경로, 선정기준 설명은 생성기와 검증기에서 같은 구조로 관리합니다.</p>
              </div>
              <div class="roadmap-grid">
                <article>
                  <h3>세율·한도 기준의 구조화</h3>
                  <p>종합소득세율, 부가가치세 과세유형, 장려금 소득·재산요건처럼 계산에 쓰이는 값을 criteria 배열로 통일합니다.</p>
                  <span>반영: criteria_kind, rate_percent, limit_krw, threshold_krw, amount_formula 검증</span>
                </article>
                <article>
                  <h3>지원제도 eligibility 흐름</h3>
                  <p>청년도약계좌, 버팀목 전세대출, 근로장려금처럼 대상 조건이 많은 제도는 판정 개념 노드와 조건 그룹으로 분해합니다.</p>
                  <span>반영: concept 노드 생성 → support-program과 related 연결 → 상세 패널에 기준 내역 노출</span>
                </article>
                <article>
                  <h3>신고기한 반복 규칙</h3>
                  <p>월별 원천세, 부가가치세 예정·확정신고, 장려금 정기·반기 신청은 start/end 날짜뿐 아니라 반복 규칙이 필요합니다.</p>
                  <span>반영: deadline 노드별 recurrence.frequency, anchor, due_rule 검증</span>
                </article>
                <article>
                  <h3>변경 이력과 기준일</h3>
                  <p>세법은 매년 바뀌므로 값 변경과 출처 확인일을 노드 단위로 비교할 수 있어야 합니다.</p>
                  <span>반영: basis_date, effective_date, expiration_date를 웹 표와 export diff에 노출</span>
                </article>
                <article>
                  <h3>사용자 사례별 경로</h3>
                  <p>근로자, 개인사업자, 청년, 주택 임차인, 법인 담당자가 자주 묻는 경로를 curated path로 만들면 탐색성이 좋아집니다.</p>
                  <span>반영: scenario 노드와 path_steps target 검증</span>
                </article>
                <article>
                  <h3>앱 기능 매핑</h3>
                  <p>TaxMeter와 다른 클라이언트의 baseline, 위험 신호, 절세 체크리스트가 어떤 OpenTax 노드에 기대는지 표시해야 유지보수가 쉬워집니다.</p>
                  <span>반영: tags에 app-surface 값을 부여하고 브라우저 탭에 “앱 사용처” 필터 추가</span>
                </article>
              </div>
            </section>

            <section class="section browser" id="browser" aria-labelledby="browser-title">
              <div class="section-heading">
                <h2 id="browser-title">온톨로지 탐색</h2>
                <p>검색어, 타입, 상위 카테고리 관계를 기준으로 노드를 빠르게 좁히고 상세 연결을 확인합니다.</p>
              </div>
              <div class="browser-shell">
                <div class="browser-list" aria-label="온톨로지 목록">
                  <div class="browser-toolbar">
                    <label class="search-field">
                      <span class="sr-only">온톨로지 검색</span>
                      <svg viewBox="0 0 24 24" aria-hidden="true">
                        <path d="m21 21-4.3-4.3M10.7 18a7.3 7.3 0 1 1 0-14.6 7.3 7.3 0 0 1 0 14.6Z" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
                      </svg>
                      <input type="search" placeholder="예: 부가가치세, 청년도약계좌, 사업자등록" data-search>
                    </label>
                    <span class="result-count" data-result-count></span>
                  </div>
                  <div class="tabs" data-tabs aria-label="목록 필터"></div>
                  <div class="item-list" data-item-list></div>
                </div>
                <aside class="detail-panel" data-detail-panel aria-live="polite"></aside>
              </div>
            </section>

            <section class="section sources" id="sources" aria-labelledby="sources-title">
              <div class="section-heading">
                <h2 id="sources-title">공식 출처</h2>
                <p>출처 노드는 설명, 발행처, 기준일, URL을 가진 독립 노드입니다. 상세 패널의 기준 내역도 이 출처로 역추적합니다.</p>
              </div>
              <div class="source-list" data-source-list></div>
            </section>

            <section class="section export" id="export" aria-labelledby="export-title">
              <div class="section-heading">
                <h2 id="export-title">JSON Export</h2>
                <p>앱, MCP 서버, 웹 페이지가 동일한 export 파일을 기준으로 움직입니다.</p>
              </div>
              <div class="export-panel">
                <div>
                  <strong>ontology/exports/korea-tax-ontology-2026.json</strong>
                  <span>{version} · {summary["relation_count"]} graph links</span>
                </div>
                <button class="button primary" type="button" data-download-json>JSON 다운로드</button>
              </div>
            </section>
          </main>

          <footer class="site-footer">
            <span>OpenTax</span>
            <nav aria-label="OpenTax 정책 문서">
              <a href="./privacy.html">개인정보처리방침</a>
              <a href="./terms.html">이용약관</a>
              <a href="./support.html">지원</a>
            </nav>
            <span>검증 기준일 {basis_date}</span>
          </footer>

          <script src="./app.js"></script>
        </body>
        </html>
        """
    )


def build_css() -> str:
    return dedent(
        """\
        :root {
          color-scheme: dark;
          --bg: #080b12;
          --bg-2: #0d121c;
          --panel: #101722;
          --panel-2: #141d2a;
          --panel-3: #182333;
          --ink: #f3f7fb;
          --muted: #9aa8b8;
          --faint: #6f7d8e;
          --line: #243142;
          --line-strong: #33465c;
          --cyan: #5ad7ff;
          --blue: #6aa6ff;
          --green: #63d99b;
          --coral: #ff8f70;
          --amber: #f4b95f;
          --violet: #b49cff;
          --shadow: 0 26px 70px rgba(0, 0, 0, 0.34);
          --radius: 8px;
          --max: 1180px;
        }

        * {
          box-sizing: border-box;
        }

        html {
          scroll-behavior: smooth;
          background: var(--bg);
        }

        body {
          margin: 0;
          background:
            linear-gradient(180deg, #0a0f18 0%, #080b12 42%, #0b1018 100%);
          color: var(--ink);
          font-family: -apple-system, BlinkMacSystemFont, "SF Pro Display", "Apple SD Gothic Neo", "Pretendard", "Noto Sans KR", "Segoe UI", sans-serif;
          font-size: 16px;
          line-height: 1.62;
          letter-spacing: 0;
        }

        a {
          color: inherit;
          text-decoration: none;
        }

        button,
        input {
          font: inherit;
          letter-spacing: 0;
        }

        button {
          cursor: pointer;
        }

        .site-header {
          position: sticky;
          top: 0;
          z-index: 20;
          display: flex;
          align-items: center;
          justify-content: space-between;
          gap: 24px;
          min-height: 64px;
          padding: 0 28px;
          background: rgba(8, 11, 18, 0.86);
          border-bottom: 1px solid var(--line);
          backdrop-filter: blur(18px);
        }

        .brand {
          display: inline-flex;
          align-items: center;
          gap: 10px;
          font-weight: 780;
          white-space: nowrap;
        }

        .brand-mark {
          display: grid;
          width: 34px;
          height: 34px;
          place-items: center;
          color: var(--cyan);
          background: #101a27;
          border: 1px solid #294a61;
          border-radius: var(--radius);
        }

        .brand-mark svg {
          width: 22px;
          height: 22px;
        }

        .top-nav {
          display: flex;
          align-items: center;
          gap: 4px;
        }

        .top-nav a {
          padding: 8px 11px;
          color: var(--muted);
          border-radius: 6px;
          font-size: 14px;
          font-weight: 720;
        }

        .top-nav a:hover,
        .top-nav a:focus-visible {
          color: var(--ink);
          background: #141d2a;
          outline: none;
        }

        .section {
          width: min(var(--max), calc(100% - 40px));
          margin: 0 auto;
        }

        .hero {
          display: grid;
          grid-template-columns: minmax(0, 0.86fr) minmax(480px, 1.14fr);
          gap: 52px;
          align-items: center;
          min-height: calc(100vh - 64px);
          padding: 72px 0 48px;
        }

        h1,
        h2,
        h3,
        p {
          margin-top: 0;
        }

        h1 {
          max-width: 9em;
          margin-bottom: 22px;
          font-size: clamp(48px, 7vw, 88px);
          line-height: 0.98;
          font-weight: 850;
        }

        .hero-lede {
          max-width: 650px;
          margin-bottom: 28px;
          color: var(--muted);
          font-size: 19px;
          line-height: 1.76;
        }

        .hero-lede strong {
          color: var(--ink);
          font-weight: 760;
        }

        .hero-actions,
        .browser-toolbar,
        .export-panel {
          display: flex;
          align-items: center;
          gap: 12px;
          flex-wrap: wrap;
        }

        .button {
          display: inline-flex;
          align-items: center;
          justify-content: center;
          min-height: 44px;
          padding: 0 18px;
          border: 1px solid transparent;
          border-radius: 7px;
          font-size: 15px;
          font-weight: 790;
        }

        .button.primary {
          color: #04111b;
          background: var(--cyan);
          box-shadow: 0 16px 36px rgba(90, 215, 255, 0.18);
        }

        .button.primary:hover,
        .button.primary:focus-visible {
          background: #8ae5ff;
          outline: none;
        }

        .button.secondary {
          color: var(--ink);
          background: #111927;
          border-color: var(--line-strong);
        }

        .button.secondary:hover,
        .button.secondary:focus-visible {
          border-color: var(--cyan);
          outline: none;
        }

        .hero-meta {
          display: grid;
          grid-template-columns: repeat(2, minmax(0, 1fr));
          gap: 10px;
          max-width: 650px;
          margin: 28px 0 0;
        }

        .hero-meta div {
          min-width: 0;
          padding: 14px;
          background: rgba(16, 23, 34, 0.74);
          border: 1px solid var(--line);
          border-radius: var(--radius);
        }

        .hero-meta dt {
          margin-bottom: 4px;
          color: var(--faint);
          font-size: 12px;
          font-weight: 780;
          text-transform: uppercase;
        }

        .hero-meta dd {
          margin: 0;
          overflow-wrap: anywhere;
          color: var(--ink);
          font-size: 13px;
          font-weight: 700;
        }

        .graph-panel {
          position: relative;
          min-height: 460px;
          overflow: hidden;
          background: linear-gradient(180deg, rgba(16, 23, 34, 0.96), rgba(11, 16, 24, 0.96));
          border: 1px solid var(--line-strong);
          border-radius: var(--radius);
          box-shadow: var(--shadow);
        }

        .graph-lines,
        .major-map svg {
          position: absolute;
          inset: 0;
          width: 100%;
          height: 100%;
          color: #3c5872;
          pointer-events: none;
        }

        .graph-lines path,
        .major-map path {
          fill: none;
          stroke: currentColor;
          stroke-width: 1.6;
          stroke-dasharray: 4 9;
        }

        .graph-node {
          position: absolute;
          z-index: 2;
          display: flex;
          flex-direction: column;
          align-items: flex-start;
          min-width: 132px;
          padding: 14px 16px;
          color: var(--ink);
          background: #121b29;
          border: 1px solid var(--line-strong);
          border-left: 5px solid var(--blue);
          border-radius: var(--radius);
          box-shadow: 0 18px 42px rgba(0, 0, 0, 0.28);
          text-align: left;
        }

        .graph-node:hover,
        .graph-node:focus-visible,
        .map-node:hover,
        .map-node:focus-visible {
          transform: translateY(-2px);
          border-color: var(--cyan);
          outline: none;
        }

        .graph-node strong,
        .map-node strong {
          font-size: 15px;
          line-height: 1.35;
        }

        .graph-node span,
        .map-node span {
          color: var(--muted);
          font-size: 12px;
          font-weight: 700;
        }

        .graph-node.root {
          top: 188px;
          left: 50%;
          min-width: 178px;
          transform: translateX(-50%);
          border-left-color: var(--cyan);
          background: #0e2030;
        }

        .graph-node.root:hover,
        .graph-node.root:focus-visible {
          transform: translateX(-50%) translateY(-2px);
        }

        .graph-node.national { top: 48px; left: 38px; border-left-color: var(--blue); }
        .graph-node.local { top: 176px; left: 28px; border-left-color: var(--green); }
        .graph-node.support { bottom: 46px; left: 44px; border-left-color: var(--coral); }
        .graph-node.customs { top: 50px; right: 38px; border-left-color: var(--violet); }
        .graph-node.relief { top: 174px; right: 30px; border-left-color: var(--green); }
        .graph-node.business { right: 52px; bottom: 98px; border-left-color: var(--cyan); }
        .graph-node.filing { right: 38px; bottom: 36px; border-left-color: var(--amber); }

        .metrics {
          display: grid;
          grid-template-columns: repeat(6, 1fr);
          gap: 1px;
          overflow: hidden;
          margin-top: -8px;
          background: var(--line);
          border: 1px solid var(--line);
          border-radius: var(--radius);
        }

        .metrics div {
          display: flex;
          min-height: 116px;
          flex-direction: column;
          justify-content: center;
          padding: 22px;
          background: #0f1621;
        }

        .metrics strong {
          color: var(--ink);
          font-size: 39px;
          line-height: 1;
          font-weight: 850;
        }

        .metrics span {
          margin-top: 8px;
          color: var(--muted);
          font-size: 14px;
          font-weight: 730;
        }

        .section-heading {
          max-width: 780px;
          margin-bottom: 28px;
        }

        .section-heading h2 {
          margin-bottom: 10px;
          font-size: clamp(30px, 4vw, 50px);
          line-height: 1.08;
          font-weight: 850;
        }

        .section-heading p {
          color: var(--muted);
          font-size: 17px;
          line-height: 1.72;
        }

        .split-section,
        .graph-section,
        .intro-grid,
        .flow,
        .roadmap,
        .browser,
        .sources,
        .export {
          padding: 96px 0 0;
        }

        .comparison-grid,
        .feature-grid,
        .roadmap-grid {
          display: grid;
          grid-template-columns: repeat(2, minmax(0, 1fr));
          gap: 14px;
        }

        .feature-grid,
        .roadmap-grid {
          grid-template-columns: repeat(3, 1fr);
        }

        .comparison-grid article,
        .feature-card,
        .roadmap-grid article {
          padding: 22px;
          background: #101722;
          border: 1px solid var(--line);
          border-radius: var(--radius);
        }

        .comparison-grid h3,
        .feature-card h3,
        .roadmap-grid h3 {
          margin-bottom: 12px;
          font-size: 20px;
          line-height: 1.28;
        }

        .comparison-grid ul {
          display: grid;
          gap: 10px;
          margin: 0;
          padding-left: 18px;
          color: var(--muted);
        }

        .feature-card {
          min-height: 238px;
        }

        .feature-icon {
          display: inline-flex;
          margin-bottom: 28px;
          color: var(--cyan);
          font-size: 13px;
          font-weight: 850;
        }

        .feature-card p,
        .roadmap-grid p {
          color: var(--muted);
          font-size: 15px;
        }

        .roadmap-grid span {
          display: block;
          margin-top: 14px;
          color: var(--green);
          font-size: 13px;
          font-weight: 730;
          line-height: 1.55;
        }

        .major-map {
          position: relative;
          min-height: 460px;
          overflow: hidden;
          background: #101722;
          border: 1px solid var(--line-strong);
          border-radius: var(--radius);
          box-shadow: var(--shadow);
        }

        .map-core,
        .map-node {
          position: absolute;
          z-index: 2;
          display: flex;
          flex-direction: column;
          justify-content: center;
          min-height: 72px;
          padding: 15px 17px;
          background: #121b29;
          border: 1px solid var(--line-strong);
          border-radius: var(--radius);
          color: var(--ink);
          text-align: left;
        }

        .map-core {
          top: 184px;
          left: 50%;
          width: 230px;
          min-height: 92px;
          transform: translateX(-50%);
          background: #0d2233;
          border-color: #326079;
        }

        .map-node {
          width: 170px;
        }

        .map-node.national { top: 48px; left: 74px; border-left: 5px solid var(--blue); }
        .map-node.local { top: 44px; left: 50%; transform: translateX(-50%); border-left: 5px solid var(--green); }
        .map-node.local:hover { transform: translateX(-50%) translateY(-2px); }
        .map-node.customs { top: 48px; right: 74px; border-left: 5px solid var(--violet); }
        .map-node.relief { bottom: 46px; left: 66px; border-left: 5px solid var(--green); }
        .map-node.support { bottom: 42px; left: 36%; border-left: 5px solid var(--coral); }
        .map-node.business { bottom: 42px; right: 30%; border-left: 5px solid var(--cyan); }
        .map-node.filing { bottom: 50px; right: 60px; border-left: 5px solid var(--amber); }

        .pipeline {
          display: grid;
          grid-template-columns: repeat(4, 1fr);
          gap: 1px;
          overflow: hidden;
          margin-bottom: 20px;
          background: var(--line);
          border: 1px solid var(--line);
          border-radius: var(--radius);
        }

        .pipeline div {
          display: flex;
          min-height: 116px;
          flex-direction: column;
          justify-content: center;
          padding: 18px;
          background: #101722;
        }

        .pipeline strong {
          font-size: 17px;
        }

        .pipeline span {
          color: var(--muted);
          font-size: 14px;
        }

        .type-table-wrap,
        .browser-shell,
        .source-list,
        .export-panel {
          background: #101722;
          border: 1px solid var(--line);
          border-radius: var(--radius);
          box-shadow: 0 18px 48px rgba(0, 0, 0, 0.22);
        }

        .type-table-wrap {
          overflow-x: auto;
        }

        table {
          width: 100%;
          border-collapse: collapse;
        }

        th,
        td {
          padding: 15px 18px;
          border-bottom: 1px solid var(--line);
          text-align: left;
          vertical-align: top;
        }

        th {
          color: var(--muted);
          background: #0d141f;
          font-size: 13px;
          font-weight: 820;
        }

        td {
          font-size: 14px;
        }

        td span {
          color: var(--faint);
        }

        tr:last-child td {
          border-bottom: 0;
        }

        .browser-shell {
          display: grid;
          grid-template-columns: minmax(0, 1.05fr) minmax(360px, 0.95fr);
          overflow: hidden;
          min-height: 700px;
        }

        .browser-list {
          border-right: 1px solid var(--line);
        }

        .browser-toolbar {
          padding: 18px;
          border-bottom: 1px solid var(--line);
        }

        .search-field {
          display: flex;
          align-items: center;
          flex: 1 1 300px;
          min-width: 260px;
          height: 46px;
          gap: 10px;
          padding: 0 13px;
          color: var(--muted);
          background: #0c121b;
          border: 1px solid var(--line-strong);
          border-radius: 7px;
        }

        .search-field svg {
          width: 18px;
          height: 18px;
          flex: 0 0 auto;
        }

        .search-field input {
          width: 100%;
          min-width: 0;
          color: var(--ink);
          background: transparent;
          border: 0;
          outline: 0;
          font-size: 15px;
        }

        .search-field input::placeholder {
          color: #6e7c8d;
        }

        .result-count {
          color: var(--muted);
          font-size: 14px;
          font-weight: 740;
          white-space: nowrap;
        }

        .tabs {
          display: flex;
          gap: 8px;
          overflow-x: auto;
          padding: 14px 18px;
          border-bottom: 1px solid var(--line);
        }

        .tab-button {
          flex: 0 0 auto;
          min-height: 34px;
          padding: 0 12px;
          color: var(--muted);
          background: #111927;
          border: 1px solid var(--line-strong);
          border-radius: 6px;
          font-size: 13px;
          font-weight: 780;
        }

        .tab-button[aria-selected="true"] {
          color: #04111b;
          background: var(--cyan);
          border-color: var(--cyan);
        }

        .item-list {
          max-height: 608px;
          overflow: auto;
        }

        .item-row {
          display: grid;
          grid-template-columns: minmax(0, 1fr) auto;
          gap: 12px;
          width: 100%;
          padding: 17px 18px;
          color: var(--ink);
          background: #101722;
          border: 0;
          border-bottom: 1px solid var(--line);
          text-align: left;
        }

        .item-row:hover,
        .item-row:focus-visible {
          background: #141d2a;
          outline: none;
        }

        .item-row.active {
          background: #102538;
        }

        .item-row strong {
          display: block;
          overflow-wrap: anywhere;
          font-size: 15px;
          line-height: 1.35;
        }

        .item-row p {
          display: -webkit-box;
          overflow: hidden;
          margin: 6px 0 0;
          color: var(--muted);
          font-size: 13px;
          line-height: 1.5;
          -webkit-box-orient: vertical;
          -webkit-line-clamp: 2;
        }

        .type-chip {
          align-self: start;
          padding: 4px 8px;
          color: var(--cyan);
          background: #0c2030;
          border: 1px solid #274d63;
          border-radius: 6px;
          font-size: 12px;
          font-weight: 790;
          white-space: nowrap;
        }

        .empty-state {
          padding: 28px 18px;
          color: var(--muted);
          font-size: 14px;
          font-weight: 720;
        }

        .detail-panel {
          padding: 24px;
          background: #0d141f;
        }

        .detail-kicker {
          margin-bottom: 8px;
          color: var(--cyan);
          font-size: 13px;
          font-weight: 840;
        }

        .detail-panel h3 {
          margin-bottom: 12px;
          font-size: 28px;
          line-height: 1.18;
        }

        .detail-panel p {
          color: var(--muted);
        }

        .meta-grid {
          display: grid;
          grid-template-columns: repeat(2, minmax(0, 1fr));
          gap: 10px;
          margin: 20px 0;
        }

        .meta-grid div,
        .criteria-block,
        .relation-group,
        .source-card {
          padding: 14px;
          background: #101722;
          border: 1px solid var(--line);
          border-radius: var(--radius);
        }

        .meta-grid span {
          display: block;
          color: var(--muted);
          font-size: 12px;
          font-weight: 780;
        }

        .meta-grid strong {
          display: block;
          margin-top: 4px;
          overflow-wrap: anywhere;
          font-size: 14px;
        }

        .relations {
          display: grid;
          gap: 10px;
        }

        .criteria-block {
          margin: 0 0 16px;
        }

        .criteria-block h4,
        .relation-group h4 {
          margin: 0 0 10px;
          color: var(--muted);
          font-size: 13px;
        }

        .criteria-block ul {
          display: grid;
          gap: 10px;
          margin: 0;
          padding: 0;
          list-style: none;
        }

        .criteria-block li {
          display: grid;
          gap: 6px;
          padding: 10px;
          background: #0c121b;
          border: 1px solid var(--line);
          border-radius: 7px;
        }

        .criteria-block li > strong {
          font-size: 14px;
        }

        .criteria-block li div {
          display: flex;
          flex-wrap: wrap;
          gap: 6px;
        }

        .criteria-block li div span {
          padding: 4px 7px;
          color: var(--muted);
          background: #121b29;
          border: 1px solid var(--line);
          border-radius: 6px;
          font-size: 12px;
        }

        .criteria-block li div span strong {
          color: var(--ink);
        }

        .criteria-block li p {
          margin: 0;
        }

        .relation-links {
          display: flex;
          flex-wrap: wrap;
          gap: 6px;
        }

        .relation-link {
          max-width: 100%;
          padding: 5px 8px;
          color: var(--ink);
          background: #121b29;
          border: 1px solid var(--line-strong);
          border-radius: 6px;
          font-size: 12px;
          font-weight: 720;
          overflow-wrap: anywhere;
        }

        .relation-link:hover,
        .relation-link:focus-visible {
          color: var(--cyan);
          border-color: var(--cyan);
          outline: none;
        }

        .source-list {
          display: grid;
          grid-template-columns: repeat(3, 1fr);
          gap: 1px;
          overflow: hidden;
          background: var(--line);
        }

        .source-card {
          min-height: 184px;
          border: 0;
          border-radius: 0;
        }

        .source-card span {
          display: block;
          color: var(--muted);
          font-size: 12px;
          font-weight: 780;
        }

        .source-card strong {
          display: block;
          margin: 8px 0 10px;
          font-size: 16px;
          line-height: 1.35;
        }

        .source-card p {
          margin-bottom: 12px;
          color: var(--muted);
          font-size: 13px;
        }

        .source-card a {
          color: var(--cyan);
          font-size: 13px;
          font-weight: 780;
          overflow-wrap: anywhere;
        }

        .export-panel {
          justify-content: space-between;
          padding: 22px;
        }

        .export-panel strong,
        .export-panel span {
          display: block;
          overflow-wrap: anywhere;
        }

        .export-panel span {
          margin-top: 5px;
          color: var(--muted);
          font-size: 14px;
        }

        .site-footer {
          display: flex;
          align-items: center;
          justify-content: space-between;
          gap: 20px;
          width: min(var(--max), calc(100% - 40px));
          margin: 92px auto 0;
          padding: 28px 0 34px;
          color: var(--muted);
          border-top: 1px solid var(--line);
          font-size: 13px;
          font-weight: 680;
        }

        .site-footer nav {
          display: flex;
          gap: 14px;
          flex-wrap: wrap;
        }

        .site-footer a {
          color: var(--ink);
        }

        .site-footer a:hover,
        .site-footer a:focus-visible {
          color: var(--cyan);
          outline: none;
        }

        .legal-page {
          width: min(860px, calc(100% - 40px));
          margin: 0 auto;
          padding: 72px 0 40px;
        }

        .legal-page h1 {
          max-width: none;
          margin-bottom: 18px;
          font-size: 44px;
          line-height: 1.08;
        }

        .legal-page h2 {
          margin: 42px 0 12px;
          font-size: 24px;
        }

        .legal-page p,
        .legal-page li {
          color: var(--muted);
        }

        .legal-page a {
          color: var(--cyan);
          text-decoration: underline;
          text-underline-offset: 3px;
        }

        .legal-meta {
          color: var(--faint);
          font-size: 14px;
          font-weight: 680;
        }

        .sr-only {
          position: absolute;
          overflow: hidden;
          width: 1px;
          height: 1px;
          padding: 0;
          margin: -1px;
          border: 0;
          clip: rect(0, 0, 0, 0);
          white-space: nowrap;
        }

        @media (max-width: 980px) {
          .site-header {
            padding: 0 18px;
          }

          .top-nav {
            display: none;
          }

          .hero {
            grid-template-columns: 1fr;
            gap: 28px;
            min-height: 0;
            padding-top: 54px;
          }

          .graph-panel,
          .major-map {
            min-height: 430px;
          }

          .metrics,
          .feature-grid,
          .roadmap-grid,
          .pipeline,
          .source-list {
            grid-template-columns: repeat(2, 1fr);
          }

          .browser-shell {
            grid-template-columns: 1fr;
          }

          .browser-list {
            border-right: 0;
            border-bottom: 1px solid var(--line);
          }

          .item-list {
            max-height: 420px;
          }
        }

        @media (max-width: 760px) {
          .section {
            width: min(100% - 28px, var(--max));
          }

          h1 {
            font-size: 44px;
          }

          .hero-lede {
            font-size: 17px;
          }

          .button,
          .hero-meta {
            width: 100%;
          }

          .hero-meta,
          .comparison-grid,
          .metrics,
          .feature-grid,
          .roadmap-grid,
          .pipeline,
          .source-list,
          .meta-grid {
            grid-template-columns: 1fr;
          }

          .graph-panel,
          .major-map {
            display: grid;
            grid-template-columns: 1fr;
            gap: 10px;
            min-height: 0;
            padding: 14px;
          }

          .graph-lines,
          .major-map svg {
            display: none;
          }

          .graph-node,
          .graph-node.root,
          .graph-node.root:hover,
          .graph-node.root:focus-visible,
          .map-core,
          .map-node,
          .map-node.local,
          .map-node.local:hover {
            position: static;
            width: 100%;
            min-width: 0;
            transform: none;
          }

          .metrics {
            margin-top: 0;
          }

          .split-section,
          .graph-section,
          .intro-grid,
          .flow,
          .roadmap,
          .browser,
          .sources,
          .export {
            padding-top: 68px;
          }

          .browser-toolbar {
            align-items: stretch;
          }

          .search-field {
            min-width: 100%;
          }

          .item-row {
            grid-template-columns: 1fr;
          }

          .type-chip {
            justify-self: start;
          }

          .site-footer {
            flex-direction: column;
            align-items: flex-start;
          }
        }
        """
    )


def type_role(type_: str) -> str:
    roles = {
        "domain": "최상위 지식 그래프 루트",
        "category": "세목·공제·지원·사업자 세무·기한의 탐색 축",
        "tax": "국세, 지방세, 관세 세목",
        "deduction": "과세표준 전 단계의 소득공제 항목",
        "tax-credit": "산출세액에서 차감하는 세액공제",
        "tax-reduction": "정책 목적의 세액감면",
        "corporate-tax-support": "법인세 공제·감면 공식 지원제도",
        "support-program": "장려금, 세제지원 계좌, 금융·복지 지원",
        "filing": "신고·납부·신청 절차",
        "scenario": "사용자 사례별 curated 탐색 경로",
        "life-expense": "월세, 병원비, 카드값처럼 사용자가 말하는 생활비 표현",
        "life-income": "부업, 프리랜서, 3.3%처럼 사용자가 말하는 소득 표현",
        "life-event": "퇴사, 이직, 첫 신고처럼 사용자가 말하는 사건 표현",
        "official-tax-item": "생활어 후보가 연결되는 공식 세금·공제 항목",
        "eligibility-rule": "공식 항목 적용 여부를 판단하는 요건 질문 규칙",
        "required-document": "신청·공제 판단에 필요한 증빙서류",
        "application-channel": "홈택스, 회사 제출 등 실제 신청·제출 경로",
        "conflict-rule": "중복공제, 제외, 이월 제한 등 충돌 판단 규칙",
        "concept": "판정 기준을 설명하는 개념 노드",
        "term": "그래프 해석에 필요한 용어",
        "deadline": "기준연도별 신고·납부·지급 기한",
        "source": "법률·기관별 공식 근거 URL",
    }
    return roles.get(type_, "온톨로지 노드")


def build_js(data: dict, summary: dict) -> str:
    payload = {
        "version": data["version"],
        "basis_date": data["basis_date"],
        "manifests": data["manifests"],
        "summary": summary,
        "type_labels": TYPE_LABELS,
        "type_roles": {type_: type_role(type_) for type_ in TYPE_LABELS},
        "items": data["items"],
    }
    data_json = json.dumps(payload, ensure_ascii=False, indent=2)
    script = dedent(
        """\
        const ONTOLOGY_DATA = __DATA__;

        (() => {
          const items = ONTOLOGY_DATA.items;
          const byId = new Map(items.map((item) => [item.id, item]));
          const typeLabels = ONTOLOGY_DATA.type_labels;
          const typeRoles = ONTOLOGY_DATA.type_roles;
          const searchInput = document.querySelector("[data-search]");
          const listEl = document.querySelector("[data-item-list]");
          const tabsEl = document.querySelector("[data-tabs]");
          const resultCountEl = document.querySelector("[data-result-count]");
          const detailEl = document.querySelector("[data-detail-panel]");
          const sourceListEl = document.querySelector("[data-source-list]");
          const typeTableEl = document.querySelector("[data-type-table]");

          const state = {
            tab: "all",
            query: "",
            selectedId: "kr-tax-system"
          };

          const tabs = [
            { id: "all", label: "전체", test: () => true },
            { id: "taxes", label: "세목", test: (item) => item.type === "tax" || hasAncestor(item, "category.national-taxes") || hasAncestor(item, "category.local-taxes") || hasAncestor(item, "category.customs") },
            { id: "reliefs", label: "공제·감면", test: (item) => ["deduction", "tax-credit", "tax-reduction", "corporate-tax-support"].includes(item.type) || hasAncestor(item, "category.deductions-and-reliefs") },
            { id: "supports", label: "정책지원", test: (item) => item.type === "support-program" || hasAncestor(item, "category.policy-supports") },
            { id: "business", label: "사업자", test: (item) => hasAncestor(item, "category.business-tax-compliance") },
            { id: "filing", label: "신고기한", test: (item) => ["filing", "deadline"].includes(item.type) || hasAncestor(item, "category.filing-calendar") },
            { id: "scenarios", label: "사용자 경로", test: (item) => item.type === "scenario" || hasAncestor(item, "category.user-scenarios") },
            { id: "life", label: "생활어", test: (item) => ["life-expense", "life-income", "life-event", "eligibility-rule", "required-document", "application-channel", "conflict-rule"].includes(item.type) || hasAncestor(item, "category.life-language") },
            { id: "terms", label: "용어·기준", test: (item) => ["term", "concept"].includes(item.type) },
            { id: "sources", label: "출처", test: (item) => item.type === "source" }
          ];

          function escapeHtml(value) {
            return String(value ?? "")
              .replaceAll("&", "&amp;")
              .replaceAll("<", "&lt;")
              .replaceAll(">", "&gt;")
              .replaceAll('"', "&quot;")
              .replaceAll("'", "&#039;");
          }

          function itemText(item) {
            return [
              item.id,
              item.title,
              typeLabels[item.type] || item.type,
              item.description,
              JSON.stringify(item.criteria || []),
              JSON.stringify(item.recurrence || {}),
              JSON.stringify(item.path_steps || []),
              JSON.stringify(item.life_phrases || []),
              JSON.stringify(item.official_candidates || []),
              JSON.stringify(item.eligibility_questions || []),
              JSON.stringify(item.source_urls || []),
              JSON.stringify(item.source_basis_dates || []),
              item.law_reference,
              item.publisher,
              item.url,
              ...(item.tags || [])
            ].join(" ").toLowerCase();
          }

          function hasAncestor(item, ancestorId, visited = new Set()) {
            if (!item || visited.has(item.id)) return false;
            visited.add(item.id);
            if ((item.parents || []).includes(ancestorId)) return true;
            return (item.parents || []).some((parentId) => hasAncestor(byId.get(parentId), ancestorId, visited));
          }

          function filteredItems() {
            const query = state.query.trim().toLowerCase();
            const activeTab = tabs.find((tab) => tab.id === state.tab) || tabs[0];
            return items
              .filter((item) => activeTab.test(item))
              .filter((item) => !query || itemText(item).includes(query))
              .sort((a, b) => {
                if (a.type === "domain") return -1;
                if (b.type === "domain") return 1;
                if (a.type !== b.type) return a.type.localeCompare(b.type);
                return a.title.localeCompare(b.title, "ko");
              });
          }

          function ensureVisibleSelection(visible) {
            if (!visible.length) {
              state.selectedId = "";
              return;
            }

            if (!visible.some((item) => item.id === state.selectedId)) {
              state.selectedId = visible[0].id;
            }
          }

          function renderTabs() {
            tabsEl.innerHTML = tabs
              .map((tab) => `<button class="tab-button" type="button" role="tab" aria-selected="${tab.id === state.tab}" data-tab="${tab.id}">${escapeHtml(tab.label)}</button>`)
              .join("");
          }

          function renderList() {
            const visible = filteredItems();
            ensureVisibleSelection(visible);
            resultCountEl.textContent = `${visible.length.toLocaleString("ko-KR")}개 표시`;
            if (!visible.length) {
              listEl.innerHTML = `<div class="empty-state">검색 조건에 맞는 항목이 없습니다.</div>`;
              return;
            }

            listEl.innerHTML = visible
              .map((item) => `
                <button class="item-row${item.id === state.selectedId ? " active" : ""}" type="button" data-select-item="${escapeHtml(item.id)}">
                  <span>
                    <strong>${escapeHtml(item.title)}</strong>
                    <p>${escapeHtml(item.description)}</p>
                  </span>
                  <span class="type-chip">${escapeHtml(typeLabels[item.type] || item.type)}</span>
                </button>
              `)
              .join("");
          }

          function relationBlock(title, ids) {
            const links = (ids || [])
              .map((id) => byId.get(id))
              .filter(Boolean)
              .map((item) => `<button class="relation-link" type="button" data-select-item="${escapeHtml(item.id)}">${escapeHtml(item.title)}</button>`)
              .join("");

            if (!links) return "";
            return `
              <div class="relation-group">
                <h4>${escapeHtml(title)}</h4>
                <div class="relation-links">${links}</div>
              </div>
            `;
          }

          function sourceBlock(ids) {
            const links = (ids || [])
              .map((id) => byId.get(id))
              .filter(Boolean)
              .map((source) => {
                if (source.url) {
                  return `<a class="relation-link" href="${escapeHtml(source.url)}" target="_blank" rel="noreferrer">${escapeHtml(source.title)}</a>`;
                }
                return `<span class="relation-link">${escapeHtml(source.title)}</span>`;
              })
              .join("");
            if (!links) return "";
            return `
              <div class="relation-group">
                <h4>근거·출처</h4>
                <div class="relation-links">${links}</div>
              </div>
            `;
          }

          function formatKrw(value) {
            if (value === undefined || value === null || value === "") return "";
            const number = Number(value);
            return Number.isFinite(number) ? `${number.toLocaleString("ko-KR")}원` : String(value);
          }

          function formatPercent(value) {
            if (value === undefined || value === null || value === "") return "";
            return `${value}%`;
          }

          function criteriaBlock(criteria) {
            if (!criteria || !criteria.length) return "";
            const labels = {
              criteria_kind: "기준 유형",
              basis: "기준항목",
              basis_category: "선정기준 분류",
              basis_definition: "선정기준 설명",
              basis_lookup: "확인 방법",
              selection_rule: "선정 규칙",
              condition: "조건",
              threshold_krw_min: "하한",
              threshold_krw: "기준금액",
              threshold_krw_max: "상한",
              rate_percent: "세율",
              rate_percent_min: "최저세율",
              rate_percent_max: "최고세율",
              progressive_deduction_krw: "누진공제",
              deduction_krw: "공제액",
              limit_krw: "한도",
              amount_krw: "금액",
              amount_formula: "금액·적용 산식",
              amount_applicability: "금액 기준 여부",
              max_amount_krw: "최대금액",
              base_deduction_krw: "기본공제액",
              per_year_deduction_krw: "연당 공제액",
              rate_basis: "비율 기준",
              law_reference: "근거 조항",
              deadline_month: "기한 월",
              deadline_day: "기한 일",
              deadline_start_month: "기한 시작 월",
              deadline_start_day: "기한 시작 일",
              deadline_end_month: "기한 종료 월",
              deadline_end_day: "기한 종료 일",
              deadline_days_after_event: "기준일 후 일수",
              deadline_months_after_month_end: "월말 후 개월",
              deadline_months_after_month_end_min: "월말 후 최소 개월",
              deadline_months_after_month_end_max: "월말 후 최대 개월",
              deadline_relative: "상대 기한",
              deadline_rule: "기한 규칙",
              benefit: "혜택",
              note: "비고"
            };
            const orderedKeys = [
              "criteria_kind",
              "basis",
              "basis_category",
              "condition",
              "basis_definition",
              "basis_lookup",
              "selection_rule",
              "law_reference",
              "threshold_krw_min",
              "threshold_krw",
              "threshold_krw_max",
              "rate_percent",
              "rate_percent_min",
              "rate_percent_max",
              "progressive_deduction_krw",
              "deduction_krw",
              "base_deduction_krw",
              "per_year_deduction_krw",
              "limit_krw",
              "amount_krw",
              "amount_formula",
              "amount_applicability",
              "max_amount_krw",
              "rate_basis",
              "deadline_month",
              "deadline_day",
              "deadline_start_month",
              "deadline_start_day",
              "deadline_end_month",
              "deadline_end_day",
              "deadline_days_after_event",
              "deadline_months_after_month_end",
              "deadline_months_after_month_end_min",
              "deadline_months_after_month_end_max",
              "deadline_relative",
              "deadline_rule",
              "benefit",
              "note"
            ];
            const items = criteria.map((criterion) => {
              const detail = orderedKeys
                .filter((key) => criterion[key] !== undefined && criterion[key] !== null && criterion[key] !== "")
                .map((key) => {
                  let value = criterion[key];
                  if (key.endsWith("_krw")) value = formatKrw(value);
                  if (key.startsWith("rate_percent")) value = formatPercent(value);
                  if (key.startsWith("deadline_month") || key === "deadline_month") value = `${value}개월`;
                  if (["deadline_month", "deadline_start_month", "deadline_end_month"].includes(key)) value = `${criterion[key]}월`;
                  if (["deadline_day", "deadline_start_day", "deadline_end_day", "deadline_days_after_event"].includes(key)) value = `${criterion[key]}일`;
                  let label = labels[key] || key;
                  if (key.startsWith("rate_percent") && criterion.rate_label) {
                    label = key === "rate_percent_min" ? `최저${criterion.rate_label}` : key === "rate_percent_max" ? `최고${criterion.rate_label}` : criterion.rate_label;
                  }
                  return `<span>${escapeHtml(label)}: <strong>${escapeHtml(value)}</strong></span>`;
                })
                .join("");
              const source = criterion.source ? byId.get(criterion.source) : null;
              const sourceLink = source ? `<button class="relation-link" type="button" data-select-item="${escapeHtml(source.id)}">${escapeHtml(source.title)}</button>` : "";
              const basisSource = criterion.basis_source && criterion.basis_source !== criterion.source ? byId.get(criterion.basis_source) : null;
              const basisSourceLink = basisSource ? `<button class="relation-link" type="button" data-select-item="${escapeHtml(basisSource.id)}">${escapeHtml(basisSource.title)}</button>` : "";
              return `
                <li>
                  <strong>${escapeHtml(criterion.label || "기준")}</strong>
                  <div>${detail}</div>
                  ${sourceLink || basisSourceLink ? `<p>${sourceLink}${basisSourceLink}</p>` : ""}
                </li>
              `;
            }).join("");
            return `
              <div class="criteria-block">
                <h4>기준 내역</h4>
                <ul>${items}</ul>
              </div>
            `;
          }

          function recurrenceBlock(recurrence) {
            if (!recurrence) return "";
            const labels = {
              frequency: "반복 주기",
              anchor: "기준일",
              period: "대상 기간",
              start_rule: "시작 규칙",
              due_rule: "마감 규칙",
              special_rule: "특례",
              example: "예시"
            };
            const detail = ["frequency", "anchor", "period", "start_rule", "due_rule", "special_rule", "example"]
              .filter((key) => recurrence[key])
              .map((key) => `<span>${escapeHtml(labels[key])}: <strong>${escapeHtml(recurrence[key])}</strong></span>`)
              .join("");
            if (!detail) return "";
            return `
              <div class="criteria-block">
                <h4>반복 규칙</h4>
                <ul><li><div>${detail}</div></li></ul>
              </div>
            `;
          }

          function pathStepsBlock(steps) {
            if (!steps || !steps.length) return "";
            const items = [...steps]
              .sort((a, b) => a.order - b.order)
              .map((step) => {
                const target = byId.get(step.target);
                const targetButton = target ? `<button class="relation-link" type="button" data-select-item="${escapeHtml(target.id)}">${escapeHtml(target.title)}</button>` : `<span class="relation-link">${escapeHtml(step.target)}</span>`;
                return `
                  <li>
                    <strong>${escapeHtml(step.order)}. ${escapeHtml(step.label)}</strong>
                    <div><span>${escapeHtml(step.reason)}</span></div>
                    <p>${targetButton}</p>
                  </li>
                `;
              })
              .join("");
            return `
              <div class="criteria-block">
                <h4>사용자 경로</h4>
                <ul>${items}</ul>
              </div>
            `;
          }

          function freshnessBlock(item) {
            const rows = [
              ["기준연도", item.basis_year || "해당 없음"],
              ["시행일", item.effective_date || "출처별 확인"],
              ["만료일", item.expiration_date || "없음"],
              ["확인일", item.reviewed_at || "출처별 확인"],
              ["폐지 여부", item.abolition_status || "active"],
              ["개정 예정 여부", item.revision_status || "none_announced"],
              ["관할기관", item.jurisdiction || ""],
              ["정부24 서비스 ID", item.gov24_service_id || ""],
              ["정부24 서비스 순번", item.gov24_service_seq || ""],
              ["원문 수정일", item.source_modified_at || ""],
              ["원문 수집일", item.source_collected_at || ""],
              ["신청기한 원문", item.application_deadline_text || ""],
              ["신청방식", item.application_method || ""],
              ["접수기관", item.receiving_agency || ""],
              ["문의처", item.contact || ""]
            ];
            const visibleRows = rows.filter(([, value]) => value !== "" && value !== null && value !== undefined);
            const sourceUrls = (item.source_urls || [])
              .map((url) => `<a class="relation-link" href="${escapeHtml(url)}" target="_blank" rel="noreferrer">${escapeHtml(url)}</a>`)
              .join("");
            const statusCheckUrl = item.status_check_url ? `<a class="relation-link" href="${escapeHtml(item.status_check_url)}" target="_blank" rel="noreferrer">${escapeHtml(item.status_check_url)}</a>` : "";
            const basisDates = (item.source_basis_dates || []).map((date) => escapeHtml(date)).join(", ");
            const legalBasis = (item.legal_basis || [])
              .map((basis) => basis && basis.url ? `<a class="relation-link" href="${escapeHtml(basis.url)}" target="_blank" rel="noreferrer">${escapeHtml(basis.title || basis.url)}</a>` : escapeHtml((basis && (basis.title || basis.name)) || ""))
              .filter(Boolean)
              .join("");
            return `
              <div class="criteria-block">
                <h4>최신성 메타데이터</h4>
                <ul>
                  <li><div>${visibleRows.map(([label, value]) => `<span>${escapeHtml(label)}: <strong>${escapeHtml(value)}</strong></span>`).join("")}</div></li>
                  ${statusCheckUrl ? `<li><strong>상태 확인 URL</strong><p>${statusCheckUrl}</p></li>` : ""}
                  ${basisDates ? `<li><strong>출처 확인일</strong><div><span>${basisDates}</span></div></li>` : ""}
                  ${sourceUrls ? `<li><strong>출처 URL</strong><p>${sourceUrls}</p></li>` : ""}
                  ${legalBasis ? `<li><strong>법령·자치법규 근거</strong><p>${legalBasis}</p></li>` : ""}
                </ul>
              </div>
            `;
          }

          function lifeMappingBlock(item) {
            const phrases = item.life_phrases || [];
            const candidates = item.official_candidates || [];
            const questions = item.eligibility_questions || [];
            if (!phrases.length && !candidates.length && !questions.length) return "";
            const phraseHtml = phrases.length ? `
              <li>
                <strong>생활어 사전</strong>
                <div>${phrases.map((phrase) => `<span>${escapeHtml(phrase)}</span>`).join("")}</div>
              </li>
            ` : "";
            const candidateHtml = candidates.length ? candidates
              .slice()
              .sort((a, b) => b.confidence - a.confidence)
              .map((candidate) => {
                const target = byId.get(candidate.target);
                const targetButton = target ? `<button class="relation-link" type="button" data-select-item="${escapeHtml(target.id)}">${escapeHtml(target.title)}</button>` : `<span class="relation-link">${escapeHtml(candidate.target)}</span>`;
                const checks = (candidate.required_checks || []).join(", ");
                return `
                  <li>
                    <strong>공식 후보 ${escapeHtml(candidate.confidence_label || "")} ${(candidate.confidence * 100).toFixed(0)}%</strong>
                    <div><span>${escapeHtml(candidate.reason)}</span>${checks ? `<span>추가 확인: <strong>${escapeHtml(checks)}</strong></span>` : ""}</div>
                    <p>${targetButton}</p>
                  </li>
                `;
              })
              .join("") : "";
            const questionHtml = questions.length ? questions
              .slice()
              .sort((a, b) => a.order - b.order)
              .map((question) => {
                const target = question.target ? byId.get(question.target) : null;
                const targetButton = target ? `<button class="relation-link" type="button" data-select-item="${escapeHtml(target.id)}">${escapeHtml(target.title)}</button>` : "";
                return `
                  <li>
                    <strong>${escapeHtml(question.order)}. ${escapeHtml(question.question)}</strong>
                    <div>${question.criterion ? `<span>판단 기준: <strong>${escapeHtml(question.criterion)}</strong></span>` : ""}${question.answer_type ? `<span>답변 유형: <strong>${escapeHtml(question.answer_type)}</strong></span>` : ""}</div>
                    ${targetButton ? `<p>${targetButton}</p>` : ""}
                  </li>
                `;
              })
              .join("") : "";
            return `
              <div class="criteria-block">
                <h4>생활어 판단 로직</h4>
                <ul>${phraseHtml}${candidateHtml}${questionHtml}</ul>
              </div>
            `;
          }

          function renderDetail() {
            const item = byId.get(state.selectedId) || byId.get("kr-tax-system") || items[0];
            if (!item) {
              detailEl.innerHTML = `
                <div class="detail-kicker">검색 결과 없음</div>
                <h3>선택할 항목이 없습니다</h3>
                <p>검색어를 줄이거나 다른 필터를 선택해 주세요.</p>
              `;
              return;
            }
            const relationHtml = [
              relationBlock("상위 항목", item.parents),
              relationBlock("하위 항목", item.children),
              relationBlock("관련 항목", item.related),
              relationBlock("관련 용어", item.terms),
              relationBlock("관련 기한", item.deadlines),
              sourceBlock(item.sources)
            ].filter(Boolean).join("");
            const criteriaHtml = criteriaBlock(item.criteria);
            const recurrenceHtml = recurrenceBlock(item.recurrence);
            const pathStepsHtml = pathStepsBlock(item.path_steps);
            const freshnessHtml = freshnessBlock(item);
            const lifeMappingHtml = lifeMappingBlock(item);

            detailEl.innerHTML = `
              <div class="detail-kicker">${escapeHtml(typeLabels[item.type] || item.type)} · ${escapeHtml(item.id)}</div>
              <h3>${escapeHtml(item.title)}</h3>
              <p>${escapeHtml(item.description)}</p>
              <div class="meta-grid">
                <div><span>기준연도</span><strong>${escapeHtml(item.basis_year || "해당 없음")}</strong></div>
                <div><span>법령 근거</span><strong>${escapeHtml(item.law_reference || "출처 노드 참조")}</strong></div>
                <div><span>폴더</span><strong>${escapeHtml(item.folder || "-")}</strong></div>
                <div><span>태그</span><strong>${escapeHtml((item.tags || []).join(", ") || "-")}</strong></div>
              </div>
              ${freshnessHtml}
              ${lifeMappingHtml}
              ${recurrenceHtml}
              ${pathStepsHtml}
              ${criteriaHtml}
              <div class="relations">${relationHtml || "<p>연결된 관계가 없습니다.</p>"}</div>
            `;
          }

          function renderTypeTable() {
            const counts = ONTOLOGY_DATA.summary.type_counts;
            typeTableEl.innerHTML = Object.keys(counts)
              .sort((a, b) => (typeLabels[a] || a).localeCompare(typeLabels[b] || b, "ko"))
              .map((type) => `
                <tr>
                  <td><strong>${escapeHtml(typeLabels[type] || type)}</strong><br><span>${escapeHtml(type)}</span></td>
                  <td>${Number(counts[type]).toLocaleString("ko-KR")}</td>
                  <td>${escapeHtml(typeRoles[type] || "온톨로지 노드")}</td>
                </tr>
              `)
              .join("");
          }

          function renderSources() {
            const sources = items
              .filter((item) => item.type === "source")
              .sort((a, b) => (a.publisher || "").localeCompare(b.publisher || "", "ko") || a.title.localeCompare(b.title, "ko"));

            sourceListEl.innerHTML = sources
              .map((source) => `
                <article class="source-card">
                  <span>${escapeHtml(source.publisher || "공식 출처")} · ${escapeHtml(source.basis_date || ONTOLOGY_DATA.basis_date)}</span>
                  <strong>${escapeHtml(source.title)}</strong>
                  <p>${escapeHtml(source.description)}</p>
                  ${source.url ? `<a href="${escapeHtml(source.url)}" target="_blank" rel="noreferrer">원문 열기</a>` : ""}
                </article>
              `)
              .join("");
          }

          function downloadJson() {
            const exportData = {
              version: ONTOLOGY_DATA.version,
              basis_date: ONTOLOGY_DATA.basis_date,
              manifests: ONTOLOGY_DATA.manifests,
              items: ONTOLOGY_DATA.items
            };
            const blob = new Blob([JSON.stringify(exportData, null, 2)], { type: "application/json" });
            const url = URL.createObjectURL(blob);
            const anchor = document.createElement("a");
            anchor.href = url;
            anchor.download = "opentax-2026.json";
            document.body.appendChild(anchor);
            anchor.click();
            anchor.remove();
            URL.revokeObjectURL(url);
          }

          document.addEventListener("click", (event) => {
            const selectButton = event.target.closest("[data-select-item]");
            if (selectButton) {
              const id = selectButton.getAttribute("data-select-item");
              if (byId.has(id)) {
                state.selectedId = id;
                renderList();
                renderDetail();
                document.querySelector("#browser")?.scrollIntoView({ behavior: "smooth", block: "start" });
              }
            }

            const tabButton = event.target.closest("[data-tab]");
            if (tabButton) {
              state.tab = tabButton.getAttribute("data-tab");
              renderTabs();
              renderList();
              renderDetail();
            }

            if (event.target.closest("[data-download-json]")) {
              downloadJson();
            }
          });

          searchInput.addEventListener("input", (event) => {
            state.query = event.target.value;
            renderList();
            renderDetail();
          });

          renderTypeTable();
          renderSources();
          renderTabs();
          renderList();
          renderDetail();
        })();
        """
    )
    return script.replace("__DATA__", data_json)


def main() -> int:
    data = load_export()
    summary = summarize(data)
    WEB_ROOT.mkdir(parents=True, exist_ok=True)
    (WEB_ROOT / "index.html").write_text(build_html(data, summary), encoding="utf-8")
    (WEB_ROOT / "styles.css").write_text(build_css(), encoding="utf-8")
    (WEB_ROOT / "app.js").write_text(build_js(data, summary), encoding="utf-8")
    print(f"Built {WEB_ROOT.relative_to(REPO_ROOT)} from {EXPORT_PATH.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
