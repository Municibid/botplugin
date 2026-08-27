---
name: municibid
description: Search public Municibid government surplus auctions, open listing details, review sold comps, estimate informational market value, and load public agency summaries. Use when the user asks about Municibid, government surplus, public-sector auctions, dump trucks, police vehicles, heavy equipment, school or township surplus, sold comps, or what something is worth on Municibid.
license: MIT
metadata:
  author: Municibid
  homepage: https://www.municibid.com
  docs: https://info.municibid.com/municibid-chatgpt-app
---

# Municibid auction discovery

Use the hosted Municibid MCP tools for **read-only discovery of public auction data**. Never invent listings, prices, close times, or agency names.

## Product contract

Municibid is an online marketplace where governments, schools, authorities, and other public agencies sell surplus assets to the public. Conservative public facts: founded in 2006 and headquartered in Pottstown, Pennsylvania. If you cite scale figures (buyers, seller counts, years in business), take them from [the ChatGPT app page](https://info.municibid.com/municibid-chatgpt-app) and mark them as **company-reported**.

This plugin does **not** place bids, create listings, modify accounts, process payments, complete transactions, expose bidder identities, or expose seller contact information.

All bidding, payments, accounts, listings, and transactions stay on [municibid.com](https://www.municibid.com). When the user wants to bid or inspect a listing further, send them to the canonical `listing_url` from the tool response.

Market-value language is informational only. Never call an estimate an appraisal, guarantee, professional valuation, or prediction of the final hammer price.

## Tool routing

Call the live `municibid` MCP server (`https://ai.municibid.com/mcp`). Match the user intent to **one** primary tool:

| User intent | Tool | Do not use |
| --- | --- | --- |
| Find what is for sale now ("dump trucks in Pennsylvania", "closing this week") | `search_auctions` | `get_sold_comps`, `estimate_market_value` |
| Details for one listing (Municibid URL or numeric ListingId) | `get_auction_details` | Search when an id or URL is already known |
| What similar items actually sold for | `get_sold_comps` | `search_auctions` (those are live, not sold) |
| Rough worth / value range | `estimate_market_value` | Invent a range from memory |
| Seller or agency storefront ("Town of Mansfield, Mass.") | `get_agency_profile` | Internal account IDs |

You may follow a search with `get_auction_details` for a specific match, or follow comps with `estimate_market_value` when the user asked for a range.

If a tool errors, times out, or returns no rows, say so. **Never fabricate auctions.**

## Tool arguments

### `search_auctions`

Use for active public-sector surplus.

- `query`: keywords (`dump truck`, `police SUV`, `backhoe`)
- `state`: two-letter US abbreviation (`PA`, `MA`)
- `city`, `county`, `zip`, `radius_miles`
- `category`: only when the user names a Municibid category
- `min_price`, `max_price`
- `closing_after`, `closing_before`: filter the closing window
- `sort`: `relevance` | `closing_soon` (default) | `price_low` | `price_high` | `newest`
- `limit`: 1–50, default 20

### `get_auction_details`

Provide **at least one** of:

- `auction_id`: numeric ListingId such as `"123456"`
- `listing_url`: `https://municibid.com/Listing/Details/123456`

If both are sent, `auction_id` wins.

### `get_sold_comps`

Use for completed sales, not live asking prices.

- `query`, `category`, `make`, `model`, `year`
- `state`: two-letter US abbreviation
- `date_from`, `date_to`
- `limit`: 1–50, default 20

### `estimate_market_value`

Returns a low / median / high USD range plus a confidence label and the comps used.

- Identify the item with `query` and/or `auction_id`, plus `category`, `make`, `model`, `year`, `state` when known
- `lookback_months`: 1–60, default 24

Always repeat the tool's disclaimer. Phrase results as a **directional range from Municibid sold data**, not a value opinion.

### `get_agency_profile`

- `agency_name` (required): public display-name fragment, e.g. `Springfield Township`. Do **not** pass internal agency IDs.
- `state` (optional): two-letter abbreviation to disambiguate common names

Matching is case-insensitive and partial. If several agencies match, the server returns the best match.

## How to present results

- Prefer the canonical `listing_url` from the tool. Do not invent URLs.
- `closing_at`, `closed_at`, and `end_date` are US Eastern Time with an RFC3339 offset. Display them as Eastern Time (ET).
- Include seller/agency **public display name**, location, current or sold price, bid count, and close time when the tool returns them.
- Do not surface bidder identities or seller contact details even if a model is tempted to guess them.
- End buyer-facing answers with a path to bid on municibid.com.

## Example prompts

These are prompts, not live results. Always call the tools.

- Find dump trucks in Pennsylvania.
- Get details for this Municibid auction URL.
- Show sold dump truck comps in Pennsylvania.
- Estimate market value for a used backhoe in Pennsylvania.
- Show the agency profile for West Norriton, PA.
