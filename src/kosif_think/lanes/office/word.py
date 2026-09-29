"""
Microsoft Word Document Engine for KOSIF Think.
Creates authentic OpenXML .docx documents and converts Markdown to Word:
- Headings (H1, H2, H3), styled body paragraphs, bold, italic
- Multi-column tables with headers and cell borders
- Bulleted and numbered lists
- Callout quote boxes and highlight callouts
- Pure Python using standard library zipfile & xml. Zero external dependencies.
"""

from typing import Dict, Any, List, Optional
import zipfile
import io
import os
import re

class WordDocumentBuilder:
    """Builds native OpenXML Microsoft Word (.docx) documents."""

    def __init__(self, title: str = "Document"):
        self.title = title
        self.paragraphs: List[Dict[str, Any]] = []
        self.tables: List[Dict[str, Any]] = []
        self._body_xml_parts: List[str] = []

    def add_heading(self, text: str, level: int = 1):
        """Adds a heading (level 1-3)."""
        style = f"Heading{level}"
        size = 36 if level == 1 else (28 if level == 2 else 24)
        color = "1F497D" if level == 1 else "595959"
        xml = (
            f'<w:p><w:pPr><w:pStyle w:val="{style}"/><w:spacing w:before="240" w:after="120"/></w:pPr>'
            f'<w:r><w:rPr><w:b/><w:color w:val="{color}"/><w:sz w:val="{size}"/></w:rPr>'
            f'<w:t>{self._escape(text)}</w:t></w:r></w:p>'
        )
        self._body_xml_parts.append(xml)

    def add_paragraph(self, text: str, bold: bool = False, italic: bool = False, color: Optional[str] = None):
        """Adds a standard text paragraph."""
        rpr_parts = []
        if bold:
            rpr_parts.append("<w:b/>")
        if italic:
            rpr_parts.append("<w:i/>")
        if color:
            rpr_parts.append(f'<w:color w:val="{color}"/>')
        rpr = f"<w:rPr>{''.join(rpr_parts)}</w:rPr>" if rpr_parts else ""

        xml = (
            f'<w:p><w:pPr><w:spacing w:after="160" w:line="276" w:lineRule="auto"/></w:pPr>'
            f'<w:r>{rpr}<w:t>{self._escape(text)}</w:t></w:r></w:p>'
        )
        self._body_xml_parts.append(xml)

    def add_bullet_point(self, text: str):
        """Adds a bulleted list item."""
        xml = (
            f'<w:p><w:pPr><w:pStyle w:val="ListBullet"/><w:spacing w:after="80"/></w:pPr>'
            f'<w:r><w:t>• {self._escape(text)}</w:t></w:r></w:p>'
        )
        self._body_xml_parts.append(xml)

    def add_callout(self, text: str, title: str = "NOTE"):
        """Adds an alert or callout box."""
        xml = (
            f'<w:p><w:pPr><w:pBdr><w:left w:val="single" w:sz="24" w:space="15" w:color="0078D4"/></w:pBdr>'
            f'<w:shd w:val="clear" w:color="auto" w:fill="F0F4F8"/><w:spacing w:before="160" w:after="160"/></w:pPr>'
            f'<w:r><w:rPr><w:b/><w:color w:val="0078D4"/></w:rPr><w:t>[{title}] </w:t></w:r>'
            f'<w:r><w:t>{self._escape(text)}</w:t></w:r></w:p>'
        )
        self._body_xml_parts.append(xml)

    def add_table(self, headers: List[str], rows: List[List[str]]):
        """Adds a formatted data table with header styling."""
        table_xml = ['<w:tbl><w:tblPr><w:tblW w:w="5000" w:type="pct"/><w:tblBorders><w:top w:val="single" w:sz="4" w:space="0" w:color="CCCCCC"/><w:bottom w:val="single" w:sz="4" w:space="0" w:color="CCCCCC"/><w:insideH w:val="single" w:sz="4" w:space="0" w:color="EEEEEE"/></w:tblBorders></w:tblPr>']

        # Header Row
        table_xml.append('<w:tr><w:trPr><w:tblHeader/></w:trPr>')
        for h in headers:
            table_xml.append(
                f'<w:tc><w:tcPr><w:shd w:val="clear" w:color="auto" w:fill="003366"/></w:tcPr>'
                f'<w:p><w:r><w:rPr><w:b/><w:color w:val="FFFFFF"/></w:rPr><w:t>{self._escape(h)}</w:t></w:r></w:p></w:tc>'
            )
        table_xml.append('</w:tr>')

        # Data Rows
        for r_idx, row in enumerate(rows):
            fill = "F9FBFD" if r_idx % 2 == 1 else "FFFFFF"
            table_xml.append('<w:tr>')
            for cell in row:
                table_xml.append(
                    f'<w:tc><w:tcPr><w:shd w:val="clear" w:color="auto" w:fill="{fill}"/></w:tcPr>'
                    f'<w:p><w:r><w:t>{self._escape(str(cell))}</w:t></w:r></w:p></w:tc>'
                )
            table_xml.append('</w:tr>')

        table_xml.append('</w:tbl>')
        self._body_xml_parts.append(''.join(table_xml))

    def markdown_to_docx(self, markdown_text: str):
        """Converts Markdown text into formatted Word document elements."""
        lines = markdown_text.splitlines()
        in_table = False
        table_headers: List[str] = []
        table_rows: List[List[str]] = []

        for line in lines:
            s_line = line.strip()
            if not s_line:
                if in_table and table_headers:
                    self.add_table(table_headers, table_rows)
                    in_table = False
                    table_headers, table_rows = [], []
                continue

            if s_line.startswith("# "):
                self.add_heading(s_line[2:], level=1)
            elif s_line.startswith("## "):
                self.add_heading(s_line[3:], level=2)
            elif s_line.startswith("### "):
                self.add_heading(s_line[4:], level=3)
            elif s_line.startswith("> "):
                self.add_callout(s_line[2:])
            elif s_line.startswith("- ") or s_line.startswith("* "):
                self.add_bullet_point(s_line[2:])
            elif "|" in s_line:
                # Table row
                parts = [p.strip() for p in s_line.split("|")[1:-1]]
                if all(set(p) <= set("-: ") for p in parts if p):
                    continue  # Divider line
                if not in_table:
                    in_table = True
                    table_headers = parts
                else:
                    table_rows.append(parts)
            else:
                self.add_paragraph(s_line)

        if in_table and table_headers:
            self.add_table(table_headers, table_rows)

    def save(self, filepath: str) -> str:
        """Packages OpenXML archive and writes .docx file to disk."""
        abs_path = os.path.abspath(filepath)
        os.makedirs(os.path.dirname(abs_path) or ".", exist_ok=True)

        body_content = "".join(self._body_xml_parts)
        doc_xml = (
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
            f'<w:body>{body_content}'
            '<w:sectPr><w:pgSz w:w="11906" w:h="16838"/><w:pgMar w:top="1440" w:right="1440" w:bottom="1440" w:left="1440"/></w:sectPr>'
            '</w:body></w:document>'
        )

        content_types = (
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
            '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
            '<Default Extension="xml" ContentType="application/xml"/>'
            '<Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>'
            '</Types>'
        )

        rels = (
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
            '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>'
            '</Relationships>'
        )

        with zipfile.ZipFile(abs_path, 'w', compression=zipfile.ZIP_DEFLATED) as z:
            z.writestr("[Content_Types].xml", content_types)
            z.writestr("_rels/.rels", rels)
            z.writestr("word/document.xml", doc_xml)

        return abs_path

    def _escape(self, text: str) -> str:
        return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")
