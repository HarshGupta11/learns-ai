# Kata 1 — Writeup: the agent loop

## Task 1 — Add a second tool

Added `read_file(path)` with a fake file store
(`{"notes.txt": "Buy milk. Dentist moved to 3pm."}`), its JSON schema in
`TOOL_SCHEMAS`, and a dispatch branch routing by tool name.

## Task 2 — A two-tool question

Demo script runs two tool calls — `get_weather` (Seattle) and `read_file`
(notes.txt) — and the final answer uses both observations: rain in Seattle
plus the notes contents.

## Task 3 — Feel the guard fail

Set `MAX_ITERS = 2` on a script that needs 3 turns: the demo hits the cap
before the final answer. That is why budgets matter — and why real
harnesses add stop conditions beyond a raw cap (e.g. "no progress in N
turns", "repeated identical tool call"). Restored to 5 in the finished
solution.

## Transfer challenge

Debugging scenario: the user provides a screenshot + filepath, and the
model dispatches `read_from_screenshot` and `read_file_content` tools
before giving a solution. Note: screenshot-tool output is where context
bloat starts — the bridge to kata 2.

## Confidence

4/5
