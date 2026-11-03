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

# ------------------------------------------------ tools (same shape as kata 1)
def get_weather(city: str) -> str:
    return {"Seattle": "rain, 54F", "Chandausi": "clear, 88F"}.get(city, "unknown")

def read_file(path: str) -> str:
    return {"notes.txt": "Buy milk. Dentist moved to 3pm."}.get(path, "unknown")

TOOLS = [
    {"name": "get_weather", "description": "Get current weather for a city",
     "inputSchema": {"type": "object",
                     "properties": {"city": {"type": "string"}},
                     "required": ["city"]}},
    {"name": "read_file", "description": "Read file content from a given path",
     "inputSchema": {"type": "object",
                     "properties": {"path": {"type": "string"}},
                     "required": ["path"]}},
]

def dispatch(name, args):
    if name == "get_weather":
        return get_weather(**args)
    if name == "read_file":
        return read_file(**args)
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
            # NOTE: this is a protocol-level error. Practice task 2 asks
            # whether a tool error should come back this way at all.
            return {"jsonrpc": "2.0", "id": rid,
                    "error": {"code": -32602, "message": str(e)}}
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

    tools = call({"jsonrpc": "2.0", "id": 2, "method": "tools/list"})
    print("-> tools/list:", [t["name"] for t in tools["result"]["tools"]])
    res = call({"jsonrpc": "2.0", "id": 3, "method": "tools/call",
                "params": {"name": "get_weather",
                           "arguments": {"city": "Seattle"}}})
    print("-> tools/call get_weather:", res["result"]["content"])
    res = call({"jsonrpc": "2.0", "id": 4, "method": "tools/call",
                "params": {"name": "read_file",
                           "arguments": {"path": "notes.txt"}}})
    print("-> tools/call read_file:", res["result"]["content"])
    proc.stdin.close()
    proc.wait()

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "server":
        serve()
    else:
        demo_client()
