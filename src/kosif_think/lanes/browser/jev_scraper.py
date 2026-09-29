"""
Jev Intelligent Web Scraper & Structured Data Extractor.
Extracts tables, metadata, articles, and semantic Markdown from web pages.
Zero external dependencies. Pure Python.
"""

from typing import Dict, Any, List, Optional
import re
import html
import time

class JevWebScraper:
    """Extracts structured knowledge from HTML documents."""

    def extract_metadata(self, html_source: str) -> Dict[str, Any]:
        """Extracts title, meta tags, and OpenGraph headers."""
        title_m = re.search(r"<title[^>]*>(.*?)</title>", html_source, re.IGNORECASE | re.DOTALL)
        title = html.unescape(title_m.group(1)).strip() if title_m else "Untitled"

        def get_meta(attr: str, val: str) -> str:
            m = re.search(rf'<meta\s+[^>]*{attr}=["\']{val}["\'][^>]*content=["\']([^"\']*)["\']', html_source, re.IGNORECASE)
            if not m:
                m = re.search(rf'<meta\s+[^>]*content=["\']([^"\']*)["\'][^>]*{attr}=["\']{val}["\']', html_source, re.IGNORECASE)
            return html.unescape(m.group(1)).strip() if m else ""

        description = get_meta("name", "description") or get_meta("property", "og:description")
        og_title = get_meta("property", "og:title") or title
        og_image = get_meta("property", "og:image")

        return {
            "title": title,
            "description": description,
            "og_title": og_title,
            "og:title": og_title,
            "og_image": og_image,
            "og:image": og_image
        }

    def extract_tables(self, html_source: str) -> List[Dict[str, Any]]:
        """Parses HTML tables into structured lists of dictionaries."""
        tables = []
        table_pattern = re.compile(r"<table\b[^>]*>(.*?)</table>", re.IGNORECASE | re.DOTALL)

        for t_idx, t_match in enumerate(table_pattern.finditer(html_source)):
            t_content = t_match.group(1)
            # Headers
            headers = []
            for th_match in re.finditer(r"<th\b[^>]*>(.*?)</th>", t_content, re.IGNORECASE | re.DOTALL):
                clean_th = re.sub(r"<[^>]+>", " ", th_match.group(1))
                headers.append(html.unescape(clean_th).strip())

            # Rows
            rows = []
            for tr_match in re.finditer(r"<tr\b[^>]*>(.*?)</tr>", t_content, re.IGNORECASE | re.DOTALL):
                tr_content = tr_match.group(1)
                row_cells = []
                for td_match in re.finditer(r"<td\b[^>]*>(.*?)</td>", tr_content, re.IGNORECASE | re.DOTALL):
                    clean_td = re.sub(r"<[^>]+>", " ", td_match.group(1))
                    row_cells.append(html.unescape(clean_td).strip())

                if row_cells:
                    if headers and len(headers) == len(row_cells):
                        rows.append(dict(zip(headers, row_cells)))
                    else:
                        rows.append(row_cells)

            tables.append({
                "table_index": t_idx + 1,
                "headers": headers,
                "rows_count": len(rows),
                "rows": rows
            })

        return tables

    def html_to_markdown(self, html_source: str) -> str:
        """Converts HTML content into clean readable Markdown."""
        # Strip scripts, styles, comments
        text = re.sub(r"<(script|style|noscript)\b[^>]*>.*?</\1>", "", html_source, flags=re.IGNORECASE | re.DOTALL)
        text = re.sub(r"<!--.*?-->", "", text, flags=re.DOTALL)

        # Convert headings
        text = re.sub(r"<h1\b[^>]*>(.*?)</h1>", r"\n# \1\n", text, flags=re.IGNORECASE | re.DOTALL)
        text = re.sub(r"<h2\b[^>]*>(.*?)</h2>", r"\n## \1\n", text, flags=re.IGNORECASE | re.DOTALL)
        text = re.sub(r"<h3\b[^>]*>(.*?)</h3>", r"\n### \1\n", text, flags=re.IGNORECASE | re.DOTALL)

        # Convert links
        text = re.sub(r'<a\b[^>]*href=["\']([^"\']*)["\'][^>]*>(.*?)</a>', r"[\2](\1)", text, flags=re.IGNORECASE | re.DOTALL)

        # Convert bold / strong
        text = re.sub(r"<(b|strong)\b[^>]*>(.*?)</\1>", r"**\2**", text, flags=re.IGNORECASE | re.DOTALL)

        # Paragraphs & linebreaks
        text = re.sub(r"<p\b[^>]*>(.*?)</p>", r"\n\1\n", text, flags=re.IGNORECASE | re.DOTALL)
        text = re.sub(r"<br\s*/?>", "\n", text, flags=re.IGNORECASE)

        # Strip remaining tags
        text = re.sub(r"<[^>]+>", "", text)
        text = html.unescape(text)

        # Collapse excess whitespace
        lines = [line.strip() for line in text.splitlines()]
        cleaned_lines = []
        for line in lines:
            if line or (cleaned_lines and cleaned_lines[-1] != ""):
                cleaned_lines.append(line)

        return "\n".join(cleaned_lines).strip()
