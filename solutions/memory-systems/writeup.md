# Kata 4 — Writeup: memory systems

## Task 1 — Add a memory, test the retrieval

Added a France memory ("The France's capital is Paris") and the query
"What is the capital of France?". Found a tokenization gap while
debugging: the query tokens `{'sam', 'food', 'suggest'}` did not match
the memory tokens `{"sam's", 'miso', 'cat', 'named'}` — `"sam"` never
equals `"sam's"` because `strip()` only removes leading/trailing
punctuation. Fix: normalize possessives in `tokens()` (drop a trailing
`"'s"`). A second, bigger find: with `MAX_MEMORY_SIZE = 3`, the three
preference memories were evicted during seeding, so the food and
scheduling queries returned nothing. Fix: raise the cap to 5.

## Task 2 — Survive the process

Deleted all the seeds from the code and re-ran: the agent still
remembered the facts and preferences, proving the data comes from
`memories.json` on disk, not from the code. (Sharper version of the
test: delete the seeds only — should still answer; delete both the
seeds and `memories.json` — should know nothing.)

## Task 3 — Forgetting

Chose LRU (least recently used) eviction, the same policy caches use:
`search()` moves retrieved memories to the end of the list and
`prune()` pops from the front on overflow. The problem with pure LRU:
it forgets important-but-rarely-used memories — adding a new rule
evicted "Sam likes spicy food" while trivia survived. Fix implemented:
importance-weighted eviction (`KIND_WEIGHT`: preference 2, fact 1) —
`prune()` now evicts the least-recently-used memory of the
lowest-priority kind, so preferences survive and trivia goes first.
The production answers beyond this kata are consolidation (summarize
instead of deleting) and tiering (demote to a cold archive instead of
evicting).

## Transfer challenge

For a coding task: if the agent completed task 1 in session 1, it is
beneficial for it to know that in session 2 — remembering completed
work helps it do task 2.

## Confidence

4/5
