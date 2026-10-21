import os
import base64
import random
import time
import requests
from datetime import date

# -------------------------------------------------------------
# AITUNNEL + Seedream 5.0 Flash
# -------------------------------------------------------------
AITUNNEL_API_KEY = os.environ.get("AITUNNEL_API_KEY", "").strip()
AITUNNEL_URL = "https://api.aitunnel.ru/v1/images/generations"
IMAGE_MODEL = "seedream-5-0-flash"

# Сколько попыток при ошибке сети / 5xx
MAX_RETRIES = 3
RETRY_DELAY = 4  # секунд

CHARACTER_DESC = {
    "Мира": (
        "a cute 5-6 year old girl named Mira, short light brown hair with a small bow, "
        "big friendly brown eyes, soft rosy cheeks, pastel yellow dress and white sneakers"
    ),
    "Тима": (
        "a cute 5-6 year old boy named Tima, short messy light brown hair, "
        "big curious brown eyes, freckles, light blue t-shirt, beige shorts and sneakers"
    ),
}

# Разнообразные комнаты и ракурсы — чтобы картинки не были однообразными
ROOMS = [
    "cozy living room with a sofa and a window with daylight",
    "bright children's room with a small table and toy shelf",
    "kitchen with a wooden table and soft morning light",
    "hallway with a rug and a door in the background",
    "play corner with cushions and scattered toys on the floor",
    "room near a large window with soft natural light",
]

CAMERA_ANGLES = [
    "wide shot, full body visible, camera pulled back",
    "medium-wide shot from slightly above, full scene",
    "three-quarter view, character fully visible in the room",
    "eye-level wide composition, environment clearly seen",
]

LIGHTING = [
    "warm soft daylight",
    "gentle morning light from the window",
    "bright and airy indoor lighting",
    "soft golden afternoon light",
]

STYLE_SUFFIX = (
    "children's book illustration style, full scene composition, "
    "character is part of the environment, room and objects clearly visible, "
    "NOT a portrait, NOT a close-up face, NOT head and shoulders only, "
    "NOT cropped at the waist, full body or three-quarter body must be visible, "
    "camera pulled back, medium-wide angle, bright gentle colors, "
    "cozy home interior, no text, no letters, no watermarks, no logos"
)


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
        ("шаг", "walking and counting steps across the room"),
        ("счита", "counting objects"),
        ("закрывает глаза", "eyes closed, listening carefully"),
        ("закрыл глаза", "eyes closed"),
        ("закрыла глаза", "eyes closed"),
        ("шпион", "playing spy, peeking around a corner"),
        ("детектив", "playing detective, searching the room"),
        ("прячет", "hiding objects under furniture"),
        ("спрятан", "searching for hidden objects under a sofa"),
        ("рису", "drawing at a small table"),
        ("цвет", "collecting colored objects from around the room"),
        ("форм", "finding square and round objects"),
        ("памят", "memory game with objects on a table"),
        ("звук", "listening to sounds with eyes closed"),
        ("красн", "looking for red objects"),
        ("предмет", "various household objects around"),
        ("диван", "looking under a sofa"),
        ("карту", "drawing a treasure map on paper"),
    ]
    found = []
    for ru, en in keywords:
        if ru in text_l and en not in found:
            found.append(en)
    return found[:4]


def build_image_prompt(character: str, category: str, post_text: str) -> str:
    desc = CHARACTER_DESC.get(character, CHARACTER_DESC["Мира"])
    objects = _extract_scene_objects(post_text)
    room = random.choice(ROOMS)
    angle = random.choice(CAMERA_ANGLES)
    light = random.choice(LIGHTING)

    if objects:
        scene_bits = ", ".join(objects)
        action = f"in a {room}, {scene_bits}"
    else:
        defaults = {
            "game": "playing an educational game with household objects scattered around",
            "task": "doing a learning activity with paper and pencils on a small table",
            "tip": "standing near toys and a window, looking thoughtful",
            "story": "sitting on a soft carpet listening with curiosity",
        }
        action = f"in a {room}, {defaults.get(category, 'playing with toys')}"

    # Добавляем случайный мелкий проп для разнообразия
    extra_props = [
        "a few colorful building blocks on the floor",
        "a soft toy nearby",
        "a small plant on the windowsill",
        "a rug with a simple pattern",
        "sunlight casting soft shadows",
    ]
    extra = random.choice(extra_props)

    return (
        f"{desc}, {action}, {extra}. "
        f"{angle}, {light}. "
        f"Full body visible, environment and props must be clearly seen. "
        f"{STYLE_SUFFIX}"
    )


def _call_seedream(prompt: str) -> bytes | str | None:
    """
    Возвращает:
      - bytes  — сырая картинка (из b64_json)
      - str    — публичный URL
      - None   — ошибка после всех попыток
    """
    if not AITUNNEL_API_KEY:
        print("[images] КРИТИЧНО: AITUNNEL_API_KEY не задан в secrets")
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

    last_error = None
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            print(f"[images] попытка {attempt}/{MAX_RETRIES} через {IMAGE_MODEL}...")
            r = requests.post(AITUNNEL_URL, headers=headers, json=payload, timeout=90)

            if r.status_code >= 400:
                body_preview = (r.text or "")[:300]
                print(f"[images] HTTP {r.status_code}: {body_preview}")
                last_error = f"HTTP {r.status_code}"
                # 401/403 — ключ плохой, нет смысла ретраить
                if r.status_code in (401, 403, 402):
                    break
                time.sleep(RETRY_DELAY)
                continue

            data = r.json()
            items = data.get("data") or []
            if not items:
                print(f"[images] пустой data: {str(data)[:300]}")
                last_error = "empty data"
                time.sleep(RETRY_DELAY)
                continue

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
            last_error = "unknown response format"
            break

        except requests.exceptions.Timeout:
            print(f"[images] таймаут на попытке {attempt}")
            last_error = "timeout"
            time.sleep(RETRY_DELAY)
        except Exception as e:
            print(f"[images] ошибка: {type(e).__name__}: {e}")
            last_error = str(e)
            time.sleep(RETRY_DELAY)

    print(f"[images] все попытки исчерпаны. Последняя ошибка: {last_error}")
    return None


def get_image_for_post(character: str, category: str, text: str) -> bytes | str:
    """
    Возвращает bytes или URL.
    Если API недоступен — поднимает RuntimeError (чтобы workflow падал, а не ставил одну и ту же картинку).
    """
    prompt = build_image_prompt(character, category, text)
    print(f"[images] prompt: {prompt[:250]}...")

    result = _call_seedream(prompt)
    if result is not None:
        return result

    # Больше не используем старые одинаковые портреты — лучше упасть, чем однообразие
    raise RuntimeError(
        "Не удалось сгенерировать картинку через Seedream после всех попыток. "
        "Проверь AITUNNEL_API_KEY и баланс. Workflow остановлен специально, "
        "чтобы не публиковать одну и ту же картинку каждый день."
    )


def get_image_for_character(character: str, mood: str = None, category: str = "game", text: str = "") -> bytes | str:
    return get_image_for_post(character, category, text)
