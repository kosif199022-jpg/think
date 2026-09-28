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

    # Command: code
    p_code = subparsers.add_parser("code", help="Code intelligence, AST parsing, testing, and debugging")
    p_code.add_argument("action", choices=["analyze", "map", "test", "debug"], help="Coding action")
    p_code.add_argument("target", nargs="?", default=".", help="File path, directory, or test command")

    # Command: graphic
    p_graph = subparsers.add_parser("graphic", help="Synthesize diagrams, SVGs, or Canvas UI")
    p_graph.add_argument("action", choices=["diagram", "svg", "canvas"], help="Graphic asset type")
    p_graph.add_argument("title", nargs="?", default="Architecture Overview", help="Asset title")

    # Command: ios
    p_ios = subparsers.add_parser("ios", help="Control iPhone via Apple Shortcuts, URL schemes, and WDA")
    p_ios.add_argument("action", choices=["app", "speak", "notify", "shortcut", "tap", "home"], help="Action on iPhone")
    p_ios.add_argument("value", nargs="?", default="", help="App name, text to speak, notification text, or shortcut name")

    # Command: status
    subparsers.add_parser("status", help="Inspect platform health, lanes, and recent traces")

    # Command: server
    p_server = subparsers.add_parser("server", help="Launch unified REST/OpenAI/ChatGPT server")
    p_server.add_argument("--host", default=DEFAULT_SERVER_HOST)
    p_server.add_argument("--port", type=int, default=DEFAULT_SERVER_PORT)

    # Command: mcp
    subparsers.add_parser("mcp", help="Run Model Context Protocol (MCP) stdio server")

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

    elif parsed.command == "code":
        c_lane: CodingLane = executor._lane_handlers["coding"]
        from .core.planner import Step
        intent_map = {"analyze": "analyze", "map": "repo_map", "test": "test", "debug": "debug"}
        res = asyncio.run(c_lane.dispatch_step(Step(step_id=1, lane="coding", intent=intent_map[parsed.action], value=parsed.target)))
        print("=" * 60)
        print(f"💻 Coding Lane Result: [{parsed.action.upper()}]")
        print("=" * 60)
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

    elif parsed.command == "status":
        print("=" * 60)
        print("🌐 KOSIF Think Platform Health (7 Autonomous Lanes)")
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
