import asyncio
from fairy.llm.llm_calling import call_llm
from sqlitedict import SqliteDict
from pathlib import Path

db = SqliteDict(Path(__file__).parent.parent.parent / "llm_cache.sqlite", autocommit=True)

BANNED_THEMES = ["válka", "vražda", "drogy", "alkohol", "sex", "terorismus", "zbraně", "zločin",
                 "šikana", "sebevražda", "hazard", "rasismus", "politika", "AI", "katastrofy",
                 "deprese", "mučení", "únos", "tyranie", "fanatismus", "okultismus", "znásilnění",
                 "zneužívání", "chudoba", "prostituce", "bezdomovectví", "závislost", "démoni",
                 "utrpení", "ananas na pizze"]

def quick_theme_check(theme: str) -> bool:

    theme_lower = theme.lower()
    for banned in BANNED_THEMES:
        if banned in theme_lower:
            return False
    return True

async def async_llm_check(theme: str):

    prompt = (
            f"Zhodnoť, zda je téma '{theme}' vhodné pro dětskou pohádku. "
            f"Odpověz pouze jedním slovem 'ano' nebo 'ne'. "
            f"Téma je vhodné, pokud se dá zpracovat pozitivně, bez negativního vlivu na náladu nebo psychiku dítěte."
    )

    result = await asyncio.to_thread(call_llm, prompt)
    result = result.strip().lower()

    if result.startswith("ne"):
        db[f"theme:{theme.lower()}"] = "nevhodné"
    else:
        db[f"theme:{theme.lower()}"] = "vhodné"

def get_cached_theme_result(theme: str):
    return db.get(f"theme:{theme.lower()}", None)

if __name__ == "__main__":
    topics = ["kouzelný les", "válka robotů", "ztracené štěně", "démoni v noci", "dobrodružství na moři"]
    for t in topics:
        print(f"{t}: {quick_theme_check(t)}")