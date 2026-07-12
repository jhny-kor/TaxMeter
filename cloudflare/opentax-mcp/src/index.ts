import { createMcpHandler } from "agents/mcp";
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { z } from "zod";

type FinanceItem = {
  id: string;
  title: string;
  type: string;
  description?: string;
  basis_year?: number;
  basis_date?: string;
  publisher?: string;
  url?: string;
  law_reference?: string;
  criteria?: unknown[];
  options?: unknown[];
  benefits?: unknown[];
  parents?: string[];
  children?: string[];
  related?: string[];
  terms?: string[];
  deadlines?: string[];
  sources?: string[];
  tags?: string[];
  provider?: string;
  provider_code?: string;
  financial_sector?: string;
  product_code?: string;
  product_kind?: string;
  search_type?: string;
  product_status?: string;
  sales_status?: string;
  source_listing_status?: string;
  sales_verification_status?: string;
  sales_verified_at?: string;
  condition_verification_status?: string;
  source_freshness_status?: string;
  status?: string;
  status_reason?: string;
  recommendation_status?: string;
  recommendation_scope?: string;
  recommendation_model_version?: string;
  recommendation_exclusion_reasons?: string[];
  recommendation_basis_fields?: string[];
  comparison_basis_fields?: string[];
  verification_status?: string;
  quality_flags?: string[];
  verification_evidence?: Record<string, unknown>;
  missing_required_fields?: string[];
  missing_in_source_fields?: string[];
  unmapped_existing_fields?: string[];
  unverified_fields?: string[];
  discovery_evidence_fields?: string[];
  completeness_ratio?: number;
  source_completeness_ratio?: number;
  normalized_completeness_ratio?: number;
  verified_completeness_ratio?: number;
  required_field_count?: number;
  completed_field_count?: number;
  domain_gate_passed?: boolean;
  comparison_options?: unknown[];
  application_status?: string;
  is_currently_applicable?: boolean;
  application_open_from?: string;
  application_open_to?: string;
  jurisdiction?: string;
  jurisdiction_code?: string;
  jurisdiction_aliases?: string[];
  freshness_status?: string;
  collection_status?: string;
  last_verified_at?: string;
  export_id?: string;
  search_text?: string;
  search_aliases?: string[];
  legacy_ids?: string[];
  aliases?: string[];
  source_urls?: string[];
  source_basis_dates?: string[];
  source_checksum?: string;
  structured_summary?: Record<string, unknown>;
  search_facets?: Record<string, unknown>;
};

type OntologyExport = {
  version: string;
  basis_date: string;
  domain?: string;
  items: FinanceItem[];
  reference_items?: FinanceItem[];
};

type ManifestEntry = {
  id: string;
  domain: string;
  path: string;
  url?: string;
  web_url?: string;
  item_count?: number;
  product_count?: number;
  description?: string;
};

type FinanceManifest = {
  version: string;
  basis_date: string;
  name: string;
  description?: string;
  search_index?: ManifestEntry;
  quality_exports?: ManifestEntry[];
  exports: ManifestEntry[];
};

type FinanceGraph = {
  version: string;
  basis_date: string;
  manifest: FinanceManifest;
  exports: ManifestEntry[];
  items: FinanceItem[];
};

type CachedGraph = {
  data: FinanceGraph;
  loadedAt: number;
};

type SearchIndex = {
  version: string;
  basis_date: string;
  items: FinanceItem[];
};

type CachedSearchIndex = {
  data: SearchIndex;
  loadedAt: number;
};

type SearchFilters = {
  readonly searchType?: string;
  readonly productKind?: string;
  readonly recommendationStatus?: string;
  readonly recommendationScope?: string;
  readonly salesStatus?: string;
  readonly applicationStatus?: string;
  readonly provider?: string;
  readonly region?: string;
  readonly freshnessStatus?: string;
};

const CACHE_TTL_MS = 5 * 60 * 1000;
const DEFAULT_FINANCE_MANIFEST_URL =
  "https://jhny-kor.github.io/TaxMeter/opentax/finance-ontology-manifest.json";
const DEFAULT_FINANCE_WEB_BASE_URL = "https://jhny-kor.github.io/TaxMeter/opentax/";
const OPENAI_APPS_CHALLENGE_PATH = "/.well-known/openai-apps-challenge";
const RATE_QUERY_RE = /(금리|최고금리|중도해지|정기예금|적금|대출|개월)/i;
const PROTECTION_QUERY_RE = /(예금자보호|보호대상|보호상품|kdic|보호)/i;
const INACTIVE_QUERY_RE = /(종료|판매중단|중단|만료|마감|지난|unknown|closed|ended|reference|보류|불확실)/i;
const RECOMMENDATION_QUERY_RE = /(추천|골라|맞는\s*상품|recommend)/i;
const DISCOVERY_ACTION_RE = /(추천|알려줘|골라줘|찾아줘|괜찮은|좋은|후보|비교|순위|해줘|해주세요)/i;
const DISCOVERY_DOMAIN_TOKENS = {
  card: ["카드", "체크카드", "신용카드", "마일리지", "구독"],
  loan: ["대출", "신용대출", "전세대출", "월세대출"],
  insurance: ["보험", "실손", "실비", "암보험", "비갱신"],
  deposit: ["예금", "정기예금"],
  saving: ["적금", "자유적금"],
} as const;
type DiscoveryDomain = keyof typeof DISCOVERY_DOMAIN_TOKENS;
const GENERIC_SEARCH_TYPES = new Set(["category", "term", "domain", "source"]);
const TAX_DECISION_TYPES = new Set(["tax-credit", "deduction"]);
const READ_ONLY_TOOL_ANNOTATIONS = {
  readOnlyHint: true,
  destructiveHint: false,
  idempotentHint: true,
  openWorldHint: false,
} as const;

let cachedGraph: CachedGraph | undefined;
let cachedManifest: { data: FinanceManifest; loadedAt: number } | undefined;
let cachedSearchIndex: CachedSearchIndex | undefined;

function jsonText(value: unknown): string {
  return JSON.stringify(value, null, 2);
}

function normalizeQuery(value: string): string {
  return value.trim().toLocaleLowerCase("ko-KR");
}

function queryTokens(query: string): string[] {
  return normalizeQuery(query)
    .split(/\s+/)
    .map((token) => token.trim())
    .filter(Boolean);
}

function financeManifestUrl(env: Env): string {
  return env.FINANCE_MANIFEST_URL || DEFAULT_FINANCE_MANIFEST_URL;
}

function financeWebBaseUrl(env: Env): string {
  return env.FINANCE_WEB_BASE_URL || DEFAULT_FINANCE_WEB_BASE_URL;
}

function itemUrl(env: Env, itemId: string): string {
  return `${financeWebBaseUrl(env).replace(/\/?$/, "/")}#${encodeURIComponent(itemId)}`;
}

// type=tax must also match tax decision types (tax-credit, deduction, ...) so
// typed queries like "연말정산 의료비 세액공제" do not fall through to unrelated tax nodes.
const SEARCH_TYPE_GROUPS: Record<string, Set<string>> = {
  tax: new Set([
    "tax",
    "tax-credit",
    "tax-reduction",
    "deduction",
    "corporate-tax-support",
    "official-tax-item",
    "filing",
    "deadline",
    "required-document",
    "eligibility-rule",
  ]),
  "tax-support": new Set(["required-document"]),
  "tax-rule": new Set(["eligibility-rule"]),
};

const TAX_INTENT_RE = /(세액공제|소득공제|연말정산|원천징수|종합소득세|부가가치세|법인세|교육비|의료비|월세|연금계좌)/;

function inferredTypesForQuery(query: string): Set<string> | null {
  if (TAX_INTENT_RE.test(query)) {
    return SEARCH_TYPE_GROUPS.tax;
  }
  if (query.includes("보험")) {
    return new Set(["insurance-product"]);
  }
  if (["카드", "체크카드", "신용카드"].some((token) => query.includes(token))) {
    return new Set(["card-product"]);
  }
  return null;
}

function inferredSearchTypeForQuery(query: string): string | undefined {
  if (TAX_INTENT_RE.test(query)) {
    return undefined;
  }
  if (query.includes("정기예금") || query.includes("예금")) {
    return "deposit";
  }
  if (query.includes("적금")) {
    return "saving";
  }
  if (query.includes("대출")) {
    return "loan";
  }
  return undefined;
}

function itemSearchText(item: FinanceItem): string {
  if (item.search_text) {
    return item.search_text.toLocaleLowerCase("ko-KR");
  }
  return [
    item.id,
    item.title,
    item.type,
    item.description,
    item.law_reference,
    item.url,
    item.publisher,
    item.provider,
    item.provider_code,
    item.financial_sector,
    item.product_code,
    item.product_kind,
    item.search_type,
    item.product_status,
    item.sales_status,
    item.status,
    item.status_reason,
    item.recommendation_status,
    item.recommendation_scope,
    item.application_status,
    item.application_open_from,
    item.application_open_to,
    item.jurisdiction,
    item.jurisdiction_code,
    ...(item.jurisdiction_aliases ?? []),
    item.freshness_status,
    item.collection_status,
    JSON.stringify(item.structured_summary ?? {}),
    JSON.stringify(item.search_facets ?? {}),
    structuredSearchText(item.criteria),
    structuredSearchText(item.options),
    structuredSearchText(item.benefits),
    ...(item.tags ?? []),
    ...(item.sources ?? []),
    ...(item.source_urls ?? []),
  ]
    .filter(Boolean)
    .join(" ")
    .toLocaleLowerCase("ko-KR");
}

function structuredSearchText(value: unknown[] | undefined): string {
  return (value ?? []).map((entry) => JSON.stringify(entry)).join(" ");
}

function matchesRecommendationDomain(item: FinanceItem, query: string, searchType: string): boolean {
  if (query.includes("보험")) {
    return item.type === "insurance-product";
  }
  if (["카드", "체크카드", "신용카드"].some((token) => query.includes(token))) {
    return item.type === "card-product";
  }
  if (query.includes("대출")) {
    return searchType === "loan";
  }
  if (query.includes("정기예금") || query.includes("예금")) {
    return searchType === "deposit";
  }
  if (query.includes("적금")) {
    return searchType === "saving";
  }
  return true;
}

function matchesSearchFilters(item: FinanceItem, filters: SearchFilters): boolean {
  const equals = (value: string | undefined, expected: string | undefined): boolean =>
    expected === undefined || normalizeQuery(value ?? "") === normalizeQuery(expected);
  const region = normalizeQuery(filters.region ?? "");
  return (
    equals(item.search_type, filters.searchType) &&
    equals(item.product_kind, filters.productKind) &&
    equals(item.recommendation_status, filters.recommendationStatus) &&
    equals(item.recommendation_scope, filters.recommendationScope) &&
    equals(item.sales_status, filters.salesStatus) &&
    equals(item.application_status, filters.applicationStatus) &&
    equals(item.provider, filters.provider) &&
    equals(item.freshness_status, filters.freshnessStatus) &&
    (!region || [item.jurisdiction, item.jurisdiction_code, ...(item.jurisdiction_aliases ?? [])]
      .some((value) => normalizeQuery(value ?? "").includes(region)))
  );
}

function isRecommendationSearchEligible(item: FinanceItem): boolean {
  return recommendationBlocker(item) === undefined;
}

function isPubliclySearchable(item: FinanceItem): boolean {
  return item.recommendation_scope !== "internal_verification_candidate" && item.recommendation_status !== "manual_review_candidate";
}

function discoveryDomainForQuery(query: string): DiscoveryDomain | undefined {
  for (const [domain, tokens] of Object.entries(DISCOVERY_DOMAIN_TOKENS) as readonly [DiscoveryDomain, readonly string[]][]) {
    if (tokens.some((token) => normalizeQuery(query).includes(normalizeQuery(token)))) return domain;
  }
  return undefined;
}

function discoveryDomainForItem(item: FinanceItem): DiscoveryDomain | undefined {
  if (item.type === "card-product") return "card";
  if (item.type === "insurance-product") return "insurance";
  if (item.search_type === "loan" || item.search_type === "deposit" || item.search_type === "saving") return item.search_type;
  return undefined;
}

function isDiscoveryCandidate(item: FinanceItem, domain: DiscoveryDomain): boolean {
  if (discoveryDomainForItem(item) !== domain) return false;
  if (item.product_status !== "active" || item.status !== "active" || item.source_freshness_status === "stale") return false;
  if (!item.source_urls?.length || (item.source_listing_status !== undefined && item.source_listing_status !== "listed")) return false;
  const evidence = new Set(item.discovery_evidence_fields ?? []);
  if (domain === "card") return Boolean(item.title && item.provider && item.product_kind && (["benefit_type", "benefit_rate_or_amount", "benefit_categories"].some((field) => evidence.has(field))));
  if (domain === "loan") return Boolean(item.provider && item.product_kind && ["loan_rate_min_percent", "loan_rate_max_percent", "loan_limit_krw"].some((field) => evidence.has(field)));
  if (domain === "insurance") return Boolean(item.product_kind && ["coverage_amount_krw", "premium_basis", "renewal_type"].some((field) => evidence.has(field)));
  return Boolean(item.comparison_options?.length || evidence.size);
}

function discoveryConfidence(item: FinanceItem): "A" | "B" | "C" | "D" {
  const ratio = item.normalized_completeness_ratio ?? item.completeness_ratio ?? 0;
  if (ratio >= 0.8) return "A";
  if (ratio >= 0.5) return "B";
  if (ratio >= 0.25) return "C";
  return "D";
}

function discoveryPayload(query: string, items: readonly FinanceItem[], limit: number): Record<string, unknown> {
  const domain = discoveryDomainForQuery(query);
  if (!domain) return { recommendation_mode: "discovery", label: "탐색 결과", query, candidates: [], warnings: ["상품 유형을 특정할 수 없어 탐색 후보를 만들지 않았습니다."] };
  const tokens = queryTokens(query).filter((token) => !DISCOVERY_ACTION_RE.test(token) && !DISCOVERY_DOMAIN_TOKENS[domain].some((domainToken) => normalizeQuery(domainToken) === normalizeQuery(token)));
  const candidates = items.filter((item) => isDiscoveryCandidate(item, domain)).map((item) => {
    const text = itemSearchText(item);
    const matched = tokens.filter((token) => text.includes(normalizeQuery(token)));
    const ratio = item.normalized_completeness_ratio ?? item.completeness_ratio ?? 0;
    const score = 35 + Math.min(20, matched.length * 10) + Math.round(ratio * 10) + (item.source_freshness_status === "current" ? 5 : 0);
    const limitations = ["탐색 후보이며 개인 적합성·승인·보험료·최적 상품을 판단하지 않습니다."];
    if (item.sales_verification_status !== "verified_active") limitations.push("공식 목록 기반 후보이므로 실제 판매·가입 가능 여부는 상세 페이지에서 재확인해야 합니다.");
    return {
      id: item.id, title: item.title, provider: item.provider, product_kind: item.product_kind, search_type: domain,
      recommendation_status: "discovery_candidate", recommendation_scope: "discovery_only", confidence_grade: discoveryConfidence(item), discovery_score: score,
      matched_conditions: matched.length ? matched : ["product_domain"], unmatched_conditions: [], unknown_conditions: tokens.filter((token) => !matched.includes(token)),
      missing_required_fields: item.missing_required_fields ?? [], why_included: "공식 출처의 현재 상품이며 탐색에 필요한 최소 구조 필드를 보유했습니다.", limitations,
      source_urls: item.source_urls ?? [], basis_dates: item.source_basis_dates ?? [], source_listing_status: item.source_listing_status,
      sales_verification_status: item.sales_verification_status, source_freshness_status: item.source_freshness_status,
      source_completeness_ratio: item.source_completeness_ratio, normalized_completeness_ratio: ratio, verified_completeness_ratio: item.verified_completeness_ratio,
    };
  }).sort((left, right) => Number(right.discovery_score) - Number(left.discovery_score) || Number(right.normalized_completeness_ratio ?? 0) - Number(left.normalized_completeness_ratio ?? 0) || String(left.id).localeCompare(String(right.id), "ko-KR"));
  return { recommendation_mode: "discovery", label: "탐색 후보", query, domain, result_count: Math.min(candidates.length, limit), candidates: candidates.slice(0, limit), excluded_count: items.filter((item) => discoveryDomainForItem(item) === domain).length - candidates.length, warnings: ["결과는 탐색용 후보입니다. 최적·승인·보험료·보장 적합성을 뜻하지 않습니다."] };
}

function scoreItem(item: FinanceItem, query: string): number {
  const normalizedTitle = normalizeQuery(item.title);
  const normalizedId = normalizeQuery(item.id);
  const searchType = normalizeQuery(item.search_type ?? item.product_kind ?? "");
  const status = normalizeQuery(item.status ?? item.product_status ?? "");
  const recommendationStatus = normalizeQuery(item.recommendation_status ?? "");
  const applicationStatus = normalizeQuery(item.application_status ?? "");
  const tokens = queryTokens(query);
  const titleTokens = queryTokens(normalizedTitle);
  const rateIntent = RATE_QUERY_RE.test(query);

  if (searchType === "deposit-protection" && rateIntent && !PROTECTION_QUERY_RE.test(query)) {
    return 0;
  }
  if (RECOMMENDATION_QUERY_RE.test(query)) {
    const intentTokens = tokens.filter((token) => !RECOMMENDATION_QUERY_RE.test(token));
    if (
      !isRecommendationSearchEligible(item) ||
      !matchesRecommendationDomain(item, query, searchType) ||
      !intentTokens.length
    ) {
      return 0;
    }
  }
  if (
    item.type === "support-program" &&
    (status === "closed" || status === "ended" || applicationStatus === "closed" || recommendationStatus === "reference_only") &&
    !INACTIVE_QUERY_RE.test(query)
  ) {
    return 0;
  }

  const text = itemSearchText(item);
  if (RECOMMENDATION_QUERY_RE.test(query)) {
    const intentTokens = tokens.filter((token) => !RECOMMENDATION_QUERY_RE.test(token));
    if (!intentTokens.every((token) => text.includes(token))) {
      return 0;
    }
  }
  let score = 0;
  const aliases = (item.search_aliases ?? []).map((alias) => normalizeQuery(alias));
  if (aliases.includes(query)) {
    score = 95;
  } else if (normalizedId === query || normalizedTitle === query) {
    score = 100;
  } else if (normalizedId.includes(query)) {
    score = 80;
  } else if (query.includes(normalizedTitle)) {
    const base = GENERIC_SEARCH_TYPES.has(item.type) && titleTokens.length < tokens.length ? 35 : 75;
    score = base + titleTokens.length;
  } else if (normalizedTitle.includes(query)) {
    score = 70;
  } else if (text.includes(query)) {
    score = 40;
  }
  if (tokens.length > 1) {
    const matchedTokens = tokens.filter((token) => text.includes(token));
    if (TAX_DECISION_TYPES.has(item.type) && matchedTokens.length >= Math.min(2, tokens.length)) {
      score = Math.max(score, 60 + matchedTokens.length);
    }
    if (!score && matchedTokens.length === tokens.length) {
      score = 30 + matchedTokens.length;
    }
    if (!score && matchedTokens.length > 0) {
      score = 10 + matchedTokens.length;
    }
  }
  if (score > 0 && rateIntent && ["deposit", "saving", "loan"].includes(searchType)) {
    score += 20;
  }
  return score;
}

async function fetchJson<T>(url: string): Promise<T> {
  const response = await fetch(url, {
    headers: {
      accept: "application/json",
      "user-agent": "finance-mcp-cloudflare-worker",
    },
  });

  if (!response.ok) {
    throw new Error(`Finance ontology fetch failed: ${url} ${response.status} ${response.statusText}`);
  }

  return (await response.json()) as T;
}

async function loadFinanceManifest(env: Env): Promise<FinanceManifest> {
  const now = Date.now();
  if (cachedManifest && now - cachedManifest.loadedAt < CACHE_TTL_MS) {
    return cachedManifest.data;
  }
  const manifest = await fetchJson<FinanceManifest>(financeManifestUrl(env));
  cachedManifest = { data: manifest, loadedAt: now };
  return manifest;
}

function resolveExportUrl(entry: ManifestEntry, manifestUrl: string): string {
  if (entry.web_url) {
    return entry.web_url;
  }
  if (entry.url) {
    return entry.url;
  }
  return new URL(entry.path, manifestUrl).toString();
}

async function loadSearchIndex(env: Env): Promise<SearchIndex> {
  const now = Date.now();
  if (cachedSearchIndex && now - cachedSearchIndex.loadedAt < CACHE_TTL_MS) {
    return cachedSearchIndex.data;
  }
  const manifestUrl = financeManifestUrl(env);
  const manifest = await loadFinanceManifest(env);
  if (!manifest.search_index) {
    const graph = await loadFinanceGraph(env);
    return { version: graph.version, basis_date: graph.basis_date, items: graph.items };
  }
  const indexUrl = resolveExportUrl(manifest.search_index, manifestUrl);
  const data = await fetchJson<SearchIndex>(indexUrl);
  cachedSearchIndex = { data, loadedAt: now };
  return data;
}

async function loadFinanceGraph(env: Env): Promise<FinanceGraph> {
  const now = Date.now();
  if (cachedGraph && now - cachedGraph.loadedAt < CACHE_TTL_MS) {
    return cachedGraph.data;
  }

  const manifestUrl = financeManifestUrl(env);
  const manifest = await loadFinanceManifest(env);
  const itemsById = new Map<string, FinanceItem>();

  for (const entry of manifest.exports) {
    const exportUrl = resolveExportUrl(entry, manifestUrl);
    const payload = await fetchJson<OntologyExport>(exportUrl);
    for (const item of [...(payload.reference_items ?? []), ...(payload.items ?? [])]) {
      if (!itemsById.has(item.id)) {
        itemsById.set(item.id, item);
      }
    }
  }

  const data = {
    version: manifest.version,
    basis_date: manifest.basis_date,
    manifest,
    exports: manifest.exports,
    items: [...itemsById.values()].sort((a, b) => a.id.localeCompare(b.id, "ko-KR")),
  };
  cachedGraph = { data, loadedAt: now };
  return data;
}

function indexItems(data: FinanceGraph): Map<string, FinanceItem> {
  return new Map(data.items.map((item) => [item.id, item]));
}

function resolveItemId(rawId: string): string {
  const trimmed = rawId.trim();
  for (const prefix of ["finance://", "opentax://"]) {
    if (trimmed.startsWith(prefix)) {
      return trimmed.slice(prefix.length);
    }
  }

  try {
    const url = new URL(trimmed);
    const hashId = decodeURIComponent(url.hash.replace(/^#/, ""));
    if (hashId) {
      return hashId;
    }
  } catch {
    // Not a URL; use the raw value as an ontology id.
  }

  return trimmed;
}

function itemAliases(item: FinanceItem): readonly string[] {
  return [...(item.legacy_ids ?? []), ...(item.search_aliases ?? []), ...(item.aliases ?? [])];
}

function resolveCanonicalItemId(rawId: string, searchIndex: SearchIndex): FinanceItem | undefined {
  const itemId = normalizeQuery(resolveItemId(rawId));
  return searchIndex.items.find(
    (item) => normalizeQuery(item.id) === itemId || itemAliases(item).some((alias) => normalizeQuery(alias) === itemId),
  );
}

function sourceItems(item: FinanceItem, itemsById: Map<string, FinanceItem>): FinanceItem[] {
  return (item.sources ?? [])
    .map((sourceId) => itemsById.get(sourceId))
    .filter((source): source is FinanceItem => Boolean(source));
}

function matchReasons(item: FinanceItem, query: string): string[] {
  const normalized = normalizeQuery(query);
  const reasons: string[] = [];
  if (normalizeQuery(item.id).includes(normalized)) {
    reasons.push("id");
  }
  if (normalizeQuery(item.title).includes(normalized)) {
    reasons.push("title");
  }
  if ((item.search_aliases ?? []).some((alias) => normalizeQuery(alias).includes(normalized))) {
    reasons.push("alias");
  }
  for (const token of queryTokens(query)) {
    if (itemSearchText(item).includes(token)) {
      reasons.push(`token:${token}`);
    }
  }
  return [...new Set(reasons)].slice(0, 10);
}

function domainMatches(item: FinanceItem, domain: string): boolean {
  const normalizedDomain = normalizeQuery(domain);
  if (normalizedDomain === "deposit") {
    return item.type === "bank-product" && item.search_type === "deposit";
  }
  if (normalizedDomain === "saving") {
    return item.type === "bank-product" && item.search_type === "saving";
  }
  if (normalizedDomain === "loan") {
    return item.type === "bank-product" && item.search_type === "loan";
  }
  if (normalizedDomain === "card") {
    return item.type === "card-product";
  }
  if (normalizedDomain === "insurance") {
    return item.type === "insurance-product";
  }
  if (normalizedDomain === "support") {
    return item.type === "support-program";
  }
  return false;
}

function recommendationBlocker(item: FinanceItem): string | undefined {
  if (item.recommendation_status !== "verified_recommendation_candidate") {
    return "not_verified_recommendation_candidate";
  }
  if (item.recommendation_scope !== "public_recommendation") {
    return "not_public_recommendation_scope";
  }
  if (item.verification_status !== "verified") return "verification_not_verified";
  if (!isRecord(item.verification_evidence)) {
    return "missing_verification_evidence";
  }
  const checksums = item.verification_evidence.source_checksums;
  if (!Array.isArray(checksums) || !checksums.includes(item.source_checksum)) return "source_checksum_mismatch";
  const expiresAt = item.verification_evidence.expires_at;
  if (!isFutureOrCurrentIsoDate(expiresAt)) return "verification_expired";
  if (item.freshness_status === "stale") {
    return "stale_source";
  }
  if (["closed", "ended", "unknown", "suspended"].includes(item.status ?? "")) {
    return `status_${item.status}`;
  }
  return undefined;
}

function recommendationScore(item: FinanceItem, profile: Record<string, unknown>): { score: number; components: Record<string, number> } {
  const components: Record<string, number> = { verification: 50 };
  if (typeof profile.provider === "string" && profile.provider === item.provider) {
    components.provider_match = 10;
  }
  if (item.freshness_status === "current") {
    components.freshness = 10;
  }
  return { score: Object.values(components).reduce((total, value) => total + value, 0), components };
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

function isFutureOrCurrentIsoDate(value: unknown): value is string {
  if (typeof value !== "string" || !/^\d{4}-\d{2}-\d{2}$/.test(value)) return false;
  const timestamp = Date.parse(`${value}T00:00:00Z`);
  return Number.isFinite(timestamp) && new Date(timestamp).toISOString().slice(0, 10) === value && value >= new Date().toISOString().slice(0, 10);
}

function comparisonBlocker(item: FinanceItem): string | undefined {
  if (item.recommendation_scope !== "comparison_only") return "not_comparison_scope";
  if (item.source_listing_status !== "listed") return "source_not_listed";
  if (item.sales_verification_status !== "verified_active") return "sales_not_verified";
  if (item.source_freshness_status !== "current") return "stale_source";
  const verifiedAt = Date.parse(`${item.sales_verified_at ?? ""}T00:00:00Z`);
  if (!Number.isFinite(verifiedAt) || verifiedAt > Date.now() || Date.now() - verifiedAt > 31 * 24 * 60 * 60 * 1000) return "stale_source";
  if (item.verification_status !== "verified") return "not_verified";
  const evidenceBlocker = recommendationBlocker({ ...item, recommendation_status: "verified_recommendation_candidate", recommendation_scope: "public_recommendation" });
  if (evidenceBlocker) return evidenceBlocker;
  if (item.domain_gate_passed !== true) return "domain_gate_not_passed";
  if (["closed", "ended", "unknown", "suspended"].includes(item.status ?? "")) return `status_${item.status}`;
  return undefined;
}

function comparisonOptionCandidates(item: FinanceItem, termMonths: number): readonly Record<string, unknown>[] {
  return (item.comparison_options ?? []).filter(
    (value): value is Record<string, unknown> => isRecord(value) && value.term_months === termMonths && typeof value.base_rate_percent === "number",
  );
}

function comparisonOptionBlocker(option: Record<string, unknown>, domain: string, depositAmount: number | undefined, monthlyPayment: number | undefined, joinChannels: readonly string[], savingMethod: string | undefined): string | undefined {
  const optionChannels = Array.isArray(option.join_channels) ? option.join_channels.filter((value): value is string => typeof value === "string").map((value) => normalizeQuery(value)) : [];
  if (joinChannels.length && optionChannels.length && !joinChannels.some((channel) => optionChannels.includes(normalizeQuery(channel)))) return "join_channel_mismatch";
  if (depositAmount !== undefined && typeof option.maximum_deposit_krw === "number" && depositAmount > option.maximum_deposit_krw) return "amount_exceeds_limit";
  if (monthlyPayment !== undefined && typeof option.monthly_payment_max_krw === "number" && monthlyPayment > option.monthly_payment_max_krw) return "monthly_payment_exceeds_limit";
  if (domain === "saving" && savingMethod && typeof option.saving_method === "string" && option.saving_method !== savingMethod) return "saving_method_mismatch";
  if (!Array.isArray(option.source_urls) || !option.source_urls.length) return "missing_source_url";
  return undefined;
}

function comparisonCandidate(item: FinanceItem, option: Record<string, unknown>, eligibleConditions: ReadonlySet<string>): Record<string, unknown> {
  const baseRate = option.base_rate_percent;
  const maximumRate = typeof option.maximum_rate_percent === "number" ? option.maximum_rate_percent : baseRate;
  if (typeof baseRate !== "number" || typeof maximumRate !== "number") throw new Error("Comparison option has invalid rate fields");
  const conditions = Array.isArray(option.preferential_rate_conditions) ? option.preferential_rate_conditions.filter(isRecord) : [];
  const matched = conditions.filter((condition) => typeof condition.condition_id === "string" && eligibleConditions.has(condition.condition_id));
  const unmatched = conditions.filter((condition) => typeof condition.condition_id === "string" && !eligibleConditions.has(condition.condition_id));
  const additionalRate = matched.reduce((total, condition) => total + (typeof condition.additional_rate_percent === "number" ? condition.additional_rate_percent : 0), 0);
  return {
    item_id: item.id,
    title: item.title,
    provider: item.provider,
    base_rate_percent: baseRate,
    maximum_rate_percent: maximumRate,
    achievable_rate_percent: Math.min(baseRate + additionalRate, maximumRate),
    matched_preferential_conditions: matched.map((condition) => condition.condition_id),
    unmatched_preferential_conditions: unmatched.map((condition) => condition.condition_id),
    unknown_preferential_conditions: conditions.filter((condition) => typeof condition.condition_id !== "string").map((condition) => condition.description ?? "unidentified_preferential_condition"),
    deposit_limit: option.maximum_deposit_krw,
    monthly_payment_limit: option.monthly_payment_max_krw,
    term_months: option.term_months,
    saving_method: option.saving_method,
    join_channel: option.join_channels ?? [],
    sales_verified_at: item.sales_verified_at,
    score_components: { achievable_rate_percent: Math.min(baseRate + additionalRate, maximumRate), source_verified: 1 },
    source_urls: option.source_urls,
    source_basis_dates: item.source_basis_dates ?? [],
    comparison_basis_fields: item.comparison_basis_fields ?? [],
    missing_required_fields: item.missing_required_fields ?? [],
  };
}

async function fetchItemGraph(env: Env, rawId: string): Promise<{ item: FinanceItem; itemsById: Map<string, FinanceItem> }> {
  const manifestUrl = financeManifestUrl(env);
  const manifest = await loadFinanceManifest(env);
  const searchIndex = await loadSearchIndex(env);
  const indexedItem = resolveCanonicalItemId(rawId, searchIndex);
  const itemId = indexedItem?.id ?? resolveItemId(rawId);
  const candidateExports = indexedItem?.export_id
    ? manifest.exports.filter((entry) => entry.id === indexedItem.export_id)
    : manifest.exports;

  for (const entry of candidateExports) {
    const payload = await fetchJson<OntologyExport>(resolveExportUrl(entry, manifestUrl));
    const items = [...(payload.reference_items ?? []), ...(payload.items ?? [])];
    const itemsById = new Map(items.map((item) => [item.id, item]));
    const item = itemsById.get(itemId);
    if (item) {
      return { item, itemsById };
    }
  }

  throw new Error(`Finance ontology item not found: ${rawId}`);
}

function createServer(env: Env): McpServer {
  const server = new McpServer({
    name: "finance",
    version: "0.2.0",
  });

  server.registerTool(
    "search",
    {
      title: "Search Finance Ontology",
      description:
        "Use this when the user needs to find Korean tax, deduction, policy support, local-government support, card, bank, insurance, filing deadline, term, or official-source nodes. Recommendation wording routes to source-backed discovery candidates; verified public recommendations remain a separate tool. Do not use for personalized tax, legal, accounting, or financial advice.",
      inputSchema: {
        query: z.string().min(1).describe("Search query, for example '보험료 공제 한도', '청년 월세', '체크카드 전월실적', or 'bank-products'."),
        type: z
          .string()
          .optional()
          .describe("Optional ontology item type filter, for example 'tax', 'support-program', 'card-product', 'bank-product', or 'insurance-product'. 'tax' also matches tax-credit, deduction, and other tax decision types."),
        search_type: z.string().optional().describe("Optional product search-type filter, for example 'loan', 'deposit', or 'saving'."),
        product_kind: z.string().optional().describe("Optional product-kind filter, for example 'policy-loan'."),
        recommendation_status: z.string().optional().describe("Optional recommendation-state filter. manual_review_candidate records are internal-only and recommendation wording returns only verified_recommendation_candidate records."),
        recommendation_scope: z.string().optional().describe("Optional recommendation-scope filter, for example 'listing_only' or 'internal_verification_candidate'."),
        sales_status: z.string().optional().describe("Optional sales-state filter, for example 'active'."),
        application_status: z.string().optional().describe("Optional support application-state filter, for example 'open'."),
        provider: z.string().optional().describe("Optional exact provider filter."),
        region: z.string().optional().describe("Optional local-support jurisdiction filter, for example '서울' or '전라남도'."),
        freshness_status: z.string().optional().describe("Optional source-freshness filter, for example 'current' or 'stale'."),
        limit: z.number().int().min(1).max(50).optional().describe("Maximum number of results. Defaults to 10."),
      },
      annotations: {
        title: "Search Finance Ontology",
        ...READ_ONLY_TOOL_ANNOTATIONS,
      },
    },
    async ({ query, type, search_type, product_kind, recommendation_status, recommendation_scope, sales_status, application_status, provider, region, freshness_status, limit }) => {
      const data = await loadSearchIndex(env);
      const normalizedQuery = normalizeQuery(query);
      const maxResults = limit ?? 10;
      if (DISCOVERY_ACTION_RE.test(query)) {
        const payload = discoveryPayload(query, data.items, maxResults);
        return { structuredContent: payload, content: [{ type: "text", text: jsonText(payload) }] };
      }

      const allowedTypes = type ? SEARCH_TYPE_GROUPS[type] ?? new Set([type]) : inferredTypesForQuery(normalizedQuery);
      const filters: SearchFilters = {
        searchType: search_type ?? inferredSearchTypeForQuery(normalizedQuery),
        productKind: product_kind,
        recommendationStatus: recommendation_status,
        recommendationScope: recommendation_scope,
        salesStatus: sales_status,
        applicationStatus: application_status,
        provider,
        region,
        freshnessStatus: freshness_status,
      };
      const results = data.items
        .filter((item) => isPubliclySearchable(item) && (!allowedTypes || allowedTypes.has(item.type)) && matchesSearchFilters(item, filters))
        .map((item) => ({ item, score: scoreItem(item, normalizedQuery) }))
        .filter((result) => result.score > 0)
        .sort((a, b) => b.score - a.score || a.item.title.localeCompare(b.item.title, "ko-KR"))
        .slice(0, maxResults)
        .map(({ item, score }) => ({
          id: item.id,
          title: item.title,
          type: item.type,
          provider: item.provider,
          product_kind: item.product_kind,
          search_type: item.search_type,
          product_status: item.product_status,
          sales_status: item.sales_status,
          source_listing_status: item.source_listing_status,
          sales_verification_status: item.sales_verification_status,
          source_freshness_status: item.source_freshness_status,
          status: item.status,
          recommendation_status: item.recommendation_status,
          recommendation_scope: item.recommendation_scope,
          application_status: item.application_status,
          is_currently_applicable: item.is_currently_applicable,
          application_open_to: item.application_open_to,
          jurisdiction: item.jurisdiction,
          freshness_status: item.freshness_status,
          recommendation_model_version: item.recommendation_model_version,
          recommendation_exclusion_reasons: item.recommendation_exclusion_reasons ?? [],
          recommendation_basis_fields: item.recommendation_basis_fields ?? [],
          comparison_basis_fields: item.comparison_basis_fields ?? [],
          verification_status: item.verification_status,
          completeness_ratio: item.completeness_ratio,
          missing_required_fields: item.missing_required_fields ?? [],
          structured_summary: item.structured_summary ?? {},
          search_facets: item.search_facets ?? {},
          match_reasons: matchReasons(item, normalizedQuery),
          url: itemUrl(env, item.id),
          score,
          text: item.description ?? "",
        }));

      const payload = {
        query,
        filters,
        result_count: results.length,
        results,
      };

      return {
        structuredContent: payload,
        content: [
          {
            type: "text",
            text: jsonText(payload),
          },
        ],
      };
    },
  );

  server.registerTool(
    "discover",
    {
      title: "Discover Finance Products",
      description: "Return source-backed exploration candidates. It does not claim a best product, approval, premium, coverage fit, or personalized recommendation.",
      inputSchema: {
        query: z.string().min(1).describe("A finance-product need, for example '실손보험 추천' or '마일리지 카드 추천'."),
        limit: z.number().int().min(1).max(50).optional().describe("Maximum number of discovery candidates. Defaults to 10."),
      },
      annotations: { title: "Discover Finance Products", ...READ_ONLY_TOOL_ANNOTATIONS },
    },
    async ({ query, limit }) => {
      const data = await loadSearchIndex(env);
      const payload = discoveryPayload(query, data.items, limit ?? 10);
      return { structuredContent: payload, content: [{ type: "text", text: jsonText(payload) }] };
    },
  );

  server.registerTool(
    "recommend",
    {
      title: "Recommend Finance Products",
      description:
        "Use this only when the user asks which finance product fits their current needs. It returns deterministic recommendations only from verified public recommendation candidates with source evidence; otherwise it returns an empty result with structured blockers.",
      inputSchema: {
        domain: z.enum(["deposit", "saving", "card", "loan", "insurance", "support"]).describe("Recommendation domain."),
        profile: z.record(z.string(), z.unknown()).optional().describe("User profile facts already supplied by the user."),
        constraints: z.record(z.string(), z.unknown()).optional().describe("Hard constraints already supplied by the user."),
        preferences: z.record(z.string(), z.unknown()).optional().describe("Soft preferences already supplied by the user."),
        limit: z.number().int().min(1).max(20).optional().describe("Maximum number of recommendations. Defaults to 5."),
      },
      annotations: {
        title: "Recommend Finance Products",
        ...READ_ONLY_TOOL_ANNOTATIONS,
      },
    },
    async ({ domain, profile, constraints, preferences, limit }) => {
      const data = await loadSearchIndex(env);
      const maxResults = limit ?? 5;
      const domainItems = data.items.filter((item) => domainMatches(item, domain));
      if (["card", "loan", "insurance"].includes(domain)) {
        const payload = {
          domain,
          profile: profile ?? {},
          constraints: constraints ?? {},
          preferences: preferences ?? {},
          recommendation_model_version: "openfin-recommendation-v0.1.0",
          result_count: 0,
          candidates: [],
          excluded_count: domainItems.length,
          excluded_sample: domainItems.slice(0, 20).map((item) => ({ item_id: item.id, reason: "domain_recommendation_not_enabled" })),
          warnings: ["No verified public recommendation candidates are available for this domain."],
        };
        return { structuredContent: payload, content: [{ type: "text", text: jsonText(payload) }] };
      }
      const excluded = [];
      const candidates = [];
      for (const item of domainItems) {
        const blocker = recommendationBlocker(item);
        if (blocker) {
          excluded.push({ item_id: item.id, reason: blocker });
          continue;
        }
        const score = recommendationScore(item, profile ?? {});
        candidates.push({
          item_id: item.id,
          title: item.title,
          provider: item.provider,
          eligible: true,
          score: score.score,
          score_components: score.components,
          matched_conditions: [],
          failed_conditions: [],
          unknown_conditions: [],
          warnings: [],
          source_basis_dates: item.source_basis_dates ?? [],
          last_verified_at: item.last_verified_at,
          recommendation_status: item.recommendation_status,
          recommendation_scope: item.recommendation_scope,
          recommendation_model_version: item.recommendation_model_version,
          sources: item.source_urls ?? [],
          structured_summary: item.structured_summary ?? {},
          url: itemUrl(env, item.id),
        });
      }
      candidates.sort((a, b) => b.score - a.score || a.item_id.localeCompare(b.item_id, "ko-KR"));
      const results = candidates.slice(0, maxResults);
      const payload = {
        domain,
        profile: profile ?? {},
        constraints: constraints ?? {},
        preferences: preferences ?? {},
        recommendation_model_version: "openfin-recommendation-v0.1.0",
        result_count: results.length,
        candidates: results,
        excluded_count: excluded.length,
        excluded_sample: excluded.slice(0, 20),
        warnings: results.length ? [] : ["No verified public recommendation candidates are available for this domain."],
      };
      return {
        structuredContent: payload,
        content: [
          {
            type: "text",
            text: jsonText(payload),
          },
        ],
      };
    },
  );

  server.registerTool(
    "compare",
    {
      title: "Compare Deposit and Saving Products",
      description:
        "Use this for deterministic deposit or saving comparison. It includes only official current listings with verified active sales status and never assumes unmet preferential conditions.",
      inputSchema: {
        domain: z.enum(["deposit", "saving"]),
        deposit_amount_krw: z.number().int().positive().optional(),
        monthly_payment_krw: z.number().int().positive().optional(),
        term_months: z.number().int().positive(),
        join_channels: z.array(z.string()).optional(),
        eligible_conditions: z.array(z.string()).optional(),
        saving_method: z.enum(["free", "fixed"]).optional(),
        limit: z.number().int().min(1).max(20).optional(),
      },
      annotations: {
        title: "Compare Deposit and Saving Products",
        ...READ_ONLY_TOOL_ANNOTATIONS,
      },
    },
    async ({ domain, deposit_amount_krw, monthly_payment_krw, term_months, join_channels, eligible_conditions, saving_method, limit }) => {
      const data = await loadSearchIndex(env);
      const channels = (join_channels ?? []).map((channel) => normalizeQuery(channel));
      const conditions = new Set(eligible_conditions ?? []);
      const excluded: Array<{ item_id: string; reason: string }> = [];
      const candidates: Record<string, unknown>[] = [];
      for (const item of data.items.filter((candidate) => domainMatches(candidate, domain))) {
        const blocker = comparisonBlocker(item);
        if (blocker) {
          excluded.push({ item_id: item.id, reason: blocker });
          continue;
        }
        const options = comparisonOptionCandidates(item, term_months);
        if (!options.length) {
          excluded.push({ item_id: item.id, reason: "term_mismatch" });
          continue;
        }
        const usableOptions = options.filter((option) => !comparisonOptionBlocker(option, domain, deposit_amount_krw, monthly_payment_krw, channels, saving_method));
        if (!usableOptions.length) {
          const reason = comparisonOptionBlocker(options[0], domain, deposit_amount_krw, monthly_payment_krw, channels, saving_method) ?? "missing_comparison_option";
          excluded.push({ item_id: item.id, reason });
          continue;
        }
        candidates.push(...usableOptions.map((option) => comparisonCandidate(item, option, conditions)));
      }
      candidates.sort((left, right) => {
        const leftRate = typeof left.achievable_rate_percent === "number" ? left.achievable_rate_percent : 0;
        const rightRate = typeof right.achievable_rate_percent === "number" ? right.achievable_rate_percent : 0;
        return rightRate - leftRate || String(left.item_id).localeCompare(String(right.item_id));
      });
      const payload = {
        domain,
        candidates: candidates.slice(0, limit ?? 10),
        excluded: excluded.sort((left, right) => left.item_id.localeCompare(right.item_id) || left.reason.localeCompare(right.reason)),
        assumptions: [
          "Achievable rate includes only user-declared preferential conditions.",
          "Missing preferential conditions are not assumed to be satisfied.",
        ],
        comparison_model_version: "openfin-comparison-v0.1.0",
        basis_date: data.basis_date,
      };
      return { structuredContent: payload, content: [{ type: "text", text: jsonText(payload) }] };
    },
  );

  server.registerTool(
    "fetch",
    {
      title: "Fetch Finance Ontology Item",
      description:
        "Use this when the user needs one exact finance ontology node with criteria, product metadata, official sources, and graph neighbors after an id or URL is known. Do not use for personalized tax, legal, accounting, or financial advice.",
      inputSchema: {
        id: z.string().min(1).describe("Ontology item id, finance:// id, opentax:// id, or web URL with hash id."),
      },
      annotations: {
        title: "Fetch Finance Ontology Item",
        ...READ_ONLY_TOOL_ANNOTATIONS,
      },
    },
    async ({ id }) => {
      const { item, itemsById } = await fetchItemGraph(env, id);
      const sources = sourceItems(item, itemsById).map((source) => ({
        id: source.id,
        title: source.title,
        publisher: source.publisher,
        basis_date: source.basis_date,
        url: source.url,
        description: source.description,
      }));

      const payload = {
        id: item.id,
        title: item.title,
        type: item.type,
        url: itemUrl(env, item.id),
        description: item.description,
        basis_year: item.basis_year,
        law_reference: item.law_reference,
        provider: item.provider,
        provider_code: item.provider_code,
        financial_sector: item.financial_sector,
        product_code: item.product_code,
        product_kind: item.product_kind,
        search_type: item.search_type,
        product_status: item.product_status,
        sales_status: item.sales_status,
        source_listing_status: item.source_listing_status,
        sales_verification_status: item.sales_verification_status,
        sales_verified_at: item.sales_verified_at,
        condition_verification_status: item.condition_verification_status,
        source_freshness_status: item.source_freshness_status,
        status: item.status,
        status_reason: item.status_reason,
        recommendation_status: item.recommendation_status,
        recommendation_scope: item.recommendation_scope,
        recommendation_model_version: item.recommendation_model_version,
        recommendation_exclusion_reasons: item.recommendation_exclusion_reasons ?? [],
        recommendation_basis_fields: item.recommendation_basis_fields ?? [],
        comparison_basis_fields: item.comparison_basis_fields ?? [],
        verification_status: item.verification_status,
        quality_flags: item.quality_flags ?? [],
        freshness_status: item.freshness_status,
        last_verified_at: item.last_verified_at,
        verification_evidence: item.verification_evidence,
        missing_required_fields: item.missing_required_fields ?? [],
        missing_in_source_fields: item.missing_in_source_fields ?? [],
        unmapped_existing_fields: item.unmapped_existing_fields ?? [],
        unverified_fields: item.unverified_fields ?? [],
        discovery_evidence_fields: item.discovery_evidence_fields ?? [],
        completeness_ratio: item.completeness_ratio,
        source_completeness_ratio: item.source_completeness_ratio,
        normalized_completeness_ratio: item.normalized_completeness_ratio,
        verified_completeness_ratio: item.verified_completeness_ratio,
        required_field_count: item.required_field_count,
        completed_field_count: item.completed_field_count,
        domain_gate_passed: item.domain_gate_passed,
        comparison_options: item.comparison_options ?? [],
        application_status: item.application_status,
        is_currently_applicable: item.is_currently_applicable,
        application_open_from: item.application_open_from,
        application_open_to: item.application_open_to,
        criteria: item.criteria ?? [],
        structured_summary: item.structured_summary ?? {},
        search_facets: item.search_facets ?? {},
        neighbors: {
          parents: item.parents ?? [],
          children: item.children ?? [],
          related: item.related ?? [],
          terms: item.terms ?? [],
          deadlines: item.deadlines ?? [],
          sources: item.sources ?? [],
        },
        source_urls: item.source_urls ?? [],
        source_basis_dates: item.source_basis_dates ?? [],
        sources,
      };

      return {
        structuredContent: payload,
        content: [
          {
            type: "text",
            text: jsonText(payload),
          },
        ],
      };
    },
  );

  server.registerTool(
    "exports",
    {
      title: "List Finance Ontology Exports",
      description:
        "Use this to see which ontology exports the finance MCP loads, including tax, local-government support, card, bank, and insurance product ontologies.",
      inputSchema: {},
      annotations: {
        title: "List Finance Ontology Exports",
        ...READ_ONLY_TOOL_ANNOTATIONS,
      },
    },
    async () => {
      const manifest = await loadFinanceManifest(env);
      const payload = {
        version: manifest.version,
        basis_date: manifest.basis_date,
        item_count: manifest.search_index?.item_count ?? manifest.exports.reduce((total, entry) => total + (entry.item_count ?? 0), 0),
        search_index: manifest.search_index,
        quality_exports: manifest.quality_exports ?? [],
        exports: manifest.exports,
      };
      return {
        structuredContent: payload,
        content: [
          {
            type: "text",
            text: jsonText(payload),
          },
        ],
      };
    },
  );

  return server;
}

function healthResponse(env: Env): Response {
  return Response.json({
    name: "finance",
    status: "ok",
    mcp_endpoint: "/mcp",
    finance_manifest_url: financeManifestUrl(env),
  });
}

function openAiAppsChallengeResponse(env: Env): Response {
  const token = env.OPENAI_APPS_CHALLENGE_TOKEN?.trim();
  if (!token) {
    return new Response("OpenAI Apps challenge token is not configured.", {
      status: 404,
      headers: {
        "content-type": "text/plain; charset=utf-8",
        "cache-control": "no-store",
      },
    });
  }

  return new Response(token, {
    headers: {
      "content-type": "text/plain; charset=utf-8",
      "cache-control": "no-store",
    },
  });
}

export default {
  async fetch(request: Request, env: Env, ctx: ExecutionContext): Promise<Response> {
    const url = new URL(request.url);
    if (url.pathname === "/" || url.pathname === "/health") {
      return healthResponse(env);
    }
    if (url.pathname === OPENAI_APPS_CHALLENGE_PATH) {
      return openAiAppsChallengeResponse(env);
    }

    const server = createServer(env);
    return createMcpHandler(server, { route: "/mcp" })(request, env, ctx);
  },
} satisfies ExportedHandler<Env>;
