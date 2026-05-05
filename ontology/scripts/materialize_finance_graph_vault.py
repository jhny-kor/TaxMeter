#!/usr/bin/env python3
"""Materialize JSON-only finance ontology exports as Obsidian graph notes.

The canonical finance data remains the JSON exports. This script creates
graph-only Markdown files so Obsidian can render those JSON items as nodes.
Generated notes intentionally use ``materialized_id`` instead of ``id`` so the
main OpenTax vault validator ignores them.
"""

from __future__ import annotations

import hashlib
import json
import re
import shutil
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
VAULT = ROOT / "vault"
EXPORTS = ROOT / "exports"
OUTPUT = VAULT / "95_FinanceGraph"

EXPORT_CONFIGS = (
    {
        "domain": "local-government-supports",
        "path": EXPORTS / "korea-local-government-supports-ontology-2026.json",
        "folder": "LocalGovernmentSupports",
        "include_reference_items": False,
        "bridge": "00_Index/OpenFin",
    },
    {
        "domain": "card-products",
        "path": EXPORTS / "korea-card-products-ontology-2026.json",
        "folder": "CardProducts",
        "include_reference_items": True,
        "bridge": "00_Index/카드 상품 온톨로지",
    },
    {
        "domain": "bank-products",
        "path": EXPORTS / "korea-bank-products-ontology-2026.json",
        "folder": "BankProducts",
        "include_reference_items": True,
        "bridge": "00_Index/은행 상품 온톨로지",
    },
    {
        "domain": "insurance-products",
        "path": EXPORTS / "korea-insurance-products-ontology-2026.json",
        "folder": "InsuranceProducts",
        "include_reference_items": True,
        "bridge": "00_Index/보험 상품 온톨로지",
    },
)

REFERENCE_KEYS = ("parents", "children", "related", "terms", "deadlines", "sources")
ROOT_EXPORT_IDS = {
    "finance.card-products-ontology",
    "finance.bank-products-ontology",
    "finance.insurance-products-ontology",
}


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def read_frontmatter(path: Path) -> dict[str, Any] | None:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n") or "\n---\n" not in text:
        return None
    frontmatter = text.split("\n---\n", 1)[0][4:]
    result: dict[str, Any] = {}
    for raw_line in frontmatter.splitlines():
        if ": " not in raw_line:
            continue
        key, value = raw_line.split(": ", 1)
        try:
            result[key] = json.loads(value)
        except json.JSONDecodeError:
            result[key] = value
    return result


def vault_link(path: Path) -> str:
    return str(path.relative_to(VAULT).with_suffix(""))


def slugify(value: str, fallback: str) -> str:
    slug = re.sub(r"[\\/:*?\"<>|#^[\\]]+", " ", value).strip()
    slug = re.sub(r"\s+", " ", slug)
    if not slug:
        slug = fallback
    if len(slug) > 72:
        slug = slug[:72].rstrip()
    return slug


def path_for_item(domain_folder: str, item: dict[str, Any]) -> Path:
    item_id = item["id"]
    title = str(item.get("title") or item_id)
    digest = hashlib.sha1(item_id.encode("utf-8")).hexdigest()[:10]
    filename = f"{slugify(title, digest)} {digest}.md"
    item_type = str(item.get("type") or "unknown")
    type_folder = slugify(item_type, "unknown")
    return OUTPUT / domain_folder / type_folder / filename


def collect_existing_id_links() -> tuple[dict[str, str], dict[str, str]]:
    links: dict[str, str] = {}
    titles: dict[str, str] = {}
    for path in VAULT.rglob("*.md"):
        if OUTPUT in path.parents:
            continue
        frontmatter = read_frontmatter(path)
        if not frontmatter or not frontmatter.get("id"):
            continue
        item_id = str(frontmatter["id"])
        links[item_id] = vault_link(path)
        titles[item_id] = str(frontmatter.get("title") or path.stem)
    return links, titles


def all_export_items() -> list[tuple[dict[str, str], dict[str, Any]]]:
    records: list[tuple[dict[str, str], dict[str, Any]]] = []
    for config in EXPORT_CONFIGS:
        payload = load_json(config["path"])
        items = list(payload.get("items") or [])
        if config["include_reference_items"]:
            items = list(payload.get("reference_items") or []) + items
        for item in items:
            if isinstance(item, dict) and item.get("id"):
                records.append((config, item))
    return records


def json_value(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False)


def link_for(item_id: str, id_links: dict[str, str], id_titles: dict[str, str]) -> str:
    target = id_links.get(item_id)
    title = id_titles.get(item_id) or item_id
    if not target:
        return f"`{item_id}`"
    return f"[[{target}|{title}]]"


def relation_ids(item: dict[str, Any]) -> dict[str, list[str]]:
    relations: dict[str, list[str]] = {}
    for key in REFERENCE_KEYS:
        values = item.get(key) or []
        if isinstance(values, list):
            relations[key] = [str(value) for value in values if value]
    criteria_sources: list[str] = []
    for criterion in item.get("criteria") or []:
        if not isinstance(criterion, dict):
            continue
        for key in ("source", "basis_source"):
            value = criterion.get(key)
            if value:
                criteria_sources.append(str(value))
    if criteria_sources:
        existing = relations.setdefault("sources", [])
        for value in criteria_sources:
            if value not in existing:
                existing.append(value)
    return relations


def frontmatter_for(config: dict[str, str], item: dict[str, Any], source_file: str) -> list[str]:
    tags = ["graph-materialized", str(config["domain"])]
    for tag in item.get("tags") or []:
        if isinstance(tag, str) and tag not in tags:
            tags.append(tag)
    return [
        "---",
        f"materialized_id: {json_value(item['id'])}",
        f"title: {json_value(item.get('title') or item['id'])}",
        f"type: {json_value(item.get('type') or 'unknown')}",
        f"domain: {json_value(config['domain'])}",
        f"basis_year: {json_value(item.get('basis_year'))}",
        f"reviewed_at: {json_value(item.get('reviewed_at'))}",
        f"source_export: {json_value(source_file)}",
        f"source_urls: {json_value(item.get('source_urls') or [])}",
        f"source_basis_dates: {json_value(item.get('source_basis_dates') or [])}",
        f"tags: {json_value(tags)}",
        "---",
        "",
    ]


def metadata_lines(item: dict[str, Any]) -> list[str]:
    lines = [
        f"- Materialized ID: `{item['id']}`",
        f"- Type: `{item.get('type') or 'unknown'}`",
    ]
    for key in (
        "provider",
        "issuer",
        "bank",
        "company",
        "jurisdiction",
        "application_method",
        "receiving_agency",
        "contact",
        "source_modified_at",
        "source_collected_at",
    ):
        value = item.get(key)
        if value:
            lines.append(f"- {key}: {value}")
    return lines


def render_note(
    config: dict[str, str],
    item: dict[str, Any],
    id_links: dict[str, str],
    id_titles: dict[str, str],
) -> str:
    title = str(item.get("title") or item["id"])
    lines = frontmatter_for(config, item, config["path"].name)
    lines.append(f"# {title}")
    lines.append("")
    lines.append(str(item.get("description") or "JSON export에서 Obsidian 그래프 표시용으로 생성한 노드입니다."))
    lines.append("")
    lines.append("> Graph-only materialization입니다. 원본 데이터는 JSON export가 authoritative source입니다.")
    lines.append("")
    lines.append("## Metadata")
    lines.extend(metadata_lines(item))
    lines.append("")

    if item["id"] in ROOT_EXPORT_IDS:
        lines.append("## OpenFin Bridge")
        lines.append(f"- {link_for('openfin', id_links, id_titles)}")
        lines.append(f"- [[{config['bridge']}]]")
        lines.append("")

    relations = relation_ids(item)
    if relations:
        lines.append("## Relations")
        for key, values in relations.items():
            if not values:
                continue
            rendered = ", ".join(link_for(value, id_links, id_titles) for value in values)
            lines.append(f"- {key}: {rendered}")
        lines.append("")

    status_url = item.get("status_check_url")
    if status_url:
        lines.append("## Status Check")
        lines.append(f"- {status_url}")
        lines.append("")

    source_urls = item.get("source_urls") or []
    if source_urls:
        lines.append("## Source URLs")
        for url in source_urls[:5]:
            lines.append(f"- {url}")
        if len(source_urls) > 5:
            lines.append(f"- ... {len(source_urls) - 5} more")
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    existing_links, existing_titles = collect_existing_id_links()
    records = all_export_items()

    generated_links: dict[str, str] = {}
    generated_titles: dict[str, str] = {}
    generated_paths: dict[str, Path] = {}
    for config, item in records:
        path = path_for_item(config["folder"], item)
        generated_paths[item["id"]] = path
        generated_links[item["id"]] = vault_link(path)
        generated_titles[item["id"]] = str(item.get("title") or item["id"])

    id_links = {**existing_links, **generated_links}
    id_titles = {**existing_titles, **generated_titles}

    if OUTPUT.exists():
        shutil.rmtree(OUTPUT)
    OUTPUT.mkdir(parents=True, exist_ok=True)

    written_paths: set[Path] = set()
    for config, item in records:
        path = generated_paths[item["id"]]
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(render_note(config, item, id_links, id_titles), encoding="utf-8")
        written_paths.add(path)

    index_lines = [
        "---",
        'title: "OpenFin Graph Materialization"',
        'type: "graph-materialization"',
        'tags: ["graph-materialized", "openfin"]',
        "---",
        "",
        "# OpenFin Graph Materialization",
        "",
        "JSON-only finance ontology exports를 Obsidian 그래프에서 볼 수 있도록 생성한 graph-only Markdown 묶음입니다.",
        "",
        "## Domains",
    ]
    for config in EXPORT_CONFIGS:
        index_lines.append(f"- [[95_FinanceGraph/{config['folder']}|{config['domain']}]]")
    (OUTPUT / "README.md").write_text("\n".join(index_lines) + "\n", encoding="utf-8")

    print(
        f"Materialized {len(written_paths)} unique graph notes "
        f"from {len(records)} export records under {OUTPUT.relative_to(ROOT)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
