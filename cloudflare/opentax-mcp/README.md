# opentax-mcp

`opentax-mcp` is a Cloudflare Worker Remote MCP adapter for OpenTax.

It exposes read-only MCP tools for ChatGPT and other remote MCP clients:

- `search`: search OpenTax tax, deduction, support, filing, concept, deadline, and source nodes.
- `fetch`: fetch one OpenTax item with criteria, source URLs, and neighboring node ids.

The Worker reads the canonical OpenTax JSON export from:

```text
https://raw.githubusercontent.com/jhny-kor/TaxMeter/main/ontology/exports/korea-tax-ontology-2026.json
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
npx wrangler login
npm run deploy
```

The deployed MCP endpoint will be:

```text
https://opentax-mcp.<cloudflare-account>.workers.dev/mcp
```

## ChatGPT Connector

Register the deployed `/mcp` URL as a custom MCP connector in ChatGPT.

Recommended first deployment is public and read-only. If write tools are added
later, add OAuth or Cloudflare Access before exposing them.

## App Directory Preparation

Public submission assets live in the GitHub Pages OpenTax site:

- App submission pack: `docs/opentax/APP_DIRECTORY_SUBMISSION.md`
- Listing metadata: `docs/opentax/app-directory-metadata.json`
- Privacy policy: `https://jhny-kor.github.io/TaxMeter/opentax/privacy.html`
- Terms: `https://jhny-kor.github.io/TaxMeter/opentax/terms.html`
- Support: `https://jhny-kor.github.io/TaxMeter/opentax/support.html`

Before submitting to the ChatGPT App Directory, run the golden prompt set in
ChatGPT Developer Mode on web and mobile.
