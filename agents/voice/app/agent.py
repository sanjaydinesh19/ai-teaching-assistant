import os, re, time, random
from typing import Optional
from openai import OpenAI
from .schemas import VoiceRequest, VoiceResponse

FILE_ROOT = os.environ.get("FILE_STORE", "/data")
ASR_MODEL  = os.environ.get("OPENAI_ASR_MODEL", "gpt-4o-mini-transcribe")
REASON_MODEL = os.environ.get("OPENAI_REASON_MODEL", "gpt-4o-mini")
TTS_MODEL = os.environ.get("OPENAI_TTS_MODEL", "gpt-4o-mini-tts")

client = OpenAI()

def _id(prefix="ans"):
    t = str(int(time.time()))
    rnd = "".join(random.choice("abcdefghijklmnopqrstuvwxyz0123456789") for _ in range(6))
    return f"{prefix}_{t}{rnd}"

def _find_audio_path(file_id: str) -> str:
    for ext in (".wav",".mp3",".m4a"):
        p = os.path.join(FILE_ROOT, f"{file_id}{ext}")
        if os.path.exists(p): return p
    # raw id fallback
    p = os.path.join(FILE_ROOT, file_id)
    if os.path.exists(p): return p
    raise FileNotFoundError(f"Audio not found for file_id={file_id}")

def clean_markdown(text: str) -> str:
    if not text: return ""
    # strip common md tokens
    text = re.sub(r"\*\*(.*?)\*\*", r"\1", text)
    text = re.sub(r"`(.*?)`", r"\1", text)
    text = re.sub(r"^#+\s*", "", text, flags=re.MULTILINE)
    text = re.sub(r"\*\s+", "- ", text)  # bullets to dashes
    # normalize spaces
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text).strip()
    return text

def transcribe(audio_path: str, lang: str) -> str:
    with open(audio_path, "rb") as f:
        tr = client.audio.transcriptions.create(
            model=ASR_MODEL,
            file=f,
            # If model supports it: language=lang  (some models auto-detect)
        )
    return tr.text.strip()

def reason(text: str, lang: str, topic_hint: Optional[str]) -> str:
    sys = f"""You are a helpful teaching assistant. 
Respond ONLY in language: {lang}. 
Write in short paragraphs with clear formatting. 
Avoid markdown syntax like **bold** or # headings."""
    user = f"""Teacher said (transcript):
\"\"\"{text}\"\"\"
{f"Topic hint: {topic_hint}" if topic_hint else ""}
Create a concise explanation for students. Include: key idea, 1 small example, and 1 quick practice question."""
    out = client.chat.completions.create(
        model=REASON_MODEL,
        temperature=0.4,
        messages=[{"role":"system","content":sys},{"role":"user","content":user}]
    )
    return out.choices[0].message.content.strip()

def tts_to_file(text: str, voice: str, speed: float, lang: str) -> str:
    # name: ai-voice-<lang>-<id>.mp3
    ans_id = _id()
    fname = f"ai-voice-{lang}-{ans_id}.mp3"
    out_path = os.path.join(FILE_ROOT, fname)

    # Some TTS endpoints stream; here we use non-streaming for simplicity
    audio = client.audio.speech.create(
        model=TTS_MODEL,
        voice=voice,
        input=text,
        speed=speed
    )
    with open(out_path, "wb") as f:
        f.write(audio.content)
    return out_path

def handle_voice(req: VoiceRequest) -> VoiceResponse:
    audio_path = _find_audio_path(req.file_id)
    transcript = transcribe(audio_path, req.target_language)
    cleaned_transcript = clean_markdown(transcript)

    answer = reason(cleaned_transcript, req.target_language, req.topic_hint)
    answer_clean = clean_markdown(answer)

    mp3_path = tts_to_file(answer_clean, req.tts_voice, req.tts_speed, req.target_language)
    mp3_name = os.path.basename(mp3_path)

    # Optional: save plaintext output for download
    txt_name = f"{os.path.splitext(mp3_name)[0]}.txt"
    txt_path = os.path.join(FILE_ROOT, txt_name)
    with open(txt_path, "w", encoding="utf-8") as f:
        f.write(answer_clean)

    return VoiceResponse(
        transcript=cleaned_transcript,
        answer_text=answer_clean,
        answer_audio_url=f"/files/{mp3_name}",
        transcript_file_url=f"/files/{txt_name}",
    )
