import os, time, random, string, json
from typing import List, Dict, Any
from PyPDF2 import PdfReader
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

from openai import OpenAI
from .schemas import StudyPlanRequest, StudyPlanResponse, WeeklyItem

FILE_ROOT = os.environ.get("FILE_STORE", "/data")
OPENAI_MODEL = os.environ.get("STUDYPLAN_MODEL", "gpt-4o-mini")

_client = OpenAI()

# --------- Utils ---------
def make_id(prefix="plan"):
    ts = str(int(time.time()))
    rnd = "".join(random.choice("abcdefghijklmnopqrstuvwxyz0123456789") for _ in range(6))
    return f"{prefix}_{ts}{rnd}"

def read_pdf_text(file_id: str) -> str:
    # find by any extension (pdf required for studyplan)
    path_pdf = os.path.join(FILE_ROOT, f"{file_id}.pdf")
    if not os.path.exists(path_pdf):
        raise FileNotFoundError(f"Syllabus PDF not found at {path_pdf}")
    reader = PdfReader(path_pdf)
    chunks = []
    for page in reader.pages:
        try:
            chunks.append(page.extract_text() or "")
        except Exception:
            pass
    return "\n".join(chunks).strip()

def grades_compact(grades: List[str]) -> str:
    gs = sorted([g.strip() for g in grades if g.strip()])
    if not gs: return "unknown"
    # "3,4,5" -> "3to5" if contiguous, else "3-4-6"
    try:
        nums = sorted(set(int(x) for x in gs))
        if nums == list(range(nums[0], nums[-1] + 1)):
            return f"{nums[0]}to{nums[-1]}"
        return "-".join(str(x) for x in nums)
    except:
        return "-".join(gs)

# basic mapping to choose a likely font family; missing fonts will trigger .md fallback
LANG_FONT = {
    "en": ("NotoSans-Regular.ttf",),
    "hi": ("NotoSansDevanagari-Regular.ttf",),
    "mr": ("NotoSansDevanagari-Regular.ttf",),
    "ta": ("NotoSansTamil-Regular.ttf",),
}

def get_font_for_lang(lang: str):
    fonts_dir = os.path.join(os.path.dirname(__file__), "assets", "fonts")
    for fname in LANG_FONT.get(lang, LANG_FONT["en"]):
        p = os.path.join(fonts_dir, fname)
        if os.path.exists(p):
            return p
    return None

def translate_text(text: str, lang: str) -> str:
    """
    Use LLM to translate text into the target language.
    """
    if not text:
        return text
    resp = _client.chat.completions.create(
        model=OPENAI_MODEL,  # or use a smaller/cheaper model here
        messages=[
            {"role": "system", "content": f"You are a translator. Translate everything into {lang}. Do not explain, only translate."},
            {"role": "user", "content": text}
        ],
        temperature=0.2
    )
    return resp.choices[0].message.content.strip()

def translate_plan(plan: Dict[str, Any], lang: str) -> Dict[str, Any]:
    """
    Translate all text fields in the plan JSON into the target language.
    Keeps structure intact.
    """
    if lang.lower() == "en":
        return plan  # no translation needed

    translated = {}
    translated["overview"] = translate_text(plan.get("overview", ""), lang)

    weekly = []
    for wk in plan.get("weekly_outline", []):
        new_wk = {}
        new_wk["week"] = wk.get("week")
        new_wk["topics"] = [translate_text(t, lang) for t in wk.get("topics", [])]
        new_wk["activities"] = [translate_text(a, lang) for a in wk.get("activities", [])]
        new_wk["assessment"] = translate_text(wk.get("assessment", ""), lang)
        if wk.get("homework"):
            new_wk["homework"] = translate_text(wk.get("homework", ""), lang)
        # resources
        new_wk["resources"] = []
        for r in wk.get("resources", []):
            new_wk["resources"].append({
                "title": translate_text(r.get("title",""), lang),
                "platform": r.get("platform",""),  # keep platform names as-is
                "search_query": translate_text(r.get("search_query",""), lang)
            })
        weekly.append(new_wk)

    translated["weekly_outline"] = weekly
    return translated


# --------- Prompting ---------
PEDAGOGY_PRINCIPLES = """
You are a helpful teaching assistant for multi-grade rural Indian classrooms.
Constraints:
- Limited devices/internet; prioritize low/no-cost, offline-friendly activities.
- Different student levels in same class; include tiered tasks (Easy/Medium/Hard).
- Encourage peer learning and simple materials (paper, seeds, sticks, chalk, local stories).
- Use formative checks (1-minute exit tickets, oral Q&A).
"""

RESOURCE_GUIDE = """
When suggesting resources, prefer *platform + search_query* over hard URLs.
Examples:
- platform: YouTube, search_query: "Khan Academy Hindi fractions"
- platform: DIKSHA, search_query: "NCERT Class 4 EVS"
- platform: OER Commons, search_query: "Grade 5 measurement activities"
Provide 2-4 suggestions per week, each with: title, platform, search_query.
"""

def build_messages(syllabus_text: str, req: StudyPlanRequest) -> list:
    grades_str = ", ".join(req.grades)
    return [
        {"role": "system",
         "content": f"""{PEDAGOGY_PRINCIPLES}
{RESOURCE_GUIDE}
You are a multilingual teaching assistant. 
Respond ONLY in the target language: {req.target_language}.
All outputs MUST be written entirely in: {req.target_language}.
If {req.target_language} is not English, do NOT mix with English. 
Translate the overview, topics, activities, assessment, homework, and resources. 
Output STRICT JSON with keys: overview (string), weekly_outline (array of weeks), no markdown.
Week object keys: week (int), topics (array of strings), activities (array of strings), assessment (string), homework (string, optional), resources (array of objects: title, platform, search_query).
Keep topics concise; align with the syllabus text supplied.
"""},
        {"role": "user",
         "content": f"""SYLLABUS (raw text):
\"\"\"{syllabus_text[:15000]}\"\"\"  # first 15k chars to be safe

REQUEST:
- grades: {grades_str}
- duration_weeks: {req.duration_weeks}
- constraints: {json.dumps(req.constraints or {}, ensure_ascii=False)}

TASK:
1) Identify teachable topics from the syllabus suited for these grades.
2) Distribute into {req.duration_weeks} weeks.
3) For each week, give 3-5 activities (tiered difficulty, low-resource), 1 assessment idea, optional homework.
4) Provide 2-4 resource suggestions (title, platform, search_query). Avoid URLs.
"""}
    ]

def llm_plan(syllabus_text: str, req: StudyPlanRequest) -> Dict[str, Any]:
    messages = build_messages(syllabus_text, req)
    resp = _client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=messages,
        temperature=0.4,
        response_format={"type": "json_object"},
    )
    content = resp.choices[0].message.content
    data = json.loads(content)
    return data

# --------- PDF / MD rendering with naming ---------
def render_plan_file(plan: Dict[str, Any], req: StudyPlanRequest, plan_id: str) -> str:
    # filename: ai-studyplan-[gradeband]-[weeks]w-<lang>.(pdf|md)
    gb = grades_compact(req.grades)
    lang = req.target_language.lower()
    base = f"ai-studyplan-{gb}-{req.duration_weeks}w-{lang}"
    font_path = get_font_for_lang(lang)

    if lang != "en" and not font_path:
        # fallback to markdown if we don't have a font for this language
        out_md = os.path.join(FILE_ROOT, f"{base}.md")
        with open(out_md, "w", encoding="utf-8") as f:
            f.write(f"# Study Plan ({gb}, {req.duration_weeks} weeks) [{lang}]\n\n")
            f.write(plan.get("overview", "") + "\n\n")
            for wk in plan.get("weekly_outline", []):
                f.write(f"## Week {wk.get('week')}\n")
                f.write(f"**Topics:** {', '.join(wk.get('topics', []))}\n\n")
                f.write("**Activities:**\n")
                for a in wk.get("activities", []):
                    f.write(f"- {a}\n")
                f.write(f"\n**Assessment:** {wk.get('assessment','')}\n")
                hw = wk.get("homework")
                if hw: f.write(f"\n**Homework:** {hw}\n")
                res = wk.get("resources", [])
                if res:
                    f.write("\n**Resources:**\n")
                    for r in res:
                        f.write(f"- {r.get('title')} ({r.get('platform')}): search \"{r.get('search_query')}\"\n")
                f.write("\n")
        return out_md

    # PDF
    out_pdf = os.path.join(FILE_ROOT, f"{base}.pdf")
    c = canvas.Canvas(out_pdf, pagesize=A4)
    width, height = A4

    # font setup
    if font_path:
        try:
            pdfmetrics.registerFont(TTFont("BodyFont", font_path))
            font_name = "BodyFont"
        except Exception:
            font_name = "Helvetica"
    else:
        font_name = "Helvetica"

    def draw_wrapped(text: str, x: int, y: int, max_width: int, leading: int = 14):
        # naive wrapping
        from textwrap import wrap
        for line in text.splitlines():
            chunks = wrap(line, width= int(max_width/7)) or [""]
            for ch in chunks:
                c.drawString(x, y, ch)
                y -= leading
        return y

    margin = 40
    y = height - margin - 10

    c.setFont(font_name, 16); c.drawString(margin, y, "Study Plan"); y -= 24
    c.setFont(font_name, 10); c.drawString(margin, y, f"Grades: {', '.join(req.grades)}  Weeks: {req.duration_weeks}  Language: {lang}"); y -= 18
    c.setFont(font_name, 12); y = draw_wrapped(plan.get("overview",""), margin, y, width - 2*margin); y -= 10

    for wk in plan.get("weekly_outline", []):
        if y < 120:
            c.showPage(); y = height - margin
            c.setFont(font_name, 12)
        c.setFont(font_name, 13); c.drawString(margin, y, f"Week {wk.get('week')}"); y -= 16

        c.setFont(font_name, 11)
        y = draw_wrapped("Topics: " + ", ".join(wk.get("topics", [])), margin, y, width-2*margin)
        y = draw_wrapped("Activities:", margin, y, width-2*margin)
        for a in wk.get("activities", []):
            y = draw_wrapped(f" • {a}", margin+12, y, width-2*margin)
        y = draw_wrapped("Assessment: " + wk.get("assessment",""), margin, y, width-2*margin)
        hw = wk.get("homework")
        if hw:
            y = draw_wrapped("Homework: " + hw, margin, y, width-2*margin)
        res = wk.get("resources", [])
        if res:
            y = draw_wrapped("Resources:", margin, y, width-2*margin)
            for r in res:
                y = draw_wrapped(f" • {r.get('title')} ({r.get('platform')}): search \"{r.get('search_query')}\"", margin+12, y, width-2*margin)
        y -= 6

    c.showPage(); c.save()
    return out_pdf

# --------- Public entry ----------
def generate_study_plan(req: StudyPlanRequest) -> StudyPlanResponse:
    syllabus_text = read_pdf_text(req.file_id)

    # Single pass: rely on the LLM to generate in the requested language
    plan_data = llm_plan(syllabus_text, req)

    plan_id = make_id()
    out_path = render_plan_file(plan_data, req, plan_id)
    out_name = os.path.basename(out_path)
    printable_url = f"/files/{out_name}"

    print("DEBUG target_language:", req.target_language)

    # Map back into Pydantic for response
    weekly = []
    for wk in plan_data.get("weekly_outline", []):
        weekly.append(WeeklyItem(
            week=wk.get("week"),
            topics=wk.get("topics", []),
            activities=wk.get("activities", []),
            assessment=wk.get("assessment", ""),
            homework=wk.get("homework"),
            resources=wk.get("resources", [])
        ))

    return StudyPlanResponse(
        plan_id=plan_id,
        grades=req.grades,
        weeks=req.duration_weeks,
        target_language=req.target_language,
        overview=plan_data.get("overview", ""),
        weekly_outline=weekly,
        printable_file_url=printable_url
    )

