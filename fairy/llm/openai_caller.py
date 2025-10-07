from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

from sqlitedict import SqliteDict

load_dotenv(Path(__file__).parent.parent / ".env")

client = OpenAI()
db = SqliteDict(Path(__file__).parent.parent / "llm_cache.sqlite", autocommit=True)


@lru_cache(maxsize=None)
def call_llm(prompt: str):
    if prompt in db:
        return db[prompt]

    resp = client.chat.completions.create(
        model="gpt-4.1",
        messages=[
            {"role": "user", "content": prompt}
        ],
        temperature=0,  # lower temperature for more deterministic output
        max_tokens=1024  # limit the response length
    )
    result = resp.choices[0].message.content
    db[prompt] = result
    return result



if __name__ == '__main__':
    import time
    start = time.time()
    print(call_llm("tell me hello in three words"))
    print("First call took", time.time() - start)

