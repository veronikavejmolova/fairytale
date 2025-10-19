from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from starlette.templating import Jinja2Templates
from fairy.llm.generator import generate
import uvicorn
from pathlib import Path

app = FastAPI()
TEMPLATES_DIR = Path(__file__).parent / "frontend"
templates = Jinja2Templates(directory=TEMPLATES_DIR)

# Step 1: theme
@app.get("/theme", response_class=HTMLResponse)
async def theme(request: Request):
    return templates.TemplateResponse("theme.html", {"request": request})

# Step 2: character
@app.post("/character", response_class=HTMLResponse)
async def character(request: Request, theme: str = Form(...)):
    return templates.TemplateResponse("character.html", {"request": request, "theme": theme})

# Step 3: moral
@app.post("/moral", response_class=HTMLResponse)
async def moral(request: Request, theme: str = Form(...), character: str = Form(...)):
    return templates.TemplateResponse("moral.html", {"request": request, "theme": theme, "character": character})

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
    return templates.TemplateResponse("result.html", {"request": request, "story": story})

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)