#!/usr/bin/env python3
"""
KATA 5 -- Agent skills: knowledge on demand.

Katas 1-4 gave the agent tools (kata 1), a budget (kata 2), a protocol
(kata 3), and a memory (kata 4). What it still lacks is know-how: the
procedures for doing a job well. That is what a skill is.

A skill is a folder with a SKILL.md file:
  --- frontmatter: name + description (what the skill is FOR) ---
  --- body: instructions the model reads WHEN the skill is loaded ---

Three ideas:
  1. DISCOVERY -- the agent only ever sees names + descriptions, like
     tools/list. Descriptions are the routing table (kata 3's lesson).
  2. PROGRESSIVE DISCLOSURE -- the full body loads only when the skill
     is chosen, so twenty skills cost almost nothing until one is used.
     Same instinct as kata 2's compaction: keep context small.
  3. SKILLS ARE KNOWLEDGE, TOOLS ARE CAPABILITY -- a tool runs code; a
     skill tells the model HOW to do the job (which tools, in what order,
     what good looks like).

Run it:  python3 kata_05_skills.py
No API key needed: a keyword router + canned turns stand in for the model.
"""

import os
import string

SKILLS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "skills")

# ------------------------------------------------ token helpers (katas 2-4)
STOP = {"the", "what", "is", "of", "a", "an", "in", "on", "for", "to",
        "and", "or", "my", "i", "you", "do", "does", "should", "can",
        "with", "it", "its", "this", "that"}

def tokens(text):
    out = []
    for w in text.lower().split():
        w = w.strip(string.punctuation)
        if w.endswith("'s"):
            w = w[:-2]
        if w and w not in STOP:
            out.append(w)
    return out

def est_tokens(text):
    return max(1, len(text) // 4)

# ------------------------------------------------ tools (same shape as kata 1)
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

# ------------------------------------------------ the skill registry
def parse_skill_md(path):
    """Return (name, description, body) from a SKILL.md file."""
    with open(path) as f:
        lines = f.read().splitlines()
    assert lines[0].strip() == "---", "SKILL.md must start with frontmatter"
    front = {}
    i = 1
    while i < len(lines) and lines[i].strip() != "---":
        if ":" in lines[i]:
            k, v = lines[i].split(":", 1)
            front[k.strip()] = v.strip()
        i += 1
    body = "\n".join(lines[i + 1:])
    return front.get("name"), front.get("description"), body

class SkillRegistry:
    def __init__(self, root):
        self.skills = []
        for name in sorted(os.listdir(root)):
            md = os.path.join(root, name, "SKILL.md")
            if os.path.isfile(md):
                sname, desc, _ = parse_skill_md(md)
                self.skills.append({"name": sname, "description": desc,
                                    "path": md})

    def match(self, query):
        """Keyword routing, same scorer as katas 3-4. A real agent lets
        the model pick from the descriptions; this stands in for it."""
        qt = set(tokens(query))
        best, best_score = None, 0
        for s in self.skills:
            hay = set(tokens(s["name"] + " " + s["description"]))
            score = len(qt & hay)
            if score > best_score:
                best, best_score = s, score
        return best

    def load(self, skill):
        _, _, body = parse_skill_md(skill["path"])
        return body

# ------------------------------------------------ the "model": canned turns per skill
# A real agent reads the loaded SKILL.md and follows it. Here a canned
# script stands in for the model, keyed by the matched skill's name.
SCRIPTS = {
    "weather-check": [
        {"content": None,
         "tool_calls": [{"name": "get_weather", "args": {"city": "Seattle"}}]},
        {"content": "Yes -- it's raining in Seattle (54F). Carry an umbrella.",
         "tool_calls": []},
    ],
    "file-summary": [
        {"content": None,
         "tool_calls": [{"name": "read_file", "args": {"path": "notes.txt"}}]},
        {"content": "notes.txt says: buy milk; dentist moved to 3pm.",
         "tool_calls": []},
    ],
}

QUERIES = [
    "Should I carry an umbrella in Seattle?",
    "Can you summarize the file notes.txt?",
]

def main():
    reg = SkillRegistry(SKILLS_DIR)
    print(f"registry: {len(reg.skills)} skills discovered "
          f"(descriptions only)")
    desc_tokens = sum(est_tokens(s["name"] + " " + s["description"])
                      for s in reg.skills)
    body_tokens = sum(est_tokens(reg.load(s)) for s in reg.skills)
    print(f"context cost: descriptions only ~{desc_tokens} tokens, "
          f"all skill bodies ~{body_tokens} tokens -- disclosure saves "
          f"~{body_tokens - desc_tokens} tokens until a skill is used")

    for q in QUERIES:
        print(f"\nQ: {q}")
        skill = reg.match(q)
        if not skill:
            print("  no skill matched -- the agent answers from scratch")
            continue
        print(f"  matched skill: {skill['name']} -- {skill['description']}")
        body = reg.load(skill)
        print(f"  loaded SKILL.md ({len(body)} chars):")
        print("  ---")
        for line in body.splitlines():
            print(f"  {line}")
        print("  ---")
        for turn in SCRIPTS[skill["name"]]:
            if turn["tool_calls"]:
                for tc in turn["tool_calls"]:
                    result = dispatch(tc["name"], tc["args"])
                    print(f"  tool [{tc['name']}] -> {result}")
            else:
                print(f"  A: {turn['content']}")

if __name__ == "__main__":
    main()
