# Municibid

Cursor marketplace plugin and Grok Bot connector for [Municibid](https://www.municibid.com). It wraps the official hosted MCP at [`https://ai.municibid.com/mcp`](https://ai.municibid.com/mcp) so agents can search public government surplus auctions.

This is the Cursor / Grok companion to the [Municibid ChatGPT app](https://info.municibid.com/municibid-chatgpt-app).

## What it does

Read-only discovery of public Municibid auction data:

- Search active government and school surplus auctions
- Open public listing details
- Review sold comps
- Get rough informational market-value ranges from Municibid sold data
- View public agency summaries and storefront links

All bidding, payments, accounts, listings, and transactions stay on [municibid.com](https://www.municibid.com).

The plugin does **not** place bids, create listings, modify accounts, process payments, complete transactions, expose bidder identities, or expose seller contact information. Market-value language is informational only — not an appraisal or a guarantee.

## How this differs from the ChatGPT app

| | ChatGPT app | This plugin |
| --- | --- | --- |
| Host | ChatGPT | Cursor, Grok Bot, and other Agent Plugins clients |
| Data | Same official Municibid MCP | Same official Municibid MCP (`https://ai.municibid.com/mcp`) |
| Capabilities | Search, listing details, sold comps, informational value ranges, agency summaries | Same five tools |
| Transactions | On municibid.com | On municibid.com |

The ChatGPT app is a conversational listing surface inside ChatGPT. This repo packages the same hosted server as an installable plugin: manifests, MCP config, and skills that teach an agent when to search vs. pull comps vs. estimate value vs. load an agency profile.

## Install in Cursor

### Marketplace

1. Open **Customize** in the Cursor sidebar.
2. Search for **Municibid**.
3. Install at user or project scope.

Until the listing is live, submit or install from this repository: [cursor.com/marketplace/publish](https://cursor.com/marketplace/publish). Docs: [https://info.municibid.com/municibid-chatgpt-app](https://info.municibid.com/municibid-chatgpt-app). Homepage: [https://www.municibid.com](https://www.municibid.com).

### Local (development)

Cursor loads plugins from `~/.cursor/plugins/local` when local plugin imports are allowed.

```bash
git clone https://github.com/Municibid/botplugin.git
mkdir -p ~/.cursor/plugins/local
ln -s "$(pwd)/botplugin" ~/.cursor/plugins/local/municibid
```

Reload the window (**Developer: Reload Window**), then open **Customize** and confirm the Municibid MCP server and the `municibid` skill.

You can also point a project or user `mcp.json` at the hosted server directly:

```json
{
  "mcpServers": {
    "municibid": {
      "url": "https://ai.municibid.com/mcp"
    }
  }
}
```

## Grok Bot

This repo is a Grok Bot-compatible connector bundle:

- `.grok-plugin/plugin.json` and `.grok-plugin/marketplace.json`
- `.mcp.json` with `type: "http"` (Grok / Claude-style remote MCP)
- Root `plugin.json` + `mcp.json` for the [Agent Plugins](https://agent-plugins.org) standard

Install from **App Settings → Plugins**, or add this repository as a team marketplace. After install, ask Grok to search Municibid (for example, “Find dump trucks in Pennsylvania”).

## Authentication

**None for the public read-only MCP.**

Probed on 2026-08-27:

- `POST https://ai.municibid.com/mcp` `initialize`, `tools/list`, and `tools/call` succeed without `Authorization` or OAuth.
- `GET https://ai.municibid.com/mcp` returns HTTP 405 and `Method not allowed` — expected for Streamable HTTP.
- `/.well-known/oauth-authorization-server` and `/.well-known/oauth-protected-resource` (and `/mcp` variants) return HTTP 401 `{"error":"Unauthorized"}` with no usable OAuth metadata. They behave like unknown-path guards, not an MCP login flow.

Do not add API keys, bearer tokens, or invented client IDs. If Municibid later requires OAuth, Cursor will show its standard MCP sign-in using metadata from the live server — not values from this repo.

## MCP server

| | |
| --- | --- |
| URL | `https://ai.municibid.com/mcp` |
| Transport | Streamable HTTP |
| Server | `municibid-read-only-mcp` (title: Municibid) |
| Auth | None |

Tools (from live `tools/list`):

| Tool | Use for |
| --- | --- |
| `search_auctions` | Active listings (keyword, location, price, closing window) |
| `get_auction_details` | One listing by `auction_id` or municibid.com URL |
| `get_sold_comps` | Historical sold comparables |
| `estimate_market_value` | Directional low/median/high range from sold data |
| `get_agency_profile` | Public agency summary by display name + optional state |

Close times are US Eastern Time. Cite the canonical `listing_url` from the tool response.

## Layout

```text
plugin.json                      Agent Plugins 1.0.0 manifest
mcp.json                         Agent Plugins MCP config (streamable-http)
.mcp.json                        Grok Bot / Claude-style MCP config (http)
.cursor-plugin/plugin.json       Cursor plugin manifest
.cursor-plugin/marketplace.json  Cursor team marketplace index
.grok-plugin/plugin.json         Grok Bot connector manifest
.grok-plugin/marketplace.json    Grok Bot marketplace index
skills/municibid/                Agent skill (tool routing + read-only contract)
rules/municibid-read-only.mdc    Cursor rule
assets/logo.svg                  Marketplace logo
```

## Verification checklist

1. **Install** — marketplace listing or `~/.cursor/plugins/local/municibid` symlink, then reload.
2. **Tools appear** — Customize shows the `municibid` MCP server. Expected tools: `search_auctions`, `get_auction_details`, `get_sold_comps`, `estimate_market_value`, `get_agency_profile`.
3. **Sample search** — in chat: `Find dump trucks in Pennsylvania.` The agent should call `search_auctions` and return live rows with municibid.com listing URLs. Do not accept invented listings.

From this repo you can also probe the hosted server:

```bash
python3 scripts/verify-plugin.py
```

That checks manifests, skill frontmatter, and a live `tools/list` plus a small `search_auctions` call. It does not print or commit listing bodies.

## Company notes

Municibid is an online auction marketplace for governments, schools, authorities, and utilities to sell surplus and forfeitures to the public. Founded in 2006. Headquartered in Pottstown, Pennsylvania.

Figures on [the ChatGPT app page](https://info.municibid.com/municibid-chatgpt-app) (for example buyer-network or seller counts) are **company-reported**. Do not invent additional metrics.

## Links

- Homepage: [https://www.municibid.com](https://www.municibid.com)
- Docs: [https://info.municibid.com/municibid-chatgpt-app](https://info.municibid.com/municibid-chatgpt-app)
- Privacy: [https://info.municibid.com/privacy-policy](https://info.municibid.com/privacy-policy)
- Terms: [https://info.municibid.com/terms](https://info.municibid.com/terms)
- Support: [https://support.municibid.com/en/](https://support.municibid.com/en/)
- Cursor plugins: [https://cursor.com/docs/plugins](https://cursor.com/docs/plugins)
- Agent Plugins: [https://agent-plugins.org](https://agent-plugins.org)
