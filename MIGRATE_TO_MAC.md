# Переезд бота с Windows на Mac

Коротко: код уже на GitHub. Нужно только перенести два локальных файла (`.env` и `state.json`), клонировать репо на Mac и запустить установщик.

## Шаг 1 (Windows): сделайте бэкап

В PowerShell, в папке `news-bot`:

```powershell
.\backup_for_mac.ps1
```

Появится **`mammy-news-migration.zip`** на рабочем столе. Внутри:
- `.env` — секреты (токен бота, ключ GigaChat)
- `state.json` — история того, что бот уже опубликовал (чтобы на Mac не дублировать)

Перенесите zip на Mac любым удобным способом — **iCloud Drive, AirDrop, флешка, email**.

После переноса — на Windows можно отключить задачу в Планировщике (Task Scheduler → MammyNewsBot → Disable), чтобы не было двух одновременных запусков.

## Шаг 2 (Mac): подготовка системы

Откройте **Terminal**.

### Установить Homebrew (если ещё нет):
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

### Установить Python 3.12 и git:
```bash
brew install python@3.12 git
```

### Авторизоваться в GitHub (если ещё нет):
```bash
brew install gh
gh auth login
```
Дальше как на Windows: GitHub.com → HTTPS → Login with browser.

## Шаг 3 (Mac): клонировать и установить

```bash
cd ~/Desktop
gh repo clone GlebGorshe/mammy-news-bot
cd mammy-news-bot

# Распакуйте mammy-news-migration.zip в эту папку
# (после распаковки тут должны появиться .env и state.json)
unzip ~/Downloads/mammy-news-migration.zip -d .

# Установите зависимости Python
python3.12 -m pip install -r requirements.txt

# Тестовый запуск — проверим что всё работает
chmod +x run_bot.sh
./run_bot.sh
```

Если всё ОК — в канале появятся 5 постов. Проверьте `run.log`.

## Шаг 4 (Mac): автозапуск

```bash
./install_scheduler.sh
```

Создаст launchd-задачу на 9:00 / 15:00 / 21:00 ежедневно по локальному времени Mac.

### Чтобы Mac просыпался для утреннего запуска

В сне launchd не работает. Два варианта:

**Вариант A (компромисс):** разбудить Mac автоматом каждое утро в 8:55:
```bash
sudo pmset repeat wakeorpoweron MTWRFSU 08:55:00
```
Запуски в 15:00 и 21:00 произойдут если Mac в этот момент включён или вы его пробудите. Обычно днём проблем нет.

**Вариант B (надёжнее, +чуть расхода):** не давать Mac засыпать когда подключён к зарядке:
```bash
sudo pmset -c sleep 0
```
Тогда launchd срабатывает железно во все 3 времени, но Mac не уходит в сон при питании от сети.

Я рекомендую B.

## Полезные команды на Mac

```bash
# Список задач:
launchctl list | grep mammynews

# Запустить вручную сейчас:
launchctl start com.mammynews.bot

# Посмотреть лог бота:
tail -f run.log

# Удалить задачу совсем:
launchctl unload ~/Library/LaunchAgents/com.mammynews.bot.plist
rm ~/Library/LaunchAgents/com.mammynews.bot.plist
```

## Если что-то не работает

- В Claude Code на Mac скажите `«проверь почему бот не запустился»` — попросите его глянуть `run.log`. Контекст проекта он подтянет из памяти.
- Если ошибка `python3.12: command not found` — поменяйте `python3.12` на `python3` в `run_bot.sh`.
- Если launchd не запускается — `launchctl list | grep mammynews` покажет статус. Кодов ошибок там же.
