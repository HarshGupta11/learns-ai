#!/usr/bin/env python3
"""
KATA 2 -- Context management: budgets, compaction, and notes.

Kata 1's loose end, restated: every observation grows the transcript.
Left alone, the transcript eats the whole context window. The model gets
slower, pricier, and worse at using the middle of a long context
("lost in the middle").

This kata adds three controls to the same loop:
  1. BUDGET     -- measure the transcript, act before it overflows.
  2. COMPACTION -- replace old turns with a short summary, keep going.
  3. NOTES      -- keep durable facts outside the transcript (practice task).

Run it:  python3 kata_02_context.py
No API key needed: mock model + stub summarizer.
"""

import json

# ------------------------------------------------ a token estimator
# Real harnesses count with the model's tokenizer. This kata estimates:
# ~4 characters per token. Wrong in detail, right in shape -- and good
# enough to make the budget mechanics visible.
def estimate_tokens(text: str) -> int:
    return max(1, len(text) // 4)

def transcript_tokens(messages) -> int:
    return sum(estimate_tokens(json.dumps(m, default=str)) for m in messages)

# ------------------------------------------------ tools (same shape as kata 1)
def get_weather(city: str) -> str:
    return {"Seattle": "rain, 54F", "Chandausi": "clear, 88F"}.get(city, "unknown")

LOG_LINES = "\n".join(
    f"2026-11-01 10:{i:02d} INFO worker-{i % 3} processed request {1000 + i} ok"
    for i in range(15)
)

def read_logs() -> str:
    return LOG_LINES

TOOL_SCHEMAS = [
    {"name": "get_weather", "description": "Get current weather for a city",
     "parameters": {"type": "object",
                    "properties": {"city": {"type": "string"}},
                    "required": ["city"]}},
    {"name": "read_logs", "description": "Read the last 15 lines of the app log",
     "parameters": {"type": "object", "properties": {}}},
]

def dispatch(name, args):
    if name == "get_weather":
        return get_weather(**args)
    if name == "read_logs":
        return read_logs()
    raise ValueError(f"unknown tool: {name}")

# ------------------------------------------------ the "brain" (swappable, as in kata 1)
def scripted_model(script):
    turns = list(script)

    def call(messages, tools):
        if not turns:
            return {"content": "(script exhausted)", "tool_calls": []}
        return turns.pop(0)

    return call

# ------------------------------------------------ the stub summarizer
# A real harness calls the model to summarize. This stub keeps the
# mechanics visible: it preserves tool results as one-line facts.
def summarize(messages) -> str:
    facts = []
    for m in messages:
        if m["role"] == "tool":
            facts.append(m["content"][:80])
        elif m["role"] == "user":
            facts.append("user asked: " + m["content"][:80])
    return " | ".join(facts)

# ------------------------------------------------ compaction
# Keep the system message and the most recent turn; fold everything
# else into one summary message. Returns (new_messages, did_compact).
def compact(messages, budget):
    if transcript_tokens(messages) <= budget or len(messages) <= 2:
        return messages, False
    system, rest = messages[:1], messages[1:]
    summary = {"role": "system",
               "content": "Earlier conversation summary: " + summarize(rest[:-1])}
    return system + [summary, rest[-1]], True

# ------------------------------------------------ the loop, now budget-aware
BUDGET = 300  # tokens -- artificially small so compaction fires in the demo
MAX_ITERS = 6

messages = [
    {"role": "system", "content": "You are a helpful assistant. Use tools when needed."},
    {"role": "user", "content": "What's the weather in Seattle and Chandausi, and are there any errors in the app log?"},
]

DEMO_SCRIPT = [
    {"content": None,
     "tool_calls": [{"name": "get_weather", "args": {"city": "Seattle"}}]},
    {"content": None,
     "tool_calls": [{"name": "get_weather", "args": {"city": "Chandausi"}}]},
    {"content": None,
     "tool_calls": [{"name": "read_logs", "args": {}}]},
    {"content": "Seattle: rain, 54F. Chandausi: clear, 88F. The log shows 15 lines, all INFO, no errors.",
     "tool_calls": []},
]

def run(model):
    global messages
    for i in range(MAX_ITERS):
        print(f"\n--- iteration {i + 1} "
              f"(transcript: {transcript_tokens(messages)} tokens) ---")
        reply = model(messages, TOOL_SCHEMAS)
        messages.append({"role": "assistant", "content": reply["content"],
                         "tool_calls": reply["tool_calls"]})
        print("assistant:", json.dumps(reply, indent=2)[:200])

        if not reply["tool_calls"]:      # model answered directly -> done
            print("\nFINAL:", reply["content"])
            return reply["content"]

        for tc in reply["tool_calls"]:
            result = dispatch(tc["name"], tc["args"])
            messages.append({"role": "tool", "content": str(result)})
            print(f"tool [{tc['name']}] -> {str(result)[:80]}...")

            # BUDGET CHECK: after every observation, before the next call.
            before = transcript_tokens(messages)
            messages, compacted = compact(messages, BUDGET)
            if compacted:
                after = transcript_tokens(messages)
                print(f"COMPACTED: {before} -> {after} tokens "
                      f"(budget {BUDGET})")

    print("\nHit iteration cap without a final answer.")
    return None

if __name__ == "__main__":
    run(scripted_model(DEMO_SCRIPT))
    print(f"\n(transcript now holds {len(messages)} messages, "
          f"{transcript_tokens(messages)} tokens)")
