from generator import generate_post
from publish import publish

def main():
    # Генерируем новый пост
    post_text = generate_post()

    # Публикуем в Telegram-канал
    result = publish(post_text)

    print("Post sent:", post_text)
    print("Telegram response:", result)


if __name__ == "__main__":
    main()
