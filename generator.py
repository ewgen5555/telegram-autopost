import os
import random
import re
import requests

from images import get_image_for_character

# -----------------------------
# Mercury 2.5 (Inception) config
# -----------------------------

INCEPTION_API_KEY = os.environ.get("INCEPTION_API_KEY", "").strip()
INCEPTION_URL = "https://api.inceptionlabs.ai/v1/chat/completions"
INCEPTION_MODEL = "mercury-2.5"

SYSTEM_PROMPT = """Ты пишешь посты для Telegram-канала «Игры и Развитие 3–7» (@kids_brain_37).

Стиль:
- Два персонажа: Мира (девочка) и Тима (мальчик). В каждом посте используй ОДНОГО из них (или обоих только в историях/фантазии).
- Текст обращён к РОДИТЕЛЯМ: мягкий добрый сарказм, без злости и без морализаторства.
- Акцент на «минуты тишины» / паузу для родителя, пока ребёнок занят.
- Коротко, живо, по делу. Без воды и канцелярита.
- Можно лёгкий рофл, но без фанатизма.

Структура поста (строго):
1. Первая строка — цепляющий заголовок с эмодзи (🎯 / 📝 / 💡 / 📖)
2. 1–2 предложения про персонажа и ситуацию
3. Блок «Что делать:» с нумерованными шагами (3–5 пунктов)
4. 1–2 предложения про бонус для родителя (тишина / пауза / чай)
5. Строка «💡 Развивает: …»
6. В конце НЕ пиши хештеги — их добавит система

Категории:
- game — развивающая игра
- task — короткое задание
- tip — совет родителю (без персонажа или с лёгким упоминанием)
- story — короткая история + вопрос ребёнку

Пиши только текст поста на русском. Без кавычек вокруг всего текста. Без markdown-заголовков #."""

# -----------------------------
# Вариативные элементы (для fallback)
# -----------------------------

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


# -----------------------------
# Mercury generation
# -----------------------------

def _call_mercury(category: str, character: str):
    if not INCEPTION_API_KEY:
        return None

    age = random.choice(AGES)
    skill1, skill2 = _two_skills()
    time = random.choice(TIMES)

    user_prompt = f"""Напиши один пост категории «{category}».
Персонаж: {character} (если tip — персонаж опционален).
Возраст: {age}.
Время занятия: примерно {time}.
Навыки: {skill1}, {skill2}.
Сделай пост уникальным, не копируй шаблоны один в один."""

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

    try:
        r = requests.post(INCEPTION_URL, headers=headers, json=payload, timeout=60)
        r.raise_for_status()
        data = r.json()
        text = data["choices"][0]["message"]["content"].strip()
        text = re.sub(r"^```(?:text|markdown)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
        return text.strip()
    except Exception as e:
        print(f"[mercury] ошибка: {e}")
        return None


def _detect_skill_from_text(text: str):
    lower = text.lower()
    for skill in SKILLS:
        if skill.lower() in lower:
            return skill
    return None


# -----------------------------
# Template fallback
# -----------------------------

GAME_TEMPLATES = [
    """🎯 Пока ребёнок считает шаги — у тебя {time} тишины

{name} сегодня решил{ended} измерить всю квартиру шагами.
Стол, диван, путь до кухни — всё идёт в зачёт.

Что делать:
1. Попросите измерить комнату / стол / диван шагами
2. Можно записать результаты на бумажке
3. Спросите: «Что длиннее?»

Бонус для вас: настоящие {time} без «мамаааа».
А ребёнку — чувство пространства и счёт.

💡 Развивает: {skill}""",
    """🎯 {time} относительной тишины (работает)

{name} только что обнаружил{ended}, что предметы умеют пропадать.
Особенно если их убрать, пока никто не смотрит.

Что делать:
1. Разложите {n} предметов на столе
2. Дайте 10–15 секунд посмотреть
3. Попросите отвернуться и уберите один
4. Спросите: «Что пропало?»

Пока ищет — можно допить чай.

💡 Развивает: {skill}""",
    """🎯 Цветной квест по квартире

{name} получил{ended} задание: найти всё {color}.
Теперь ходит по дому с серьёзным видом охотника.

Что делать:
1. Назовите цвет
2. Ребёнок ищет 3–5 предметов этого цвета
3. Можно усложнить: «только круглое и {color}»

Пока ищет — вы можете хотя бы постоять у окна.

💡 Развивает: {skill}""",
    """🎯 Шпионская миссия по квартире

{name} получил{ended} секретное задание: найти {n} спрятанных предметов.

Что делать:
1. Спрячьте предметы {place}
2. Давайте простые подсказки
3. Когда найдёт все — обсудите, где было сложнее всего

Пока ищет — дом относительно тих.

💡 Развивает: {skill}""",
]

TASK_TEMPLATES = [
    """📝 Слова на букву «{letter}» (и 10 минут спокойствия)

{name} сегодня собирает коллекцию слов на букву «{letter}».
Примеры: {word1}, {word2}, {word3}.

Что делать:
1. Назовите букву
2. Вместе придумайте 5–7 слов
3. Можно ограничить темой: дом / еда / животные

💡 Развивает: {skill}""",
    """📝 «Что было бы, если…» — фантазия без границ

{name} сегодня размышляет: «А что если бы у меня были крылья?»

Что делать:
1. Задайте один такой вопрос
2. Слушайте
3. Можно потом нарисовать ответ

💡 Развивает: {skill}""",
    """📝 Найди форму — квест для глаз и рук

{name} ищет всё {shape}.

Что делать:
1. Найдите вместе 5 предметов нужной формы
2. Разложите их
3. Обсудите, чем похожи и чем отличаются

💡 Развивает: {skill}""",
]

TIP_TEMPLATES = [
    """💡 Совет, который работает лучше комплиментов

Хвалите за усилия, а не только за результат.
«Ты старался» работает заметно лучше, чем «ты умный».

Потому что «умный» — как будто подарок судьбы.
А «старался» — то, что ребёнок может повторить завтра.""",
    """💡 15 секунд тишины перед тем, как исправлять

Не торопитесь сразу говорить «не так».
Дайте ребёнку 10–15 секунд подумать самому.

Иногда за эти секунды ребёнок сам всё понимает.""",
    """💡 10–15 минут без телефона — это уже подвиг

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


def generate_game_template():
    age = random.choice(AGES)
    skill1, skill2 = _two_skills()
    char = random.choice(list(CHARACTERS.values()))
    objs = random.sample(OBJECTS, 3)
    text = random.choice(GAME_TEMPLATES).format(
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


def generate_task_template():
    age = random.choice(AGES)
    skill1, skill2 = _two_skills()
    char = random.choice(list(CHARACTERS.values()))
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


def generate_story_template():
    text = random.choice(STORY_TEMPLATES)
    return text, None, None, None


def generate_post():
    category = random.choices(
        ["game", "task", "tip", "story"],
        weights=[40, 30, 15, 15],
        k=1,
    )[0]

    character = random.choice(["Мира", "Тима"])
    text = None
    skill = None
    age = None

    if INCEPTION_API_KEY:
        print(f"[mercury] генерирую категорию={category}, персонаж={character}...")
        text = _call_mercury(category, character)
        if text:
            skill = _detect_skill_from_text(text)
            print("[mercury] успех")
        else:
            print("[mercury] fallback на шаблоны")

    if not text:
        if category == "game":
            text, character, skill, age = generate_game_template()
        elif category == "task":
            text, character, skill, age = generate_task_template()
        elif category == "tip":
            text, character, skill, age = generate_tip_template()
        else:
            text, character, skill, age = generate_story_template()

    if character is None:
        character = random.choice(["Мира", "Тима"])

    hashtags = make_hashtags(category, skill, age)
    full_text = text.rstrip() + "\n\n" + hashtags

    image = get_image_for_character(
        character=character,
        category=category,
        text=full_text,
    )

    return {
        "text": full_text,
        "image": image,
        "category": category,
        "character": character,
    }


if __name__ == "__main__":
    post = generate_post()
    print(post["text"])
    print("\n---")
    print("Category:", post["category"])
    print("Character:", post.get("character"))
    print("Image:", post["image"])
