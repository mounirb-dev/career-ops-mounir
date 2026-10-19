#!/usr/bin/env python3
"""Convierte un CV markdown de cvs/ a un PDF compacto (Helvetica, sin fuentes embebidas)
y escribe el base64 en <pdf>.b64 para pegarlo como adjunto en Gmail send_message.

Uso: python3 scripts/cv_pdf.py cvs/<archivo>.md [salida.pdf]
"""
import base64, re, sys
from pathlib import Path
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer

def inline(t):
    t = t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    return re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", t)

def build(md_path, pdf_path):
    base = ParagraphStyle("b", fontName="Helvetica", fontSize=9, leading=11.5)
    st = {
        "h1": ParagraphStyle("h1", parent=base, fontName="Helvetica-Bold", fontSize=18, leading=22),
        "h2": ParagraphStyle("h2", parent=base, fontName="Helvetica-Bold", fontSize=11, leading=14, spaceBefore=8, spaceAfter=2),
        "h3": ParagraphStyle("h3", parent=base, fontName="Helvetica-Bold", fontSize=9.5, spaceBefore=4),
        "li": ParagraphStyle("li", parent=base, leftIndent=10, bulletIndent=2, spaceAfter=1),
        "p": ParagraphStyle("p", parent=base, spaceAfter=3),
    }
    out = []
    for line in Path(md_path).read_text(encoding="utf-8").splitlines():
        s = line.strip()
        if not s:
            continue
        if s.startswith("### "): out.append(Paragraph(inline(s[4:]), st["h3"]))
        elif s.startswith("## "): out.append(Paragraph(inline(s[3:]), st["h2"]))
        elif s.startswith("# "): out.append(Paragraph(inline(s[2:]), st["h1"]))
        elif s.startswith(("- ", "* ")): out.append(Paragraph(inline(s[2:]), st["li"], bulletText="•"))
        else: out.append(Paragraph(inline(s), st["p"]))
    SimpleDocTemplate(str(pdf_path), pagesize=A4, leftMargin=16*mm, rightMargin=16*mm,
                      topMargin=14*mm, bottomMargin=14*mm, title="Mounir Bella - CV",
                      author="Mounir Bella").build(out)

if __name__ == "__main__":
    md = Path(sys.argv[1])
    pdf = Path(sys.argv[2]) if len(sys.argv) > 2 else md.with_suffix(".pdf")
    build(md, pdf)
    b64 = base64.b64encode(pdf.read_bytes()).decode()
    pdf.with_suffix(".pdf.b64").write_text(b64)
    print(f"{pdf} {pdf.stat().st_size} bytes | base64 {len(b64)} chars -> {pdf}.b64")
