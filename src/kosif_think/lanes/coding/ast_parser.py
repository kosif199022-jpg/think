"""
AST Code Intelligence Parser for KOSIF Think.
Extracts symbols, class structures, method signatures, cyclomatic complexity,
and dependency import graphs across codebases.
"""

import ast
from typing import Dict, Any, List, Optional
from pathlib import Path

class CodeSymbol:
    def __init__(self, name: str, kind: str, line_no: int, docstring: str = "", args: List[str] = None):
        self.name = name
        self.kind = kind  # "function", "class", "async_function"
        self.line_no = line_no
        self.docstring = docstring
        self.args = args or []

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "kind": self.kind,
            "line": self.line_no,
            "args": self.args,
            "docstring": self.docstring[:100] if self.docstring else None
        }


class ASTCodeParser:
    """Parses code into structured symbol tables and dependency trees."""

    def parse_source(self, source_code: str, filename: str = "snippet.py") -> Dict[str, Any]:
        """Analyzes Python source code into an AST symbol hierarchy."""
        try:
            tree = ast.parse(source_code, filename=filename)
        except SyntaxError as e:
            return {
                "ok": False,
                "error": f"SyntaxError at line {e.lineno}: {e.msg}",
                "symbols": [],
                "imports": []
            }

        symbols: List[Dict[str, Any]] = []
        imports: List[str] = []
        complexity_count = 1

        for node in ast.walk(tree):
            if isinstance(node, (ast.If, ast.For, ast.While, ast.ExceptHandler, ast.With)):
                complexity_count += 1

            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                mod = node.module or ""
                for alias in node.names:
                    imports.append(f"{mod}.{alias.name}")

            elif isinstance(node, ast.FunctionDef):
                doc = ast.get_docstring(node) or ""
                arg_names = [a.arg for a in node.args.args]
                sym = CodeSymbol(name=node.name, kind="function", line_no=node.lineno, docstring=doc, args=arg_names)
                symbols.append(sym.to_dict())

            elif isinstance(node, ast.AsyncFunctionDef):
                doc = ast.get_docstring(node) or ""
                arg_names = [a.arg for a in node.args.args]
                sym = CodeSymbol(name=node.name, kind="async_function", line_no=node.lineno, docstring=doc, args=arg_names)
                symbols.append(sym.to_dict())

            elif isinstance(node, ast.ClassDef):
                doc = ast.get_docstring(node) or ""
                sym = CodeSymbol(name=node.name, kind="class", line_no=node.lineno, docstring=doc)
                symbols.append(sym.to_dict())

        return {
            "ok": True,
            "filename": filename,
            "symbol_count": len(symbols),
            "symbols": symbols,
            "imports": list(set(imports)),
            "cyclomatic_complexity": complexity_count
        }

    def parse_file(self, file_path: str) -> Dict[str, Any]:
        p = Path(file_path)
        if not p.exists():
            return {"ok": False, "error": f"File {file_path} not found"}
        code = p.read_text(encoding="utf-8", errors="ignore")
        return self.parse_source(code, filename=p.name)
