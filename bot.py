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

from sources import SOURCES, POSTS_PER_CATEGORY, FRESHNESS_HOURS
from state import load_posted_urls, save_posted_urls
from translator import prepare_post

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


def collect_candidates(category_key: str) -> list[NewsItem]:
    cutoff = datetime.now(timezone.utc) - timedelta(hours=FRESHNESS_HOURS)
    candidates: list[NewsItem] = []
    for source in SOURCES[category_key]["feeds"]:
        items = parse_feed(source)
        fresh = [i for i in items if i.published >= cutoff]
        log.info("  %s: %d всего, %d свежих", source["name"], len(items), len(fresh))
        candidates.extend(fresh)
    candidates.sort(key=lambda x: x.published, reverse=True)
    return candidates


def prepare_ru_post(item: NewsItem) -> tuple[str, str]:
    """Вернуть (заголовок_на_рус, тело_на_рус) — делегируется в translator.prepare_post."""
    return prepare_post(item.title, item.summary, item.source, item.lang)


def format_post(category: dict, item: NewsItem, ru_title: str, ru_body: str) -> str:
    emoji = category["emoji"]
    hashtag = category.get("hashtag", "")
    parts = [
        f"{emoji} <b>{html.escape(ru_title)}</b>",
    ]
    if ru_body:
        parts += ["", html.escape(ru_body)]
    parts += ["", f"🔗 <a href=\"{html.escape(item.link)}\">{html.escape(item.source)}</a>"]
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

        picked = 0
        for item in candidates:
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
