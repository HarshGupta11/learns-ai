#!/usr/bin/env python3
"""
KATA 3 -- Build an MCP server from scratch (no SDK).

Kata 1's lesson, restated: tools are contracts (a schema) + dispatch.
MCP is that same idea, standardized: any MCP client can discover and call
your tools over JSON-RPC, without knowing your code.

This kata implements a minimal subset of the MCP stdio protocol:
  initialize        -> handshake (protocol version, capabilities, server info)
  tools/list        -> what tools exist (schemas, like kata 1's TOOL_SCHEMAS)
  tools/call        -> run one tool by name, get content blocks back
  notifications/*   -> fire-and-forget, no reply expected

Run the demo:  python3 kata_03_mcp.py
  It spawns itself as the server subprocess and talk s to it as a client.
Run just the server:  python3 kata_03_mcp.py server
  (it reads JSON-RPC from stdin, writes replies to stdout)

This is a teaching subset, not the full spec: the real SDK
(`pip install mcp`) adds types, validation, resources, prompts, and more
transports. The shape you see here is the shape it standardizes.
"""

import json
import sys
from datetime import datetime
import string


FILES = {"notes.txt": "Buy milk. Dentist moved to 3pm."}

# ------------------------------------------------ tools (same shape as kata 1)
def get_weather(city: str) -> str:
    return {"Seattle": "rain, 54F", "Chandausi": "clear, 88F"}.get(city, "unknown")

def read_file(path: str) -> str:
    return FILES.get(path, "unknown")

def get_time() -> str:
    now = datetime.now()
    return now.strftime("%H:%M:%S")

def list_files() -> list[str]:
    return list(FILES.keys())

TOOLS = [
    {"name": "get_weather", "description": "Get current weather for a city",
     "inputSchema": {"type": "object",
                     "properties": {"city": {"type": "string"}},
                     "required": ["city"]}},
    {"name": "read_file", "description": "Read file content from a given path",
     "inputSchema": {"type": "object",
                     "properties": {"path": {"type": "string"}},
                     "required": ["path"]}},
    {
        "name": "get_time", "description" : "Get the current time of the system",
        "inputSchema": {"type": "object",
                        "properties": {},
                        "required": []}},
    {
        "name": "list_files", "description": "Get the list of files on the server",
        "inputSchema": {"type": "object",
                        "properties": {},
                        "required": []}},

]

def dispatch(name, args):
    if name == "get_weather":
        return get_weather(**args)
    if name == "read_file":
        return read_file(**args)
    if name == "get_time":
        return get_time(**args)
    if name == "list_files":
        return list_files(**args)
    raise ValueError(f"unknown tool: {name}")

# ------------------------------------------------ the server: JSON-RPC over stdio
def handle(req):
    method = req.get("method")
    rid = req.get("id")
    if method == "initialize":
        return {"jsonrpc": "2.0", "id": rid, "result": {
            "protocolVersion": "2024-11-05",
            "capabilities": {"tools": {}},
            "serverInfo": {"name": "kata-mcp", "version": "0.1.0"}}}
    if method == "tools/list":
        return {"jsonrpc": "2.0", "id": rid, "result": {"tools": TOOLS}}
    if method == "tools/call":
        params = req.get("params", {})
        try:
            result = dispatch(params.get("name"), params.get("arguments", {}))
        except Exception as e:
            # NOTE: Sending error response in same format as success response
            return {"jsonrpc": "2.0", "id": rid,
                    "result": {"content": [{"type": "text", "text": f"Tool call failed: {e}"}], "isError": True}}
        return {"jsonrpc": "2.0", "id": rid, "result": {
            "content": [{"type": "text", "text": str(result)}],
            "isError": False}}
    if method == "ping":
        return {"jsonrpc": "2.0", "id": rid, "result": {}}
    if rid is None:
        return None  # a notification: no reply, by design
    return {"jsonrpc": "2.0", "id": rid,
            "error": {"code": -32601, "message": f"unknown method: {method}"}}

def serve():
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            req = json.loads(line)
        except json.JSONDecodeError:
            continue
        resp = handle(req)
        if resp is not None:
            sys.stdout.write(json.dumps(resp) + "\n")
            sys.stdout.flush()

# ------------------------------------------------ the demo client

STOP = {"the", "what", "is", "of", "a", "an", "in", "on", "for", "to"}

def tokens(text):
    out = []
    for w in text.lower().split():
        w = w.strip(string.punctuation)
        if w and w not in STOP:
            out.append(w)
    return (' ').join(out)
def pick_tool(query, tools):
    q = tokens(query.lower())
    best, best_score = None, 0
    for t in tools:
        hay = (t["name"] + " " + t["description"]).lower()
        score = sum(1 for word in q.split() if word in hay and len(word) > 2)
        if score > best_score:
            best, best_score = t, score
    return best

def extract_args(tool, query):
    q = tokens(query.lower())
    if tool["name"] == "get_weather":
        for city in ("Seattle", "Chandausi"):
            if city.lower() in q:
                return {"city": city}
        return {"city": "unknown"}
    if tool["name"] == "read_file":
        for word in q.split():
            if word.endswith(".txt"):
                return {"path": word}
        return {"path": "unknown"}
    if tool["name"] == "get_time" or tool["name"] == "list_files":
        return {}

    return {}

def demo_client():
    import subprocess
    proc = subprocess.Popen([sys.executable, __file__, "server"],
                            stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                            text=True)

    def call(req):
        proc.stdin.write(json.dumps(req) + "\n")
        proc.stdin.flush()
        return json.loads(proc.stdout.readline())

    print("-> initialize:",
          json.dumps(call({"jsonrpc": "2.0", "id": 1, "method": "initialize",
                           "params": {"protocolVersion": "2024-11-05",
                                      "capabilities": {},
                                      "clientInfo": {"name": "kata-client",
                                                     "version": "0.1.0"}}}),
                     indent=2)[:300])
    # Notification: no id, so no reply -- the client must NOT wait for one.
    proc.stdin.write(json.dumps({"jsonrpc": "2.0",
                                 "method": "notifications/initialized"}) + "\n")
    proc.stdin.flush()

    query = "What is current time?"
    tools = call({"jsonrpc": "2.0", "id": 2, "method": "tools/list"})
    print("-> tools/list:", [t["name"] for t in tools["result"]["tools"]])
    selected_tool = pick_tool(query, tools["result"]["tools"])
    res = call({"jsonrpc": "2.0", "id": 3, "method": "tools/call",
                "params": {"name": selected_tool["name"],
                           "arguments": extract_args(selected_tool, query)}})
    print(f"-> tools/call {selected_tool["name"]}:", res["result"]["content"])
    proc.stdin.close()
    proc.wait()

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "server":
        serve()
    else:
        demo_client()
