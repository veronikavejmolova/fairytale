import os
from pathlib import Path

from dotenv import load_dotenv

# load_dotenv(Path(__file__).with_name(".env"))
load_dotenv(Path(__file__).parent.parent.parent / ".env")

ELEVENLABS_API_KEY = os.environ["ELEVENLABS_API_KEY"]
ELEVENLABS_VOICE_ID = "piwFF76q4v4xA9Wyxu1R"
ELEVENLABS_MODEL_ID = "eleven_v3"
