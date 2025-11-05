
from pathlib import Path
from fastapi import FastAPI, Request, Form, BackgroundTasks
from fastapi.responses import HTMLResponse
from starlette.templating import Jinja2Templates

from fairy.llm.generator import generate
from fairy.llm.theme_filter import quick_theme_check, async_llm_check, get_cached_theme_result

app = FastAPI()
TEMPLATES_DIR = Path(__file__).parent.parent / "frontend"
templates = Jinja2Templates(directory=TEMPLATES_DIR)


@app.get("/api/generate")
async def api_generate():
    return {"message": generate("hello")}


@app.get("/", response_class=HTMLResponse)
async def theme(request: Request):
    return templates.TemplateResponse("theme.html", {"request": request})


@app.post("/character", response_class=HTMLResponse)
async def character(request: Request, background_tasks: BackgroundTasks, theme: str = Form(...), age: int | None = Form(None)):
    if not quick_theme_check(theme):
        return templates.TemplateResponse("error.html",{"request": request, "theme": theme,  "age": age})

    background_tasks.add_task(async_llm_check, theme)

    return templates.TemplateResponse("character.html", {"request": request, "theme": theme, "age": age})


@app.post("/moral", response_class=HTMLResponse)
async def moral(request: Request, theme: str = Form(...), character: str = Form(...), age: int | None = Form(None)):
    cached = get_cached_theme_result(theme)
    if cached == "nevhodné":
        return templates.TemplateResponse("error.html", {"request": request, "theme": theme,  "age": age})

    return templates.TemplateResponse("moral.html", {"request": request, "theme": theme, "character": character,  "age": age})


@app.post("/generate", response_class=HTMLResponse)
async def generate_story(
    request: Request,
    theme: str = Form(...),
    character: str = Form(...),
    moral: str = Form(...),
    age: int = Form(...),
    prompt: str = Form("")):

    prompt_text = f"Napiš pohádku pro dítě ve věku {age} let. Téma: {theme}. Hlavní postava: {character}. Ponaučení: {moral}. Další: {prompt}."
    story = generate(prompt_text)
    return templates.TemplateResponse("result.html",{
        "request": request,
        "theme": theme,
        "character": character,
        "moral": moral,
        "prompt": prompt,
        "story": story,
        "age": age
    })