"""
Бесплатный перевод на русский через Google Translate (библиотека deep-translator).
Никаких ключей и регистраций.
"""
import logging
import re
from deep_translator import GoogleTranslator

log = logging.getLogger("translator")

MAX_CHUNK = 4800  # лимит Google Translate ~5000 символов


def translate_to_russian(text: str, source_lang: str = "auto") -> str:
    text = (text or "").strip()
    if not text:
        return ""
    try:
        # Google translate имеет лимит по длине — режем на куски по предложениям
        chunks = _split_into_chunks(text, MAX_CHUNK)
        translator = GoogleTranslator(source=source_lang, target="ru")
        translated = [translator.translate(c) or c for c in chunks]
        return " ".join(translated).strip()
    except Exception as e:
        log.warning("Не удалось перевести (%s...): %s", text[:60], e)
        return text  # fallback: оригинал лучше, чем пусто


def _split_into_chunks(text: str, max_len: int) -> list[str]:
    if len(text) <= max_len:
        return [text]
    sentences = re.split(r"(?<=[.!?])\s+", text)
    chunks, buf = [], ""
    for s in sentences:
        if len(buf) + len(s) + 1 > max_len:
            if buf:
                chunks.append(buf)
            buf = s
        else:
            buf = f"{buf} {s}".strip()
    if buf:
        chunks.append(buf)
    return chunks


def smart_truncate(text: str, max_chars: int = 400) -> str:
    """Обрезать до max_chars, по возможности на границе предложения."""
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
