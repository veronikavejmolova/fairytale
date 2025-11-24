
from pathlib import Path

from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from starlette.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

from fairy.llm.generator import generate
from fairy.llm.theme_filter import is_theme_appropriate

app = FastAPI()
BASE_DIR = Path(__file__).resolve().parent.parent
TEMPLATES_DIR = BASE_DIR / "frontend"

templates = Jinja2Templates(directory=str(TEMPLATES_DIR))
templates.env.globals['url_for'] = app.url_path_for

app.mount("/static", StaticFiles(directory=str(TEMPLATES_DIR / "static")), name="static")

@app.get("/api/generate")
async def api_generate():
    return {"message": generate("hello")}


@app.get("/", response_class=HTMLResponse)
async def theme(request: Request):
    return templates.TemplateResponse("theme.html", {"request": request})


@app.post("/character", response_class=HTMLResponse)
async def character(request: Request, theme: str = Form(...), age: int | None = Form(None)):
    if not is_theme_appropriate(theme):
        return templates.TemplateResponse("error.html",{"request": request, "theme": theme, "age": age})


    return templates.TemplateResponse("character.html", {"request": request, "theme": theme, "age": age})


@app.post("/moral", response_class=HTMLResponse)
async def moral(request: Request, theme: str = Form(...), character: str = Form(...), age: int | None = Form(None)):
    return templates.TemplateResponse("moral.html", {"request": request, "theme": theme, "character": character, "age": age})


@app.post("/generate", response_class=HTMLResponse)
async def generate_story(
    request: Request,
    theme: str = Form(...),
    character: str = Form(...),
    moral: str = Form(...),
    age: int = Form(...),
    prompt: str = Form("")
):
    prompt_text = f"Napiš pohádku pro dítě ve věku {age} podle následujících parametrů: téma: {theme}, postava: {character}, ponaučení: {moral}, další: {prompt}"
    story = generate(prompt_text)
    return templates.TemplateResponse("result.html", {
        "request": request,
        "theme": theme,
        "character": character,
        "moral": moral,
        "prompt": prompt,
        "story": story,
        "age": age})