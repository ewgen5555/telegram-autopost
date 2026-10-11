import os
import re
import random
import requests
from datetime import date

# -------------------------------------------------------------
# AITUNNEL + Seedream 5.0 Flash
# -------------------------------------------------------------
AITUNNEL_API_KEY = os.environ.get("AITUNNEL_API_KEY", "").strip()
AITUNNEL_URL = "https://api.aitunnel.ru/v1/images/generations"
IMAGE_MODEL = "seedream-5-0-flash"

# -------------------------------------------------------------
# Фиксированные описания персонажей (для стабильности внешности)
# -------------------------------------------------------------
CHARACTER_DESC = {
    "Мира": (
        "cute little girl about 5-6 years old named Mira, short light brown hair with a small bow, "
        "big friendly brown eyes, soft rosy cheeks, wearing a simple pastel yellow dress and white sneakers"
    ),
    "Тима": (
        "cute little boy about 5-6 years old named Tima, short messy brown hair, "
        "big curious dark eyes, freckles on nose, wearing a light blue t-shirt, beige shorts and sneakers"
    ),
}

STYLE_SUFFIX = (
    "children's book illustration style, warm soft lighting, bright but gentle colors, "
    "cozy home interior, detailed but not cluttered, friendly atmosphere, "
    "no text, no letters, no watermarks, no logos, high quality"
)

# Старые портреты — только как аварийный fallback, если API недоступен
FALLBACK_URLS = {
    "Мира": [
        "https://litter.catbox.moe/m9qmlz.jpg",
        "https://litter.catbox.moe/gptjs0.jpg",
        "https://litter.catbox.moe/vrv539.jpg",
        "https://litter.catbox.moe/jbgzbw.jpg",
        "https://litter.catbox.moe/yjhijn.jpg",
    ],
    "Тима": [
        "https://litter.catbox.moe/ouuzdw.jpg",
    ],
}


def get_character_for_today() -> str:
    """
    Чередование по числу месяца:
    чётный день → Мира, нечётный → Тима.
    """
    day = date.today().day
    return "Мира" if day % 2 == 0 else "Тима"


def _extract_scene_objects(text: str) -> list[str]:
    """Достаём из текста поста предметы/действия, которые должны попасть в кадр."""
    text_l = (text or "").lower()

    keywords = [
        ("носк", "socks"),
        ("пуговиц", "a button"),
        ("коробк", "a cardboard box"),
        ("чемодан", "an old suitcase"),
        ("простын", "a bedsheet"),
        ("ложк", "a spoon"),
        ("расческ", "a comb"),
        ("лент", "a ribbon"),
        ("карандаш", "a pencil"),
        ("фломастер", "a marker"),
        ("книг", "a book"),
        ("кубик", "building blocks"),
        ("мяч", "a ball"),
        ("машинк", "a toy car"),
        ("игрушк", "toys"),
        ("подушк", "a pillow"),
        ("тарелк", "a plate"),
        ("кружк", "a mug"),
        ("ключ", "keys"),
        ("камеш", "small stones"),
        ("монет", "coins"),
        ("шаг", "counting steps across the room"),
        ("счита", "counting"),
        ("закрывает глаза", "with eyes closed"),
        ("закрыл глаза", "with eyes closed"),
        ("закрыла глаза", "with eyes closed"),
        ("шпион", "playing spy"),
        ("детектив", "playing detective"),
        ("прячет", "hiding objects"),
        ("спрятан", "searching for hidden objects"),
        ("рису", "drawing"),
        ("цвет", "looking for colored objects"),
        ("форм", "looking for shapes"),
        ("памят", "memory game"),
        ("звук", "listening carefully to sounds"),
    ]

    found = []
    for ru, en in keywords:
        if ru in text_l and en not in found:
            found.append(en)
    return found[:5]  # не больше 5, чтобы промпт не раздувался


def build_image_prompt(character: str, category: str, post_text: str) -> str:
    """
    Собираем промпт композиции:
    персонаж + действие/предметы из поста + единый стиль.
    """
    desc = CHARACTER_DESC.get(character, CHARACTER_DESC["Мира"])
    objects = _extract_scene_objects(post_text)

    if objects:
        scene_bits = ", ".join(objects)
        action = f"engaged in a children's activity involving {scene_bits}"
    else:
        # запасные сцены по категории
        defaults = {
            "game": "playing an educational game at home",
            "task": "doing a simple learning task at a table",
            "tip": "sitting calmly in a cozy room",
            "story": "listening to a short story with curiosity",
        }
        action = defaults.get(category, "playing and learning at home")

    prompt = (
        f"{desc}, {action}, full scene composition (not a close-up portrait), "
        f"character clearly visible in the middle of the scene, "
        f"{STYLE_SUFFIX}"
    )
    return prompt


def _call_seedream(prompt: str) -> str | None:
    """Генерация картинки через AITUNNEL (Seedream 5.0 Flash)."""
    if not AITUNNEL_API_KEY:
        print("[images] AITUNNEL_API_KEY не задан")
        return None

    payload = {
        "model": IMAGE_MODEL,
        "prompt": prompt,
        "resolution": "2K",
        "aspect_ratio": "1:1",
        "n": 1,
    }
    headers = {
        "Authorization": f"Bearer {AITUNNEL_API_KEY}",
        "Content-Type": "application/json",
    }

    try:
        print(f"[images] генерирую картинку через {IMAGE_MODEL}...")
        r = requests.post(AITUNNEL_URL, headers=headers, json=payload, timeout=90)
        r.raise_for_status()
        data = r.json()

        items = data.get("data") or []
        if not items:
            print(f"[images] пустой ответ: {data}")
            return None

        item = items[0]
        url = item.get("url")
        if url:
            print(f"[images] готово: {url[:80]}...")
            return url

        # если пришёл base64 — пока не умеем заливать, просто сообщаем
        if item.get("b64_json"):
            print("[images] получен b64_json, URL отсутствует — нужен хостинг")
            return None

        print(f"[images] неизвестный формат ответа: {item.keys()}")
        return None

    except Exception as e:
        print(f"[images] ошибка генерации: {e}")
        return None


def get_image_for_post(character: str, category: str, text: str) -> str:
    """
    Главная точка входа:
    1) собираем промпт композиции
    2) генерируем через Seedream
    3) при ошибке — fallback на старый портрет
    """
    prompt = build_image_prompt(character, category, text)
    print(f"[images] prompt: {prompt[:180]}...")

    url = _call_seedream(prompt)
    if url:
        return url

    # аварийный fallback
    fallbacks = FALLBACK_URLS.get(character) or FALLBACK_URLS["Мира"]
    chosen = random.choice(fallbacks)
    print(f"[images] fallback → {chosen}")
    return chosen


# Совместимость со старым импортом (если где-то ещё вызывается)
def get_image_for_character(character: str, mood: str = None, category: str = "game", text: str = "") -> str:
    return get_image_for_post(character, category, text)
