import os
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

FILE_STORE = os.environ.get("FILE_STORE", "/data")
FONTS_DIR = os.path.join(os.path.dirname(__file__), "assets", "fonts")

# Register fonts once
pdfmetrics.registerFont(TTFont("NotoSans", os.path.join(FONTS_DIR, "NotoSans-Regular.ttf")))
pdfmetrics.registerFont(TTFont("NotoSansDevanagari", os.path.join(FONTS_DIR, "NotoSansDevanagari-Regular.ttf")))
pdfmetrics.registerFont(TTFont("NotoSansTamil", os.path.join(FONTS_DIR, "NotoSansTamil-Regular.ttf")))

def get_font_for_lang(lang: str) -> str:
    if lang == "hi":
        return "NotoSansDevanagari"
    elif lang == "ta":
        return "NotoSansTamil"
    return "NotoSans"

def render_pdf(items, worksheet_id: str, lang: str) -> str:
    styles = getSampleStyleSheet()
    font_name = get_font_for_lang(lang)

    styles["Normal"].fontName = font_name
    styles["Heading1"].fontName = font_name

    doc_path = os.path.join(FILE_STORE, f"{worksheet_id}.pdf")
    doc = SimpleDocTemplate(doc_path, pagesize=A4)

    story = []
    story.append(Paragraph(f"Generated Worksheet ({lang})", styles["Heading1"]))
    story.append(Spacer(1, 12))

    for i, item in enumerate(items, 1):
        story.append(Paragraph(f"Q{i}. ({item.type}) {item.q}", styles["Normal"]))
        if item.options:
            for opt in item.options:
                story.append(Paragraph(f"- {opt}", styles["Normal"]))
        story.append(Spacer(1, 12))

    doc.build(story)
    return doc_path
