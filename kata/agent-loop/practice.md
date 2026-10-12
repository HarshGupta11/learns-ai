# Kata 1 — Practice: the agent loop

Do these **one at a time**. After each one, paste your script's output (and the
transcript lines) back to me. I'll name what was correct, then give you the
single most useful adjustment — then you re-run.

## Task 1 — Add a second tool

Add `read_file(path)`:

1. Write the function. A fake file store is fine for the kata, e.g.
   `{"notes.txt": "Buy milk. Dentist moved to 3pm."}`.
2. Add its JSON schema to `TOOL_SCHEMAS` (name, description, parameters, required).
3. Add a branch in `dispatch`.

What I'm checking: the schema matches the function signature, and dispatch
routes by name.

## Task 2 — A two-tool question

Get the agent to answer: "What's in notes.txt and is it raining in Seattle?"

It needs two tool calls, possibly across two loop turns (extend the
scripted model's turn list, or wire up a real model in `call_llm`).

What I'm checking: the transcript shows both tool calls, both observations
land as `tool` messages, and the final answer uses both.

## Task 3 — Feel the guard fail

Set `MAX_ITERS = 2` and re-run a task that needs 3 tool calls.

What I'm checking: you can describe the failure mode in one sentence. This is
why budgets matter — and why real harnesses add stop conditions beyond a raw
cap (e.g. "no progress in N turns", "repeated identical tool call").

---

## Transfer challenge

Name one real situation in your life or work where this loop pattern applies —
a repo Q&A helper over your team's codebase, a personal tool wrapper, or even
re-reading how Muse itself behaves through this lens. You pick the situation;
then sketch it: which part is the model, which part is dispatch, and where
does the transcript live?

## Confidence check

After you've run it: rate 1–5 how confident you are that you could rebuild
this loop from memory.
