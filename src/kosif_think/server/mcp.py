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
        "description": "Runs AST parsing, codebase mapping, test running, debugging, regex search, symbols lookup, directory tree, or TDD loop.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "action": {"type": "string", "enum": ["analyze", "repo_map", "test", "debug", "search", "symbols", "tree", "tdd"]},
                "target": {"type": "string", "description": "File path, directory, regex pattern, or spec."}
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
    },
    {
        "name": "think_self_consistency",
        "description": "Samples multiple diverse reasoning trajectories and votes on majority consensus.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "problem": {"type": "string", "description": "The complex problem to evaluate."}
            },
            "required": ["problem"]
        }
    },
    {
        "name": "think_react",
        "description": "Executes iterative Thought-Action-Observation loop with tool execution.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "goal": {"type": "string", "description": "The goal or task to resolve."}
            },
            "required": ["goal"]
        }
    },
    {
        "name": "think_rag_search",
        "description": "Sub-millisecond document ranking and knowledge retrieval using Okapi BM25 and HyDE.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "The query to search knowledge manuals for."}
            },
            "required": ["query"]
        }
    },
    {
        "name": "think_gui_ground",
        "description": "Maps natural language UI instructions onto screen coordinates (x, y) and interactive elements.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "instruction": {"type": "string", "description": "Natural language command, e.g. 'click Save'."}
            },
            "required": ["instruction"]
        }
    },
    {
        "name": "think_guardrails_scan",
        "description": "Scans text for prompt injection exploits and redacts sensitive PII and API credentials.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "text": {"type": "string", "description": "The prompt or output to inspect and clean."}
            },
            "required": ["text"]
        }
    },
    {
        "name": "think_mobile_action",
        "description": "Controls Android (ADB) and iOS smartphones: tap, swipe, launch app, dial call, send SMS, or dump UI elements.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "intent": {"type": "string", "enum": ["tap", "swipe", "launch_app", "dial", "sms", "locate", "home", "back", "type"]},
                "target": {"type": "string", "description": "Target app, phone number, or search query."},
                "value": {"type": "string", "description": "Value or coordinates, e.g. '500,800' or message text."},
                "platform": {"type": "string", "enum": ["android", "ios", "auto"]}
            },
            "required": ["intent"]
        }
    },
    {
        "name": "think_telephony_call",
        "description": "Dispatches phone calls, VoIP/SIP connections, Google Meet/Zoom room links, IVR flows, or Astra live conversational sessions.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "intent": {"type": "string", "enum": ["dial", "hangup", "meeting", "astra_session", "ivr"]},
                "target": {"type": "string", "description": "Phone number or meeting topic."},
                "value": {"type": "string", "description": "Message, prompt, or meeting parameters."}
            },
            "required": ["intent"]
        }
    },
    {
        "name": "think_scientific_research",
        "description": "Searches ArXiv/PubMed academic papers, synthesizes literature reviews, compiles LaTeX documents, or validates statistical p-values.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "intent": {"type": "string", "enum": ["search", "review", "latex", "bibtex", "stats"]},
                "target": {"type": "string", "description": "Search topic, paper title, or DOI."},
                "value": {"type": "string", "description": "Topic or abstract input."}
            },
            "required": ["intent"]
        }
    },
    {
        "name": "think_office_generate",
        "description": "Autonomously generates Microsoft Word (.docx), PowerPoint (.pptx & HTML presentations), and Excel (.xlsx, CSV, financial models, formulas).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "intent": {"type": "string", "enum": ["word", "ppt", "excel", "formula"]},
                "filename": {"type": "string", "description": "Target filename (.docx, .pptx, or .xlsx)."},
                "title": {"type": "string", "description": "Document or presentation title."},
                "value": {"type": "string", "description": "Markdown body, slide content, or formula string."}
            },
            "required": ["intent"]
        }
    },
    {
        "name": "think_open_models_inference",
        "description": "Executes inference via open-source flagship models (DeepSeek-R1, Qwen 2.5 Coder, Llama 3.3, Ollama).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "prompt": {"type": "string", "description": "Instruction or reasoning challenge."},
                "model": {"type": "string", "enum": ["deepseek-r1", "deepseek-r1-distill-qwen-32b", "qwen-2.5-coder-32b", "llama-3.3-70b", "phi-4", "ui-tars-7b"]},
                "system_instruction": {"type": "string", "description": "System role prompt."}
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
    elif name == "think_self_consistency":
        prob = arguments.get("problem", "")
        handler = executor._lane_handlers.get("reasoning")
        if handler:
            from ..core.planner import Step
            return await handler.dispatch_step(Step(step_id=1, lane="reasoning", intent="self_consistency", value=prob))
        return {"error": "Reasoning lane not available"}
    elif name == "think_react":
        goal = arguments.get("goal", "")
        handler = executor._lane_handlers.get("reasoning")
        if handler:
            from ..core.planner import Step
            return await handler.dispatch_step(Step(step_id=1, lane="reasoning", intent="react", value=goal))
        return {"error": "Reasoning lane not available"}
    elif name == "think_rag_search":
        query = arguments.get("query", "")
        handler = executor._lane_handlers.get("reasoning")
        if handler:
            from ..core.planner import Step
            return await handler.dispatch_step(Step(step_id=1, lane="reasoning", intent="rag", value=query))
        return {"error": "Reasoning lane not available"}
    elif name == "think_gui_ground":
        instruction = arguments.get("instruction", "")
        handler = executor._lane_handlers.get("computer")
        if handler:
            from ..core.planner import Step
            return await handler.dispatch_step(Step(step_id=1, lane="computer", intent="ground", value=instruction))
        return {"error": "Computer lane not available"}
    elif name == "think_guardrails_scan":
        text = arguments.get("text", "")
        from ..core.guardrails import GuardrailsSystem
        guard = GuardrailsSystem()
        scan = guard.scan_prompt(text)
        cleaned, pii_count = guard.redact_pii(text)
        return {"scan": scan, "redacted_pii_count": pii_count, "cleaned_text": cleaned}
    elif name == "think_mobile_action":
        handler = executor._lane_handlers.get("mobile")
        if handler:
            from ..core.planner import Step
            intent = arguments.get("intent", "observe")
            val = arguments.get("value")
            target = arguments.get("target")
            return await handler.dispatch_step(Step(step_id=1, lane="mobile", intent=intent, value=val, target=type("T", (), {"ref": target})(), args=arguments))
        return {"error": "Mobile lane not available"}
    elif name == "think_telephony_call":
        handler = executor._lane_handlers.get("telephony")
        if handler:
            from ..core.planner import Step
            intent = arguments.get("intent", "dial")
            val = arguments.get("value")
            target = arguments.get("target")
            return await handler.dispatch_step(Step(step_id=1, lane="telephony", intent=intent, value=val, target=type("T", (), {"ref": target})(), args=arguments))
        return {"error": "Telephony lane not available"}
    elif name == "think_scientific_research":
        handler = executor._lane_handlers.get("research")
        if handler:
            from ..core.planner import Step
            intent = arguments.get("intent", "search")
            val = arguments.get("value")
            target = arguments.get("target")
            return await handler.dispatch_step(Step(step_id=1, lane="research", intent=intent, value=val, target=type("T", (), {"ref": target})(), args=arguments))
        return {"error": "Research lane not available"}
    elif name == "think_office_generate":
        handler = executor._lane_handlers.get("office")
        if handler:
            from ..core.planner import Step
            intent = arguments.get("intent", "word")
            val = arguments.get("value")
            target = arguments.get("filename")
            return await handler.dispatch_step(Step(step_id=1, lane="office", intent=intent, value=val, target=type("T", (), {"ref": target})(), args=arguments))
        return {"error": "Office lane not available"}
    elif name == "think_open_models_inference":
        from ..connectors.open_source_engine import OpenSourceEngine
        engine = OpenSourceEngine()
        prompt = arguments.get("prompt", "")
        model_id = arguments.get("model", "deepseek-r1")
        system_inst = arguments.get("system_instruction")
        return engine.run_inference(prompt, model_id=model_id, system_instruction=system_inst)
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
