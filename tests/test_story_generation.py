from dotenv import load_dotenv

from fairy.llm.generator import generate
from fairy.llm.llm_calling import call_llm

load_dotenv("../../.env")


def test_generate_story():
    text = generate("o chytré lišce a hloupém vlkovi")
    assert text
    assert "lišce" in text or "liška" in text.lower()


def test_is_it_funny():
    text = generate("o chytré lišce a hloupém vlkovi")
    response = call_llm("Is following story funny? Answer Yes or No.\n\n" + text)
    assert "yes" in response.lower()
