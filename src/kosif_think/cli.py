"""
Unified Command-Line Interface for KOSIF Think.
Usage:
    think run "<goal>" [--approved]
    think plan "<goal>"
    think council "<prompt>"
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
from .lanes.computer import ComputerLane
from .lanes.browser import BrowserLane
from .lanes.whatsapp import WhatsAppLane
from .server.api import run_server
from .server.mcp import run_mcp_stdio
from .config import DEFAULT_SERVER_HOST, DEFAULT_SERVER_PORT

def setup_executor() -> ThinkExecutor:
    ex = ThinkExecutor()
    ex.register_lane("reasoning", ReasoningLane())
    ex.register_lane("computer", ComputerLane())
    ex.register_lane("browser", BrowserLane())
    ex.register_lane("whatsapp", WhatsAppLane())
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
        description="🧠 KOSIF Think: Unified orchestration & execution platform."
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

    # Command: status
    subparsers.add_parser("status", help="Inspect platform health, lanes, and recent traces")

    # Command: server
    p_server = subparsers.add_parser("server", help="Launch unified REST/JSON server")
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
            print(f"     Expected: {s.expected_postconditions}")

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

    elif parsed.command == "status":
        print("=" * 60)
        print("🌐 KOSIF Think Platform Health")
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
