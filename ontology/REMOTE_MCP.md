# Finance Remote MCP on Cloudflare

This guide deploys the read-only Finance remote MCP adapter to Cloudflare
Workers under the service name `finance-mcp`.

## What It Provides

The Worker is in `cloudflare/opentax-mcp` and exposes:

- `search`: searches tax, support, card, bank, insurance, deadline, term, and source nodes.
- `fetch`: returns one ontology item with criteria, product metadata, source URLs, and graph neighbors.
- `exports`: lists the ontology JSON files loaded through the manifest.

It intentionally does not expose write tools. Keep writes in the local stdio MCP
server until authentication and authorization are added.

## Data Source

By default the Worker reads the canonical manifest from GitHub:

```text
https://raw.githubusercontent.com/jhny-kor/TaxMeter/main/ontology/exports/finance-ontology-manifest.json
```

The manifest points to split exports such as:

```text
ontology/exports/korea-tax-ontology-2026.json
ontology/exports/korea-local-government-supports-ontology-2026.json
ontology/exports/korea-card-products-ontology-2026.json
ontology/exports/korea-bank-products-ontology-2026.json
ontology/exports/korea-insurance-products-ontology-2026.json
```

Override `FINANCE_MANIFEST_URL` in `cloudflare/opentax-mcp/wrangler.toml` if you
later host the JSON from GitHub Pages, R2, or another static endpoint.

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

Create a Cloudflare API token with deploy permissions before running Wrangler.
For this Worker, use a user API token with at least:

- Account: Workers Scripts: Edit
- Account: Account Settings: Read
- User: User Details: Read
- User: Memberships: Read

Then keep it in local `.env`, not in Git:

```sh
CLOUDFLARE_API_TOKEN=...
CLOUDFLARE_ACCOUNT_ID=...
```

```sh
cd cloudflare/opentax-mcp
npm run deploy
```

The deployed endpoint will look like:

```text
https://finance-mcp.<cloudflare-account>.workers.dev/mcp
```

## ChatGPT

In ChatGPT, add a custom MCP connector with the deployed `/mcp` URL.

Use the connector by asking questions such as:

```text
OpenTax에서 ISA 비과세 한도와 출처를 찾아주세요.
finance에서 체크카드 전월실적과 월 혜택 한도 항목을 찾아주세요.
finance에서 은행 적금 우대금리 기준을 찾아주세요.
```

## Finance Product Imports

금융상품 실데이터는 변동성이 크므로 세금 온톨로지와 별도 export로 둡니다.
금감원 금융상품한눈에 API 키가 있으면 다음 순서로 갱신합니다.

```sh
FINLIFE_API_KEY=... python3 ontology/scripts/import_finance_products.py
python3 ontology/scripts/build_finance_ontology.py
```

카드와 보험은 여신금융협회, 보험다모아, 생명보험협회, 손해보험협회 공시
원천을 별도 crawler로 붙이면 같은 generated JSON 형식으로 합쳐집니다.
