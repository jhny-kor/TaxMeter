# OpenTax finance ontology refresh gate review

## recommendation

REJECT

## originalIntent

Refresh the existing finance ontology from current source evidence, update card information, add loan categories/details, organize finance categories, and make `docs/opentax` show the latest finance information through a real static web surface.

## desiredOutcome

- Finance manifest and product exports reflect current source evidence consistently.
- Card, bank/loan, and insurance product counts and details are exposed in the generated web page.
- Finance tab/search/detail behavior is backed by real DOM/data, not screenshots.
- Implementation is acceptable for the scope and does not introduce unresolved slop or misleading freshness claims.

## userOutcomeReview

The web surface is not a fake screenshot. `docs/opentax/index.html` serves `./app.js`; `docs/opentax/app.js` contains a parseable `ONTOLOGY_DATA` payload, finance tab filtering, search text indexing, detail rendering, product meta, benefits, and options. Local HTTP checks against the already-running `http://127.0.0.1:8087/` confirmed the page serves the updated index, app bundle, and finance manifest.

However, the shipped result does not satisfy "latest finance info" because the public finance basis date was advanced to `2026-07-02` while every bank and insurance product row still reports `collected_at: 2026-05-05`. This makes the visible finance basis date and source freshness metadata misleading for 1,380 of 2,386 finance products.

## blockers

1. Misleading freshness for bank and insurance products.
   - `ontology/scripts/build_finance_ontology.py:22` sets `CURRENT_REVIEW_DATE = "2026-07-02"`.
   - `ontology/scripts/build_finance_ontology.py:108`, `ontology/scripts/build_finance_ontology.py:116`, `ontology/scripts/build_finance_ontology.py:124`, and `ontology/scripts/build_finance_ontology.py:132` update finance source nodes to `2026-07-02 확인`.
   - `ontology/exports/korea-bank-products-ontology-2026.json:1349` shows a bank product with `"collected_at": "2026-05-05"`.
   - `ontology/exports/korea-insurance-products-ontology-2026.json:595` shows an insurance product with `"collected_at": "2026-05-05"`.
   - Independent count check found `1037/1037` bank products and `343/343` insurance products were not collected on `2026-07-02`, while their source basis dates include `2026-07-02 확인`.

2. Required final-gate artifacts are missing.
   - No code review report artifact was provided or found.
   - No manual QA matrix artifact was provided or found. Only `output/playwright/opentax-finance-check.json` and screenshots exist.
   - No notepad path was provided, and `.omx/notepad.md` was not found.
   - Because the code review report is absent, it cannot show the required programming and remove-ai-slops perspective coverage.

3. Direct anti-slop/programming pass finds unresolved scope debt.
   - `ontology/scripts/build_finance_ontology.py` is 708 pure LOC.
   - `ontology/scripts/build_web.py` is 2107 pure LOC.
   - Both exceed the 250 pure LOC ceiling from the consulted programming/remove-ai-slops criteria, with no visible `SIZE_OK` justification.
   - `docs/opentax/app.js` is 25,755,088 bytes and 674,539 lines because it embeds pretty-printed product data. It is generated, so this is not the same source-file smell, but it is still a performance/reviewability risk for a static public page.

4. QA evidence is too narrow for the freshness claim.
   - `output/playwright/opentax-finance-check.json` verifies a card detail path (`finance.card.credit-card.광주은행.1st카드-340294`) and a `신용카드` filtered result count of 763 rows.
   - It does not check bank/insurance product freshness, loan detail rows, or consistency between `finance_basis_date` and product-level `collected_at`.

## goodAspects

- `python3 ontology/scripts/validate_finance_ontology.py` passed with 5 exports.
- `python3 ontology/scripts/validate_ontology.py` passed with 378 notes.
- `docs/opentax/app.js` contains real data-backed behavior:
  - `ontology/scripts/build_web.py:24` lists finance data files.
  - `ontology/scripts/build_web.py:81` loads finance items.
  - `ontology/scripts/build_web.py:101` enriches summary counts.
  - `ontology/scripts/build_web.py:1783` renders list results from filtered data.
  - `ontology/scripts/build_web.py:2111` renders product metadata.
  - `ontology/scripts/build_web.py:2132` renders product benefits.
  - `ontology/scripts/build_web.py:2173` renders product options.
- Parsed `docs/opentax/app.js` summary:
  - total items: 2804
  - finance products: 2386
  - card products: 1006
  - bank products: 1037
  - insurance products: 343
  - finance basis date: 2026-07-02
- Finance category additions are represented in source:
  - `ontology/scripts/build_finance_ontology.py:353` defines the bank/loan domain.
  - `ontology/scripts/build_finance_ontology.py:424` adds personal business loan category.
  - `ontology/scripts/build_finance_ontology.py:433` adds policy loan category.
  - `ontology/scripts/build_finance_ontology.py:467`, `ontology/scripts/build_finance_ontology.py:475`, and `ontology/scripts/build_finance_ontology.py:482` add credit score, loan purpose, and repayment method terms.

## checkedArtifactPaths

- `/Users/plo/Documents/TaxMeter/ontology/scripts/build_finance_ontology.py`
- `/Users/plo/Documents/TaxMeter/ontology/scripts/build_web.py`
- `/Users/plo/Documents/TaxMeter/ontology/custom/finance/card-products.generated.json`
- `/Users/plo/Documents/TaxMeter/ontology/custom/finance/bank-products.generated.json`
- `/Users/plo/Documents/TaxMeter/ontology/custom/finance/insurance-products.generated.json`
- `/Users/plo/Documents/TaxMeter/ontology/exports/finance-ontology-manifest.json`
- `/Users/plo/Documents/TaxMeter/ontology/exports/korea-card-products-ontology-2026.json`
- `/Users/plo/Documents/TaxMeter/ontology/exports/korea-bank-products-ontology-2026.json`
- `/Users/plo/Documents/TaxMeter/ontology/exports/korea-insurance-products-ontology-2026.json`
- `/Users/plo/Documents/TaxMeter/docs/opentax/index.html`
- `/Users/plo/Documents/TaxMeter/docs/opentax/app.js`
- `/Users/plo/Documents/TaxMeter/output/playwright/opentax-finance-check.json`
- `/Users/plo/Documents/TaxMeter/output/playwright/opentax-finance-desktop.png`
- `/Users/plo/Documents/TaxMeter/output/playwright/opentax-finance-mobile.png`

## exactEvidenceGaps

- No evidence that bank products were refreshed from current source data. All 1037 bank products still have `collected_at = 2026-05-05`.
- No evidence that insurance products were refreshed from current source data. All 343 insurance products still have `collected_at = 2026-05-05`.
- No current-source audit trail showing which official pages/APIs were recrawled and when.
- No code review report artifact, so required remove-ai-slops/programming coverage cannot be confirmed.
- No manual QA matrix artifact covering finance tab all-products, card search, loan search, bank detail, insurance detail, mobile behavior, and stale-date assertions.
- No notepad path was provided.

## verificationPerformed

- Loaded and applied `omo:remove-ai-slops` and `omo:programming` criteria.
- Searched memory registry for TaxMeter/OpenTax finance context; no relevant hits.
- Inspected git status, changed source files, generated exports, and web output.
- Parsed `docs/opentax/app.js` to confirm `ONTOLOGY_DATA` is real JSON-backed data.
- Counted finance tab rows by emulating the app filter:
  - finance tab rows: 2415
  - product rows: 2386
  - non-product finance ontology/category/source/term rows: 29
- Verified local HTTP server output:
  - `/` serves updated index with `./app.js`, `금융상품`, `2386`, and `금융 기준일 2026-07-02`.
  - `/app.js` serves the generated data-backed JS bundle.
  - `/finance-ontology-manifest.json` returns basis date `2026-07-02` and product sum `2386`.
- Ran validators:
  - `python3 ontology/scripts/validate_finance_ontology.py`: PASS
  - `python3 ontology/scripts/validate_ontology.py`: PASS
- Consulted official source URLs referenced by the diff:
  - `https://www.fsc.go.kr/no010101/83693` supports the personal business loan comparison category/source reference.
  - `https://www.data.go.kr/data/15106208/openapi.do?recommendDataYn=Y` shows the policy loan API metadata, including `수정일 2026-06-09`.

## conclusion

The implementation has real DOM/data-backed finance behavior and valid JSON outputs, but it should not pass the gate. The "latest finance info" claim is materially unsupported for bank and insurance products, and required review/QA artifacts are missing.
