# Kata 2 — Practice: context management

Do these **one at a time**. After each one, paste your script's output back
to me. I'll name what was correct, then give you the single most useful
adjustment — then you re-run.

## Task 1 — Move the budget

Set `BUDGET` to 150 and re-run.

What I'm checking: can you say when compaction first fires, what got folded
into the summary, what was lost, and whether the final answer stayed
correct? This is the core tradeoff: compaction buys room by spending
information.

## Task 2 — Break compaction

Put `BUDGET` back to 300, then raise the log to 60 lines (change
`range(15)` to `range(60)`) and re-run.

What I'm checking: you notice compaction fires but the transcript stays
over budget — and you can say why (one giant observation dominates the
window). Then: what would you do instead? Ideas, not code yet: truncate
the tool output, return only matching lines, chunk it and retrieve the
relevant chunk. Don't just raise the budget.

## Task 3 — Notes that survive compaction

Add a `notes` list **outside** the transcript. After each tool result,
append one fact line (e.g. `"Seattle: rain, 54F"`). Then set `BUDGET` to
120 so compaction fires aggressively, and show the final answer still
works because the notes survive while transcript turns get folded.

What I'm checking: the notes live outside `messages`, they accumulate one
fact per tool result, and the final answer can use them. This is the
retrieval pattern: durable facts live outside the window; the transcript
is working memory.

---

## Transfer challenge

Name one real situation where context bloat bites you — a long debugging
chat, pasting big logs, a multi-file code review — and sketch it: what
would you budget, what would you compact, and what would you keep as
notes?

## Confidence check

After you've run it: rate 1–5 how confident you are that you could rebuild
budget + compaction from memory.
