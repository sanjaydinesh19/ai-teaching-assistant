import os

FILE_STORE = os.environ.get("FILE_STORE","/data")

def get_audio_path(file_id: str) -> str:
    # expected _filestore/<file_id>.wav or .mp3
    for ext in [".wav",".mp3",".m4a"]:
        path = os.path.join(FILE_STORE, f"{file_id}{ext}")
        if os.path.exists(path):
            return path
    raise FileNotFoundError(f"No audio file found for {file_id}")
