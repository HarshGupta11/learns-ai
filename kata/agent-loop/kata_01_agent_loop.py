#!/usr/bin/env python3
"""
KATA 1 -- The agent loop, from scratch (~70 lines).

Core idea: an agent is just a loop.
  model proposes -> code executes -> results re-enter the model's context -> repeat.

Run it:   python3 kata_01_agent_loop.py

No API key needed: a scripted stand-in plays the "brain" so you can watch the
loop mechanics. Swap in a real model later by changing exactly one function.
"""

import json

# ------------------------------------------------ STEP 1: tools are contracts
# Tools are plain functions + JSON schemas the model can read.
# The model NEVER runs code. It emits structured JSON; the harness executes.
# The schema is the entire interface between the model and your code.

def get_weather(city: str) -> str:
    data = {"Seattle": "rain, 54F", "Chandausi": "clear, 88F"}
    return data.get(city, "unknown")

TOOL_SCHEMAS = [
    {
        "name": "get_weather",
        "description": "Get current weather for a city",
        "parameters": {
            "type": "object",
            "properties": {"city": {"type": "string"}},
            "required": ["city"],
        },
    }
]

# ------------------------------------------------ STEP 4: dispatch is yours
# Tool execution is ordinary code. This is where permissions, timeouts, retries,
# and side effects live -- and where real agent bugs hide.

def dispatch(name, args):
    if name == "get_weather":
        return get_weather(**args)
    raise ValueError(f"unknown tool: {name}")

# ------------------------------------------------ the "brain" (swappable)
def scripted_model(script):
    """A fake model that plays a canned sequence of turns.

    Each turn is {"tool_calls": [...]} or {"content": "..."}.
    The loop cannot tell this apart from a real LLM -- that
    interchangeability is the whole point of the harness design.
    """
    turns = list(script)

    def call(messages, tools):
        if not turns:
            return {"content": "(script exhausted)", "tool_calls": []}
        return turns.pop(0)

    return call

# To use a real model, replace the body below with an actual API call
# (Anthropic / OpenAI / Bedrock all accept `messages` + `tools` and return
# either a text reply or tool calls). Nothing else in this file changes.
def call_llm(messages, tools):
    raise NotImplementedError("wire a real API call here, or use scripted_model")

# ------------------------------------------------ STEP 2: seed the transcript
# System + user + assistant + tool results form one growing transcript.
# A single LLM call is stateless; the transcript is the agent's memory.

messages = [
    {"role": "system", "content": "You are a helpful assistant. Use tools when needed."},
    {"role": "user", "content": "Should I carry an umbrella in Seattle today?"},
]

DEMO_SCRIPT = [
    {"content": None,
     "tool_calls": [{"name": "get_weather", "args": {"city": "Seattle"}}]},
    {"content": "Yes -- it's raining in Seattle (54F). Carry an umbrella.",
     "tool_calls": []},
]

MAX_ITERS = 5  # GUARD: loops must always terminate.
               # Infinite loops are the cheapest agent failure.

# ------------------------------------------------ STEP 3: the loop (agency lives here)
def run(model):
    for i in range(MAX_ITERS):
        print(f"\n--- iteration {i + 1} ---")
        reply = model(messages, TOOL_SCHEMAS)

        # Append the assistant message FIRST: the transcript keeps the model's
        # reasoning. Drop this and the agent loses its own train of thought.
        messages.append({"role": "assistant", "content": reply["content"],
                         "tool_calls": reply["tool_calls"]})
        print("assistant:", json.dumps(reply, indent=2)[:300])

        if not reply["tool_calls"]:      # model answered directly -> done
            print("\nFINAL:", reply["content"])
            return reply["content"]

        for tc in reply["tool_calls"]:   # model wants tools run
            result = dispatch(tc["name"], tc["args"])      # STEP 4: execute
            messages.append(               # STEP 5: observation re-enters context
                {"role": "tool", "content": str(result)})
            print(f"tool [{tc['name']}] -> {result}")
            # ^ every observation grows the transcript. That is also where
            # context bloat starts -- the bridge to the next kata topic.

    print("\nHit iteration cap without a final answer.")
    return None

if __name__ == "__main__":
    run(scripted_model(DEMO_SCRIPT))
    print(f"\n(transcript now holds {len(messages)} messages)")
