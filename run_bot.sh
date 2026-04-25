#!/bin/bash
# News bot local runner for macOS. Triggered by launchd.
# Загружает секреты из .env, ждёт интернет, запускает бота с retry при сетевом сбое.

set -u

BOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_FILE="$BOT_DIR/run.log"
ENV_FILE="$BOT_DIR/.env"

# Найти python (предпочтение python3.12, затем 3.11, затем python3)
PYTHON=""
for cmd in python3.12 python3.11 python3; do
    if command -v "$cmd" >/dev/null 2>&1; then
        PYTHON="$cmd"
        break
    fi
done
if [ -z "$PYTHON" ]; then
    echo "ERROR: python3 not found in PATH" >> "$LOG_FILE"
    exit 1
fi

# Загрузить .env
if [ ! -f "$ENV_FILE" ]; then
    echo "ERROR: .env not found at $ENV_FILE" >> "$LOG_FILE"
    exit 1
fi
set -a
# shellcheck disable=SC1090
source "$ENV_FILE"
set +a
export PYTHONIOENCODING=utf-8

cd "$BOT_DIR"

# Ротация лога если > 2 MB
if [ -f "$LOG_FILE" ]; then
    size=$(wc -c < "$LOG_FILE" | tr -d ' ')
    if [ "$size" -gt 2097152 ]; then
        mv "$LOG_FILE" "$LOG_FILE.old"
    fi
fi

echo "=== $(date '+%Y-%m-%d %H:%M:%S') start ===" >> "$LOG_FILE"

# Ждём пока появится интернет (после пробуждения из сна)
NET_OK=false
for i in $(seq 0 29); do
    if "$PYTHON" -c "import socket; socket.gethostbyname('habr.com')" >/dev/null 2>&1; then
        NET_OK=true
        echo "Network ready after ~$((i * 2))s" >> "$LOG_FILE"
        break
    fi
    sleep 2
done
if ! $NET_OK; then
    echo "ERROR: no network after 60s, aborting" >> "$LOG_FILE"
    exit 1
fi

# Запускаем бота
run_bot() {
    "$PYTHON" "$BOT_DIR/bot.py" >> "$LOG_FILE" 2>&1
    echo $?
}

EXIT_CODE=$(run_bot)

# Если все фиды вернули 0 — подозрение на сетевой сбой, retry через 30с
if tail -n 60 "$LOG_FILE" | grep -q "Итого: 0 постов" \
   && [ "$(tail -n 60 "$LOG_FILE" | grep -c '0 всего, 0 свежих')" -ge 5 ]; then
    echo "All feeds returned 0 — suspected network flake. Retrying in 30s..." >> "$LOG_FILE"
    sleep 30
    EXIT_CODE=$(run_bot)
fi

echo "=== $(date '+%Y-%m-%d %H:%M:%S') done (exit $EXIT_CODE) ===" >> "$LOG_FILE"
exit "$EXIT_CODE"
