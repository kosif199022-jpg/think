"""
CodeAgent Execution Engine for KOSIF Think.
Inspired by Hugging Face smolagents & OpenAI Code-Interpreter:
Allows KOSIF Think to synthesize and run actions as high-density Python scripts
rather than serialized JSON tool calls. Enables:
- Native loops and multi-step data processing within a single cognitive step
- Direct piping of outputs between tools (e.g. ArXiv search -> Word synthesis -> Mobile notification)
- Safe execution in an AST-inspected runtime with pre-bound platform toolkits
- Rich error capture and self-healing trace reporting
"""

from typing import Dict, Any, List, Optional
import ast
import io
import sys
import time
import traceback

class CodeAgentInterpreter:
    """Executes expressive Python action scripts with bound KOSIF Think capabilities."""

    def __init__(self, context_tools: Optional[Dict[str, Any]] = None):
        self.context_tools = context_tools or {}
        self.execution_history: List[Dict[str, Any]] = []

    def register_tool(self, name: str, callable_fn: Any):
        """Registers a callable platform capability into the execution scope."""
        self.context_tools[name] = callable_fn

    def inspect_safety(self, code_str: str) -> Dict[str, Any]:
        """Performs static AST analysis to prevent dangerous operations (e.g. eval, os.system)."""
        try:
            tree = ast.parse(code_str)
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for n in node.names:
                        if n.name in ("subprocess", "shutil"):
                            return {"safe": False, "reason": f"Disallowed direct import: {n.name}"}
                elif isinstance(node, ast.Call):
                    if isinstance(node.func, ast.Name) and node.func.id in ("eval", "exec"):
                        return {"safe": False, "reason": f"Disallowed dynamic code execution: {node.func.id}"}
            return {"safe": True}
        except SyntaxError as se:
            return {"safe": False, "reason": f"Syntax error: {str(se)}"}

    def execute_script(self, script_code: str, custom_locals: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Executes a Python action script in an isolated namespace, capturing stdout and return values.
        """
        t0 = time.perf_counter()
        safety = self.inspect_safety(script_code)
        if not safety["safe"]:
            return {
                "status": "error",
                "stage": "safety_check",
                "error": safety["reason"],
                "duration_ms": round((time.perf_counter() - t0) * 1000, 2)
            }

        # Setup scope
        stdout_capture = io.StringIO()
        local_scope = dict(self.context_tools)
        if custom_locals:
            local_scope.update(custom_locals)

        # Standard safe builtins
        safe_builtins = {
            "print": lambda *args: stdout_capture.write(" ".join(map(str, args)) + "\n"),
            "len": len, "range": range, "enumerate": enumerate, "zip": zip,
            "min": min, "max": max, "sum": sum, "round": round, "abs": abs,
            "int": int, "float": float, "str": str, "bool": bool, "list": list,
            "dict": dict, "set": set, "tuple": tuple, "sorted": sorted,
            "isinstance": isinstance, "Exception": Exception
        }
        global_scope = {"__builtins__": safe_builtins}

        try:
            # Execute compiled code
            compiled = compile(script_code, "<kosif_code_agent>", "exec")
            old_stdout = sys.stdout
            sys.stdout = stdout_capture
            try:
                exec(compiled, global_scope, local_scope)
            finally:
                sys.stdout = old_stdout

            output_text = stdout_capture.getvalue().strip()
            # Extract final variable or result if defined
            result_val = local_scope.get("result") or local_scope.get("output") or output_text

            record = {
                "status": "ok",
                "success": True,
                "executed": True,
                "output": output_text,
                "result": result_val,
                "duration_ms": round((time.perf_counter() - t0) * 1000, 2)
            }
            self.execution_history.append(record)
            return record

        except Exception as e:
            duration_ms = round((time.perf_counter() - t0) * 1000, 2)
            err_msg = f"{type(e).__name__}: {str(e)}"
            return {
                "status": "error",
                "success": False,
                "error": err_msg,
                "traceback": traceback.format_exc(),
                "duration_ms": duration_ms
            }

    # Alias for smolagents python action convention
    execute_python_action = execute_script
