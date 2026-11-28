#!/usr/bin/env python3
"""
KATA 7 -- Real-model wiring: swap the mock for Ollama.

Katas 1-6 ran on scripted mock models. This kata plugs in a real one
-- a small model running locally on your Mac via Ollama. No API key,
no cloud, no cost: the model runs on your machine and answers over
HTTP at http://localhost:11434.

Three ideas:
  1. THE MODEL IS A SERVICE, NOT A FUNCTION -- it lives behind HTTP,
     speaks JSON, and can be down, slow, or missing the model. The
     agent must handle all three: unreachable server, model not
     pulled, and a slow first reply. (The mock never failed, so none
     of this mattered before.)
  2. THE LOOP DOESN'T CHANGE -- kata 1's loop (ask -> tool calls ->
     results -> ask again) is identical; only the model call changes.
     The mock was a stand-in with the same shape: a turn returns
     either text or tool calls. Swapping it out touches one function.
  3. THE MODEL IS CONFIG, NOT CODE -- which model answers is an env
     var (OLLAMA_MODEL), not a code change. Same instinct as kata 5's
     registry: new capability, no client change. (Kata 9 turns this
     into a router that picks the model per task.)

Setup (once, on your Mac -- Muse can't run shell there, so you do):
  1. Install Ollama: download from https://ollama.com/download/mac
     (or: brew install --cask ollama)
  2. Pull a small model:  ollama pull llama3.2     (~2 GB)
  3. Check it:           ollama list
                         curl http://localhost:11434/api/tags

Run it:  python3 kata_07_ollama.py
         OLLAMA_MODEL=qwen2.5:3b python3 kata_07_ollama.py   (another model)
If Ollama isn't running or the model isn't pulled, the script says so
and falls back to the mock, so the demo still runs.
"""

import json
import os
import time
import urllib.error
import urllib.request

OLLAMA_HOST = os.environ.get("OLLAMA_HOST", "http://localhost:11434")
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "llama3.2")
MAX_ITERS = 5

# ------------------------------------------------ tools (same fake stores as kata 1)
def get_weather(city: str) -> str:
    return {"Seattle": "rain, 54F", "Chandausi": "clear, 88F"}.get(city, "unknown")

def read_file(path: str) -> str:
    return {"notes.txt": "Buy milk. Dentist moved to 3pm."}.get(path, "unknown")

def dispatch(name, args):
    if name == "get_weather":
        return get_weather(**args)
    if name == "read_file":
        return read_file(**args)
    raise ValueError(f"unknown tool: {name}")

# Ollama tool spec: the same tools, described for the model.
TOOLS = [
    {"type": "function",
     "function": {"name": "get_weather",
                  "description": "Get the current weather in a city.",
                  "parameters": {"type": "object",
                                 "properties": {"city": {"type": "string",
                                                         "description": "City name, e.g. Seattle"}},
                                 "required": ["city"]}}},
    {"type": "function",
     "function": {"name": "read_file",
                  "description": "Read a file's contents.",
                  "parameters": {"type": "object",
                                 "properties": {"path": {"type": "string",
                                                         "description": "File path, e.g. notes.txt"}},
                                 "required": ["path"]}}},
]

SYSTEM_PROMPT = ("You are a helpful assistant with access to tools. "
                 "Use get_weather for weather questions and read_file "
                 "for questions about a file's contents. "
                 "Answer in one sentence.")

# ------------------------------------------------ the real model: one HTTP call
def ollama_turn(messages):
    """One turn against Ollama. Returns (content, tool_calls, error).
    tool_calls is a list of {"name": ..., "args": {...}}."""
    payload = {"model": OLLAMA_MODEL, "messages": messages,
               "tools": TOOLS, "stream": False}
    req = urllib.request.Request(
        OLLAMA_HOST + "/api/chat",
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"}, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            body = json.load(resp)
    except urllib.error.HTTPError as e:
        try:
            err = json.load(e).get("error", "")
        except Exception:
            err = e.read().decode(errors="replace")
        if "not found" in str(err):
            return None, [], (f"model '{OLLAMA_MODEL}' is not pulled yet -- "
                              f"run: ollama pull {OLLAMA_MODEL}")
        return None, [], f"Ollama answered with HTTP {e.code}: {err}"
    except urllib.error.URLError:
        return None, [], (f"Ollama is not reachable at {OLLAMA_HOST} -- "
                          "is Ollama running? (open the Ollama app, or run: "
                          "ollama serve)")
    msg = body.get("message", {})
    calls = []
    for tc in msg.get("tool_calls") or []:
        fn = tc.get("function", {})
        args = fn.get("arguments", {})
        if isinstance(args, str):  # some servers send arguments as a JSON string
            args = json.loads(args)
        calls.append({"name": fn.get("name"), "args": args})
    return msg.get("content") or "", calls, None

# ------------------------------------------------ the mock model (kata 1 shape)
def mock_turn(messages):
    """Same shape as ollama_turn, but scripted. Stands in when Ollama
    is unavailable, so the demo still runs."""
    for m in reversed(messages):
        if m["role"] == "tool":
            return f"Based on the tool result: {m['content']}", []
    user = next(m["content"] for m in reversed(messages)
                if m["role"] == "user")
    q = user.lower()
    if any(w in q for w in ("weather", "umbrella", "rain")):
        city = "Seattle" if "seattle" in q else "Chandausi"
        return None, [{"name": "get_weather", "args": {"city": city}}]
    if any(w in q for w in ("file", "summarize", "notes", ".txt", ".pdf")):
        path = "notes.txt" if "notes.txt" in q else "report.pdf"
        return None, [{"name": "read_file", "args": {"path": path}}]
    return "I don't know.", []

# ------------------------------------------------ the agent loop (kata 1, unchanged shape)
def run_agent(query, use_mock):
    """Returns (final_answer, fell_back_to_mock)."""
    messages = [{"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": query}]
    for i in range(MAX_ITERS):
        if use_mock:
            content, calls = mock_turn(messages)
        else:
            content, calls, err = ollama_turn(messages)
            if err:
                print(f"  [!] {err}")
                print("  falling back to the mock model for this run")
                use_mock = True
                content, calls = mock_turn(messages)
        if calls:
            for c in calls:
                print(f"  turn {i + 1}: model calls {c['name']}({c['args']})")
                try:
                    result = dispatch(c["name"], c["args"])
                except Exception as e:
                    result = f"Tool call failed: {e}"
                print(f"  turn {i + 1}: tool -> {result}")
                messages.append({"role": "assistant", "content": content or "",
                                 "tool_calls": [{"function": {"name": c["name"],
                                                             "arguments": c["args"]}}]})
                messages.append({"role": "tool",
                                 "content": f"{c['name']}({c['args']}) -> {result}"})
            continue
        print(f"  A: {content}")
        return content, use_mock
    print("  [!] hit MAX_ITERS without a final answer")
    return None, use_mock

QUERIES = [
    "Should I carry an umbrella in Seattle?",
    "Can you summarize the file notes.txt?",
    "What's the weather in Chandausi?",
]

def main():
    print(f"model: {OLLAMA_MODEL}  (OLLAMA_MODEL to change it)")
    print(f"host:  {OLLAMA_HOST}  (OLLAMA_HOST to change it)")
    print("trying Ollama first; falls back to the mock if it is unavailable\n")
    use_mock = False
    for q in QUERIES:
        print(f"Q: {q}")
        t0 = time.perf_counter()
        _, use_mock = run_agent(q, use_mock)
        # once the fallback triggers, keep it for the rest of the run
        # instead of retrying a dead server per query
        print(f"  ({time.perf_counter() - t0:.1f}s)\n")

if __name__ == "__main__":
    main()
