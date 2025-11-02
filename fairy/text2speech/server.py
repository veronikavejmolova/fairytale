"""
server.py

FastAPI web server for ElevenLabs text-to-speech with modern UI.
Imports configuration from tools.text2speech.config.
"""

import hashlib
from io import BytesIO
from pathlib import Path

import httpx
from fastapi import FastAPI, Form, Query
from fastapi.responses import HTMLResponse, JSONResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from starlette.responses import PlainTextResponse

from fairy.text2speech.config import (
    ELEVENLABS_API_KEY,
    ELEVENLABS_MODEL_ID,
    ELEVENLABS_VOICE_ID,
)
from fairy.llm.generator import generate
#from tools.text_generation.main import ask_openai


STATIC_DIR = Path(__file__).parent / "static"
AUDIO_MIME_TYPE = "audio/mpeg"
CACHE_DIR = Path(__file__).parent / "cache"
CACHE_DIR.mkdir(exist_ok=True)

app = FastAPI()
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/", response_class=HTMLResponse)
async def index():
    return HTMLResponse(
        """
        <html>
            <head>
                <title>Text to Speech</title>
                <link rel="stylesheet" href="/static/style.css">
                <script src="/static/app.js" defer></script>
            </head>
            <body>
                <div class="container">
                    <h2>Převod textu na řeč</h2>
                    <form id="tts-form" action="/tts" method="post">
                        <textarea name="text" id="tts-text" rows="6" cols="60" required>Vložte text…</textarea><br><br>
                        <button type="submit" id="speak-btn">Přehrát</button>
                    </form>
                    <button type="button" id="fairytale-btn" style="margin-top:18px;">Generovat pohádku</button>
                    <div id="player"></div>
                </div>
            </body>
        </html>
        """
    )


@app.get("/fairytale", response_class=PlainTextResponse)
async def fairytale():
    task = "Napiš krátkou českou pohádku pro děti. Styl: klasický, pohádkový."
    fairytale_text = await ask_openai(task)
    return fairytale_text


@app.post("/tts", response_class=HTMLResponse)
async def tts_post(text: str = Form(...)):
    return await render_tts_page(text)

@app.get("/audio/{cache_key}/status")
async def audio_status(cache_key: str):
    audio_cache_file = CACHE_DIR / f"{cache_key}.mp3"
    return JSONResponse({"ready": audio_cache_file.exists()})


@app.get("/tts", response_class=HTMLResponse)
async def tts_get(text: str = Query("")):
    return await render_tts_page(text)


async def render_tts_page(text: str) -> HTMLResponse:
    """
    Render the result page for TTS.
    Triggers ElevenLabs audio generation in the background, shows a progress bar, and swaps in the player when ready.
    """
    hash_input = f"{text}|{ELEVENLABS_VOICE_ID}|{ELEVENLABS_MODEL_ID}|0.5|0.5"
    cache_key = hashlib.sha256(hash_input.encode("utf-8")).hexdigest()
    text_cache_file = CACHE_DIR / f"{cache_key}.txt"
    if not text_cache_file.exists():
        text_cache_file.write_text(text, encoding="utf-8")
    audio_id = cache_key

    # HTMLResponse escapes, so f-string here is safe for {audio_id} and constants only
    return HTMLResponse(
        f"""
        <!DOCTYPE html>
        <html>
            <head>
                <title>Výsledek řeči</title>
                <link rel="stylesheet" href="/static/style.css">
            </head>
            <body>
                <div class="container">
                    <h2>Výsledek</h2>
                    <div id="audio-placeholder">
                        <div id="progress-bar" style="width:60%;margin:auto;text-align:center;">
                            <span>⏳ Generuji audio...</span>
                            <div style="width:100%;background:#eee;height:18px;border-radius:12px;margin-top:12px;">
                                <div id="bar" style="width:10%;height:18px;background:#69f;border-radius:12px;transition:width 0.6s;"></div>
                            </div>
                        </div>
                    </div>
                    <br><br>
                    <a href="/" class="back-link">← Zpět</a>
                </div>
                <script>
                    let percent = 10;
                    const bar = document.getElementById('bar');
                    function progressFake() {{
                        percent += Math.random() * 10;
                        if (percent > 99) percent = 99;
                        bar.style.width = percent + "%";
                        if (percent < 98) setTimeout(progressFake, 1000);
                    }}
                    progressFake();

                    // Start background audio generation
                    console.log("Triggering audio generation for {audio_id}");
                    fetch("/audio/{audio_id}/generate", {{method: "POST"}})
                        .then(resp => {{
                            if (resp.ok) {{
                                console.log("Audio generation request sent for {audio_id}");
                            }} else {{
                                console.warn("Audio generation trigger failed:", resp.status);
                            }}
                        }})
                        .catch(err => {{
                            console.error("Error triggering audio generation:", err);
                        }});

                    async function poll() {{
                        console.log("Polling status for audio {audio_id}");
                        let resp = await fetch("/audio/{audio_id}/status");
                        let data = await resp.json();
                        if (data.ready) {{
                            console.log("Audio ready, swapping player in");
                            document.getElementById('audio-placeholder').innerHTML = `
                                <audio controls id="tts-audio" autoplay>
                                    <source src="/audio/{audio_id}" type="{AUDIO_MIME_TYPE}">
                                    Váš prohlížeč nepodporuje audio element.
                                </audio>
                            `;
                            var audio = document.getElementById('tts-audio');
                            if (audio) {{
                                var playPromise = audio.play();
                                if (playPromise !== undefined) {{
                                    playPromise.catch(function() {{
                                        document.body.addEventListener('click', function handler() {{
                                            audio.play();
                                            document.body.removeEventListener('click', handler);
                                        }});
                                    }});
                                }}
                            }}
                        }} else {{
                            setTimeout(poll, 2000);
                        }}
                    }}
                    poll();
                </script>
            </body>
        </html>
        """
    )


@app.post("/audio/{cache_key}/generate")
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



@app.get("/audio/{cache_key}")
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


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)
