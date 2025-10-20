import os
from pathlib import Path

from dotenv import load_dotenv


load_dotenv(Path(__file__).with_name(".env"))

ELEVEN_LABS_KEY = os.environ["ELEVEN_LABS_KEY"]
ELEVEN_LABS_VOICE_ID = "piwFF76q4v4xA9Wyxu1R"
ELEVEN_LABS_MODEL_ID = "eleven_v3"
