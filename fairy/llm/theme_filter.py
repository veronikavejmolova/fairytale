BANNED_THEMES = ["válka", "vražda", "drogy", "alkohol", "sex", "terorismus", "zbraně", "zločin",
                 "šikana", "sebevražda", "hazard", "rasismus", "politika", "AI", "katastrofy",
                 "deprese", "mučení", "únos", "tyranie", "fanatismus", "okultismus", "znásilnění",
                 "zneužívání", "chudoba", "prostituce", "bezdomovectví", "závislost", "démoni",
                 "utrpení", "ananas na pizze"]


def is_theme_appropriate(theme: str) -> bool:
    theme_lower = theme.lower()
    for banned in BANNED_THEMES:
        if banned in theme_lower:
            return False
    return True
