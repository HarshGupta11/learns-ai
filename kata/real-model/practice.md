# Kata 7 — Practice: real-model wiring (Ollama)

Do these **one at a time**. After each one, paste your script's output back
to me. I'll name what was correct, then give you the single most useful
adjustment — then you re-run.

## Setup first (once)

1. Install Ollama: download from https://ollama.com/download/mac
   (or `brew install --cask ollama`).
2. Pull a small model: `ollama pull llama3.2` (~2 GB).
3. Check it: `ollama list`, and `curl http://localhost:11434/api/tags`
   should list the model.

Until Ollama is up, the script falls back to the mock and says so —
the demo still runs, but you're talking to the script, not a model.

## Task 1 — Real model vs mock

Run the kata with Ollama up and compare with the mock run: same three
queries, real model. Note where the real model surprises you — wrong
tool arguments, extra text, a turn where it answers without calling
a tool, a turn where it calls a tool twice.

What I'm checking: you can say what changed when the model stopped
being a script. The loop is identical (kata 1); the nondeterminism is
new. That is the whole difference between a mock and a model: the mock
always does the right thing, the model sometimes doesn't, and the
agent has to cope.

## Task 2 — Switch models

Pull a second model (`ollama pull qwen2.5:3b`) and run with
`OLLAMA_MODEL=qwen2.5:3b python3 kata_07_ollama.py`. Compare the two
runs on the same queries.

What I'm checking: the model is config, not code — one env var, zero
code changes. Same lesson as kata 5's registry and kata 6's cases-as-
data: the thing that varies lives outside the code.

## Task 3 — Prompts as code

Change the system prompt — e.g. "Answer in one sentence, with no
extra words" or "Always state the city first" — and re-run. Watch the
answers change with no other edit.

What I'm checking: you can say why the system prompt is code, not
commentary. It is the only instruction the model gets about the job,
and editing it is the cheapest way to change behavior — cheaper than
changing the model, cheaper than changing the loop.

---

## Transfer challenge

Name a real workflow you'd wire to a local model — e.g. the kata-6
evals with an LLM-as-judge (a local model grading answers instead of
keyword checks), or a personal automation (triage, summarise, draft).
Sketch it: which model, what tools, what the system prompt says, and
what happens when the model is down (fallback? fail loudly? queue?).

## Confidence check

After you've run it: rate 1–5 how confident you are that you could
explain real-model wiring to a teammate — and what breaks when the
model stops being a script.

## Going further (not a task)

The next layers are streaming (`stream: true`, NDJSON lines as the
model types), context windows (what happens past the model's limit —
kata 2's compaction, for real), and model routing (kata 9: pick the
model per task).
