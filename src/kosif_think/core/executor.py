"""
Think Executor: Core orchestrator implementing the complete KOSIF Think pipeline:
User request -> preflight -> planner -> router -> risk gate -> lane executor -> verifier -> recovery/trace -> final result.
"""

import time
import logging
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional

from .preflight import PreflightGate, SanitizedRequest
from .planner import TaskPlanner, Plan, Step
from .router import CapabilityRouter
from .risk_gate import RiskGate, RiskLevel, CheckpointRequired
from .verifier import ObservableVerifier, VerificationResult
from .recovery import RecoveryEngine, CircuitBreaker
from .cancellation import CancellationToken, OperationCancelledException
from .audit import AuditLogger
from .memory import MemoryEngine

logger = logging.getLogger("kosif_think.executor")

@dataclass
class ExecutionResult:
    task_id: str
    goal: str
    status: str  # completed, human_checkpoint, cancelled, failed
    steps_executed: int
    duration_ms: float
    output: Dict[str, Any] = field(default_factory=dict)
    checkpoint_details: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class ThinkExecutor:
    """Unified single-surface executor for all KOSIF Think capabilities."""

    def __init__(
        self,
        audit_logger: Optional[AuditLogger] = None,
        memory_engine: Optional[MemoryEngine] = None
    ):
        self.preflight = PreflightGate()
        self.planner = TaskPlanner()
        self.router = CapabilityRouter()
        self.risk_gate = RiskGate()
        self.verifier = ObservableVerifier()
        self.recovery = RecoveryEngine()
        self.circuit_breaker = CircuitBreaker()
        self.audit = audit_logger or AuditLogger()
        self.memory = memory_engine or MemoryEngine()

        # Dynamic Lane Handlers
        self._lane_handlers: Dict[str, Any] = {}

    def register_lane(self, lane_name: str, handler: Any):
        """Registers an execution handler for a specific lane (reasoning, computer, browser, whatsapp)."""
        self._lane_handlers[lane_name.lower()] = handler

    async def execute_goal(
        self,
        raw_prompt: str,
        context: Optional[Dict[str, Any]] = None,
        cancellation_token: Optional[CancellationToken] = None,
        approved: bool = False
    ) -> ExecutionResult:
        """Executes the complete Think pipeline for an incoming goal."""
        t0 = time.perf_counter()

        # 1. Preflight
        req = self.preflight.run_preflight(raw_prompt, context, cancellation_token)
        if not req.is_valid:
            return ExecutionResult(
                task_id=req.task_id,
                goal=raw_prompt,
                status="cancelled" if "Cancelled" in (req.error_message or "") else "failed",
                steps_executed=0,
                duration_ms=round((time.perf_counter() - t0) * 1000, 2),
                error=req.error_message
            )

        self.audit.record_event("preflight_passed", req.task_id, "core", {"goal": req.clean_goal})

        # 2. Planning
        plan = self.planner.create_plan(req)
        self.audit.record_event("plan_created", req.task_id, "core", {
            "steps_count": len(plan.steps),
            "estimated_risk": plan.estimated_risk
        })

        executed_steps = 0
        last_output: Dict[str, Any] = {}

        # 3. Execution of Plan Steps
        for step in plan.steps:
            # Check cancellation token
            if cancellation_token and cancellation_token.is_cancellation_requested:
                self.audit.record_event("execution_cancelled", req.task_id, step.lane, {"step_id": step.step_id})
                return ExecutionResult(
                    task_id=req.task_id,
                    goal=req.clean_goal,
                    status="cancelled",
                    steps_executed=executed_steps,
                    duration_ms=round((time.perf_counter() - t0) * 1000, 2),
                    error="Operation cancelled by user."
                )

            # Route step
            lane = self.router.route_step(step.lane, step.intent)

            # Risk Gate check
            try:
                self.risk_gate.check_checkpoint_preconditions(
                    step=step,
                    page_url=last_output.get("url", ""),
                    page_title=last_output.get("title", ""),
                    approved=approved
                )
            except CheckpointRequired as cp:
                self.audit.record_event("checkpoint_triggered", req.task_id, lane, {
                    "checkpoint_type": cp.checkpoint_type,
                    "message": cp.message
                })
                return ExecutionResult(
                    task_id=req.task_id,
                    goal=req.clean_goal,
                    status="human_checkpoint",
                    steps_executed=executed_steps,
                    duration_ms=round((time.perf_counter() - t0) * 1000, 2),
                    checkpoint_details={"type": cp.checkpoint_type, "message": cp.message, **cp.details}
                )

            # Execute via Lane Handler
            handler = self._lane_handlers.get(lane)
            step_t0 = time.perf_counter()
            step_result: Dict[str, Any] = {}

            try:
                if handler:
                    step_result = await handler.dispatch_step(step, cancellation_token)
                else:
                    # Fallback simulation/mock if lane handler is not yet registered
                    step_result = {"status": "ok", "action": step.intent, "changed": True, "value": step.value}

                step_latency = (time.perf_counter() - step_t0) * 1000
                self.router.record_lane_metric(lane, success=True, latency_ms=step_latency)

            except Exception as e:
                step_latency = (time.perf_counter() - step_t0) * 1000
                self.router.record_lane_metric(lane, success=False, latency_ms=step_latency)
                self.audit.record_event("step_failed", req.task_id, lane, {"error": str(e)}, status="error")
                return ExecutionResult(
                    task_id=req.task_id,
                    goal=req.clean_goal,
                    status="failed",
                    steps_executed=executed_steps,
                    duration_ms=round((time.perf_counter() - t0) * 1000, 2),
                    error=str(e)
                )

            # 4. Observable Verification
            v_res = self.verifier.verify_step_postconditions(step.expected_postconditions, step_result)
            if not v_res.verified:
                self.audit.record_event("verification_failed", req.task_id, lane, {
                    "reason": v_res.failure_reason
                }, status="warning")

                # Try recovery
                if self.recovery.detect_action_loop():
                    rec_action = self.recovery.plan_recovery_action(step_result.get("url", ""), req.clean_goal)
                    self.audit.record_event("recovery_dispatched", req.task_id, lane, rec_action)

            executed_steps += 1
            last_output = step_result
            self.recovery.record_action({"lane": lane, "action": step.intent, "target": step.target.name})

        # Record memory
        total_duration = round((time.perf_counter() - t0) * 1000, 2)
        self.memory.record_task_summary(req.task_id, req.clean_goal, success=True, steps_count=executed_steps)
        self.audit.record_event("task_completed", req.task_id, "core", {"duration_ms": total_duration})

        return ExecutionResult(
            task_id=req.task_id,
            goal=req.clean_goal,
            status="completed",
            steps_executed=executed_steps,
            duration_ms=total_duration,
            output=last_output
        )
