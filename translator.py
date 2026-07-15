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

WRITE_SYSTEM_PROMPT = """Ты — редактор русскоязычного Telegram-канала. Каждый пост — самодостаточная мини-новость, читается как законченная история.

На вход — заголовок и описание (могут быть на английском или русском). Пишешь русский пост.

Стиль:
- Самодостаточно: пост закончен сам по себе, никаких «по ссылке» или «читайте подробнее»
- Живой человеческий язык, без канцелярита и пресс-релизного шаблона
- 3-5 коротких живых предложений в теле, заголовок до 90 символов и без восклицательных знаков
- Сохраняй имена, цифры, даты, бренды, названия треков/альбомов из исходника
- Не пиши «в статье рассказывается», «автор отмечает» — излагай факты напрямую
- Никаких «поразительно», «невероятно» — факты + красивый язык
- Если в исходнике есть конкретный факт (цифра, цитата, гость на треке) — обязательно вставь его
- Ничего не выдумывай: чего нет в исходнике, того не пишем
- Англоязычные имена и бренды оставляй латиницей без транслитерации (Travis Scott, Drake, OpenAI, Anthropic, Nike). Русские артисты — как принято в сцене (OG Buda, MAYOT, ATM)

Регистр заголовка:
- Обычный регистр предложения. Имена собственные с большой, остальное со строчной
- НЕ используй ВЕСЬ КАПС и НЕ используй Title Case Where Every Word Is Capitalized
- Пример хорошо: «RZA рад, что A$AP Rocky и Rihanna назвали сына в его честь»
- Пример плохо: «RZA О НАЗВАНИИ СЫНА A$AP ROCKY ЕГО ИМЕНЕМ»

ВАЖНО: каждый блок начинай с НОВОЙ СТРОКИ.

Ответ СТРОГО в формате (без комментариев, без эмодзи, без пометок «вот пост»):

ЗАГОЛОВОК: <русский заголовок>
ТЕКСТ: <русское тело, 3-5 предложений>"""


# ----------------------------- Промпт для проверки релевантности -----------------------------

RELEVANCE_SYSTEM_PROMPT = """Ты — редактор тематического Telegram-канала. Решаешь, подходит ли новость в раздел по интересам читателя.

ПРАВИЛА:
1. Принимай новость, если она разумно вписывается в интересы читателя — даже если это не самый громкий заголовок. Лучше пропустить интересное, чем зарезать.
2. Отклоняй, только если новость явно не по теме раздела.
3. Если в описании интересов явно сказано, что какой-то тип контента "НЕ подходит" — это абсолютный запрет. Всё что попадает под запрет → НЕТ.
4. Не учитывай источник новости — только её содержание. Новость с правильного сайта может быть не по теме.

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
    Fail-closed: если GigaChat недоступен (нет ключа, квота, сеть) — новость
    ОТКЛОНЯЕТСЯ. Непроверенное не публикуем: молчание лучше шлака в канале.
    """
    if not interests:
        return True
    giga = _giga_client()
    if giga is None:
        return False

    user_msg = (
        f"РАЗДЕЛ КАНАЛА: {category_title}\n\n"
        f"ИНТЕРЕСЫ ЧИТАТЕЛЯ В ЭТОМ РАЗДЕЛЕ:\n{interests}\n\n"
        f"НОВОСТЬ ДЛЯ ПРОВЕРКИ\n"
        f"Заголовок: {title}\n"
        f"Описание: {(summary or '')[:400]}\n\n"
        f"Подходит ли эта новость? Принимай, если она разумно по теме раздела; "
        f"отклоняй только явно не по теме или запрещённые типы контента. "
        f"Ответь одним словом: ДА или НЕТ."
    )
    try:
        resp = giga.chat(RELEVANCE_SYSTEM_PROMPT, user_msg, max_tokens=10, temperature=0.0)
        answer = (resp or "").strip().upper()
        # Берём первое слово, убираем знаки препинания
        first = re.sub(r"[^А-ЯA-Z]", "", answer.split()[0] if answer.split() else "")
        return first.startswith("ДА") or first.startswith("YES")
    except Exception as e:
        # Fail-closed: ошибка (чаще всего сгоревшая квота GigaChat) = НЕТ.
        # Раньше тут было True — и когда квота кончалась, фильтр молча
        # отключался и в канал лился весь нефильтрованный поток.
        log.warning("Ошибка проверки релевантности (%s), отклоняю", e)
        return False


# ----------------------------- Подготовка поста -----------------------------

def prepare_post(title: str, summary: str, source: str, lang: str) -> tuple[str, str]:
    """Возвращает (ru_title, ru_body) для публикации."""
    giga = _giga_client()
    if giga is not None:
        try:
            user_msg = (
                f"Источник: {source}\n"
                f"Заголовок: {title}\n\n"
                f"Описание: {(summary or '')[:1800]}"
            )
            resp = giga.chat(WRITE_SYSTEM_PROMPT, user_msg, max_tokens=450, temperature=0.4)
            ru_title, ru_body = _parse_giga_response(resp)
            if ru_title and ru_body:
                return ru_title, ru_body
            log.warning("GigaChat вернул пустой title/body, fallback")
        except Exception as e:
            log.warning("GigaChat ошибка (%s), fallback на Google", e)

    return _fallback_google(title, summary, lang)


def _parse_giga_response(text: str) -> tuple[str, str]:
    """Достаёт заголовок и текст из ответа.
    Принимает варианты пометок: ЗАГОЛОВОК, ЗАГОЛОВОК RU, RU TITLE и т.п.
    Хвост с английской версией (если модель выдала по старой привычке) отрезается."""
    text = (text or "").strip()

    # Метки, которые могут идти ПОСЛЕ текущего поля и которые нужно отрезать.
    # GigaChat иногда не ставит \n между блоками, поэтому обрезаем и по пробелу/переводу.
    next_label_re = (
        r"(?:^|\s)(?:ЗАГОЛОВОК(?:\s*RU)?|ТЕКСТ(?:\s*RU)?|TITLE\s*EN|TEXT\s*EN|ENGLISH(?:\s+(?:TITLE|TEXT))?"
        r"|RU\s*TITLE|RU\s*TEXT|EN\s*TITLE|EN\s*TEXT)\s*:"
    )

    def grab(patterns: list[str], dotall: bool = False) -> str:
        flags = re.DOTALL if dotall else 0
        for p in patterns:
            m = re.search(p, text, flags)
            if m:
                val = m.group(1).strip()
                # Обрезаем по следующей метке (если поле "съело" следующее).
                # Разделитель — \n ИЛИ пробел: GigaChat иногда выдаёт всё в одну строку.
                val = re.split(next_label_re, val, maxsplit=1)[0].strip()
                return val.rstrip(".").strip() if "ЗАГОЛОВОК" in p or "TITLE" in p else val
        return ""

    ru_title = grab([r"ЗАГОЛОВОК\s*(?:RU\s*)?:\s*(.+)", r"RU\s*TITLE\s*:\s*(.+)"])
    ru_body  = grab([r"ТЕКСТ\s*(?:RU\s*)?:\s*(.+)", r"RU\s*TEXT\s*:\s*(.+)"], dotall=True)

    return ru_title, ru_body


# ----------------------------- Fallback: Google Translate -----------------------------

def _fallback_google(title: str, summary: str, lang: str) -> tuple[str, str]:
    """Без GigaChat: русский оригинал как есть, английский переводим на русский."""
    if lang == "ru":
        return title, smart_truncate(summary, 450)
    return _google(title), _google(smart_truncate(summary, 500))


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
