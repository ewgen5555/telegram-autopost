import os
import sys
import requests

def get_env(name: str) -> str:
    value = os.environ.get(name)
    if not value:
        print(f"Ошибка: не задана переменная окружения {name}")
        sys.exit(1)
    return value

TOKEN = get_env("TELEGRAM_BOT_TOKEN")
CHAT_ID = get_env("TELEGRAM_CHANNEL_ID")


def publish(text: str, image: str | bytes | None = None) -> dict:
    """
    Отправляет пост в Telegram-канал.
    image:
      - str  → URL картинки (sendPhoto с photo=url)
      - bytes → файл (sendPhoto multipart)
      - None → только текст
    """
    try:
        if isinstance(image, bytes):
            # Картинка как файл — без внешнего хостинга
            response = requests.post(
                f"https://api.telegram.org/bot{TOKEN}/sendPhoto",
                data={
                    "chat_id": CHAT_ID,
                    "caption": text,
                },
                files={
                    "photo": ("image.jpg", image, "image/jpeg"),
                },
                timeout=60,
            )
        elif isinstance(image, str) and image:
            response = requests.post(
                f"https://api.telegram.org/bot{TOKEN}/sendPhoto",
                data={
                    "chat_id": CHAT_ID,
                    "caption": text,
                    "photo": image,
                },
                timeout=30,
            )
        else:
            response = requests.post(
                f"https://api.telegram.org/bot{TOKEN}/sendMessage",
                data={
                    "chat_id": CHAT_ID,
                    "text": text,
                    "parse_mode": "HTML",
                },
                timeout=30,
            )

        response.raise_for_status()
        data = response.json()

        if not data.get("ok"):
            error_code = data.get("error_code")
            description = data.get("description", "Неизвестная ошибка")
            raise RuntimeError(f"Telegram API error {error_code}: {description}")

        return data

    except requests.exceptions.Timeout:
        raise RuntimeError("Таймаут при запросе к Telegram API")
    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"Ошибка сети при отправке в Telegram: {e}")


if __name__ == "__main__":
    post_text = os.environ.get(
        "POST_TEXT",
        "Тестовый пост 🤖 Если видите это — автопубликация работает!"
    )
    try:
        result = publish(post_text)
        print("Успешно отправлено:", result)
    except Exception as e:
        print("Ошибка:", e)
        sys.exit(1)
