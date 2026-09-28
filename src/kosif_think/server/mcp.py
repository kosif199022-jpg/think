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
        "description": "Executes a unified KOSIF Think goal across reasoning, coding, graphics, computer, browser, and WhatsApp lanes.",
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
    },
    {
        "name": "think_tree_of_thoughts",
        "description": "Explores a complex problem using branched Tree of Thoughts (ToT) search with beam pruning.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "problem": {"type": "string", "description": "The complex reasoning problem to explore."}
            },
            "required": ["problem"]
        }
    },
    {
        "name": "think_code_action",
        "description": "Runs AST parsing, codebase mapping, test running, or debugging.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "action": {"type": "string", "enum": ["analyze", "repo_map", "test", "debug"]},
                "target": {"type": "string", "description": "File path, directory, or test command."}
            },
            "required": ["action"]
        }
    },
    {
        "name": "think_render_graphic",
        "description": "Generates Mermaid diagrams, SVG component vectors, or interactive Canvas HTML widgets.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "format": {"type": "string", "enum": ["mermaid", "svg", "canvas"]},
                "title": {"type": "string", "description": "Title or description for the visual asset."}
            },
            "required": ["format"]
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
    elif name == "think_tree_of_thoughts":
        prob = arguments.get("problem", "")
        handler = executor._lane_handlers.get("reasoning")
        if handler:
            return handler.tot.search(prob)
        return {"error": "Reasoning lane not available"}
    elif name == "think_code_action":
        action = arguments.get("action", "analyze")
        target = arguments.get("target", ".")
        handler = executor._lane_handlers.get("coding")
        if handler:
            from ..core.planner import Step
            return await handler.dispatch_step(Step(step_id=1, lane="coding", intent=action, value=target))
        return {"error": "Coding lane not available"}
    elif name == "think_render_graphic":
        fmt = arguments.get("format", "mermaid")
        title = arguments.get("title", "Visual Architecture")
        handler = executor._lane_handlers.get("graphics")
        if handler:
            from ..core.planner import Step
            return await handler.dispatch_step(Step(step_id=1, lane="graphics", intent=fmt, description=title))
        return {"error": "Graphics lane not available"}
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
