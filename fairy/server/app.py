
from pathlib import Path

from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from starlette.templating import Jinja2Templates

from fairy.llm.generator import generate
from fairy.llm.theme_filter import is_theme_appropriate

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
async def character(
    request: Request,
    theme: str = Form(...),
    length: str = Form("")
):
    if not is_theme_appropriate(theme):
        return templates.TemplateResponse(
            "error.html",
            {"request": request, "theme": theme, "length": length}
        )

    return templates.TemplateResponse(
        "character.html",
        {"request": request, "theme": theme, "length": length}
    )



@app.post("/additional_characters", response_class=HTMLResponse)
async def additional_characters(
    request: Request,
    theme: str = Form(...),
    character: str = Form(...),
    length: str = Form(""),
):
    return templates.TemplateResponse(
        "additional_characters.html",
        {
            "request": request,
            "theme": theme,
            "character": character,
            "length": length
        }
    )


@app.post("/supernatural", response_class=HTMLResponse)
async def supernatural(
    request: Request,
    theme: str = Form(...),
    character: str = Form(...),
    length: str = Form(""),
    other_characters: str = Form(""),
):
    return templates.TemplateResponse(
        "supernatural.html",
        {
            "request": request,
            "theme": theme,
            "character": character,
            "length": length,
            "other_characters": other_characters
        }
    )


@app.post("/moral", response_class=HTMLResponse)
async def moral(
    request: Request,
    theme: str = Form(...),
    character: str = Form(...),
    length: str = Form(""),
    other_characters: str = Form(""),
    supernatural_present: str = Form("no"),
    super_types: str = Form(""),
    super_tone: str = Form(""),
):
    return templates.TemplateResponse(
        "moral.html",
        {
            "request": request,
            "theme": theme,
            "character": character,
            "length": length,
            "other_characters": other_characters,
            "supernatural_present": supernatural_present,
            "super_types": super_types,
            "super_tone": super_tone,
        }
    )


@app.post("/generate", response_class=HTMLResponse)
async def generate_story(
    request: Request,
    theme: str = Form(...),
    character: str = Form(...),
    moral: str = Form(...),
    length: str = Form(""),
    other_characters: str = Form(""),
    supernatural_present: str = Form("no"),
    super_types: str = Form(""),
    super_tone: str = Form(""),
):
    prompt_text = f"""
    Téma: {theme}
    Hlavní postava: {character}
    Další postavy: {other_characters}
    Nadpřirozené bytosti: {super_types if supernatural_present == 'yes' else 'ne'}
    Role nadpřirozených bytostí: {super_tone}
    Ponaučení: {moral}
    Délka: {length}
    """

    story = generate(prompt_text)

    return templates.TemplateResponse(
        "result.html",
        {
            "request": request,
            "story": story,
            "theme": theme,
            "character": character,
            "moral": moral,
            "length": length,
            "other_characters": other_characters,
            "supernatural_present": supernatural_present,
            "super_types": super_types,
            "super_tone": super_tone,
        }
    )
