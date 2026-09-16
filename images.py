import random

# -----------------------------
# Тематические картинки
# -----------------------------

GAME_IMAGES = [
    "https://picsum.photos/seed/game1/800/600",
    "https://picsum.photos/seed/game2/800/600",
    "https://picsum.photos/seed/game3/800/600",
]

TASK_IMAGES = [
    "https://picsum.photos/seed/task1/800/600",
    "https://picsum.photos/seed/task2/800/600",
]

TIP_IMAGES = [
    "https://picsum.photos/seed/tip1/800/600",
    "https://picsum.photos/seed/tip2/800/600",
]

STORY_IMAGES = [
    "https://picsum.photos/seed/story1/800/600",
    "https://picsum.photos/seed/story2/800/600",
]

# -----------------------------
# Функция выбора картинки по теме
# -----------------------------

def get_image_for_category(category: str):
    if category == "game":
        return random.choice(GAME_IMAGES)
    if category == "task":
        return random.choice(TASK_IMAGES)
    if category == "tip":
        return random.choice(TIP_IMAGES)
    if category == "story":
        return random.choice(STORY_IMAGES)

    return None
