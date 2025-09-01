import os, json
from typing import Any, Dict, List
from pydantic import ValidationError
from openai import OpenAI
from .schemas import StudyPlanRequest, StudyPlanResponse, WeeklyItem

OPENAI_MODEL = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")
client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

SYSTEM_PROMPT = (
    "You are a careful curriculum planner for multi-grade classrooms. "
    "Given a syllabus (raw text), produce a realistic weekly plan with:\n"
    "- brief 'overview'\n"
    "- 'weekly_outline': list of {week, topics[], outcomes[], checks[]}\n"
    "- optional 'resources' suggestions (type, agent, template)\n"
    "Honor constraints (minutes/day, weekdays) and pacing. Keep topics concrete.\n"
    "Output STRICT JSON only. No prose."
)

def build_user_prompt(syllabus_text: str, req: StudyPlanRequest) -> str:
    return (
        f"Syllabus (raw text):\n'''{syllabus_text}'''\n\n"
        f"Grades: {req.grades}\n"
        f"Weeks: {req.duration_weeks}\n"
        f"Constraints: {req.constraints}\n\n"
        "Return JSON with keys: overview (str), weekly_outline (list of objects with week,topics,outcomes,checks), "
        "resources (list of objects)."
    )

def llm_plan_json(syllabus_text: str, req: StudyPlanRequest) -> Dict[str, Any]:
    """
    Calls the model and ensures valid JSON. Retries once with a repair hint if needed.
    """
    user = build_user_prompt(syllabus_text, req)
    for attempt in range(2):
        resp = client.chat.completions.create(
            model=OPENAI_MODEL,
            temperature=0.3,
            response_format={"type": "json_object"},  # JSON mode
            messages=[{"role": "system", "content": SYSTEM_PROMPT},
                      {"role": "user", "content": user}]
        )
        content = resp.choices[0].message.content
        try:
            return json.loads(content)
        except Exception:
            # Try to repair thin issues (fallback)
            user += "\n\nIf invalid, fix and return VALID JSON only."
    raise RuntimeError("Failed to obtain valid JSON from model.")

def to_response(json_obj: Dict[str, Any], plan_id: str) -> StudyPlanResponse:
    # Minimal normalization
    weekly_outline: List[WeeklyItem] = []
    for w in json_obj.get("weekly_outline", []):
        weekly_outline.append(WeeklyItem(
            week=int(w.get("week", len(weekly_outline)+1)),
            topics=[t for t in w.get("topics", []) if isinstance(t, str)],
            outcomes=[o for o in w.get("outcomes", []) if isinstance(o, str)],
            checks=[c for c in w.get("checks", []) if isinstance(c, str)] if w.get("checks") else None
        ))
    resp = StudyPlanResponse(
        plan_id=plan_id,
        overview=str(json_obj.get("overview", ""))[:2000],
        weekly_outline=weekly_outline,
        resources=[r for r in json_obj.get("resources", []) if isinstance(r, dict)]
    )
    return resp

def generate_studyplan(syllabus_text: str, req: StudyPlanRequest, plan_id: str) -> StudyPlanResponse:
    json_obj = llm_plan_json(syllabus_text, req)
    try:
        return to_response(json_obj, plan_id=plan_id)
    except ValidationError as ve:
        # If the model returned malformed shapes, surface a clear error
        raise RuntimeError(f"Model JSON did not match schema: {ve}")
