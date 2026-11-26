#!/usr/bin/env python3
"""
KATA 6 -- Evals harness: test the agent like software.

Katas 1-5 built an agent (loop, context, protocol, memory, skills).
Nothing so far checks whether it actually works. That is what evals
are: a test suite for the agent, the same way unit tests are a test
suite for code -- your kata 5 transfer challenge (TDD) applied to the
agent itself.

Three ideas:
  1. CASES ARE DATA, NOT CODE -- each test is a dict: a query, the
     tools the agent should call, words the answer must contain, and
     words it must not. Adding a test means adding a dict; the
     harness never changes.
  2. SCORERS ARE SMALL, DETERMINISTIC CHECKS -- exact tool sequence,
     keyword containment, keyword absence (the no-fabrication check).
     Deterministic beats vibes: a check either passes or it doesn't,
     and it costs nothing to run. LLM-as-judge (a model grading the
     answer) is a later layer -- it needs a real model, which is
     kata 7.
  3. RUNS ARE COMPARABLE -- results are saved to eval_results.json
     (same instinct as kata 4's persistence: state on disk across
     runs). Each run diffs against the last one, so a case that used
     to pass and now fails is flagged as a REGRESSION automatically.

Run it:  python3 kata_06_evals.py
Run it twice: the second run compares against the first. Then break
the agent on purpose (practice task 2) and run again -- the harness
catches it. No API key needed: the agent is a keyword router, like
kata 5's matcher, standing in for the model.
"""

import json
import os

RESULTS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                            "eval_results.json")

# ------------------------------------------------ tools (same fake stores as kata 1)
def get_weather(city: str) -> str:
    return {"Seattle": "rain, 54F", "Chandausi": "clear, 88F"}.get(city, "unknown")

def read_file(path: str) -> str:
    return {"notes.txt": "Buy milk. Dentist moved to 3pm."}.get(path, "unknown")

# ------------------------------------------------ the agent under test
def run_agent(query):
    """Keyword router standing in for the model. Returns (answer,
    tools_called in order)."""
    q = query.lower()
    if any(w in q for w in ("weather", "umbrella", "rain")):
        city = "Seattle" if "seattle" in q else "Chandausi"
        result = get_weather(city)
        if "rain" in result:
            return f"{city}: {result}. Carry an umbrella.", ["get_weather"]
        return f"{city}: {result}. No umbrella needed.", ["get_weather"]
    if any(w in q for w in ("file", "summarize", "notes", ".txt", ".pdf")):
        path = "notes.txt" if "notes.txt" in q else "report.pdf"
        result = read_file(path)
        if result == "unknown":
            return f"I don't know what's in {path}.", ["read_file"]
        return f"{path} says: {result}", ["read_file"]
    return "I don't know.", []

# ------------------------------------------------ eval cases: data, not code
CASES = [
    {"name": "weather-seattle",
     "query": "Should I carry an umbrella in Seattle?",
     "expect_tools": ["get_weather"],
     "expect_contains": ["rain", "umbrella"],
     "expect_absent": ["Chandausi"]},
    {"name": "weather-chandausi",
     "query": "What's the weather in Chandausi?",
     "expect_tools": ["get_weather"],
     "expect_contains": ["clear", "88F"],
     "expect_absent": ["rain"]},
    {"name": "weather-default-city",
     "query": "What's the weather like?",
     "expect_tools": ["get_weather"],
     "expect_contains": ["Chandausi", "clear"],
     "expect_absent": ["Seattle", "rain"]},
    {"name": "file-summary",
     "query": "Can you summarize the file notes.txt?",
     "expect_tools": ["read_file"],
     "expect_contains": ["milk", "dentist"],
     "expect_absent": ["unknown"]},
    {"name": "unknown-file",
     "query": "What's in report.pdf?",
     "expect_tools": ["read_file"],
     "expect_contains": ["don't know"],
     "expect_absent": ["milk"]},
    {"name": "no-tool-question",
     "query": "Tell me a joke",
     "expect_tools": [],
     "expect_contains": ["don't know"],
     "expect_absent": ["rain", "milk"]},
]

# ------------------------------------------------ scorers: small, deterministic
def check_tools(actual, expected):
    return actual == expected, actual

def check_contains(answer, keywords):
    missing = [k for k in keywords if k.lower() not in answer.lower()]
    return not missing, missing

def check_absent(answer, banned):
    present = [b for b in banned if b.lower() in answer.lower()]
    return not present, present

# ------------------------------------------------ runner
def run_case(case):
    answer, tools = run_agent(case["query"])
    checks = {}
    checks["tools"] = check_tools(tools, case["expect_tools"])
    checks["contains"] = check_contains(answer, case["expect_contains"])
    checks["absent"] = check_absent(answer, case.get("expect_absent", []))
    return answer, tools, checks

def load_previous():
    if os.path.isfile(RESULTS_FILE):
        with open(RESULTS_FILE) as f:
            return json.load(f)
    return {}

def main():
    results = {}
    passed = 0
    for case in CASES:
        answer, tools, checks = run_case(case)
        ok = all(v[0] for v in checks.values())
        results[case["name"]] = "pass" if ok else "fail"
        passed += ok
        print(f"[{'PASS' if ok else 'FAIL'}] {case['name']}: {answer}")
        if not checks["tools"][0]:
            print(f"       tools: expected {case['expect_tools']}, "
                  f"got {checks['tools'][1]}")
        if not checks["contains"][0]:
            print(f"       contains: missing {checks['contains'][1]}")
        if not checks["absent"][0]:
            print(f"       absent: found {checks['absent'][1]} (must not appear)")

    print(f"\n{passed}/{len(CASES)} passed")
    prev = load_previous()
    for name, status in results.items():
        if name not in prev:
            print(f"  NEW: {name} ({status})")
        elif prev[name] == "pass" and status == "fail":
            print(f"  REGRESSION: {name} passed before, fails now")
        elif prev[name] == "fail" and status == "pass":
            print(f"  FIXED: {name} failed before, passes now")
    with open(RESULTS_FILE, "w") as f:
        json.dump(results, f, indent=2)
    print(f"results saved to {RESULTS_FILE} -- add it to .gitignore, "
          f"like kata 4's memories.json")

if __name__ == "__main__":
    main()
