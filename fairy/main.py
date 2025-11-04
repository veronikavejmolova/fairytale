from fairy.server.app import app
import logging
#from fairy.text2speech.tts_server import app as tts_app
import uvicorn

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    uvicorn.run(app, host="0.0.0.0", port=8000)
