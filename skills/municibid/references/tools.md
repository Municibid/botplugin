# Municibid MCP tools

Hosted endpoint: `https://ai.municibid.com/mcp`  
Transport: Streamable HTTP  
Auth: none required for these public read-only tools  
Server name: `municibid-read-only-mcp`

GET on `/mcp` returns HTTP 405 (`Method not allowed`). That is expected. Clients must POST JSON-RPC.

## `search_auctions`

Search active public-sector surplus auctions.

Arguments: `query`, `category`, `state` (2-letter), `city`, `county`, `zip`, `radius_miles`, `min_price`, `max_price`, `closing_after`, `closing_before`, `sort` (`relevance` | `closing_soon` | `price_low` | `price_high` | `newest`), `limit` (1–50, default 20).

Returns: `results[]` with `auction_id`, `title`, `category`, `seller_name`, `city`, `county`, `state`, `current_price`, `bid_count`, `closing_at`, `image_url`, `listing_url`, plus `result_count` and `data_freshness`.

## `get_auction_details`

Fetch one public listing. Pass `auction_id` and/or `listing_url`.

Returns title, description, seller, location, current price, public reserve if present, bid count, start/close times, images, and canonical `listing_url`.

## `get_sold_comps`

Historical sold auctions. Arguments: `query`, `category`, `make`, `model`, `year`, `state`, `date_from`, `date_to`, `limit`.

Returns `comps[]` with `sold_price`, `closed_at`, location, `listing_url`, and optional `similarity_reason`.

## `estimate_market_value`

Rough low/median/high USD range from sold comps. Arguments: `query`, `auction_id`, `category`, `make`, `model`, `year`, `state`, `lookback_months` (1–60, default 24).

Returns `estimate` (`low`, `median`, `high`, `currency`, `confidence`, `comp_count`), `comps_used`, `notes`, and `disclaimer`. Not an appraisal.

## `get_agency_profile`

Public seller summary. Required `agency_name` (min 2 chars). Optional `state`. No internal IDs.

Returns `agency_name`, location, `active_auction_count`, `recent_sold_count`, and `agency_url`.
