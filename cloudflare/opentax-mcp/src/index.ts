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
  status?: string;
  status_reason?: string;
  recommendation_status?: string;
  application_status?: string;
  is_currently_applicable?: boolean;
  application_open_from?: string;
  application_open_to?: string;
  export_id?: string;
  search_text?: string;
  search_aliases?: string[];
  source_urls?: string[];
  source_basis_dates?: string[];
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

const CACHE_TTL_MS = 5 * 60 * 1000;
const DEFAULT_FINANCE_MANIFEST_URL =
  "https://jhny-kor.github.io/TaxMeter/opentax/finance-ontology-manifest.json";
const DEFAULT_FINANCE_WEB_BASE_URL = "https://jhny-kor.github.io/TaxMeter/opentax/";
const OPENAI_APPS_CHALLENGE_PATH = "/.well-known/openai-apps-challenge";
const RATE_QUERY_RE = /(금리|최고금리|중도해지|정기예금|적금|대출|개월)/i;
const PROTECTION_QUERY_RE = /(예금자보호|보호대상|보호상품|kdic|보호)/i;
const INACTIVE_QUERY_RE = /(종료|판매중단|중단|만료|마감|지난|unknown|closed|ended|reference|보류|불확실)/i;
const RECOMMENDATION_QUERY_RE = /(추천|골라|맞는\s*상품|recommend)/i;
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
    item.application_status,
    item.application_open_from,
    item.application_open_to,
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
  return (value ?? []).slice(0, 4).map((entry) => JSON.stringify(entry)).join(" ");
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

function scoreItem(item: FinanceItem, query: string): number {
  const normalizedTitle = normalizeQuery(item.title);
  const normalizedId = normalizeQuery(item.id);
  const searchType = normalizeQuery(item.search_type ?? item.product_kind ?? "");
  const status = normalizeQuery(item.status ?? item.product_status ?? "");
  const recommendationStatus = normalizeQuery(item.recommendation_status ?? "");
  const applicationStatus = normalizeQuery(item.application_status ?? "");
  const text = itemSearchText(item);
  const aliases = (item.search_aliases ?? []).map((alias) => normalizeQuery(alias));
  const tokens = queryTokens(query);
  const titleTokens = queryTokens(normalizedTitle);
  const rateIntent = RATE_QUERY_RE.test(query);

  if (searchType === "deposit-protection" && rateIntent && !PROTECTION_QUERY_RE.test(query)) {
    return 0;
  }
  if (RECOMMENDATION_QUERY_RE.test(query)) {
    const intentTokens = tokens.filter((token) => !RECOMMENDATION_QUERY_RE.test(token));
    if (
      recommendationStatus !== "recommendation_candidate" ||
      !matchesRecommendationDomain(item, query, searchType) ||
      !intentTokens.length ||
      !intentTokens.every((token) => text.includes(token))
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

  let score = 0;
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

function sourceItems(item: FinanceItem, itemsById: Map<string, FinanceItem>): FinanceItem[] {
  return (item.sources ?? [])
    .map((sourceId) => itemsById.get(sourceId))
    .filter((source): source is FinanceItem => Boolean(source));
}

async function fetchItemGraph(env: Env, rawId: string): Promise<{ item: FinanceItem; itemsById: Map<string, FinanceItem> }> {
  const itemId = resolveItemId(rawId);
  const manifestUrl = financeManifestUrl(env);
  const manifest = await loadFinanceManifest(env);
  const searchIndex = await loadSearchIndex(env);
  const indexedItem = searchIndex.items.find((item) => item.id === itemId);
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
        "Use this when the user needs to find Korean tax, deduction, policy support, local-government support, card, bank, insurance, filing deadline, term, or official-source nodes. Recommendation wording returns only recommendation_candidate nodes. Do not use for personalized tax, legal, accounting, or financial advice.",
      inputSchema: {
        query: z.string().min(1).describe("Search query, for example '보험료 공제 한도', '청년 월세', '체크카드 전월실적', or 'bank-products'."),
        type: z
          .string()
          .optional()
          .describe("Optional ontology item type filter, for example 'tax', 'support-program', 'card-product', 'bank-product', or 'insurance-product'. 'tax' also matches tax-credit, deduction, and other tax decision types."),
        limit: z.number().int().min(1).max(50).optional().describe("Maximum number of results. Defaults to 10."),
      },
      annotations: {
        title: "Search Finance Ontology",
        ...READ_ONLY_TOOL_ANNOTATIONS,
      },
    },
    async ({ query, type, limit }) => {
      const data = await loadSearchIndex(env);
      const normalizedQuery = normalizeQuery(query);
      const maxResults = limit ?? 10;

      const allowedTypes = type ? SEARCH_TYPE_GROUPS[type] ?? new Set([type]) : null;
      const results = data.items
        .filter((item) => !allowedTypes || allowedTypes.has(item.type))
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
          status: item.status,
          recommendation_status: item.recommendation_status,
          application_status: item.application_status,
          is_currently_applicable: item.is_currently_applicable,
          application_open_to: item.application_open_to,
          url: itemUrl(env, item.id),
          score,
          text: item.description ?? "",
        }));

      const payload = {
        query,
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
        status: item.status,
        status_reason: item.status_reason,
        recommendation_status: item.recommendation_status,
        application_status: item.application_status,
        is_currently_applicable: item.is_currently_applicable,
        application_open_from: item.application_open_from,
        application_open_to: item.application_open_to,
        criteria: item.criteria ?? [],
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
