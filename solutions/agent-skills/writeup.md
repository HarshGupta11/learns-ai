# Kata 5 — Writeup: agent skills

## Task 1 — Write a third skill

Added a `time-check` skill: a folder under `skills/` with a `SKILL.md`
(frontmatter + steps) plus a real `time_check` tool using `ZoneInfo`,
a dispatch branch, canned turns, and a third query ("What is current
time in Seattle?"). The registry discovers it with zero code changes
— new capability, no client change.

## Task 2 — Break a description

Changed file-summary's description to "Help doing the stuff": the
summarize query then scored 0 against every skill, so the demo
answered from scratch. That proves the description is the routing
table — the agent never sees the body before choosing. Rewrote the
description to "Read a file and summarize its contents in one line"
and routing works again.

## Task 3 — A second level of disclosure

Added `references/format.md` (an output-format guide) to file-summary
and a step in the skill body pointing to it. The registry never loads
references — only `SKILL.md` files are read, and only the matched
skill's body — so the format guide loads only on demand: descriptions,
then body, then references.

Fixes applied after review: time-check's heading said "# Weather
check" (copy-paste) and its steps named `get_time` while the tool is
`time_check`; both corrected so the skill file agrees with the code.

## Transfer challenge

A developer skill: TDD → Implementation → Mutation Testing → Code
Review → iterate back to TDD. A workflow skill with an explicit
iteration edge — mutation testing as the verification step, code
review as the quality gate.

## Confidence

4/5
