"""
GigaChat-редактор: проверка релевантности новости и пересказ на русском.
Fallback на Google Translate если GigaChat недоступен.
"""
import re
import logging

from deep_translator import GoogleTranslator

from gigachat_client import get_client_from_env

log = logging.getLogger("translator")


# ----------------------------- Промпт для написания поста -----------------------------

WRITE_SYSTEM_PROMPT = """Ты — редактор живого русскоязычного Telegram-канала. Пишешь красиво и по-человечески, без канцелярита и пресс-релизного стиля.

На вход получаешь заголовок и описание новости (может быть на английском). Превращай в пост для Telegram на русском так, чтобы было интересно читать.

Структура:
- Заголовок: одна строка, до 90 символов. Цепкий, по-человечески, без эмодзи и без восклицательного знака в конце.
- Тело: 2-4 живых предложения. Простой современный русский язык, как пишет умный знакомый, а не пресс-секретарь.

Стиль:
- Сохраняй все имена, цифры, бренды, названия продуктов из исходника
- Не пиши "в статье рассказывается", "автор отмечает", "по словам", "сообщается" — излагай факты прямо
- Англоязычные имена и бренды оставляй как есть, без транслитерации (Drake, OpenAI, Apple, Nike)
- Никаких "поразительно", "невероятно", "сенсационно" — просто факты, но красивым языком
- Если в новости есть яркий конкретный факт (цифра, цитата, деталь) — поставь его в тело
- Не придумывай ничего, чего нет в исходнике

Ответ СТРОГО в формате (без лишних комментариев и без эмодзи):

ЗАГОЛОВОК: <русский заголовок>
ТЕКСТ: <2-4 предложения>"""


# ----------------------------- Промпт для проверки релевантности -----------------------------

RELEVANCE_SYSTEM_PROMPT = """Ты — очень строгий редактор тематического Telegram-канала. Решаешь, подходит ли новость в раздел по интересам читателя.

ПРАВИЛА:
1. По умолчанию — отклоняй. Принимай ТОЛЬКО если новость прямо и бесспорно соответствует интересам.
2. Если новость на грани, "вроде по теме но не совсем" — отклоняй.
3. Если в описании интересов явно сказано что какой-то тип контента "НЕ подходит" — это абсолютный запрет. Всё что попадает под запрет → НЕТ.
4. Не учитывай источник новости — только её содержание. Новость с правильного сайта может быть не по теме.
5. Думай так: "Открыл бы читатель эту конкретную статью, если бы она пришла отдельно?" Если нет — отклоняй.

Ответ — РОВНО одно слово: ДА или НЕТ. Без пояснений, без точек, без эмодзи."""


_giga = None
_giga_tried = False


def _giga_client():
    global _giga, _giga_tried
    if not _giga_tried:
        _giga_tried = True
        _giga = get_client_from_env()
        if _giga:
            log.info("GigaChat включён")
        else:
            log.info("GIGACHAT_CREDENTIALS не задан, используется Google Translate без фильтра")
    return _giga


# ----------------------------- Релевантность -----------------------------

def is_relevant(title: str, summary: str, category_title: str, interests: str) -> bool:
    """
    Решает, подходит ли новость в категорию.
    Если GigaChat недоступен — пропускаем фильтр (возвращаем True).
    """
    giga = _giga_client()
    if giga is None or not interests:
        return True

    user_msg = (
        f"РАЗДЕЛ КАНАЛА: {category_title}\n\n"
        f"ИНТЕРЕСЫ ЧИТАТЕЛЯ В ЭТОМ РАЗДЕЛЕ:\n{interests}\n\n"
        f"НОВОСТЬ ДЛЯ ПРОВЕРКИ\n"
        f"Заголовок: {title}\n"
        f"Описание: {(summary or '')[:400]}\n\n"
        f"Подходит ли эта новость? Помни: по умолчанию НЕТ, на грани НЕТ, "
        f"запрещённые типы контента НЕТ. Ответь одним словом: ДА или НЕТ."
    )
    try:
        resp = giga.chat(RELEVANCE_SYSTEM_PROMPT, user_msg, max_tokens=10, temperature=0.0)
        answer = (resp or "").strip().upper()
        # Берём первое слово, убираем знаки препинания
        first = re.sub(r"[^А-ЯA-Z]", "", answer.split()[0] if answer.split() else "")
        return first.startswith("ДА") or first.startswith("YES")
    except Exception as e:
        log.warning("Ошибка проверки релевантности (%s), пропускаю фильтр", e)
        return True


# ----------------------------- Подготовка поста -----------------------------

def prepare_post(title: str, summary: str, source: str, lang: str) -> tuple[str, str]:
    """Возвращает (заголовок_на_рус, тело_на_рус) для публикации."""
    giga = _giga_client()
    if giga is not None:
        try:
            user_msg = (
                f"Источник: {source}\n"
                f"Заголовок: {title}\n\n"
                f"Описание: {(summary or '')[:1800]}"
            )
            resp = giga.chat(WRITE_SYSTEM_PROMPT, user_msg, max_tokens=500, temperature=0.4)
            ru_title, ru_body = _parse_giga_response(resp)
            if ru_title and ru_body:
                return ru_title, ru_body
            log.warning("GigaChat вернул пустой title/body, fallback")
        except Exception as e:
            log.warning("GigaChat ошибка (%s), fallback на Google", e)

    return _fallback_google(title, summary, lang)


def _parse_giga_response(text: str) -> tuple[str, str]:
    text = (text or "").strip()
    title = ""
    body = ""
    m_title = re.search(r"ЗАГОЛОВОК\s*:\s*(.+)", text)
    if m_title:
        title = m_title.group(1).strip().rstrip(".").strip()
    m_body = re.search(r"ТЕКСТ\s*:\s*(.+)", text, re.DOTALL)
    if m_body:
        body = m_body.group(1).strip()
    return title, body


# ----------------------------- Fallback: Google Translate -----------------------------

def _fallback_google(title: str, summary: str, lang: str) -> tuple[str, str]:
    if lang == "ru":
        return title, smart_truncate(summary, 450)
    ru_title = _google(title)
    body = smart_truncate(summary, 500)
    ru_body = _google(body)
    return ru_title, ru_body


def _google(text: str) -> str:
    text = (text or "").strip()
    if not text:
        return ""
    try:
        return GoogleTranslator(source="auto", target="ru").translate(text[:4800]) or text
    except Exception as e:
        log.warning("Google translate failed: %s", e)
        return text


def smart_truncate(text: str, max_chars: int = 400) -> str:
    text = (text or "").strip()
    if len(text) <= max_chars:
        return text
    cut = text[:max_chars]
    for sep in (". ", "! ", "? ", "… ", "; "):
        idx = cut.rfind(sep)
        if idx > max_chars * 0.5:
            return cut[: idx + 1].strip()
    idx = cut.rfind(" ")
    if idx > max_chars * 0.3:
        return cut[:idx].strip() + "…"
    return cut.strip() + "…"


def translate_to_russian(text: str, source_lang: str = "auto") -> str:
    """Совместимость со старым кодом."""
    return _google(text)
