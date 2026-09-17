# telegram-autopost

Автопостинг развивающих игр, заданий, советов и историй в Telegram-канал.

## Как это работает

- `generator.py` — собирает текст поста из шаблонов (категории: `game`, `task`, `tip`, `story`) и подбирает картинку.
- `images.py` — тематические картинки под каждую категорию.
- `publish.py` — отправка в Telegram через Bot API (`sendPhoto`, если есть картинка, иначе `sendMessage`).
- `autopost.py` — точка входа: генерирует пост и публикует его.

## Подготовка

1. Создайте бота у [@BotFather](https://t.me/BotFather) и получите токен.
2. Добавьте бота администратором в канал с правом публикации сообщений.
3. Узнайте ID канала: для публичного — `@my_channel`, для приватного — числовой `-100...`.

## Локальный запуск

```bash
pip install -r requirements.txt

export TELEGRAM_BOT_TOKEN="123456:ABC..."
export TELEGRAM_CHANNEL_ID="@my_channel"

python autopost.py
```

Проверить генерацию без отправки в Telegram:

```bash
python generator.py
```

Отправить произвольный текст:

```bash
POST_TEXT="Привет из бота" python publish.py
```

## Переменные окружения

| Переменная | Обязательна | Описание |
| --- | --- | --- |
| `TELEGRAM_BOT_TOKEN` | да | Токен бота от BotFather |
| `TELEGRAM_CHANNEL_ID` | да | `@username` канала или числовой ID |
| `POST_TEXT` | нет | Текст для ручного запуска `publish.py` |

## Запуск по расписанию (GitHub Actions)

Воркфлоу `.github/workflows/autopost.yml` запускается ежедневно в 09:00 UTC и вручную через **Actions → Telegram Autopost → Run workflow**.

Перед первым запуском добавьте секреты в **Settings → Secrets and variables → Actions**:

- `TELEGRAM_BOT_TOKEN`
- `TELEGRAM_CHANNEL_ID`

## Запуск по cron на сервере

```cron
0 9 * * * cd /path/to/telegram-autopost && /usr/bin/env TELEGRAM_BOT_TOKEN=... TELEGRAM_CHANNEL_ID=... python3 autopost.py >> autopost.log 2>&1
```
