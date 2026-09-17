import sys
from generator import generate_post
from publish import publish

def main():
    try:
        print("Генерирую пост...")
        post = generate_post()

        text = post.get("text")
        image = post.get("image")

        if not text:
            raise ValueError("Генератор вернул пустой текст")

        print("\n===== Сгенерированный пост =====")
        print(text)
        print("===============================")
        print("Картинка:", image)

        print("\nОтправляю в Telegram...")
        result = publish(text, image)

        message_id = result.get("result", {}).get("message_id")
        print(f"Успешно опубликовано! message_id = {message_id}")

    except Exception as e:
        print(f"\nОшибка при автопостинге: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
