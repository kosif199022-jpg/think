"""
Model-backed reasoning strategies for KOSIF Think, implemented as the papers describe them.

Every strategy takes a ``ModelClient`` (Claude, Ollama, any OpenAI-compatible server, or ``ScriptedClient`` in
tests) and returns a plain dict with the final answer, the intermediate calls and the token usage.

- Self-consistency: Wang et al., 2022, "Self-Consistency Improves Chain of Thought Reasoning in Language Models".
- Chain-of-Verification: Dhuliawala et al. (Meta), 2023, "Chain-of-Verification Reduces Hallucination in LLMs",
  factored variant (each verification question is answered without seeing the draft).
- Self-Refine: Madaan et al., 2023, "Self-Refine: Iterative Refinement with Self-Feedback".
- Reflexion: Shinn et al., 2023, "Reflexion: Language Agents with Verbal Reinforcement Learning".
- Tree of Thoughts (BFS): Yao et al. (Princeton), 2023, "Tree of Thoughts: Deliberate Problem Solving with LLMs",
  propose/value prompting with sure/likely/impossible state values.
- Multi-agent debate: Du et al., 2023, "Improving Factuality and Reasoning in Language Models through
  Multiagent Debate".
- Least-to-most: Zhou et al., 2022, "Least-to-Most Prompting Enables Complex Reasoning in LLMs".
"""

from collections import Counter
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Sequence, Tuple
import math
import re
import time

from ...connectors.models import ModelClient, ModelError

ANSWER_INSTRUCTION = "Think step by step, then finish with a final line of the form 'Answer: <answer>'."


@dataclass
class _Trace:
    """Collects every model call a strategy makes."""
    client: ModelClient
    max_tokens: int = 2048
    calls: List[Dict[str, Any]] = field(default_factory=list)

    def ask(self, prompt: str, system: Optional[str] = None, temperature: Optional[float] = None,
            role: str = "") -> str:
        completion = self.client.complete(prompt, system=system, max_tokens=self.max_tokens, temperature=temperature)
        self.calls.append({"role": role, "prompt": prompt, "response": completion.text,
                           "input_tokens": completion.input_tokens, "output_tokens": completion.output_tokens})
        return completion.text

    def usage(self) -> Dict[str, int]:
        return {"model_calls": len(self.calls),
                "input_tokens": sum(c["input_tokens"] for c in self.calls),
                "output_tokens": sum(c["output_tokens"] for c in self.calls)}


def extract_answer(text: str) -> str:
    """The text after the last 'Answer:' line, else the last non-empty line."""
    matches = re.findall(r"(?im)^\s*(?:final\s+)?answer\s*[:：]\s*(.+?)\s*$", text)
    if matches:
        return matches[-1]
    lines = [ln.strip() for ln in text.strip().splitlines() if ln.strip()]
    return lines[-1] if lines else ""


def normalize_answer(answer: str) -> str:
    """Canonical form used for voting: lower case, no surrounding punctuation, numbers without separators."""
    a = answer.strip().strip("*_`").strip().rstrip(".").strip()
    a = re.sub(r"\s+", " ", a).lower()
    if re.fullmatch(r"[-+]?[\d,]*\.?\d+", a):
        a = a.replace(",", "")
        try:
            value = float(a)
            a = str(int(value)) if value.is_integer() else str(value)
        except ValueError:
            pass
    return a


def _entropy(counts: Sequence[int]) -> float:
    total = sum(counts)
    if total <= 1:
        return 0.0
    return round(-sum((c / total) * math.log2(c / total) for c in counts if c), 3)


def _result(mode: str, trace: _Trace, t0: float, **fields: Any) -> Dict[str, Any]:
    return {"mode": mode, "simulated": False, "model": trace.client.describe(), **fields,
            "usage": trace.usage(), "calls": trace.calls,
            "duration_ms": round((time.perf_counter() - t0) * 1000, 2)}


def self_consistency(client: ModelClient, question: str, samples: int = 5, temperature: float = 0.8,
                     max_tokens: int = 2048) -> Dict[str, Any]:
    """Samples several independent chains of thought and returns the majority final answer."""
    t0 = time.perf_counter()
    trace = _Trace(client, max_tokens)
    prompt = f"{question}\n\n{ANSWER_INSTRUCTION}"
    answers: List[Tuple[str, str]] = []
    for i in range(max(1, samples)):
        text = trace.ask(prompt, temperature=temperature, role=f"sample_{i + 1}")
        raw = extract_answer(text)
        answers.append((raw, normalize_answer(raw)))
    votes = Counter(norm for _, norm in answers)
    winner, top = votes.most_common(1)[0]
    shown = next(raw for raw, norm in answers if norm == winner)
    return _result("self_consistency", trace, t0, question=question, answer=shown,
                   votes=dict(votes), consensus_ratio=round(top / len(answers), 3),
                   entropy=_entropy(list(votes.values())), unanimous=top == len(answers))


def _numbered(text: str) -> List[str]:
    items = []
    for line in text.splitlines():
        m = re.match(r"^\s*(?:\d+[.)]|[-*•])\s+(.+)$", line)
        if m:
            items.append(m.group(1).strip())
    return items


def chain_of_verification(client: ModelClient, question: str, max_questions: int = 5,
                          max_tokens: int = 2048) -> Dict[str, Any]:
    """Draft, plan verification questions, answer them independently of the draft, then revise."""
    t0 = time.perf_counter()
    trace = _Trace(client, max_tokens)
    draft = trace.ask(question, role="baseline")
    plan = trace.ask(
        "Here is a question and a draft answer.\n\n"
        f"Question: {question}\n\nDraft answer:\n{draft}\n\n"
        f"List up to {max_questions} short fact-checking questions, one per line and numbered, whose answers "
        "would confirm or refute the individual claims in the draft. Output only the list.",
        role="plan")
    questions = _numbered(plan)[:max_questions] or [q.strip() for q in plan.splitlines() if q.strip()][:max_questions]
    checks = []
    for q in questions:
        # Factored: the draft is not shown, so its errors cannot be copied into the check.
        ans = trace.ask(f"Answer concisely and factually: {q}", role="verify")
        checks.append({"question": q, "answer": ans})
    evidence = "\n".join(f"Q: {c['question']}\nA: {c['answer']}" for c in checks)
    final = trace.ask(
        f"Question: {question}\n\nDraft answer:\n{draft}\n\nIndependent verification:\n{evidence}\n\n"
        "Write the final answer. Keep what the verification supports, correct what it contradicts, and drop "
        "claims it cannot support. Then add a final line 'Changed: yes' or 'Changed: no'.",
        role="final")
    changed_m = re.search(r"(?im)^\s*changed\s*:\s*(yes|no)\s*$", final)
    final_text = re.sub(r"(?im)^\s*changed\s*:\s*(yes|no)\s*$", "", final).strip()
    return _result("chain_of_verification", trace, t0, question=question, draft_response=draft,
                   verifications=checks, verification_questions_count=len(checks),
                   verified_response=final_text,
                   draft_changed=(changed_m.group(1).lower() == "yes") if changed_m else None)


def self_refine(client: ModelClient, task: str, max_iterations: int = 3, stop_phrase: str = "NO ISSUES",
                max_tokens: int = 2048) -> Dict[str, Any]:
    """Generate, get feedback from the same model, refine; stops when the feedback finds nothing to fix."""
    t0 = time.perf_counter()
    trace = _Trace(client, max_tokens)
    output = trace.ask(task, role="initial")
    history = []
    for i in range(max(1, max_iterations)):
        feedback = trace.ask(
            f"Task: {task}\n\nCurrent output:\n{output}\n\nGive specific, actionable feedback on errors or "
            f"weaknesses in this output. If nothing needs to change, reply exactly '{stop_phrase}'.",
            role=f"feedback_{i + 1}")
        history.append({"output": output, "feedback": feedback})
        if stop_phrase.lower() in feedback.lower():
            break
        output = trace.ask(
            f"Task: {task}\n\nPrevious output:\n{output}\n\nFeedback:\n{feedback}\n\n"
            "Rewrite the output, addressing every point of the feedback. Output only the new version.",
            role=f"refine_{i + 1}")
    else:
        history.append({"output": output, "feedback": None})
    return _result("self_refine", trace, t0, task=task, answer=output, iterations=history,
                   converged=bool(history and history[-1]["feedback"]
                                  and stop_phrase.lower() in history[-1]["feedback"].lower()))


Evaluator = Callable[[str], Tuple[bool, str]]


def reflexion(client: ModelClient, task: str, evaluator: Evaluator, max_trials: int = 3,
              max_tokens: int = 2048) -> Dict[str, Any]:
    """Try, evaluate with an external signal, write a verbal self-reflection, retry with the reflections in memory.

    ``evaluator(attempt) -> (passed, feedback)`` is the environment signal: unit tests, a checker, a validator.
    """
    t0 = time.perf_counter()
    trace = _Trace(client, max_tokens)
    reflections: List[str] = []
    trials = []
    attempt = ""
    passed = False
    for trial in range(1, max(1, max_trials) + 1):
        memory = ("\n\nLessons from your earlier failed attempts:\n" + "\n".join(f"- {r}" for r in reflections)
                  if reflections else "")
        attempt = trace.ask(f"{task}{memory}", role=f"attempt_{trial}")
        passed, feedback = evaluator(attempt)
        trials.append({"trial": trial, "attempt": attempt, "passed": passed, "feedback": feedback})
        if passed:
            break
        reflection = trace.ask(
            f"Task: {task}\n\nYour attempt:\n{attempt}\n\nIt failed with this feedback:\n{feedback}\n\n"
            "In two or three sentences, diagnose why it failed and state concretely what to do differently "
            "next time.", role=f"reflect_{trial}")
        reflections.append(reflection.strip())
    return _result("reflexion", trace, t0, task=task, answer=attempt, passed=passed, trials=trials,
                   reflections=reflections)


VALUE_WEIGHTS = {"sure": 20.0, "likely": 1.0, "impossible": 0.001}


def tree_of_thoughts(client: ModelClient, problem: str, breadth: int = 3, depth: int = 3, beam: int = 2,
                     value_samples: int = 1, max_tokens: int = 1024) -> Dict[str, Any]:
    """Breadth-first Tree of Thoughts: propose next steps, value each partial solution, keep the best ``beam``."""
    t0 = time.perf_counter()
    trace = _Trace(client, max_tokens)
    frontier: List[Tuple[float, List[str]]] = [(1.0, [])]
    explored = 0
    for level in range(1, max(1, depth) + 1):
        candidates: List[Tuple[float, List[str]]] = []
        for _, steps in frontier:
            so_far = "\n".join(f"Step {i + 1}: {s}" for i, s in enumerate(steps)) or "(no steps yet)"
            proposal = trace.ask(
                f"Problem: {problem}\n\nSteps so far:\n{so_far}\n\n"
                f"Propose {breadth} different possible next steps, numbered, one per line. "
                + ("This is the last step: each proposal must state the final answer." if level == depth else ""),
                role=f"propose_d{level}")
            options = _numbered(proposal)[:breadth] or [proposal.strip()]
            for option in options:
                path = steps + [option]
                listing = "\n".join(f"Step {i + 1}: {s}" for i, s in enumerate(path))
                score = 0.0
                for _ in range(max(1, value_samples)):
                    verdict = trace.ask(
                        f"Problem: {problem}\n\nPartial solution:\n{listing}\n\n"
                        "Evaluate whether this partial solution can reach a correct answer. Reply with one word: "
                        "sure, likely or impossible.", role=f"value_d{level}").strip().lower()
                    word = next((w for w in ("impossible", "sure", "likely") if w in verdict), "likely")
                    score += VALUE_WEIGHTS[word]
                candidates.append((score, path))
                explored += 1
        candidates.sort(key=lambda c: c[0], reverse=True)
        frontier = candidates[:max(1, beam)]
    best_score, best_path = frontier[0]
    return _result("tree_of_thoughts", trace, t0, problem=problem, answer=best_path[-1] if best_path else "",
                   optimal_reasoning_path=best_path, best_score=best_score, total_thoughts_explored=explored,
                   frontier=[{"score": s, "path": p} for s, p in frontier])


def multi_agent_debate(clients: Sequence[ModelClient], question: str, rounds: int = 2,
                       max_tokens: int = 2048) -> Dict[str, Any]:
    """Several agents answer, read each other's answers, and update over ``rounds``; majority final answer.

    Pass the same client several times for self-debate, or different providers for a mixed panel.
    """
    if not clients:
        raise ModelError("multi_agent_debate needs at least one client.")
    t0 = time.perf_counter()
    traces = [_Trace(c, max_tokens) for c in clients]
    responses = [t.ask(f"{question}\n\n{ANSWER_INSTRUCTION}", role=f"agent_{i + 1}_round_1")
                 for i, t in enumerate(traces)]
    transcript = [list(responses)]
    for r in range(2, max(1, rounds) + 1):
        updated = []
        for i, t in enumerate(traces):
            others = "\n\n".join(f"Agent {j + 1}:\n{resp}" for j, resp in enumerate(responses) if j != i)
            updated.append(t.ask(
                f"{question}\n\nThese are the solutions from other agents:\n\n{others}\n\n"
                f"Your previous solution:\n{responses[i]}\n\nUsing their reasoning as additional advice, give an "
                f"updated solution. {ANSWER_INSTRUCTION}", role=f"agent_{i + 1}_round_{r}"))
        responses = updated
        transcript.append(list(responses))
    finals = [(extract_answer(x), normalize_answer(extract_answer(x))) for x in responses]
    votes = Counter(n for _, n in finals)
    winner, top = votes.most_common(1)[0]
    merged = _Trace(clients[0])
    merged.calls = [c for t in traces for c in t.calls]
    return _result("multi_agent_debate", merged, t0, question=question,
                   answer=next(raw for raw, n in finals if n == winner), votes=dict(votes),
                   consensus_ratio=round(top / len(finals), 3), agents=len(clients), rounds=len(transcript),
                   transcript=transcript)


def least_to_most(client: ModelClient, problem: str, max_subproblems: int = 6,
                  max_tokens: int = 2048) -> Dict[str, Any]:
    """Decompose into simpler subproblems, then solve them in order, each with the earlier answers in context."""
    t0 = time.perf_counter()
    trace = _Trace(client, max_tokens)
    plan = trace.ask(
        f"Problem: {problem}\n\nTo solve this, which simpler subproblems should be solved first? List them in "
        f"order, numbered, at most {max_subproblems}, ending with the original problem itself. Output only the list.",
        role="decompose")
    subproblems = _numbered(plan)[:max_subproblems] or [problem]
    solved: List[Dict[str, str]] = []
    for sp in subproblems:
        context = "\n".join(f"Q: {s['subproblem']}\nA: {s['answer']}" for s in solved)
        answer = trace.ask(f"Problem: {problem}\n\n{context}\n\nQ: {sp}\nA:" if context else
                           f"Problem: {problem}\n\nQ: {sp}\nA:", role="solve")
        solved.append({"subproblem": sp, "answer": answer.strip()})
    return _result("least_to_most", trace, t0, problem=problem, answer=solved[-1]["answer"], subproblems=solved)


STRATEGIES: Dict[str, Callable[..., Dict[str, Any]]] = {
    "self_consistency": self_consistency,
    "chain_of_verification": chain_of_verification,
    "self_refine": self_refine,
    "reflexion": reflexion,
    "tree_of_thoughts": tree_of_thoughts,
    "multi_agent_debate": multi_agent_debate,
    "least_to_most": least_to_most,
}
