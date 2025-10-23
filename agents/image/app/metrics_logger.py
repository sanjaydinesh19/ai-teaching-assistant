import os, json, time
from datetime import datetime
from typing import Dict, Any, List
from pydantic import ValidationError
from openai import OpenAI
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from .schemas import WorksheetResponse, WorksheetItem

METRICS_LOG_PATH = os.environ.get("METRICS_LOG_PATH", "/data/worksheet_metrics.jsonl")
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


# ---------- Accuracy / Relevance ----------
def compute_accuracy(source_text: str, generated_items: List[WorksheetItem]) -> float:
    """Compute semantic similarity between source (PDF/PPT text) and generated worksheet questions."""
    if not source_text or not generated_items:
        return 0.0

    questions_text = " ".join([i.q for i in generated_items])
    source_text = source_text[:24000]
    questions_text = questions_text[:24000]

    try:
        emb = _client.embeddings.create(
            model="text-embedding-3-small",
            input=[source_text, questions_text]
        )
        v1, v2 = np.array(emb.data[0].embedding), np.array(emb.data[1].embedding)
        sim = np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))
        return round(float(sim), 3)
    except Exception as e:
        print("[ACCURACY WARNING] Embedding failed:", e)
        # Fallback: TF-IDF
        try:
            corpus = [source_text, questions_text]
            X = TfidfVectorizer(stop_words="english").fit_transform(corpus)
            sim = cosine_similarity(X[0:1], X[1:2])[0][0]
            return round(float(sim), 3)
        except Exception:
            return 0.0


# ---------- Quality ----------
def compute_quality(items: List[WorksheetItem], difficulty: str, grade_bands: List[str]) -> float:
    """Ask LLM to rate quality on a 1–10 scale."""
    rubric_prompt = f"""
    Evaluate the quality of this worksheet (difficulty: {difficulty}, grades: {', '.join(grade_bands)}).
    Criteria:
    1. Relevance to input context
    2. Clarity of questions
    3. Variety and creativity
    4. Alignment to difficulty level
    Reply only with a number between 1 and 10.
    Questions:
    {json.dumps([i.q for i in items])[:6000]}
    """
    try:
        resp = _client.chat.completions.create(
            model="gpt-4o-mini",
            temperature=0,
            messages=[
                {"role": "system", "content": "You are a strict educational evaluator. Output only a number (1–10)."},
                {"role": "user", "content": rubric_prompt}
            ]
        )
        score_text = resp.choices[0].message.content.strip()
        # Extract first numeric value in string
        import re
        match = re.search(r"\b\d+(\.\d+)?\b", score_text)
        if match:
            return float(match.group(0))
        print("[QUALITY WARN] Could not parse numeric score from:", score_text)
        return 0.0
    except Exception as e:
        print("[QUALITY ERROR]", e)
        return 0.0



# ---------- Validation ----------
def validate_response(resp: Dict[str, Any]) -> bool:
    """Ensure the generated structure matches expected Pydantic schema."""
    try:
        _ = WorksheetResponse(**resp)
        return True
    except ValidationError as e:
        print("[VALIDATION ERROR]", e)
        return False


# ---------- Aggregation ----------
def aggregate_metrics() -> Dict[str, Any]:
    logs = load_logs()
    if not logs:
        return {}

    total = len(logs)
    successes = sum(1 for x in logs if x.get("success"))
    valids = sum(1 for x in logs if x.get("json_valid"))
    qualities = [x["quality_score"] for x in logs if x.get("quality_score")]
    accuracies = [x["accuracy"] for x in logs if x.get("accuracy")]

    return {
        "quality_of_response": round(sum(qualities) / len(qualities), 2) if qualities else 0.0,
        "reliability": round(successes / total, 3),
        "batch_validation": round(valids / total, 3),
        "accuracy": round(sum(accuracies) / len(accuracies), 3) if accuracies else 0.0,
        "total_requests": total
    }
