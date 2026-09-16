import random

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
# Генерация поста
# -----------------------------

def generate_game():
    template = random.choice(GAME_TEMPLATES)
    return template.format(
        n=random.randint(3, 6),
        place=random.choice(PLACES),
        obj1=random.choice(OBJECTS),
        obj2=random.choice(OBJECTS),
        obj3=random.choice(OBJECTS),
        skill=random.choice(SKILLS),
        emoji=random.choice(EMOJIS),
    )

def generate_task():
    template = random.choice(TASK_TEMPLATES)
    letter = random.choice(LETTERS)
    words = WORDS_BY_LETTER[letter]
    return template.format(
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
    template = random.choice(TIP_TEMPLATES)
    return template.format(emoji=random.choice(EMOJIS))

def generate_story():
    template = random.choice(STORY_TEMPLATES)
    return template.format(emoji=random.choice(EMOJIS))

# -----------------------------
# Главная функция
# -----------------------------

def generate_post():
    category = random.choice(["game", "task", "tip", "story"])

    if category == "game":
        return generate_game()
    if category == "task":
        return generate_task()
    if category == "tip":
        return generate_tip()
    if category == "story":
        return generate_story()

    return "Сегодня маленькое задание для развития внимания 😊"


if __name__ == "__main__":
    print(generate_post())

