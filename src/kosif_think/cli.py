"""
Unified Command-Line Interface for KOSIF Think.
Usage:
    think run "<goal>" [--approved]
    think plan "<goal>"
    think council "<prompt>"
    think tot "<problem>"
    think got "<problem>"
    think reflexion "<action>"
    think mcts "<problem>"
    think dspy "<goal>"
    think agent-graph "<goal>"
    think repo-intel "<query>"
    think code [analyze|map|test|debug] [target]
    think graphic [diagram|svg|canvas] [title]
    think ios [app|speak|notify|shortcut|tap|home] [args...]
    think status
    think server [--host 127.0.0.1] [--port 49400]
    think mcp
"""

import argparse
import asyncio
import json
import sys
from typing import List, Optional

from .core.executor import ThinkExecutor
from .lanes.reasoning import ReasoningLane
from .lanes.coding import CodingLane
from .lanes.graphics import GraphicsLane
from .lanes.computer import ComputerLane
from .lanes.browser import BrowserLane
from .lanes.whatsapp import WhatsAppLane
from .lanes.ios import IOSLane
from .lanes.voice import VoiceLane
from .lanes.mobile import MobileLane
from .lanes.telephony import TelephonyLane
from .lanes.research import ResearchLane
from .lanes.office import OfficeLane
from .connectors.open_source_engine import OpenSourceEngine
from .server.api import run_server
from .server.mcp import run_mcp_stdio
from .config import DEFAULT_SERVER_HOST, DEFAULT_SERVER_PORT

def setup_executor() -> ThinkExecutor:
    ex = ThinkExecutor()
    ex.register_lane("reasoning", ReasoningLane())
    ex.register_lane("coding", CodingLane())
    ex.register_lane("graphics", GraphicsLane())
    ex.register_lane("computer", ComputerLane())
    ex.register_lane("browser", BrowserLane())
    ex.register_lane("whatsapp", WhatsAppLane())
    ex.register_lane("ios", IOSLane())
    ex.register_lane("voice", VoiceLane())
    ex.register_lane("mobile", MobileLane())
    ex.register_lane("telephony", TelephonyLane())
    ex.register_lane("research", ResearchLane())
    ex.register_lane("office", OfficeLane())
    return ex

def main(args: Optional[List[str]] = None):
    # Ensure UTF-8 output on Windows
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

    parser = argparse.ArgumentParser(
        prog="think",
        description="🧠 KOSIF Think: Super-Intelligent Unified Platform for Reasoning, Coding, Graphics, and Multi-Device Automation (including iPhone & ChatGPT)."
    )
    subparsers = parser.add_subparsers(dest="command", help="Available subcommands")

    # Command: run
    p_run = subparsers.add_parser("run", help="Execute a goal through the Think pipeline")
    p_run.add_argument("goal", type=str, help="The goal or instruction to execute")
    p_run.add_argument("--approved", action="store_true", help="Approve high-risk operations")

    # Command: plan
    p_plan = subparsers.add_parser("plan", help="Generate a verified execution plan without running")
    p_plan.add_argument("goal", type=str, help="The goal to inspect and plan")

    # Command: council
    p_council = subparsers.add_parser("council", help="Run multi-agent deliberation on a dilemma")
    p_council.add_argument("prompt", type=str, help="Question or problem space")

    # Command: tot (Tree of Thoughts)
    p_tot = subparsers.add_parser("tot", help="Run Tree of Thoughts (ToT) exploration")
    p_tot.add_argument("problem", type=str, help="Complex reasoning challenge")

    # Command: got (Graph of Thoughts)
    p_got = subparsers.add_parser("got", help="Run Graph of Thoughts (GoT) synthesis")
    p_got.add_argument("problem", type=str, help="Problem requiring non-linear synthesis")

    # Command: reflexion
    p_ref = subparsers.add_parser("reflexion", help="Run verbal self-reflection and extract lessons")
    p_ref.add_argument("action", type=str, help="Action or execution attempt to reflect upon")

    # Command: mcts
    p_mcts = subparsers.add_parser("mcts", help="Run Monte Carlo Tree Search planning")
    p_mcts.add_argument("problem", type=str, help="Decision space state")

    # Command: dspy
    p_dspy = subparsers.add_parser("dspy", help="Run DSPy declarative prompt optimization")
    p_dspy.add_argument("goal", type=str, help="Target task to optimize")

    # Command: agent-graph
    p_ag = subparsers.add_parser("agent-graph", help="Run LangGraph/AutoGen multi-agent cyclic state machine")
    p_ag.add_argument("goal", type=str, help="Multi-agent collaboration objective")

    # Command: repo-intel
    p_ri = subparsers.add_parser("repo-intel", help="Search and ingest open-source architectural patterns from GitHub")
    p_ri.add_argument("query", type=str, help="Framework or architectural pattern to investigate")

    # Command: cove (Chain-of-Verification)
    p_cove = subparsers.add_parser("cove", help="Run Meta Chain-of-Verification (CoVe) 4-step hallucination check")
    p_cove.add_argument("prompt", type=str, help="Claim or task to verify and hallucination-check")

    # Command: coala (CoALA Cognitive Memory)
    p_coala = subparsers.add_parser("coala", help="Query 4-tier CoALA cognitive memory system")
    p_coala.add_argument("query", type=str, help="Goal or query to retrieve memory context for")

    # Command: tournament (LLM-as-a-Verifier Tournament)
    p_tour = subparsers.add_parser("tournament", help="Run LLM-as-a-Verifier pairwise tournament elimination")
    p_tour.add_argument("problem", type=str, help="Problem or objective to select best strategy for")

    # Command: consistency (Self-Consistency & Majority Voting)
    p_cons = subparsers.add_parser("consistency", help="Run Self-Consistency & Majority Voting reasoning")
    p_cons.add_argument("problem", type=str, help="Problem to evaluate across diverse cognitive perspectives")

    # Command: react (Thought-Action-Observation)
    p_react = subparsers.add_parser("react", help="Run autonomous ReAct Thought-Action-Observation loop")
    p_react.add_argument("goal", type=str, help="Goal to resolve via iterative tool actions")

    # Command: rag (Agentic RAG & BM25 Search)
    p_rag = subparsers.add_parser("rag", help="Search platform manuals and knowledge via Okapi BM25 and HyDE")
    p_rag.add_argument("query", type=str, help="Query or question to search")

    # Command: ground (GUI Element Localization)
    p_ground = subparsers.add_parser("ground", help="Ground natural language onto GUI coordinates")
    p_ground.add_argument("instruction", type=str, help="UI instruction (e.g., 'click submit button')")

    # Command: guard (AI Safety Guardrails)
    p_guard = subparsers.add_parser("guard", help="Scan text for prompt injections and redact PII credentials")
    p_guard.add_argument("text", type=str, help="Prompt or text to scan")

    # Command: code
    p_code = subparsers.add_parser("code", help="Code intelligence, AST parsing, grep, tree, TDD, testing, and debugging")
    p_code.add_argument("action", choices=["analyze", "map", "test", "debug", "search", "symbols", "tree", "tdd"], help="Coding action")
    p_code.add_argument("target", nargs="?", default=".", help="File path, directory, regex pattern, or spec")

    # Command: graphic
    p_graph = subparsers.add_parser("graphic", help="Synthesize diagrams, SVGs, or Canvas UI")
    p_graph.add_argument("action", choices=["diagram", "svg", "canvas"], help="Graphic asset type")
    p_graph.add_argument("title", nargs="?", default="Architecture Overview", help="Asset title")

    # Command: ios
    p_ios = subparsers.add_parser("ios", help="Control iPhone via Apple Shortcuts, URL schemes, and WDA")
    p_ios.add_argument("action", choices=["app", "speak", "notify", "shortcut", "tap", "home"], help="Action on iPhone")
    p_ios.add_argument("value", nargs="?", default="", help="App name, text to speak, notification text, or shortcut name")

    # Command: cloud-browser
    p_cb = subparsers.add_parser("cloud-browser", help="Jev Cloud Browser Controller")
    p_cb.add_argument("action", choices=["navigate", "click", "type", "scroll", "auto", "scrape", "view", "state"], help="Browser action")
    p_cb.add_argument("value", nargs="?", default="", help="URL, text to type, or autonomous goal")
    p_cb.add_argument("--selector", default="", help="CSS selector or badge number")
    p_cb.add_argument("--session", default=None, help="Target Cloud session ID")

    # Command: deep-think
    p_dt = subparsers.add_parser("deep-think", help="Long-CoT Deep Deliberation with explicit <think> buffer")
    p_dt.add_argument("problem", help="Problem statement or query to deliberate")

    # Command: symbolic
    p_sym = subparsers.add_parser("symbolic", help="Formal symbolic verification (truth tables, equations, units)")
    p_sym.add_argument("expression", help="Expression or formula to evaluate/solve")
    p_sym.add_argument("--action", choices=["sat", "quadratic", "linear", "convert", "interval"], default="sat")
    p_sym.add_argument("--from-unit", dest="from_unit", default="km", help="Unit to convert from")
    p_sym.add_argument("--to-unit", dest="to_unit", default="m", help="Unit to convert to")

    # Command: voice
    p_voice = subparsers.add_parser("voice", help="Speech synthesis and voice recognition lane")
    p_voice.add_argument("action", choices=["speak", "ssml", "transcribe"], help="Voice action")
    p_voice.add_argument("value", help="Text to speak or audio path")

    # Command: kg
    p_kg = subparsers.add_parser("kg", help="Cognitive Knowledge Graph (GraphRAG)")
    p_kg.add_argument("action", choices=["query", "mermaid", "stats"], help="Action on knowledge graph")
    p_kg.add_argument("entity", nargs="?", default="", help="Entity to query")

    # Command: thought-map
    p_tmap = subparsers.add_parser("thought-map", help="Cognitive Thought Map & Mental Models")
    p_tmap.add_argument("goal", help="Root goal or query to construct thought map for")
    p_tmap.add_argument("--format", choices=["ascii", "mermaid", "html", "json"], default="ascii", help="Output visualization format")

    # Command: status
    subparsers.add_parser("status", help="Inspect platform health, lanes, and recent traces")

    # Command: server
    p_server = subparsers.add_parser("server", help="Launch unified REST/OpenAI/ChatGPT server")
    p_server.add_argument("--host", default=DEFAULT_SERVER_HOST)
    p_server.add_argument("--port", type=int, default=DEFAULT_SERVER_PORT)

    # Command: mcp
    subparsers.add_parser("mcp", help="Run Model Context Protocol (MCP) stdio server")

    # Command: mobile
    p_mobile = subparsers.add_parser("mobile", help="Control Android & iOS smartphone devices")
    p_mobile.add_argument("action", choices=["tap", "swipe", "app", "dial", "sms", "locate", "home", "back", "type", "info"], help="Mobile action")
    p_mobile.add_argument("value", nargs="?", default="", help="Coordinates (x,y), package name, phone number, or text")
    p_mobile.add_argument("--platform", choices=["android", "ios", "auto"], default="auto")

    # Command: call
    p_call = subparsers.add_parser("call", help="Telephony, voice calls, virtual meetings, and Astra voice sessions")
    p_call.add_argument("action", choices=["dial", "hangup", "meeting", "astra", "ivr"], help="Telephony action")
    p_call.add_argument("value", nargs="?", default="", help="Phone number, meeting topic, or speech prompt")
    p_call.add_argument("--provider", default="cellular", choices=["cellular", "sip", "twilio"])

    # Command: research
    p_res = subparsers.add_parser("research", help="Scientific literature search, reviews, LaTeX, citations, and statistics")
    p_res.add_argument("action", choices=["search", "review", "latex", "bibtex", "stats"], help="Research action")
    p_res.add_argument("value", nargs="?", default="", help="Paper topic, title, or formula")
    p_res.add_argument("--limit", type=int, default=5, help="Maximum papers to retrieve")

    # Command: office
    p_off = subparsers.add_parser("office", help="Autonomous Microsoft Word (.docx), PowerPoint (.pptx), and Excel (.xlsx) suite")
    p_off.add_argument("action", choices=["word", "ppt", "excel", "formula", "model"], help="Office document action")
    p_off.add_argument("target", nargs="?", default="", help="Output filename or formula")
    p_off.add_argument("--title", default="Executive Report", help="Document or presentation title")
    p_off.add_argument("--value", default="", help="Markdown body or specific data input")

    # Command: open-models
    p_om = subparsers.add_parser("open-models", help="Open-source AI models hub (DeepSeek-R1, Qwen 2.5, Llama 3.3, Ollama)")
    p_om.add_argument("action", choices=["list", "run", "benchmark", "status"], help="Open-source models action")
    p_om.add_argument("prompt", nargs="?", default="", help="Inference prompt or query")
    p_om.add_argument("--model", default="deepseek-r1", help="Target model identifier")

    parsed = parser.parse_args(args)

    if not parsed.command:
        parser.print_help()
        sys.exit(0)

    executor = setup_executor()

    if parsed.command == "run":
        res = asyncio.run(executor.execute_goal(raw_prompt=parsed.goal, approved=parsed.approved))
        print("=" * 60)
        print(f"🎯 KOSIF Think Result [{res.status.upper()}] (Task ID: {res.task_id})")
        print(f"⏱️ Duration: {res.duration_ms} ms | Steps: {res.steps_executed}")
        print("=" * 60)
        if res.status == "human_checkpoint":
            print(f"🛡️ HUMAN CHECKPOINT REQUIRED:")
            print(f"   {res.checkpoint_details.get('message')}")
        elif res.status == "completed":
            print("✅ Execution completed successfully.")
            if res.output:
                print(json.dumps(res.output, ensure_ascii=False, indent=2))
        else:
            print(f"❌ Execution status: {res.status}. Error: {res.error}")

    elif parsed.command == "plan":
        req = executor.preflight.run_preflight(parsed.goal)
        plan = executor.planner.create_plan(req)
        print("=" * 60)
        print(f"📋 Plan for: '{plan.goal}'")
        print(f"⚠️ Risk Level: {plan.estimated_risk.upper()} | Total Steps: {len(plan.steps)}")
        print("=" * 60)
        for s in plan.steps:
            print(f" [{s.step_id}] Lane: {s.lane:<10} | Intent: {s.intent:<15} | Risk: {s.risk_level}")
            print(f"     Action: {s.description}")

    elif parsed.command == "council":
        r_lane: ReasoningLane = executor._lane_handlers["reasoning"]
        delib = r_lane.council.deliberate(parsed.prompt, {})
        print("=" * 60)
        print("🏛️ KOSIF Council Deliberation")
        print("=" * 60)
        print(delib["deliberation_summary"])
        print("\nPersonas:")
        for op in delib["opinions"]:
            print(f"  • {op['persona']}: {op['recommendation']} (Conf: {op['confidence']})")

    elif parsed.command == "tot":
        r_lane: ReasoningLane = executor._lane_handlers["reasoning"]
        res = r_lane.tot.search(parsed.problem)
        print("=" * 60)
        print(f"🌳 Tree of Thoughts (Score: {res['best_score']} | Explored: {res['total_thoughts_explored']} nodes)")
        print("=" * 60)
        for i, step in enumerate(res["optimal_reasoning_path"], 1):
            print(f"  [{i}] {step}")

    elif parsed.command == "got":
        r_lane: ReasoningLane = executor._lane_handlers["reasoning"]
        res = r_lane.got.solve_graph(parsed.problem)
        print("=" * 60)
        print(f"🕸️ Graph of Thoughts (Vertices: {res['vertex_count']} | Conf: {res['confidence']})")
        print("=" * 60)
        print(f"Execution Order: {' -> '.join(res['topological_order'])}")
        print(f"Consensus: {res['final_consensus']}")

    elif parsed.command == "reflexion":
        r_lane: ReasoningLane = executor._lane_handlers["reasoning"]
        rec = r_lane.reflexion.reflect_on_trial(1, parsed.action, "Execution verified", True, parsed.action)
        print("=" * 60)
        print("🪞 Reflexion Self-Improvement Analysis")
        print("=" * 60)
        print(f"Reflection: {rec.reflection}")
        print(f"Lesson Learned: {rec.lesson_learned}")

    elif parsed.command == "mcts":
        r_lane: ReasoningLane = executor._lane_handlers["reasoning"]
        actions = ["decompose", "formal_verify", "execute_step", "backtrack"]
        res = r_lane.mcts.plan(parsed.problem, actions)
        print("=" * 60)
        print(f"🎲 Monte Carlo Tree Search ({res['simulations_run']} rollouts)")
        print("=" * 60)
        print(f"Optimal Action: {res['best_action']} (Expected Reward: {res['expected_reward']})")

    elif parsed.command == "dspy":
        r_lane: ReasoningLane = executor._lane_handlers["reasoning"]
        from .core.planner import Step
        res = asyncio.run(r_lane.dispatch_step(Step(step_id=1, lane="reasoning", intent="dspy", value=parsed.goal)))
        print("=" * 60)
        print("📐 DSPy Declarative Prompt Optimization")
        print("=" * 60)
        print(json.dumps(res, ensure_ascii=False, indent=2))

    elif parsed.command == "agent-graph":
        r_lane: ReasoningLane = executor._lane_handlers["reasoning"]
        from .core.planner import Step
        res = asyncio.run(r_lane.dispatch_step(Step(step_id=1, lane="reasoning", intent="agent_graph", value=parsed.goal)))
        print("=" * 60)
        print("🕸️ Multi-Agent Cyclic Graph Execution")
        print("=" * 60)
        print(f"Iterations: {res['iterations']} | Approved: {res['approved']}")
        for t in res["turns"]:
            print(f"  • {t.get('agent')}: {t.get('decision') or t.get('action') or t.get('critique')}")

    elif parsed.command == "repo-intel":
        r_lane: ReasoningLane = executor._lane_handlers["reasoning"]
        from .core.planner import Step
        res = asyncio.run(r_lane.dispatch_step(Step(step_id=1, lane="reasoning", intent="repo_intel", value=parsed.query)))
        print("=" * 60)
        print(f"🔍 Open-Source Repository Intelligence: '{parsed.query}'")
        print("=" * 60)
        for r in res.get("matched_repos", []):
            print(f"  ⭐ {r['full_name']} ({r['stars']} stars) - {r['description']}")
        print("\nExtracted Invariants:")
        for p in res.get("extracted_patterns", []):
            print(f"  • {p['repo']}: {p['architecture']['paradigm']}")

    elif parsed.command == "cove":
        r_lane: ReasoningLane = executor._lane_handlers["reasoning"]
        from .core.planner import Step
        res = asyncio.run(r_lane.dispatch_step(Step(step_id=1, lane="reasoning", intent="cove", value=parsed.prompt)))
        print("=" * 60)
        print(f"🔍 Chain-of-Verification (CoVe) Result")
        print("=" * 60)
        print(f"Draft: {res.get('draft_response')}\n")
        print("Verifications:")
        for v in res.get("verifications", []):
            print(f"  • {v['question']}")
            print(f"    -> {v['answer']}")
        print(f"\n{res.get('verified_response')}")

    elif parsed.command == "coala":
        r_lane: ReasoningLane = executor._lane_handlers["reasoning"]
        from .core.planner import Step
        res = asyncio.run(r_lane.dispatch_step(Step(step_id=1, lane="reasoning", intent="coala", value=parsed.query)))
        print("=" * 60)
        print(f"🧠 CoALA 4-Tier Memory Retrieval for: '{parsed.query}'")
        print("=" * 60)
        ctx = res.get("memory_context", {})
        print("Working Memory Focus:", ctx.get("working_memory", {}).get("current_goal"))
        print("\nSemantic Invariants:")
        for k, v in ctx.get("relevant_semantics", {}).items():
            print(f"  • {k}: {v}")
        print("\nMatched Procedural Skills:")
        for k, v in ctx.get("matched_procedures", {}).items():
            print(f"  • {k}: {v.get('steps')}")

    elif parsed.command == "tournament":
        r_lane: ReasoningLane = executor._lane_handlers["reasoning"]
        from .core.planner import Step
        res = asyncio.run(r_lane.dispatch_step(Step(step_id=1, lane="reasoning", intent="tournament", value=parsed.problem)))
        print("=" * 60)
        print(f"🏆 LLM Tournament Verifier Winner: {res.get('winner_id')}")
        print("=" * 60)
        print(f"Title: {res.get('winner_title')}")
        print(f"Confidence Score: {res.get('winner_score')}")
        print(f"Execution Steps: {res.get('recommended_steps')}")
        print("\nTournament Matches:")
        for m in res.get("matches", []):
            print(f"  • [{m['round']}] {m['match']} -> Winner: {m['winner']}")

    elif parsed.command == "consistency":
        r_lane: ReasoningLane = executor._lane_handlers["reasoning"]
        from .core.planner import Step
        res = asyncio.run(r_lane.dispatch_step(Step(step_id=1, lane="reasoning", intent="self_consistency", value=parsed.problem)))
        print("=" * 60)
        print("🗳️ Self-Consistency & Majority Voting Reasoning")
        print("=" * 60)
        print(f"Majority Conclusion: {res.get('majority_conclusion')}")
        print(f"Consensus Ratio: {int(res.get('consensus_ratio', 0) * 100)}% | Entropy: {res.get('entropy')}")
        print(f"Vote Distribution: {res.get('vote_distribution')}")
        print("\nReasoning Rollouts:")
        for r in res.get("rollouts", []):
            print(f"  • [{r['perspective']}] -> {r['conclusion']} (Conf: {r['confidence']})")

    elif parsed.command == "react":
        r_lane: ReasoningLane = executor._lane_handlers["reasoning"]
        from .core.planner import Step
        res = asyncio.run(r_lane.dispatch_step(Step(step_id=1, lane="reasoning", intent="react", value=parsed.goal)))
        print("=" * 60)
        print("🔄 ReAct (Thought-Action-Observation) Trajectory")
        print("=" * 60)
        for s in res.get("trajectory", []):
            print(f"Step {s['step']}:")
            print(f"  🧠 Thought: {s['thought']}")
            if s.get("action"):
                print(f"  ⚡ Action: {s['action']}")
                print(f"  👁️ Obs:    {s['observation']}")
        print(f"\n{res.get('final_answer')}")

    elif parsed.command == "rag":
        r_lane: ReasoningLane = executor._lane_handlers["reasoning"]
        from .core.planner import Step
        res = asyncio.run(r_lane.dispatch_step(Step(step_id=1, lane="reasoning", intent="rag", value=parsed.query)))
        print("=" * 60)
        print(f"📚 Agentic RAG & Okapi BM25 Search: '{parsed.query}'")
        print("=" * 60)
        print(f"Matches Found: {res.get('matches_count')} (Top-K: {res.get('top_k')})")
        for m in res.get("results", []):
            print(f"  • [{m['score']}] {m['title']}: {m['snippet']}")

    elif parsed.command == "ground":
        c_lane: ComputerLane = executor._lane_handlers["computer"]
        from .core.planner import Step
        res = asyncio.run(c_lane.dispatch_step(Step(step_id=1, lane="computer", intent="ground", value=parsed.instruction)))
        print("=" * 60)
        print(f"🎯 Multimodal GUI Element Grounding: '{parsed.instruction}'")
        print("=" * 60)
        if res.get("status") == "grounded":
            coords = res.get("target_coordinates", {})
            elem = res.get("element", {})
            print(f"Action: {res.get('action').upper()} at ({coords.get('x')}, {coords.get('y')})")
            print(f"Confidence: {int(res.get('confidence', 0) * 100)}%")
            print(f"Target Element: [{elem.get('role')}] '{elem.get('text')}' (ID: {elem.get('element_id')})")
        else:
            print("Status: Element not found or below confidence threshold.")

    elif parsed.command == "guard":
        from .core.guardrails import GuardrailsSystem
        guard = GuardrailsSystem()
        scan = guard.scan_prompt(parsed.text)
        cleaned, pii_count = guard.redact_pii(parsed.text)
        print("=" * 60)
        print("🛡️ AI Safety Guardrails & PII Inspection")
        print("=" * 60)
        print(f"Safe: {scan.get('is_safe')} | Risk Level: {scan.get('risk_level').upper()}")
        print(f"Detected Injections: {scan.get('detected_patterns')}")
        print(f"PII Redactions: {pii_count}")
        print(f"\nGuarded Output:\n{cleaned}")

    elif parsed.command == "code":
        c_lane: CodingLane = executor._lane_handlers["coding"]
        from .core.planner import Step
        intent_map = {
            "analyze": "analyze",
            "map": "repo_map",
            "test": "test",
            "debug": "debug",
            "search": "search",
            "symbols": "symbols",
            "tree": "tree",
            "tdd": "tdd"
        }
        res = asyncio.run(c_lane.dispatch_step(Step(step_id=1, lane="coding", intent=intent_map[parsed.action], value=parsed.target)))
        print("=" * 60)
        print(f"💻 Coding Lane Result: [{parsed.action.upper()}]")
        print("=" * 60)
        if parsed.action == "tree" and "tree" in res:
            print(res["tree"])
        else:
            print(json.dumps(res, ensure_ascii=False, indent=2))

    elif parsed.command == "graphic":
        g_lane: GraphicsLane = executor._lane_handlers["graphics"]
        from .core.planner import Step
        res = asyncio.run(g_lane.dispatch_step(Step(step_id=1, lane="graphics", intent=parsed.action, description=parsed.title)))
        print("=" * 60)
        print(f"🎨 Graphics Lane Result: [{parsed.action.upper()}]")
        print("=" * 60)
        if "diagram" in res:
            print(res["diagram"])
        elif "svg" in res:
            print(f"Generated SVG markup ({len(res['svg'])} characters)")
        elif "html" in res:
            print(f"Generated HTML5/Canvas widget ({len(res['html'])} characters)")

    elif parsed.command == "ios":
        i_lane: IOSLane = executor._lane_handlers["ios"]
        from .core.planner import Step
        intent_map = {
            "app": "open_app",
            "speak": "speak",
            "notify": "notify",
            "shortcut": "shortcut",
            "tap": "tap",
            "home": "home"
        }
        res = asyncio.run(i_lane.dispatch_step(Step(step_id=1, lane="ios", intent=intent_map[parsed.action], value=parsed.value, target=None)))
        print("=" * 60)
        print(f"📱 iPhone Control Result: [{parsed.action.upper()}]")
        print("=" * 60)
        print(json.dumps(res, ensure_ascii=False, indent=2))

    elif parsed.command == "cloud-browser":
        b_lane: BrowserLane = executor._lane_handlers["browser"]
        from .core.planner import Step
        action_intent_map = {
            "navigate": "cloud_navigate",
            "click": "cloud_click",
            "type": "cloud_type",
            "scroll": "cloud_scroll",
            "auto": "jev_goal",
            "scrape": "cloud_scrape",
            "state": "cloud_state",
            "view": "cloud_view",
        }
        intent = action_intent_map.get(parsed.action, "cloud_navigate")
        step_args = {
            "url": parsed.value if parsed.action == "navigate" else None,
            "selector": parsed.selector or (parsed.value if parsed.action == "click" else None),
            "text": parsed.value if parsed.action == "type" else None,
            "goal": parsed.value if parsed.action == "auto" else None,
            "session_id": parsed.session,
        }
        res = asyncio.run(b_lane.dispatch_step(Step(step_id=1, lane="browser", intent=intent, value=parsed.value, args=step_args)))
        print("=" * 60)
        print(f"☁️ Jev Cloud Browser Action: [{parsed.action.upper()}]")
        print("=" * 60)
        print(json.dumps(res, ensure_ascii=False, indent=2))

    elif parsed.command == "deep-think":
        r_lane: ReasoningLane = executor._lane_handlers["reasoning"]
        delib = r_lane.deep_think.deliberate(parsed.problem)
        print("=" * 60)
        print(f"🧠 Long-CoT Deep Thinking Deliberation")
        print("=" * 60)
        print(f"Deliberation Time: {delib.deliberation_time_ms} ms | Self-Corrections: {delib.self_correction_count} | Confidence: {delib.confidence_score}")
        print("\n" + "=" * 30 + " <think> " + "=" * 30)
        print(delib.think_trace)
        print("=" * 30 + " </think> " + "=" * 29)
        print(f"\n💡 Final Solution:\n{delib.final_solution}")

    elif parsed.command == "symbolic":
        r_lane: ReasoningLane = executor._lane_handlers["reasoning"]
        print("=" * 60)
        print(f"🔬 Formal Symbolic Verifier: [{parsed.action.upper()}]")
        print("=" * 60)
        if parsed.action == "sat":
            res = r_lane.symbolic.verify_proposition(parsed.expression)
            print(f"Formula: {res.formula}")
            print(f"Satisfiable: {'✅ YES' if res.satisfiable else '❌ NO'} | Tautology: {'✅ YES' if res.tautology else '❌ NO'}")
            print(f"Variables: {res.variables}")
            print(f"Satisfying Assignments: {len(res.satisfying_assignments)}")
        elif parsed.action == "quadratic":
            import re
            nums = [float(x) for x in re.findall(r"[-+]?\d*\.?\d+", parsed.expression)]
            if len(nums) >= 3:
                a, b, c = nums[0], nums[1], nums[2]
                sol = r_lane.symbolic.solve_quadratic(a, b, c)
                print(f"Equation: {a}x² + {b}x + {c} = 0")
                print(f"Discriminant: {sol.discriminant} | Roots: {sol.roots} | Type: {sol.nature}")
            else:
                print("Error: Please provide 3 coefficients: 'a b c' or 'ax^2 + bx + c = 0'")
        elif parsed.action == "linear":
            import re
            nums = [float(x) for x in re.findall(r"[-+]?\d*\.?\d+", parsed.expression)]
            if len(nums) >= 2:
                a, b = nums[0], nums[1]
                sol = r_lane.symbolic.solve_linear(a, b)
                print(f"Equation: {a}x + {b} = 0 -> Solution: {sol}")
            else:
                print("Error: Please provide 2 coefficients: 'a b'")
        elif parsed.action == "convert":
            import re
            nums = [float(x) for x in re.findall(r"[-+]?\d*\.?\d+", parsed.expression)]
            val = nums[0] if nums else 1.0
            conv = r_lane.symbolic.convert_units(val, parsed.from_unit, parsed.to_unit)
            print(f"Converted: {val} {parsed.from_unit} = {conv} {parsed.to_unit}")
        elif parsed.action == "interval":
            print(f"Interval analysis for: {parsed.expression}")

    elif parsed.command == "voice":
        v_lane: VoiceLane = executor._lane_handlers["voice"]
        from .core.planner import Step
        intent_map = {"speak": "speak", "ssml": "to_ssml", "transcribe": "transcribe"}
        res = asyncio.run(v_lane.dispatch_step(Step(step_id=1, lane="voice", intent=intent_map[parsed.action], value=parsed.value)))
        print("=" * 60)
        print(f"🎙️ Voice Lane Result: [{parsed.action.upper()}]")
        print("=" * 60)
        print(json.dumps(res, ensure_ascii=False, indent=2))

    elif parsed.command == "kg":
        from .core.knowledge_graph import CognitiveKnowledgeGraph
        kg = CognitiveKnowledgeGraph()
        kg.add_triple("kosif_think", "implements", "Long-CoT Deep Thinking")
        kg.add_triple("kosif_think", "implements", "Jev Cloud Browser")
        kg.add_triple("kosif_think", "implements", "Symbolic Verifier")
        kg.add_triple("kosif_think", "implements", "Voice Lane")
        kg.add_triple("Jev Cloud Browser", "provides", "Virtual Canvas Streaming")
        kg.add_triple("Jev Cloud Browser", "provides", "Stealth Anti-Bot Evasion")
        kg.add_triple("Deep Thinking", "features", "Deliberation <think> Buffer")
        kg.add_triple("Deep Thinking", "features", "Backtracking & Hypothesis Branching")
        print("=" * 60)
        print(f"🌐 Cognitive Knowledge Graph (GraphRAG): [{parsed.action.upper()}]")
        print("=" * 60)
        if parsed.action == "mermaid":
            print(kg.to_mermaid())
        elif parsed.action == "stats":
            print(f"Total Triples: {len(kg.triples)}")
            print(f"Total Entities: {len(kg.entities)}")
            for ent in sorted(kg.entities):
                print(f"  • {ent}")
        elif parsed.action == "query":
            target = parsed.entity or "kosif_think"
            subgraph = kg.get_ego_graph(target, hops=2)
            print(f"Ego-Graph for '{target}' ({len(subgraph)} triples):")
            for t in subgraph:
                print(f"  • {t['subject']} --[{t['predicate']}]--> {t['object']}")

    elif parsed.command == "thought-map":
        r_lane: ReasoningLane = executor._lane_handlers["reasoning"]
        from .core.planner import Step
        res = asyncio.run(r_lane.dispatch_step(Step(step_id=1, lane="reasoning", intent="thought_map", value=parsed.goal)))
        print("=" * 60)
        print(f"🧠 Cognitive Thought Map: '{parsed.goal}'")
        print("=" * 60)
        if parsed.format == "mermaid":
            print(res["mermaid"])
        elif parsed.format == "html":
            print(f"Generated Interactive HTML5 Canvas widget ({len(res['interactive_html'])} bytes)")
            out_file = "thought_map.html"
            with open(out_file, "w", encoding="utf-8") as f:
                f.write(res["interactive_html"])
            print(f"Saved interactive map to: {out_file}")
        elif parsed.format == "json":
            print(json.dumps(res, ensure_ascii=False, indent=2))
        else:
            print(res["ascii_tree"])
            print(f"\nCritical Reasoning Path ({len(res['critical_path'])} hops):")
            for step in res["critical_path"]:
                print(f"  ➜ [{step['category'].upper()}] {step['label']} ({int(step['belief']*100)}% belief)")

    elif parsed.command == "mobile":
        m_lane: MobileLane = executor._lane_handlers["mobile"]
        from .core.planner import Step
        intent_map = {"app": "launch_app", "tap": "tap", "swipe": "swipe", "dial": "dial", "sms": "sms", "locate": "locate", "home": "home", "back": "back", "type": "type", "info": "info"}
        intent = intent_map.get(parsed.action, parsed.action)
        step = Step(step_id=1, lane="mobile", intent=intent, value=parsed.value, args={"platform": parsed.platform})
        res = asyncio.run(m_lane.dispatch_step(step))
        print("=" * 60)
        print(f"📱 Mobile Lane Action: [{parsed.action.upper()}] ({parsed.platform})")
        print("=" * 60)
        print(json.dumps(res, ensure_ascii=False, indent=2))

    elif parsed.command == "call":
        t_lane: TelephonyLane = executor._lane_handlers["telephony"]
        from .core.planner import Step
        intent_map = {"dial": "dial", "hangup": "hangup", "meeting": "meeting", "astra": "astra_session", "ivr": "ivr"}
        intent = intent_map.get(parsed.action, parsed.action)
        step = Step(step_id=1, lane="telephony", intent=intent, value=parsed.value, args={"provider": parsed.provider})
        res = asyncio.run(t_lane.dispatch_step(step))
        print("=" * 60)
        print(f"📞 Telephony Lane Result: [{parsed.action.upper()}]")
        print("=" * 60)
        print(json.dumps(res, ensure_ascii=False, indent=2))

    elif parsed.command == "research":
        r_lane: ResearchLane = executor._lane_handlers["research"]
        from .core.planner import Step
        intent = parsed.action
        step = Step(step_id=1, lane="research", intent=intent, value=parsed.value, args={"limit": parsed.limit})
        res = asyncio.run(r_lane.dispatch_step(step))
        print("=" * 60)
        print(f"🔬 Scientific Research Lane: [{parsed.action.upper()}]")
        print("=" * 60)
        if parsed.action == "review":
            print(res.get("markdown_review", json.dumps(res, ensure_ascii=False, indent=2)))
        elif parsed.action == "latex":
            print(res.get("latex_code", ""))
        else:
            print(json.dumps(res, ensure_ascii=False, indent=2))

    elif parsed.command == "office":
        o_lane: OfficeLane = executor._lane_handlers["office"]
        from .core.planner import Step
        intent_map = {"word": "word", "ppt": "ppt", "excel": "excel", "formula": "formula", "model": "excel"}
        intent = intent_map.get(parsed.action, parsed.action)
        step = Step(step_id=1, lane="office", intent=intent, target=type("T", (), {"ref": parsed.target})(), value=parsed.value, args={"title": parsed.title})
        res = asyncio.run(o_lane.dispatch_step(step))
        print("=" * 60)
        print(f"📄 Office Suite Lane: [{parsed.action.upper()}]")
        print("=" * 60)
        print(json.dumps(res, ensure_ascii=False, indent=2))

    elif parsed.command == "open-models":
        engine = OpenSourceEngine()
        print("=" * 60)
        print(f"🌐 Open-Source AI Models Hub: [{parsed.action.upper()}]")
        print("=" * 60)
        if parsed.action == "list":
            for m in engine.list_models():
                print(f"  • {m['name']} ({m['family']} {m['parameters']}) - Domain: {m['domain']}")
                print(f"    Benchmarks: {m['benchmarks']}")
        elif parsed.action == "status":
            st = engine.check_ollama_status()
            print(f"Local Ollama Status: {'🟢 ONLINE' if st.get('online') else '🔴 OFFLINE'}")
            print(f"Base URL: {st.get('base_url')}")
            if st.get('installed_models'):
                print(f"Installed Models: {', '.join(st['installed_models'])}")
        elif parsed.action == "benchmark":
            print(f"{'Model':<30} | {'Domain':<20} | {'Benchmarks'}")
            print("-" * 75)
            for m in engine.list_models():
                bm = ", ".join([f"{k}: {v}" for k, v in m['benchmarks'].items()])
                print(f"{m['name']:<30} | {m['domain']:<20} | {bm}")
        else:
            res = engine.run_inference(parsed.prompt or "Analyze distributed agentic consensus", model_id=parsed.model)
            print(f"Engine: {res['engine']} | Model: {res['model']} | Latency: {res['duration_ms']}ms")
            if res.get("think_buffer"):
                print("\n<think>\n" + res["think_buffer"] + "\n</think>\n")
            print(res["response"])

    elif parsed.command == "status":
        print("=" * 60)
        print("🌐 KOSIF Think Platform Health (12 Autonomous Lanes)")
        print("=" * 60)
        for lane, metrics in executor.router._lane_health.items():
            st = "🟢 Active" if metrics.get("available") and not metrics.get("circuit_open") else "🔴 Degraded"
            print(f"  • {lane:<12}: {st} (Latency: {metrics.get('latency_ms', 0):.1f}ms)")
        events = executor.audit.get_recent_events(limit=5)
        print(f"\nRecent Audit Events ({len(events)}):")
        for ev in events:
            print(f"  [{ev.get('iso_time')}] {ev.get('event')} ({ev.get('lane')}) -> {ev.get('status')}")

    elif parsed.command == "server":
        run_server(host=parsed.host, port=parsed.port)

    elif parsed.command == "mcp":
        asyncio.run(run_mcp_stdio())

if __name__ == "__main__":
    main()
