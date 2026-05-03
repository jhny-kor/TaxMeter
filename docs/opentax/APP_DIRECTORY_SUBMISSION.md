# OpenTax ChatGPT App Directory Submission Pack

Status: draft  
Last updated: 2026-05-03

## App Identity

- Name: OpenTax
- Public MCP URL: `https://opentax-mcp.y2kthr.workers.dev/mcp`
- Health URL: `https://opentax-mcp.y2kthr.workers.dev/health`
- Homepage: `https://jhny-kor.github.io/TaxMeter/opentax/`
- Privacy policy: `https://jhny-kor.github.io/TaxMeter/opentax/privacy.html`
- Terms: `https://jhny-kor.github.io/TaxMeter/opentax/terms.html`
- Support: `https://jhny-kor.github.io/TaxMeter/opentax/support.html`
- Repository: `https://github.com/jhny-kor/TaxMeter`

## Short Description

Search Korean tax, deduction, policy support, filing deadline, and official-source nodes from the OpenTax ontology.

## Long Description

OpenTax connects Korean tax items, deductions, credits, policy support
programs, filing deadlines, terms, and official source references into a
read-only ontology. Use it to find criteria, thresholds, legal references,
deadlines, and source URLs with traceable node IDs.

OpenTax is not a personalized tax, legal, accounting, or financial adviser.
Users should verify official sources before filing, applying, paying, or making
financial decisions.

## Tools

### `search`

- Purpose: Find OpenTax items by ID, title, description, type, tag, source, or law reference.
- Inputs: `query`, optional `type`, optional `limit`.
- Output: matching item IDs, titles, types, web URLs, scores, and short text.
- Hints: `readOnlyHint: true`, `destructiveHint: false`, `openWorldHint: false`.

### `fetch`

- Purpose: Fetch one exact OpenTax node with criteria, official sources, and graph neighbors.
- Inputs: `id` as OpenTax ID, `opentax://` ID, or OpenTax web URL hash.
- Output: node metadata, criteria, related IDs, deadlines, source IDs, and source URLs.
- Hints: `readOnlyHint: true`, `destructiveHint: false`, `openWorldHint: false`.

## Data Handling Summary

- Authentication required: no
- Accounts stored by OpenTax: no
- Cookies used by OpenTax: no
- User inputs processed: search query, node ID, or OpenTax URL passed through ChatGPT tool calls
- User-related data returned: none intentionally
- Public data returned: OpenTax ontology records and official source URLs
- Infrastructure: GitHub Pages, GitHub raw content, Cloudflare Workers

## Golden Prompt Set

| Prompt | Expected Tool Use | Expected Result |
| --- | --- | --- |
| OpenTax에서 보험료 공제 한도를 찾아서 출처와 함께 설명해주세요. | `search`, then `fetch` | Insurance premium deduction criteria and official source URLs. |
| OpenTax에서 ISA 비과세 한도와 근거를 찾아주세요. | `search`, then `fetch` | ISA criteria and official source URLs. |
| OpenTax에서 근로장려금 신청 기준을 조회하고 공식 출처를 보여주세요. | `search`, then `fetch` | Earned income tax credit criteria and official source URLs. |
| 오늘 서울 날씨 알려줘. | none | OpenTax should not be called for unrelated weather queries. |

## Review Checklist

- [x] MCP endpoint is public over HTTPS.
- [x] `/health` endpoint returns `status: ok`.
- [x] Tools are read-only.
- [x] Tools include read-only, destructive, and open-world annotations.
- [x] Privacy policy URL exists.
- [x] Terms URL exists.
- [x] Support URL exists.
- [x] No API tokens, request IDs, auth secrets, or user identifiers are returned in tool responses.
- [ ] Test all golden prompts in ChatGPT Developer Mode on web.
- [ ] Test all golden prompts in ChatGPT mobile.
- [ ] Complete OpenAI account verification.
- [ ] Submit through the OpenAI Platform app submission page.

## Official Submission References

- App submission flow: `https://developers.openai.com/apps-sdk/deploy/submission`
- App submission guidelines: `https://developers.openai.com/apps-sdk/app-submission-guidelines`
- Metadata optimization: `https://developers.openai.com/apps-sdk/guides/optimize-metadata`
- Security and privacy: `https://developers.openai.com/apps-sdk/guides/security-privacy`
- Help Center submission overview: `https://help.openai.com/en/articles/20001040-submitting-apps-to-the-chatgpt-app-directory`
