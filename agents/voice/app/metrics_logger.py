import os, json, time, re
from datetime import datetime
from typing import Dict, Any, List
from pydantic import ValidationError
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from openai import OpenAI
from .schemas import VoiceResponse  # assuming you have a response model

METRICS_LOG_PATH = os.environ.get("METRICS_LOG_PATH", "/data/voice_metrics.jsonl")
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


# ---------- Quality ----------
def compute_quality(asr_text: str, llm_text: str) -> float:
    """Ask an evaluator LLM to rate the response quality on 1–10."""
    rubric_prompt = f"""
    Evaluate this AI response on a scale of 1–10.
    Criteria:
    1. Relevance to user query
    2. Factual accuracy
    3. Clarity and tone
    4. Helpfulness and completeness

    USER (transcribed): "{asr_text}"
    ASSISTANT (response): "{llm_text}"

    Reply only with a number between 1 and 10.
    """
    try:
        resp = _client.chat.completions.create(
            model="gpt-4o-mini",
            temperature=0,
            messages=[
                {"role": "system", "content": "You are a fair but strict evaluator of conversational AI responses."},
                {"role": "user", "content": rubric_prompt}
            ]
        )
        content = resp.choices[0].message.content.strip()
        match = re.search(r"\b\d+(\.\d+)?\b", content)
        if match:
            return float(match.group(0))
        print("[QUALITY WARN] Could not parse numeric score from:", content)
        return 0.0
    except Exception as e:
        print("[QUALITY ERROR]", e)
        return 0.0


# ---------- Validation ----------
def validate_response(resp_dict: Dict[str, Any]) -> bool:
    """Check if VoiceResponse schema validates correctly."""
    try:
        _ = VoiceResponse(**resp_dict)
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
