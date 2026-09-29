"""
Citation & Bibliography Engine for KOSIF Think.
Formats academic literature into BibTeX, APA 7th, IEEE, and Harvard styles.
"""

from typing import Dict, Any, List
import re

class CitationEngine:
    """Formats papers into standard academic citation styles."""

    def to_bibtex(self, paper: Dict[str, Any]) -> str:
        """Formats an academic paper into valid BibTeX format."""
        authors = paper.get("authors", ["Anonymous"])
        first_author = authors[0].split()[-1].lower() if authors else "author"
        year = paper.get("year", 2024)
        title = paper.get("title", "Untitled")
        first_word = re.sub(r'[^a-zA-Z]', '', title.split()[0].lower()) if title.split() else "paper"
        cite_key = f"{first_author}{year}{first_word}"

        auth_str = " and ".join(authors)
        journal = paper.get("journal") or f"arXiv preprint arXiv:{paper.get('paper_id', 'abs')}"
        doi_line = f"  doi = {{{paper['doi']}}},\n" if paper.get("doi") else ""

        return (
            f"@article{{{cite_key},\n"
            f"  title = {{{{{title}}}}},\n"
            f"  author = {{{auth_str}}},\n"
            f"  journal = {{{journal}}},\n"
            f"  year = {{{year}}},\n"
            f"{doi_line}"
            f"  url = {{{paper.get('pdf_url', '')}}}\n"
            f"}}"
        )

    def to_apa(self, paper: Dict[str, Any]) -> str:
        """Formats citation in APA 7th edition style."""
        authors = paper.get("authors", ["Anonymous"])
        year = paper.get("year", 2024)
        title = paper.get("title", "Untitled")
        formatted_authors = []
        for a in authors[:3]:
            parts = a.split()
            last = parts[-1]
            initials = " ".join([p[0] + "." for p in parts[:-1]])
            formatted_authors.append(f"{last}, {initials}" if initials else last)

        if len(authors) > 3:
            auth_str = ", ".join(formatted_authors) + ", et al."
        elif len(formatted_authors) == 2:
            auth_str = " & ".join(formatted_authors)
        else:
            auth_str = ", ".join(formatted_authors)

        doi_str = f" https://doi.org/{paper['doi']}" if paper.get("doi") else ""
        return f"{auth_str} ({year}). {title}. arXiv preprint arXiv:{paper.get('paper_id', '')}.{doi_str}"

    def to_ieee(self, paper: Dict[str, Any], index: int = 1) -> str:
        """Formats citation in IEEE numbered style."""
        authors = paper.get("authors", ["Anonymous"])
        year = paper.get("year", 2024)
        title = paper.get("title", "Untitled")
        auth_str = ", ".join(authors[:3]) + (" et al." if len(authors) > 3 else "")
        return f"[{index}] {auth_str}, \"{title},\" arXiv:{paper.get('paper_id', '')}, {year}."
