#!/bin/bash
# Установить launchd-задачу на Mac: запуск бота 9:00 / 15:00 / 21:00 ежедневно.
# Запускается один раз пользователем после клонирования репозитория.

set -e

BOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PLIST_LABEL="com.mammynews.bot"
PLIST_PATH="$HOME/Library/LaunchAgents/$PLIST_LABEL.plist"

# Делаем run_bot.sh исполняемым
chmod +x "$BOT_DIR/run_bot.sh"

# Если задача уже стояла — выгружаем
if launchctl list | grep -q "$PLIST_LABEL"; then
    launchctl unload "$PLIST_PATH" 2>/dev/null || true
fi

mkdir -p "$HOME/Library/LaunchAgents"

cat > "$PLIST_PATH" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>$PLIST_LABEL</string>

    <key>ProgramArguments</key>
    <array>
        <string>/bin/bash</string>
        <string>$BOT_DIR/run_bot.sh</string>
    </array>

    <key>WorkingDirectory</key>
    <string>$BOT_DIR</string>

    <key>StandardOutPath</key>
    <string>$BOT_DIR/launchd.out.log</string>

    <key>StandardErrorPath</key>
    <string>$BOT_DIR/launchd.err.log</string>

    <key>StartCalendarInterval</key>
    <array>
        <dict>
            <key>Hour</key><integer>9</integer>
            <key>Minute</key><integer>0</integer>
        </dict>
        <dict>
            <key>Hour</key><integer>15</integer>
            <key>Minute</key><integer>0</integer>
        </dict>
        <dict>
            <key>Hour</key><integer>21</integer>
            <key>Minute</key><integer>0</integer>
        </dict>
    </array>

    <key>RunAtLoad</key>
    <false/>
</dict>
</plist>
EOF

launchctl load "$PLIST_PATH"

echo "Готово. Задача '$PLIST_LABEL' установлена."
echo "Запуск: 9:00 / 15:00 / 21:00 ежедневно (по локальному времени Mac)."
echo ""
echo "Полезные команды:"
echo "  Список:        launchctl list | grep mammynews"
echo "  Запустить сейчас: launchctl start $PLIST_LABEL"
echo "  Удалить:       launchctl unload \"$PLIST_PATH\" && rm \"$PLIST_PATH\""
echo "  Лог бота:      tail -f \"$BOT_DIR/run.log\""
echo ""
echo "ВАЖНО для пробуждения из сна на macOS:"
echo "  Чтобы Mac просыпался для задачи, выполните (один раз, требует пароля):"
echo "    sudo pmset repeat wakeorpoweron MTWRFSU 08:55:00"
echo "  Это будит Mac в 8:55 каждый день. Запуски в 15:00 и 21:00 обычно"
echo "  происходят когда Mac уже разбужен пользователем."
echo "  Альтернатива (надёжнее, но повышенный расход): запретить сон при питании от сети:"
echo "    sudo pmset -c sleep 0"
