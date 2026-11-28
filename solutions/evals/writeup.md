# Kata 6 — Writeup: evals harness

## Task 1 — Add a case

Added two cases as pure data, zero harness changes: `weather-seattle-
umbrella` ("Should I carry an umbrella in Seattle?", expects
`["get_weather"]` and the words "rain" and "umbrella") and
`file-read` ("What's in notes.txt?", expects `["read_file"]` and
"milk" / "dentist").

## Task 2 — Break the agent, watch the harness catch it

Broke the agent two ways: Seattle's weather changed to "clear, 70F"
and the router default flipped to Seattle. The harness flagged the
failures, and the diff against the saved baseline flagged them as
REGRESSIONs. First instinct was to rewrite the cases to match the
broken agent — that made the suite green, but it moved the goalposts:
the rain branch lost all coverage. Fixed the agent back instead
(Seattle "rain, 54F", default Chandausi), restored the original
cases, and fixed the new umbrella case to expect "rain" + "umbrella".
Lesson: when a case goes red, fix the code, not the test.

## Task 3 — Add a scorer

Added two scorers, both wired into `run_case` so they apply to every
case: a tool-count check (at most one tool call) and a no-fabrication
check. The fabrication scorer is stubbed to always pass for now — the
naive version fails on the agent's own template words ("No umbrella
needed", "says:"), which aren't in the query or the tool result. The
fix (deferred): a template allowlist of the agent's own phrasing.

## Transfer challenge

Per-turn assertions for the developer skill: a multi-turn workflow
gets one eval case per turn, each with its expected tool and keyword.
Example — TDD turn: query "Write the test for this feature.",
expected tool `test_generator`, expected keyword "Test annotation".

## Confidence

4/5
