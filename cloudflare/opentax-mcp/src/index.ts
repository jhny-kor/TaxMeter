import { createMcpHandler } from "agents/mcp";
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { z } from "zod";

type OpenTaxItem = {
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
  parents?: string[];
  children?: string[];
  related?: string[];
  terms?: string[];
  deadlines?: string[];
  sources?: string[];
  tags?: string[];
};

type OpenTaxExport = {
  version: string;
  basis_date: string;
  items: OpenTaxItem[];
};

type CachedExport = {
  data: OpenTaxExport;
  loadedAt: number;
};

const CACHE_TTL_MS = 5 * 60 * 1000;
const DEFAULT_OPENTAX_JSON_URL =
  "https://raw.githubusercontent.com/jhny-kor/TaxMeter/main/ontology/exports/korea-tax-ontology-2026.json";
const DEFAULT_OPENTAX_WEB_BASE_URL = "https://jhny-kor.github.io/TaxMeter/opentax/";
const OPENAI_APPS_CHALLENGE_PATH = "/.well-known/openai-apps-challenge";
const READ_ONLY_TOOL_ANNOTATIONS = {
  readOnlyHint: true,
  destructiveHint: false,
  idempotentHint: true,
  openWorldHint: false,
} as const;

let cachedExport: CachedExport | undefined;

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

function itemUrl(env: Env, itemId: string): string {
  const baseUrl = env.OPENTAX_WEB_BASE_URL || DEFAULT_OPENTAX_WEB_BASE_URL;
  return `${baseUrl.replace(/\/?$/, "/")}#${encodeURIComponent(itemId)}`;
}

function itemSearchText(item: OpenTaxItem): string {
  return [
    item.id,
    item.title,
    item.type,
    item.description,
    item.law_reference,
    item.url,
    ...(item.tags ?? []),
    ...(item.sources ?? []),
  ]
    .filter(Boolean)
    .join(" ")
    .toLocaleLowerCase("ko-KR");
}

function scoreItem(item: OpenTaxItem, query: string): number {
  const normalizedTitle = normalizeQuery(item.title);
  const normalizedId = normalizeQuery(item.id);
  const text = itemSearchText(item);
  const tokens = queryTokens(query);

  if (normalizedId === query || normalizedTitle === query) {
    return 100;
  }
  if (normalizedId.includes(query)) {
    return 80;
  }
  if (normalizedTitle.includes(query)) {
    return 70;
  }
  if (text.includes(query)) {
    return 40;
  }
  if (tokens.length > 1) {
    const matchedTokens = tokens.filter((token) => text.includes(token));
    if (matchedTokens.length === tokens.length) {
      return 30 + matchedTokens.length;
    }
    if (matchedTokens.length > 0) {
      return 10 + matchedTokens.length;
    }
  }
  return 0;
}

async function loadOpenTax(env: Env): Promise<OpenTaxExport> {
  const now = Date.now();
  if (cachedExport && now - cachedExport.loadedAt < CACHE_TTL_MS) {
    return cachedExport.data;
  }

  const exportUrl = env.OPENTAX_JSON_URL || DEFAULT_OPENTAX_JSON_URL;
  const response = await fetch(exportUrl, {
    headers: {
      accept: "application/json",
      "user-agent": "opentax-mcp-cloudflare-worker",
    },
  });

  if (!response.ok) {
    throw new Error(`OpenTax export fetch failed: ${response.status} ${response.statusText}`);
  }

  const data = (await response.json()) as OpenTaxExport;
  cachedExport = { data, loadedAt: now };
  return data;
}

function indexItems(data: OpenTaxExport): Map<string, OpenTaxItem> {
  return new Map(data.items.map((item) => [item.id, item]));
}

function resolveItemId(rawId: string): string {
  const trimmed = rawId.trim();
  if (trimmed.startsWith("opentax://")) {
    return trimmed.slice("opentax://".length);
  }

  try {
    const url = new URL(trimmed);
    const hashId = decodeURIComponent(url.hash.replace(/^#/, ""));
    if (hashId) {
      return hashId;
    }
  } catch {
    // Not a URL; use the raw value as an OpenTax id.
  }

  return trimmed;
}

function sourceItems(item: OpenTaxItem, itemsById: Map<string, OpenTaxItem>): OpenTaxItem[] {
  return (item.sources ?? [])
    .map((sourceId) => itemsById.get(sourceId))
    .filter((source): source is OpenTaxItem => Boolean(source));
}

function createServer(env: Env): McpServer {
  const server = new McpServer({
    name: "opentax-mcp",
    version: "0.1.0",
  });

  server.registerTool(
    "search",
    {
      title: "Search OpenTax",
      description:
        "Use this when the user needs to find Korean tax, deduction, policy support, filing deadline, term, or official-source nodes in OpenTax. Do not use for personalized tax, legal, or financial advice.",
      inputSchema: {
        query: z.string().min(1).describe("Search query, for example '보험료 공제 한도' or 'support.isa'."),
        type: z
          .string()
          .optional()
          .describe("Optional OpenTax item type filter, for example 'tax' or 'support-program'."),
        limit: z.number().int().min(1).max(50).optional().describe("Maximum number of results. Defaults to 10."),
      },
      annotations: {
        title: "Search OpenTax",
        ...READ_ONLY_TOOL_ANNOTATIONS,
      },
    },
    async ({ query, type, limit }) => {
      const data = await loadOpenTax(env);
      const normalizedQuery = normalizeQuery(query);
      const maxResults = limit ?? 10;

      const results = data.items
        .filter((item) => !type || item.type === type)
        .map((item) => ({ item, score: scoreItem(item, normalizedQuery) }))
        .filter((result) => result.score > 0)
        .sort((a, b) => b.score - a.score || a.item.title.localeCompare(b.item.title, "ko-KR"))
        .slice(0, maxResults)
        .map(({ item, score }) => ({
          id: item.id,
          title: item.title,
          type: item.type,
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
      title: "Fetch OpenTax Item",
      description:
        "Use this when the user needs one exact OpenTax node with criteria, official sources, and graph neighbors after an id or URL is known. Do not use for personalized tax, legal, or financial advice.",
      inputSchema: {
        id: z.string().min(1).describe("OpenTax item id, opentax:// id, or OpenTax web URL with hash id."),
      },
      annotations: {
        title: "Fetch OpenTax Item",
        ...READ_ONLY_TOOL_ANNOTATIONS,
      },
    },
    async ({ id }) => {
      const data = await loadOpenTax(env);
      const itemsById = indexItems(data);
      const itemId = resolveItemId(id);
      const item = itemsById.get(itemId);

      if (!item) {
        throw new Error(`OpenTax item not found: ${id}`);
      }

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
        criteria: item.criteria ?? [],
        neighbors: {
          parents: item.parents ?? [],
          children: item.children ?? [],
          related: item.related ?? [],
          terms: item.terms ?? [],
          deadlines: item.deadlines ?? [],
          sources: item.sources ?? [],
        },
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

  return server;
}

function healthResponse(env: Env): Response {
  return Response.json({
    name: "opentax-mcp",
    status: "ok",
    mcp_endpoint: "/mcp",
    opentax_json_url: env.OPENTAX_JSON_URL || DEFAULT_OPENTAX_JSON_URL,
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
