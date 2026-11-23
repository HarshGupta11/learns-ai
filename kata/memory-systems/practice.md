# Kata 4 — Practice: memory systems

Do these **one at a time**. After each one, paste your script's output back
to me. I'll name what was correct, then give you the single most useful
adjustment — then you re-run.

## Task 1 — Add a memory, test the retrieval

Add a memory of your own (a preference or a fact), then query it: verify
it comes back for a related query and not for an unrelated one (try "What
is the capital of France?").

What I'm checking: you can say what the misses tell you about keyword
scoring. Hint: "Sam" matches everything in the demo store, so a common
token dilutes ranking — a related query pulls in unrelated memories that
share one word. That's why real systems use embeddings, not keywords.

## Task 2 — Survive the process

Right now session B is a new object in the same run. Prove the memory
survives a real restart: run the script once to store, then in a fresh
terminal run a tiny one-liner (or a small `recall.py`) that loads
`memories.json` and answers one query.

What I'm checking: it answers from disk with no seeding. If it does, your
agent remembers across sessions — which is the entire point of this kata.

## Task 3 — Forgetting

A store that only grows eventually drowns retrieval. Add one of:
(a) recency weighting — a recent memory scores higher than an old one
with the same overlap; or (b) a `prune()` that drops memories older than
N days, or never retrieved.

What I'm checking: the store stays useful as it grows. Say which rule you
picked and what it would wrongly forget — every forgetting rule has a
failure mode, and naming it is the task.

---

## Transfer challenge

Name a real situation where an agent needs memory across sessions — a
coding assistant remembering your team's conventions, an agent tracking
your kata progress — and sketch it: what gets stored, what gets
retrieved, what gets forgotten, and what must never be stored (secrets,
credentials — memory is the wrong place for those).

## Confidence check

After you've run it: rate 1–5 how confident you are that you could
explain why an agent with a memory store beats one with only a transcript.

## Going further (not a task)

Production memory uses embeddings + vector search instead of keyword
overlap, and distinguishes episodic (events), semantic (facts), and
procedural (skills) memory. Your notes in kata 2 were the in-memory
version of this store.
