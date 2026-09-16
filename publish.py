import os
import requests

TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
CHAT_ID = os.environ["TELEGRAM_CHANNEL_ID"]

def publish(text: str, image_url: str | None = None):
    if image_url:
        return requests.post(
            f"https://api.telegram.org/bot{TOKEN}/sendPhoto",
            data={"chat_id": CHAT_ID, "caption": text, "photo": image_url},
        ).json()
    return requests.post(
        f"https://api.telegram.org/bot{TOKEN}/sendMessage",
        data={"chat_id": CHAT_ID, "text": text, "parse_mode": "HTML"},
    ).json()

if __name__ == "__main__":
    post_text = os.environ.get(
        "POST_TEXT",
        "Тестовый пост от Mira 🤖 Если видите это — автопубликация работает!"
    )
    result = publish(post_text)
    print("Telegram response:", result)
