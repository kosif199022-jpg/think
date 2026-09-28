"""
Model Context Protocol (MCP) Server for KOSIF Think.
Exposes KOSIF Think capabilities as standardized MCP tools.
"""

import json
import sys
import asyncio
from typing import Dict, Any, List
from .api import executor

TOOLS_DEFINITION = [
    {
        "name": "think_execute",
        "description": "Executes a unified KOSIF Think goal across reasoning, computer, browser, and WhatsApp lanes.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "goal": {"type": "string", "description": "The natural language instruction or goal."},
                "approved": {"type": "boolean", "description": "Explicit approval for high-risk operations."}
            },
            "required": ["goal"]
        }
    },
    {
        "name": "think_plan",
        "description": "Pre-plans a goal without executing, showing steps, lane assignments, and risk ratings.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "goal": {"type": "string", "description": "The goal to decompose into an execution contract."}
            },
            "required": ["goal"]
        }
    },
    {
        "name": "think_council",
        "description": "Runs multi-agent council deliberation across safety, speed, and architectural personas.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "prompt": {"type": "string", "description": "The problem or question to deliberate."}
            },
            "required": ["prompt"]
        }
    }
]

async def handle_tool_call(name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
    if name == "think_execute":
        goal = arguments.get("goal", "")
        approved = bool(arguments.get("approved", False))
        res = await executor.execute_goal(raw_prompt=goal, approved=approved)
        return {
            "status": res.status,
            "task_id": res.task_id,
            "steps_executed": res.steps_executed,
            "duration_ms": res.duration_ms,
            "output": res.output,
            "checkpoint": res.checkpoint_details
        }
    elif name == "think_plan":
        goal = arguments.get("goal", "")
        req = executor.preflight.run_preflight(goal)
        plan = executor.planner.create_plan(req)
        return {
            "task_id": plan.task_id,
            "goal": plan.goal,
            "steps": [
                {"step_id": s.step_id, "lane": s.lane, "intent": s.intent, "description": s.description, "risk": s.risk_level}
                for s in plan.steps
            ]
        }
    elif name == "think_council":
        prompt = arguments.get("prompt", "")
        handler = executor._lane_handlers.get("reasoning")
        if handler:
            return handler.council.deliberate(prompt, {})
        return {"error": "Reasoning lane not available"}
    return {"error": f"Unknown tool: {name}"}

async def run_mcp_stdio():
    """Runs a standard JSON-RPC 2.0 stdio loop for MCP clients."""
    reader = asyncio.StreamReader()
    protocol = asyncio.StreamReaderProtocol(reader)
    await asyncio.get_event_loop().connect_read_pipe(lambda: protocol, sys.stdin)

    while True:
        line = await reader.readline()
        if not line:
            break
        try:
            req = json.loads(line.decode("utf-8"))
            req_id = req.get("id")
            method = req.get("method")

            if method == "tools/list":
                resp = {"jsonrpc": "2.0", "id": req_id, "result": {"tools": TOOLS_DEFINITION}}
            elif method == "tools/call":
                params = req.get("params", {})
                name = params.get("name")
                args = params.get("arguments", {})
                tool_res = await handle_tool_call(name, args)
                resp = {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {"content": [{"type": "text", "text": json.dumps(tool_res, ensure_ascii=False)}]}
                }
            else:
                resp = {"jsonrpc": "2.0", "id": req_id, "result": {}}

            sys.stdout.write(json.dumps(resp, ensure_ascii=False) + "\n")
            sys.stdout.flush()
        except Exception as e:
            err_resp = {"jsonrpc": "2.0", "error": {"code": -32603, "message": str(e)}}
            sys.stdout.write(json.dumps(err_resp) + "\n")
            sys.stdout.flush()
