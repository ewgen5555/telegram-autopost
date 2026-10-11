import os
import base64
import random
import requests
from datetime import date

# -------------------------------------------------------------
# AITUNNEL + Seedream 5.0 Flash
# -------------------------------------------------------------
AITUNNEL_API_KEY = os.environ.get("AITUNNEL_API_KEY", "").strip()
AITUNNEL_URL = "https://api.aitunnel.ru/v1/images/generations"
IMAGE_MODEL = "seedream-5-0-flash"

CHARACTER_DESC = {
    "Мира": (
        "a cute 5-6 year old girl named Mira, short light brown hair with a small bow, "
        "big friendly brown eyes, soft rosy cheeks, pastel yellow dress and white sneakers, "
        "shown full body or three-quarter view"
    ),
    "Тима": (
        "a cute 5-6 year old boy named Tima, short messy light brown hair, "
        "big curious brown eyes, freckles, light blue t-shirt, beige shorts and sneakers, "
        "shown full body or three-quarter view"
    ),
}

STYLE_SUFFIX = (
    "wide shot children's book illustration, full scene composition, "
    "character is part of the environment, room and objects clearly visible, "
    "NOT a portrait, NOT a close-up face, NOT head and shoulders only, "
    "camera pulled back, medium-wide angle, warm soft lighting, bright gentle colors, "
    "cozy home interior, no text, no letters, no watermarks, no logos"
)

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
    """Чётный день месяца → Мира, нечётный → Тима."""
    day = date.today().day
    return "Мира" if day % 2 == 0 else "Тима"


def _extract_scene_objects(text: str) -> list[str]:
    text_l = (text or "").lower()
    keywords = [
        ("носк", "colorful socks on the floor"),
        ("пуговиц", "a small button in his hands"),
        ("коробк", "an open cardboard box with toys inside"),
        ("чемодан", "an old suitcase"),
        ("простын", "a bedsheet tent"),
        ("ложк", "a spoon"),
        ("расческ", "a comb"),
        ("лент", "a ribbon"),
        ("карандаш", "pencils and paper on a table"),
        ("фломастер", "markers and a drawing"),
        ("книг", "an open book"),
        ("кубик", "colorful building blocks"),
        ("мяч", "a ball"),
        ("машинк", "a toy car"),
        ("игрушк", "scattered toys"),
        ("подушк", "a pillow"),
        ("тарелк", "a plate"),
        ("кружк", "a mug"),
        ("ключ", "keys"),
        ("камеш", "small stones"),
        ("монет", "coins"),
        ("шаг", "walking and counting steps across the living room"),
        ("счита", "counting objects"),
        ("закрывает глаза", "eyes closed, listening carefully"),
        ("закрыл глаза", "eyes closed"),
        ("закрыла глаза", "eyes closed"),
        ("шпион", "playing spy, peeking around a corner"),
        ("детектив", "playing detective, searching the room"),
        ("прячет", "hiding objects under furniture"),
        ("спрятан", "searching for hidden objects under a sofa"),
        ("рису", "drawing at a small table"),
        ("цвет", "collecting red and blue objects from around the room"),
        ("форм", "finding square and round objects"),
        ("памят", "memory game with objects on a table"),
        ("звук", "listening to sounds with eyes closed"),
        ("красн", "looking for red objects"),
        ("предмет", "various household objects around him"),
        ("диван", "looking under a sofa"),
        ("карту", "drawing a treasure map on paper"),
    ]
    found = []
    for ru, en in keywords:
        if ru in text_l and en not in found:
            found.append(en)
    return found[:5]


def build_image_prompt(character: str, category: str, post_text: str) -> str:
    desc = CHARACTER_DESC.get(character, CHARACTER_DESC["Мира"])
    objects = _extract_scene_objects(post_text)

    if objects:
        scene_bits = ", ".join(objects)
        action = f"in a cozy apartment room, {scene_bits}"
    else:
        defaults = {
            "game": "in a cozy living room, playing an educational game with household objects scattered around",
            "task": "sitting at a small kids table doing a learning activity with paper and pencils",
            "tip": "in a bright home room with toys and a window in the background",
            "story": "sitting on a carpet in a children's room listening with curiosity",
        }
        action = defaults.get(category, "in a cozy home room with toys around")

    return (
        f"{desc}, {action}. "
        f"Full body visible, environment and props must be clearly seen. "
        f"{STYLE_SUFFIX}"
    )


def _call_seedream(prompt: str) -> bytes | str | None:
    """
    Возвращает:
      - bytes  — сырая картинка (из b64_json)
      - str    — публичный URL
      - None   — ошибка
    """
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
            print(f"[images] готово (url): {url[:80]}...")
            return url

        b64 = item.get("b64_json")
        if b64:
            print("[images] получен b64_json, декодирую...")
            if "," in b64 and b64.strip().startswith("data:"):
                b64 = b64.split(",", 1)[1]
            image_bytes = base64.b64decode(b64)
            print(f"[images] готово (bytes): {len(image_bytes)} байт")
            return image_bytes

        print(f"[images] неизвестный формат ответа: {list(item.keys())}")
        return None

    except Exception as e:
        print(f"[images] ошибка генерации: {e}")
        return None


def get_image_for_post(character: str, category: str, text: str) -> bytes | str:
    """
    Возвращает bytes (файл) или str (URL).
    При ошибке API — fallback URL старого портрета.
    """
    prompt = build_image_prompt(character, category, text)
    print(f"[images] prompt: {prompt[:220]}...")

    result = _call_seedream(prompt)
    if result is not None:
        return result

    fallbacks = FALLBACK_URLS.get(character) or FALLBACK_URLS["Мира"]
    chosen = random.choice(fallbacks)
    print(f"[images] fallback → {chosen}")
    return chosen


def get_image_for_character(character: str, mood: str = None, category: str = "game", text: str = "") -> bytes | str:
    return get_image_for_post(character, category, text)
