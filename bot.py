"""
Парсит RSS, переводит (если нужно), публикует в Telegram-канал.
Запускается из GitHub Actions по cron.
"""
import os
import sys
import time
import html
import re
import logging
from datetime import datetime, timezone, timedelta
from dataclasses import dataclass
from urllib.parse import urljoin

import feedparser
import requests

from sources import SOURCES, POSTS_PER_CATEGORY, FRESHNESS_HOURS, HARD_REJECT_PATTERNS
from state import load_posted_urls, save_posted_urls
from translator import prepare_post, is_relevant

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("bot")


@dataclass
class NewsItem:
    title: str
    summary: str
    link: str
    source: str
    lang: str
    published: datetime
    image: str | None = None


def parse_source(source: dict) -> list[NewsItem]:
    """Диспетчер: RSS-фид или публичный Telegram-канал (t.me/s/...)."""
    if source.get("type") == "telegram":
        return parse_telegram_channel(source)
    return parse_feed(source)


def parse_telegram_channel(source: dict) -> list[NewsItem]:
    """Парсит публичную web-версию Telegram-канала: https://t.me/s/<channel>."""
    channel = source["url"].strip().lstrip("@")
    url = f"https://t.me/s/{channel}"
    try:
        r = requests.get(
            url,
            headers={
                "User-Agent": _BROWSER_UA,
                "Accept": "text/html,application/xhtml+xml,*/*;q=0.9",
            },
            timeout=15,
        )
        if r.status_code != 200:
            log.warning("Telegram %s status %s", url, r.status_code)
            return []
    except Exception as e:
        log.warning("Telegram %s: %s", url, e)
        return []

    html_text = r.text
    # Разбиваем на отдельные сообщения по якорю tgme_widget_message_wrap
    chunks = re.split(r'<div class="tgme_widget_message_wrap', html_text)[1:]
    items: list[NewsItem] = []

    for chunk in chunks[-20:]:  # последние 20 постов
        # Permalink: data-post="channel/id"
        m_post = re.search(r'data-post="([^"]+)"', chunk)
        if not m_post:
            continue
        post_id = m_post.group(1)
        link = f"https://t.me/{post_id}"

        # Дата публикации
        m_dt = re.search(r'<time[^>]*datetime="([^"]+)"', chunk)
        if not m_dt:
            continue
        try:
            published = datetime.fromisoformat(m_dt.group(1).replace("Z", "+00:00"))
            if published.tzinfo is None:
                published = published.replace(tzinfo=timezone.utc)
        except Exception:
            continue

        # Текст сообщения
        m_text = re.search(
            r'<div class="tgme_widget_message_text[^"]*"[^>]*>(.+?)</div>\s*(?:<div class="tgme_widget_message_(?:reply_markup|footer))',
            chunk,
            re.DOTALL,
        )
        if not m_text:
            m_text = re.search(
                r'<div class="tgme_widget_message_text[^"]*"[^>]*>(.+?)</div>',
                chunk,
                re.DOTALL,
            )
        if not m_text:
            continue
        # Превратим <br> в \n чтобы не клеились абзацы
        raw_text = re.sub(r"<br\s*/?>", "\n", m_text.group(1))
        text = _strip_html(raw_text).strip()
        # Удалить хвост из реакций вида "❤ 27 🤮 4 🔥 3"
        text = re.sub(r"(\s*\S+\s+\d+){2,}\s*$", "", text).strip()
        if len(text) < 20:  # совсем короткие посты пропускаем (часто реклама/мем)
            continue

        # Заголовок = первая строка/предложение, тело = остальное
        first_line = text.split("\n", 1)[0]
        if len(first_line) > 200:
            # Если первая строка слишком длинная — режем по точке
            m_dot = re.search(r"^(.{20,180}?[.!?])\s", first_line + " ")
            if m_dot:
                first_line = m_dot.group(1)
            else:
                first_line = first_line[:180]
        title = first_line.strip()
        summary = text[len(first_line):].strip() or text

        # Картинка из background-image:url('...')
        m_img = re.search(r"background-image:\s*url\(['\"]?([^'\")]+)['\"]?\)", chunk)
        image = m_img.group(1) if m_img else None

        items.append(NewsItem(
            title=title,
            summary=summary,
            link=link,
            source=source["name"],
            lang=source.get("lang", "ru"),
            published=published,
            image=image,
        ))
    return items


def parse_feed(source: dict) -> list[NewsItem]:
    try:
        feed = feedparser.parse(
            source["url"],
            request_headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
                "Accept": "application/rss+xml, application/atom+xml, application/xml;q=0.9, */*;q=0.8",
                "Accept-Encoding": "gzip, deflate",
            },
        )
    except Exception as e:
        log.warning("Ошибка парсинга %s: %s", source["url"], e)
        return []

    items: list[NewsItem] = []
    for entry in feed.entries[:15]:
        link = entry.get("link")
        title = (entry.get("title") or "").strip()
        if not link or not title:
            continue
        summary_raw = entry.get("summary") or entry.get("description") or ""
        summary = _strip_html(summary_raw)
        items.append(NewsItem(
            title=title,
            summary=summary,
            link=link,
            source=source["name"],
            lang=source["lang"],
            published=_parse_date(entry),
            image=_extract_image_from_entry(entry),
        ))
    return items


def _extract_image_from_entry(entry) -> str | None:
    """Ищем изображение в полях RSS-записи (без обращения к сети)."""
    # 1. media_content
    for m in (entry.get("media_content") or []):
        url = (m or {}).get("url")
        if url:
            return url
    # 2. media_thumbnail
    for m in (entry.get("media_thumbnail") or []):
        url = (m or {}).get("url")
        if url:
            return url
    # 3. enclosures
    for enc in (entry.get("enclosures") or []):
        if (enc.get("type") or "").startswith("image/"):
            url = enc.get("href") or enc.get("url")
            if url:
                return url
    # 4. links с rel=enclosure
    for ln in (entry.get("links") or []):
        if ln.get("rel") == "enclosure" and (ln.get("type") or "").startswith("image/"):
            if ln.get("href"):
                return ln["href"]
    # 5. <img> в summary/content HTML
    raw = entry.get("summary") or entry.get("description") or ""
    content_list = entry.get("content") or []
    if content_list and isinstance(content_list, list):
        raw += " " + (content_list[0].get("value") or "")
    m = re.search(r'<img[^>]+src=["\']([^"\']+)["\']', raw)
    if m:
        return m.group(1)
    return None


_BROWSER_UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36"


def _fetch_og_image(article_url: str) -> str | None:
    """Fallback: скачиваем HTML статьи и парсим og:image. Возвращает абсолютный URL."""
    try:
        r = requests.get(
            article_url,
            headers={"User-Agent": _BROWSER_UA, "Accept": "text/html,*/*"},
            timeout=10,
            allow_redirects=True,
        )
        if r.status_code != 200:
            return None
        html_text = r.text[:400_000]
        patterns = [
            r'<meta\s+property=["\']og:image(?::secure_url|:url)?["\']\s+content=["\']([^"\']+)["\']',
            r'<meta\s+content=["\']([^"\']+)["\']\s+property=["\']og:image(?::secure_url|:url)?["\']',
            r'<meta\s+name=["\']twitter:image(?::src)?["\']\s+content=["\']([^"\']+)["\']',
            r'<meta\s+content=["\']([^"\']+)["\']\s+name=["\']twitter:image(?::src)?["\']',
            r'<link\s+rel=["\']image_src["\']\s+href=["\']([^"\']+)["\']',
        ]
        for p in patterns:
            m = re.search(p, html_text, re.IGNORECASE)
            if m:
                return urljoin(article_url, html.unescape(m.group(1)))
    except Exception as e:
        log.debug("og:image fetch failed for %s: %s", article_url, e)
    return None


MAX_IMAGE_BYTES = 5 * 1024 * 1024  # 5 MB
IMAGE_CONTENT_TYPES = ("image/jpeg", "image/jpg", "image/png", "image/webp", "image/gif")


def download_image(url: str) -> tuple[bytes, str] | None:
    """Скачиваем картинку, возвращаем (bytes, content_type) или None."""
    if not url:
        return None
    try:
        r = requests.get(
            url,
            headers={"User-Agent": _BROWSER_UA, "Accept": "image/*,*/*;q=0.8", "Referer": url},
            timeout=15,
            stream=True,
            allow_redirects=True,
        )
        if r.status_code != 200:
            return None
        ctype = (r.headers.get("content-type") or "").split(";")[0].strip().lower()
        if ctype not in IMAGE_CONTENT_TYPES:
            # Иногда сервер не ставит content-type, но URL явно ведёт на image
            if not any(url.lower().split("?")[0].endswith(ext) for ext in (".jpg", ".jpeg", ".png", ".webp", ".gif")):
                return None
            ctype = "image/jpeg"
        # Читаем с лимитом
        content = r.raw.read(MAX_IMAGE_BYTES + 1, decode_content=True)
        if len(content) == 0 or len(content) > MAX_IMAGE_BYTES:
            return None
        return content, ctype
    except Exception as e:
        log.debug("Не удалось скачать картинку %s: %s", url, e)
        return None


def _parse_date(entry) -> datetime:
    for key in ("published_parsed", "updated_parsed"):
        t = entry.get(key)
        if t:
            return datetime(*t[:6], tzinfo=timezone.utc)
    return datetime.now(timezone.utc)


def _strip_html(text: str) -> str:
    text = re.sub(r"<[^>]+>", " ", text)
    text = html.unescape(text)
    return re.sub(r"\s+", " ", text).strip()


_COMPILED_HARD_REJECT: dict[str, list[re.Pattern]] = {
    key: [re.compile(p, re.IGNORECASE) for p in patterns]
    for key, patterns in HARD_REJECT_PATTERNS.items()
}


def is_hard_rejected(item: NewsItem, category_key: str) -> str | None:
    """Жёсткий regex-фильтр до LLM. Возвращает совпавший паттерн или None.
    Проверяет и текст (заголовок + описание), и URL — некоторые издания (Billboard)
    зашивают жанр прямо в путь ссылки, что ловится точнее, чем по словам."""
    patterns = _COMPILED_HARD_REJECT.get(category_key)
    if not patterns:
        return None
    text = f"{item.title}\n{item.summary or ''}\n{item.link or ''}"
    for p in patterns:
        if p.search(text):
            return p.pattern
    return None


def collect_candidates(category_key: str) -> list[NewsItem]:
    cutoff = datetime.now(timezone.utc) - timedelta(hours=FRESHNESS_HOURS)
    candidates: list[NewsItem] = []
    for source in SOURCES[category_key]["feeds"]:
        items = parse_source(source)
        fresh = [i for i in items if i.published >= cutoff]
        log.info("  %s: %d всего, %d свежих", source["name"], len(items), len(fresh))
        candidates.extend(fresh)
    candidates.sort(key=lambda x: x.published, reverse=True)
    return candidates


def prepare_ru_post(item: NewsItem) -> tuple[str, str]:
    """Вернуть (заголовок_на_рус, тело_на_рус) — делегируется в translator.prepare_post."""
    return prepare_post(item.title, item.summary, item.source, item.lang)


def format_post(category: dict, item: NewsItem, ru_title: str, ru_body: str) -> str:
    """Самодостаточный пост: заголовок + тело + хэштег. Без ссылок и атрибуции —
    читатель должен узнавать всё прямо из текста, без перехода куда-либо."""
    emoji = category["emoji"]
    hashtag = category.get("hashtag", "")
    parts = [
        f"{emoji} <b>{html.escape(ru_title)}</b>",
    ]
    if ru_body:
        parts += ["", html.escape(ru_body)]
    if hashtag:
        parts += ["", hashtag]
    return "\n".join(parts)


def send_to_telegram(token: str, chat_id: str, text: str, image_url: str | None = None) -> bool:
    # Сначала пробуем отправить фото: скачиваем сами и загружаем как файл (надёжнее, чем давать URL)
    if image_url:
        dl = download_image(image_url)
        if dl is not None:
            img_bytes, ctype = dl
            ext = {"image/png": "png", "image/webp": "webp", "image/gif": "gif"}.get(ctype, "jpg")
            try:
                files = {"photo": (f"image.{ext}", img_bytes, ctype)}
                data = {"chat_id": chat_id, "caption": text[:1020], "parse_mode": "HTML"}
                r = requests.post(
                    f"https://api.telegram.org/bot{token}/sendPhoto",
                    data=data, files=files, timeout=60,
                )
                if r.status_code == 200:
                    return True
                log.warning("sendPhoto (multipart) %s: %s — fallback на текст", r.status_code, r.text[:200])
            except Exception as e:
                log.warning("sendPhoto ошибка: %s — fallback на текст", e)
        else:
            log.info("Картинку скачать не удалось, публикую как текст: %s", image_url[:80])

    # Fallback: текстовое сообщение с link preview (Telegram сам покажет превью если сможет)
    payload = {
        "chat_id": chat_id,
        "text": text[:4000],
        "parse_mode": "HTML",
        "disable_web_page_preview": False,
    }
    try:
        r = requests.post(f"https://api.telegram.org/bot{token}/sendMessage", json=payload, timeout=30)
        if r.status_code == 200:
            return True
        log.error("Telegram API %s: %s", r.status_code, r.text)
    except Exception as e:
        log.error("Ошибка отправки в Telegram: %s", e)
    return False


def main() -> int:
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")
    if not token or not chat_id:
        log.error("Нужны переменные TELEGRAM_BOT_TOKEN и TELEGRAM_CHAT_ID")
        return 1

    posted_urls = load_posted_urls()
    log.info("В памяти %d ранее опубликованных ссылок", len(posted_urls))

    new_urls: set[str] = set()
    total_posted = 0

    for key, category in SOURCES.items():
        log.info("=== %s ===", category["title"])
        candidates = collect_candidates(key)
        candidates = [c for c in candidates if c.link not in posted_urls]
        log.info("Кандидатов после фильтра по памяти: %d", len(candidates))

        # Жёсткий regex-блэклист срабатывает ДО обращения к LLM.
        # Это страховка от очевидного мусора (политика в музыке, K-pop, спорт и т.п.),
        # который GigaChat иногда пропускает.
        before_hard = len(candidates)
        kept: list[NewsItem] = []
        for c in candidates:
            hit = is_hard_rejected(c, key)
            if hit:
                log.info("  — жёсткий блэклист (%s): %s", hit, c.title[:90])
            else:
                kept.append(c)
        candidates = kept
        if before_hard != len(candidates):
            log.info("После hard-фильтра: %d (было %d)", len(candidates), before_hard)

        # Фильтр релевантности: проходим по самым свежим, GigaChat решает по теме или нет.
        # Ограничиваем число AI-проверок, чтобы не упереться в квоту.
        interests = category.get("interests") or ""
        max_relevance_checks = 20
        relevant: list[NewsItem] = []
        for item in candidates[:max_relevance_checks]:
            if len(relevant) >= POSTS_PER_CATEGORY * 3:  # запас на случай если sendPhoto/перевод сломается
                break
            try:
                if is_relevant(item.title, item.summary, category["title"], interests):
                    relevant.append(item)
                else:
                    log.info("  — нерелевантно: %s", item.title[:90])
            except Exception as e:
                log.warning("Ошибка проверки релевантности (%s), пропускаю", e)
                relevant.append(item)
        if not relevant and candidates:
            # Если фильтр всех отбраковал — берём самую свежую как страховку
            log.info("Релевантных не нашлось, беру самую свежую как fallback")
            relevant = candidates[:POSTS_PER_CATEGORY]
        log.info("Релевантных: %d", len(relevant))

        picked = 0
        for item in relevant:
            if picked >= POSTS_PER_CATEGORY:
                break
            try:
                ru_title, ru_body = prepare_ru_post(item)
            except Exception as e:
                log.warning("Ошибка подготовки поста %s: %s", item.link, e)
                continue

            post_text = format_post(category, item, ru_title, ru_body)
            img = item.image or _fetch_og_image(item.link)
            if send_to_telegram(token, chat_id, post_text, image_url=img):
                log.info("Опубликовано: %s", item.link)
                new_urls.add(item.link)
                picked += 1
                total_posted += 1
                time.sleep(3)
            else:
                log.warning("Не удалось опубликовать %s", item.link)

        log.info("Категория %s: опубликовано %d", key, picked)

    if new_urls:
        save_posted_urls(posted_urls | new_urls)
        log.info("State сохранён (+%d ссылок)", len(new_urls))

    log.info("Итого: %d постов", total_posted)
    return 0


if __name__ == "__main__":
    sys.exit(main())
