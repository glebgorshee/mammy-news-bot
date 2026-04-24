"""
Перевод и пересказ новости на русский.

Основной путь: GigaChat (Сбер) — делает умный пересказ на русском.
Fallback (если GigaChat недоступен): Google Translate (deep-translator).
"""
import re
import logging

from deep_translator import GoogleTranslator

from gigachat_client import get_client_from_env

log = logging.getLogger("translator")

SYSTEM_PROMPT = """Ты — редактор русскоязычного Telegram-канала о технологиях, культуре, музыке, стритвире и экономике.

На вход получаешь заголовок и описание новости (может быть на английском). Напиши пост для Telegram на русском языке:

- Заголовок: короткий (до 90 символов), без эмодзи, без кликбейта, без восклицательных знаков в конце. Смысл оригинального заголовка.
- Тело: 2-4 живых предложения с главным. Сохрани все имена, цифры, названия из исходника. Пиши простым языком как человек, а не как переводчик.
- Не пиши "в статье рассказывается", "автор отмечает", "по мнению" — излагай факты прямо.
- Не добавляй ничего, чего нет в исходнике. Не фантазируй.
- Если исходник на русском — просто причеши стиль, ничего не придумывай.

Ответ СТРОГО в таком формате (два раздела, без лишних комментариев):

ЗАГОЛОВОК: <русский заголовок>
ТЕКСТ: <2-4 предложения>"""


_giga = None
_giga_tried = False


def _giga_client():
    """Ленивая инициализация. None если ключа нет."""
    global _giga, _giga_tried
    if not _giga_tried:
        _giga_tried = True
        _giga = get_client_from_env()
        if _giga:
            log.info("GigaChat включён")
        else:
            log.info("GIGACHAT_CREDENTIALS не задан, используется Google Translate")
    return _giga


def prepare_post(title: str, summary: str, source: str, lang: str) -> tuple[str, str]:
    """Возвращает (заголовок_на_рус, тело_на_рус)."""
    giga = _giga_client()
    if giga is not None:
        try:
            user_msg = (
                f"Источник: {source}\n"
                f"Заголовок: {title}\n\n"
                f"Описание: {(summary or '')[:1800]}"
            )
            resp = giga.chat(SYSTEM_PROMPT, user_msg, max_tokens=450)
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


# ------- Fallback: Google Translate + умная обрезка -------

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


# Для совместимости со старым кодом (если где-то вызывается напрямую)
def translate_to_russian(text: str, source_lang: str = "auto") -> str:
    return _google(text)
