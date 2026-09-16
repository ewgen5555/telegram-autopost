import os
from generator import generate_post
from publish import publish

if __name__ == "__main__":
    text = generate_post()
    print("Generated post:", text)

    result = publish(text)
    print("Telegram response:", result)
