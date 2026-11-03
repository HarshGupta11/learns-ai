# Kata 3 — Practice: build an MCP server

Do these **one at a time**. After each one, paste your script's output back
to me. I'll name what was correct, then give you the single most useful
adjustment — then you re-run.

## Task 1 — Add a third tool

Add a tool of your own to the server — e.g. `get_time` (current time) or
`list_files` (the keys of the fake file store). Schema in `TOOLS` +
dispatch branch, same as kata 1.

What I'm checking: it shows up in `tools/list` and works via `tools/call`,
with zero changes to the client. That is the point of the protocol: the
client never imports your code.

## Task 2 — Tool errors vs protocol errors

Call a tool that doesn't exist and watch what comes back: a JSON-RPC
`error` object. Now change `tools/call` so a failed tool call instead
returns a result with `isError: true` and the message in `content`.

What I'm checking: you can say why the second shape is better. A protocol
error aborts the call; an `isError` result arrives as an observation the
model can read, explain, and recover from — same idea as kata 1's tool
messages re-entering context.

## Task 3 — Dynamic discovery

Change the demo client so it doesn't hardcode tool names: it reads
`tools/list`, picks the tool whose description fits the user's question,
and calls it.

What I'm checking: adding a new tool to the server works with no client
change at all. A generic client + a self-describing server is the whole
MCP bet.

---

## Transfer challenge

Name one real tool you would expose as an MCP server — a search over your
team's codebase, your learns-ai repo, a personal wrapper — and sketch it:
what are the tools, who is the client, and what travels over the protocol?

## Confidence check

After you've run it: rate 1–5 how confident you are that you could explain
MCP to a teammate from this code alone.

## Going further (not a task)

The production path is the official SDK (`pip install mcp`, FastMCP) and
the spec at https://modelcontextprotocol.io — same shapes you just built,
plus types, validation, resources, prompts, and more transports.
