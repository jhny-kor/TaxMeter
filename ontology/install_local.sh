#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"

if ! command -v python3 >/dev/null 2>&1; then
  echo "python3 is required" >&2
  exit 1
fi

python3 -m venv .venv
. .venv/bin/activate
python -m pip install --upgrade pip setuptools
python -m pip install -e .

echo "Installed tax-ontology-mcp into $(pwd)/.venv"
echo "Use this MCP command in clients:"
echo "$(pwd)/.venv/bin/tax-ontology-mcp"
