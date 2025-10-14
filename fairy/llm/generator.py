from fairy.llm.llm_calling import call_llm

def generate(tema_pohadky: str) -> str:

    final_prompt = f"""
    Napiš mi poučnou větu o jedenácti slovech, na toto téma: "{tema_pohadky}".
    Odpověď vrať jako HTML text."
    """

    vygenerovany_pribeh_html = call_llm(final_prompt.strip())

    return vygenerovany_pribeh_html

if __name__ == '__main__':
    tema = "o veverce, která se bála výšek"
    pohadka = generate(tema)
    print("Vygenerovaná pohádka:")
    print(pohadka)