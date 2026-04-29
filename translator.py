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

WRITE_SYSTEM_PROMPT = """Ты — редактор Telegram-канала, который выпускает посты сразу на двух языках: русском и английском. Каждый пост — самодостаточная мини-новость, читается как законченная история.

На вход — заголовок и описание (могут быть на английском или русском). Делаешь ДВЕ версии: русскую и английскую. Обе версии описывают одно и то же, в одинаковом стиле и объёме, чтобы читатель мог тренировать английский, сравнивая текст.

Стиль обеих версий:
- Самодостаточно: пост закончен сам по себе, никаких «по ссылке» или «читайте подробнее»
- Живой человеческий язык, без канцелярита и пресс-релизного шаблона
- 3-5 коротких живых предложений в теле, заголовок до 90 символов и без восклицательных знаков
- Сохраняй имена, цифры, даты, бренды, названия треков/альбомов из исходника
- Не пиши «в статье рассказывается», «автор отмечает» / «the article states», «according to» — излагай факты напрямую
- Никаких «поразительно», «amazingly», «incredibly» — факты + красивый язык
- Если в исходнике есть конкретный факт (цифра, цитата, гость на треке) — обязательно вставь его в обе версии
- Ничего не выдумывай: чего нет в исходнике, того не пишем
- Англоязычные имена и бренды в РУССКОЙ версии оставляй латиницей без транслитерации (Travis Scott, Drake, OpenAI, Anthropic, Nike). Русские артисты — как принято в сцене (OG Buda, MAYOT, ATM)

Английская версия:
- Естественный современный английский (American English)
- Та же длина и структура что и русская (3-5 предложений)
- Такой же информативный, не более и не менее

Регистр заголовков:
- Обычный регистр предложения. Имена собственные с большой, остальное со строчной
- НЕ используй ВЕСЬ КАПС и НЕ используй Title Case Where Every Word Is Capitalized
- Пример хорошо: «RZA рад, что A$AP Rocky и Rihanna назвали сына в его честь»
- Пример плохо: «RZA О НАЗВАНИИ СЫНА A$AP ROCKY ЕГО ИМЕНЕМ»

ВАЖНО: каждый из четырёх блоков начинай с НОВОЙ СТРОКИ. Между блоками — перевод строки.

Ответ СТРОГО в формате (без комментариев, без эмодзи, без пометок «вот пост»):

ЗАГОЛОВОК RU: <русский заголовок>
ТЕКСТ RU: <русское тело, 3-5 предложений>
TITLE EN: <english headline in sentence case>
TEXT EN: <english body, 3-5 sentences>"""


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

def prepare_post(title: str, summary: str, source: str, lang: str) -> tuple[str, str, str, str]:
    """Возвращает (ru_title, ru_body, en_title, en_body) для публикации.
    Двуязычный пост: русская версия + английская той же стилистики."""
    giga = _giga_client()
    if giga is not None:
        try:
            user_msg = (
                f"Источник: {source}\n"
                f"Заголовок: {title}\n\n"
                f"Описание: {(summary or '')[:1800]}"
            )
            # max_tokens увеличен — теперь генерим обе версии разом
            resp = giga.chat(WRITE_SYSTEM_PROMPT, user_msg, max_tokens=900, temperature=0.4)
            ru_title, ru_body, en_title, en_body = _parse_giga_response(resp)
            if ru_title and ru_body:
                # Если EN не получили — fallback переводим RU → EN через Google
                if not en_title:
                    en_title = _google_en(ru_title)
                if not en_body:
                    en_body = _google_en(ru_body)
                return ru_title, ru_body, en_title, en_body
            log.warning("GigaChat вернул пустой RU title/body, fallback")
        except Exception as e:
            log.warning("GigaChat ошибка (%s), fallback на Google", e)

    return _fallback_google(title, summary, lang)


def _parse_giga_response(text: str) -> tuple[str, str, str, str]:
    """Достаёт 4 поля из ответа: RU заголовок/текст и EN title/body.
    Принимает варианты пометок: ЗАГОЛОВОК RU, RU TITLE, TITLE EN и т.п."""
    text = (text or "").strip()

    # Метки, которые могут идти ПОСЛЕ текущего поля и которые нужно отрезать.
    # GigaChat иногда не ставит \n между блоками, поэтому обрезаем и по пробелу/переводу.
    next_label_re = (
        r"(?:^|\s)(?:ЗАГОЛОВОК\s*RU|ТЕКСТ\s*RU|TITLE\s*EN|TEXT\s*EN|ENGLISH(?:\s+(?:TITLE|TEXT))?"
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

    ru_title = grab([r"ЗАГОЛОВОК\s*RU\s*:\s*(.+)", r"RU\s*TITLE\s*:\s*(.+)", r"ЗАГОЛОВОК\s*:\s*(.+)"])
    ru_body  = grab([r"ТЕКСТ\s*RU\s*:\s*(.+)", r"RU\s*TEXT\s*:\s*(.+)", r"ТЕКСТ\s*:\s*(.+)"], dotall=True)
    en_title = grab([r"TITLE\s*EN\s*:\s*(.+)", r"EN\s*TITLE\s*:\s*(.+)", r"ENGLISH\s*TITLE\s*:\s*(.+)"])
    en_body  = grab([r"TEXT\s*EN\s*:\s*(.+)", r"EN\s*TEXT\s*:\s*(.+)", r"ENGLISH\s*TEXT\s*:\s*(.+)"], dotall=True)

    return ru_title, ru_body, en_title, en_body


# ----------------------------- Fallback: Google Translate -----------------------------

def _fallback_google(title: str, summary: str, lang: str) -> tuple[str, str, str, str]:
    """Без GigaChat: переводим оригинал на русский + сохраняем оригинал/EN."""
    if lang == "ru":
        ru_title = title
        ru_body = smart_truncate(summary, 450)
        en_title = _google_en(title)
        en_body = _google_en(ru_body)
    else:
        # Источник на английском — берём как EN, переводим в RU
        en_title = title
        en_body = smart_truncate(summary, 500)
        ru_title = _google(title)
        ru_body = _google(en_body)
    return ru_title, ru_body, en_title, en_body


def _google(text: str) -> str:
    text = (text or "").strip()
    if not text:
        return ""
    try:
        return GoogleTranslator(source="auto", target="ru").translate(text[:4800]) or text
    except Exception as e:
        log.warning("Google translate failed: %s", e)
        return text


def _google_en(text: str) -> str:
    text = (text or "").strip()
    if not text:
        return ""
    try:
        return GoogleTranslator(source="auto", target="en").translate(text[:4800]) or text
    except Exception as e:
        log.warning("Google translate (EN) failed: %s", e)
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
