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
  catalog_recommendation_status?: string;
  catalog_recommendation_scope?: string;
  canonical_product_id?: string;
  source_records?: Record<string, unknown>[];
  preferred_source?: string;
  merged_fields?: Record<string, unknown>;
  field_provenance?: Record<string, string[]>;
  field_conflicts?: Record<string, unknown>;
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
  parent_jurisdiction_code?: string;
  administrative_history?: unknown[];
  target_group?: string[];
  support_category?: string[];
  last_status_checked_at?: string;
  freshness_status?: string;
  collection_status?: string;
  last_verified_at?: string;
  last_source_checked_at?: string;
  last_reviewed_at?: string;
  public_recommendation_exclusion_reasons?: string[];
  comparison_exclusion_reasons?: string[];
  discovery_limitations?: string[];
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
const DISCOVERY_QUERY_RE = /(추천|알려줘|골라줘|찾아줘|괜찮은|좋은|후보|순위|해줘|해주세요)/i;
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
const ENABLE_CARD_DISCOVERY = true;
const ENABLE_LOAN_DISCOVERY = true;
const ENABLE_INSURANCE_DISCOVERY = true;
const ENABLE_DEPOSIT_COMPARISON = true;
const ENABLE_SAVING_COMPARISON = true;
const ENABLE_PUBLIC_RECOMMENDATION = false;
const QUERY_PARSER_VERSION = "openfin-query-parser-v1.1.0";
const FIELD_EXTRACTOR_VERSION = "openfin-field-extractor-v1.1.0";
const DISCOVERY_ENGINE_VERSION = "openfin-discovery-v1.1.0";
const COMPARISON_ENGINE_VERSION = "openfin-comparison-v1.0.0";

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
const SUPPORT_INTENT_RE = /(지원|보조금|신청|청년.*월세|월세.*청년)/;
const SUPPORT_REGION_TOKENS = ["전남광주통합특별시", "충청북도", "충청남도", "전라북도", "전라남도", "경상북도", "경상남도", "서울", "부산", "대구", "인천", "광주", "대전", "울산", "세종", "경기", "강원", "충북", "충남", "전북", "전남", "경북", "경남", "제주"] as const;

function inferredTypesForQuery(query: string): Set<string> | null {
  if (SUPPORT_INTENT_RE.test(query)) {
    return new Set(["support-program"]);
  }
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

function supportRegionForQuery(query: string): string | undefined {
  return SUPPORT_REGION_TOKENS.find((region) => query.includes(normalizeQuery(region)));
}

function matchesSupportRegion(item: FinanceItem, region: string | undefined): boolean {
  if (item.type !== "support-program" || !region) return true;
  return [item.jurisdiction, item.jurisdiction_code, item.parent_jurisdiction_code, ...(item.jurisdiction_aliases ?? [])]
    .some((value) => normalizeQuery(value ?? "").includes(region));
}

function matchesSupportIntent(item: FinanceItem, query: string): boolean {
  if (item.type !== "support-program" || !SUPPORT_INTENT_RE.test(query)) return true;
  const targetGroups = new Set((item.target_group ?? []).map(normalizeQuery));
  const categories = new Set((item.support_category ?? []).map(normalizeQuery));
  const requiresYouth = query.includes("청년");
  const requiresHousing = /(월세|주거|전세)/.test(query);
  const requiresCurrentAvailability = /(지원|보조금|신청|월세|주거)/.test(query);
  const currentlyAvailable = item.is_currently_applicable === true || ["open", "always_open"].includes(item.application_status ?? "");
  return (!requiresYouth || targetGroups.has("youth"))
    && (!requiresHousing || categories.has("housing") || categories.has("rent"))
    && (!requiresCurrentAvailability || currentlyAvailable);
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

function isDiscoveryQuery(query: string): boolean {
  return DISCOVERY_QUERY_RE.test(query);
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
  if (!item.source_urls?.length || item.source_listing_status !== "listed") return false;
  const evidence = new Set(item.discovery_evidence_fields ?? []);
  if (domain === "card") return Boolean(item.title && item.provider && item.product_kind && (["benefit_type", "benefit_rate_or_amount", "benefit_categories"].some((field) => evidence.has(field))));
  if (domain === "loan") return Boolean(item.provider && item.product_kind && ["loan_rate_min_percent", "loan_rate_max_percent", "loan_limit_krw"].some((field) => evidence.has(field)));
  if (domain === "insurance") return Boolean(item.product_kind && ["coverage_amount_krw", "premium_basis", "renewal_type"].some((field) => evidence.has(field)));
  return Boolean(item.comparison_options?.length || evidence.size);
}

function discoveryConfidence(item: FinanceItem): "A" | "B" | "C" | "D" {
  const ratio = item.normalized_completeness_ratio ?? item.completeness_ratio ?? 0;
  if (ratio >= 0.9) return "A";
  if (ratio >= 0.7) return "B";
  if (ratio >= 0.4) return "C";
  return "D";
}

function requestedProductKind(query: string): string | undefined {
  if (query.includes("체크카드")) return "check-card";
  if (query.includes("신용카드")) return "credit-card";
  if (query.includes("신용대출")) return "credit-loan";
  if (query.includes("전세대출") || query.includes("월세대출")) return "rent-loan";
  if (query.includes("주택담보대출")) return "mortgage-loan";
  if (query.includes("정책대출")) return "policy-loan";
  if (query.includes("실손") || query.includes("실비")) return "indemnity-health";
  if (query.includes("암보험")) return "cancer";
  if (query.includes("상해보험")) return "accident";
  if (query.includes("질병보험")) return "disease";
  if (query.includes("정기보험")) return "term-life";
  if (query.includes("종신보험")) return "whole-life";
  if (query.includes("정기예금") || query.includes("예금")) return "deposit";
  if (query.includes("자유적금") || query.includes("적금")) return "saving";
  return undefined;
}

type DiscoveryConstraint = { readonly field: string; readonly operator: "equals" | "lte" | "contains"; readonly value: string | number };
type ParsedDiscoveryQuery = {
  readonly original_query: string;
  readonly parser_version: string;
  readonly intent: "discovery";
  readonly domain: DiscoveryDomain;
  readonly product_kind?: string;
  readonly hard_constraints: readonly DiscoveryConstraint[];
  readonly soft_preferences: readonly string[];
  readonly negative_constraints: readonly string[];
  readonly numeric_constraints: readonly DiscoveryConstraint[];
  readonly unparsed_tokens: readonly string[];
};

function parseAmountKrw(query: string): number | undefined {
  const match = query.replace(/,/g, "").match(/(\d+(?:\.\d+)?)\s*(천만원|억원|만원|천원|원)/);
  if (!match) return undefined;
  const multiplier = { "억원": 100_000_000, "천만원": 10_000_000, "만원": 10_000, "천원": 1_000, "원": 1 }[match[2]];
  if (multiplier === undefined) return undefined;
  return Math.trunc(Number(match[1]) * multiplier);
}

function parseDiscoveryQuery(query: string, domain: DiscoveryDomain): ParsedDiscoveryQuery {
  const productKind = requestedProductKind(query);
  const hardConstraints: DiscoveryConstraint[] = productKind ? [{ field: "product_kind", operator: "equals", value: productKind }] : [];
  if (query.includes("전월실적 없는")) hardConstraints.push({ field: "previous_month_spend_min_krw", operator: "equals", value: 0 });
  if (query.includes("연회비 없는")) hardConstraints.push({ field: "annual_fee_krw", operator: "equals", value: 0 });
  if (query.includes("비갱신") || query.includes("갱신 안 되는")) hardConstraints.push({ field: "renewal_type", operator: "equals", value: "non_renewable" });
  else if (query.includes("갱신형")) hardConstraints.push({ field: "renewal_type", operator: "equals", value: "renewable" });
  if (query.includes("직장인")) hardConstraints.push({ field: "employment_type", operator: "equals", value: "employee" });
  if (query.includes("중도상환수수료 없는")) hardConstraints.push({ field: "early_repayment_fee", operator: "equals", value: 0 });
  if (query.includes("구독")) hardConstraints.push({ field: "benefit_category", operator: "contains", value: "subscription" });
  if (query.includes("자유적립") || query.includes("자유적금")) hardConstraints.push({ field: "saving_method", operator: "equals", value: "free" });
  const term = query.match(/(\d+)\s*개월/);
  if (term) hardConstraints.push({ field: "term_months", operator: "equals", value: Number(term[1]) });
  const amount = parseAmountKrw(query);
  if (amount !== undefined) hardConstraints.push({ field: domain === "deposit" ? "deposit_amount_krw" : "monthly_payment_krw", operator: "lte", value: amount });
  const softPreferences = ["마일리지", "교통", "쇼핑", "온라인", "우대금리", "낮은 금리", "높은 한도", "대한항공", "SKYPASS", "청년"]
    .filter((token) => normalizeQuery(query).includes(normalizeQuery(token)));
  return { original_query: query, parser_version: QUERY_PARSER_VERSION, intent: "discovery", domain, product_kind: productKind, hard_constraints: hardConstraints, soft_preferences: softPreferences, negative_constraints: [], numeric_constraints: hardConstraints.filter((constraint) => typeof constraint.value === "number"), unparsed_tokens: [] };
}

function discoveryValues(item: FinanceItem, field: string): unknown[] {
  const direct = item[field as keyof FinanceItem];
  if (direct !== undefined && direct !== null && direct !== "" && (!Array.isArray(direct) || direct.length)) return Array.isArray(direct) ? direct : [direct];
  const values: unknown[] = [];
  for (const section of Object.values(item.structured_summary ?? {})) {
    if (isRecord(section) && section[field] !== undefined && section[field] !== null && section[field] !== "") {
      const value = section[field];
      values.push(...(Array.isArray(value) ? value : [value]));
    }
  }
  for (const option of item.comparison_options ?? []) {
    if (isRecord(option) && option[field] !== undefined && option[field] !== null && option[field] !== "") {
      const value = option[field];
      values.push(...(Array.isArray(value) ? value : [value]));
    }
  }
  return values;
}

function flattenDiscoveryValues(values: readonly unknown[]): unknown[] {
  return values.flatMap((value) => Array.isArray(value) ? flattenDiscoveryValues(value) : [value]);
}

function discoveryItemText(item: FinanceItem): string {
  return normalizeQuery([item.title, item.description, item.product_kind, item.search_text, ...(item.search_aliases ?? [])].filter(Boolean).join(" "));
}

function discoveryConstraintState(item: FinanceItem, constraint: DiscoveryConstraint): "matched" | "failed" | "unknown" {
  const { field, value: expected } = constraint;
  const candidateText = discoveryItemText(item);
  if (field === "product_kind") return item.product_kind === expected || (expected === "rent-loan" && item.product_kind === "policy-loan" && candidateText.includes("전세")) ? "matched" : "failed";
  if (field === "employment_type") return ["직장인", "재직자", "근로소득자"].some((token) => candidateText.includes(token)) ? "matched" : "unknown";
  if (field === "term_months") {
    const termMonths = discoveryValues(item, "term_months");
    const terms = termMonths.length ? termMonths : discoveryValues(item, "terms");
    return terms.some((term) => String(term) === String(expected)) ? "matched" : "unknown";
  }
  if (field === "deposit_amount_krw" || field === "monthly_payment_krw") {
    const limits = discoveryValues(item, field === "deposit_amount_krw" ? "maximum_deposit_krw" : "monthly_payment_max_krw");
    return limits.length ? (limits.some((limit) => typeof limit === "number" && limit >= Number(expected)) ? "matched" : "failed") : "unknown";
  }
  const candidates = discoveryValues(item, field === "benefit_category" ? "benefit_categories" : field);
  if (!candidates.length) return "unknown";
  if (field === "renewal_type") return candidates.some((candidate) => String(candidate).replace("nonrenewable", "non_renewable") === expected) ? "matched" : "failed";
  if (field === "benefit_category") return flattenDiscoveryValues(candidates).some((candidate) => ["구독", "subscription"].includes(normalizeQuery(String(candidate)))) ? "matched" : "failed";
  if (expected === 0) return candidates.some((candidate) => candidate === 0) ? "matched" : "failed";
  return candidates.some((candidate) => candidate === expected) ? "matched" : "failed";
}

function discoveryPreferenceState(item: FinanceItem, preference: string): "matched" | "unknown" {
  const tokens: Record<string, readonly string[]> = { "마일리지": ["마일", "mileage"], "구독": ["구독", "subscription"], "교통": ["교통"], "쇼핑": ["쇼핑"], "온라인": ["온라인"], "대한항공": ["대한항공"], "SKYPASS": ["skypass"], "청년": ["청년", "youth"], "자유": ["자유", "free"] };
  return (tokens[preference] ?? [preference]).some((token) => discoveryItemText(item).includes(normalizeQuery(token))) ? "matched" : "unknown";
}

function discoveryPayload(query: string, items: readonly FinanceItem[], limit: number): Record<string, unknown> {
  const domain = discoveryDomainForQuery(query);
  const enabled = domain === "card" ? ENABLE_CARD_DISCOVERY : domain === "loan" ? ENABLE_LOAN_DISCOVERY : domain === "insurance" ? ENABLE_INSURANCE_DISCOVERY : true;
  if (!domain || !enabled) return { requested_intent: "discovery", executed_mode: "discovery", parsed_query: { original_query: query, parser_version: QUERY_PARSER_VERSION, domain: domain ?? null }, exact_candidates: [], partial_candidates: [], related_candidates: [], excluded_summary: {}, warnings: [domain ? "이 도메인의 탐색은 현재 비활성화되어 있습니다." : "상품 유형을 특정할 수 없어 탐색 후보를 만들지 않았습니다."], engine_version: DISCOVERY_ENGINE_VERSION, field_extractor_version: FIELD_EXTRACTOR_VERSION };
  const parsed = parseDiscoveryQuery(query, domain);
  const groups = { exact_candidates: [] as Record<string, unknown>[], partial_candidates: [] as Record<string, unknown>[], related_candidates: [] as Record<string, unknown>[] };
  const excludedSummary: Record<string, number> = {};
  const seen = new Set<string>();
  for (const item of items) {
    if (discoveryDomainForItem(item) !== domain) {
      excludedSummary.domain_mismatch = (excludedSummary.domain_mismatch ?? 0) + 1;
      continue;
    }
    if (!isDiscoveryCandidate(item, domain)) {
      excludedSummary.inactive_or_unlisted = (excludedSummary.inactive_or_unlisted ?? 0) + 1;
      continue;
    }
    const text = discoveryItemText(item);
    const matched = parsed.soft_preferences.filter((preference) => discoveryPreferenceState(item, preference) === "matched");
    const ratio = item.normalized_completeness_ratio ?? item.completeness_ratio ?? 0;
    const score = 35 + Math.min(20, matched.length * 10) + Math.round(ratio * 10) + (item.source_freshness_status === "current" ? 5 : 0);
    const canonicalId = item.canonical_product_id ?? item.id;
    const states = new Map(parsed.hard_constraints.map((constraint) => [constraint.field, discoveryConstraintState(item, constraint)]));
    const preferenceStates = new Map(parsed.soft_preferences.map((preference) => [preference, discoveryPreferenceState(item, preference)]));
    const failed = [...states.entries()].filter(([, state]) => state === "failed").map(([field]) => field);
    const unknown = [...states.entries(), ...preferenceStates.entries()].filter(([, state]) => state === "unknown").map(([field]) => field);
    const matchedConstraints = [...states.entries(), ...preferenceStates.entries()].filter(([, state]) => state === "matched").map(([field]) => field);
    const eligibility = failed.length ? (failed.includes("product_kind") ? "related_candidate" : "excluded") : (unknown.length ? "partial_candidate" : "exact_candidate");
    const relevance = eligibility === "exact_candidate" ? "A" : eligibility === "partial_candidate" ? "B" : "D";
    const verification = item.sales_verification_status === "verified_active" && item.verification_status === "verified" && item.verified_completeness_ratio === 1 ? "A" : item.verification_status === "verified" ? "B" : item.source_urls?.length ? "C" : "D";
    let overall: "A" | "B" | "C" | "D" = relevance > verification ? relevance : verification;
    if (item.sales_verification_status === "listed_unverified" || !item.domain_gate_passed || ratio === 0) {
      overall = overall > "C" ? overall : "C";
    }
    const decision = { mode: "discovery", eligibility, decision_scope: "discovery_only", score, relevance_grade: relevance, data_completeness_grade: discoveryConfidence(item), verification_grade: verification, overall_candidate_grade: overall, matched_constraints: matchedConstraints, unknown_constraints: unknown, failed_constraints: failed, decision_reasons: matchedConstraints.map((field) => ({ constraint: field, matched_value: field === "product_kind" ? item.product_kind : field, evidence_field: field })), limitations: item.discovery_limitations ?? ["sales_status_unverified"] };
    if (eligibility === "excluded") {
      excludedSummary.hard_constraint_failed = (excludedSummary.hard_constraint_failed ?? 0) + 1;
      continue;
    }
    if (seen.has(canonicalId)) {
      excludedSummary.duplicate_canonical_product = (excludedSummary.duplicate_canonical_product ?? 0) + 1;
      continue;
    }
    seen.add(canonicalId);
    groups[`${eligibility}s` as keyof typeof groups].push({ canonical_product_id: canonicalId, id: item.id, title: item.title, provider: item.provider, product_kind: item.product_kind, catalog_recommendation_status: item.catalog_recommendation_status ?? item.recommendation_status, catalog_recommendation_scope: item.catalog_recommendation_scope ?? item.recommendation_scope, relevance_grade: relevance, data_completeness_grade: discoveryConfidence(item), verification_grade: verification, overall_candidate_grade: overall, matched_constraints: decision.matched_constraints, unknown_constraints: decision.unknown_constraints, failed_constraints: decision.failed_constraints, why_included: decision.decision_reasons, limitations: decision.limitations, source_urls: item.source_urls ?? [], source_basis_dates: item.source_basis_dates ?? [], decision });
  }
  for (const values of Object.values(groups)) values.sort((left, right) => Number((right.decision as Record<string, unknown>).score) - Number((left.decision as Record<string, unknown>).score) || String(left.canonical_product_id).localeCompare(String(right.canonical_product_id), "ko-KR")).splice(limit);
  return { requested_intent: /추천|골라|알려|찾아/.test(query) ? "recommend" : "discovery", executed_mode: "discovery", fallback_reason: /추천|골라|알려|찾아/.test(query) ? "verified_recommendation_candidate_not_available" : undefined, parsed_query: parsed, ...groups, excluded_summary: excludedSummary, warnings: ["탐색 결과는 최적 상품·승인·보험료·보장 적합성을 뜻하지 않습니다."], engine_version: DISCOVERY_ENGINE_VERSION, field_extractor_version: FIELD_EXTRACTOR_VERSION };
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
    (item) => normalizeQuery(item.id) === itemId || normalizeQuery(item.canonical_product_id ?? "") === itemId || itemAliases(item).some((alias) => normalizeQuery(alias) === itemId),
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

function verificationEvidenceBlocker(item: FinanceItem): string | undefined {
  if (item.verification_status !== "verified") return "verification_not_verified";
  if (!isRecord(item.verification_evidence)) {
    return "missing_verification_evidence";
  }
  const checksums = item.verification_evidence.source_checksums;
  const evidence = item.verification_evidence.evidence;
  if (!Array.isArray(evidence) || !evidence.length || evidence.some((value) => !isRecord(value) || typeof value.source_url !== "string" || !value.source_url || typeof value.document_type !== "string" || !value.document_type || typeof value.locator !== "string" || !value.locator || !isPastOrCurrentIsoDate(value.captured_at) || (typeof value.field !== "string" && typeof value.verified_field !== "string") || (value.value === undefined && typeof value.source_text !== "string"))) return "invalid_verification_evidence";
  if (!item.source_records?.length) return "missing_source_records";
  const sourceChecksums = item.source_records
    .map((record) => record.source_checksum)
    .filter((checksum): checksum is string => typeof checksum === "string" && checksum.length > 0);
  if (sourceChecksums.length !== item.source_records.length) return "missing_source_checksum";
  if (!Array.isArray(checksums) || !sourceChecksums.every((checksum) => checksums.includes(checksum))) return "source_checksum_mismatch";
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

function recommendationBlocker(item: FinanceItem): string | undefined {
  if (!ENABLE_PUBLIC_RECOMMENDATION) return "public_recommendation_disabled";
  if (item.public_recommendation_exclusion_reasons?.length) return "public_recommendation_excluded";
  if (item.recommendation_status !== "verified_recommendation_candidate") return "not_verified_recommendation_candidate";
  if (item.recommendation_scope !== "public_recommendation") return "not_public_recommendation_scope";
  if (item.sales_status !== "active" || item.sales_verification_status !== "verified_active") return "sales_not_verified";
  return verificationEvidenceBlocker(item);
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

function isPastOrCurrentIsoDate(value: unknown): value is string {
  if (typeof value !== "string" || !/^\d{4}-\d{2}-\d{2}$/.test(value)) return false;
  const timestamp = Date.parse(`${value}T00:00:00Z`);
  return Number.isFinite(timestamp) && new Date(timestamp).toISOString().slice(0, 10) === value && value <= new Date().toISOString().slice(0, 10);
}

function comparisonBlocker(item: FinanceItem): string | undefined {
  if (item.comparison_exclusion_reasons?.length) return "comparison_excluded";
  if (item.recommendation_scope !== "comparison_only") return "not_comparison_scope";
  if (item.source_listing_status !== "listed") return "source_not_listed";
  if (item.sales_verification_status !== "verified_active") return "sales_not_verified";
  if (item.source_freshness_status !== "current") return "stale_source";
  const verifiedAt = Date.parse(`${item.sales_verified_at ?? ""}T00:00:00Z`);
  if (!Number.isFinite(verifiedAt) || verifiedAt > Date.now() || Date.now() - verifiedAt > 31 * 24 * 60 * 60 * 1000) return "stale_source";
  if (item.verification_status !== "verified") return "not_verified";
  const evidenceBlocker = verificationEvidenceBlocker(item);
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
  if (depositAmount !== undefined && typeof option.minimum_deposit_krw === "number" && depositAmount < option.minimum_deposit_krw) return "amount_below_minimum";
  if (monthlyPayment !== undefined && typeof option.monthly_payment_max_krw === "number" && monthlyPayment > option.monthly_payment_max_krw) return "monthly_payment_exceeds_limit";
  if (monthlyPayment !== undefined && typeof option.monthly_payment_min_krw === "number" && monthlyPayment < option.monthly_payment_min_krw) return "monthly_payment_below_minimum";
  if (domain === "saving" && savingMethod && typeof option.saving_method === "string" && option.saving_method !== savingMethod) return "saving_method_mismatch";
  if (!Array.isArray(option.source_urls) || !option.source_urls.length) return "missing_source_url";
  return undefined;
}

function comparisonCandidate(item: FinanceItem, option: Record<string, unknown>, eligibleConditions: ReadonlySet<string>, depositAmount: number | undefined, monthlyPayment: number | undefined, taxRatePercent: number): Record<string, unknown> {
  const baseRate = option.base_rate_percent;
  const maximumRate = typeof option.maximum_rate_percent === "number" ? option.maximum_rate_percent : baseRate;
  if (typeof baseRate !== "number" || typeof maximumRate !== "number") throw new Error("Comparison option has invalid rate fields");
  const conditions = Array.isArray(option.preferential_rate_conditions) ? option.preferential_rate_conditions.filter(isRecord) : [];
  const matched = conditions.filter((condition) => typeof condition.condition_id === "string" && eligibleConditions.has(condition.condition_id));
  const unmatched = conditions.filter((condition) => typeof condition.condition_id === "string" && !eligibleConditions.has(condition.condition_id));
  const additionalRate = matched.reduce((total, condition) => total + (typeof condition.additional_rate_percent === "number" ? condition.additional_rate_percent : 0), 0);
  const achievableRate = Math.min(baseRate + additionalRate, maximumRate);
  const termMonths = typeof option.term_months === "number" ? option.term_months : 0;
  const isDeposit = item.search_type === "deposit";
  const amountMissing = isDeposit ? depositAmount === undefined : monthlyPayment === undefined;
  const principal = amountMissing ? null : isDeposit ? depositAmount : monthlyPayment! * termMonths;
  const grossInterest = amountMissing ? null : isDeposit
    ? principal! * achievableRate / 100 * termMonths / 12
    : monthlyPayment! * achievableRate / 100 * (termMonths * (termMonths + 1) / 2) / 12;
  const taxWithheld = grossInterest === null ? null : grossInterest * taxRatePercent / 100;
  return {
    item_id: item.id,
    title: item.title,
    provider: item.provider,
    base_rate_percent: baseRate,
    maximum_rate_percent: maximumRate,
    achievable_rate_percent: achievableRate,
    matched_preferential_conditions: matched.map((condition) => condition.condition_id),
    unmatched_preferential_conditions: unmatched.map((condition) => condition.condition_id),
    unknown_preferential_conditions: conditions.filter((condition) => typeof condition.condition_id !== "string").map((condition) => condition.description ?? "unidentified_preferential_condition"),
    deposit_limit: option.maximum_deposit_krw,
    monthly_payment_limit: option.monthly_payment_max_krw,
    term_months: option.term_months,
    saving_method: option.saving_method,
    join_channel: option.join_channels ?? [],
    sales_verified_at: item.sales_verified_at,
    score_components: { achievable_rate_percent: achievableRate, source_verified: 1 },
    source_urls: option.source_urls,
    source_basis_dates: item.source_basis_dates ?? [],
    comparison_basis_fields: item.comparison_basis_fields ?? [],
    missing_required_fields: item.missing_required_fields ?? [],
    principal_krw: principal,
    gross_interest_krw: grossInterest === null ? null : Math.round(grossInterest),
    tax_rate_percent: taxRatePercent,
    tax_withheld_krw: taxWithheld === null ? null : Math.round(taxWithheld),
    net_interest_krw: grossInterest === null || taxWithheld === null ? null : Math.round(grossInterest - taxWithheld),
    calculation_assumption: amountMissing ? (isDeposit ? "deposit_amount_required" : "monthly_payment_required") : isDeposit ? "simple_interest_for_full_term_deposit" : "simple_interest_with_each_month_paid_at_month_start",
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
      return {
        item: indexedItem?.canonical_product_id
          ? { ...item, ...indexedItem, criteria: item.criteria, options: item.options, benefits: item.benefits }
          : item,
        itemsById,
      };
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
      if (isDiscoveryQuery(query)) {
        const payload = discoveryPayload(query, data.items, maxResults);
        return { structuredContent: payload, content: [{ type: "text", text: jsonText(payload) }] };
      }

      const allowedTypes = type ? SEARCH_TYPE_GROUPS[type] ?? new Set([type]) : inferredTypesForQuery(normalizedQuery);
      const supportRegion = supportRegionForQuery(normalizedQuery);
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
        .filter((item) => isPubliclySearchable(item) && (!allowedTypes || allowedTypes.has(item.type)) && matchesSearchFilters(item, filters) && matchesSupportRegion(item, supportRegion) && matchesSupportIntent(item, normalizedQuery))
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
          catalog_recommendation_status: item.catalog_recommendation_status,
          catalog_recommendation_scope: item.catalog_recommendation_scope,
          canonical_product_id: item.canonical_product_id,
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
      if (!ENABLE_PUBLIC_RECOMMENDATION) {
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
        tax_rate_percent: z.number().min(0).max(100).optional(),
        limit: z.number().int().min(1).max(20).optional(),
      },
      annotations: {
        title: "Compare Deposit and Saving Products",
        ...READ_ONLY_TOOL_ANNOTATIONS,
      },
    },
    async ({ domain, deposit_amount_krw, monthly_payment_krw, term_months, join_channels, eligible_conditions, saving_method, tax_rate_percent, limit }) => {
      if ((domain === "deposit" && !ENABLE_DEPOSIT_COMPARISON) || (domain === "saving" && !ENABLE_SAVING_COMPARISON)) {
        const payload = { domain, result_count: 0, candidates: [], excluded_count: 0, excluded_sample: [], warnings: ["Deposit and saving comparison is currently disabled."], comparison_engine_version: COMPARISON_ENGINE_VERSION };
        return { structuredContent: payload, content: [{ type: "text", text: jsonText(payload) }] };
      }
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
        candidates.push(...usableOptions.map((option) => comparisonCandidate(item, option, conditions, deposit_amount_krw, monthly_payment_krw, tax_rate_percent ?? 15.4)));
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
        comparison_engine_version: COMPARISON_ENGINE_VERSION,
        basis_date: data.basis_date,
        requested_intent: { domain, deposit_amount_krw, monthly_payment_krw, term_months, join_channels, eligible_conditions, saving_method, tax_rate_percent: tax_rate_percent ?? 15.4 },
        executed_mode: "deterministic_comparison",
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
        catalog_recommendation_status: item.catalog_recommendation_status,
        catalog_recommendation_scope: item.catalog_recommendation_scope,
        canonical_product_id: item.canonical_product_id,
        source_records: item.source_records ?? [],
        preferred_source: item.preferred_source,
        merged_fields: item.merged_fields ?? {},
        field_provenance: item.field_provenance ?? {},
        field_conflicts: item.field_conflicts ?? {},
        recommendation_model_version: item.recommendation_model_version,
        recommendation_exclusion_reasons: item.recommendation_exclusion_reasons ?? [],
        recommendation_basis_fields: item.recommendation_basis_fields ?? [],
        comparison_basis_fields: item.comparison_basis_fields ?? [],
        verification_status: item.verification_status,
        quality_flags: item.quality_flags ?? [],
        freshness_status: item.freshness_status,
        last_verified_at: item.last_verified_at,
        last_source_checked_at: item.last_source_checked_at,
        last_reviewed_at: item.last_reviewed_at,
        public_recommendation_exclusion_reasons: item.public_recommendation_exclusion_reasons ?? [],
        comparison_exclusion_reasons: item.comparison_exclusion_reasons ?? [],
        discovery_limitations: item.discovery_limitations ?? [],
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
