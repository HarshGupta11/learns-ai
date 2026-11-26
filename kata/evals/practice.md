# Kata 6 — Practice: evals harness

Do these **one at a time**. After each one, paste your script's output back
to me. I'll name what was correct, then give you the single most useful
adjustment — then you re-run.

Run the harness twice first, so the second run has a baseline to compare
against. `eval_results.json` is runtime data — add it to `.gitignore`
(like kata 4's `memories.json`); it must not be committed.

## Task 1 — Add a case

Add a new eval case — e.g. "What's in notes.txt?" expecting
`["read_file"]` and the words "milk" and "dentist", or a new weather
query of your own. Just a dict in `CASES`.

What I'm checking: the suite grows with zero harness changes. Cases
are data, not code — the same lesson as kata 3's dynamic discovery
and kata 5's registry, but for tests instead of tools or skills.

## Task 2 — Break the agent, watch the harness catch it

Break the agent on purpose — e.g. make `get_weather` return "clear,
70F" for Seattle, or make the router default to Seattle instead of
Chandausi. Run the harness: the failing case shows up. Run it again:
the diff against the saved baseline flags it as a REGRESSION. Then
fix the agent and watch the case flip to FIXED.

What I'm checking: you can say why the saved baseline matters. A
single run tells you what fails now; the diff tells you what *changed*.
Without the baseline, a red case is just a red case — with it, it's a
regression you introduced, and you know exactly when.

## Task 3 — Add a scorer

Add a new scorer that applies to every case — e.g. a tool-count check
(the agent must use at most 1 tool call), or a "no fabrication" check
(the answer must not contain a word that isn't in the tool result or
the query). Wire it into `run_case` alongside tools/contains/absent.

What I'm checking: the scorer is one small function plus one line in
the runner, and it runs against all cases at once. That is the whole
point of a harness: a new quality bar applies everywhere, immediately.

---

## Transfer challenge

Sketch an eval suite for a real agent — e.g. test cases for the
developer skill from kata 5 (TDD → Implementation → Mutation Testing
→ Code Review): what queries would you feed it, what tool calls would
you expect, what must the answer contain, and what must it never say?
Or the same for a code-review agent at work.

## Confidence check

After you've run it: rate 1–5 how confident you are that you could
explain evals to a teammate — and when a deterministic check is enough
versus when you'd want a model grading the answer.

## Going further (not a task)

The production forms are promptfoo, LangSmith evals, and Ragas. The
next layer is LLM-as-judge — a model scoring the answer instead of
keyword checks — which needs a real model. That's kata 7 (Ollama,
local, no API key).
