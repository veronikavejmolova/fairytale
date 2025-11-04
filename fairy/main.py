from fairy.server.app import app
from fairy.text2speech.tts_server import app as tts_app
import uvicorn

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("tts_app", host="0.0.0.0", port=8000, reload=True)