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
  resolved_canonical_product_id?: string;
  external_product_ids?: { namespace: string; value: string }[];
  provider_external_ids?: { namespace: string; value: string }[];
  provider_roles?: string[];
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
  comparison_engine_gate_passed?: boolean;
  comparison_field_verification_status?: string;
  comparison_field_verification?: Record<string, unknown>;
  comparison_options?: unknown[];
  application_status?: string;
  is_currently_applicable?: boolean;
  application_open_from?: string;
  application_open_to?: string;
  application_window?: Record<string, unknown>;
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
  state?: string;
  collected_at?: string | null;
  normalized_at?: string | null;
  verified_at?: string | null;
  published_at?: string | null;
  source_assertions?: Record<string, unknown>[];
  promotion_receipt?: Record<string, unknown>;
  risk_level?: string;
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
  shards?: SearchIndexShard[];
};

type SearchIndexShard = {
  id: string;
  shard_id: string;
  path: string;
  url?: string;
  web_url?: string;
  item_count?: number;
  export_checksum?: string;
};

type FinanceManifest = {
  version: string;
  basis_date: string;
  name: string;
  description?: string;
  release_status?: string;
  recommendation_enabled?: boolean;
  blocking_reasons?: string[];
  openfin_120_live_regression?: Record<string, unknown>;
  runtime_quality_metrics?: Record<string, unknown>;
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

type SearchIndexFile = {
  readonly version: string;
  readonly basis_date: string;
  readonly item_count?: number;
  readonly export_checksum?: string;
  readonly items?: readonly FinanceItem[];
  readonly shards?: readonly SearchIndexShard[];
};

type CachedSearchIndexMetadata = {
  readonly data: SearchIndexFile;
  readonly loadedAt: number;
};

type CachedSearchItems = {
  readonly items: readonly FinanceItem[];
  readonly loadedAt: number;
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
const EXCLUDED_SAMPLE_LIMIT = 10;
const QUERY_PARSER_VERSION = "openfin-query-parser-v1.3.0";
const FIELD_EXTRACTOR_VERSION = "openfin-field-extractor-v1.1.0";
const DISCOVERY_ENGINE_VERSION = "openfin-discovery-v1.3.0";
const COMPARISON_ENGINE_VERSION = "openfin-comparison-v1.1.0";
const PERSONAL_FINANCE_POLICY_VERSION = "openfin-personal-finance-v1.0.0";
const ADVICE_POLICY_VERSION = "openfin-advice-policy-v1.0.0";
const MINIMUM_EMERGENCY_FUND_MONTHS = 3;
const HIGH_INTEREST_DEBT_RATE_PERCENT = 15;
const SENSITIVE_KEY_TOKENS = new Set([
  "accountnumber", "bankaccount", "cardnumber", "creditcardnumber", "residentregistrationnumber",
  "rrn", "password", "passcode", "pin", "certificate", "privatekey", "apikey", "apitoken",
  "accesstoken", "refreshtoken", "secret", "ssn",
]);
const PROMPT_INJECTION_TOKENS = new Set(["무시", "이전", "지시", "시스템", "프롬프트", "명령", "규칙", "ignore", "previous", "instruction", "instructions", "system", "prompt", "rule", "rules"]);

let cachedGraph: CachedGraph | undefined;
let cachedManifest: { data: FinanceManifest; loadedAt: number } | undefined;
let cachedSearchIndexMetadata: CachedSearchIndexMetadata | undefined;
let cachedSearchItems: CachedSearchItems | undefined;

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

function canonicalSupportRegion(region: string | undefined): string | undefined {
  if (!region) return undefined;
  const normalized = normalizeQuery(region);
  const aliases: Record<string, string> = {
    "서울": "서울특별시",
    "부산": "부산광역시",
    "대구": "대구광역시",
    "인천": "인천광역시",
    "광주": "광주광역시",
    "대전": "대전광역시",
    "울산": "울산광역시",
    "세종": "세종특별자치시",
    "경기": "경기도",
    "강원": "강원특별자치도",
    "충북": "충청북도",
    "충남": "충청남도",
    "전북": "전북특별자치도",
    "전남": "전라남도",
    "경북": "경상북도",
    "경남": "경상남도",
    "제주": "제주특별자치도",
  };
  return aliases[normalized] ?? region;
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
  const requiresRent = /월세/.test(query);
  const requiresHousing = /(월세|주거|전세|임대|보증금|입주|공급|수선)/.test(query);
  const requiresEmployment = /(취업|일자리|구직)/.test(query);
  const requiresEducation = /교육/.test(query);
  const requiresHealth = /(의료|건강)/.test(query);
  const requiresCulture = /(문화|예술)/.test(query);
  const requiresBusiness = /(창업|사업|소상공인)/.test(query);
  const requiresCurrentAvailability = /(지원|보조금|신청|월세|주거)/.test(query);
  const currentlyAvailable = item.is_currently_applicable === true || ["open", "always_open"].includes(item.application_status ?? "");
  return (!requiresYouth || targetGroups.has("youth"))
    && (!requiresRent || categories.has("housing") || categories.has("rent"))
    && (!requiresHousing || categories.has("housing") || categories.has("rent") || categories.has("lease_deposit") || categories.has("deposit_guarantee") || categories.has("housing_supply") || categories.has("housing_repair"))
    && (!requiresEmployment || categories.has("employment"))
    && (!requiresEducation || categories.has("education"))
    && (!requiresHealth || categories.has("health"))
    && (!requiresCulture || categories.has("culture"))
    && (!requiresBusiness || categories.has("business"))
    && (!requiresCurrentAvailability || currentlyAvailable);
}

function supportMatchTier(item: FinanceItem, query: string): "exact" | "partial" | "related" | undefined {
  if (item.type !== "support-program" || !SUPPORT_INTENT_RE.test(query)) return undefined;
  const text = itemSearchText(item);
  const categories = new Set((item.support_category ?? []).map(normalizeQuery));
  const youthRequested = query.includes("청년");
  const youthMatched = !youthRequested || (item.target_group ?? []).map(normalizeQuery).includes("youth");
  const rentRequested = query.includes("월세");
  const rentMatched = categories.has("rent") || text.includes("월세");
  const housingMatched = categories.has("housing") || categories.has("lease_deposit") || categories.has("deposit_guarantee") || categories.has("housing_supply") || categories.has("housing_repair");
  if (youthMatched && (!rentRequested || rentMatched)) return "exact";
  if (youthMatched && housingMatched) return "partial";
  return "related";
}

function supportParsedQuery(query: string, explicitRegion: string | undefined): Record<string, unknown> {
  const normalized = normalizeQuery(query);
  const categories = [
    ...(normalized.includes("월세") ? ["housing", "rent"] : []),
    ...(normalized.includes("전세") || normalized.includes("보증금") ? ["lease_deposit", "deposit_guarantee"] : []),
    ...(normalized.includes("취업") || normalized.includes("일자리") || normalized.includes("구직") ? ["employment"] : []),
    ...(normalized.includes("교육") ? ["education"] : []),
    ...(normalized.includes("의료") || normalized.includes("건강") ? ["health"] : []),
    ...(normalized.includes("문화") || normalized.includes("예술") ? ["culture"] : []),
    ...(normalized.includes("창업") || normalized.includes("사업") || normalized.includes("소상공인") ? ["business"] : []),
  ];
  return {
    original_query: query,
    intent: SUPPORT_INTENT_RE.test(normalized) ? "find-support" : "search",
    region: canonicalSupportRegion(explicitRegion ?? supportRegionForQuery(normalized)),
    target_groups: normalized.includes("청년") ? ["youth"] : [],
    support_categories: [...new Set(categories)],
  };
}

function supportExcludedSummary(
  items: readonly FinanceItem[],
  query: string,
  supportRegion: string | undefined,
  filters: SearchFilters,
  allowedTypes: Set<string> | null,
  returnedIds: ReadonlySet<string>,
  maxResults: number,
): Record<string, number> {
  if (!SUPPORT_INTENT_RE.test(query)) return {};
  const counts: Record<string, number> = {};
  const add = (reason: string) => { counts[reason] = (counts[reason] ?? 0) + 1; };
  for (const item of items.filter((candidate) => candidate.type === "support-program")) {
    if (returnedIds.has(item.id)) continue;
    if (!isPubliclySearchable(item)) { add("not_publicly_searchable"); continue; }
    if (allowedTypes && !allowedTypes.has(item.type)) { add("type_filter"); continue; }
    if (!matchesSearchFilters(item, filters)) { add("filter_mismatch"); continue; }
    if (!matchesSupportRegion(item, supportRegion)) { add("region_mismatch"); continue; }
    if (!matchesSupportIntent(item, query)) { add("support_intent_mismatch"); continue; }
    if (scoreItem(item, query) <= 0) { add("query_mismatch"); continue; }
    if (maxResults > 0) add("result_limit");
  }
  return counts;
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

const PROVIDER_ALIASES: Record<string, readonly string[]> = {
  "삼성카드": ["삼성카드", "삼성"],
  "BC바로카드": ["BC바로카드", "BC카드", "비씨카드"],
  "신한카드": ["신한카드", "신한"],
  "KB국민카드": ["KB국민카드", "KB국민", "국민카드", "KB"],
  "롯데카드": ["롯데카드", "롯데"],
  "광주은행": ["광주은행"],
};
const GENERIC_PRODUCT_TOKENS = new Set(["카드", "체크카드", "신용카드", "보험", "대출", "예금", "적금", "정기예금", "자유적금", "자유적립", "실손보험", "실비보험", "암보험", "상해보험", "질병보험", "정기보험", "종신보험", "신용대출", "전세대출", "월세대출", "정책대출", "주택담보대출", "상품", "추천", "비교", "후보", "순위", "없는", "비갱신형", "갱신형", "전월실적", "연회비", "교통", "쇼핑", "온라인", "할인", "적립", "마일리지", "구독", "직장인", "중도상환수수료", "낮은", "금리", "청년"]);

function compactProductText(value: string): string {
  return value.toLocaleLowerCase("ko-KR").replace(/[^0-9a-z가-힣]/g, "");
}

function providerForQuery(query: string): string | undefined {
  const compact = compactProductText(query);
  const matches = Object.entries(PROVIDER_ALIASES).filter(([, aliases]) => aliases.some((alias) => compact.includes(compactProductText(alias))));
  if (!matches.length) return undefined;
  return matches.sort((left, right) => Math.max(...right[1].map((alias) => compactProductText(alias).length)) - Math.max(...left[1].map((alias) => compactProductText(alias).length)))[0][0];
}

function productNameTokens(query: string, provider: string | undefined): readonly string[] {
  const providerTokens = new Set((provider ? PROVIDER_ALIASES[provider] ?? [] : []).map(compactProductText));
  const genericTokens = new Set([...GENERIC_PRODUCT_TOKENS].map(compactProductText));
  return [...new Set((query.match(/[0-9A-Za-z가-힣]+/g) ?? [])
    .map(compactProductText)
    .filter((token) => token && token !== "월" && !/^\d+(?:\.\d+)?개월$/.test(token) && !/^\d+(?:\.\d+)?(?:천만원|억원|만원|천원|원)$/.test(token) && !genericTokens.has(token) && !providerTokens.has(token)))];
}

function namedQueryParts(query: string): { cleanQuery: string; unparsedTokens: string[]; promptInjectionDetected: boolean } {
  const tokens = query.match(/[0-9A-Za-z가-힣]+/g) ?? [];
  const firstInjection = tokens.findIndex((token) => PROMPT_INJECTION_TOKENS.has(token.toLocaleLowerCase("ko-KR")));
  if (firstInjection < 0) return { cleanQuery: query, unparsedTokens: [], promptInjectionDetected: false };
  return {
    cleanQuery: tokens.slice(0, firstInjection).join(" "),
    unparsedTokens: tokens.slice(firstInjection),
    promptInjectionDetected: true,
  };
}

function providerForNamedQuery(query: string, items: readonly FinanceItem[]): string | undefined {
  return providerForQuery(query) ?? [...new Set(items.map((item) => item.provider).filter((value): value is string => Boolean(value)))]
    .filter((provider) => compactProductText(query).includes(compactProductText(provider)))
    .sort((left, right) => compactProductText(right).length - compactProductText(left).length)[0];
}

function isNamedProductQuery(query: string): boolean {
  const provider = providerForQuery(query);
  return Boolean(requestedProductKind(query) && productNameTokens(query, provider).length);
}

function strictNamedProductPayload(query: string, items: readonly FinanceItem[], limit: number, env: Env): Record<string, unknown> | undefined {
  const parts = namedQueryParts(query);
  const provider = providerForNamedQuery(parts.cleanQuery, items);
  const productKind = requestedProductKind(parts.cleanQuery);
  const nameTokens = productNameTokens(parts.cleanQuery, provider);
  if (!productKind && !provider && !nameTokens.length) return undefined;
  if (!productKind || !provider || !nameTokens.length) {
    return {
      query,
      resolution_status: "ambiguous",
      result_count: 0,
      results: [],
      exact_results: [],
      unparsed_query_tokens: parts.unparsedTokens,
      prompt_injection_detected: parts.promptInjectionDetected,
      reason_codes: [
        ...(!provider ? ["PROVIDER_REQUIRED"] : []),
        ...(!productKind ? ["PRODUCT_KIND_REQUIRED"] : []),
        ...(!nameTokens.length ? ["OFFICIAL_PRODUCT_NAME_REQUIRED"] : []),
      ],
      warnings: ["Named product queries require provider, official product name, and product kind; no broad fallback was used."],
    };
  }
  const compactNames = nameTokens.map(compactProductText);
  const matches = dedupeProductItems(items).filter((item) => {
    if (!item.provider || compactProductText(item.provider) !== compactProductText(provider)) return false;
    if (item.product_kind !== productKind) return false;
    const text = compactProductText([item.title, ...(item.search_aliases ?? []), ...(item.aliases ?? [])].join(" "));
    return compactNames.every((token) => text.includes(token));
  });
  const resolutionStatus = matches.length === 0 ? "not_found" : matches.length === 1 ? "exact" : "ambiguous";
  const results = matches.slice(0, limit).map((item) => ({
    id: item.id,
    title: item.title,
    type: item.type,
    provider: item.provider,
    product_kind: item.product_kind,
    canonical_product_id: item.resolved_canonical_product_id ?? item.canonical_product_id ?? item.id,
    resolved_canonical_product_id: item.resolved_canonical_product_id ?? item.canonical_product_id ?? item.id,
    resolution_status: resolutionStatus,
    unparsed_query_tokens: parts.unparsedTokens,
    prompt_injection_detected: parts.promptInjectionDetected,
    source_urls: item.source_urls ?? [],
    url: itemUrl(env, item.id),
  }));
  const sources = [...new Set(matches.flatMap((item) => item.source_urls ?? []).filter(Boolean))];
  const dataAsOf = [...new Set(matches.flatMap((item) => item.source_basis_dates ?? []).filter(Boolean))].sort().at(-1) ?? null;
  return {
    query,
    parsed_intent: { intent: "search", domain: productKind === "check-card" || productKind === "credit-card" ? "card" : productKind?.includes("loan") ? "loan" : productKind?.includes("insurance") ? "insurance" : productKind },
    resolution: {
      status: resolutionStatus,
      provider_required: provider,
      product_kind_required: productKind,
      name_tokens_required: nameTokens,
      canonical_product_ids: results.map((result) => result.resolved_canonical_product_id),
      candidate_count: results.length,
    },
    resolution_status: resolutionStatus,
    result_count: results.length,
    results,
    exact_results: resolutionStatus === "exact" ? results : [],
    partial_results: resolutionStatus === "ambiguous" ? results : [],
    data_as_of: dataAsOf,
    sources,
    limitations: [
      "named product matching requires provider, official product name, and product kind",
      "no any-term fallback is used for named product queries",
      ...(parts.promptInjectionDetected ? ["prompt-injection-like suffix was surfaced as unparsed input and ignored"] : []),
    ],
    unparsed_query_tokens: parts.unparsedTokens,
    prompt_injection_detected: parts.promptInjectionDetected,
    reason_codes: results.length ? [] : ["EXACT_PRODUCT_NOT_FOUND"],
    warnings: ["Prompt-injection-like suffixes are surfaced as unparsed tokens and ignored for matching; no any-term fallback was used."],
  };
}

type DiscoveryConstraint = { readonly field: string; readonly operator: "equals" | "lte" | "contains"; readonly value: string | number };
type ParsedDiscoveryQuery = {
  readonly original_query: string;
  readonly parser_version: string;
  readonly intent: "discovery";
  readonly domain: DiscoveryDomain;
  readonly product_kind?: string;
  readonly provider?: string;
  readonly product_name_tokens: readonly string[];
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
  const provider = providerForQuery(query);
  const nameTokens = productNameTokens(query, provider);
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
  if (provider) hardConstraints.push({ field: "provider", operator: "equals", value: provider });
  if (nameTokens.length) hardConstraints.push({ field: "product_name_tokens", operator: "contains", value: nameTokens.join("|") });
  return { original_query: query, parser_version: QUERY_PARSER_VERSION, intent: "discovery", domain, product_kind: productKind, provider, product_name_tokens: nameTokens, hard_constraints: hardConstraints, soft_preferences: softPreferences, negative_constraints: [], numeric_constraints: hardConstraints.filter((constraint) => typeof constraint.value === "number"), unparsed_tokens: [] };
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
  if (field === "provider") {
    const provider = compactProductText(item.provider ?? "");
    return (PROVIDER_ALIASES[String(expected)] ?? [String(expected)]).some((alias) => provider.includes(compactProductText(alias))) ? "matched" : "failed";
  }
  if (field === "product_name_tokens") {
    const expectedTokens = String(expected).split("|").map(compactProductText).filter(Boolean);
    const candidate = compactProductText(candidateText);
    return expectedTokens.length && expectedTokens.every((token) => candidate.includes(token)) ? "matched" : "failed";
  }
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

function discoveryDecisionReason(item: FinanceItem, field: string): Record<string, unknown> {
  const values = discoveryValues(item, field === "benefit_category" ? "benefit_categories" : field);
  const matchedValue = field === "product_kind" ? item.product_kind : values[0];
  return {
    constraint: field,
    matched_value: matchedValue ?? null,
    evidence_field: field,
    evidence_text: typeof matchedValue === "string" ? matchedValue : undefined,
    source_url: item.source_urls?.[0],
    source_locator: item.source_basis_dates?.[0],
  };
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
    const canonicalId = item.resolved_canonical_product_id ?? item.canonical_product_id ?? item.id;
    const states = new Map(parsed.hard_constraints.map((constraint) => [constraint.field, discoveryConstraintState(item, constraint)]));
    const preferenceStates = new Map(parsed.soft_preferences.map((preference) => [preference, discoveryPreferenceState(item, preference)]));
    const failed = [...states.entries()].filter(([, state]) => state === "failed").map(([field]) => field);
    if (domain === "insurance" && !parsed.product_kind && item.product_kind === "other-protection") failed.push("product_kind");
    const unknown = [...states.entries(), ...preferenceStates.entries()].filter(([, state]) => state === "unknown").map(([field]) => field);
    const matchedConstraints = [...states.entries(), ...preferenceStates.entries()].filter(([, state]) => state === "matched").map(([field]) => field);
    const score = 35 + Math.min(20, matched.length * 10)
      + (matchedConstraints.includes("product_name_tokens") ? 40 : 0)
      + (matchedConstraints.includes("provider") ? 25 : 0)
      + Math.round(ratio * 10)
      + (item.source_freshness_status === "current" ? 5 : 0);
    const eligibility = failed.length ? (["product_kind", "provider", "product_name_tokens"].some((field) => failed.includes(field)) ? "related_candidate" : "excluded") : (unknown.length ? "partial_candidate" : "exact_candidate");
    const relevance = eligibility === "exact_candidate" ? "A" : eligibility === "partial_candidate" ? "B" : "D";
    const verification = item.sales_verification_status === "verified_active" && item.verification_status === "verified" && item.verified_completeness_ratio === 1 ? "A" : item.verification_status === "verified" ? "B" : item.source_urls?.length ? "C" : "D";
    const dataGrade = discoveryConfidence(item);
    let overall: "A" | "B" | "C" | "D" = relevance;
    if (verification > overall) overall = verification;
    if (dataGrade > overall) overall = dataGrade;
    if (item.sales_verification_status === "listed_unverified" || !item.domain_gate_passed || ratio === 0) {
      overall = overall > "C" ? overall : "C";
    }
    const decision = { mode: "discovery", eligibility, decision_scope: "discovery_only", score, relevance_grade: relevance, data_completeness_grade: dataGrade, verification_grade: verification, overall_candidate_grade: overall, matched_constraints: matchedConstraints, unknown_constraints: unknown, failed_constraints: failed, decision_reasons: matchedConstraints.map((field) => discoveryDecisionReason(item, field)), limitations: item.discovery_limitations ?? ["sales_status_unverified"] };
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

function resolveExportUrl(entry: { path: string; url?: string; web_url?: string }, manifestUrl: string): string {
  if (entry.web_url) {
    return entry.web_url;
  }
  if (entry.url) {
    return entry.url;
  }
  return new URL(entry.path, manifestUrl).toString();
}

class SearchIndexContractError extends Error {
  readonly name = "SearchIndexContractError";

  constructor(readonly detail: string) {
    super(`Finance search-index contract error: ${detail}`);
  }
}

function isFinanceItem(value: unknown): value is FinanceItem {
  return isRecord(value) && typeof value.id === "string" && typeof value.title === "string" && typeof value.type === "string";
}

function parseSearchItems(value: unknown, source: string): readonly FinanceItem[] {
  const items = Array.isArray(value) ? value : isRecord(value) ? value.items : undefined;
  if (!Array.isArray(items) || !items.every(isFinanceItem)) {
    throw new SearchIndexContractError(`${source} must be a raw item array or an object with an items array`);
  }
  return items;
}

function parseSearchShard(value: unknown, source: string): SearchIndexShard {
  if (!isRecord(value) || typeof value.id !== "string" || typeof value.shard_id !== "string" || typeof value.path !== "string") {
    throw new SearchIndexContractError(`${source} must include id, shard_id, path, and integer item_count`);
  }
  const itemCount = value.item_count;
  if (typeof itemCount !== "number" || !Number.isInteger(itemCount)) {
    throw new SearchIndexContractError(`${source} must include id, shard_id, path, and integer item_count`);
  }
  if (value.url !== undefined && typeof value.url !== "string") {
    throw new SearchIndexContractError(`${source}.url must be a string when present`);
  }
  if (value.web_url !== undefined && typeof value.web_url !== "string") {
    throw new SearchIndexContractError(`${source}.web_url must be a string when present`);
  }
  if (value.export_checksum !== undefined && typeof value.export_checksum !== "string") {
    throw new SearchIndexContractError(`${source}.export_checksum must be a string when present`);
  }
  return {
    id: value.id,
    shard_id: value.shard_id,
    path: value.path,
    url: value.url,
    web_url: value.web_url,
    item_count: itemCount,
    export_checksum: value.export_checksum,
  };
}

function parseSearchIndexFile(value: unknown, source: string): SearchIndexFile {
  if (!isRecord(value) || typeof value.version !== "string" || typeof value.basis_date !== "string") {
    throw new SearchIndexContractError(`${source} must include version and basis_date`);
  }
  const itemCount = value.item_count;
  if (itemCount !== undefined && (typeof itemCount !== "number" || !Number.isInteger(itemCount))) {
    throw new SearchIndexContractError(`${source}.item_count must be an integer when present`);
  }
  const items = value.items === undefined ? undefined : parseSearchItems(value.items, `${source}.items`);
  const shards = value.shards === undefined
    ? undefined
    : Array.isArray(value.shards)
      ? value.shards.map((shard, index) => parseSearchShard(shard, `${source}.shards[${index}]`))
      : (() => { throw new SearchIndexContractError(`${source}.shards must be an array when present`); })();
  if (value.export_checksum !== undefined && typeof value.export_checksum !== "string") {
    throw new SearchIndexContractError(`${source}.export_checksum must be a string when present`);
  }
  return { version: value.version, basis_date: value.basis_date, item_count: itemCount, export_checksum: value.export_checksum, items, shards };
}

function assertSearchItemCount(actual: number, expected: number | undefined, source: string): void {
  if (!Number.isInteger(expected)) {
    throw new SearchIndexContractError(`${source} is missing integer item_count`);
  }
  if (actual !== expected) {
    throw new SearchIndexContractError(`${source} item_count=${expected} but hydrated ${actual} items`);
  }
}

function assertEmbeddedItemCount(value: unknown, items: readonly FinanceItem[], source: string): void {
  if (!isRecord(value) || value.item_count === undefined) return;
  if (typeof value.item_count !== "number") {
    throw new SearchIndexContractError(`${source}.item_count must be an integer when present`);
  }
  assertSearchItemCount(items.length, value.item_count, source);
}

async function loadSearchIndexMetadata(env: Env): Promise<SearchIndexFile> {
  const now = Date.now();
  if (cachedSearchIndexMetadata && now - cachedSearchIndexMetadata.loadedAt < CACHE_TTL_MS) {
    return cachedSearchIndexMetadata.data;
  }
  const manifestUrl = financeManifestUrl(env);
  const manifest = await loadFinanceManifest(env);
  if (!manifest.search_index) {
    throw new SearchIndexContractError("finance manifest is missing search_index metadata");
  }
  const indexUrl = resolveExportUrl(manifest.search_index, manifestUrl);
  const data = parseSearchIndexFile(await fetchJson<unknown>(indexUrl), indexUrl);
  cachedSearchIndexMetadata = { data, loadedAt: now };
  return data;
}

async function loadSearchItems(env: Env): Promise<readonly FinanceItem[]> {
  const now = Date.now();
  if (cachedSearchItems && now - cachedSearchItems.loadedAt < CACHE_TTL_MS) {
    return cachedSearchItems.items;
  }

  const manifestUrl = financeManifestUrl(env);
  const manifest = await loadFinanceManifest(env);
  const metadata = await loadSearchIndexMetadata(env);
  const inlineItems = metadata.items;
  if (inlineItems) {
    assertSearchItemCount(inlineItems.length, metadata.item_count, "search-index root");
    assertSearchItemCount(inlineItems.length, manifest.search_index?.item_count, "finance manifest search_index");
    cachedSearchItems = { items: inlineItems, loadedAt: now };
    return inlineItems;
  }

  const shards = metadata.shards ?? manifest.search_index?.shards;
  if (!shards?.length) {
    throw new SearchIndexContractError("search-index manifest has neither inline items nor shards");
  }
  const shardItems = await Promise.all(shards.map(async (shard) => {
    const shardUrl = resolveExportUrl(shard, manifestUrl);
    const payload = await fetchJson<unknown>(shardUrl);
    const items = parseSearchItems(payload, shardUrl);
    assertSearchItemCount(items.length, shard.item_count, `search-index shard ${shard.shard_id}`);
    assertEmbeddedItemCount(payload, items, `search-index shard ${shard.shard_id}`);
    return items;
  }));
  const items = shardItems.flat();
  assertSearchItemCount(items.length, metadata.item_count, "search-index root");
  assertSearchItemCount(items.length, manifest.search_index?.item_count, "finance manifest search_index");
  cachedSearchItems = { items, loadedAt: now };
  return items;
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
  return [
    ...(item.legacy_ids ?? []),
    ...(item.search_aliases ?? []),
    ...(item.aliases ?? []),
    ...(item.source_records ?? []).flatMap((record) => [record.id, record.source_record_id].filter((value): value is string => typeof value === "string")),
    ...(item.external_product_ids ?? []).flatMap((identifier) => [identifier.value]),
  ];
}

function resolveCanonicalItemId(rawId: string, items: readonly FinanceItem[]): FinanceItem | undefined {
  const itemId = normalizeQuery(resolveItemId(rawId));
  const direct = items.find((item) => normalizeQuery(item.id) === itemId || normalizeQuery(item.canonical_product_id ?? "") === itemId || itemAliases(item).some((alias) => normalizeQuery(alias) === itemId));
  if (!direct) return undefined;
  const canonicalId = direct.resolved_canonical_product_id ?? direct.canonical_product_id ?? direct.id;
  return dedupeProductItems(items).find((item) => (item.resolved_canonical_product_id ?? item.canonical_product_id ?? item.id) === canonicalId) ?? direct;
}

function sourceItems(item: FinanceItem, itemsById: Map<string, FinanceItem>): FinanceItem[] {
  return (item.sources ?? [])
    .map((sourceId) => itemsById.get(sourceId))
    .filter((source): source is FinanceItem => Boolean(source));
}

function directExportIdForItem(rawId: string): string | undefined {
  const itemId = resolveItemId(rawId);
  if (/^(credit|deduction|tax)\./.test(itemId)) return "tax-ontology";
  if (itemId.startsWith("support.local-gov.")) return "local-government-supports-ontology";
  if (itemId.startsWith("finance.card.")) return "card-products-ontology";
  if (itemId.startsWith("finance.bank.deposit.")) return "deposit-products-ontology";
  if (itemId.startsWith("finance.bank.saving.")) return "saving-products-ontology";
  if (itemId.startsWith("finance.bank.loan.")) return "loan-products-ontology";
  if (itemId.startsWith("finance.insurance.")) return "insurance-products-ontology";
  return undefined;
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

function reasonCounts(excluded: readonly { readonly reason: string }[]): Record<string, number> {
  const counts: Record<string, number> = {};
  for (const item of excluded) {
    counts[item.reason] = (counts[item.reason] ?? 0) + 1;
  }
  return Object.fromEntries(Object.entries(counts).sort(([left], [right]) => left.localeCompare(right)));
}

function productQualityScore(item: FinanceItem): number {
  return (item.verification_status === "verified" ? 1000 : 0)
    + (item.sales_verification_status === "verified_active" ? 500 : 0)
    + Math.round((item.verified_completeness_ratio ?? item.completeness_ratio ?? 0) * 100)
    + (item.source_records?.length ?? 0)
    + (item.source_urls?.length ?? 0);
}

function dedupeProductItems(items: readonly FinanceItem[]): readonly FinanceItem[] {
  const selected = new Map<string, FinanceItem>();
  for (const item of items) {
    const key = item.type === "card-product" || item.type === "bank-product" || item.type === "insurance-product"
      ? item.resolved_canonical_product_id ?? item.canonical_product_id ?? item.id
      : item.id;
    const previous = selected.get(key);
    if (!previous || productQualityScore(item) > productQualityScore(previous)) selected.set(key, item);
  }
  return [...selected.values()];
}

function minimumVerifiedCount(domain: string): number {
  if (domain === "deposit" || domain === "saving") return 30;
  if (domain === "card" || domain === "loan" || domain === "insurance") return 20;
  return 0;
}

function recommendationReadiness(domain: string, items: readonly FinanceItem[]): Record<string, number> {
  return {
    verified_active_product_count: items.filter((item) => item.sales_verification_status === "verified_active").length,
    verification_evidence_product_count: items.filter((item) => isRecord(item.verification_evidence)).length,
    comparison_engine_product_count: items.filter((item) => item.comparison_engine_gate_passed === true).length,
    verified_completeness_product_count: items.filter((item) => item.verified_completeness_ratio === 1).length,
    public_recommendation_candidate_count: items.filter((item) => recommendationBlocker(item) === undefined).length,
    minimum_required_count: minimumVerifiedCount(domain),
  };
}

function recommendationReadinessStates(domain: string, readiness: Record<string, number>): Record<string, string> {
  const comparisonDomain = domain === "deposit" || domain === "saving";
  return {
    discovery: "ready",
    comparison_engine: comparisonDomain && readiness.comparison_engine_product_count > 0 ? "ready" : comparisonDomain ? "blocked" : "not_applicable",
    sales_verification_pilot: readiness.verified_active_product_count >= readiness.minimum_required_count ? "ready" : "blocked",
    comparison_field_verification: comparisonDomain ? (readiness.comparison_engine_product_count > 0 ? "ready" : "blocked") : "not_applicable",
    live_comparison: comparisonDomain ? (readiness.comparison_engine_product_count > 0 ? "ready" : "blocked") : "not_applicable",
    public_recommendation: readiness.public_recommendation_candidate_count > 0 ? "ready" : "blocked",
  };
}

function nextRecommendationActions(domain: string, readiness: Record<string, number>): readonly Record<string, unknown>[] {
  if (readiness.verified_active_product_count === 0) return [{ code: "VERIFY_SALES_STATUS", affected_product_count: readiness.minimum_required_count }];
  if ((domain === "deposit" || domain === "saving") && readiness.public_recommendation_candidate_count === 0 && readiness.verification_evidence_product_count > 0 && readiness.comparison_engine_product_count === 0) {
    return [
      { code: "VERIFY_COMPARISON_FIELDS", affected_product_count: readiness.verification_evidence_product_count },
      { code: "PASS_DOMAIN_GATE", affected_product_count: readiness.verification_evidence_product_count },
    ];
  }
  if (readiness.public_recommendation_candidate_count === 0 && readiness.verification_evidence_product_count > 0) {
    return [{ code: "VERIFY_RECOMMENDATION_FIELDS", affected_product_count: readiness.verification_evidence_product_count }];
  }
  if (readiness.public_recommendation_candidate_count === 0) return [{ code: "REVIEW_PUBLIC_RECOMMENDATION_FLAG", affected_product_count: readiness.minimum_required_count }];
  return [{ code: "USE_VERIFIED_PUBLIC_CANDIDATES", affected_product_count: readiness.public_recommendation_candidate_count }];
}

function nextRecommendationAction(domain: string, readiness: Record<string, number>): string {
  const action = nextRecommendationActions(domain, readiness)[0];
  if (action.code === "VERIFY_SALES_STATUS") return `Verify ${domain} product sales status.`;
  if (action.code === "VERIFY_COMPARISON_FIELDS" || action.code === "PASS_DOMAIN_GATE") return `Complete ${domain} comparison field verification.`;
  if (action.code === "VERIFY_RECOMMENDATION_FIELDS") return `Complete ${domain} recommendation field verification.`;
  if (action.code === "REVIEW_PUBLIC_RECOMMENDATION_FLAG") return `Review ${domain} public recommendation approval and feature flag.`;
  return "Use verified public recommendation candidates.";
}

function comparisonBlockers(domain: string, excludedSummary: Record<string, number>): readonly Record<string, unknown>[] {
  const salesNotVerified = excludedSummary.sales_not_verified ?? 0;
  const fieldNotVerified = excludedSummary.comparison_fields_not_verified ?? 0;
  const label = domain === "deposit" ? "정기예금" : "적금";
  return [
    ...(salesNotVerified ? [{ code: "SALES_NOT_VERIFIED", count: salesNotVerified, message: `판매상태가 검증되지 않은 ${label}입니다.` }] : []),
    ...(fieldNotVerified ? [{ code: "COMPARISON_FIELDS_NOT_VERIFIED", count: fieldNotVerified, message: `비교 필드 검증이 끝나지 않은 ${label}입니다.` }] : []),
  ];
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
  if (item.comparison_engine_gate_passed !== true) return "comparison_fields_not_verified";
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
  if (joinChannels.length && (!optionChannels.length || !joinChannels.some((channel) => optionChannels.includes(normalizeQuery(channel))))) return "join_channel_mismatch";
  if (depositAmount !== undefined && typeof option.maximum_deposit_krw === "number" && depositAmount > option.maximum_deposit_krw) return "amount_exceeds_limit";
  if (depositAmount !== undefined && typeof option.minimum_deposit_krw === "number" && depositAmount < option.minimum_deposit_krw) return "amount_below_minimum";
  if (monthlyPayment !== undefined && typeof option.monthly_payment_max_krw === "number" && monthlyPayment > option.monthly_payment_max_krw) return "monthly_payment_exceeds_limit";
  if (monthlyPayment !== undefined && typeof option.monthly_payment_min_krw === "number" && monthlyPayment < option.monthly_payment_min_krw) return "monthly_payment_below_minimum";
  if (domain === "saving" && savingMethod && (typeof option.saving_method !== "string" || option.saving_method !== savingMethod)) return "saving_method_mismatch";
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
    data_as_of: item.sales_verified_at ?? item.last_verified_at ?? item.source_basis_dates?.[0] ?? null,
    source: option.source_urls ?? item.source_urls ?? [],
    confidence: item.sales_verification_status === "verified_active" ? "verified" : "insufficient_information",
    score_components: { achievable_rate_percent: achievableRate, source_verified: 1 },
    source_urls: option.source_urls,
    source_basis_dates: item.source_basis_dates ?? [],
    comparison_basis_fields: item.comparison_basis_fields ?? [],
    comparison_object_version: COMPARISON_ENGINE_VERSION,
    comparison_field_verification_status: item.comparison_field_verification_status,
    comparison_field_verification: item.comparison_field_verification ?? {},
    missing_required_fields: (item.missing_required_fields ?? []).filter((field) => !(field === "sales_verification_status" && item.sales_verification_status === "verified_active")),
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
  const directExportId = directExportIdForItem(rawId);
  const indexedItem = directExportId ? undefined : resolveCanonicalItemId(rawId, await loadSearchItems(env));
  const itemId = indexedItem?.id ?? resolveItemId(rawId);
  // Non-product nodes are fully represented in the hydrated search index. Avoid
  // loading every ontology export for a tax/support/reference fetch; this keeps
  // the MCP response inside the Worker streaming budget while preserving the
  // same canonical/legacy resolution path used by product fetches.
  if (indexedItem && !["card-product", "bank-product", "insurance-product"].includes(indexedItem.type)) {
    return { item: indexedItem, itemsById: new Map([[indexedItem.id, indexedItem]]) };
  }
  const candidateExports = directExportId
    ? manifest.exports.filter((entry) => entry.id === directExportId)
    : indexedItem?.export_id
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

async function runtimeMetadata(env: Env, manifest: FinanceManifest, metadata: SearchIndexFile): Promise<Record<string, unknown>> {
  const itemCount = metadata.item_count ?? manifest.search_index?.item_count ?? 0;
  return {
    runtime_version: env.RUNTIME_VERSION ?? "openfin-mcp-2026.07.18.1",
    deployment_commit: env.DEPLOYMENT_COMMIT ?? "unknown",
    manifest_version: manifest.version,
    loaded_index_checksum: metadata.export_checksum ?? manifest.search_index?.shards?.map((shard) => shard.export_checksum ?? "").join("") ?? null,
    loaded_item_count: itemCount,
  };
}

function financeKeyToken(value: unknown): string {
  return String(value).toLocaleLowerCase("en-US").replace(/[^a-z0-9]/g, "");
}

const MAX_FINANCE_INPUT_DEPTH = 12;
const MAX_FINANCE_INPUT_NODES = 1_000;
const MAX_FINANCE_OBJECT_KEYS = 100;
const MAX_FINANCE_ARRAY_ITEMS = 200;
const MAX_FINANCE_STRING_LENGTH = 4_096;

function assertFinanceSafe(value: unknown, path = "input", depth = 0, counter: { value: number } = { value: 0 }): void {
  if (depth > MAX_FINANCE_INPUT_DEPTH) throw new Error(`input nesting exceeds ${MAX_FINANCE_INPUT_DEPTH} levels at ${path}`);
  counter.value += 1;
  if (counter.value > MAX_FINANCE_INPUT_NODES) throw new Error(`input contains more than ${MAX_FINANCE_INPUT_NODES} values`);
  if (typeof value === "string") {
    if (value.length > MAX_FINANCE_STRING_LENGTH) throw new Error(`string exceeds ${MAX_FINANCE_STRING_LENGTH} characters at ${path}`);
    return;
  }
  if (Array.isArray(value)) {
    if (value.length > MAX_FINANCE_ARRAY_ITEMS) throw new Error(`array has more than ${MAX_FINANCE_ARRAY_ITEMS} items at ${path}`);
    value.forEach((child, index) => assertFinanceSafe(child, `${path}[${index}]`, depth + 1, counter));
    return;
  }
  if (!isRecord(value)) return;
  if (Object.keys(value).length > MAX_FINANCE_OBJECT_KEYS) throw new Error(`object has more than ${MAX_FINANCE_OBJECT_KEYS} keys at ${path}`);
  for (const [key, child] of Object.entries(value)) {
    const token = financeKeyToken(key);
    if (SENSITIVE_KEY_TOKENS.has(token) || ["password", "token", "secret", "privatekey"].some((suffix) => token.endsWith(suffix))) {
      throw new Error(`sensitive field is not accepted: ${path}.${key}`);
    }
    assertFinanceSafe(child, `${path}.${key}`, depth + 1, counter);
  }
}

function financeNumber(value: unknown, field: string, allowNegative = false): number {
  if (typeof value !== "number" || !Number.isFinite(value) || (!allowNegative && value < 0)) throw new Error(`${field} must be a finite ${allowNegative ? "" : "non-negative "}number`);
  return Math.round(value * 1_000_000) / 1_000_000;
}

function optionalFinanceNumber(value: unknown, field: string): number | null {
  return value === undefined || value === null || value === "" ? null : financeNumber(value, field);
}

function normalizeFinanceSnapshot(raw: Record<string, unknown> | undefined): Record<string, unknown> {
  if (!raw) return {};
  assertFinanceSafe(raw);
  const expenses = isRecord(raw.expenses) ? raw.expenses : {};
  const firstNumber = (keys: readonly string[], field: string, source: Record<string, unknown> = raw): number | null => {
    const key = keys.find((candidate) => source[candidate] !== undefined && source[candidate] !== null && source[candidate] !== "");
    return key ? financeNumber(source[key], field) : null;
  };
  const rawLiabilities = raw.liabilities === undefined ? [] : Array.isArray(raw.liabilities) ? raw.liabilities : [raw.liabilities];
  const liabilities = rawLiabilities.map((value, index) => {
    if (!isRecord(value)) throw new Error(`liabilities[${index}] must be an object`);
    const balance = firstNumber(["balance_krw", "balance", "principal_krw"], `liabilities[${index}].balance_krw`, value);
    if (balance === null) throw new Error(`liabilities[${index}].balance_krw is required`);
    return {
      id: String(value.id ?? `liability-${index + 1}`), kind: String(value.kind ?? "unspecified"), balance_krw: balance,
      annual_rate_percent: optionalFinanceNumber(value.annual_rate_percent ?? value.rate_percent, `liabilities[${index}].annual_rate_percent`),
      monthly_payment_krw: optionalFinanceNumber(value.monthly_payment_krw ?? value.monthly_payment, `liabilities[${index}].monthly_payment_krw`),
    };
  });
  const goals = Array.isArray(raw.goals) ? raw.goals.map((value, index) => {
    if (!isRecord(value)) throw new Error(`goals[${index}] must be an object`);
    const target = firstNumber(["target_amount_krw", "amount_krw", "amount"], `goals[${index}].target_amount_krw`, value);
    if (target === null) throw new Error(`goals[${index}].target_amount_krw is required`);
    return { id: String(value.id ?? `goal-${index + 1}`), target_amount_krw: target, current_funding_krw: firstNumber(["current_funding_krw", "current_amount_krw", "current"], `goals[${index}].current_funding_krw`, value) ?? 0, target_date: value.target_date ?? null, liquidity_need: String(value.liquidity_need ?? "unknown") };
  }) : [];
  const snapshot: Record<string, unknown> = {
    as_of: raw.as_of ?? raw.profile_as_of ?? null, currency: String(raw.currency ?? "KRW").toUpperCase(),
    monthly_net_income_krw: firstNumber(["monthly_net_income_krw", "monthly_net_income", "monthly_income_krw", "monthly_income"], "monthly_net_income_krw"),
    essential_monthly_expenses_krw: firstNumber(["essential_monthly_expenses_krw", "essential_expenses_krw", "essential_monthly_expenses"], "essential_monthly_expenses_krw") ?? firstNumber(["essential_krw", "essential_monthly_krw", "essential"], "essential_monthly_expenses_krw", expenses),
    discretionary_monthly_expenses_krw: firstNumber(["discretionary_monthly_expenses_krw", "optional_monthly_expenses_krw", "discretionary_expenses_krw"], "discretionary_monthly_expenses_krw") ?? firstNumber(["discretionary_krw", "optional_krw", "discretionary"], "discretionary_monthly_expenses_krw", expenses) ?? 0,
    liquid_assets_krw: firstNumber(["liquid_assets_krw", "liquid_assets"], "liquid_assets_krw"), investment_assets_krw: firstNumber(["investment_assets_krw", "investment_assets"], "investment_assets_krw"), other_assets_krw: firstNumber(["other_assets_krw", "other_assets"], "other_assets_krw") ?? 0,
    liabilities, goals, dependents: Math.trunc(financeNumber(raw.dependents ?? 0, "dependents")), liquidity_requirement: raw.liquidity_requirement ?? null,
    risk_tolerance: String(raw.risk_tolerance ?? "unknown"), risk_capacity: String(raw.risk_capacity ?? "unknown"), constraints: isRecord(raw.constraints) ? raw.constraints : {}, asset_allocation: isRecord(raw.asset_allocation) ? raw.asset_allocation : {}, insurance_coverage: isRecord(raw.insurance_coverage) ? raw.insurance_coverage : {},
  };
  if (snapshot.as_of !== null && (typeof snapshot.as_of !== "string" || !/^\d{4}-\d{2}-\d{2}$/.test(snapshot.as_of))) throw new Error("as_of must use YYYY-MM-DD");
  return snapshot;
}

function financeAuditId(...values: unknown[]): string {
  const stable = (value: unknown): unknown => {
    if (Array.isArray(value)) return value.map(stable);
    if (isRecord(value)) return Object.fromEntries(Object.keys(value).sort().map((key) => [key, stable(value[key])]));
    return value;
  };
  const source = JSON.stringify(stable(values));
  let hash = 2166136261;
  for (const character of source) { hash ^= character.charCodeAt(0); hash = Math.imul(hash, 16777619); }
  return `fin-${(hash >>> 0).toString(16).padStart(8, "0")}`;
}

function financeSafety(fields: Partial<Record<string, unknown>> = {}): Record<string, unknown> {
  return {
    mode: "decision_support", status: "ready", reason_codes: [], profile_as_of: null, data_as_of: null,
    assumptions: [], missing_information: [], financial_needs: [], candidates: [], decision_owner: "user", limitations: [], audit_id: financeAuditId(fields),
    as_of: null,
    source: [{ kind: "ontology_or_deterministic_runtime" }],
    confidence: "derived",
    ...fields,
  };
}

function standardResult(payload: Record<string, unknown>): Record<string, unknown> {
  return {
    ...payload,
    as_of: payload.as_of ?? payload.data_as_of ?? payload.profile_as_of ?? null,
    source: payload.source ?? [{ kind: "ontology_or_deterministic_runtime" }],
    confidence: payload.confidence ?? "declared",
    limitations: payload.limitations ?? [],
  };
}

const STANDARD_OUTPUT_SCHEMA = z.object({
  as_of: z.string().nullable(),
  source: z.array(z.record(z.string(), z.unknown())),
  confidence: z.string(),
  limitations: z.array(z.unknown()),
}).passthrough();

function financeMetric(name: string, value: number | null, formula: string, inputs: Record<string, unknown>, snapshot: Record<string, unknown>, assumptions: string[] = []): Record<string, unknown> {
  return { metric: name, value: value === null ? null : Math.round(value * 1_000_000) / 1_000_000, formula, inputs, assumptions, calculated_at: snapshot.as_of ?? "unspecified", policy_version: PERSONAL_FINANCE_POLICY_VERSION };
}

function financeMetrics(snapshot: Record<string, unknown>): Record<string, Record<string, unknown>> {
  const liabilities = Array.isArray(snapshot.liabilities) ? snapshot.liabilities.filter(isRecord) : [];
  const debt = liabilities.reduce((sum, item) => sum + Number(item.balance_krw ?? 0), 0);
  const debtService = liabilities.reduce((sum, item) => sum + Number(item.monthly_payment_krw ?? 0), 0);
  const income = typeof snapshot.monthly_net_income_krw === "number" ? snapshot.monthly_net_income_krw : null;
  const essential = typeof snapshot.essential_monthly_expenses_krw === "number" ? snapshot.essential_monthly_expenses_krw : null;
  const discretionary = Number(snapshot.discretionary_monthly_expenses_krw ?? 0);
  const surplus = income === null || essential === null ? null : income - essential - discretionary - debtService;
  const liquid = typeof snapshot.liquid_assets_krw === "number" ? snapshot.liquid_assets_krw : null;
  const weightedItems = liabilities.filter((item) => typeof item.annual_rate_percent === "number");
  const weightedBalance = weightedItems.reduce((sum, item) => sum + Number(item.balance_krw ?? 0), 0);
  const weightedRate = weightedBalance ? weightedItems.reduce((sum, item) => sum + Number(item.balance_krw) * Number(item.annual_rate_percent), 0) / weightedBalance : null;
  const liquidity = isRecord(snapshot.liquidity_requirement) ? (typeof snapshot.liquidity_requirement.required_amount_krw === "number" ? snapshot.liquidity_requirement.required_amount_krw : typeof snapshot.liquidity_requirement.months === "number" && essential !== null ? snapshot.liquidity_requirement.months * essential : null) : typeof snapshot.liquidity_requirement === "number" ? snapshot.liquidity_requirement : null;
  const coverage = isRecord(snapshot.insurance_coverage) && typeof snapshot.insurance_coverage.required_coverage_krw === "number" ? Math.max(0, snapshot.insurance_coverage.required_coverage_krw - Number(snapshot.insurance_coverage.current_coverage_krw ?? 0)) : null;
  const assets = Number(snapshot.liquid_assets_krw ?? 0) + Number(snapshot.investment_assets_krw ?? 0) + Number(snapshot.other_assets_krw ?? 0);
  return {
    net_worth: financeMetric("net_worth", assets - debt, "liquid_assets + investment_assets + other_assets - liability_balances", { assets_krw: assets, liabilities_krw: debt }, snapshot),
    monthly_surplus: financeMetric("monthly_surplus", surplus, "net_income - essential_expenses - discretionary_expenses - debt_service", { income_krw: income, essential_krw: essential, discretionary_krw: discretionary, debt_service_krw: debtService }, snapshot),
    savings_rate: financeMetric("savings_rate", income && surplus !== null ? surplus / income : null, "monthly_surplus / monthly_net_income", { income_krw: income, surplus_krw: surplus }, snapshot, income ? [] : ["income must be positive"]),
    emergency_fund_months: financeMetric("emergency_fund_months", liquid !== null && essential ? liquid / essential : null, "liquid_assets / essential_monthly_expenses", { liquid_assets_krw: liquid, essential_krw: essential }, snapshot, ["only liquid assets are counted"]),
    debt_service_ratio: financeMetric("debt_service_ratio", income ? debtService / income : null, "monthly_debt_service / monthly_net_income", { debt_service_krw: debtService, income_krw: income }, snapshot),
    weighted_debt_rate_percent: financeMetric("weighted_debt_rate_percent", weightedRate, "sum(balance * annual_rate) / sum(balance)", { rate_known_balance_krw: weightedBalance, liability_count: weightedItems.length }, snapshot, ["liabilities without a known rate are excluded"]),
    liquidity_gap: financeMetric("liquidity_gap", liquidity !== null && liquid !== null ? Math.max(0, liquidity - liquid) : null, "max(0, required_liquidity - liquid_assets)", { required_liquidity_krw: liquidity, liquid_assets_krw: liquid }, snapshot),
    goal_funding_gap: financeMetric("goal_funding_gap", (Array.isArray(snapshot.goals) ? snapshot.goals.filter(isRecord) : []).reduce((sum, goal) => sum + Math.max(0, Number(goal.target_amount_krw) - Number(goal.current_funding_krw ?? 0)), 0), "sum(max(0, target_amount - current_funding))", { goal_count: Array.isArray(snapshot.goals) ? snapshot.goals.length : 0 }, snapshot),
    insurance_coverage_gap: financeMetric("insurance_coverage_gap", coverage, "max(0, required_coverage - current_coverage)", {}, snapshot, ["coverage need must be explicitly supplied"]),
  };
}

function financeNeeds(snapshot: Record<string, unknown>, metrics: Record<string, Record<string, unknown>>): Record<string, unknown>[] {
  const missing = ["as_of", "monthly_net_income_krw", "essential_monthly_expenses_krw", "liquid_assets_krw", "investment_assets_krw"].filter((key) => snapshot[key] === null || snapshot[key] === undefined || snapshot[key] === "");
  const needs: Record<string, unknown>[] = missing.length ? [{ need_type: "information_completion", priority: 1, status: "blocked", evidence: missing, action: "request_missing_finance_snapshot_fields" }] : [];
  const add = (name: string, priority: number, evidence: Record<string, unknown>, action: string) => needs.push({ need_type: name, priority, status: "active", evidence, action });
  const value = (name: string) => metrics[name]?.value;
  if (typeof value("monthly_surplus") === "number" && Number(value("monthly_surplus")) < 0) add("cashflow_stabilization", 1, { monthly_surplus_krw: value("monthly_surplus") }, "reduce_deficit_before_product_selection");
  if (typeof value("weighted_debt_rate_percent") === "number" && Number(value("weighted_debt_rate_percent")) >= HIGH_INTEREST_DEBT_RATE_PERCENT) add("high_interest_debt", 2, { weighted_debt_rate_percent: value("weighted_debt_rate_percent") }, "compare_debt_paydown_scenarios");
  if (typeof value("emergency_fund_months") === "number" && Number(value("emergency_fund_months")) < MINIMUM_EMERGENCY_FUND_MONTHS) add("emergency_liquidity", 2, { emergency_fund_months: value("emergency_fund_months"), target_months: MINIMUM_EMERGENCY_FUND_MONTHS }, "protect_liquid_principal");
  if (typeof value("liquidity_gap") === "number" && Number(value("liquidity_gap")) > 0) add("liquidity_gap", 2, { liquidity_gap_krw: value("liquidity_gap") }, "avoid_locking_required_liquidity");
  if (typeof value("insurance_coverage_gap") === "number" && Number(value("insurance_coverage_gap")) > 0) add("insurance_coverage_gap", 3, { coverage_gap_krw: value("insurance_coverage_gap") }, "review_protection_gap_as_lookup_only");
  for (const goal of Array.isArray(snapshot.goals) ? snapshot.goals.filter(isRecord) : []) {
    const liquidityNeed = String(goal.liquidity_need ?? "unknown");
    if (["high", "short", "principal"].includes(liquidityNeed)) add("short_horizon_goal", 2, { goal_id: goal.id ?? null, target_date: goal.target_date ?? null }, "prefer_liquid_principal_preserving_options");
    if (["low", "long", "growth"].includes(liquidityNeed)) add("long_horizon_goal", 4, { goal_id: goal.id ?? null, target_date: goal.target_date ?? null }, "separate_long_horizon_risk_discussion");
  }
  return needs.sort((a, b) => Number(a.priority) - Number(b.priority) || String(a.need_type).localeCompare(String(b.need_type)));
}

function createServer(env: Env): McpServer {
  const server = new McpServer({
    name: "finance",
    version: "0.2.0",
  });

  const mcpResult = (payload: Record<string, unknown>) => {
    const normalized = standardResult(payload);
    return { structuredContent: normalized, content: [{ type: "text" as const, text: jsonText(normalized) }] };
  };
  const financeResult = (payload: Record<string, unknown>) => mcpResult(financeSafety(payload));

  server.registerTool("get_finance_summary", {
    title: "Get Personal Finance Summary",
    description: "Summarize a transient user-supplied finance snapshot and prioritize needs. This is decision support, not a recommendation.",
    inputSchema: { snapshot: z.record(z.string(), z.unknown()).optional() },
    annotations: { title: "Get Personal Finance Summary", ...READ_ONLY_TOOL_ANNOTATIONS },
  }, async ({ snapshot }) => {
    const normalized = normalizeFinanceSnapshot(snapshot);
    const metrics = financeMetrics(normalized);
    const needs = financeNeeds(normalized, metrics);
    return financeResult(financeSafety({ status: needs.some((need) => need.status === "blocked") ? "insufficient_information" : "ready", profile_as_of: normalized.as_of ?? null, data_as_of: normalized.as_of ?? null, assumptions: ["only explicitly supplied snapshot fields are used"], missing_information: ["as_of", "monthly_net_income_krw", "essential_monthly_expenses_krw", "liquid_assets_krw", "investment_assets_krw"].filter((key) => normalized[key] === null || normalized[key] === undefined), financial_needs: needs, metrics, currency: normalized.currency ?? "KRW", limitations: ["summary does not constitute financial advice or product approval"] }));
  });

  server.registerTool("calculate_finance_metrics", {
    title: "Calculate Finance Metrics",
    description: "Calculate deterministic personal-finance metrics from a transient snapshot.",
    inputSchema: { snapshot: z.record(z.string(), z.unknown()).optional() },
    annotations: { title: "Calculate Finance Metrics", ...READ_ONLY_TOOL_ANNOTATIONS },
  }, async ({ snapshot }) => {
    const normalized = normalizeFinanceSnapshot(snapshot);
    const metrics = financeMetrics(normalized);
    return financeResult(financeSafety({ profile_as_of: normalized.as_of ?? null, data_as_of: normalized.as_of ?? null, assumptions: ["deterministic formulas; missing inputs produce null metrics"], missing_information: ["as_of", "monthly_net_income_krw", "essential_monthly_expenses_krw", "liquid_assets_krw", "investment_assets_krw"].filter((key) => normalized[key] === null || normalized[key] === undefined), financial_needs: financeNeeds(normalized, metrics), metrics, policy_version: PERSONAL_FINANCE_POLICY_VERSION, limitations: ["metrics are educational and not financial advice"] }));
  });

  server.registerTool("evaluate_product_fit", {
    title: "Evaluate Finance Product Fit",
    description: "Evaluate explicit fit conditions for one supplied product without making a recommendation.",
    inputSchema: { snapshot: z.record(z.string(), z.unknown()).optional(), item: z.record(z.string(), z.unknown()), domain: z.string().optional() },
    outputSchema: STANDARD_OUTPUT_SCHEMA,
    annotations: { title: "Evaluate Finance Product Fit", ...READ_ONLY_TOOL_ANNOTATIONS },
  }, async ({ snapshot, item, domain }) => {
    assertFinanceSafe(item);
    const normalized = normalizeFinanceSnapshot(snapshot);
    const requestedId = typeof item.id === "string" ? item.id : typeof item.item_id === "string" ? item.item_id : undefined;
    const catalogItem = (await loadSearchItems(env)).find((candidate) => candidate.id === requestedId || candidate.canonical_product_id === requestedId || candidate.resolved_canonical_product_id === requestedId);
    const candidateItem: FinanceItem | Record<string, unknown> = catalogItem ?? {
      id: requestedId ?? "unresolved-product",
      title: "Unresolved catalog product",
      type: "unknown",
      status: item.status,
      product_status: item.product_status,
      source_listing_status: item.source_listing_status,
      source_assertions: [],
    };
    const value = candidateItem as Record<string, unknown>;
    const failed: string[] = []; const unknown: string[] = catalogItem ? [] : ["catalog_product_unresolved"];
    if (value.status !== undefined && value.status !== "active") failed.push("product_not_active");
    if (value.product_status !== undefined && value.product_status !== "active") failed.push("product_not_active");
    if (value.source_listing_status !== undefined && value.source_listing_status !== "listed") failed.push("source_not_listed");
    if (value.freshness_status === "stale" || value.source_freshness_status === "stale") failed.push("stale_source");
    if (value.verification_status !== "verified") unknown.push("verification_status");
    const assertions = Array.isArray(value.source_assertions) ? value.source_assertions.filter(isRecord) : [];
    if (!assertions.some((assertion) => assertion.verification_status === "verified" && typeof assertion.source_id === "string" && typeof assertion.checksum === "string")) unknown.push("verified_primary_source_assertion");
    if (value.recommendation_status === "manual_review_candidate" || value.recommendation_status === "retired") failed.push("recommendation_state_not_eligible");
    const constraints = isRecord(normalized.constraints) ? normalized.constraints : {};
    if (constraints.provider && value.provider && String(constraints.provider) !== String(value.provider)) failed.push("provider_constraint_failed");
    const requirement = isRecord(normalized.liquidity_requirement) ? normalized.liquidity_requirement : {};
    if (typeof requirement.months === "number" && value.term_months === undefined) unknown.push("term_months");
    if (typeof requirement.months === "number" && typeof value.term_months === "number" && value.term_months > requirement.months) failed.push("term_exceeds_liquidity_horizon");
    const riskCapacity = String(normalized.risk_capacity ?? "unknown"); const productRisk = typeof value.risk_level === "string" ? value.risk_level : undefined;
    const riskOrder: Record<string, number> = { low: 1, conservative: 1, medium: 2, moderate: 2, high: 3, aggressive: 3 };
    if (riskCapacity !== "unknown" && !productRisk) unknown.push("product_risk_level");
    if (riskCapacity !== "unknown" && productRisk && (riskOrder[productRisk] ?? 0) > (riskOrder[riskCapacity] ?? 0)) failed.push("risk_capacity_exceeded");
    const eligible = !failed.length && !unknown.length;
    const candidate = { item_id: value.id ?? requestedId ?? null, domain: domain ?? null, eligible, decision: eligible ? "fit" : failed.length ? "not_fit" : "insufficient_information", failed_conditions: [...new Set(failed)].sort(), unknown_conditions: [...new Set(unknown)].sort(), score: eligible ? 100 : null, score_components: { source_verification: value.verification_status === "verified" ? 30 : 0, current_listing: value.source_listing_status === "listed" ? 20 : 0, liquidity_fit: unknown.includes("term_months") || failed.includes("term_exceeds_liquidity_horizon") ? 0 : 25, risk_fit: unknown.includes("product_risk_level") || failed.includes("risk_capacity_exceeded") ? 0 : 25 }, recommendation_state: value.recommendation_status ?? value.status ?? "unknown", sources: value.source_urls ?? value.sources ?? [], source_assertions: assertions, verification_status: value.verification_status ?? "unknown", promotion_receipt: value.promotion_receipt ?? null, data_as_of: value.last_verified_at ?? value.verified_at ?? value.source_basis_dates ?? normalized.as_of ?? null, limitations: ["fit evaluation is not a recommendation", "user remains the decision owner"], policy_version: ADVICE_POLICY_VERSION };
    return financeResult({ status: eligible ? "ready" : "insufficient_information", profile_as_of: normalized.as_of ?? null, data_as_of: candidate.data_as_of, assumptions: ["only catalog-resolved product fields and user constraints are evaluated"], missing_information: [...new Set(unknown)].sort(), financial_needs: [], candidates: eligible ? [candidate] : [], limitations: candidate.limitations, fit: candidate });
  });

  server.registerTool("simulate_finance_scenario", {
    title: "Simulate Finance Scenario",
    description: "Run a deterministic educational scenario using simple monthly balance arithmetic.",
    inputSchema: { snapshot: z.record(z.string(), z.unknown()).optional(), scenario: z.record(z.string(), z.unknown()).optional() },
    annotations: { title: "Simulate Finance Scenario", ...READ_ONLY_TOOL_ANNOTATIONS },
  }, async ({ snapshot, scenario }) => {
    const normalized = normalizeFinanceSnapshot(snapshot); assertFinanceSafe(scenario);
    const input = scenario ?? {}; const months = financeNumber(input.months ?? 12, "scenario.months");
    if (!Number.isInteger(months) || months < 1 || months > 120) throw new Error("scenario.months must be between 1 and 120");
    const additional = financeNumber(input.additional_monthly_payment_krw ?? 0, "scenario.additional_monthly_payment_krw"); const contribution = financeNumber(input.monthly_contribution_krw ?? 0, "scenario.monthly_contribution_krw");
    const liabilities = Array.isArray(normalized.liabilities) ? normalized.liabilities.filter(isRecord) : []; const debt = liabilities.reduce((sum, item) => sum + Number(item.balance_krw ?? 0), 0); const rateKnown = liabilities.filter((item) => typeof item.annual_rate_percent === "number"); const rateBalance = rateKnown.reduce((sum, item) => sum + Number(item.balance_krw ?? 0), 0); const weightedRate = rateBalance ? rateKnown.reduce((sum, item) => sum + Number(item.balance_krw ?? 0) * Number(item.annual_rate_percent), 0) / rateBalance : 0; const interest = liabilities.reduce((sum, item) => sum + Number(item.balance_krw ?? 0) * Number(item.annual_rate_percent ?? 0) / 100 / 12, 0); const liquid = Number(normalized.liquid_assets_krw ?? 0); const afterDebt = Math.max(0, debt - additional * months);
    const result = { scenario: { months, additional_monthly_payment_krw: additional, monthly_contribution_krw: contribution }, before: { debt_balance_krw: debt, monthly_debt_interest_estimate_krw: interest, liquid_assets_krw: liquid }, after: { debt_balance_krw: afterDebt, monthly_debt_interest_estimate_krw: afterDebt ? afterDebt * weightedRate / 100 / 12 : 0, liquid_assets_krw: liquid + contribution * months }, assumptions: ["simple monthly balance estimate", "weighted debt rate uses only liabilities with a known annual rate", "no taxes, fees, compounding, new borrowing, or product-specific terms are inferred"], limitations: ["scenario is educational and not a promise of future return or approval"] };
    return financeResult(financeSafety({ profile_as_of: normalized.as_of ?? null, data_as_of: normalized.as_of ?? null, assumptions: result.assumptions, financial_needs: [], scenario: result, limitations: result.limitations, policy_version: PERSONAL_FINANCE_POLICY_VERSION }));
  });

  server.registerTool("explain_recommendation", {
    title: "Explain Finance Decision Support",
    description: "Explain inclusion, exclusion, tradeoffs, and limitations for an already-produced candidate; it never creates a recommendation.",
    inputSchema: { candidate: z.record(z.string(), z.unknown()), snapshot: z.record(z.string(), z.unknown()).optional() },
    annotations: { title: "Explain Finance Decision Support", ...READ_ONLY_TOOL_ANNOTATIONS },
  }, async ({ candidate, snapshot }) => {
    assertFinanceSafe(candidate); const normalized = normalizeFinanceSnapshot(snapshot); const eligible = candidate.eligible === true; const explanation = { candidate_id: candidate.item_id ?? candidate.id ?? null, why_included: candidate.matched_conditions ?? candidate.score_components ?? [], why_excluded: candidate.failed_conditions ?? candidate.unknown_conditions ?? [], tradeoffs: candidate.tradeoffs ?? ["source status, eligibility conditions, liquidity, and risk must be checked before the user decides"], sources: candidate.sources ?? [], data_as_of: candidate.data_as_of ?? candidate.as_of ?? normalized.as_of ?? null };
    return financeResult(financeSafety({ status: eligible ? "ready" : "blocked", profile_as_of: normalized.as_of ?? null, data_as_of: explanation.data_as_of, assumptions: candidate.assumptions ?? [], missing_information: candidate.unknown_conditions ?? [], financial_needs: [], candidates: eligible ? [candidate] : [], explanation, limitations: ["explanation does not constitute financial advice or product approval"], audit_id: financeAuditId(candidate, normalized) }));
  });

  server.registerTool("validate_finance_advice", {
    title: "Validate Finance Advice Contract",
    description: "Validate the required fail-closed OpenFin advice response fields and recommendation gate.",
    inputSchema: { advice: z.record(z.string(), z.unknown()) },
    outputSchema: STANDARD_OUTPUT_SCHEMA,
    annotations: { title: "Validate Finance Advice Contract", ...READ_ONLY_TOOL_ANNOTATIONS },
  }, async ({ advice }) => {
    assertFinanceSafe(advice); const required = ["mode", "status", "reason_codes", "profile_as_of", "data_as_of", "assumptions", "missing_information", "financial_needs", "candidates", "decision_owner", "limitations", "audit_id"]; const errors = required.filter((field) => !(field in advice)); if (advice.decision_owner !== "user") errors.push("decision_owner_must_be_user"); const candidates = Array.isArray(advice.candidates) ? advice.candidates : []; if (advice.status === "ready" && !candidates.length) errors.push("ready_requires_candidates"); if (advice.status !== "ready" && candidates.length) errors.push("blocked_or_insufficient_must_not_include_candidates"); candidates.forEach((candidate) => { if (!isRecord(candidate)) { errors.push("candidate_must_be_object"); return; } if (!candidate.item_id) errors.push("candidate_item_id_required"); if (candidate.verification_status !== "verified") errors.push("candidate_verification_required"); const assertions = Array.isArray(candidate.source_assertions) ? candidate.source_assertions.filter(isRecord) : []; if (!assertions.some((assertion) => assertion.verification_status === "verified" && typeof assertion.source_id === "string" && typeof assertion.checksum === "string")) errors.push("candidate_verified_source_assertion_required"); if (!candidate.data_as_of) errors.push("candidate_data_as_of_required"); if (advice.mode === "recommendation" && advice.status === "ready" && candidate.recommendation_status !== "verified_recommendation_candidate") errors.push("recommendation_candidate_not_verified"); if (advice.mode === "recommendation" && advice.status === "ready" && !isRecord(candidate.promotion_receipt)) errors.push("candidate_promotion_receipt_required"); });
    return financeResult(financeSafety({ status: errors.length ? "blocked" : "ready", validation: { valid: !errors.length, errors: [...new Set(errors)], policy_version: ADVICE_POLICY_VERSION }, reason_codes: errors.length ? ["ADVICE_CONTRACT_INVALID"] : [] }));
  });

  server.registerTool("get_openfin_quality_status", {
    title: "Get OpenFin Quality Status",
    description: "Return manifest, index, and public-recommendation gate status without changing state.",
    inputSchema: {},
    annotations: { title: "Get OpenFin Quality Status", ...READ_ONLY_TOOL_ANNOTATIONS },
  }, async () => {
    const manifest = await loadFinanceManifest(env); const metadata = await loadSearchIndexMetadata(env);
    const live = manifest.openfin_120_live_regression ?? {};
    const releaseStatus = manifest.release_status ?? "unknown";
    const blockingReasons = manifest.blocking_reasons ?? [];
    const livePassed = live.mode === "live" && live.test_count === 120 && live.passed_count === 120 && live.failed_count === 0 && live.skipped_count === 0;
    return financeResult(financeSafety({
      status: releaseStatus === "ready" && livePassed ? "ready" : "blocked",
      reason_codes: releaseStatus === "ready" && livePassed ? [] : ["QUALITY_RELEASE_BLOCKED"],
      data_as_of: manifest.basis_date,
      missing_information: blockingReasons,
      assumptions: ["quality status reflects the loaded manifest and search index"],
      quality_status: { manifest_version: manifest.version, release_status: releaseStatus, basis_date: manifest.basis_date, search_index_item_count: metadata.item_count ?? null, loaded_index_checksum: metadata.export_checksum ?? null, quality_exports: manifest.quality_exports ?? [], openfin_120_live_regression: live, public_recommendation_enabled: ENABLE_PUBLIC_RECOMMENDATION },
      limitations: ["quality status is not a product recommendation", ...blockingReasons],
    }));
  });

  server.registerTool("update_finance_snapshot", {
    title: "Update Personal Finance Snapshot",
    description: "Persistence is fail-closed: owner authentication, explicit confirmation, and an enabled persistence binding are all required, and this public Worker never persists snapshots.",
    inputSchema: { snapshot: z.record(z.string(), z.unknown()), owner_authenticated: z.boolean(), explicit_confirmation: z.boolean(), persistence_enabled: z.boolean() },
    annotations: { title: "Update Personal Finance Snapshot", ...READ_ONLY_TOOL_ANNOTATIONS },
  }, async ({ snapshot, owner_authenticated, explicit_confirmation, persistence_enabled }) => {
    assertFinanceSafe(snapshot); const reasons = [!owner_authenticated ? "OWNER_AUTH_REQUIRED" : null, !explicit_confirmation ? "EXPLICIT_CONFIRMATION_REQUIRED" : null, !persistence_enabled ? "PERSISTENCE_FLAG_REQUIRED" : null, "PERSISTENCE_BACKEND_NOT_CONFIGURED"].filter((value): value is string => Boolean(value));
    return financeResult(financeSafety({ status: "blocked", reason_codes: reasons, assumptions: ["the public Worker does not persist personal financial snapshots"], missing_information: reasons, financial_needs: [], candidates: [], limitations: ["no snapshot was written", "use a separately authenticated owner-controlled persistence service"] }));
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
      outputSchema: STANDARD_OUTPUT_SCHEMA,
      annotations: {
        title: "Search Finance Ontology",
        ...READ_ONLY_TOOL_ANNOTATIONS,
      },
    },
    async ({ query, type, search_type, product_kind, recommendation_status, recommendation_scope, sales_status, application_status, provider, region, freshness_status, limit }) => {
      const items = dedupeProductItems(await loadSearchItems(env));
      const normalizedQuery = normalizeQuery(query);
      const maxResults = limit ?? 10;
      if (isNamedProductQuery(query)) {
        const payload = strictNamedProductPayload(query, items, maxResults, env);
        if (payload) return mcpResult(payload);
      }
      if (isDiscoveryQuery(query)) {
        const payload = discoveryPayload(query, items, maxResults);
        return mcpResult(payload);
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
      const results = items
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
          resolved_canonical_product_id: item.resolved_canonical_product_id ?? item.canonical_product_id,
          external_product_ids: item.external_product_ids ?? [],
          provider_external_ids: item.provider_external_ids ?? [],
          provider_roles: item.provider_roles ?? [],
          application_status: item.application_status,
          is_currently_applicable: item.is_currently_applicable,
          application_open_to: item.application_open_to,
          application_window: item.application_window ?? {},
          jurisdiction: item.jurisdiction,
          freshness_status: item.freshness_status,
          recommendation_model_version: item.recommendation_model_version,
          recommendation_exclusion_reasons: item.recommendation_exclusion_reasons ?? [],
          recommendation_basis_fields: item.recommendation_basis_fields ?? [],
          comparison_basis_fields: item.comparison_basis_fields ?? [],
          verification_status: item.verification_status,
          completeness_ratio: item.completeness_ratio,
          comparison_engine_gate_passed: item.comparison_engine_gate_passed,
          comparison_field_verification_status: item.comparison_field_verification_status,
          comparison_field_verification: item.comparison_field_verification ?? {},
          missing_required_fields: item.missing_required_fields ?? [],
          structured_summary: item.structured_summary ?? {},
          search_facets: item.search_facets ?? {},
          match_reasons: matchReasons(item, normalizedQuery),
          match_tier: supportMatchTier(item, normalizedQuery),
          url: itemUrl(env, item.id),
          score,
          text: item.description ?? "",
        }));

      const payload = {
        query,
        filters,
        parsed_query: supportParsedQuery(query, region),
        result_count: results.length,
        results,
        exact_results: results.filter((item) => item.match_tier === "exact"),
        partial_results: results.filter((item) => item.match_tier === "partial"),
        related_results: results.filter((item) => item.match_tier === "related"),
        support_match_tier_counts: reasonCounts(results.filter((item) => item.match_tier).map((item) => ({ reason: item.match_tier as string }))),
        excluded_summary: supportExcludedSummary(
          items,
          normalizedQuery,
          supportRegion,
          filters,
          allowedTypes,
          new Set(results.map((item) => item.id)),
          maxResults,
        ),
      };

      return mcpResult(payload);
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
      outputSchema: STANDARD_OUTPUT_SCHEMA,
      annotations: { title: "Discover Finance Products", ...READ_ONLY_TOOL_ANNOTATIONS },
    },
    async ({ query, limit }) => {
      const items = dedupeProductItems(await loadSearchItems(env));
      if (isNamedProductQuery(query)) {
        const payload = strictNamedProductPayload(query, items, limit ?? 10, env);
        if (payload) return mcpResult(payload);
      }
      const payload = discoveryPayload(query, items, limit ?? 10);
      return mcpResult(payload);
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
        decision_context: z.record(z.string(), z.unknown()).optional().describe("Transient typed personal-finance snapshot; sensitive account, credential, and identity fields are rejected."),
        limit: z.number().int().min(1).max(20).optional().describe("Maximum number of recommendations. Defaults to 5."),
      },
      outputSchema: STANDARD_OUTPUT_SCHEMA,
      annotations: {
        title: "Recommend Finance Products",
        ...READ_ONLY_TOOL_ANNOTATIONS,
      },
    },
    async ({ domain, profile, constraints, preferences, decision_context, limit }) => {
      assertFinanceSafe(profile, "profile");
      assertFinanceSafe(constraints, "constraints");
      assertFinanceSafe(preferences, "preferences");
      assertFinanceSafe(decision_context, "decision_context");
      const items = dedupeProductItems(await loadSearchItems(env));
      const maxResults = limit ?? 5;
      const domainItems = items.filter((item) => domainMatches(item, domain));
      const readiness = recommendationReadiness(domain, domainItems);
      const context = normalizeFinanceSnapshot(decision_context);
      const contextMetrics = financeMetrics(context);
      const contextNeeds = financeNeeds(context, contextMetrics);
      const contextMissing = ["as_of", "monthly_net_income_krw", "essential_monthly_expenses_krw", "liquid_assets_krw", "investment_assets_krw"].filter((key) => context[key] === null || context[key] === undefined || context[key] === "");
      if (!ENABLE_PUBLIC_RECOMMENDATION) {
        const blockerCounts = {
          domain_recommendation_not_enabled: domainItems.length,
          sales_not_verified: domainItems.filter((item) => item.sales_verification_status !== "verified_active").length,
          verification_evidence_missing: domainItems.filter((item) => !isRecord(item.verification_evidence)).length,
          verified_completeness_incomplete: domainItems.filter((item) => item.verified_completeness_ratio !== 1).length,
        };
        const payload = {
          mode: "decision_support",
          status: "blocked",
          reason_codes: ["PUBLIC_RECOMMENDATION_DISABLED", "NO_VERIFIED_RECOMMENDATION_CANDIDATE"],
          profile_as_of: context.as_of ?? (isRecord(profile) ? profile.as_of ?? null : null),
          data_as_of: null,
          assumptions: ["public recommendation feature flag is disabled", "only verified recommendation candidates could qualify"],
          missing_information: contextMissing,
          financial_needs: contextNeeds,
          domain,
          domain_enabled: false,
          input_summary: { profile_fields: Object.keys(profile ?? {}).sort(), constraint_fields: Object.keys(constraints ?? {}).sort(), preference_fields: Object.keys(preferences ?? {}).sort() },
          recommendation_model_version: "openfin-recommendation-v0.1.0",
          result_count: 0,
          candidates: [],
          blocker_counts: blockerCounts,
          readiness,
          readiness_states: recommendationReadinessStates(domain, readiness),
          next_required_actions: nextRecommendationActions(domain, readiness),
          next_required_action: nextRecommendationAction(domain, readiness),
          excluded_count: domainItems.length,
          excluded_sample: domainItems.slice(0, EXCLUDED_SAMPLE_LIMIT).map((item) => ({ item_id: item.id, reason: "domain_recommendation_not_enabled" })),
          decision_owner: "user",
          limitations: ["use lookup, education, comparison, and scenario tools only until the owner pilot is enabled"],
          audit_id: financeAuditId("blocked-recommendation", domain, context.as_of ?? null),
          warnings: ["No verified public recommendation candidates are available for this domain."],
        };
        return mcpResult(payload);
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
          source_assertions: item.source_assertions ?? [],
          verification_status: item.verification_status ?? "unknown",
          promotion_receipt: item.promotion_receipt ?? null,
          data_as_of: item.last_verified_at ?? item.verified_at ?? null,
          structured_summary: item.structured_summary ?? {},
          url: itemUrl(env, item.id),
        });
      }
      candidates.sort((a, b) => b.score - a.score || a.item_id.localeCompare(b.item_id, "ko-KR"));
      const results = candidates.slice(0, maxResults);
      const payload = {
        mode: "recommendation",
        status: results.length ? "ready" : "blocked",
        reason_codes: results.length ? [] : ["NO_VERIFIED_RECOMMENDATION_CANDIDATE"],
        profile_as_of: context.as_of ?? (isRecord(profile) ? profile.as_of ?? null : null),
        data_as_of: null,
        assumptions: ["only verified public recommendation candidates are eligible"],
        missing_information: contextMissing,
        financial_needs: contextNeeds,
        domain,
        input_summary: { profile_fields: Object.keys(profile ?? {}).sort(), constraint_fields: Object.keys(constraints ?? {}).sort(), preference_fields: Object.keys(preferences ?? {}).sort() },
        recommendation_model_version: "openfin-recommendation-v0.1.0",
        domain_enabled: true,
        result_count: results.length,
        candidates: results,
        blocker_counts: reasonCounts(excluded),
        readiness,
        readiness_states: recommendationReadinessStates(domain, readiness),
        next_required_actions: nextRecommendationActions(domain, readiness),
        next_required_action: nextRecommendationAction(domain, readiness),
        excluded_count: excluded.length,
        excluded_sample: excluded.slice(0, EXCLUDED_SAMPLE_LIMIT),
        decision_owner: "user",
        limitations: ["recommendation output is subject to source freshness and user verification"],
        audit_id: financeAuditId("recommendation", domain, profile ?? {}, results),
        warnings: results.length ? [] : ["No verified public recommendation candidates are available for this domain."],
      };
      return mcpResult(payload);
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
      outputSchema: STANDARD_OUTPUT_SCHEMA,
      annotations: {
        title: "Compare Deposit and Saving Products",
        ...READ_ONLY_TOOL_ANNOTATIONS,
      },
    },
    async ({ domain, deposit_amount_krw, monthly_payment_krw, term_months, join_channels, eligible_conditions, saving_method, tax_rate_percent, limit }) => {
      if ((domain === "deposit" && !ENABLE_DEPOSIT_COMPARISON) || (domain === "saving" && !ENABLE_SAVING_COMPARISON)) {
        const payload = { domain, result_count: 0, candidates: [], excluded_count: 0, excluded_sample: [], warnings: ["Deposit and saving comparison is currently disabled."], comparison_engine_version: COMPARISON_ENGINE_VERSION };
        return mcpResult(payload);
      }
      const items = dedupeProductItems(await loadSearchItems(env));
      const metadata = await loadSearchIndexMetadata(env);
      const channels = (join_channels ?? []).map((channel) => normalizeQuery(channel));
      const conditions = new Set(eligible_conditions ?? []);
      const excluded: Array<{ item_id: string; reason: string }> = [];
      const candidates: Record<string, unknown>[] = [];
      const candidateTargetIds = new Set<string>();
      for (const item of items.filter((candidate) => domainMatches(candidate, domain))) {
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
        candidateTargetIds.add(item.id);
        candidates.push(...usableOptions.map((option) => comparisonCandidate(item, option, conditions, deposit_amount_krw, monthly_payment_krw, tax_rate_percent ?? 15.4)));
      }
      candidates.sort((left, right) => {
        const leftRate = typeof left.achievable_rate_percent === "number" ? left.achievable_rate_percent : 0;
        const rightRate = typeof right.achievable_rate_percent === "number" ? right.achievable_rate_percent : 0;
        return rightRate - leftRate || String(left.item_id).localeCompare(String(right.item_id));
      });
      const sortedExcluded = excluded.sort((left, right) => left.item_id.localeCompare(right.item_id) || left.reason.localeCompare(right.reason));
      const excludedSummary = reasonCounts(sortedExcluded);
      const results = candidates.slice(0, limit ?? 10);
      const targetItems = items.filter((candidate) => domainMatches(candidate, domain));
      const verifiedDates = targetItems.map((candidate) => candidate.sales_verified_at?.slice(0, 10)).filter((value): value is string => Boolean(value)).sort();
      const comparisonBasisDate = verifiedDates[verifiedDates.length - 1] ?? metadata.basis_date;
      const payload = {
        domain,
        candidates: results,
        candidate_count: candidateTargetIds.size,
        result_count: results.length,
        excluded_count: sortedExcluded.length,
        excluded_summary: excludedSummary,
        filter_exclusions: { ...excludedSummary },
        comparison_target_count: targetItems.length,
        excluded_sample: sortedExcluded.slice(0, EXCLUDED_SAMPLE_LIMIT),
        blockers: comparisonBlockers(domain, excludedSummary),
        assumptions: [
          "Achievable rate includes only user-declared preferential conditions.",
          "Missing preferential conditions are not assumed to be satisfied.",
        ],
        comparison_model_version: "openfin-comparison-v0.1.0",
        comparison_engine_version: COMPARISON_ENGINE_VERSION,
        ontology_basis_date: comparisonBasisDate,
        data_as_of: comparisonBasisDate,
        latest_product_collection_date: comparisonBasisDate,
        verification_basis_date: comparisonBasisDate,
        calculation_policy_basis_date: "2026-07-14",
        comparison_basis: { candidate_values_are_from_final_object: true, object_version: COMPARISON_ENGINE_VERSION },
        executed_at: new Date().toISOString(),
        requested_intent: { domain, deposit_amount_krw, monthly_payment_krw, term_months, join_channels, eligible_conditions, saving_method, tax_rate_percent: tax_rate_percent ?? 15.4 },
        executed_mode: "deterministic_comparison",
      };
      return mcpResult(payload);
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
      const requestedId = resolveItemId(id);
      const resolvedCanonicalId = item.resolved_canonical_product_id ?? item.canonical_product_id ?? item.id;
      const redirected = requestedId !== item.id;
      const sources = sourceItems(item, itemsById).map((source) => ({
        id: source.id,
        title: source.title,
        publisher: source.publisher,
        basis_date: source.basis_date,
        url: source.url,
        description: source.description,
      }));

      const payload = {
        requested_id: id,
        id: item.id,
        resolved_canonical_product_id: resolvedCanonicalId,
        redirected,
        legacy_redirect: redirected ? { from: requestedId, to: item.id, resolved_canonical_product_id: resolvedCanonicalId, reason: "merged_by_external_product_id" } : null,
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
        comparison_engine_gate_passed: item.comparison_engine_gate_passed,
        comparison_field_verification_status: item.comparison_field_verification_status,
        comparison_field_verification: item.comparison_field_verification ?? {},
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
      const metadata = await loadSearchIndexMetadata(env);
      const payload = {
        version: manifest.version,
        basis_date: manifest.basis_date,
        item_count: manifest.search_index?.item_count ?? manifest.exports.reduce((total, entry) => total + (entry.item_count ?? 0), 0),
        search_index: manifest.search_index,
        quality_exports: manifest.quality_exports ?? [],
        exports: manifest.exports,
        runtime: await runtimeMetadata(env, manifest, metadata),
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
    // Keep the request promise open until the tool handler has produced its
    // result. Streamable SSE responses can otherwise be closed by the
    // stateless Worker runtime while a shard-backed tool is still hydrating.
    // JSON mode uses the same MCP transport and is accepted by the live client.
    return createMcpHandler(server, { route: "/mcp", enableJsonResponse: true })(request, env, ctx);
  },
} satisfies ExportedHandler<Env>;
