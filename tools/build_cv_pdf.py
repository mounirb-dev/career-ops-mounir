#!/usr/bin/env python3
"""Convierte un CV en Markdown (formato de cv.md) a un PDF compacto de 1 pagina.

Uso: python3 tools/build_cv_pdf.py cvs/AAAA-MM-DD_empresa_puesto.md [salida.pdf]
Solo usa fuentes estandar de reportlab (Helvetica): el PDF pesa ~3-6 KB, asi que
su base64 cabe sin problema en el campo `attachments` de Gmail send_message.
Requiere: pip install reportlab
"""
import re
import sys
from xml.sax.saxutils import escape

from reportlab.lib.colors import HexColor
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import HRFlowable, KeepTogether, Paragraph, SimpleDocTemplate, Spacer

NAVY, BLUE, GRAY = HexColor('#0f172a'), HexColor('#2563eb'), HexColor('#4b5563')


def styles(scale):
    f = lambda n: round(n * scale, 2)
    return {
        'title': ParagraphStyle('t', fontName='Helvetica-Bold', fontSize=f(24), leading=f(27), textColor=NAVY),
        'sub': ParagraphStyle('s', fontName='Helvetica', fontSize=f(12.5), leading=f(16), textColor=BLUE),
        'contact': ParagraphStyle('c', fontName='Helvetica', fontSize=f(9), leading=f(12.5), textColor=GRAY),
        'h': ParagraphStyle('h', fontName='Helvetica-Bold', fontSize=f(11.5), leading=f(14), textColor=NAVY,
                            spaceBefore=f(8), spaceAfter=f(3)),
        'body': ParagraphStyle('b', fontName='Helvetica', fontSize=f(9.1), leading=f(12.2), textColor=NAVY),
        'entry': ParagraphStyle('e', fontName='Helvetica-Bold', fontSize=f(10), leading=f(13), textColor=NAVY,
                                spaceBefore=f(2)),
        'meta': ParagraphStyle('m', fontName='Helvetica-Oblique', fontSize=f(8.6), leading=f(11.5), textColor=GRAY),
        'bullet': ParagraphStyle('bl', fontName='Helvetica', fontSize=f(9.1), leading=f(12.2), textColor=NAVY,
                                 leftIndent=10, firstLineIndent=-10, spaceAfter=f(1.5)),
    }


def inline(text):
    """Escapa XML y convierte **negrita** / *cursiva* de Markdown."""
    t = escape(text.strip())
    t = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', t)
    t = re.sub(r'(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)', r'<i>\1</i>', t)
    return re.sub(r'`(.+?)`', r'\1', t)


def build(md_path, out_path, scale):
    st = styles(scale)
    lines = open(md_path, encoding='utf-8').read().splitlines()
    story, first_para_after_title = [], 0
    in_header = True
    for raw in lines:
        line = raw.rstrip()
        if not line.strip():
            continue
        if line.startswith('# '):
            story.append(Paragraph(inline(line[2:]), st['title']))
            story.append(Spacer(1, 2))
            first_para_after_title = 1
        elif line.startswith('## '):
            if in_header:
                story.append(Spacer(1, 4))
                story.append(HRFlowable(width='100%', thickness=1.2, color=BLUE, spaceAfter=3))
                in_header = False
            story.append(Paragraph(inline(line[3:]).upper(), st['h']))
        elif line.startswith('### '):
            title, _, meta = line[4:].partition('|')
            block = [Paragraph(inline(title), st['entry'])]
            if meta.strip():
                block.append(Paragraph(inline(meta), st['meta']))
            story.append(KeepTogether(block))
        elif re.match(r'^\s*[-*] ', line):
            story.append(Paragraph('&bull;&nbsp;&nbsp;' + inline(re.sub(r'^\s*[-*] ', '', line)), st['bullet']))
        elif in_header and first_para_after_title == 1:
            story.append(Paragraph(inline(line), st['sub']))
            story.append(Spacer(1, 3))
            first_para_after_title = 2
        elif in_header:
            story.append(Paragraph(inline(line), st['contact']))
        else:
            story.append(Paragraph(inline(line), st['body']))
    doc = SimpleDocTemplate(out_path, pagesize=A4, leftMargin=52, rightMargin=52, topMargin=30, bottomMargin=26,
                            title='Mounir Bella - CV', author='Mounir Bella')
    doc.build(story)


def page_count(path):
    return len(re.findall(rb'/Type\s*/Page[^s]', open(path, 'rb').read()))


if __name__ == '__main__':
    import os
    src = sys.argv[1]
    out = sys.argv[2] if len(sys.argv) > 2 else re.sub(r'\.md$', '.pdf', src)
    for scale in (1.0, 0.94, 0.88, 0.82, 0.76):  # reduce el tamano hasta que quepa en 1 pagina
        build(src, out, scale)
        if page_count(out) == 1:
            break
    print(f'ok {out} pages={page_count(out)} bytes={os.path.getsize(out)}')
