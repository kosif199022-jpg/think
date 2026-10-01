"""KOSIF Think Pro: deterministic verification and decision tools, ported from the KOSIF Think Pro 4.2.2 plugin.

Every tool takes a plain dict and returns a plain dict, so the same calls work from Python, the CLI
(``think pro <tool> input.json``) and the HTTP/MCP servers. They check the internal consistency of what they are
given; none of them proves the inputs are true.
"""

from typing import Any, Callable, Dict

from . import (calibration, capability_truth, council_aggregate, council_independence, council_select, decision,
               evidence, graph, ledger, probability, secrets, source_atlas)
from .council_model import deliberate


def _atlas(payload: Dict[str, Any]) -> Dict[str, Any]:
    if not payload.get("as_of"):
        raise ValueError("as_of (YYYY-MM-DD) is required")
    return source_atlas.build_atlas(payload.get("records") or [], as_of=payload["as_of"],
                                    near_threshold=float(payload.get("near_threshold", 0.75)))


def _secrets(payload: Dict[str, Any]) -> Dict[str, Any]:
    text = str(payload.get("text") or "")
    result = secrets.scan_text(text)
    if payload.get("redact"):
        result["redacted_text"] = secrets.redact_text(text)
    return result


TOOLS: Dict[str, Callable[[Dict[str, Any]], Dict[str, Any]]] = {
    "decision": decision.analyse,
    "probability": probability.check,
    "calibration": calibration.check,
    "evidence": evidence.validate,
    "council-select": council_select.select,
    "council-aggregate": council_aggregate.aggregate,
    "council-independence": council_independence.score,
    "source-atlas": _atlas,
    "secrets": _secrets,
    "capability": capability_truth.assess_capability,
    "dag": graph.verify,
    "ledger": ledger.check,
}

DESCRIPTIONS: Dict[str, str] = {
    "decision": "Feasibility, Pareto dominance, weighted ranking and weight sensitivity for options",
    "probability": "Probability coherence (complements, conjunction/disjunction) and Bayes base-rate checks",
    "calibration": "Do certainty words in claims match the independent direct evidence?",
    "evidence": "Typed arithmetic/sum/percent/ratio/range/date/unit checks; quarantine contradicted answers",
    "council-select": "Pick Council-100 lenses for a task (standard, pro or full)",
    "council-aggregate": "Evidence-weighted council verdict: proceed, revise or escalate (vetoes cannot be outvoted)",
    "council-independence": "Provenance diversity score for council artifacts",
    "source-atlas": "Exact/near duplicate detection, retrieval weights, quarantine and freshness for sources",
    "secrets": "Scan text for likely credentials (optionally redact) without echoing them",
    "capability": "Capability truth status from evidence (verified, measured, implemented, ...)",
    "dag": "Validate a directed graph is acyclic and return a topological order",
    "ledger": "Journal entry controls: balance, chart, period, VAT, duplicates, invoice-bank matching",
}


def run_tool(name: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    if name not in TOOLS:
        raise KeyError(f"unknown tool {name!r}; available: {', '.join(sorted(TOOLS))}")
    if not isinstance(payload, dict):
        raise ValueError("payload must be a JSON object")
    return TOOLS[name](payload)


__all__ = ["TOOLS", "DESCRIPTIONS", "run_tool", "deliberate"]
