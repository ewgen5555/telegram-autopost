import random

from images import get_image_for_category

# -----------------------------
# Вариативные элементы
# -----------------------------

OBJECTS = [
    "мяч", "кубик", "книга", "ложка", "машинка", "фломастер",
    "игрушка", "ключи", "носки", "кружка", "подушка"
]

PLACES = [
    "в комнате", "на кухне", "в коридоре", "в детской", "на столе", "под диваном"
]

SKILLS = [
    "внимание", "память", "речь", "мышление", "креативность", "наблюдательность"
]

EMOJIS = ["😊", "✨", "🎯", "🤖", "🧠", "🐣", "📘", "🎲"]

# -----------------------------
# Шаблоны игр
# -----------------------------

GAME_TEMPLATES = [
    "Игра «Шпион». Спрячь {n} предмета {place}. Ребёнок ищет их по подсказкам. Прокачивает {skill}. {emoji}",
    "Игра «Звуковой детектив». Дай ребёнку угадать предмет по звуку: {obj1}, {obj2}, {obj3}. Отлично тренирует {skill}. {emoji}",
    "Игра «Кто пропал?». Положи {n} предметов, убери один. Ребёнок должен сказать, что исчезло. Развивает {skill}. {emoji}",
    "Игра «Память». Положи {n} вещей на стол, дай 10 секунд посмотреть. Потом накрой. Пусть перечислит. Тренирует {skill}. {emoji}",
]

# -----------------------------
# Шаблоны заданий
# -----------------------------

TASK_TEMPLATES = [
    "Задание дня: придумайте 3 слова на букву «{letter}». Например: {word1}, {word2}, {word3}. Развивает {skill}. {emoji}",
    "Задание: найдите дома 5 предметов {shape}. Потом обсудите, чем они похожи. Формирует {skill}. {emoji}",
    "Задание: придумайте историю из трёх предложений про {obj1}. Отлично тренирует {skill}. {emoji}",
]

SHAPES = ["круглой формы", "квадратной формы", "длинной формы"]

LETTERS = ["М", "С", "К", "Л", "П"]

WORDS_BY_LETTER = {
    "М": ["мама", "мыло", "машина"],
    "С": ["сок", "солнце", "собака"],
    "К": ["кот", "книга", "кран"],
    "Л": ["луна", "лист", "лампа"],
    "П": ["папа", "парта", "пазл"],
}

# -----------------------------
# Шаблоны советов
# -----------------------------

TIP_TEMPLATES = [
    "Совет: хвалите ребёнка за усилия, а не за результат. Это формирует здоровую мотивацию. {emoji}",
    "Совет: не исправляйте сразу — дайте время подумать. Так развивается самостоятельность. {emoji}",
    "Совет: показывайте пример — дети лучше учатся, когда видят, как делает взрослый. {emoji}",
    "Совет: задавайте вопросы «почему?» и «как ты думаешь?». Это развивает мышление. {emoji}",
]

# -----------------------------
# Шаблоны историй
# -----------------------------

STORY_TEMPLATES = [
    "История: «Робот Мира искал заряд. Он пробовал книги, игры и задачки — и нашёл энергию в любопытстве». Спросите ребёнка: где он сам берёт энергию? {emoji}",
    "История: «Совёнок Оли замечал мелочи, которые другие пропускали». Попросите ребёнка назвать 3 мелочи вокруг. {emoji}",
    "История: «Лисёнок Тико каждый день учился одному маленькому навыку — и стал мастером». Спросите ребёнка: чему он хочет научиться? {emoji}",
]

# -----------------------------
# Генерация постов
# -----------------------------

def generate_game():
    return GAME_TEMPLATES[random.randint(0, len(GAME_TEMPLATES)-1)].format(
        n=random.randint(3, 6),
        place=random.choice(PLACES),
        obj1=random.choice(OBJECTS),
        obj2=random.choice(OBJECTS),
        obj3=random.choice(OBJECTS),
        skill=random.choice(SKILLS),
        emoji=random.choice(EMOJIS),
    )

def generate_task():
    letter = random.choice(LETTERS)
    words = WORDS_BY_LETTER[letter]
    return TASK_TEMPLATES[random.randint(0, len(TASK_TEMPLATES)-1)].format(
        letter=letter,
        word1=words[0],
        word2=words[1],
        word3=words[2],
        shape=random.choice(SHAPES),
        obj1=random.choice(OBJECTS),
        skill=random.choice(SKILLS),
        emoji=random.choice(EMOJIS),
    )

def generate_tip():
    return TIP_TEMPLATES[random.randint(0, len(TIP_TEMPLATES)-1)].format(
        emoji=random.choice(EMOJIS)
    )

def generate_story():
    return STORY_TEMPLATES[random.randint(0, len(STORY_TEMPLATES)-1)].format(
        emoji=random.choice(EMOJIS)
    )

# -----------------------------
# Умный генератор
# -----------------------------

def generate_post():
    category = random.choice(["game", "task", "tip", "story"])

    text = None
    image = get_image_for_category(category)

    if category == "game":
        text = generate_game()
    elif category == "task":
        text = generate_task()
    elif category == "tip":
        text = generate_tip()
    elif category == "story":
        text = generate_story()

    return {
        "text": text,
        "image": image
    }

if __name__ == "__main__":
    print(generate_post())

