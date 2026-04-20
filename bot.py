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

import feedparser
import requests

from sources import SOURCES, POSTS_PER_CATEGORY, FRESHNESS_HOURS
from state import load_posted_urls, save_posted_urls
from translator import translate_to_russian, smart_truncate

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


def parse_feed(source: dict) -> list[NewsItem]:
    try:
        feed = feedparser.parse(
            source["url"],
            request_headers={"User-Agent": "Mozilla/5.0 NewsBot/1.0"},
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
        ))
    return items


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
    """Вернуть (заголовок_на_рус, тело_на_рус)."""
    if item.lang == "ru":
        title_ru = item.title
        body_ru = smart_truncate(item.summary, max_chars=450)
    else:
        title_ru = translate_to_russian(item.title, source_lang="en")
        body_short = smart_truncate(item.summary, max_chars=500)
        body_ru = translate_to_russian(body_short, source_lang="en")
    return title_ru, body_ru


def format_post(category: dict, item: NewsItem, ru_title: str, ru_body: str) -> str:
    emoji = category["emoji"]
    cat_title = category["title"]
    parts = [
        f"{emoji} <b>{html.escape(cat_title)}</b>",
        "",
        f"<b>{html.escape(ru_title)}</b>",
    ]
    if ru_body:
        parts += ["", html.escape(ru_body)]
    parts += ["", f"🔗 <a href=\"{html.escape(item.link)}\">{html.escape(item.source)}</a>"]
    return "\n".join(parts)


def send_to_telegram(token: str, chat_id: str, text: str) -> bool:
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text[:4000],  # Telegram лимит 4096
        "parse_mode": "HTML",
        "disable_web_page_preview": False,
    }
    try:
        r = requests.post(url, json=payload, timeout=30)
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
            if send_to_telegram(token, chat_id, post_text):
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
