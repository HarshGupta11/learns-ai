# Kata 3 — Writeup: build an MCP server

## Task 1 — Add a third tool

Added two tools, `get_time` (current time) and `list_files` (keys of the
fake file store), each with a schema in `TOOLS` and a dispatch branch.
`read_file` was refactored onto a shared `FILES` dict, so `list_files`
and `read_file` agree by construction. Both new tools show up in
`tools/list` and work via `tools/call` with no client changes.

## Task 2 — Tool errors vs protocol errors

A failed tool call now returns a result with `isError: true` and the
message in `content` (`"Tool call failed: {e}"`) instead of a JSON-RPC
protocol error. A protocol error aborts the call; an `isError` result
arrives as an observation the model can read, explain, and recover from.

## Task 3 — Dynamic discovery

The demo client no longer hardcodes tool names: `pick_tool` scores the
user's query against each tool's name + description from `tools/list`,
and `extract_args` fills in the arguments. The demo query "What is
current time" routes to `get_time`. The client never imports server code;
the descriptions are the routing table.

Nuances found while testing the scorer:

- Stop words contribute to the score. The `len(word) > 2` filter drops
  "is" and "of", but "the" (3 letters) still counts — it appears in
  several descriptions, so it adds noise to every tool's score.
- Punctuation is not stripped. `"time?"` does not match `"time"`, while
  `"time"` does — so a question mark can silently drop a matching word
  from the score.

## Transfer challenge

A CR search tool, with the developer as the client: over the protocol,
`tools/list` carries the tool's schema and `tools/call` carries the
search input in and the matching code reviews out.

## Confidence

4/5
