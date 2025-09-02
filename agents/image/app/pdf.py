import os
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet

FILE_STORE = os.environ.get("FILE_STORE","/data")

def render_pdf(items, worksheet_id: str) -> str:
    styles = getSampleStyleSheet()
    doc_path = os.path.join(FILE_STORE, f"{worksheet_id}.pdf")
    doc = SimpleDocTemplate(doc_path, pagesize=A4)
    story = []
    story.append(Paragraph("Generated Worksheet", styles["Heading1"]))
    story.append(Spacer(1,12))
    for i,item in enumerate(items,1):
        story.append(Paragraph(f"Q{i}. ({item.type}) {item.q}", styles["Normal"]))
        if item.options:
            for opt in item.options:
                story.append(Paragraph(f"- {opt}", styles["Normal"]))
        story.append(Spacer(1,12))
    doc.build(story)
    return doc_path
