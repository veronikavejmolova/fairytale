import hashlib
import logging
from io import BytesIO
from pathlib import Path

from starlette.templating import Jinja2Templates
import httpx
from fastapi import FastAPI, Query, Form, Request, APIRouter
from fastapi.responses import HTMLResponse, JSONResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from starlette.responses import PlainTextResponse

from fairy.text2speech.config import (
    ELEVENLABS_API_KEY,
    ELEVENLABS_MODEL_ID,
    ELEVENLABS_VOICE_ID,
)

BASE_DIR = Path(__file__).resolve().parent.parent
TEMPLATES_DIR = BASE_DIR / "frontend"
STATIC_DIR = BASE_DIR.parent / "frontend" / "static"

AUDIO_MIME_TYPE = "audio/mpeg"
CACHE_DIR = Path(__file__).parent / "cache"
CACHE_DIR.mkdir(exist_ok=True)

templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

router = APIRouter()


# sending story to tts
@router.post("/tts", response_class=HTMLResponse)
async def tts(request: Request):  # <--- 1. Change to 'async def'
    data = await request.json()  # <--- 2. Add 'await'

    # request.json() returns a dictionary, so use ["text"], not .text
    return render_tts_page(request, data["text"])


@router.get("/audio/{cache_key}/status")
async def audio_status(cache_key: str):
    audio_cache_file = CACHE_DIR / f"{cache_key}.mp3"
    logging.info(audio_cache_file.exists())
    return JSONResponse({"ready": audio_cache_file.exists()})


def render_tts_page(request: Request, story: str) -> HTMLResponse:
    """
    Render the result page for TTS.
    Triggers ElevenLabs audio generation in the background, shows a progress bar, and swaps in the player when ready.
    """
    hash_input = f"{story}|{ELEVENLABS_VOICE_ID}|{ELEVENLABS_MODEL_ID}|0.5|0.5"
    cache_key = hashlib.sha256(hash_input.encode("utf-8")).hexdigest()
    text_cache_file = CACHE_DIR / f"{cache_key}.txt"
    if not text_cache_file.exists():
        text_cache_file.write_text(story, encoding="utf-8")
    logging.info({"request": request,
                  "story": story,
                  "cache_key": cache_key,
                  "audio_mime": AUDIO_MIME_TYPE, "cache": text_cache_file.exists()})
    return templates.TemplateResponse(
        "tts.html",  # název šablony v TEMPLATES_DIR
        {
            "request": request,
            "story": story,
            "cache_key": cache_key,
            "audio_mime": AUDIO_MIME_TYPE,
        },
    )


@router.post("/audio/{cache_key}/generate")
async def generate_audio(cache_key: str):
    try:
        text_cache_file = CACHE_DIR / f"{cache_key}.txt"
        if not text_cache_file.exists():
            print(f"[ERROR] Text cache file not found: {text_cache_file}")
            return PlainTextResponse("Text not found for audio", status_code=404)
        text = text_cache_file.read_text(encoding="utf-8")

        audio_cache_file = CACHE_DIR / f"{cache_key}.mp3"
        if audio_cache_file.exists():
            print(f"[INFO] Audio already exists for {cache_key}")
            return PlainTextResponse("Audio already exists", status_code=200)

        url = f"https://api.elevenlabs.io/v1/text-to-speech/{ELEVENLABS_VOICE_ID}"
        headers = {
            "xi-api-key": ELEVENLABS_API_KEY,
            "Content-Type": "application/json",
        }
        data = {
            "text": text,
            "model_id": ELEVENLABS_MODEL_ID,
            "voice_settings": {"stability": 0.5, "similarity_boost": 0.5},
        }
        print(f"[INFO] Sending TTS request for {cache_key} (text length: {len(text)})")
        async with httpx.AsyncClient(timeout=90.0) as client:
            r = await client.post(url, headers=headers, json=data)
            r.raise_for_status()
            audio_bytes = r.content
            audio_cache_file.write_bytes(audio_bytes)
        print(f"[SUCCESS] Audio generated and saved: {audio_cache_file}")
        return PlainTextResponse("Audio generated", status_code=200)
    except Exception as e:
        print(f"[FATAL] Error in /audio/{cache_key}/generate: {e}")
        return PlainTextResponse(f"Error generating audio: {e}", status_code=500)


@router.get("/audio/{cache_key}")
async def audio(cache_key: str):
    text_cache_file = CACHE_DIR / f"{cache_key}.txt"
    if not text_cache_file.exists():
        return PlainTextResponse("Text not found for audio", status_code=404)
    text = text_cache_file.read_text(encoding="utf-8")

    audio_cache_file = CACHE_DIR / f"{cache_key}.mp3"
    if audio_cache_file.exists():
        audio_fp = audio_cache_file.open("rb")
        return StreamingResponse(audio_fp, media_type=AUDIO_MIME_TYPE)

    url = f"https://api.elevenlabs.io/v1/text-to-speech/{ELEVENLABS_VOICE_ID}"
    headers = {
        "xi-api-key": ELEVENLABS_API_KEY,
        "Content-Type": "application/json",
    }
    data = {
        "text": text,
        "model_id": ELEVENLABS_MODEL_ID,
        "voice_settings": {"stability": 0.5, "similarity_boost": 0.5},
    }
    async with httpx.AsyncClient(timeout=90.0) as client:
        r = await client.post(url, headers=headers, json=data)
        r.raise_for_status()
        audio_bytes = r.content
        audio_cache_file.write_bytes(audio_bytes)
        audio_bytesio = BytesIO(audio_bytes)
        return StreamingResponse(audio_bytesio, media_type=AUDIO_MIME_TYPE)
