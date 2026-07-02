const DATA_BASE = "../opentax/";
const MANIFEST_FILE = "finance-ontology-manifest.json";
const MAX_RESULTS = 120;

const DOMAIN_META = {
  tax: {
    label: "세금·공제",
    short: "Tax",
    className: "tax",
    summary: "세금, 공제, 신고기한, 중앙 정책지원 핵심 노드",
  },
  "local-government-supports": {
    label: "지자체 지원금",
    short: "Local Supports",
    className: "local",
    summary: "정부24 보조금24 기준 전국 지자체 지원사업",
  },
  "card-products": {
    label: "카드 상품",
    short: "Cards",
    className: "card",
    summary: "신용카드·체크카드 혜택, 카드대출, 리볼빙, 전월실적, 한도",
  },
  "bank-products": {
    label: "예금·대출 상품",
    short: "Banks",
    className: "bank",
    summary: "예금·적금·대출, 정책대출, 리스·할부금융 금리와 한도",
  },
  "insurance-products": {
    label: "보험 상품",
    short: "Insurance",
    className: "insurance",
    summary: "보험료, 보장, 면책, 갱신, 약관 출처",
  },
};

const numberFormat = new Intl.NumberFormat("ko-KR");
const state = {
  manifest: null,
  currentDomain: "tax",
  items: [],
  loadedDomains: new Map(),
  itemIndex: new Map(),
  selectedId: "",
  isLoadingAll: false,
};

document.addEventListener("DOMContentLoaded", init);

async function init() {
  bindStaticControls();
  renderLoadingTabs();

  try {
    state.manifest = await fetchJson(DATA_BASE + MANIFEST_FILE);
    updateManifestUI();
    renderOperationalSummary();
    renderExportCards();
    renderDomainTabs();

    const hashId = decodeURIComponent(window.location.hash.replace(/^#/, ""));
    if (hashId) {
      await loadAllDomains();
      selectItem(hashId, { updateHash: false });
    } else {
      await loadDomain("tax");
    }
  } catch (error) {
    showFatalError(error);
  }
}

function bindStaticControls() {
  document.querySelector("[data-search]")?.addEventListener("input", renderResults);
  document.querySelector("[data-type-filter]")?.addEventListener("change", renderResults);
  document.querySelector("[data-load-all]")?.addEventListener("click", () => loadAllDomains());

  document.querySelectorAll("[data-domain]").forEach((node) => {
    node.addEventListener("click", async (event) => {
      const domain = event.currentTarget.dataset.domain;
      if (!domain) return;
      event.preventDefault();
      if (domain === "all") {
        await loadAllDomains();
      } else {
        await loadDomain(domain);
      }
      document.querySelector("#explorer")?.scrollIntoView({ block: "start" });
    });
  });
}

async function fetchJson(url) {
  const response = await fetch(url, { cache: "no-store", headers: { accept: "application/json" } });
  if (!response.ok) {
    throw new Error(`${url} 로딩 실패: ${response.status} ${response.statusText}`);
  }
  return response.json();
}

function updateManifestUI() {
  const manifest = state.manifest;
  const exports = manifest.exports || [];
  const exportItemTotal = exports.reduce((sum, item) => sum + Number(item.item_count || 0), 0);
  const totalItems = Number(manifest.item_count || manifest.unique_item_count || exportItemTotal);
  const productItems = exports.reduce((sum, item) => sum + Number(item.product_count || 0), 0);
  const localCount = exports.find((item) => item.domain === "local-government-supports")?.item_count || 0;
  const versionShort = String(manifest.version || "").replace("-2026.05.05.1", "");
  const sourceReviewDate = manifest.source_review_date || manifest.basis_date || "unknown";
  const productCollectionDates = financeCollectionLabel(manifest);

  setText("[data-version]", manifest.version || "unknown");
  setText("[data-version-short]", versionShort || "KR-FINANCE-ONTOLOGY");
  setText("[data-basis-date]", manifest.basis_date || "unknown");
  setText("[data-basis-date-short]", manifest.basis_date || "unknown");
  setText("[data-source-review-date]", sourceReviewDate);
  setText("[data-product-collection-dates]", productCollectionDates || "미기록");
  setText("[data-total-items]", `${formatNumber(totalItems)} items`);
  setText("[data-total-items-plain]", formatNumber(totalItems));
  setText("[data-export-count]", formatNumber(exports.length));
  setText("[data-product-count]", formatNumber(productItems));
  setText("[data-local-count]", formatNumber(localCount));

  exports.forEach((entry) => {
    document.querySelectorAll(`[data-domain-count="${entry.domain}"]`).forEach((node) => {
      node.textContent = formatNumber(entry.item_count || 0);
    });
  });
}

function renderExportCards() {
  const grid = document.querySelector("[data-export-grid]");
  if (!grid) return;

  grid.innerHTML = (state.manifest.exports || [])
    .map((entry) => {
      const meta = domainMeta(entry.domain);
      const filename = fileNameFromEntry(entry);
      const collectionDates = collectionDatesForEntry(entry);
      const quality = qualityLine(entry.quality_summary);
      return `
        <article class="export-card ${meta.className}">
          <span class="domain-chip">${escapeHtml(meta.label)}</span>
          <h3>${escapeHtml(meta.short)}</h3>
          <div class="export-count">
            <strong>${formatNumber(entry.item_count || 0)}</strong>
            <span>items</span>
          </div>
          <p>${escapeHtml(entry.description || meta.summary)}</p>
          <p>${formatNumber(entry.product_count || 0)} product nodes · 수집일 ${escapeHtml(collectionDates || "미기록")} · ${escapeHtml(filename)}</p>
          ${quality ? `<p>${escapeHtml(quality)}</p>` : ""}
          <button type="button" data-load-domain="${escapeHtml(entry.domain)}">탐색기에 로드</button>
        </article>
      `;
    })
    .join("");

  grid.querySelectorAll("[data-load-domain]").forEach((button) => {
    button.addEventListener("click", async () => {
      await loadDomain(button.dataset.loadDomain);
      document.querySelector("#explorer")?.scrollIntoView({ block: "start" });
    });
  });
}

function financeCollectionLabel(manifest) {
  const labels = {
    "card-products": "카드",
    "bank-products": "은행·대출",
    "insurance-products": "보험",
  };
  return (manifest.exports || [])
    .filter((entry) => Number(entry.product_count || 0) > 0)
    .map((entry) => {
      const dates = collectionDatesForEntry(entry);
      return dates ? `${labels[entry.domain] || entry.domain} ${dates}` : "";
    })
    .filter(Boolean)
    .join(" · ");
}

function collectionDatesForEntry(entry) {
  return [...new Set(entry.product_collection_dates || [])].join(", ");
}

function renderLoadingTabs() {
  const tabs = document.querySelector("[data-domain-tabs]");
  if (tabs) {
    tabs.innerHTML = `<button type="button" class="active">manifest 로딩 중</button>`;
  }
}

function renderDomainTabs() {
  const tabs = document.querySelector("[data-domain-tabs]");
  if (!tabs) return;

  const buttons = [
    `<button type="button" data-tab-domain="all">전체</button>`,
    ...(state.manifest.exports || []).map((entry) => {
      const meta = domainMeta(entry.domain);
      return `<button type="button" data-tab-domain="${escapeHtml(entry.domain)}">${escapeHtml(meta.label)}</button>`;
    }),
  ];
  tabs.innerHTML = buttons.join("");

  tabs.querySelectorAll("[data-tab-domain]").forEach((button) => {
    button.addEventListener("click", async () => {
      const domain = button.dataset.tabDomain;
      if (domain === "all") {
        await loadAllDomains();
      } else {
        await loadDomain(domain);
      }
    });
  });

  markActiveDomainTab();
}

async function loadDomain(domain) {
  if (!domain) return;
  state.currentDomain = domain;
  markActiveDomainTab();
  setResultSummary(`${domainMeta(domain).label} 데이터를 로딩 중입니다.`);

  if (!state.loadedDomains.has(domain)) {
    const entry = findExport(domain);
    if (!entry) {
      setResultSummary(`${domain} export를 manifest에서 찾을 수 없습니다.`);
      return;
    }
    const payload = await fetchJson(DATA_BASE + fileNameFromEntry(entry));
    const items = [...(payload.reference_items || []), ...(payload.items || [])].map((item) => ({
      ...item,
      __domain: domain,
      __exportId: entry.id,
    }));
    state.loadedDomains.set(domain, items);
    mergeItems(items);
  }

  updateTypeFilter();
  renderResults();
  selectFirstVisibleResult();
}

async function loadAllDomains() {
  if (state.isLoadingAll) return;
  state.isLoadingAll = true;
  state.currentDomain = "all";
  markActiveDomainTab();
  setResultSummary("전체 export를 로딩 중입니다. 대용량 지자체 지원금 파일을 포함합니다.");

  try {
    for (const entry of state.manifest.exports || []) {
      if (!state.loadedDomains.has(entry.domain)) {
        await loadDomain(entry.domain);
      }
    }
    state.currentDomain = "all";
    markActiveDomainTab();
    updateTypeFilter();
    renderResults();
    selectFirstVisibleResult();
  } finally {
    state.isLoadingAll = false;
  }
}

function mergeItems(items) {
  for (const item of items) {
    if (!state.itemIndex.has(item.id)) {
      state.items.push(item);
      state.itemIndex.set(item.id, item);
    }
  }
}

function renderResults() {
  const container = document.querySelector("[data-results]");
  if (!container) return;

  const query = normalize(document.querySelector("[data-search]")?.value || "");
  const type = document.querySelector("[data-type-filter]")?.value || "";
  const sourceItems = currentItems();
  const filtered = sourceItems
    .map((item, index) => ({ item, index, score: scoreItem(item, query) }))
    .filter(({ item, score }) => (!query || score > 0) && (!type || item.type === type) && isSearchVisible(item, query))
    .sort((a, b) => (query ? b.score - a.score : a.index - b.index) || a.item.title.localeCompare(b.item.title, "ko-KR"));
  const visible = filtered.slice(0, MAX_RESULTS);

  setResultSummary(resultSummary(filtered.length, sourceItems.length, visible.length));
  container.innerHTML = visible.map(({ item }) => resultItemHtml(item)).join("") || `<p class="empty-state">검색 결과가 없습니다.</p>`;

  container.querySelectorAll("[data-select-id]").forEach((button) => {
    button.addEventListener("click", () => selectItem(button.dataset.selectId));
  });

  markActiveResult();
}

function resultSummary(filteredCount, sourceCount, visibleCount) {
  const scope = state.currentDomain === "all" ? "전체 로드된 도메인" : domainMeta(state.currentDomain).label;
  if (!sourceCount) return `${scope}: 아직 로드된 항목이 없습니다.`;
  if (filteredCount > visibleCount) {
    return `${scope}: ${formatNumber(filteredCount)}개 중 상위 ${formatNumber(visibleCount)}개 표시`;
  }
  return `${scope}: ${formatNumber(filteredCount)}개 표시`;
}

function resultItemHtml(item) {
  const meta = domainMeta(item.__domain);
  const status = item.status || item.product_status || item.abolition_status || "";
  return `
    <button type="button" class="result-item" data-select-id="${escapeAttribute(item.id)}">
      <strong>${escapeHtml(item.title || item.id)}</strong>
      <div class="item-meta">
        <span>${escapeHtml(meta.label)}</span>
        <span>${escapeHtml(item.type || "unknown")}</span>
        ${status ? `<span class="status-chip ${escapeAttribute(statusClass(status))}">${escapeHtml(status)}</span>` : ""}
        ${item.provider ? `<span>${escapeHtml(item.provider)}</span>` : ""}
      </div>
      <p>${escapeHtml(item.description || "설명이 없습니다.")}</p>
    </button>
  `;
}

function selectFirstVisibleResult() {
  const first = document.querySelector("[data-results] [data-select-id]");
  const visibleSelected = [...document.querySelectorAll("[data-results] [data-select-id]")]
    .some((button) => button.dataset.selectId === state.selectedId);
  if (first && !visibleSelected) {
    selectItem(first.dataset.selectId, { updateHash: false });
  } else if (state.selectedId) {
    const selected = state.itemIndex.get(state.selectedId);
    if (selected) renderDetail(selected);
  }
}

function selectItem(id, options = {}) {
  if (!id) return;
  const item = state.itemIndex.get(id);
  if (!item) {
    renderMissingItem(id);
    return;
  }

  state.selectedId = id;
  renderDetail(item);
  markActiveResult();

  if (options.updateHash !== false) {
    history.replaceState(null, "", `#${encodeURIComponent(id)}`);
  }
}

function renderDetail(item) {
  const panel = document.querySelector("[data-detail-panel]");
  if (!panel) return;

  const meta = domainMeta(item.__domain);
  const kv = pickFields(item, [
    ["id", "ID"],
    ["type", "Type"],
    ["provider", "Provider"],
    ["financial_sector", "Sector"],
    ["product_kind", "Product kind"],
    ["product_code", "Product code"],
    ["status", "Status"],
    ["status_reason", "Status reason"],
    ["status_confidence", "Status confidence"],
    ["product_status", "Product status"],
    ["sales_status", "Sales status"],
    ["recommendation_status", "Recommendation"],
    ["effective_from", "Effective from"],
    ["effective_to", "Effective to"],
    ["application_open_from", "Application from"],
    ["application_open_to", "Application to"],
    ["disclosure_month", "Disclosure"],
    ["basis_year", "Basis year"],
    ["reviewed_at", "Reviewed"],
    ["last_verified_at", "Last verified"],
    ["source_modified_at", "Source modified"],
    ["jurisdiction", "Jurisdiction"],
    ["law_reference", "Law"],
    ["source_api", "Source API"],
  ]);

  panel.innerHTML = `
    <span class="domain-chip">${escapeHtml(meta.label)}</span>
    <h3>${escapeHtml(item.title || item.id)}</h3>
    <p class="detail-description">${escapeHtml(item.description || "설명이 없습니다.")}</p>
    ${kv.length ? renderKvGrid(kv) : ""}
    ${renderCriteria(item.criteria)}
    ${renderOptions(item.options)}
    ${renderPills("Tags", item.tags)}
    ${renderNeighbors(item)}
    ${renderSources(item)}
  `;
}

function renderMissingItem(id) {
  const panel = document.querySelector("[data-detail-panel]");
  if (!panel) return;
  panel.innerHTML = `
    <p class="empty-state">로드된 export에서 ${escapeHtml(id)} 항목을 찾지 못했습니다. 전체 인덱스 로딩 후 다시 시도하세요.</p>
  `;
}

function renderKvGrid(rows) {
  return `
    <dl class="detail-section kv-grid">
      ${rows
        .map(([label, value]) => `
          <div>
            <dt>${escapeHtml(label)}</dt>
            <dd>${escapeHtml(stringifyValue(value))}</dd>
          </div>
        `)
        .join("")}
    </dl>
  `;
}

function renderCriteria(criteria) {
  if (!Array.isArray(criteria) || !criteria.length) return "";
  const rows = criteria.slice(0, 6).map((criterion) => {
    const label = criterion.label || criterion.criteria_kind || criterion.basis_category || "기준";
    const body = criterion.condition || criterion.benefit || criterion.basis || criterion.basis_definition || stringifyValue(criterion);
    return `
      <article>
        <strong>${escapeHtml(label)}</strong>
        <p>${escapeHtml(body)}</p>
      </article>
    `;
  });
  const more = criteria.length > 6 ? `<p class="empty-state">외 ${formatNumber(criteria.length - 6)}개 기준은 원본 JSON에서 확인할 수 있습니다.</p>` : "";
  return `
    <section class="detail-section">
      <h4>Criteria</h4>
      <div class="criteria-list">${rows.join("")}${more}</div>
    </section>
  `;
}

function renderOptions(options) {
  if (!Array.isArray(options) || !options.length) return "";
  const rows = options.slice(0, 3).map((option, index) => {
    const compact = Object.entries(option)
      .filter(([, value]) => value !== null && value !== undefined && value !== "")
      .slice(0, 8)
      .map(([key, value]) => `${key}: ${stringifyValue(value)}`)
      .join(" · ");
    return `
      <article>
        <strong>Option ${index + 1}</strong>
        <p>${escapeHtml(compact)}</p>
      </article>
    `;
  });
  const more = options.length > 3 ? `<p class="empty-state">외 ${formatNumber(options.length - 3)}개 옵션은 원본 JSON에서 확인할 수 있습니다.</p>` : "";
  return `
    <section class="detail-section">
      <h4>Product Options</h4>
      <div class="criteria-list">${rows.join("")}${more}</div>
    </section>
  `;
}

function renderPills(title, values) {
  if (!Array.isArray(values) || !values.length) return "";
  return `
    <section class="detail-section">
      <h4>${escapeHtml(title)}</h4>
      <ul class="pill-list">
        ${values.slice(0, 28).map((value) => `<li>${escapeHtml(value)}</li>`).join("")}
      </ul>
    </section>
  `;
}

function renderNeighbors(item) {
  const groups = [
    ["Parents", item.parents],
    ["Children", item.children],
    ["Related", item.related],
    ["Terms", item.terms],
    ["Deadlines", item.deadlines],
    ["Sources", item.sources],
  ].filter(([, values]) => Array.isArray(values) && values.length);

  if (!groups.length) return "";

  return `
    <section class="detail-section">
      <h4>Graph Neighbors</h4>
      ${groups
        .map(([title, values]) => `
          <p class="empty-state">${escapeHtml(title)}</p>
          <ul class="pill-list">
            ${values.slice(0, 18).map((value) => `<li>${escapeHtml(value)}</li>`).join("")}
          </ul>
        `)
        .join("")}
    </section>
  `;
}

function renderSources(item) {
  const sourceUrls = Array.isArray(item.source_urls) ? item.source_urls : [];
  const sourceBasisDates = Array.isArray(item.source_basis_dates) ? item.source_basis_dates : [];
  if (!sourceUrls.length && !sourceBasisDates.length) return "";

  return `
    <section class="detail-section">
      <h4>Sources</h4>
      ${sourceBasisDates.length ? `<ul class="pill-list">${sourceBasisDates.slice(0, 12).map((value) => `<li>${escapeHtml(value)}</li>`).join("")}</ul>` : ""}
      ${sourceUrls.length ? `
        <div class="source-list">
          ${sourceUrls.slice(0, 8).map((url) => `<a href="${escapeAttribute(url)}" target="_blank" rel="noreferrer">${escapeHtml(url)}</a>`).join("")}
        </div>
      ` : ""}
    </section>
  `;
}

function updateTypeFilter() {
  const select = document.querySelector("[data-type-filter]");
  if (!select) return;
  const previous = select.value;
  const counts = new Map();
  for (const item of currentItems()) {
    if (item.type) counts.set(item.type, (counts.get(item.type) || 0) + 1);
  }
  const options = [...counts.entries()].sort((a, b) => b[1] - a[1] || a[0].localeCompare(b[0], "ko-KR"));
  select.innerHTML = `<option value="">모든 타입</option>${options
    .map(([type, count]) => `<option value="${escapeAttribute(type)}">${escapeHtml(type)} (${formatNumber(count)})</option>`)
    .join("")}`;
  if (options.some(([type]) => type === previous)) {
    select.value = previous;
  }
}

function currentItems() {
  if (state.currentDomain === "all") {
    return state.items;
  }
  return state.loadedDomains.get(state.currentDomain) || [];
}

function scoreItem(item, query) {
  if (!query) return 1;
  const title = normalize(item.title || "");
  const id = normalize(item.id || "");
  const text = normalize([
    item.id,
    item.title,
    item.type,
    item.description,
    item.provider,
    item.financial_sector,
    item.product_kind,
    item.product_code,
    item.jurisdiction,
    item.status,
    item.status_reason,
    item.status_confidence,
    item.recommendation_status,
    structuredSearchText(item.criteria, 4),
    structuredSearchText(item.options, 3),
    structuredSearchText(item.benefits, 3),
    ...(item.tags || []),
    ...(item.sources || []),
    ...(item.source_urls || []),
  ].filter(Boolean).join(" "));
  const tokens = query.split(/\s+/).filter(Boolean);

  if (id === query || title === query) return 100;
  if (id.includes(query)) return 80;
  if (title.includes(query)) return 70;
  if (text.includes(query)) return 40;

  const matched = tokens.filter((token) => text.includes(token)).length;
  if (tokens.length > 1 && matched === tokens.length) return 30 + matched;
  if (matched) return 10 + matched;
  return 0;
}

function renderOperationalSummary() {
  const container = document.querySelector("[data-operational-summary]");
  if (!container) return;
  const risks = state.manifest.source_access_risks || [];
  const financeExports = (state.manifest.exports || []).filter((entry) => entry.domain.endsWith("products"));
  const activeInsuranceGap = state.manifest.quality_summary?.finance_exports?.insurance?.active_insurance_without_criteria ?? 0;
  const riskLines = risks.slice(0, 5).map((risk) => `${risk.source_id}: ${risk.status}`).join(" · ");
  const qualityLines = financeExports
    .map((entry) => `${domainMeta(entry.domain).label} ${qualityLine(entry.quality_summary)}`)
    .filter((line) => line.trim())
    .join(" · ");
  container.innerHTML = `
    <article>
      <h3>상태 게이트</h3>
      <p>active 보험상품 criteria 빈 값 ${formatNumber(activeInsuranceGap)}건. 종료·불확실 상품은 기본 검색과 추천 후보에서 제외합니다.</p>
    </article>
    <article>
      <h3>출처 접근 리스크</h3>
      <p>${escapeHtml(riskLines || "현재 manifest에 기록된 출처 접근 리스크가 없습니다.")}</p>
    </article>
    <article>
      <h3>품질 요약</h3>
      <p>${escapeHtml(qualityLines || "품질 요약 로딩 전입니다.")}</p>
    </article>
  `;
}

function qualityLine(summary) {
  if (!summary) return "";
  const counts = summary.status_counts || {};
  const active = counts.active || 0;
  const closed = counts.closed || counts.ended || 0;
  const unknown = counts.unknown || 0;
  const referenceOnly = summary.reference_only_products || 0;
  return `active ${formatNumber(active)} · closed ${formatNumber(closed)} · unknown ${formatNumber(unknown)} · reference_only ${formatNumber(referenceOnly)}`;
}

function isSearchVisible(item, query) {
  if (!isInactiveOrUnverified(item)) return true;
  return hasInactiveIntent(query);
}

function isInactiveOrUnverified(item) {
  const status = normalize(item.status || item.product_status || item.abolition_status || "");
  const recommendation = normalize(item.recommendation_status || "");
  return ["closed", "ended", "sunset", "unknown", "suspended"].includes(status) || recommendation === "reference_only";
}

function hasInactiveIntent(query) {
  return /(종료|판매중단|중단|만료|unknown|closed|ended|reference|보류|불확실)/i.test(query);
}

function statusClass(status) {
  const normalized = normalize(status);
  if (normalized === "active") return "status-active";
  if (["closed", "ended", "sunset"].includes(normalized)) return "status-closed";
  return "status-unknown";
}

function structuredSearchText(value, limit) {
  if (!Array.isArray(value) || !value.length) return "";
  return value
    .slice(0, limit)
    .map((entry) => stringifyValue(entry))
    .join(" ");
}

function markActiveDomainTab() {
  document.querySelectorAll("[data-tab-domain]").forEach((button) => {
    button.classList.toggle("active", button.dataset.tabDomain === state.currentDomain);
  });
}

function markActiveResult() {
  document.querySelectorAll("[data-select-id]").forEach((button) => {
    button.classList.toggle("active", button.dataset.selectId === state.selectedId);
  });
}

function setResultSummary(text) {
  setText("[data-result-summary]", text);
}

function showFatalError(error) {
  const summary = document.querySelector("[data-result-summary]");
  if (summary) {
    summary.textContent = "OpenFin 데이터를 로드하지 못했습니다.";
  }
  const detail = document.querySelector("[data-detail-panel]");
  if (detail) {
    detail.innerHTML = `<p class="empty-state">${escapeHtml(error.message || String(error))}</p>`;
  }
  console.error(error);
}

function findExport(domain) {
  return (state.manifest.exports || []).find((entry) => entry.domain === domain);
}

function fileNameFromEntry(entry) {
  if (entry.web_url) {
    return new URL(entry.web_url).pathname.split("/").pop();
  }
  return String(entry.path || "").split("/").pop();
}

function domainMeta(domain) {
  return DOMAIN_META[domain] || {
    label: domain || "unknown",
    short: domain || "unknown",
    className: "unknown",
    summary: "",
  };
}

function pickFields(item, fields) {
  return fields
    .map(([key, label]) => [label, item[key]])
    .filter(([, value]) => value !== undefined && value !== null && value !== "");
}

function stringifyValue(value) {
  if (Array.isArray(value)) return value.join(", ");
  if (typeof value === "object" && value !== null) return JSON.stringify(value);
  return String(value);
}

function normalize(value) {
  return String(value).trim().toLocaleLowerCase("ko-KR");
}

function formatNumber(value) {
  return numberFormat.format(Number(value || 0));
}

function setText(selector, value) {
  document.querySelectorAll(selector).forEach((node) => {
    node.textContent = value;
  });
}

function escapeHtml(value) {
  return String(value ?? "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#39;");
}

function escapeAttribute(value) {
  return escapeHtml(value).replace(/`/g, "&#96;");
}
