# placeholder for shared dependencies (settings, clients, auth)
import os
STUDYPLAN_URL = os.environ.get("STUDYPLAN_URL", "http://studyplan:8001")
IMAGE_URL = os.environ.get("IMAGE_URL", "http://image:8002")
VOICE_URL = os.environ.get("VOICE_URL","http://voice:8003")

