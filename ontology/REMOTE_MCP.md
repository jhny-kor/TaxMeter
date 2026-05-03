# OpenTax Remote MCP on Cloudflare

This guide deploys the read-only OpenTax remote MCP adapter to Cloudflare
Workers under the service name `opentax-mcp`.

## What It Provides

The Worker is in `cloudflare/opentax-mcp` and exposes:

- `search`: searches OpenTax items.
- `fetch`: returns one OpenTax item with criteria, source URLs, and graph neighbors.

It intentionally does not expose write tools. Keep writes in the local stdio MCP
server until authentication and authorization are added.

## Data Source

By default the Worker reads the canonical JSON export from GitHub:

```text
https://raw.githubusercontent.com/jhny-kor/TaxMeter/main/ontology/exports/korea-tax-ontology-2026.json
```

Override it in `cloudflare/opentax-mcp/wrangler.toml` if you later host the JSON
from GitHub Pages, R2, or another static endpoint.

## Local Test

```sh
cd cloudflare/opentax-mcp
npm install
npm run dev
```

MCP endpoint:

```text
http://localhost:8787/mcp
```

Health endpoint:

```text
http://localhost:8787/health
```

Use MCP Inspector to test:

```sh
npx @modelcontextprotocol/inspector@latest
```

## Deploy to Cloudflare

```sh
cd cloudflare/opentax-mcp
npx wrangler login
npm run deploy
```

The deployed endpoint will look like:

```text
https://opentax-mcp.<cloudflare-account>.workers.dev/mcp
```

## ChatGPT

In ChatGPT, add a custom MCP connector with the deployed `/mcp` URL.

Use the connector by asking questions such as:

```text
OpenTax에서 ISA 비과세 한도와 출처를 찾아주세요.
OpenTax에서 보험료 공제 기준을 fetch해서 설명해주세요.
```

## Official References

- Cloudflare remote MCP server guide:
  https://developers.cloudflare.com/agents/guides/remote-mcp-server/
- Cloudflare `createMcpHandler` API:
  https://developers.cloudflare.com/agents/api-reference/mcp-handler-api/
- OpenAI MCP documentation:
  https://platform.openai.com/docs/mcp/
