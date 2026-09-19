import random

# -----------------------------
# Персонажи и выражения
# -----------------------------
# Картинки залиты на litterbox (живут 72 часа с момента загрузки).
# Позже можно заменить на постоянный хостинг или assets/ в репо.

EXPRESSIONS = ["smile", "think", "surprise", "focus", "sly"]

CATEGORY_MOOD = {
    "game": ["smile", "sly", "focus", "think"],
    "task": ["think", "focus", "smile"],
    "tip": ["smile", "think"],
    "story": ["smile", "think", "surprise"],
}

KEYWORD_MOOD = {
    "пропал": "surprise",
    "изменилось": "surprise",
    "угадывает": "surprise",
    "считает": "think",
    "шаги": "think",
    "размышляет": "think",
    "фантази": "think",
    "шпион": "sly",
    "детектив": "sly",
    "хитр": "sly",
    "рисует": "focus",
    "линии": "focus",
    "сосредоточ": "focus",
    "память": "focus",
}

# Актуальные URL (загружены 2026-09-19, живут ~72ч)
MIRA_IMAGES = {
    "smile": "https://litter.catbox.moe/m9qmlz.jpg",
    "think": "https://litter.catbox.moe/gptjs0.jpg",
    "surprise": "https://litter.catbox.moe/vrv539.jpg",
    "focus": "https://litter.catbox.moe/jbgzbw.jpg",
    "sly": "https://litter.catbox.moe/yjhijn.jpg",
}

TIMA_IMAGES = {
    "smile": "https://litter.catbox.moe/ouuzdw.jpg",
    # остальные выражения Тимы — когда сгенерируем
    "think": "https://litter.catbox.moe/ouuzdw.jpg",
    "surprise": "https://litter.catbox.moe/ouuzdw.jpg",
    "focus": "https://litter.catbox.moe/ouuzdw.jpg",
    "sly": "https://litter.catbox.moe/ouuzdw.jpg",
}

FALLBACK = {
    "mira": list(MIRA_IMAGES.values()),
    "tima": list(TIMA_IMAGES.values()),
}


def pick_mood(category: str, text: str = "") -> str:
    text_lower = (text or "").lower()
    for keyword, mood in KEYWORD_MOOD.items():
        if keyword in text_lower:
            return mood
    options = CATEGORY_MOOD.get(category, EXPRESSIONS)
    return random.choice(options)


def get_image_for_character(character: str, mood: str = None, category: str = "game", text: str = "") -> str:
    if mood is None:
        mood = pick_mood(category, text)

    key = "mira" if character == "Мира" else "tima"
    images = MIRA_IMAGES if key == "mira" else TIMA_IMAGES

    if mood in images:
        return images[mood]

    return random.choice(FALLBACK[key])


def get_image_for_category(category: str):
    return random.choice(FALLBACK["mira"] + FALLBACK["tima"])
