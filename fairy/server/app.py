from fastapi import FastAPI

from fairy.llm.generator import generate

app = FastAPI()


@app.get("/")
async def root():
    return {"message": generate("hello")}

