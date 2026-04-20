"""
Состояние: какие URL уже публиковали, чтобы не дублировать.
Храним в state.json, GitHub Actions коммитит файл обратно в репо после каждого запуска.
"""
import json
from pathlib import Path

STATE_FILE = Path(__file__).parent / "state.json"
MAX_REMEMBERED = 2000  # держим последние N URL — хватит на месяцы


def load_posted_urls() -> set[str]:
    if not STATE_FILE.exists():
        return set()
    try:
        data = json.loads(STATE_FILE.read_text(encoding="utf-8"))
        return set(data.get("posted", []))
    except Exception:
        return set()


def save_posted_urls(urls: set[str]) -> None:
    items = list(urls)[-MAX_REMEMBERED:]
    STATE_FILE.write_text(
        json.dumps({"posted": items}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
