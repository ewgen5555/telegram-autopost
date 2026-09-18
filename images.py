import random

# -----------------------------
# Тематические картинки (пока через picsum — временное решение)
# Позже можно заменить на свои или тематические Unsplash/другие
# -----------------------------

GAME_IMAGES = [
    "https://picsum.photos/seed/game1/800/600",
    "https://picsum.photos/seed/game2/800/600",
    "https://picsum.photos/seed/game3/800/600",
    "https://picsum.photos/seed/game4/800/600",
    "https://picsum.photos/seed/kidsplay/800/600",
    "https://picsum.photos/seed/toys/800/600",
]

TASK_IMAGES = [
    "https://picsum.photos/seed/task1/800/600",
    "https://picsum.photos/seed/task2/800/600",
    "https://picsum.photos/seed/task3/800/600",
    "https://picsum.photos/seed/learning/800/600",
]

TIP_IMAGES = [
    "https://picsum.photos/seed/tip1/800/600",
    "https://picsum.photos/seed/tip2/800/600",
    "https://picsum.photos/seed/parent/800/600",
]

STORY_IMAGES = [
    "https://picsum.photos/seed/story1/800/600",
    "https://picsum.photos/seed/story2/800/600",
    "https://picsum.photos/seed/story3/800/600",
    "https://picsum.photos/seed/fairytale/800/600",
]


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
