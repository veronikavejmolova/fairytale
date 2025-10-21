from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from starlette.templating import Jinja2Templates
from fairy.llm.generator import generate
from fairy.llm.theme_filter import is_theme_appropriate
import uvicorn
from pathlib import Path

app = FastAPI()
TEMPLATES_DIR = Path(__file__).parent / "frontend"
templates = Jinja2Templates(directory=TEMPLATES_DIR)

# Step 1: theme
@app.get("/", response_class=HTMLResponse)
async def step1(request: Request):
    return templates.TemplateResponse("step1.html", {"request": request})

# Step 2: character
@app.post("/step2", response_class=HTMLResponse)
async def step2(request: Request, theme: str = Form(...)):
    # Ověření vhodnosti tématu
    if not is_theme_appropriate(theme):
        return templates.TemplateResponse("error.html",{"request": request, "theme": theme})

    # Pokud téma prošlo, pokračujeme dál
    return templates.TemplateResponse("step2.html", {"request": request, "theme": theme})

# Step 3: moral
@app.post("/step3", response_class=HTMLResponse)
async def step3(request: Request, theme: str = Form(...), character: str = Form(...)):
    return templates.TemplateResponse("step3.html", {"request": request, "theme": theme, "character": character})

# Result 4: generate story
@app.post("/generate", response_class=HTMLResponse)
async def generate_story(
    request: Request,
    theme: str = Form(...),
    character: str = Form(...),
    moral: str = Form(...),
    prompt: str = Form("")
):
    prompt_text = f"Napiš pohádku, téma: {theme}, postava: {character}, ponaučení: {moral}, další: {prompt}"
    story = generate(prompt_text)
    return templates.TemplateResponse("result.html", {
        "request": request,
        "theme": theme,
        "character": character,
        "moral": moral,
        "prompt": prompt,
        "story": story})

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)