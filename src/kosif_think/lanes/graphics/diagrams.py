"""
Diagram Synthesizer for KOSIF Think.
Generates Mermaid diagrams, Graphviz DOT specifications, and ASCII flowcharts.
"""

from typing import Dict, Any, List

class DiagramSynthesizer:
    """Produces verified architectural diagrams in multiple standard formats."""

    def generate_flowchart(self, title: str, nodes: List[Dict[str, str]], direction: str = "TD") -> str:
        """Generates a Mermaid flowchart string."""
        lines = [f"flowchart {direction}"]
        for n in nodes:
            nid = n.get("id", "node")
            label = n.get("label", nid)
            shape = n.get("shape", "rect")
            if shape == "circle":
                lines.append(f'    {nid}(("{label}"))')
            elif shape == "diamond":
                lines.append(f'    {nid}{{"{label}"}}')
            elif shape == "round":
                lines.append(f'    {nid}("{label}")')
            else:
                lines.append(f'    {nid}["{label}"]')

            target = n.get("next")
            if target:
                edge_label = f'|"{n.get("edge", "")}"| ' if n.get("edge") else ""
                lines.append(f"    {nid} --> {edge_label}{target}")

        return "\n".join(lines)

    def generate_sequence(self, participants: List[str], interactions: List[Dict[str, str]]) -> str:
        """Generates a Mermaid sequence diagram string."""
        lines = ["sequenceDiagram", "    autonumber"]
        for p in participants:
            lines.append(f"    participant {p}")
        for i in interactions:
            f = i.get("from")
            t = i.get("to")
            msg = i.get("message", "")
            dash = "-->>" if i.get("async") else "->>"
            lines.append(f"    {f}{dash}{t}: {msg}")
        return "\n".join(lines)

    def generate_dot(self, graph_name: str, edges: List[tuple]) -> str:
        """Generates a Graphviz DOT syntax string."""
        lines = [f"digraph {graph_name} {{", '    rankdir="LR";', '    node [shape=box, style=rounded, fontname="sans-serif"];']
        for u, v in edges:
            lines.append(f'    "{u}" -> "{v}";')
        lines.append("}")
        return "\n".join(lines)
