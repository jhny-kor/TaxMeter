# finance-mcp

`finance-mcp` is a Cloudflare Worker Remote MCP adapter for the Finance ontology.

It exposes read-only MCP tools for ChatGPT and other remote MCP clients:

- `search`: search tax, deduction, support, local-government support, card, bank, insurance, filing, concept, deadline, and source nodes.
- `fetch`: fetch one ontology item with criteria, product metadata, source URLs, and neighboring node ids.
- `exports`: list ontology exports loaded by the MCP adapter.

The Worker reads the canonical manifest from:

```text
https://raw.githubusercontent.com/jhny-kor/TaxMeter/main/ontology/exports/finance-ontology-manifest.json
```

The manifest can point to separate ontology JSON files, for example:

```text
ontology/exports/korea-tax-ontology-2026.json
ontology/exports/korea-local-government-supports-ontology-2026.json
ontology/exports/korea-card-products-ontology-2026.json
ontology/exports/korea-bank-products-ontology-2026.json
ontology/exports/korea-insurance-products-ontology-2026.json
```

## Local Development

```sh
cd cloudflare/opentax-mcp
npm install
npm run dev
```

Local MCP endpoint:

```text
http://localhost:8787/mcp
```

Test with MCP Inspector:

```sh
npx @modelcontextprotocol/inspector@latest
```

## Deploy

Create a Cloudflare API token with at least:

- Account: Workers Scripts: Edit
- Account: Account Settings: Read
- User: User Details: Read
- User: Memberships: Read

Store the token locally in `.env`:

```sh
CLOUDFLARE_API_TOKEN=...
CLOUDFLARE_ACCOUNT_ID=...
```

```sh
cd cloudflare/opentax-mcp
npm run deploy
```

The deployed MCP endpoint will be:

```text
https://finance-mcp.<cloudflare-account>.workers.dev/mcp
```

## ChatGPT Connector

Register the deployed `/mcp` URL as a custom MCP connector in ChatGPT.

Recommended first deployment is public and read-only. If write tools are added
later, add OAuth or Cloudflare Access before exposing them.

## Finance Product Imports

Finance products are split from the tax ontology because product values change
frequently. Use the official importer when a FinLife API key is available:

```sh
FINLIFE_API_KEY=... python3 ontology/scripts/import_finance_products.py
python3 ontology/scripts/build_finance_ontology.py
```

The generated product nodes must keep provider, product code, sale status,
collected date, source URLs, and source basis dates so stale or ended products
can be checked later.
