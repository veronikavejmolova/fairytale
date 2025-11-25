from fairy.server.app import app
import logging
from fairy.text2speech.tts_server import router as tts_app
import uvicorn

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    uvicorn.run(app, host="127.0.0.1", port=8000)