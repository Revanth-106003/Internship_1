"""
report_generator.py
-------------------
Generates high-quality, professional downloadable PDF (via ReportLab) and Word DOCX
(via python-docx) reports using the validated ComparisonResult.
"""

import io
from datetime import datetime
from typing import Any, Dict, List, Optional

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.platypus import (
    HRFlowable,
    KeepTogether,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from comparison import ComparisonResult


class NumberedCanvas(canvas.Canvas):
    """
    Two-pass canvas to dynamically compute and display running headers and
    footers with total page count: 'Page X of Y'.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count: int):
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#64748b"))

        # Header (pages after cover/first page)
        if self._pageNumber > 1:
            self.drawString(54, 755, "AI Document Comparison Assistant — Formal Analysis Report")
            self.setStrokeColor(colors.HexColor("#e2e8f0"))
            self.setLineWidth(0.5)
            self.line(54, 750, 558, 750)

        # Footer (all pages)
        self.setStrokeColor(colors.HexColor("#e2e8f0"))
        self.setLineWidth(0.5)
        self.line(54, 45, 558, 45)

        footer_text = "AI Document Comparison Assistant • Strict Evidence Grounding"
        page_str = f"Page {self._pageNumber} of {page_count}"
        self.drawString(54, 32, footer_text)
        self.drawRightString(558, 32, page_str)
        self.restoreState()


def safe_text(text: Optional[str]) -> str:
    """Escapes XML entities so ReportLab Paragraph doesn't error on raw characters."""
    if not text:
        return "Not found in the provided text."
    cleaned = str(text).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    return cleaned


def build_pdf_report(comparison: ComparisonResult) -> bytes:
    """
    Builds a beautifully structured, comprehensive PDF report from the validated comparison.
    Returns bytes of the generated PDF.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54,
    )

    styles = getSampleStyleSheet()

    # Custom Palette
    c_primary = colors.HexColor("#0f172a")     # Deep navy
    c_secondary = colors.HexColor("#1e40af")   # Vivid blue
    c_accent = colors.HexColor("#0d9488")      # Teal
    c_dark = colors.HexColor("#334155")        # Slate body
    c_light_bg = colors.HexColor("#f8fafc")    # Light off-white
    c_border = colors.HexColor("#cbd5e1")      # Border grey
    c_tag_added = colors.HexColor("#10b981")   # Emerald
    c_tag_mod = colors.HexColor("#f59e0b")     # Amber
    c_tag_rem = colors.HexColor("#ef4444")     # Rose

    # Paragraph Styles
    title_style = ParagraphStyle(
        "DocTitle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=22,
        leading=26,
        textColor=c_primary,
        spaceAfter=4,
    )

    subtitle_style = ParagraphStyle(
        "DocSubtitle",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=10,
        leading=14,
        textColor=colors.HexColor("#64748b"),
        spaceAfter=15,
    )

    h1_style = ParagraphStyle(
        "Heading1_Custom",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=14,
        leading=18,
        textColor=c_secondary,
        spaceBefore=14,
        spaceAfter=6,
        keepWithNext=True,
    )

    h2_style = ParagraphStyle(
        "Heading2_Custom",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=11,
        leading=15,
        textColor=c_primary,
        spaceBefore=10,
        spaceAfter=4,
        keepWithNext=True,
    )

    body_style = ParagraphStyle(
        "Body_Custom",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9,
        leading=13,
        textColor=c_dark,
        spaceAfter=4,
    )

    bullet_style = ParagraphStyle(
        "Bullet_Custom",
        parent=body_style,
        leftIndent=15,
        bulletIndent=5,
        spaceAfter=3,
    )

    quote_style = ParagraphStyle(
        "Quote_Custom",
        parent=styles["Normal"],
        fontName="Helvetica-Oblique",
        fontSize=8.5,
        leading=12,
        textColor=colors.HexColor("#475569"),
        leftIndent=10,
        spaceAfter=2,
    )

    table_header_style = ParagraphStyle(
        "TableHeader",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=8.5,
        leading=11,
        textColor=colors.white,
    )

    table_cell_style = ParagraphStyle(
        "TableCell",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8,
        leading=11,
        textColor=c_dark,
    )

    table_cell_bold = ParagraphStyle(
        "TableCellBold",
        parent=table_cell_style,
        fontName="Helvetica-Bold",
        textColor=c_primary,
    )

    story = []

    # ---------------------------------------------------------
    # 1. Header Banner
    # ---------------------------------------------------------
    story.append(Paragraph("AI Document Comparison Report", title_style))
    now_str = datetime.now().strftime("%B %d, %Y • %H:%M:%S UTC")
    story.append(
        Paragraph(
            f"<b>Generated:</b> {now_str} &nbsp;|&nbsp; <b>Tool:</b> AI Document Comparison Assistant &nbsp;|&nbsp; <b>Model:</b> Gemini",
            subtitle_style,
        )
    )
    story.append(HRFlowable(width="100%", thickness=1.5, color=c_secondary, spaceAfter=14))

    # ---------------------------------------------------------
    # 2. Executive Overview & Document Metadata
    # ---------------------------------------------------------
    story.append(Paragraph("1. Executive Summary & Document Overview", h1_style))

    meta_data = [
        [
            Paragraph("<b>Metric / Parameter</b>", table_header_style),
            Paragraph("<b>Document A</b>", table_header_style),
            Paragraph("<b>Document B</b>", table_header_style),
        ],
        [
            Paragraph("<b>Filename</b>", table_cell_bold),
            Paragraph(safe_text(comparison.doc_a_summary.filename), table_cell_style),
            Paragraph(safe_text(comparison.doc_b_summary.filename), table_cell_style),
        ],
        [
            Paragraph("<b>Primary Purpose</b>", table_cell_bold),
            Paragraph(safe_text(comparison.doc_a_summary.main_purpose), table_cell_style),
            Paragraph(safe_text(comparison.doc_b_summary.main_purpose), table_cell_style),
        ],
    ]

    meta_table = Table(meta_data, colWidths=[120, 192, 192])
    meta_table.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), c_primary),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("ALIGN", (0, 0), (-1, -1), "LEFT"),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("INNERGRID", (0, 0), (-1, -1), 0.5, c_border),
            ("BOX", (0, 0), (-1, -1), 1, c_secondary),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [c_light_bg, colors.white]),
        ])
    )
    story.append(meta_table)
    story.append(Spacer(1, 10))

    # Executive Overview Narrative
    story.append(Paragraph("<b>Executive Synthesis:</b>", h2_style))
    story.append(Paragraph(safe_text(comparison.overall_conclusion.neutral_summary), body_style))
    story.append(Spacer(1, 10))

    # ---------------------------------------------------------
    # 3. Individual Document Summaries
    # ---------------------------------------------------------
    story.append(Paragraph("2. Individual Document Profiles", h1_style))

    # Document A Card
    story.append(Paragraph(f"<b>Document A: {safe_text(comparison.doc_a_summary.filename)}</b>", h2_style))
    story.append(Paragraph(f"<b>Summary:</b> {safe_text(comparison.doc_a_summary.executive_summary)}", body_style))

    if comparison.doc_a_summary.important_requirements:
        story.append(Paragraph("<b>Key Requirements (Doc A):</b>", body_style))
        for req in comparison.doc_a_summary.important_requirements[:5]:
            story.append(Paragraph(f"• {safe_text(req)}", bullet_style))

    story.append(Spacer(1, 6))

    # Document B Card
    story.append(Paragraph(f"<b>Document B: {safe_text(comparison.doc_b_summary.filename)}</b>", h2_style))
    story.append(Paragraph(f"<b>Summary:</b> {safe_text(comparison.doc_b_summary.executive_summary)}", body_style))

    if comparison.doc_b_summary.important_requirements:
        story.append(Paragraph("<b>Key Requirements (Doc B):</b>", body_style))
        for req in comparison.doc_b_summary.important_requirements[:5]:
            story.append(Paragraph(f"• {safe_text(req)}", bullet_style))

    story.append(Spacer(1, 12))

    # ---------------------------------------------------------
    # 4. Verified Differences & Discrepancies
    # ---------------------------------------------------------
    story.append(Paragraph("3. Verified Differences & Document Modifications", h1_style))
    story.append(
        Paragraph(
            "Every modification, addition, removal, and contradiction identified between Document A and Document B is itemized below with page attribution.",
            body_style,
        )
    )
    story.append(Spacer(1, 6))

    if comparison.differences:
        diff_table_data = [
            [
                Paragraph("<b>Category / Topic</b>", table_header_style),
                Paragraph("<b>Document A (State & Page)</b>", table_header_style),
                Paragraph("<b>Document B (State & Page)</b>", table_header_style),
                Paragraph("<b>Impact & Explanation</b>", table_header_style),
            ]
        ]
        for diff in comparison.differences:
            cat_topic = f"<b>[{safe_text(diff.category)}]</b><br/>{safe_text(diff.topic)}"
            doc_a_cell = f"{safe_text(diff.doc_a_state)}<br/><font color='#64748b' size='7'><i>Source: {safe_text(diff.doc_a_page)}</i></font>"
            doc_b_cell = f"{safe_text(diff.doc_b_state)}<br/><font color='#64748b' size='7'><i>Source: {safe_text(diff.doc_b_page)}</i></font>"
            impact_cell = safe_text(diff.description)
            if diff.quote_excerpt and diff.quote_excerpt != "Not found in the provided text.":
                impact_cell += f"<br/><font color='#475569' size='7'><i>Excerpt: \"{safe_text(diff.quote_excerpt)}\"</i></font>"

            diff_table_data.append([
                Paragraph(cat_topic, table_cell_style),
                Paragraph(doc_a_cell, table_cell_style),
                Paragraph(doc_b_cell, table_cell_style),
                Paragraph(impact_cell, table_cell_style),
            ])

        diff_table = Table(diff_table_data, colWidths=[110, 125, 125, 144])
        diff_table.setStyle(
            TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1e3a8a")),
                ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("INNERGRID", (0, 0), (-1, -1), 0.5, c_border),
                ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#1e3a8a")),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [c_light_bg, colors.white]),
            ])
        )
        story.append(diff_table)
    else:
        story.append(Paragraph("<i>No significant differences were detected between the two documents.</i>", body_style))

    story.append(Spacer(1, 12))

    # ---------------------------------------------------------
    # 5. Verified Similarities
    # ---------------------------------------------------------
    story.append(Paragraph("4. Common Topics & Unchanged Content (Similarities)", h1_style))

    if comparison.similarities:
        for sim in comparison.similarities:
            sim_header = f"<b>• {safe_text(sim.topic)}</b> (Doc A: {safe_text(sim.doc_a_page)} | Doc B: {safe_text(sim.doc_b_page)})"
            story.append(Paragraph(sim_header, body_style))
            story.append(Paragraph(safe_text(sim.description), bullet_style))
            if sim.quote_excerpt and sim.quote_excerpt != "Not found in the provided text.":
                story.append(Paragraph(f"<i>Quote:</i> \"{safe_text(sim.quote_excerpt)}\"", quote_style))
            story.append(Spacer(1, 3))
    else:
        story.append(Paragraph("<i>No notable matching points found.</i>", body_style))

    story.append(Spacer(1, 12))

    # ---------------------------------------------------------
    # 6. Key Details Comparison Table
    # ---------------------------------------------------------
    story.append(Paragraph("5. Key Operational Details Comparison", h1_style))

    if comparison.key_details:
        kd_table_data = [
            [
                Paragraph("<b>Operational Field</b>", table_header_style),
                Paragraph("<b>Document A</b>", table_header_style),
                Paragraph("<b>Document B</b>", table_header_style),
                Paragraph("<b>Status</b>", table_header_style),
            ]
        ]
        for kd in comparison.key_details:
            kd_table_data.append([
                Paragraph(f"<b>{safe_text(kd.field_name)}</b>", table_cell_style),
                Paragraph(safe_text(kd.doc_a_value), table_cell_style),
                Paragraph(safe_text(kd.doc_b_value), table_cell_style),
                Paragraph(f"<b>{safe_text(kd.status)}</b>", table_cell_style),
            ])

        kd_table = Table(kd_table_data, colWidths=[120, 150, 150, 84])
        kd_table.setStyle(
            TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), c_secondary),
                ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("INNERGRID", (0, 0), (-1, -1), 0.5, c_border),
                ("BOX", (0, 0), (-1, -1), 1, c_secondary),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [c_light_bg, colors.white]),
            ])
        )
        story.append(kd_table)

    story.append(Spacer(1, 14))

    # ---------------------------------------------------------
    # 7. Overall Conclusion & Actionable Items
    # ---------------------------------------------------------
    story.append(Paragraph("6. Overall Conclusions & Attention Areas", h1_style))
    story.append(Paragraph(f"<b>Core Shifts:</b> {safe_text(comparison.overall_conclusion.main_changes)}", body_style))
    story.append(Spacer(1, 4))

    if comparison.overall_conclusion.areas_requiring_attention:
        story.append(Paragraph("<b>Specific Areas Requiring Scrutiny:</b>", h2_style))
        for item in comparison.overall_conclusion.areas_requiring_attention:
            story.append(Paragraph(f"⚠️ {safe_text(item)}", bullet_style))

    story.append(Spacer(1, 10))

    # ---------------------------------------------------------
    # 8. Limitations, Caveats & Disclaimer
    # ---------------------------------------------------------
    story.append(Paragraph("7. Analysis Limitations & Governance Notice", h1_style))

    if comparison.limitations.unreadable_or_missing_content:
        for unc in comparison.limitations.unreadable_or_missing_content:
            story.append(Paragraph(f"• <b>Missing Content:</b> {safe_text(unc)}", bullet_style))

    if comparison.limitations.processing_notes:
        for note in comparison.limitations.processing_notes:
            story.append(Paragraph(f"• <b>Notice:</b> {safe_text(note)}", bullet_style))

    story.append(Spacer(1, 8))
    story.append(
        Paragraph(
            "<b>Scope & Informational Notice:</b> This comparison report was generated automatically by an AI document comparison assistant based solely on extracted text representations. It is intended for informational review and comparative productivity only. It does not replace professional legal, financial, or technical scrutiny.",
            quote_style,
        )
    )

    doc.build(story, canvasmaker=NumberedCanvas)
    return buffer.getvalue()


def build_docx_report(comparison: ComparisonResult) -> bytes:
    """
    Builds a Microsoft Word (.docx) document report from the validated comparison result.
    Returns bytes of the generated DOCX.
    """
    import docx
    from docx.shared import Inches, Pt, RGBColor
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    from docx.oxml import OxmlElement, parse_xml
    from docx.oxml.ns import nsdecls, qn

    doc = docx.Document()

    # Set Margins
    sections = doc.sections
    for section in sections:
        section.top_margin = Inches(0.8)
        section.bottom_margin = Inches(0.8)
        section.left_margin = Inches(0.8)
        section.right_margin = Inches(0.8)

    # Title
    title = doc.add_paragraph()
    title_run = title.add_run("AI Document Comparison Report")
    title_run.font.size = Pt(20)
    title_run.font.bold = True
    title_run.font.color.rgb = RGBColor(15, 23, 42)

    # Subtitle
    sub = doc.add_paragraph()
    now_str = datetime.now().strftime("%B %d, %Y at %H:%M:%S UTC")
    sub_run = sub.add_run(f"Generated on {now_str} • Powered by Google Gemini AI")
    sub_run.font.size = Pt(9.5)
    sub_run.font.color.rgb = RGBColor(100, 116, 139)

    doc.add_paragraph("―" * 55)

    # 1. Executive Summary
    h1 = doc.add_heading("1. Executive Summary & Overview", level=1)
    doc.add_paragraph(f"Document A: {comparison.doc_a_summary.filename}")
    doc.add_paragraph(f"Document B: {comparison.doc_b_summary.filename}")
    doc.add_paragraph(f"Conclusion: {comparison.overall_conclusion.neutral_summary}")

    # 2. Document Profiles
    doc.add_heading("2. Document Summaries", level=1)
    doc.add_heading(f"Document A: {comparison.doc_a_summary.filename}", level=2)
    doc.add_paragraph(f"Purpose: {comparison.doc_a_summary.main_purpose}")
    doc.add_paragraph(f"Summary: {comparison.doc_a_summary.executive_summary}")

    doc.add_heading(f"Document B: {comparison.doc_b_summary.filename}", level=2)
    doc.add_paragraph(f"Purpose: {comparison.doc_b_summary.main_purpose}")
    doc.add_paragraph(f"Summary: {comparison.doc_b_summary.executive_summary}")

    # 3. Differences Table
    doc.add_heading("3. Verified Differences & Modifications", level=1)
    if comparison.differences:
        table = doc.add_table(rows=1, cols=4)
        table.style = "Table Grid"
        hdr_cells = table.rows[0].cells
        hdr_cells[0].text = "Category & Topic"
        hdr_cells[1].text = "Document A State"
        hdr_cells[2].text = "Document B State"
        hdr_cells[3].text = "Impact & Explanation"

        for diff in comparison.differences:
            row_cells = table.add_row().cells
            row_cells[0].text = f"[{diff.category}]\n{diff.topic}"
            row_cells[1].text = f"{diff.doc_a_state}\n(Page: {diff.doc_a_page})"
            row_cells[2].text = f"{diff.doc_b_state}\n(Page: {diff.doc_b_page})"
            row_cells[3].text = diff.description

    # 4. Similarities
    doc.add_heading("4. Common Features & Similarities", level=1)
    for sim in comparison.similarities:
        p = doc.add_paragraph(style="List Bullet")
        p.add_run(f"{sim.topic} (Doc A: {sim.doc_a_page}, Doc B: {sim.doc_b_page}): ").bold = True
        p.add_run(sim.description)

    # 5. Key Details Table
    doc.add_heading("5. Key Operational Details Comparison", level=1)
    if comparison.key_details:
        kd_table = doc.add_table(rows=1, cols=4)
        kd_table.style = "Table Grid"
        k_hdr = kd_table.rows[0].cells
        k_hdr[0].text = "Operational Field"
        k_hdr[1].text = "Document A"
        k_hdr[2].text = "Document B"
        k_hdr[3].text = "Status"

        for kd in comparison.key_details:
            r = kd_table.add_row().cells
            r[0].text = kd.field_name
            r[1].text = kd.doc_a_value
            r[2].text = kd.doc_b_value
            r[3].text = kd.status

    # 6. Conclusion
    doc.add_heading("6. Conclusion & Attention Areas", level=1)
    doc.add_paragraph(f"Main Changes: {comparison.overall_conclusion.main_changes}")
    for item in comparison.overall_conclusion.areas_requiring_attention:
        p = doc.add_paragraph(style="List Bullet")
        p.add_run(f"Attention Required: {item}")

    # 7. Limitations
    doc.add_heading("7. Limitations & Disclaimers", level=1)
    for note in comparison.limitations.processing_notes:
        doc.add_paragraph(f"• {note}")

    doc.add_paragraph(
        "Disclaimer: This document is produced for comparative informational purposes only and does not constitute a legal determination."
    )

    buffer = io.BytesIO()
    doc.save(buffer)
    return buffer.getvalue()
