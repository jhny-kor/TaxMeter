# OpenTax MCP Install Guide

`OpenTax`는 stdio 방식 MCP 서버입니다. MCP를 지원하는 LLM 클라이언트는
대부분 `command`와 `args`만 설정하면 연결할 수 있습니다.

## 빠른 실행

저장소 안에서 바로 실행:

```sh
cd /path/to/TaxMeter
python3 ontology/mcp_server.py
```

launcher로 실행:

```sh
/path/to/TaxMeter/ontology/run_mcp.sh
```

패키지 형태로 설치:

```sh
cd /path/to/TaxMeter/ontology
python3 -m pip install -e .
```

Homebrew Python처럼 PEP 668로 시스템 설치가 막히는 환경에서는 가상환경을
사용합니다.

```sh
cd /path/to/TaxMeter/ontology
./install_local.sh
```

설치 후 실행:

```sh
opentax-mcp
```

보조 명령:

```sh
opentax-generate
opentax-validate
```

기존 설치 문서와 클라이언트 호환을 위해 `tax-ontology-mcp`,
`tax-ontology-generate`, `tax-ontology-validate` 명령도 legacy alias로 유지합니다.

## Claude Desktop 연결

Claude Desktop 설정 파일의 `mcpServers`에 추가합니다.

macOS 예시 경로:

```text
~/Library/Application Support/Claude/claude_desktop_config.json
```

저장소 직접 실행 방식:

```json
{
  "mcpServers": {
    "opentax": {
      "command": "/path/to/TaxMeter/ontology/run_mcp.sh",
      "args": []
    }
  }
}
```

Python 직접 실행 방식:

```json
{
  "mcpServers": {
    "opentax": {
      "command": "python3",
      "args": [
        "/path/to/TaxMeter/ontology/mcp_server.py"
      ]
    }
  }
}
```

패키지 설치 후 실행 방식:

```json
{
  "mcpServers": {
    "opentax": {
      "command": "opentax-mcp",
      "args": []
    }
  }
}
```

설치 없이 압축 파일이나 복사본을 배포했다면 `command`는 `python3`, `args`는
해당 복사본의 `mcp_server.py` 절대경로로 둡니다.

## Codex 연결

Codex 설정 파일:

```text
~/.codex/config.toml
```

등록 예시:

```toml
[mcp_servers.opentax]
command = "python3"
args = ["/path/to/TaxMeter/ontology/mcp_server.py"]
enabled = true
startup_timeout_sec = 10

[mcp_servers.opentax.tools.opentax_add_or_update_item]
approval_mode = "approve"

[mcp_servers.opentax.tools.opentax_patch_item]
approval_mode = "approve"

[mcp_servers.opentax.tools.opentax_delete_custom_item]
approval_mode = "approve"
```

쓰기 도구는 항목을 추가하거나 수정하므로 approval 대상으로 두는 것을 권장합니다.

## Cursor / 다른 MCP 클라이언트

MCP 설정에서 다음 값을 사용합니다.

```json
{
  "opentax": {
    "command": "/path/to/TaxMeter/ontology/run_mcp.sh",
    "args": []
  }
}
```

패키지 설치 후에는 다음처럼 줄일 수 있습니다.

```json
{
  "opentax": {
    "command": "opentax-mcp",
    "args": []
  }
}
```

## ChatGPT / 원격 MCP

ChatGPT에서 직접 연결하려면 로컬 stdio 서버가 아니라 HTTPS 원격 MCP 서버가
필요합니다. Cloudflare Workers용 읽기 전용 어댑터는
`cloudflare/opentax-mcp`에 있습니다.

배포 이름은 `opentax-mcp`이며, 배포 후 ChatGPT 커넥터에는 다음 형태의 URL을
등록합니다.

```text
https://opentax-mcp.<cloudflare-account>.workers.dev/mcp
```

상세 절차는 [REMOTE_MCP.md](REMOTE_MCP.md)를 봅니다.

## 제공 도구

- `opentax_search`
- `opentax_get_item`
- `opentax_read_note`
- `opentax_neighbors`
- `opentax_sources`
- `opentax_validate`
- `opentax_export_summary`
- `opentax_add_or_update_item`
- `opentax_patch_item`
- `opentax_delete_custom_item`

기존 `tax_ontology_*` 도구명도 legacy alias로 계속 동작합니다.

## 쓰기 동작

쓰기 도구는 기본 공식 데이터 파일을 직접 수정하지 않습니다. 대신
`custom/items.json`에 overlay를 저장하고 다음 순서로 동작합니다.

1. overlay 저장
2. Obsidian vault 재생성
3. JSON export 재생성
4. validator 실행
5. 실패하면 overlay rollback

## 수동 프로토콜 테스트

```sh
printf '%s\n' \
'{"jsonrpc":"2.0","id":1,"method":"initialize","params":{}}' \
'{"jsonrpc":"2.0","id":2,"method":"tools/list","params":{}}' \
| PYTHONDONTWRITEBYTECODE=1 python3 /path/to/TaxMeter/ontology/mcp_server.py
```

## 배포 형태

가장 단순한 배포는 `ontology/` 디렉터리 전체를 복사하거나 zip으로 묶는 것입니다.
서버가 자기 위치 기준으로 `vault`, `custom`, `exports`, `scripts`를 찾기 때문에
복사한 위치의 `mcp_server.py`를 실행하면 됩니다.

```sh
cd /path/to/TaxMeter
zip -r opentax-mcp.zip ontology \
  -x 'ontology/**/__pycache__/*' \
  -x 'ontology/**/*.pyc'
```

복사 후에는 다음 명령으로 검증합니다.

```sh
PYTHONDONTWRITEBYTECODE=1 python3 /path/to/ontology/scripts/validate_ontology.py
```
