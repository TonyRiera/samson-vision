#!/usr/bin/env python3
"""Generate Samson Vision Use Cases PDF (v0.3.3)."""

from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    HRFlowable,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

# Brand palette (matches index.html / infographic)
NAVY = colors.HexColor("#0a0a0f")
GOLD = colors.HexColor("#c9a227")
GOLD_DIM = colors.HexColor("#8B6914")
FG = colors.HexColor("#1a1a24")
MUTED = colors.HexColor("#5a5560")
LIGHT_BG = colors.HexColor("#f8f7f4")
BORDER = colors.HexColor("#e0ddd4")

OUT_DOCS = Path(__file__).resolve().parent / "Samson_Vision_Use_Cases.pdf"
OUT_PUBLIC = OUT_DOCS.resolve().parents[1] / "Samson_Vision_Use_Cases.pdf"


def build_styles():
    base = getSampleStyleSheet()
    return {
        "title": ParagraphStyle(
            "title",
            parent=base["Heading1"],
            fontName="Helvetica-Bold",
            fontSize=26,
            leading=30,
            textColor=NAVY,
            alignment=TA_CENTER,
            spaceAfter=4,
        ),
        "tagline": ParagraphStyle(
            "tagline",
            parent=base["Normal"],
            fontName="Helvetica-Oblique",
            fontSize=13,
            leading=16,
            textColor=GOLD_DIM,
            alignment=TA_CENTER,
            spaceAfter=6,
        ),
        "oneliner": ParagraphStyle(
            "oneliner",
            parent=base["Normal"],
            fontName="Helvetica",
            fontSize=10.5,
            leading=14,
            textColor=MUTED,
            alignment=TA_CENTER,
            spaceAfter=14,
        ),
        "disclaimer": ParagraphStyle(
            "disclaimer",
            parent=base["Normal"],
            fontName="Helvetica-Oblique",
            fontSize=9,
            leading=12,
            textColor=colors.HexColor("#6b4e12"),
            alignment=TA_LEFT,
        ),
        "h2": ParagraphStyle(
            "h2",
            parent=base["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=11.5,
            leading=14,
            textColor=NAVY,
            spaceBefore=10,
            spaceAfter=6,
        ),
        "bullet": ParagraphStyle(
            "bullet",
            parent=base["Normal"],
            fontName="Helvetica",
            fontSize=9.5,
            leading=13,
            textColor=FG,
            leftIndent=14,
            spaceAfter=3,
        ),
        "body": ParagraphStyle(
            "body",
            parent=base["Normal"],
            fontName="Helvetica",
            fontSize=9,
            leading=12,
            textColor=FG,
            spaceAfter=4,
        ),
        "footer": ParagraphStyle(
            "footer",
            parent=base["Normal"],
            fontName="Helvetica",
            fontSize=8,
            leading=10,
            textColor=MUTED,
            alignment=TA_CENTER,
        ),
        "mono": ParagraphStyle(
            "mono",
            parent=base["Code"],
            fontName="Courier",
            fontSize=7.5,
            leading=10,
            textColor=FG,
            backColor=colors.HexColor("#eeece6"),
            borderPadding=6,
            spaceAfter=8,
        ),
        "link": ParagraphStyle(
            "link",
            parent=base["Normal"],
            fontName="Helvetica",
            fontSize=9,
            leading=12,
            textColor=GOLD_DIM,
            alignment=TA_CENTER,
        ),
    }


def gold_rule():
    return HRFlowable(width="100%", thickness=1.5, color=GOLD, spaceBefore=4, spaceAfter=10)


def section_table(data, col_widths):
    t = Table(data, colWidths=col_widths, repeatRows=1)
    t.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), NAVY),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 8),
                ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
                ("TEXTCOLOR", (0, 1), (-1, -1), FG),
                ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, LIGHT_BG]),
                ("GRID", (0, 0), (-1, -1), 0.4, BORDER),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
            ]
        )
    )
    return t


def disclaimer_box(styles):
    text = (
        "<b>Early release — honest scope.</b> Samson Vision is <b>not</b> a replacement "
        "for native multimodal vision. It is a cheap, auditable bridge: structured text "
        "so text-only LLMs can reason over screenshots and UI. Benchmarks use "
        "<b>6/6 binary signals</b>, not 100% visual quality claims."
    )
    inner = Table([[Paragraph(text, styles["disclaimer"])]], colWidths=[6.8 * inch])
    inner.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#fff8e6")),
                ("BOX", (0, 0), (-1, -1), 1, GOLD),
                ("LEFTPADDING", (0, 0), (-1, -1), 10),
                ("RIGHTPADDING", (0, 0), (-1, -1), 10),
                ("TOPPADDING", (0, 0), (-1, -1), 8),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
            ]
        )
    )
    return inner


def make_story(styles):
    story = []
    story.append(Spacer(1, 0.15 * inch))
    story.append(Paragraph("Samson Vision", styles["title"]))
    story.append(Paragraph("Visual-to-text bridge for AI agents", styles["tagline"]))
    story.append(
        Paragraph(
            "Structured <b>SVP</b> (SAMSON_VISION_PACK) for text-only LLMs — "
            "screenshots, documents, and UI without native vision APIs.",
            styles["oneliner"],
        )
    )
    story.append(gold_rule())
    story.append(disclaimer_box(styles))
    story.append(Spacer(1, 0.12 * inch))

    story.append(Paragraph("Use Cases", styles["h2"]))
    for title, desc in [
        ("Web screenshots", "Capture page structure, headlines, and navigation for agent reasoning."),
        ("Dashboards & analytics", "Extract KPIs, chart labels, and layout from BI screens."),
        ("Documents & OCR", "Scanned PDFs and forms — readable text plus spatial layout."),
        ("Form & UI review", "Fields, buttons, states — coordinate-aware for automation agents."),
        ("Error screens & logs", "Stack traces and alert dialogs as structured, searchable text."),
        ("Visual QA / CI", "Versionable SVP diffs for regression checks without vision APIs."),
    ]:
        story.append(
            Paragraph(
                f'<font color="#c9a227">▸</font> <b>{title}</b> — {desc}',
                styles["bullet"],
            )
        )

    story.append(Spacer(1, 0.08 * inch))
    story.append(Paragraph("What SVP Delivers", styles["h2"]))
    for item in [
        "OCR text with position & confidence (Tesseract)",
        "Layout map, visual hierarchy & object regions (OpenCV)",
        "ASCII representation (8 styles) + color map + density bands",
        "Pixel coordinates (0–100 scale) for click/automation hints",
        "Anti-hallucination rules — auditable, deterministic pipeline (0% AI at generation)",
    ]:
        story.append(Paragraph(f"• {item}", styles["bullet"]))

    story.append(Spacer(1, 0.1 * inch))
    story.append(Paragraph("Integration Modes", styles["h2"]))
    story.append(
        section_table(
            [
                ["Mode", "Stack", "Best for"],
                ["A — Text only", "SVP + text LLM", "Cheap agents, OCR/layout, CI diffs"],
                [
                    "B — SVP + subagent",
                    "Orchestrator reads SVP → vision subagent validates",
                    "UI review, accessibility, regressions",
                ],
                [
                    "C — Native vision",
                    "Multimodal model on raw image",
                    "Photos, logos, fine detail (fidelity > cost)",
                ],
            ],
            [1.1 * inch, 2.5 * inch, 3.2 * inch],
        )
    )

    story.append(Spacer(1, 0.12 * inch))
    story.append(Paragraph("Costs (per query, not monthly)", styles["h2"]))
    story.append(
        Paragraph(
            "SVP generation is <b>local & free</b> (compute only) — no per-image API. "
            "Interpretation uses standard text tokens (~1,700 in + 400 out per query).",
            styles["body"],
        )
    )
    story.append(
        section_table(
            [
                ["Approach", "Example", "Cost / query", "Notes"],
                ["SVP gen only", "samson-vision CLI", "$0", "Local: numpy + OpenCV + Tesseract"],
                ["SVP + text LLM", "MiniMax-M2.1", "$0.0008", "6/6 signals on benchmark"],
                ["SVP + text LLM", "GPT-4o-mini", "~$0.0005", "Solid text interpreter"],
                ["Direct vision", "GPT-4o", "~$0.008", "Native multimodal — 4–10× costlier"],
                ["Direct vision", "MiniMax-M3", "~$0.003", "Better for photos; higher per-call cost"],
            ],
            [1.35 * inch, 1.35 * inch, 0.95 * inch, 3.15 * inch],
        )
    )
    story.append(
        Paragraph(
            "<i>Text agent + cached SVP vs. sending every image to a vision model: "
            "fewer multimodal calls, predictable token billing.</i>",
            styles["body"],
        )
    )

    story.append(Spacer(1, 0.14 * inch))
    story.append(Paragraph("Install", styles["h2"]))
    story.append(
        Paragraph(
            'pip install "samson-vision[dev] @ '
            'git+https://github.com/TonyRiera/samson-vision.git@v0.3.3"',
            styles["mono"],
        )
    )
    story.append(
        Paragraph(
            '<link href="https://github.com/TonyRiera/samson-vision" color="#8B6914">'
            "github.com/TonyRiera/samson-vision</link>",
            styles["link"],
        )
    )
    story.append(Spacer(1, 0.2 * inch))
    story.append(gold_rule())
    story.append(
        Paragraph("MIT License &nbsp;|&nbsp; Early Release &nbsp;|&nbsp; Tony Riera", styles["footer"])
    )
    return story


def main():
    styles = build_styles()
    for out_path in (OUT_DOCS, OUT_PUBLIC):
        out_path.parent.mkdir(parents=True, exist_ok=True)
        doc = SimpleDocTemplate(
            str(out_path),
            pagesize=letter,
            leftMargin=0.65 * inch,
            rightMargin=0.65 * inch,
            topMargin=0.55 * inch,
            bottomMargin=0.5 * inch,
            title="Samson Vision — Use Cases",
            author="Tony Riera",
            subject="Samson Vision v0.3.3 Use Cases",
        )
        doc.build(make_story(styles))
        print(f"Wrote: {out_path}")


if __name__ == "__main__":
    main()
