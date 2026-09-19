import random
import os

# -----------------------------
# Персонажи и выражения
# -----------------------------
# Ожидаемые файлы в репозитории:
#   assets/mira/smile.jpg, think.jpg, surprise.jpg, focus.jpg, sly.jpg
#   assets/tima/smile.jpg, think.jpg, surprise.jpg, focus.jpg, sly.jpg
#
# Пока файлов нет — используется fallback на picsum.

EXPRESSIONS = ["smile", "think", "surprise", "focus", "sly"]

# Какая эмоция лучше подходит под тип поста
CATEGORY_MOOD = {
    "game": ["smile", "sly", "focus", "think"],
    "task": ["think", "focus", "smile"],
    "tip": ["smile", "think"],
    "story": ["smile", "think", "surprise"],
}

# Более точный маппинг по ключевым словам шаблона (опционально)
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

# Raw GitHub URLs (заработают после загрузки файлов в assets/)
REPO_RAW = "https://raw.githubusercontent.com/ewgen5555/telegram-autopost/main"

MIRA_IMAGES = {
    "smile": f"{REPO_RAW}/assets/mira/smile.jpg",
    "think": f"{REPO_RAW}/assets/mira/think.jpg",
    "surprise": f"{REPO_RAW}/assets/mira/surprise.jpg",
    "focus": f"{REPO_RAW}/assets/mira/focus.jpg",
    "sly": f"{REPO_RAW}/assets/mira/sly.jpg",
}

TIMA_IMAGES = {
    "smile": f"{REPO_RAW}/assets/tima/smile.jpg",
    "think": f"{REPO_RAW}/assets/tima/think.jpg",
    "surprise": f"{REPO_RAW}/assets/tima/surprise.jpg",
    "focus": f"{REPO_RAW}/assets/tima/focus.jpg",
    "sly": f"{REPO_RAW}/assets/tima/sly.jpg",
}

# Временный fallback, пока картинки не залиты
FALLBACK = {
    "mira": [
        "https://picsum.photos/seed/mira1/800/800",
        "https://picsum.photos/seed/mira2/800/800",
        "https://picsum.photos/seed/mira3/800/800",
    ],
    "tima": [
        "https://picsum.photos/seed/tima1/800/800",
        "https://picsum.photos/seed/tima2/800/800",
        "https://picsum.photos/seed/tima3/800/800",
    ],
}

# Флаг: ставим True, когда файлы реально лежат в assets/
ASSETS_READY = {
    "mira": False,  # поставить True после загрузки 5 файлов Миры
    "tima": False,  # поставить True после загрузки 5 файлов Тимы
}


def pick_mood(category: str, text: str = "") -> str:
    """Выбирает выражение лица под категорию и текст поста."""
    text_lower = (text or "").lower()

    for keyword, mood in KEYWORD_MOOD.items():
        if keyword in text_lower:
            return mood

    options = CATEGORY_MOOD.get(category, EXPRESSIONS)
    return random.choice(options)


def get_image_for_character(character: str, mood: str = None, category: str = "game", text: str = "") -> str:
    """
    character: "Мира" или "Тима"
    mood: smile / think / surprise / focus / sly (если None — выбирается автоматически)
    """
    if mood is None:
        mood = pick_mood(category, text)

    key = "mira" if character == "Мира" else "tima"
    images = MIRA_IMAGES if key == "mira" else TIMA_IMAGES

    if ASSETS_READY.get(key) and mood in images:
        return images[mood]

    # Fallback
    return random.choice(FALLBACK[key])


def get_image_for_category(category: str):
    """Обратная совместимость со старым кодом."""
    # Старый вызов без персонажа — просто случайный fallback
    return random.choice(FALLBACK["mira"] + FALLBACK["tima"])
