"""Model-backed Council-100 deliberation.

Selects lenses with ``council_select.select``, asks the model for one frozen first-pass artifact per lens
(stance, confidence, evidence, objection, severity), aggregates them with ``council_aggregate.aggregate``
(evidence-weighted, a blocking veto cannot be outvoted), then asks for one synthesis that answers the
surviving objections. Every persona is voiced by the same client, so the result counts as one independent
source; ``extra_sources`` can name tools or other models whose evidence was actually used.
"""

from typing import Any, Dict, List, Optional, Sequence
import json
import re
import time

from ..connectors.models import ModelClient
from .council_aggregate import SEVERITIES, STANCES, aggregate
from .council_select import load, select

ARTIFACT_INSTRUCTION = (
    "Reply with one JSON object only, no prose: "
    '{"stance": "support|oppose|abstain|not-material", "confidence": 0.0-1.0, '
    '"evidence": ["concrete fact, measurement or source you rely on"], '
    '"objection": "your strongest objection, or empty", "severity": "none|low|material|blocking"}. '
    "Use \"blocking\" only for an objection that must stop the plan. List only evidence you can name; "
    "an empty list is better than invented evidence."
)


def _parse_artifact(text: str) -> Optional[Dict[str, Any]]:
    match = re.search(r"\{.*\}", text, flags=re.S)
    if not match:
        return None
    try:
        data = json.loads(match.group(0))
    except json.JSONDecodeError:
        return None
    return data if isinstance(data, dict) else None


def _clean(pid: str, raw: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    if raw is None:
        return {"id": pid, "stance": "abstain", "confidence": 0.0, "evidence": [], "objection": "",
                "severity": "none", "parse_error": True}
    stance = str(raw.get("stance", "abstain")).strip().lower()
    severity = str(raw.get("severity", "none")).strip().lower()
    try:
        confidence = min(1.0, max(0.0, float(raw.get("confidence", 0.5))))
    except (TypeError, ValueError):
        confidence = 0.5
    evidence = [str(e) for e in (raw.get("evidence") or []) if str(e).strip()][:3]
    objection = str(raw.get("objection") or "").strip()
    return {"id": pid, "stance": stance if stance in STANCES else "abstain", "confidence": confidence,
            "evidence": evidence, "objection": objection,
            "severity": severity if severity in SEVERITIES else ("material" if objection else "none")}


def deliberate(client: ModelClient, task: str, mode: str = "standard", max_personas: int = 8,
               domains: Sequence[str] = (), extra_sources: Sequence[str] = (),
               max_tokens: int = 1024) -> Dict[str, Any]:
    t0 = time.perf_counter()
    data = load()
    by_id = {p["id"]: p for p in data["personas"]}
    selection = select({"task": task, "mode": mode, "max": max_personas, "domains": list(domains)}, data)
    artifacts: List[Dict[str, Any]] = []
    calls: List[Dict[str, Any]] = []
    for chosen in selection["personas"]:
        persona = by_id[chosen["id"]]
        system = (f"You are the council lens '{persona['name']}' ({persona['name_ar']}), chamber "
                  f"'{persona['chamber']}'. Specialty: {persona.get('specialty', '')}. "
                  f"Rule: {persona['if_then']}. Your guiding question: {persona['question']}")
        prompt = f"Proposal or question under review:\n{task}\n\n{ARTIFACT_INSTRUCTION}"
        completion = client.complete(prompt, system=system, max_tokens=max_tokens)
        calls.append({"persona": persona["id"], "response": completion.text,
                      "input_tokens": completion.input_tokens, "output_tokens": completion.output_tokens})
        artifacts.append(_clean(persona["id"], _parse_artifact(completion.text)))

    verdict = aggregate({"artifacts": [{k: v for k, v in a.items() if k != "parse_error"} for a in artifacts],
                         "sources": {"models": [client.model], "tools": list(extra_sources)}}, data)
    open_items = verdict.get("blocking_vetoes", []) + verdict.get("surviving_dissent", [])
    objections = "\n".join(f"- [{o['severity']}] {o['id']}: {o['objection']}" for o in open_items) or "- none"
    synthesis = client.complete(
        f"Proposal or question:\n{task}\n\nCouncil verdict: {verdict.get('verdict')}.\nOpen objections:\n"
        f"{objections}\n\nWrite the recommended course of action. Address every open objection explicitly "
        "(accept it and change the plan, or explain with evidence why it does not apply). Be concise.",
        max_tokens=max_tokens * 2)
    calls.append({"persona": "synthesis", "response": synthesis.text, "input_tokens": synthesis.input_tokens,
                  "output_tokens": synthesis.output_tokens})
    return {
        "mode": "council100", "simulated": False, "model": client.describe(), "task": task,
        "selection": {"mode": selection["mode"], "count": selection["count"], "chambers": selection["chambers"],
                      "veto_holders": selection["veto_holders"]},
        "artifacts": artifacts, "verdict": verdict, "recommendation": synthesis.text,
        "parse_errors": [a["id"] for a in artifacts if a.get("parse_error")],
        "usage": {"model_calls": len(calls), "input_tokens": sum(c["input_tokens"] for c in calls),
                  "output_tokens": sum(c["output_tokens"] for c in calls)},
        "calls": calls, "duration_ms": round((time.perf_counter() - t0) * 1000, 2),
    }
