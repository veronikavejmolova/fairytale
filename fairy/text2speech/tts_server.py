import hashlib
import logging
from io import BytesIO
from pathlib import Path

from starlette.templating import Jinja2Templates
import httpx
from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse, JSONResponse, StreamingResponse
from starlette.responses import PlainTextResponse
from pydantic import BaseModel

from fairy.text2speech.config import (
    ELEVENLABS_API_KEY,
    ELEVENLABS_MODEL_ID,
    ELEVENLABS_VOICE_ID,
)

BASE_DIR = Path(__file__).resolve().parent.parent
TEMPLATES_DIR = BASE_DIR / "frontend"
CACHE_DIR = Path(__file__).parent / "cache"
CACHE_DIR.mkdir(exist_ok=True)

AUDIO_MIME_TYPE = "audio/mpeg"

templates = Jinja2Templates(directory=str(TEMPLATES_DIR))
router = APIRouter()


# Model pro příchozí JSON data
class TTSRequest(BaseModel):
    text: str
    voice_id: str = None


# --- POMOCNÁ FUNKCE PRO ZÍSKÁNÍ NEBO VYGENEROVÁNÍ AUDIA ---
async def get_audio_bytes(text: str) -> bytes:
    # 1. Vytvoření hashe (Cache Key)
    hash_input = f"{text}|{ELEVENLABS_VOICE_ID}|{ELEVENLABS_MODEL_ID}|0.5|0.5"
    cache_key = hashlib.sha256(hash_input.encode("utf-8")).hexdigest()

    # 2. Uložení textu (pro debug/info)
    text_cache_file = CACHE_DIR / f"{cache_key}.txt"
    if not text_cache_file.exists():
        text_cache_file.write_text(text, encoding="utf-8")

    # 3. Kontrola existence MP3
    audio_cache_file = CACHE_DIR / f"{cache_key}.mp3"
    if audio_cache_file.exists():
        logging.info(f"[CACHE HIT] Audio found for {cache_key}")
        return audio_cache_file.read_bytes()

    # 4. Volání ElevenLabs API (pokud není v cache)
    logging.info(f"[API CALL] Generating audio for {cache_key}")
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
        r.raise_for_status()  # Vyhodí chybu, pokud API selže
        audio_bytes = r.content

        # Uložení do cache
        audio_cache_file.write_bytes(audio_bytes)
        return audio_bytes


# --- ENDPOINTY ---

# 1. Hlavní endpoint pro result.html (AJAX Streaming)
@router.post("/tts_stream", name="tts_stream")
async def tts_stream_endpoint(request: TTSRequest):
    try:
        audio_data = await get_audio_bytes(request.text)
        return StreamingResponse(BytesIO(audio_data), media_type=AUDIO_MIME_TYPE)
    except Exception as e:
        logging.error(f"Error generating audio: {e}")
        return JSONResponse({"error": str(e)}, status_code=500)


# 2. API pro polling (pokud byste chtěl používat tts.html logiku)
@router.post("/tts/api/init")
async def tts_init_api(request: TTSRequest):
    # Jen vrátí klíč, frontend si pak musí sám volat status a generate
    hash_input = f"{request.text}|{ELEVENLABS_VOICE_ID}|{ELEVENLABS_MODEL_ID}|0.5|0.5"
    cache_key = hashlib.sha256(hash_input.encode("utf-8")).hexdigest()

    # Uložíme text, aby ho generate našel
    text_cache_file = CACHE_DIR / f"{cache_key}.txt"
    if not text_cache_file.exists():
        text_cache_file.write_text(request.text, encoding="utf-8")

    return JSONResponse({
        "cache_key": cache_key,
        "audio_mime": AUDIO_MIME_TYPE
    })


# 3. Endpoint pro manuální vyvolání generování (pro polling)
@router.post("/audio/{cache_key}/generate")
async def generate_audio_trigger(cache_key: str):
    try:
        text_cache_file = CACHE_DIR / f"{cache_key}.txt"
        if not text_cache_file.exists():
            return PlainTextResponse("Text not found", status_code=404)

        text = text_cache_file.read_text(encoding="utf-8")
        await get_audio_bytes(text)  # Tato funkce se postará o generování i uložení
        return PlainTextResponse("Audio generated", status_code=200)
    except Exception as e:
        return PlainTextResponse(f"Error: {e}", status_code=500)


@router.get("/audio/{cache_key}/status")
async def audio_status(cache_key: str):
    audio_cache_file = CACHE_DIR / f"{cache_key}.mp3"
    return JSONResponse({"ready": audio_cache_file.exists()})


@router.get("/audio/{cache_key}")
async def get_audio_file(cache_key: str):
    audio_cache_file = CACHE_DIR / f"{cache_key}.mp3"
    if audio_cache_file.exists():
        return StreamingResponse(audio_cache_file.open("rb"), media_type=AUDIO_MIME_TYPE)
    return PlainTextResponse("Audio not found", status_code=404)


# 4. Starý endpoint pro formulář (zachován pro kompatibilitu)
@router.post("/tts", name="tts_old_page", response_class=HTMLResponse)
async def tts_post_page(request: Request, text: str = Form(...)):
    # ... logika pro render tts.html ...
    pass