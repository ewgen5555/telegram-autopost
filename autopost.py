from generator import generate_post
from publish import publish

if __name__ == "__main__":
    post = generate_post()      # генератор вернул текст и картинку

    text = post["text"]         # текст поста
    image = post["image"]       # картинка или None

    print("Generated text:", text)
    print("Generated image:", image)

    result = publish(text, image)
    print("Telegram response:", result)

