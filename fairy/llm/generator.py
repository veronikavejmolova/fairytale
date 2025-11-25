from fairy.llm.llm_calling import call_llm


def generate(tema_pohadky: str, length: str = "medium") -> str:
    length_map = {
        "short": "1-10 vět",
        "medium": "10-20 vět",
        "long": "více než 20 vět"
    }
    length_text = length_map.get(length, "6–15 vět")

    final_prompt = f"""
    Napiš pohádku o délce {length_text}, na toto téma: "{tema_pohadky}".
    Odpověď vrať jako čistý text.
    """

    vygenerovany_pribeh = call_llm(final_prompt.strip())
    return vygenerovany_pribeh


if __name__ == '__main__':
    tema = "o veverce, která se bála výšek"
    pohadka = generate(tema, length="long")
    print("Vygenerovaná pohádka:")
    print(pohadka)
