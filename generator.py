import os
import random
import re
import time
import requests
from datetime import datetime

from images import get_character_for_today, get_image_for_post

# -------------------------------------------------------------
# Mercury 2.5 (Inception) config
# -------------------------------------------------------------

INCEPTION_API_KEY = os.environ.get("INCEPTION_API_KEY", "").strip()
INCEPTION_URL = "https://api.inceptionlabs.ai/v1/chat/completions"
INCEPTION_MODEL = "mercury-2.5"

MAX_RETRIES = 3
RETRY_DELAY = 3

SYSTEM_PROMPT = """Ты пишешь посты для Telegram-канала «Игры и Развитие 3–7» (@kids_brain_37).

Стиль:
- Два персонажа: Мира (девочка) и Тима (мальчик). В каждом посте используй ТОЛЬКО указанного персонажа.
- Текст обращён к РОДИТЕЛЯМ: мягкий, тёплый, живой тон.
- Лёгкий добрый юмор и мягкая ирония допустимы — они добавляют человечности. Но они должны быть разными каждый раз.
- Категорически избегай однообразных концовок. Не превращай каждый пост в вариацию «пока ребёнок занят — у тебя тишина / пауза / можно выдохнуть».
- Упоминания чая, кофе и любых напитков — только если в инструкции пользователя это явно разрешено. В остальные дни — никаких напитков вообще.
- Коротко, живо, по делу. Без воды и канцелярита.

Структура поста (строго):
1. Первая строка — цепляющий заголовок с эмодзи (🎯 / 📝 / 💡 / 📖)
2. 1–2 предложения про персонажа и ситуацию
3. Блок «Что делать:» с нумерованными шагами (3–5 пунктов)
4. Короткий живой штрих (1–2 предложения). Это может быть:
   • лёгкая узнаваемая деталь из жизни с детьми 3–7 лет
   • мягкая ирония
   • тёплое замечание
   • маленький неочевидный бонус
   Главное — чтобы этот штрих каждый раз звучал по-новому и не превращался в шаблон.
5. Строка «💡 Развивает: …»
6. В конце НЕ пиши хештеги — их добавит система

Категории:
- game — развивающая игра
- task — короткое задание
- tip — совет родителю (без персонажа или с лёгким упоминанием)
- story — короткая история + вопрос ребёнку

Пиши только текст поста на русском. Без кавычек вокруг всего текста. Без markdown-заголовков #."""

# -------------------------------------------------------------
# Вариативные элементы (для fallback)
# -------------------------------------------------------------

OBJECTS = [
    "мяч", "кубик", "книга", "ложка", "машинка", "фломастер",
    "игрушка", "ключи", "носки", "кружка", "подушка", "тарелка",
    "карандаш", "платок", "коробка", "мягкая игрушка", "расческа",
    "часы", "пуговица", "лента", "камешек", "листочек",
]

PLACES = [
    "в комнате", "на кухне", "в коридоре", "в детской", "на столе",
    "под диваном", "на подоконнике", "в шкафу", "на полу",
]

SKILLS = [
    "внимание", "память", "речь", "мышление", "креативность",
    "наблюдательность", "мелкую моторику", "логику",
    "фантазию", "усидчивость", "пространственное мышление",
    "эмоциональный интеллект",
]

AGES = ["3–5 лет", "3–6 лет", "4–6 лет", "4–7 лет", "3–7 лет", "5–7 лет"]
TIMES = ["10–15 минут", "15–20 минут", "10 минут", "15 минут", "20 минут", "5–10 минут"]
SHAPES = ["круглой формы", "квадратной формы", "прямоугольной формы", "треугольной формы", "длинной формы", "овальной формы"]
COLORS = ["красный", "синий", "зелёный", "жёлтый", "оранжевый", "фиолетовый"]
LETTERS = ["М", "С", "К", "Л", "П", "Б", "Т", "Н", "Р", "Д"]

WORDS_BY_LETTER = {
    "М": ["мама", "мыло", "машина", "мяч", "молоко", "мишка"],
    "С": ["сок", "солнце", "собака", "стол", "слоник", "сумка"],
    "К": ["кот", "книга", "кран", "кубик", "конфета", "корабль"],
    "Л": ["луна", "лист", "лампа", "ложка", "лёд", "ласточка"],
    "П": ["папа", "парта", "пазл", "подушка", "пирог", "петух"],
    "Б": ["банан", "банка", "бусы", "ботинок", "бабочка", "белка"],
    "Т": ["трава", "тапок", "тарелка", "тигр", "торт", "туча"],
    "Н": ["нос", "ножницы", "носок", "небо", "нитка", "ночь"],
    "Р": ["рыба", "рука", "радуга", "робот", "роза", "рюкзак"],
    "Д": ["дом", "дерево", "дыня", "дверь", "дождик", "динозавр"],
}

CHARACTERS = {
    "Мира": {"name": "Мира", "ended": "а", "ended_past": "а", "pronoun": "она"},
    "Тима": {"name": "Тима", "ended": "", "ended_past": "", "pronoun": "он"},
}

BASE_HASHTAGS = ["#развитиедетей", "#игрыдлядетей", "#занятиядома", "#kids_brain"]
CATEGORY_HASHTAGS = {
    "game": ["#игры3года", "#развивающиеигры", "#играемдома", "#10минуттишины"],
    "task": ["#заданиядлядетей", "#развивающиезанятия", "#домашниезадания"],
    "tip": ["#советыродителям", "#воспитаниедетей", "#родителям"],
    "story": ["#сказкидлядетей", "#историидлядетей", "#читаемдетям"],
}
SKILL_HASHTAGS = {
    "внимание": ["#внимание", "#игрынавнимание"],
    "память": ["#память", "#развитиепамяти"],
    "речь": ["#речь", "#развитиеречи"],
    "мышление": ["#мышление", "#логика"],
    "креативность": ["#творчество", "#креативность"],
    "наблюдательность": ["#наблюдательность"],
    "мелкую моторику": ["#моторика", "#мелкаямоторика"],
    "логику": ["#логика", "#логическоемышление"],
    "фантазию": ["#фантазия", "#воображение"],
    "усидчивость": ["#усидчивость"],
    "пространственное мышление": ["#пространственноемышление"],
    "эмоциональный интеллект": ["#эмоции", "#эмоциональныйинтеллект"],
}
AGE_HASHTAGS = {
    "3–5 лет": ["#3года", "#4года", "#5лет"],
    "3–6 лет": ["#3года", "#4года", "#5лет", "#6лет"],
    "4–6 лет": ["#4года", "#5лет", "#6лет"],
    "4–7 лет": ["#4года", "#5лет", "#6лет", "#7лет"],
    "3–7 лет": ["#3года", "#4года", "#5лет", "#6лет", "#7лет"],
    "5–7 лет": ["#5лет", "#6лет", "#7лет"],
}


def make_hashtags(category: str, skill: str = None, age: str = None) -> str:
    tags = set(BASE_HASHTAGS)
    tags.update(CATEGORY_HASHTAGS.get(category, []))
    if skill:
        for key, vals in SKILL_HASHTAGS.items():
            if key in skill.lower() or skill.lower() in key:
                tags.update(vals)
                break
    if age:
        tags.update(AGE_HASHTAGS.get(age, []))
    selected = list(tags)
    random.shuffle(selected)
    return " ".join(selected[:7])


def _two_skills():
    return random.sample(SKILLS, 2)


def _is_tea_day() -> bool:
    """Через день: чётный день месяца — можно упомянуть чай/кофе."""
    return datetime.now().day % 2 == 0


# -------------------------------------------------------------
# Mercury generation (с retry)
# -------------------------------------------------------------

def _call_mercury(category: str, character: str):
    if not INCEPTION_API_KEY:
        print("[mercury] КРИТИЧНО: INCEPTION_API_KEY не задан в secrets")
        return None

    age = random.choice(AGES)
    skill1, skill2 = _two_skills()
    time_str = random.choice(TIMES)
    tea_allowed = _is_tea_day()

    tea_instruction = (
        "Сегодня разрешено очень лёгкое упоминание чая или кофе (не обязательно). Если используешь — только один раз и не в центре внимания."
        if tea_allowed
        else "Сегодня НЕ упоминай чай, кофе и любые напитки вообще."
    )

    user_prompt = f"""Напиши один пост категории «{category}».
Персонаж: {character} (если tip — персонаж опционален, но если упоминаешь — только {character}).
Возраст: {age}.
Время занятия: примерно {time_str}.
Навыки: {skill1}, {skill2}.
{tea_instruction}
Сделай пост уникальным. Особенно важна концовка: она должна быть живой и разной, без шаблонных фраз про тишину и паузу."""

    payload = {
        "model": INCEPTION_MODEL,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": 0.85,
        "max_completion_tokens": 1200,
        "reasoning_effort": "low",
    }
    headers = {
        "Authorization": f"Bearer {INCEPTION_API_KEY}",
        "Content-Type": "application/json",
    }

    last_error = None
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            print(f"[mercury] попытка {attempt}/{MAX_RETRIES}...")
            r = requests.post(INCEPTION_URL, headers=headers, json=payload, timeout=60)

            if r.status_code >= 400:
                body_preview = (r.text or "")[:400]
                print(f"[mercury] HTTP {r.status_code}: {body_preview}")
                last_error = f"HTTP {r.status_code}"
                if r.status_code in (401, 403, 402):
                    break
                time.sleep(RETRY_DELAY)
                continue

            data = r.json()
            text = data["choices"][0]["message"]["content"].strip()
            text = re.sub(r"^```(?:text|markdown)?\s*", "", text)
            text = re.sub(r"\s*```$", "", text)
            return text.strip()

        except requests.exceptions.Timeout:
            print(f"[mercury] таймаут на попытке {attempt}")
            last_error = "timeout"
            time.sleep(RETRY_DELAY)
        except Exception as e:
            print(f"[mercury] ошибка: {type(e).__name__}: {e}")
            last_error = str(e)
            time.sleep(RETRY_DELAY)

    print(f"[mercury] все попытки исчерпаны. Последняя ошибка: {last_error}")
    return None


def _detect_skill_from_text(text: str):
    lower = text.lower()
    for skill in SKILLS:
        if skill.lower() in lower:
            return skill
    return None


# -------------------------------------------------------------
# Template fallback
# -------------------------------------------------------------

GAME_TEMPLATES = [
    """🎯 Пока ребёнок считает шаги

{name} сегодня решил{ended} измерить всю квартиру шагами.
Стол, диван, путь до кухни — всё идёт в зачёт.

Что делать:
1. Попросите измерить комнату / стол / диван шагами
2. Можно записать результаты на бумажке
3. Спросите: «Что длиннее?»

И да, если он начнёт объяснять тебе правила измерения — просто кивай. Это важный момент.

💡 Развивает: {skill}""",
    """🎯 Предметы умеют пропадать

{name} только что обнаружил{ended}, что вещи умеют исчезать.
Особенно если их убрать, пока никто не смотрит.

Что делать:
1. Разложите {n} предметов на столе
2. Дайте 10–15 секунд посмотреть
3. Попросите отвернуться и уберите один
4. Спросите: «Что пропало?»

Главное — не подсказывать слишком быстро. Пусть немного помучается. Это полезно.

💡 Развивает: {skill}""",
    """🎯 Цветной квест по квартире

{name} получил{ended} задание: найти всё {color}.
Теперь ходит по дому с серьёзным видом охотника.

Что делать:
1. Назовите цвет
2. Ребёнок ищет 3–5 предметов этого цвета
3. Можно усложнить: «только круглое и {color}»

А если принесёт что-то совсем не того цвета — не торопись исправлять. Иногда это даже интереснее.

💡 Развивает: {skill}""",
    """🎯 Шпионская миссия

{name} получил{ended} секретное задание: найти {n} спрятанных предметов.

Что делать:
1. Спрячьте предметы {place}
2. Давайте простые подсказки
3. Когда найдёт все — обсудите, где было сложнее всего

Если вдруг скажет «я сам» — лучше отойти. Это важный момент.

💡 Развивает: {skill}""",
]

GAME_TEMPLATE_TEA = """🎯 Предметы умеют пропадать

{name} только что обнаружил{ended}, что вещи умеют исчезать.
Особенно если их убрать, пока никто не смотрит.

Что делать:
1. Разложите {n} предметов на столе
2. Дайте 10–15 секунд посмотреть
3. Попросите отвернуться и уберите один
4. Спросите: «Что пропало?»

Пока ищет — можно спокойно допить чай. Редко, но бывает.

💡 Развивает: {skill}"""

TASK_TEMPLATES = [
    """📝 Слова на букву «{letter}»

{name} сегодня собирает коллекцию слов на букву «{letter}».
Примеры: {word1}, {word2}, {word3}.

Что делать:
1. Назовите букву
2. Вместе придумайте 5–7 слов
3. Можно ограничить темой: дом / еда / животные

Если он придумает совсем странное слово — не спорь. Иногда это лучшая часть.

💡 Развивает: {skill}""",
    """📝 «Что было бы, если…»

{name} сегодня размышляет: «А что если бы у меня были крылья?»

Что делать:
1. Задайте один такой вопрос
2. Слушайте
3. Можно потом нарисовать ответ

И да, можно потом спросить: «А как ты догадался?» — они обычно очень гордятся ответом.

💡 Развивает: {skill}""",
    """📝 Найди форму

{name} ищет всё {shape}.

Что делать:
1. Найдите вместе 5 предметов нужной формы
2. Разложите их
3. Обсудите, чем похожи и чем отличаются

Если в процессе что-то упадёт — ну… хотя бы не скучно.

💡 Развивает: {skill}""",
]

TIP_TEMPLATES = [
    """💡 Совет, который работает лучше комплиментов

Хвалите за усилия, а не только за результат.
«Ты старался» работает заметно лучше, чем «ты умный».

Потому что «умный» — как будто подарок судьбы.
А «старался» — то, что ребёнок может повторить завтра.""",
    """💡 15 секунд перед тем, как исправлять

Не торопитесь сразу говорить «не так».
Дайте ребёнку 10–15 секунд подумать самому.

Иногда за эти секунды ребёнок сам всё понимает.""",
    """💡 10–15 минут без телефона

Качественное внимание важнее дорогих игрушек.
Даже 10 минут совместной игры без экрана дают больше,
чем час «рядом, но в телефоне».""",
]

STORY_TEMPLATES = [
    """📖 Короткая история + вопрос

Мира искала, откуда берётся энергия.
Пробовала книги, игры и задачки.
А потом поняла: энергия появляется, когда становится по-настоящему интересно.

Спросите ребёнка:
«А где ты сам берёшь энергию?»""",
    """📖 Короткая история + вопрос

Тима замечал мелочи, которые другие пропускали:
листочек, камешек, странную тень на стене.

Попросите ребёнка:
«Назови 3 мелочи, которые ты видишь вокруг себя прямо сейчас.»""",
]


def generate_game_template(character_name: str):
    age = random.choice(AGES)
    skill1, skill2 = _two_skills()
    char = CHARACTERS[character_name]
    objs = random.sample(OBJECTS, 3)

    templates = list(GAME_TEMPLATES)
    if _is_tea_day():
        templates.append(GAME_TEMPLATE_TEA)

    text = random.choice(templates).format(
        n=random.randint(3, 6),
        place=random.choice(PLACES),
        obj1=objs[0],
        obj2=objs[1],
        obj3=objs[2],
        skill=f"{skill1}, {skill2}",
        age=age,
        time=random.choice(TIMES),
        color=random.choice(COLORS),
        name=char["name"],
        ended=char["ended"],
    )
    return text, char["name"], skill1, age


def generate_task_template(character_name: str):
    age = random.choice(AGES)
    skill1, skill2 = _two_skills()
    char = CHARACTERS[character_name]
    letter = random.choice(LETTERS)
    words = WORDS_BY_LETTER[letter]
    text = random.choice(TASK_TEMPLATES).format(
        letter=letter,
        word1=words[0],
        word2=words[1],
        word3=words[2],
        shape=random.choice(SHAPES),
        obj1=random.choice(OBJECTS),
        skill=f"{skill1}, {skill2}",
        age=age,
        time=random.choice(TIMES),
        name=char["name"],
        ended=char["ended"],
    )
    return text, char["name"], skill1, age


def generate_tip_template():
    text = random.choice(TIP_TEMPLATES)
    return text, None, None, None


def generate_story_template(character_name: str):
    text = random.choice(STORY_TEMPLATES)
    if character_name == "Мира":
        text = text.replace("Тима", "Мира")
    else:
        text = text.replace("Мира", "Тима")
    return text, character_name, None, None


def generate_post():
    category = random.choices(
        ["game", "task", "tip", "story"],
        weights=[40, 30, 15, 15],
        k=1,
    )[0]

    character = get_character_for_today()
    text = None
    skill = None
    age = None
    used_mercury = False

    if not INCEPTION_API_KEY:
        print("[mercury] КРИТИЧНО: INCEPTION_API_KEY отсутствует. Текст будет из шаблона.")
    if not os.environ.get("AITUNNEL_API_KEY", "").strip():
        print("[images] КРИТИЧНО: AITUNNEL_API_KEY отсутствует. Генерация картинки упадёт.")

    if INCEPTION_API_KEY:
        print(f"[mercury] генерирую категорию={category}, персонаж={character}...")
        text = _call_mercury(category, character)
        if text:
            skill = _detect_skill_from_text(text)
            used_mercury = True
            print("[mercury] успех — токены списаны")
        else:
            print("[mercury] fallback на шаблоны (токены не списаны)")

    if not text:
        if category == "game":
            text, character, skill, age = generate_game_template(character)
        elif category == "task":
            text, character, skill, age = generate_task_template(character)
        elif category == "tip":
            text, character, skill, age = generate_tip_template()
            character = get_character_for_today()
        else:
            text, character, skill, age = generate_story_template(character)

    if character is None:
        character = get_character_for_today()

    hashtags = make_hashtags(category, skill, age)
    full_text = text.rstrip() + "\n\n" + hashtags

    image = get_image_for_post(
        character=character,
        category=category,
        text=full_text,
    )

    return {
        "text": full_text,
        "image": image,
        "category": category,
        "character": character,
        "used_mercury": used_mercury,
    }


if __name__ == "__main__":
    post = generate_post()
    print(post["text"])
    print("\n---")
    print("Category:", post["category"])
    print("Character:", post.get("character"))
    print("Used Mercury:", post.get("used_mercury"))
    print("Image:", post["image"] if not isinstance(post["image"], bytes) else f"bytes({len(post['image'])})")
