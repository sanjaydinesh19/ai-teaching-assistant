# app/metrics_logger.py

import os, json, re
from datetime import datetime
from typing import Dict, Any, List
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from pydantic import ValidationError
from .schemas import StudyPlanResponse, WeeklyItem
from openai import OpenAI

METRICS_LOG_PATH = os.environ.get("METRICS_LOG_PATH", "/data/studyplan_metrics.jsonl")
_client = OpenAI()


# ---------- Core Logging ----------
def log_metric_entry(entry: Dict[str, Any]):
    entry["timestamp"] = datetime.utcnow().isoformat()
    os.makedirs(os.path.dirname(METRICS_LOG_PATH), exist_ok=True)
    with open(METRICS_LOG_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def load_logs() -> List[Dict[str, Any]]:
    if not os.path.exists(METRICS_LOG_PATH):
        return []
    with open(METRICS_LOG_PATH, encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


# ---------- Accuracy ----------
def compute_accuracy(syllabus_text: str, plan_data: dict) -> float:
    """
    Compute semantic similarity between syllabus and generated plan.
    Falls back to TF-IDF if embeddings fail or input too long.
    """
    from openai import OpenAI
    import numpy as np
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity

    _eval = OpenAI()

    generated_topics = " ".join(
        sum((wk.get("topics", []) for wk in plan_data.get("weekly_outline", [])), [])
    )
    if not syllabus_text or not generated_topics:
        print("[ACCURACY] Missing syllabus or topics.")
        return 0.0

    # ---- Truncate inputs to avoid token overflow (max ~8000 chars each) ----
    max_chars = 24000  # roughly ~6000 tokens
    syllabus_text = syllabus_text[:max_chars]
    generated_topics = generated_topics[:max_chars]

    try:
        emb = _eval.embeddings.create(
            model="text-embedding-3-small",
            input=[syllabus_text, generated_topics]
        )
        print(f"[ACCURACY] Using embeddings: syllabus_len={len(syllabus_text)}, topics_len={len(generated_topics)}")
        v1, v2 = np.array(emb.data[0].embedding), np.array(emb.data[1].embedding)
        sim = np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))
        print("[ACCURACY] Cosine similarity (embeddings):", sim)
        return round(float(sim), 3)

    except Exception as e:
        print("[ACCURACY WARNING] Embedding failed, falling back to TF-IDF:", e)
        try:
            corpus = [syllabus_text, generated_topics]
            X = TfidfVectorizer(stop_words="english").fit_transform(corpus)
            sim = cosine_similarity(X[0:1], X[1:2])[0][0]
            print("[ACCURACY] Cosine similarity (TF-IDF):", sim)
            return round(float(sim), 3)
        except Exception as e2:
            print("[ACCURACY ERROR] Both embedding and TF-IDF failed:", e2)
            return 0.0





# ---------- Quality ----------
def compute_quality(plan_data: dict) -> float:
    """Use an LLM evaluator with robust numeric parsing."""
    rubric_prompt = f"""
    You are an education expert reviewing an AI-generated study plan.
    Evaluate it on a scale of 1–10 based on:
    1. Alignment with the syllabus and grade level.
    2. Pedagogical soundness and structure.
    3. Completeness of weekly coverage.
    4. Clarity and usefulness for a teacher.
    Respond with only a single number between 1 and 10, no words or explanation.

    STUDY PLAN:
    {json.dumps(plan_data)[:7000]}
    """

    try:
        resp = _client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a strict academic evaluator."},
                {"role": "user", "content": rubric_prompt}
            ],
            temperature=0
        )

        raw_score = resp.choices[0].message.content.strip()
        # Extract the first numeric value from response (handles "8/10", "Score: 9", etc.)
        match = re.search(r"\b(\d{1,2}(?:\.\d)?)\b", raw_score)
        score = float(match.group(1)) if match else 0.0

        # Ensure within bounds
        score = max(0.0, min(score, 10.0))
        return round(score, 2)

    except Exception as e:
        print(f"[QualityEvalError] {e}")
        return 0.0


# ---------- Batch Validation ----------
def validate_plan(req, plan_data: dict) -> bool:
    """Check if output matches expected schema (real validation)."""
    try:
        _ = StudyPlanResponse(
            plan_id="temp",
            grades=req.grades,
            weeks=req.duration_weeks,
            target_language=req.target_language,
            overview=plan_data.get("overview", ""),
            weekly_outline=[WeeklyItem(**wk) for wk in plan_data.get("weekly_outline", [])],
            printable_file_url="temp.pdf"
        )
        return True
    except ValidationError:
        return False


# ---------- Aggregation ----------
def aggregate_metrics() -> Dict[str, Any]:
    logs = load_logs()
    if not logs:
        return {}

    total = len(logs)
    successes = sum(1 for x in logs if x.get("success"))
    valids = sum(1 for x in logs if x.get("json_valid"))
    qualities = [x["quality_score"] for x in logs if x.get("quality_score", 0) > 0]
    accuracies = [x["accuracy"] for x in logs if x.get("accuracy", 0) > 0]

    return {
        "quality_of_response": round(sum(qualities) / len(qualities), 2) if qualities else 0.0,
        "reliability": round(successes / total, 3),
        "batch_validation": round(valids / total, 3),
        "accuracy": round(sum(accuracies) / len(accuracies), 3) if accuracies else 0.0,
        "total_requests": total
    }
