#!/usr/bin/env python3
"""Validate Municibid plugin files and probe the hosted MCP. No secrets."""

from __future__ import annotations

import json
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MCP_URL = "https://ai.municibid.com/mcp"
EXPECTED_TOOLS = {
    "search_auctions",
    "get_auction_details",
    "get_sold_comps",
    "estimate_market_value",
    "get_agency_profile",
}
NAME_RE = re.compile(r"^(?!.*(?:--|\.\.))[a-z0-9](?:[a-z0-9.-]*[a-z0-9])?$")
SKILL_NAME_RE = re.compile(r"^[a-z0-9](?:[a-z0-9-]*[a-z0-9])?$")
errors: list[str] = []


def fail(msg: str) -> None:
    errors.append(msg)


def load_json(path: Path) -> dict:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        fail(f"{path.relative_to(ROOT)}: invalid JSON ({exc})")
        return {}
    if not isinstance(data, dict):
        fail(f"{path.relative_to(ROOT)}: expected a JSON object")
        return {}
    return data


def require_files() -> None:
    required = [
        "plugin.json",
        "mcp.json",
        ".mcp.json",
        ".cursor-plugin/plugin.json",
        ".cursor-plugin/marketplace.json",
        ".grok-plugin/plugin.json",
        ".grok-plugin/marketplace.json",
        "skills/municibid/SKILL.md",
        "rules/municibid-read-only.mdc",
        "assets/logo.svg",
        "README.md",
        "LICENSE",
    ]
    for rel in required:
        if not (ROOT / rel).is_file():
            fail(f"missing {rel}")


def check_plugin_json() -> None:
    data = load_json(ROOT / "plugin.json")
    if not data:
        return
    if data.get("$schema") != "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json":
        fail("plugin.json: $schema must be Agent Plugins 1.0.0")
    name = data.get("name")
    if not isinstance(name, str) or not NAME_RE.match(name):
        fail("plugin.json: invalid name")
    if data.get("homepage") != "https://www.municibid.com":
        fail("plugin.json: homepage must be https://www.municibid.com")
    extra = set(data) - {
        "$schema",
        "name",
        "version",
        "description",
        "author",
        "homepage",
        "repository",
        "license",
        "keywords",
        "extensions",
    }
    if extra:
        fail(f"plugin.json: unknown fields {sorted(extra)}")


def check_mcp_json() -> None:
    data = load_json(ROOT / "mcp.json")
    if not data:
        return
    if data.get("$schema") != "https://agent-plugins.org/schemas/1.0.0/mcp.schema.json":
        fail("mcp.json: $schema must be Agent Plugins 1.0.0")
    server = (data.get("mcpServers") or {}).get("municibid") or {}
    if server.get("type") != "streamable-http":
        fail("mcp.json: municibid.type must be streamable-http")
    if server.get("url") != MCP_URL:
        fail(f"mcp.json: url must be {MCP_URL}")
    if "headers" in server:
        fail("mcp.json: do not ship headers or tokens")

    grok = load_json(ROOT / ".mcp.json")
    gserver = (grok.get("mcpServers") or {}).get("municibid") or {}
    if gserver.get("type") != "http":
        fail(".mcp.json: municibid.type must be http")
    if gserver.get("url") != MCP_URL:
        fail(f".mcp.json: url must be {MCP_URL}")
    if "headers" in gserver:
        fail(".mcp.json: do not ship headers or tokens")


def check_cursor_and_grok() -> None:
    cursor = load_json(ROOT / ".cursor-plugin/plugin.json")
    if cursor.get("name") != "municibid":
        fail(".cursor-plugin/plugin.json: name must be municibid")
    if cursor.get("displayName") != "Municibid":
        fail(".cursor-plugin/plugin.json: displayName must be Municibid")
    author = cursor.get("author") or {}
    if set(author) - {"name", "email"}:
        fail(".cursor-plugin/plugin.json: author allows only name and email")
    if cursor.get("logo") != "assets/logo.svg":
        fail(".cursor-plugin/plugin.json: logo path")
    if cursor.get("homepage") != "https://www.municibid.com":
        fail(".cursor-plugin/plugin.json: homepage")

    market = load_json(ROOT / ".cursor-plugin/marketplace.json")
    plugins = market.get("plugins") or []
    if not plugins or plugins[0].get("name") != "municibid":
        fail(".cursor-plugin/marketplace.json: missing municibid plugin")
        return
    entry = plugins[0]
    allowed = {"name", "source", "description"}
    extra = set(entry) - allowed
    if extra:
        fail(f".cursor-plugin/marketplace.json: plugin entry extra fields {sorted(extra)}")
    if set(entry) != allowed:
        fail(".cursor-plugin/marketplace.json: plugin entry must be name, source, description")
    if entry.get("source") != ".":
        fail(".cursor-plugin/marketplace.json: source must be .")

    grok = load_json(ROOT / ".grok-plugin/plugin.json")
    if grok.get("name") != "municibid":
        fail(".grok-plugin/plugin.json: name must be municibid")
    grok_author = grok.get("author") or {}
    if set(grok_author) - {"name", "email"}:
        fail(".grok-plugin/plugin.json: author allows only name and email")


def check_skill() -> None:
    path = ROOT / "skills/municibid/SKILL.md"
    if not path.is_file():
        return
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        fail("skills/municibid/SKILL.md: missing YAML frontmatter")
        return
    parts = text.split("---", 2)
    if len(parts) < 3:
        fail("skills/municibid/SKILL.md: incomplete frontmatter")
        return
    meta = {}
    for line in parts[1].splitlines():
        if ":" in line:
            key, value = line.split(":", 1)
            meta[key.strip()] = value.strip()
    if meta.get("name") != "municibid":
        fail("skill name must match directory: municibid")
    if not SKILL_NAME_RE.match(meta.get("name", "")):
        fail("skill name is invalid")
    desc = meta.get("description", "")
    if not desc or len(desc) > 1024:
        fail("skill description missing or longer than 1024 characters")
    body = parts[2]
    for tool in sorted(EXPECTED_TOOLS):
        if tool not in body:
            fail(f"skill does not mention tool {tool}")
    for phrase in ("never invent", "informational", "municibid.com"):
        if phrase not in body.lower():
            fail(f"skill missing required guidance: {phrase}")


def parse_sse_json(body: str) -> dict:
    for line in body.splitlines():
        if line.startswith("data:"):
            payload = line[5:].strip()
            if payload:
                return json.loads(payload)
    return json.loads(body)


UA = "municibid-plugin-verify/1.0"


def mcp_post(payload: dict) -> dict:
    request = urllib.request.Request(
        MCP_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream",
            "MCP-Protocol-Version": "2025-03-26",
            "User-Agent": UA,
        },
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=30) as resp:
        raw = resp.read().decode("utf-8")
        return parse_sse_json(raw)


def check_live_mcp() -> None:
    get_req = urllib.request.Request(
        MCP_URL,
        headers={"Accept": "application/json, text/event-stream", "User-Agent": UA},
        method="GET",
    )
    try:
        with urllib.request.urlopen(get_req, timeout=20) as resp:
            fail(f"GET /mcp expected 405, got {resp.status}")
    except urllib.error.HTTPError as exc:
        if exc.code != 405:
            fail(f"GET /mcp expected 405, got {exc.code}")
        else:
            print("GET /mcp -> 405 Method not allowed (expected)")

    init = mcp_post(
        {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2025-03-26",
                "capabilities": {},
                "clientInfo": {"name": "municibid-plugin-verify", "version": "1.0.0"},
            },
        }
    )
    info = ((init.get("result") or {}).get("serverInfo") or {})
    print(f"initialize -> {info.get('name')} {info.get('version')}")
    if info.get("name") != "municibid-read-only-mcp":
        fail(f"unexpected server name: {info.get('name')}")

    listed = mcp_post({"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}})
    names = {tool.get("name") for tool in ((listed.get("result") or {}).get("tools") or [])}
    print("tools/list -> " + ", ".join(sorted(names)))
    missing = EXPECTED_TOOLS - names
    extra_note = names - EXPECTED_TOOLS
    if missing:
        fail(f"tools/list missing {sorted(missing)}")
    if extra_note:
        print("note: server also exposed " + ", ".join(sorted(extra_note)))

    search = mcp_post(
        {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": "search_auctions",
                "arguments": {"query": "dump truck", "state": "PA", "limit": 1},
            },
        }
    )
    result = search.get("result") or {}
    structured = result.get("structuredContent") or {}
    count = structured.get("result_count")
    rows = structured.get("results") or []
    if "error" in search:
        fail(f"search_auctions error: {search['error']}")
        return
    if count is None:
        fail("search_auctions returned no result_count")
        return
    print(f"search_auctions(dump truck, PA, limit=1) -> result_count={count}")
    if rows:
        url = rows[0].get("listing_url") or ""
        if "municibid.com/Listing/Details/" not in url:
            fail("search result missing canonical municibid.com listing URL")
        else:
            print("sample result includes a municibid.com listing URL")


def main() -> int:
    require_files()
    check_plugin_json()
    check_mcp_json()
    check_cursor_and_grok()
    check_skill()
    try:
        check_live_mcp()
    except Exception as exc:  # noqa: BLE001 - report probe failures as test errors
        fail(f"live MCP probe failed: {exc}")

    if errors:
        print("FAILED")
        for item in errors:
            print(f"- {item}")
        return 1
    print("OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
