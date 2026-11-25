#!/usr/bin/env python3
"""
KATA 4 -- Memory systems: remember across sessions.

Kata 2's lesson, restated: notes live outside the transcript and survive
compaction. But they died with the process. This kata makes them durable:
a memory store that is written to disk, reloaded next run, and searched
by relevance instead of dumped wholesale into context.

Three ideas:
  1. STORE    -- memories are records (text, kind, timestamp), not transcript.
  2. RETRIEVE -- a query scores memories by token overlap; only the top-k
     enter the model's context. Keyword scoring, with kata 3's fix applied:
     strip punctuation, drop stop words.
  3. FORGET   -- a store that only grows eventually drowns retrieval. Score
     in recency, prune what never gets used. (Practice task.)

Run it:  python3 kata_04_memory.py
No API key needed: mock model + keyword retrieval.

memories.json is runtime data, not kata code -- add it to .gitignore if
you commit the kata.
"""

import json
import os
import string
import time

# ------------------------------------------------ token normalization (kata 3's fix)
STOP = {"the", "what", "is", "of", "a", "an", "in", "on", "for", "to",
        "and", "or", "my", "i", "you", "do", "does", "should", "can",
        "with", "it", "its", "this", "that"}
MAX_MEMORY_SIZE = 5
KIND_WEIGHT = {"preference": 2, "fact": 1}

def tokens(text):
    out = []
    for w in text.lower().split():
        w = w.strip(string.punctuation)
        if w.endswith("'s"):
            w = w[:-2]
        if w and w not in STOP:
            out.append(w)
    return out

# ------------------------------------------------ the store
class MemoryStore:

    def __init__(self, path):
        self.path = path
        self.memories = []
        self._next_id = 1
        if os.path.exists(path):
            self.load()

    def add(self, text, kind="fact"):
        m = {"id": self._next_id, "text": text, "kind": kind, "ts": time.time()}
        self._next_id += 1
        self.memories.append(m)
        self.prune()
        return m

    def search(self, query, k=3):
        qt = set(tokens(query))
        scored = []
        old_memories = []
        refreshed_memories = []
        for m in self.memories:
            overlap = len(qt & set(tokens(m["text"])))
            if overlap:
                scored.append((overlap, m))
                refreshed_memories.append(m)
            else:
                old_memories.append(m)
        self.memories = old_memories + refreshed_memories
        scored.sort(key=lambda s: s[0], reverse=True)

        search_results = [m for _, m in scored[:k]]
        return search_results

    def save(self):
        with open(self.path, "w") as f:
            json.dump({"next_id": self._next_id, "memories": self.memories},
                      f, indent=2)

    def load(self):
        with open(self.path) as f:
            data = json.load(f)
        self.memories = data["memories"]
        self._next_id = data["next_id"]

    def prune(self):
        if(len(self.memories) > MAX_MEMORY_SIZE) :
            lowest = min(KIND_WEIGHT.get(m["kind"], 1) for m in self.memories)
            for i, m in enumerate(self.memories):
                if KIND_WEIGHT.get(m["kind"], 1) == lowest:
                    self.memories.pop(i)
                    break


# ------------------------------------------------ the "brain": answer from recalled memories
def answer(hits):
    if not hits:
        return "I don't know -- I'd have to ask."
    facts = "; ".join(f"{h['text']} [{h['kind']}]" for h in hits)
    return f"Based on what I remember: {facts}."

# ------------------------------------------------ demo: two sessions
STORE_PATH = "memories.json"

SEED = [
    ("Sam is vegetarian", "preference"),
    ("Sam likes spicy food", "preference"),
    ("Sam prefers morning meetings", "preference"),
    ("Sam's cat is named Miso", "fact"),
    ("Sam's hometown is Pune", "fact"),
    ("The France's capital is Paris", "fact"),
]

QUERIES = [
    "What food should I suggest for Sam?",
    "When should I schedule the morning review with Sam?",
    "What is Sam's cat called?",
    "What is the capital of France?"
]

def main():
    # ---- session A: learn (seed only if the store is empty) ----
    store = MemoryStore(STORE_PATH)
    if not store.memories:
        for text, kind in SEED:
            store.add(text, kind)
        store.save()
        print(f"session A: stored {len(store.memories)} memories -> {STORE_PATH}")
    else:
        print(f"session A: store already has {len(store.memories)} memories, "
              f"not re-seeding")

    # ---- session B: a later session. A new store object loaded from disk --
    # in a real system this would be a separate process; a fresh object
    # loaded from the same file is the same test.
    store2 = MemoryStore(STORE_PATH)
    print(f"session B: loaded {len(store2.memories)} memories from disk")
    for q in QUERIES:
        print(f"\nQ: {q}")
        hits = store2.search(q)
        for h in hits:
            print(f"  recalled [{h['kind']}]: {h['text']}")
        print(f"  A: {answer(hits)}")

if __name__ == "__main__":
    main()
