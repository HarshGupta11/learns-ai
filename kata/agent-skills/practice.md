# Kata 5 — Practice: agent skills

Do these **one at a time**. After each one, paste your script's output back
to me. I'll name what was correct, then give you the single most useful
adjustment — then you re-run.

## Task 1 — Write a third skill

Write a skill of your own — e.g. `time-check` ("Tell the current time")
or `list-files` ("List the files on the server"). A folder under
`skills/` with a `SKILL.md`: frontmatter (name + description) and a
body with steps. Add its canned turns to `SCRIPTS` so the demo can run
it.

What I'm checking: the registry discovers it with zero code changes.
Same lesson as kata 3's dynamic discovery, but for knowledge instead
of tools: new capability, no client change.

## Task 2 — Break a description

Change one skill's description to something vague ("Help with stuff")
and re-run. Watch routing pick the wrong skill — or none at all. Then
rewrite the description so routing works again.

What I'm checking: you can say why the description is the most
important line in the file. It is the routing table: the agent never
sees the body before choosing, so a bad description means the skill
never gets used, however good its instructions are.

## Task 3 — A second level of disclosure

Give a skill a `references/` file — e.g. a weather-code table for
`weather-check`, or a file-format guide for `file-summary` — and add
one line to the skill body telling the agent to read it only when
needed.

What I'm checking: the references file is NOT loaded during discovery
or during the normal run — only on demand. That is progressive
disclosure one level deeper: descriptions, then body, then references.

---

## Transfer challenge

Name a real skill you would write — a code-review skill for your team
(what to check, what good looks like), or a skill encoding this kata's
own feedback loop (run, paste output, one adjustment per round) — and
sketch it: what triggers it (the description), what it contains, and
what it must NOT contain (secrets, huge dumps, anything that belongs
in a tool instead).

## Confidence check

After you've run it: rate 1–5 how confident you are that you could
explain skills to a teammate — and when to write a skill versus a tool.

## Going further (not a task)

The real spec lives at https://github.com/agentskills/agentskills, and
the production form is the official SDKs plus `scripts/` (code the
agent can run) alongside `references/`. The rule of thumb: a tool is
for what code can do; a skill is for what the model needs to know.
