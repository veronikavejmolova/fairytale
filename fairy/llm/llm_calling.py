from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI, OpenAIError
from sqlitedict import SqliteDict

load_dotenv(Path(__file__).parent.parent.parent / ".env")


client = OpenAI()
db = SqliteDict(Path(__file__).parent.parent.parent / "llm_cache.sqlite", autocommit=True)


def call_llm(prompt: str) -> str:
    if prompt in db:
        return db[prompt]

    try:
        resp = client.chat.completions.create(
            model="gpt-4.1",
            messages=[
                 {"role": "user", "content": prompt}
            ],
            temperature=0,  # lower temperature for more deterministic output
            max_tokens=1024
        )
        result = resp.choices[0].message.content
        db[prompt] = result
        return result

    except OpenAIError as e:
        error_message = f"Chyba při volání OpenAI API: {e}"
        print(error_message)
        return error_message
    except Exception as e:
        error_message = f"Nastala neočekávaná chyba: {e}"
        print(error_message)
        return error_message

if __name__ == '__main__':
    import time
    start = time.time()
    print(call_llm("tell me hello in three words"))
    print("First call took", time.time() - start)

if __name__ == '__main__':
    import time
    start = time.time()
    print(call_llm("Pověz mi krátký vtip o programátorovi."))
    print(f"První volání trvalo: {time.time() - start:.2f} s")
