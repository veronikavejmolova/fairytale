from fastapi import FastAPI, Request
from starlette.responses import HTMLResponse
from starlette.templating import Jinja2Templates

from fairy.llm.generator import generate

app = FastAPI()


templates = Jinja2Templates(directory="frontend")


@app.get("/api/generate")
async def api_generate():
    return {"message": generate("hello")}


@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse(
        "theme.html",
        {"request": request}
    )

