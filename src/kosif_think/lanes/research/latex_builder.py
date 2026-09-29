"""
Academic LaTeX Document Builder for KOSIF Think.
Synthesizes publication-ready academic papers in LaTeX format:
- Standard documentclass (article, IEEEtran, acmart, neurips)
- Abstract, Keywords, and Section hierarchy
- Mathematical equations in LaTeX math mode
- Tabular environments and figure wrappers
- Clean BibTeX integration
"""

from typing import Dict, Any, List, Optional
import re

class LatexBuilder:
    """Builds valid LaTeX academic documents."""

    def generate_paper_latex(
        self,
        title: str,
        authors: List[str],
        abstract: str,
        sections: List[Dict[str, str]],
        equations: Optional[List[str]] = None,
        bibtex_entries: Optional[List[str]] = None,
        doc_class: str = "article"
    ) -> str:
        """Generates complete compilable LaTeX document string."""
        auth_str = " \\and \n".join([f"\\textbf{{{a}}}" for a in authors])

        lines = [
            f"\\documentclass[11pt,a4paper,twocolumn]{{{doc_class}}}",
            "\\usepackage[utf8]{inputenc}",
            "\\usepackage{amsmath,amssymb,amsfonts}",
            "\\usepackage{graphicx}",
            "\\usepackage{booktabs}",
            "\\usepackage{hyperref}",
            "\\usepackage{cite}",
            "",
            f"\\title{{{title}}}",
            f"\\author{{{auth_str}}}",
            "\\date{\\today}",
            "",
            "\\begin{document}",
            "\\maketitle",
            "",
            "\\begin{abstract}",
            abstract.strip(),
            "\\end{abstract}",
            "",
            "\\textbf{Keywords:} Artificial Intelligence, Deep Reasoning, Autonomous Agents, Verifiable Inference",
            ""
        ]

        # Insert Sections
        for sec in sections:
            sec_title = sec.get("title", "Section")
            sec_body = sec.get("content", "")
            lines.append(f"\\section{{{sec_title}}}")
            lines.append(sec_body.strip())
            lines.append("")

        # Insert Equations if provided
        if equations:
            lines.append("\\section{Mathematical Formulations}")
            for idx, eq in enumerate(equations, 1):
                clean_eq = eq.replace("$", "").strip()
                lines.append(f"\\begin{{equation}}")
                lines.append(f"  {clean_eq} \\label{{eq:{idx}}}")
                lines.append(f"\\end{{equation}}")
                lines.append("")

        # Insert Bibliography
        lines.append("\\begin{thebibliography}{99}")
        if bibtex_entries:
            for idx, b in enumerate(bibtex_entries, 1):
                # Extract clean key and title from bibtex or text
                key_match = re.search(r'\{([^,]+),', b)
                key = key_match.group(1) if key_match else f"ref{idx}"
                lines.append(f"\\bibitem{{{key}}} {b[:120]}...")
        else:
            lines.append("\\bibitem{vaswani2017} Vaswani et al., ``Attention is All You Need'', NeurIPS 2017.")
            lines.append("\\bibitem{deepseek2025} DeepSeek-AI, ``DeepSeek-R1 Technical Report'', arXiv:2501.12948, 2025.")
        lines.append("\\end{thebibliography}")
        lines.append("")
        lines.append("\\end{document}")

        return "\n".join(lines)
