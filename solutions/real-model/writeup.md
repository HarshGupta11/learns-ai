# Kata 7 — Writeup: real-model wiring (Ollama)

## Task 1 — Real model vs mock

Ran the same three queries against the mock, llama3.2, and qwen2.5:3b.
All three called the right tool with the right args on the first turn,
every time — no wrong args, no double calls. Differences: the mock's
answers are mechanical ("Based on the tool result: ..."), the models'
are natural sentences; and latency is now observable — first query
slow (~4s, cold model load), then ~1s. Qwen quotes file contents
verbatim; llama paraphrases ("Dentist moved to 3pm" became "Dentist
appointment is at 3pm").

## Task 2 — Switch models

`OLLAMA_MODEL=qwen2.5:3b` switches models with one env var and zero
code changes. The default is back to `llama3.2` — the env var is the
switch, that's the point.

## Task 3 — Prompts as code

First edit put "(Always state the city first)" in parentheses
mid-sentence: ignored — Q2/Q3 were identical to the run before, and
Q1 didn't start with the city. Second edit made it a prominent first
line with an example format ("[IMPORTANT RULE - Always write down
city in response first for weather questions. Example: Seattle:
weather is rainy]"): now observable. Q3 follows it exactly
("Chandausi: The weather is clear, with a high of 88F."), and Q2
became verbatim contents ("Buy milk. Dentist moved to 3pm.") with no
wrapper sentence — "no extra words" took effect. Q1 still leads with
"Yes" instead of the city: a yes/no question pulls the model to
answer Yes/No first, so format instructions compete with question
shape. Lesson: prompt instructions must be prominent and checkable,
and small models follow them unreliably — which is what kata 6's
evals are for.

## Transfer challenge

A local code-review agent: tools `read_file` (code + coding
guidelines), `web_fetch` (latest design patterns), `write_tool`
(review summary); system prompt as a software-development reviewer
whose code will be reviewed by a senior principal engineer, so find
the bugs and bad patterns first. If the model is down: retry with a
circuit breaker, then switch to another model (model1, model2,
model3 — whichever is available). That fallback chain is kata 9's
topic.

## Confidence

4/5
