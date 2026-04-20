# News Digest Bot

Телеграм-бот, публикующий в канал свежие новости раз в день по темам:
- 🤖 Нейросети и ИИ
- 🎵 Музыка
- 🎨 Дизайн и искусство
- 💰 Экономика, финансы, крипта

Новости собираются с русских и зарубежных RSS. Англоязычные переводятся на русский через бесплатный Google Translate (без ключей и регистраций). Хостинг — GitHub Actions (бесплатно).

## Что нужно один раз

### 1. Telegram: бот + канал
- ✅ Бот создан у @BotFather (`@MammyNewsBot`)
- ✅ Канал создан (`@mammynews`)
- ✅ Бот добавлен в канал администратором с правом публикации

### 2. GitHub: репозиторий

1. Создать репозиторий на github.com (приватный можно).
2. Залить содержимое папки `news-bot/`:
   ```bash
   cd news-bot
   git init
   git add .
   git commit -m "init"
   git branch -M main
   git remote add origin https://github.com/<логин>/news-bot.git
   git push -u origin main
   ```

### 3. GitHub: секреты

В репо: **Settings → Secrets and variables → Actions → New repository secret**

| Name | Value |
|---|---|
| `TELEGRAM_BOT_TOKEN` | токен от @BotFather |
| `TELEGRAM_CHAT_ID` | `@mammynews` |

### 4. Запуск
**Actions → Daily news digest → Run workflow**. Через 1-2 минуты посты прилетят в канал. Дальше — автоматически раз в сутки в 09:00 МСК.

## Настройка

- **Время публикации** — `cron` в `.github/workflows/daily.yml` (время в UTC, Москва = UTC+3)
- **Источники** — `sources.py`, поле `feeds` у каждой категории
- **Кол-во постов в день на категорию** — `POSTS_PER_CATEGORY` в `sources.py` (сейчас 3 → 12 постов/день суммарно)
- **Окно свежести** — `FRESHNESS_HOURS` (сейчас 30 часов — чтобы ничего не пропустить между запусками)

## Апгрейд качества (опционально, потом)

Сейчас англоязычные новости переводятся "в лоб" (Google Translate) — качество хорошее, но без пересказа редактора. Если захочется умных саммари на русском, можно подключить **GigaChat** от Сбера (бесплатный тариф, принимает РФ-карты):

1. Регистрация на https://developers.sber.ru/gigachat/
2. Получить credentials → добавить секрет `GIGACHAT_CREDENTIALS` в GitHub
3. Написать небольшой адаптер в `translator.py` (можно попросить меня)

## Стоимость

- GitHub Actions: **0 ₽** (в пределах бесплатного лимита 2000 мин/мес, нам надо ~30 мин/мес)
- Перевод: **0 ₽** (Google Translate free)
- Telegram: **0 ₽**
