"""
Symbolic Math & Propositional Logic Verifier for KOSIF Think.
Inspired by SymPy, Z3, and Lean theorem provers.
Provides formal mathematical verification, propositional logic truth tables,
algebraic root solving, and dimensional unit conversions.
Zero external dependencies. Pure Python.
"""

from typing import Dict, Any, List, Optional, Tuple, Set
import math
import itertools
import re
import time

class SymbolicResult(dict):
    """Result wrapper supporting both dict and attribute access, plus float equality."""
    def __getattr__(self, name: str) -> Any:
        if name in self:
            return self[name]
        if name == "satisfiable":
            return self.get("is_satisfiable", False)
        if name == "tautology":
            return self.get("is_tautology", False)
        if name == "nature":
            return self.get("root_nature", "")
        if name == "satisfying_assignments":
            return self.get("satisfying_models", [])
        raise AttributeError(f"'SymbolicResult' object has no attribute '{name}'")

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, (int, float)):
            return self.get("root") == other or self.get("value") == other
        return super().__eq__(other)

    def __float__(self) -> float:
        return float(self.get("root", self.get("value", 0.0)))


class SymbolicVerifier:
    """Formal mathematical, logic, and constraint verification engine."""

    # ----------------------------------------------------
    # 1. Propositional Logic & Truth Table Verification
    # ----------------------------------------------------

    def verify_propositional_logic(self, formula: str) -> Dict[str, Any]:
        """
        Evaluates boolean formula, checks SAT (satisfiability),
        and verifies if it is a Tautology or Contradiction.
        Supported operators: AND (&), OR (|), NOT (~), -> (implies), == (iff), XOR (^).
        """
        t0 = time.perf_counter()
        # Find variable names (single uppercase or lowercase letters)
        variables = sorted(list(set(re.findall(r"\b[A-Za-z]\b", formula))))
        if not variables:
            return {"error": "No propositional variables found in formula."}

        # Convert operators to valid python boolean operators
        expr = formula
        expr = expr.replace("->", " <= ")   # A implies B is equivalent to not A or B (A <= B in bool arithmetic)
        expr = expr.replace("<->", " == ")
        expr = expr.replace("AND", " and ").replace("&", " and ")
        expr = expr.replace("OR", " or ").replace("|", " or ")
        expr = expr.replace("NOT", " not ").replace("~", " not ")
        expr = expr.replace("XOR", " ^ ")

        truth_table = []
        all_true = True
        all_false = True
        sat_assignments = []

        for combo in itertools.product([False, True], repeat=len(variables)):
            env = dict(zip(variables, combo))
            try:
                res = bool(eval(expr, {"__builtins__": {}}, env))
                entry = dict(env)
                entry["result"] = res
                truth_table.append(entry)

                if res:
                    all_false = False
                    sat_assignments.append(env)
                else:
                    all_true = False
            except Exception as ex:
                return {"error": f"Evaluation error in formula: {ex}"}

        duration_ms = round((time.perf_counter() - t0) * 1000, 2)

        return SymbolicResult({
            "formula": formula,
            "variables": variables,
            "total_evaluations": len(truth_table),
            "is_tautology": all_true,
            "tautology": all_true,
            "is_contradiction": all_false,
            "is_satisfiable": len(sat_assignments) > 0,
            "satisfiable": len(sat_assignments) > 0,
            "satisfying_models_count": len(sat_assignments),
            "satisfying_assignments": sat_assignments,
            "sample_satisfying_model": sat_assignments[0] if sat_assignments else None,
            "duration_ms": duration_ms
        })

    verify_proposition = verify_propositional_logic

    # ----------------------------------------------------
    # 2. Algebraic Equation Solver
    # ----------------------------------------------------

    def solve_linear(self, a: float, b: float, c: float = 0.0) -> SymbolicResult:
        """Solves a * x + b = c  =>  x = (c - b) / a"""
        if a == 0:
            return SymbolicResult({"status": "error", "error": "Coefficient 'a' cannot be zero in linear equation.", "root": 0.0, "value": 0.0})
        x = (c - b) / a
        root_val = round(x, 6)
        return SymbolicResult({"equation": f"{a}x + {b} = {c}", "root": root_val, "value": root_val})

    def solve_quadratic(self, a: float, b: float, c: float) -> SymbolicResult:
        """Solves a * x^2 + b * x + c = 0 via discriminant."""
        if a == 0:
            return self.solve_linear(b, c, 0.0)

        delta = b ** 2 - 4 * a * c
        if delta > 0:
            r1 = (-b + math.sqrt(delta)) / (2 * a)
            r2 = (-b - math.sqrt(delta)) / (2 * a)
            roots = [round(r1, 6), round(r2, 6)]
            nature = "two_real_roots"
        elif delta == 0:
            r = -b / (2 * a)
            roots = [round(r, 6)]
            nature = "one_repeated_real_root"
        else:
            real_part = round(-b / (2 * a), 6)
            imag_part = round(math.sqrt(-delta) / (2 * a), 6)
            roots = [f"{real_part} + {imag_part}i", f"{real_part} - {imag_part}i"]
            nature = "two_complex_conjugate_roots"

        return SymbolicResult({
            "equation": f"{a}x^2 + {b}x + {c} = 0",
            "discriminant": round(delta, 4),
            "root_nature": nature,
            "nature": nature,
            "roots": roots
        })

    # ----------------------------------------------------
    # 3. Unit Conversion Engine
    # ----------------------------------------------------

    def convert_units(self, value: float, from_unit: str, to_unit: str) -> SymbolicResult:
        """Converts dimensions between digital storage, time, length, and temperature."""
        u_from = from_unit.lower().strip()
        u_to = to_unit.lower().strip()

        # Length / Distance
        length_map = {"mm": 0.001, "cm": 0.01, "m": 1.0, "km": 1000.0, "inch": 0.0254, "ft": 0.3048, "mile": 1609.344}
        if u_from in length_map and u_to in length_map:
            total_m = value * length_map[u_from]
            converted = total_m / length_map[u_to]
            val = round(converted, 4)
            return SymbolicResult({"from": f"{value} {from_unit}", "to": f"{val} {to_unit}", "dimension": "length", "value": val, "root": val})

        # Digital Storage
        bytes_map = {"b": 1, "kb": 1024, "mb": 1024**2, "gb": 1024**3, "tb": 1024**4}
        if u_from in bytes_map and u_to in bytes_map:
            total_bytes = value * bytes_map[u_from]
            converted = total_bytes / bytes_map[u_to]
            val = round(converted, 4)
            return SymbolicResult({"from": f"{value} {from_unit}", "to": f"{val} {to_unit}", "dimension": "storage", "value": val, "root": val})

        # Time
        time_map = {"ms": 0.001, "s": 1, "sec": 1, "m": 60, "min": 60, "h": 3600, "hr": 3600, "d": 86400}
        if u_from in time_map and u_to in time_map:
            total_sec = value * time_map[u_from]
            converted = total_sec / time_map[u_to]
            val = round(converted, 4)
            return SymbolicResult({"from": f"{value} {from_unit}", "to": f"{val} {to_unit}", "dimension": "time", "value": val, "root": val})

        # Temperature
        if u_from in ("c", "celsius") and u_to in ("f", "fahrenheit"):
            converted = (value * 9/5) + 32
            val = round(converted, 2)
            return SymbolicResult({"from": f"{value} C", "to": f"{val} F", "dimension": "temperature", "value": val, "root": val})
        elif u_from in ("f", "fahrenheit") and u_to in ("c", "celsius"):
            converted = (value - 32) * 5/9
            val = round(converted, 2)
            return SymbolicResult({"from": f"{value} F", "to": f"{val} C", "dimension": "temperature", "value": val, "root": val})

        return SymbolicResult({"error": f"Unsupported conversion from '{from_unit}' to '{to_unit}'.", "value": 0.0, "root": 0.0})

    # ----------------------------------------------------
    # 4. Range Constraint Verification (Interval Arithmetic)
    # ----------------------------------------------------

    def verify_numeric_bounds(self, var_name: str, constraints: List[str]) -> Dict[str, Any]:
        """
        Evaluates a set of inequalities like ["x >= 10", "x <= 50", "x < 100"]
        and finds the feasible bounding interval [lower, upper].
        """
        lower = -float("inf")
        upper = float("inf")

        for c in constraints:
            m_gt = re.search(rf"{var_name}\s*(>=|>)\s*(-?\d+(?:\.\d+)?)", c)
            if m_gt:
                val = float(m_gt.group(2))
                lower = max(lower, val)
            m_lt = re.search(rf"{var_name}\s*(<=|<)\s*(-?\d+(?:\.\d+)?)", c)
            if m_lt:
                val = float(m_lt.group(2))
                upper = min(upper, val)

        is_feasible = lower <= upper
        return {
            "variable": var_name,
            "feasible": is_feasible,
            "lower_bound": lower if lower != -float("inf") else None,
            "upper_bound": upper if upper != float("inf") else None,
            "interval_str": f"[{lower}, {upper}]" if is_feasible else "Infeasible (Empty Set)"
        }
