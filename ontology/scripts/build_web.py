#!/usr/bin/env python3
"""Build the static web guide for the Korean tax ontology."""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from textwrap import dedent


REPO_ROOT = Path(__file__).resolve().parents[2]
ONTOLOGY_ROOT = REPO_ROOT / "ontology"
EXPORT_PATH = ONTOLOGY_ROOT / "exports" / "korea-tax-ontology-2026.json"
WEB_ROOT = REPO_ROOT / "docs" / "tax-ontology"


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
    "concept": "판정 개념",
    "term": "용어",
    "deadline": "기한",
    "source": "공식 출처",
}


def load_export() -> dict:
    return json.loads(EXPORT_PATH.read_text(encoding="utf-8"))


def summarize(data: dict) -> dict:
    items = data["items"]
    counts = Counter(item["type"] for item in items)
    return {
        "item_count": len(items),
        "source_count": counts["source"],
        "term_count": counts["term"],
        "category_count": counts["category"],
        "national_tax_count": len(data["manifests"]["national_tax_ids"]),
        "local_tax_count": len(data["manifests"]["local_tax_ids"]),
        "corporate_support_count": len(data["manifests"]["corporate_support_ids"]),
        "type_counts": dict(sorted(counts.items())),
    }


def build_html(data: dict, summary: dict) -> str:
    version = data["version"]
    basis_date = data["basis_date"]
    return dedent(
        f"""\
        <!doctype html>
        <html lang="ko">
        <head>
          <meta charset="utf-8">
          <meta name="viewport" content="width=device-width, initial-scale=1">
          <title>대한민국 세금 온톨로지</title>
          <meta name="description" content="대한민국 세금, 공제, 감면, 정책지원금, 신고기한을 연결한 TaxMeter 온톨로지 웹 가이드">
          <link rel="stylesheet" href="./styles.css">
        </head>
        <body>
          <header class="site-header">
            <a class="brand" href="#top" aria-label="대한민국 세금 온톨로지 홈">
              <span class="brand-mark" aria-hidden="true">
                <svg viewBox="0 0 32 32" role="img">
                  <path d="M16 3.5 27 9.8v12.4l-11 6.3-11-6.3V9.8L16 3.5Z" fill="none" stroke="currentColor" stroke-width="2"/>
                  <path d="M10 16h12M16 10v12" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
                </svg>
              </span>
              <span>Tax Ontology</span>
            </a>
            <nav class="top-nav" aria-label="주요 섹션">
              <a href="#browser">둘러보기</a>
              <a href="#structure">구조</a>
              <a href="#sources">출처</a>
              <a href="#export">Export</a>
            </nav>
          </header>

          <main id="top">
            <section class="hero section">
              <div class="hero-copy">
                <p class="version-line">{version} · 기준일 {basis_date}</p>
                <h1>대한민국 세금 온톨로지</h1>
                <p class="hero-lede">
                  국세, 지방세, 관세, 공제·감면, 정책지원금, 신고·납부 기한을
                  하나의 검증 가능한 지식 그래프로 정리한 TaxMeter 데이터 표면입니다.
                </p>
                <div class="hero-actions">
                  <a class="button primary" href="#browser">온톨로지 둘러보기</a>
                  <button class="button secondary" type="button" data-download-json>JSON export 보기</button>
                </div>
              </div>

              <div class="graph-panel" aria-label="온톨로지 상위 그래프">
                <button class="graph-node root" type="button" data-select-item="kr-tax-system">
                  <strong>대한민국 세금</strong>
                  <span>{summary["item_count"]} nodes</span>
                </button>
                <button class="graph-node national" type="button" data-select-item="category.national-taxes">
                  <strong>국세</strong>
                  <span>{summary["national_tax_count"]} 세목</span>
                </button>
                <button class="graph-node customs" type="button" data-select-item="category.customs">
                  <strong>관세</strong>
                  <span>별도 영역</span>
                </button>
                <button class="graph-node local" type="button" data-select-item="category.local-taxes">
                  <strong>지방세</strong>
                  <span>{summary["local_tax_count"]} 세목</span>
                </button>
                <button class="graph-node relief" type="button" data-select-item="category.deductions-and-reliefs">
                  <strong>공제·감면</strong>
                  <span>소득·세액·법인</span>
                </button>
                <button class="graph-node support" type="button" data-select-item="category.policy-supports">
                  <strong>정책지원</strong>
                  <span>계좌·장려금</span>
                </button>
                <button class="graph-node filing" type="button" data-select-item="category.filing-calendar">
                  <strong>신고기한</strong>
                  <span>신청·납부</span>
                </button>
                <svg class="graph-lines" viewBox="0 0 640 420" aria-hidden="true">
                  <path d="M320 205 C260 130 210 82 125 76"/>
                  <path d="M320 205 C380 125 465 85 535 86"/>
                  <path d="M320 205 C198 201 131 206 82 210"/>
                  <path d="M320 205 C440 200 507 205 562 211"/>
                  <path d="M320 205 C236 285 196 335 126 345"/>
                  <path d="M320 205 C400 289 450 337 535 345"/>
                </svg>
              </div>
            </section>

            <section class="metrics section" aria-label="온톨로지 요약 수치">
              <div>
                <strong>{summary["item_count"]}</strong>
                <span>검증 노트</span>
              </div>
              <div>
                <strong>{summary["national_tax_count"]}</strong>
                <span>국세 세목</span>
              </div>
              <div>
                <strong>{summary["local_tax_count"]}</strong>
                <span>지방세 세목</span>
              </div>
              <div>
                <strong>{summary["corporate_support_count"]}</strong>
                <span>법인세 지원</span>
              </div>
              <div>
                <strong>{summary["source_count"]}</strong>
                <span>공식 출처</span>
              </div>
            </section>

            <section class="section intro-grid" aria-labelledby="what-you-get">
              <div class="section-heading">
                <h2 id="what-you-get">What You Get</h2>
                <p>Obsidian vault, JSON export, MCP 검색면, 그리고 웹 탐색 UI를 같은 데이터에서 만듭니다.</p>
              </div>
              <div class="feature-grid">
                <article class="feature-card">
                  <span class="feature-icon" aria-hidden="true">01</span>
                  <h3>완전한 세목 골격</h3>
                  <p>국세기본법과 지방세기본법 기준 세목을 매니페스트로 고정하고 검증합니다.</p>
                </article>
                <article class="feature-card">
                  <span class="feature-icon" aria-hidden="true">02</span>
                  <h3>공제·감면 연결</h3>
                  <p>소득공제, 세액공제, 세액감면, 법인세 지원 항목을 상위 카테고리와 용어에 연결합니다.</p>
                </article>
                <article class="feature-card">
                  <span class="feature-icon" aria-hidden="true">03</span>
                  <h3>신고 일정 표면</h3>
                  <p>종합소득세, 연말정산, 원천세, 부가가치세, 장려금 신청·지급 기한을 연결합니다.</p>
                </article>
                <article class="feature-card">
                  <span class="feature-icon" aria-hidden="true">04</span>
                  <h3>공식 근거 추적</h3>
                  <p>각 항목은 국세청, 법령정보센터, 금융위원회 등 출처 노드와 URL을 보유합니다.</p>
                </article>
              </div>
            </section>

            <section class="section structure" id="structure" aria-labelledby="structure-title">
              <div class="section-heading">
                <h2 id="structure-title">구조</h2>
                <p>원본 정의에서 vault와 export를 생성한 뒤, 검증기가 링크 무결성과 필수 항목을 확인합니다.</p>
              </div>
              <div class="pipeline">
                <div><strong>Definition</strong><span>generate_vault.py</span></div>
                <div><strong>Vault</strong><span>154 Markdown notes</span></div>
                <div><strong>Validation</strong><span>references + manifests</span></div>
                <div><strong>Export</strong><span>JSON + MCP + Web</span></div>
              </div>
              <div class="type-table-wrap">
                <table class="type-table">
                  <thead>
                    <tr>
                      <th>노드 타입</th>
                      <th>개수</th>
                      <th>역할</th>
                    </tr>
                  </thead>
                  <tbody data-type-table></tbody>
                </table>
              </div>
            </section>

            <section class="section browser" id="browser" aria-labelledby="browser-title">
              <div class="section-heading">
                <h2 id="browser-title">온톨로지 둘러보기</h2>
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
                      <input type="search" placeholder="예: 부가가치세, 세액공제, 신고기한" data-search>
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
                <p>웹 표면은 설명을 다시 쓰지 않고 출처 노드의 발행처, 기준일, URL을 그대로 노출합니다.</p>
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
                  <span>{version}</span>
                </div>
                <button class="button primary" type="button" data-download-json>JSON 다운로드</button>
              </div>
            </section>
          </main>

          <footer class="site-footer">
            <span>TaxMeter · Korea Tax Ontology</span>
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
          color-scheme: light;
          --bg: #f7f9fb;
          --paper: #ffffff;
          --ink: #0c1424;
          --muted: #526073;
          --soft: #e7edf4;
          --line: #d8e0ea;
          --blue: #1555d6;
          --blue-strong: #0f3f9f;
          --teal: #0f8b8d;
          --green: #287a4f;
          --coral: #c44f35;
          --amber: #a36412;
          --purple: #7253b7;
          --shadow: 0 18px 50px rgba(12, 20, 36, 0.08);
          --radius: 8px;
          --max: 1180px;
        }

        * {
          box-sizing: border-box;
        }

        html {
          scroll-behavior: smooth;
        }

        body {
          margin: 0;
          background: var(--bg);
          color: var(--ink);
          font-family: -apple-system, BlinkMacSystemFont, "SF Pro Display", "Apple SD Gothic Neo", "Pretendard", "Noto Sans KR", "Segoe UI", sans-serif;
          font-size: 16px;
          line-height: 1.6;
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
          background: rgba(255, 255, 255, 0.92);
          border-bottom: 1px solid var(--line);
          backdrop-filter: blur(18px);
        }

        .brand {
          display: inline-flex;
          align-items: center;
          gap: 10px;
          color: var(--ink);
          font-weight: 760;
          white-space: nowrap;
        }

        .brand-mark {
          display: grid;
          width: 34px;
          height: 34px;
          place-items: center;
          color: var(--blue);
          background: #edf4ff;
          border: 1px solid #cfe0ff;
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
          border-radius: 6px;
          color: var(--muted);
          font-size: 14px;
          font-weight: 680;
        }

        .top-nav a:hover,
        .top-nav a:focus-visible {
          color: var(--ink);
          background: #eef3f8;
          outline: none;
        }

        .section {
          width: min(var(--max), calc(100% - 40px));
          margin: 0 auto;
        }

        .hero {
          display: grid;
          grid-template-columns: minmax(0, 0.9fr) minmax(440px, 1.1fr);
          gap: 56px;
          align-items: center;
          min-height: calc(100vh - 64px);
          padding: 76px 0 52px;
        }

        .version-line {
          margin: 0 0 14px;
          color: var(--blue);
          font-size: 14px;
          font-weight: 720;
        }

        h1,
        h2,
        h3,
        p {
          margin-top: 0;
        }

        h1 {
          max-width: 10em;
          margin-bottom: 24px;
          font-size: clamp(46px, 7vw, 86px);
          line-height: 0.98;
          font-weight: 820;
        }

        .hero-lede {
          max-width: 610px;
          margin-bottom: 28px;
          color: var(--muted);
          font-size: 19px;
          line-height: 1.72;
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
          font-weight: 760;
        }

        .button.primary {
          color: #fff;
          background: var(--blue);
          box-shadow: 0 12px 24px rgba(21, 85, 214, 0.22);
        }

        .button.primary:hover,
        .button.primary:focus-visible {
          background: var(--blue-strong);
          outline: none;
        }

        .button.secondary {
          color: var(--ink);
          background: #fff;
          border-color: var(--line);
        }

        .button.secondary:hover,
        .button.secondary:focus-visible {
          border-color: #a9b9cc;
          outline: none;
        }

        .graph-panel {
          position: relative;
          min-height: 420px;
          overflow: hidden;
          background: var(--paper);
          border: 1px solid var(--line);
          border-radius: var(--radius);
          box-shadow: var(--shadow);
        }

        .graph-lines {
          position: absolute;
          inset: 0;
          width: 100%;
          height: 100%;
          color: #aebdcd;
          pointer-events: none;
        }

        .graph-lines path {
          fill: none;
          stroke: currentColor;
          stroke-width: 1.6;
          stroke-dasharray: 4 8;
        }

        .graph-node {
          position: absolute;
          z-index: 2;
          display: flex;
          flex-direction: column;
          align-items: flex-start;
          min-width: 128px;
          padding: 14px 16px;
          color: var(--ink);
          background: #fff;
          border: 1px solid var(--line);
          border-left: 5px solid var(--blue);
          border-radius: var(--radius);
          box-shadow: 0 12px 30px rgba(12, 20, 36, 0.09);
          text-align: left;
        }

        .graph-node:hover,
        .graph-node:focus-visible {
          transform: translateY(-2px);
          outline: 2px solid rgba(21, 85, 214, 0.24);
          outline-offset: 2px;
        }

        .graph-node strong {
          font-size: 15px;
          line-height: 1.35;
        }

        .graph-node span {
          color: var(--muted);
          font-size: 12px;
          font-weight: 680;
        }

        .graph-node.root {
          top: 166px;
          left: 50%;
          min-width: 162px;
          transform: translateX(-50%);
          border-left-color: var(--blue);
        }

        .graph-node.root:hover,
        .graph-node.root:focus-visible {
          transform: translateX(-50%) translateY(-2px);
        }

        .graph-node.national {
          top: 48px;
          left: 38px;
          border-left-color: var(--blue);
        }

        .graph-node.customs {
          top: 50px;
          right: 40px;
          border-left-color: var(--purple);
        }

        .graph-node.local {
          top: 180px;
          left: 30px;
          border-left-color: var(--teal);
        }

        .graph-node.relief {
          top: 182px;
          right: 28px;
          border-left-color: var(--green);
        }

        .graph-node.support {
          bottom: 44px;
          left: 46px;
          border-left-color: var(--coral);
        }

        .graph-node.filing {
          right: 38px;
          bottom: 44px;
          border-left-color: var(--amber);
        }

        .metrics {
          display: grid;
          grid-template-columns: repeat(5, 1fr);
          gap: 1px;
          overflow: hidden;
          margin-top: -18px;
          background: var(--line);
          border: 1px solid var(--line);
          border-radius: var(--radius);
        }

        .metrics div {
          display: flex;
          min-height: 118px;
          flex-direction: column;
          justify-content: center;
          padding: 22px;
          background: #fff;
        }

        .metrics strong {
          font-size: 38px;
          line-height: 1;
          font-weight: 820;
        }

        .metrics span {
          margin-top: 8px;
          color: var(--muted);
          font-size: 14px;
          font-weight: 720;
        }

        .section-heading {
          max-width: 760px;
          margin-bottom: 28px;
        }

        .section-heading h2 {
          margin-bottom: 10px;
          font-size: clamp(30px, 4vw, 48px);
          line-height: 1.08;
          font-weight: 820;
        }

        .section-heading p {
          color: var(--muted);
          font-size: 17px;
          line-height: 1.7;
        }

        .intro-grid,
        .structure,
        .browser,
        .sources,
        .export {
          padding: 96px 0 0;
        }

        .feature-grid {
          display: grid;
          grid-template-columns: repeat(4, 1fr);
          gap: 14px;
        }

        .feature-card {
          min-height: 220px;
          padding: 22px;
          background: #fff;
          border: 1px solid var(--line);
          border-radius: var(--radius);
        }

        .feature-icon {
          display: inline-flex;
          margin-bottom: 28px;
          color: var(--blue);
          font-size: 13px;
          font-weight: 820;
        }

        .feature-card h3 {
          margin-bottom: 12px;
          font-size: 20px;
          line-height: 1.25;
        }

        .feature-card p {
          color: var(--muted);
          font-size: 15px;
        }

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
          background: #fff;
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
          background: #fff;
          border: 1px solid var(--line);
          border-radius: var(--radius);
          box-shadow: 0 12px 34px rgba(12, 20, 36, 0.05);
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
          border-bottom: 1px solid var(--soft);
          text-align: left;
          vertical-align: top;
        }

        th {
          color: var(--muted);
          background: #f8fafc;
          font-size: 13px;
          font-weight: 800;
        }

        td {
          font-size: 14px;
        }

        tr:last-child td {
          border-bottom: 0;
        }

        .browser-shell {
          display: grid;
          grid-template-columns: minmax(0, 1.06fr) minmax(360px, 0.94fr);
          overflow: hidden;
          min-height: 680px;
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
          background: #f8fafc;
          border: 1px solid var(--line);
          border-radius: 7px;
          color: var(--muted);
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

        .result-count {
          color: var(--muted);
          font-size: 14px;
          font-weight: 720;
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
          background: #fff;
          border: 1px solid var(--line);
          border-radius: 6px;
          font-size: 13px;
          font-weight: 760;
        }

        .tab-button[aria-selected="true"] {
          color: #fff;
          background: var(--ink);
          border-color: var(--ink);
        }

        .item-list {
          max-height: 588px;
          overflow: auto;
        }

        .item-row {
          display: grid;
          grid-template-columns: minmax(0, 1fr) auto;
          gap: 12px;
          width: 100%;
          padding: 17px 18px;
          color: var(--ink);
          background: #fff;
          border: 0;
          border-bottom: 1px solid var(--soft);
          text-align: left;
        }

        .item-row:hover,
        .item-row:focus-visible {
          background: #f8fafc;
          outline: none;
        }

        .item-row.active {
          background: #eef5ff;
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
          color: var(--blue-strong);
          background: #eef5ff;
          border: 1px solid #d6e5ff;
          border-radius: 6px;
          font-size: 12px;
          font-weight: 780;
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
          background: #fcfdff;
        }

        .detail-kicker {
          margin-bottom: 8px;
          color: var(--blue);
          font-size: 13px;
          font-weight: 820;
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
          background: #fff;
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
          font-size: 13px;
          color: var(--muted);
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
          background: #f8fafc;
          border: 1px solid var(--soft);
          border-radius: 8px;
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
          background: #fff;
          border: 1px solid var(--line);
          border-radius: 6px;
          font-size: 12px;
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
          background: #f6f8fb;
          border: 1px solid var(--soft);
          border-radius: 6px;
          font-size: 12px;
          font-weight: 720;
          overflow-wrap: anywhere;
        }

        .relation-link:hover,
        .relation-link:focus-visible {
          color: var(--blue);
          border-color: #bdd2f8;
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
          color: var(--blue);
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

          .graph-panel {
            min-height: 390px;
          }

          .metrics,
          .feature-grid,
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

        @media (max-width: 640px) {
          .section {
            width: min(100% - 28px, var(--max));
          }

          h1 {
            font-size: 44px;
          }

          .hero-lede {
            font-size: 17px;
          }

          .button {
            width: 100%;
          }

          .graph-panel {
            display: grid;
            grid-template-columns: 1fr;
            gap: 10px;
            min-height: 0;
            padding: 14px;
          }

          .graph-lines {
            display: none;
          }

          .graph-node,
          .graph-node.root,
          .graph-node.root:hover,
          .graph-node.root:focus-visible {
            position: static;
            min-width: 0;
            transform: none;
          }

          .metrics,
          .feature-grid,
          .pipeline,
          .source-list,
          .meta-grid {
            grid-template-columns: 1fr;
          }

          .metrics {
            margin-top: 0;
          }

          .intro-grid,
          .structure,
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
          }
        }
        """
    )


def type_role(type_: str) -> str:
    roles = {
        "domain": "최상위 지식 그래프 루트",
        "category": "세목·공제·지원·기한의 탐색 축",
        "tax": "국세, 지방세, 관세 세목",
        "deduction": "과세표준 전 단계의 소득공제 항목",
        "tax-credit": "산출세액에서 차감하는 세액공제",
        "tax-reduction": "정책 목적의 세액감면",
        "corporate-tax-support": "법인세 공제·감면 공식 지원제도",
        "support-program": "장려금과 세제지원 계좌",
        "filing": "신고·납부·신청 절차",
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
    return dedent(
        f"""\
        const ONTOLOGY_DATA = {data_json};

        (() => {{
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

          const state = {{
            tab: "all",
            query: "",
            selectedId: "kr-tax-system"
          }};

          const tabs = [
            {{ id: "all", label: "전체", test: () => true }},
            {{ id: "taxes", label: "세목", test: (item) => item.type === "tax" || hasAncestor(item, "category.national-taxes") || hasAncestor(item, "category.local-taxes") || hasAncestor(item, "category.customs") }},
            {{ id: "reliefs", label: "공제·감면", test: (item) => ["deduction", "tax-credit", "tax-reduction", "corporate-tax-support"].includes(item.type) || hasAncestor(item, "category.deductions-and-reliefs") }},
            {{ id: "supports", label: "정책지원", test: (item) => item.type === "support-program" || hasAncestor(item, "category.policy-supports") }},
            {{ id: "filing", label: "신고기한", test: (item) => ["filing", "deadline"].includes(item.type) || hasAncestor(item, "category.filing-calendar") }},
            {{ id: "terms", label: "용어", test: (item) => ["term", "concept"].includes(item.type) }},
            {{ id: "sources", label: "출처", test: (item) => item.type === "source" }}
          ];

          function escapeHtml(value) {{
            return String(value ?? "")
              .replaceAll("&", "&amp;")
              .replaceAll("<", "&lt;")
              .replaceAll(">", "&gt;")
              .replaceAll('"', "&quot;")
              .replaceAll("'", "&#039;");
          }}

          function itemText(item) {{
            return [
              item.id,
              item.title,
              typeLabels[item.type] || item.type,
              item.description,
              JSON.stringify(item.criteria || []),
              item.law_reference,
              ...(item.tags || [])
            ].join(" ").toLowerCase();
          }}

          function hasAncestor(item, ancestorId, visited = new Set()) {{
            if (!item || visited.has(item.id)) return false;
            visited.add(item.id);
            if ((item.parents || []).includes(ancestorId)) return true;
            return (item.parents || []).some((parentId) => hasAncestor(byId.get(parentId), ancestorId, visited));
          }}

          function filteredItems() {{
            const query = state.query.trim().toLowerCase();
            const activeTab = tabs.find((tab) => tab.id === state.tab) || tabs[0];
            return items
              .filter((item) => activeTab.test(item))
              .filter((item) => !query || itemText(item).includes(query))
              .sort((a, b) => {{
                if (a.type === "domain") return -1;
                if (b.type === "domain") return 1;
                if (a.type !== b.type) return a.type.localeCompare(b.type);
                return a.title.localeCompare(b.title, "ko");
              }});
          }}

          function ensureVisibleSelection(visible) {{
            if (!visible.length) {{
              state.selectedId = "";
              return;
            }}

            if (!visible.some((item) => item.id === state.selectedId)) {{
              state.selectedId = visible[0].id;
            }}
          }}

          function renderTabs() {{
            tabsEl.innerHTML = tabs
              .map((tab) => `<button class="tab-button" type="button" role="tab" aria-selected="${{tab.id === state.tab}}" data-tab="${{tab.id}}">${{escapeHtml(tab.label)}}</button>`)
              .join("");
          }}

          function renderList() {{
            const visible = filteredItems();
            ensureVisibleSelection(visible);
            resultCountEl.textContent = `${{visible.length.toLocaleString("ko-KR")}}개 표시`;
            if (!visible.length) {{
              listEl.innerHTML = `<div class="empty-state">검색 조건에 맞는 항목이 없습니다.</div>`;
              return;
            }}

            listEl.innerHTML = visible
              .map((item) => `
                <button class="item-row${{item.id === state.selectedId ? " active" : ""}}" type="button" data-select-item="${{escapeHtml(item.id)}}">
                  <span>
                    <strong>${{escapeHtml(item.title)}}</strong>
                    <p>${{escapeHtml(item.description)}}</p>
                  </span>
                  <span class="type-chip">${{escapeHtml(typeLabels[item.type] || item.type)}}</span>
                </button>
              `)
              .join("");
          }}

          function relationBlock(title, ids) {{
            const links = (ids || [])
              .map((id) => byId.get(id))
              .filter(Boolean)
              .map((item) => `<button class="relation-link" type="button" data-select-item="${{escapeHtml(item.id)}}">${{escapeHtml(item.title)}}</button>`)
              .join("");

            if (!links) return "";
            return `
              <div class="relation-group">
                <h4>${{escapeHtml(title)}}</h4>
                <div class="relation-links">${{links}}</div>
              </div>
            `;
          }}

          function sourceBlock(ids) {{
            const links = (ids || [])
              .map((id) => byId.get(id))
              .filter(Boolean)
              .map((source) => {{
                const href = source.url ? `<a class="relation-link" href="${{escapeHtml(source.url)}}" target="_blank" rel="noreferrer">${{escapeHtml(source.title)}}</a>` : `<span class="relation-link">${{escapeHtml(source.title)}}</span>`;
                return href;
              }})
              .join("");
            if (!links) return "";
            return `
              <div class="relation-group">
                <h4>근거·출처</h4>
                <div class="relation-links">${{links}}</div>
              </div>
            `;
          }}

          function formatKrw(value) {{
            if (value === undefined || value === null || value === "") return "";
            const number = Number(value);
            return Number.isFinite(number) ? `${{number.toLocaleString("ko-KR")}}원` : String(value);
          }}

          function formatPercent(value) {{
            if (value === undefined || value === null || value === "") return "";
            return `${{value}}%`;
          }}

          function criteriaBlock(criteria) {{
            if (!criteria || !criteria.length) return "";
            const labels = {{
              basis: "기준항목",
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
              max_amount_krw: "최대금액",
              benefit: "혜택",
              note: "비고"
            }};
            const orderedKeys = [
              "basis",
              "condition",
              "threshold_krw_min",
              "threshold_krw",
              "threshold_krw_max",
              "rate_percent",
              "rate_percent_min",
              "rate_percent_max",
              "progressive_deduction_krw",
              "deduction_krw",
              "limit_krw",
              "amount_krw",
              "max_amount_krw",
              "benefit",
              "note"
            ];
            const items = criteria.map((criterion) => {{
              const detail = orderedKeys
                .filter((key) => criterion[key] !== undefined && criterion[key] !== null && criterion[key] !== "")
                .map((key) => {{
                  let value = criterion[key];
                  if (key.endsWith("_krw")) value = formatKrw(value);
                  if (key.startsWith("rate_percent")) value = formatPercent(value);
                  return `<span>${{escapeHtml(labels[key] || key)}}: <strong>${{escapeHtml(value)}}</strong></span>`;
                }})
                .join("");
              const source = criterion.source ? byId.get(criterion.source) : null;
              const sourceLink = source ? `<button class="relation-link" type="button" data-select-item="${{escapeHtml(source.id)}}">${{escapeHtml(source.title)}}</button>` : "";
              return `
                <li>
                  <strong>${{escapeHtml(criterion.label || "기준")}}</strong>
                  <div>${{detail}}</div>
                  ${{sourceLink ? `<p>${{sourceLink}}</p>` : ""}}
                </li>
              `;
            }}).join("");
            return `
              <div class="criteria-block">
                <h4>기준 내역</h4>
                <ul>${{items}}</ul>
              </div>
            `;
          }}

          function renderDetail() {{
            const item = byId.get(state.selectedId) || byId.get("kr-tax-system") || items[0];
            if (!item) {{
              detailEl.innerHTML = `
                <div class="detail-kicker">검색 결과 없음</div>
                <h3>선택할 항목이 없습니다</h3>
                <p>검색어를 줄이거나 다른 필터를 선택해 주세요.</p>
              `;
              return;
            }}
            const relationHtml = [
              relationBlock("상위 항목", item.parents),
              relationBlock("하위 항목", item.children),
              relationBlock("관련 항목", item.related),
              relationBlock("관련 용어", item.terms),
              relationBlock("관련 기한", item.deadlines),
              sourceBlock(item.sources)
            ].filter(Boolean).join("");
            const criteriaHtml = criteriaBlock(item.criteria);

            detailEl.innerHTML = `
              <div class="detail-kicker">${{escapeHtml(typeLabels[item.type] || item.type)}} · ${{escapeHtml(item.id)}}</div>
              <h3>${{escapeHtml(item.title)}}</h3>
              <p>${{escapeHtml(item.description)}}</p>
              <div class="meta-grid">
                <div><span>기준연도</span><strong>${{escapeHtml(item.basis_year || "해당 없음")}}</strong></div>
                <div><span>법령 근거</span><strong>${{escapeHtml(item.law_reference || "출처 노드 참조")}}</strong></div>
                <div><span>폴더</span><strong>${{escapeHtml(item.folder || "-")}}</strong></div>
                <div><span>태그</span><strong>${{escapeHtml((item.tags || []).join(", ") || "-")}}</strong></div>
              </div>
              ${{criteriaHtml}}
              <div class="relations">${{relationHtml || "<p>연결된 관계가 없습니다.</p>"}}</div>
            `;
          }}

          function renderTypeTable() {{
            const counts = ONTOLOGY_DATA.summary.type_counts;
            typeTableEl.innerHTML = Object.keys(counts)
              .sort((a, b) => (typeLabels[a] || a).localeCompare(typeLabels[b] || b, "ko"))
              .map((type) => `
                <tr>
                  <td><strong>${{escapeHtml(typeLabels[type] || type)}}</strong><br><span>${{escapeHtml(type)}}</span></td>
                  <td>${{Number(counts[type]).toLocaleString("ko-KR")}}</td>
                  <td>${{escapeHtml(typeRoles[type] || "온톨로지 노드")}}</td>
                </tr>
              `)
              .join("");
          }}

          function renderSources() {{
            const sources = items
              .filter((item) => item.type === "source")
              .sort((a, b) => (a.publisher || "").localeCompare(b.publisher || "", "ko") || a.title.localeCompare(b.title, "ko"));

            sourceListEl.innerHTML = sources
              .map((source) => `
                <article class="source-card">
                  <span>${{escapeHtml(source.publisher || "공식 출처")}} · ${{escapeHtml(source.basis_date || ONTOLOGY_DATA.basis_date)}}</span>
                  <strong>${{escapeHtml(source.title)}}</strong>
                  <p>${{escapeHtml(source.description)}}</p>
                  ${{source.url ? `<a href="${{escapeHtml(source.url)}}" target="_blank" rel="noreferrer">원문 열기</a>` : ""}}
                </article>
              `)
              .join("");
          }}

          function downloadJson() {{
            const exportData = {{
              version: ONTOLOGY_DATA.version,
              basis_date: ONTOLOGY_DATA.basis_date,
              manifests: ONTOLOGY_DATA.manifests,
              items: ONTOLOGY_DATA.items
            }};
            const blob = new Blob([JSON.stringify(exportData, null, 2)], {{ type: "application/json" }});
            const url = URL.createObjectURL(blob);
            const anchor = document.createElement("a");
            anchor.href = url;
            anchor.download = "korea-tax-ontology-2026.json";
            document.body.appendChild(anchor);
            anchor.click();
            anchor.remove();
            URL.revokeObjectURL(url);
          }}

          document.addEventListener("click", (event) => {{
            const selectButton = event.target.closest("[data-select-item]");
            if (selectButton) {{
              const id = selectButton.getAttribute("data-select-item");
              if (byId.has(id)) {{
                state.selectedId = id;
                renderList();
                renderDetail();
                document.querySelector("#browser")?.scrollIntoView({{ behavior: "smooth", block: "start" }});
              }}
            }}

            const tabButton = event.target.closest("[data-tab]");
            if (tabButton) {{
              state.tab = tabButton.getAttribute("data-tab");
              renderTabs();
              renderList();
              renderDetail();
            }}

            if (event.target.closest("[data-download-json]")) {{
              downloadJson();
            }}
          }});

          searchInput.addEventListener("input", (event) => {{
            state.query = event.target.value;
            renderList();
            renderDetail();
          }});

          renderTypeTable();
          renderSources();
          renderTabs();
          renderList();
          renderDetail();
        }})();
        """
    )


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
