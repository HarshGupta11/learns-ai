# Kata 2 — Writeup: context management

## Task 1 — Move the budget

Compaction fires when the estimated token count goes over budget. Old turns
are folded into a summary: assistant responses are removed, and user/tool
responses are kept, truncated to 80 characters in the summary. The final
answer stayed correct — with the caveat that the response is hardcoded in
the simulated model, so a real model would have to actually read the
compacted transcript.

## Task 2 — Break compaction

The last message is not compacted, so when it is very long it dominates
the window on its own. Fixes: invoke the model summarizer on the tool
output itself so a long output doesn't dominate, and include the last
message in the compaction candidates.

## Task 3 — Notes that survive compaction

Summarize facts into notes and build retrieval (RAG-style) over them:
retrieve only the relevant facts instead of passing all facts to the
model every turn. Notes live outside the transcript, so they survive
compaction.

## Transfer challenge

Reading a very big file: the model determines which lines to read using
grep, compacts if the transcript goes over budget, and stores any semantic
information that could be useful later as notes.

## Confidence

4/5
