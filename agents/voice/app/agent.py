import os, json
from openai import OpenAI
from .schemas import VoiceAskRequest, VoiceAskResponse
from .audio_utils import get_audio_path

client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
MODEL_ASR = os.environ.get("OPENAI_ASR_MODEL","gpt-4o-mini-transcribe")
MODEL_REASON = os.environ.get("OPENAI_REASON_MODEL","gpt-4o-mini")
MODEL_TTS = os.environ.get("OPENAI_TTS_MODEL","gpt-4o-mini-tts")
FILE_STORE = os.environ.get("FILE_STORE","/data")

SYSTEM_PROMPT = (
    "You are a teaching assistant. Given a student's spoken question, "
    "generate a clear explanation in the requested visual format. "
    "Be concise, age-appropriate, and cover key concepts."
)

def process_voice(req: VoiceAskRequest, answer_id: str) -> VoiceAskResponse:
    # 1. Transcribe
    audio_path = get_audio_path(req.audio_file_id)
    with open(audio_path,"rb") as f:
        asr = client.audio.transcriptions.create(
            model=MODEL_ASR,
            file=f
        )
    transcript = asr.text.strip()

    # 2. Reason
    user_prompt = (
        f"Level: {req.level}\nVisual style: {req.visual_format}\n"
        f"Transcript of student question: {transcript}\n\n"
        "Provide an explanation."
    )
    resp = client.chat.completions.create(
        model=MODEL_REASON,
        messages=[{"role":"system","content":SYSTEM_PROMPT},
                  {"role":"user","content":user_prompt}],
        temperature=0.4
    )
    explanation = resp.choices[0].message.content.strip()

    # 3. TTS
    tts_path = os.path.join(FILE_STORE, f"{answer_id}.mp3")
    with client.audio.speech.with_streaming_response.create(
        model=MODEL_TTS,
        voice="alloy",
        input=explanation
    ) as response:
        response.stream_to_file(tts_path)

    return VoiceAskResponse(
        transcript=transcript,
        explanation=explanation,
        audio_url=f"/files/{answer_id}.mp3"
    )
