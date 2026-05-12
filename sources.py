"""
RSS-источники по категориям. lang='ru' — не переводим, 'en' — переводим через Google.
"""

SOURCES = {
    "ai": {
        "emoji": "🤖",
        "title": "Нейросети и ИИ",
        "hashtag": "#нейросети",
        "interests": (
            "Новости про искусственный интеллект и нейросети.\n\n"
            "ВЫСШИЙ ПРИОРИТЕТ:\n"
            "- ВСЕ обновления Claude от Anthropic (новые модели Opus/Sonnet/Haiku, "
            "Claude Code, Claude Agent SDK, MCP, Projects, Artifacts, любые новые фичи) — "
            "это всегда ДА;\n"
            "- AI-инструменты для МУЗЫКИ и звука: Suno, Udio, ElevenLabs, AIVA, Stable Audio, "
            "AI-плагины для DAW (Cubase, Ableton, FL Studio), AI-мастеринг, AI-стемы и сепарация, "
            "генерация вокала и инструментала, голосовые модели — это всегда ДА;\n"
            "- AI-инструменты для ДИЗАЙНА и визуала: Midjourney, DALL-E, Stable Diffusion, Flux, "
            "Runway, Sora, Veo, Kling, Figma AI, Adobe Firefly, AI в архитектуре и интерьере, "
            "img2img, видео-генерация — это всегда ДА.\n\n"
            "ТАКЖЕ ПОДХОДИТ:\n"
            "- релизы и обновления других топ-моделей (ChatGPT/GPT, Gemini, Grok, опенсорс — Llama, Qwen, DeepSeek);\n"
            "- крупные AI-продукты и сервисы для творчества;\n"
            "- важные исследования и прорывы в AI;\n"
            "- значимые споры и драмы в AI-индустрии (Sam Altman, Elon Musk, OpenAI vs Anthropic vs xAI);\n"
            "- регуляция AI, влияние ИИ на креативные индустрии.\n\n"
            "НЕ ПОДХОДИТ:\n"
            "- общие IT/кибербез без AI;\n"
            "- обычные гаджеты;\n"
            "- бизнес-аналитика без AI-составляющей;\n"
            "- AI в военке, биотехе, медицине без связи с творческими/потребительскими инструментами."
        ),
        "feeds": [
            # Русские
            {"name": "Habr AI",            "url": "https://habr.com/ru/rss/hub/artificial_intelligence/all/?fl=ru", "lang": "ru"},
            {"name": "Habr ML",            "url": "https://habr.com/ru/rss/hub/machine_learning/all/?fl=ru",         "lang": "ru"},
            # Лаборатории и крупные издания
            {"name": "OpenAI",             "url": "https://openai.com/news/rss.xml",                                 "lang": "en"},
            {"name": "Google AI",          "url": "https://blog.google/technology/ai/rss/",                          "lang": "en"},
            {"name": "DeepMind",           "url": "https://deepmind.google/blog/rss.xml",                            "lang": "en"},
            {"name": "Hugging Face",       "url": "https://huggingface.co/blog/feed.xml",                            "lang": "en"},
            {"name": "MIT Tech Review AI", "url": "https://www.technologyreview.com/topic/artificial-intelligence/feed", "lang": "en"},
            {"name": "Ars Technica AI",    "url": "https://arstechnica.com/ai/feed/",                                "lang": "en"},
            {"name": "TechCrunch AI",      "url": "https://techcrunch.com/category/artificial-intelligence/feed/",   "lang": "en"},
            {"name": "The Verge",          "url": "https://www.theverge.com/rss/index.xml",                          "lang": "en"},
            # Авторские блоги/ньюслеттеры — высший сигнал по AI
            {"name": "Simon Willison",     "url": "https://simonwillison.net/atom/everything/",                      "lang": "en"},
            {"name": "Latent Space",       "url": "https://www.latent.space/feed",                                   "lang": "en"},
            {"name": "Andrej Karpathy",    "url": "https://karpathy.bearblog.dev/feed/",                             "lang": "en"},
            {"name": "Last Week in AI",    "url": "https://lastweekin.ai/feed",                                      "lang": "en"},
        ],
    },
    "hiphop": {
        "emoji": "🎵",
        "title": "Музыка",
        "hashtag": "#музыка",
        "interests": (
            "ТОЛЬКО актуальная музыкальная сцена: хип-хоп, рэп, R&B, трэп, drill, "
            "afrobeats, hyperpop и современные/новые жанры на стыке. "
            "Главный фокус — АКТУАЛЬНОЕ, СВЕЖЕЕ, МОЛОДЁЖНОЕ. "
            "Особенно ценна СВЯЗКА русской и зарубежной сцены.\n\n"
            "ВЫСШИЙ ПРИОРИТЕТ — РУССКИЙ РЭП НОВОЙ ВОЛНЫ (любые их новости — ДА):\n"
            "OG Buda, MAYOT, Платина, ATM, Хофманита, Toxi$, Cakeboy, "
            "Baby Cute, SkyRay, Lovv66, Soda Luv, Friendly Thug 52 NGG, "
            "Big Baby Tape, Aikko, GONE.Fludd, Slava Marlow, OBLADAET, Markul, "
            "Pyrokinesis, Pharaoh, Husky, Loqiemean, Ssshhhiiittt!, Kizaru, "
            "MORGENSHTERN, Boulevard Depo, Yanix, Тима Белорусских, "
            "Monetochka, ICEGERGERT, 9mice, KIZARU, Мукка, Эра Канн.\n\n"
            "ВЫСШИЙ ПРИОРИТЕТ — ЗАРУБЕЖНЫЕ АКТУАЛЬНЫЕ АРТИСТЫ (любые их новости — ДА):\n"
            "Travis Scott, Future, Drake, Kendrick Lamar, Don Toliver, Playboi Carti, "
            "Yeat, Ken Carson, Destroy Lonely, Lil Yachty, Lil Uzi Vert, 21 Savage, "
            "Metro Boomin, Tyler the Creator, A$AP Rocky, A$AP Ferg, Young Thug, "
            "Gunna, Lil Baby, Lil Durk, Roddy Ricch, J. Cole, Quavo, Offset, "
            "Lil Yachty, Denzel Curry, JID, Smino, Saba, Jack Harlow, Central Cee, "
            "Dave, Stormzy, Skepta, Burna Boy, Rema, Wizkid, Tems.\n\n"
            "ВЫСШИЙ ПРИОРИТЕТ — ФРЕШМЕНЫ И НОВЫЕ ЗАРУБЕЖНЫЕ:\n"
            "XXL Freshman Class, breakout-артисты последних 1-2 лет, "
            "Ice Spice, GloRilla, Sexyy Red, Lola Brooke, Doechii, Cash Cobain, Veeze, "
            "BabyTron, Skilla Baby, That Mexican OT, Lil Tecca, Lil Tjay, NLE Choppa, "
            "Babyface Ray, 42 Dugg, Pooh Shiesty, Kodak Black, Rod Wave, Polo G, "
            "Latto, Coi Leray, Flo Milli, Maiya The Don.\n\n"
            "ВЫСШИЙ ПРИОРИТЕТ — R&B новой волны:\n"
            "PinkPantheress, SZA, Brent Faiyaz, Daniel Caesar, Lucky Daye, "
            "Summer Walker, Bryson Tiller, Coco & Clair Clair, FLO, Victoria Monét, "
            "Jorja Smith, Snoh Aalegra, Kaytranada, dvsn, 6lack.\n\n"
            "ТАКЖЕ ДА:\n"
            "- русско-зарубежные коллабы и пересечения сцен — это всегда ДА;\n"
            "- новые альбомы, EP, синглы, клипы, mixtape (не перевыпуски);\n"
            "- значимые бифы и драмы между актуальными рэп/R&B-артистами;\n"
            "- крупные коллабы;\n"
            "- лейбловые подписания у молодых;\n"
            "- Grammy в категориях Rap/R&B, чарты Billboard в рэп/R&B-сегменте;\n"
            "- значимые туры и концерты актуальных артистов.\n\n"
            "ОТКЛОНЯЙ если новость про:\n"
            "- ретроспективы 90-х/2000-х, байопики, 'where are they now' про неактивных;\n"
            "- цитаты и реакции подкастеров/блогеров (Joe Budden, DJ Akademiks, Funk Flex) — всегда НЕТ;\n"
            "- кроссовки/мода/брендовые послы — даже если коллаб с музыкантом, это НЕ музыкальная новость "
            "(пример: 'Ningning из aespa стала послом Gucci' — НЕТ).\n\n"
            "АБСОЛЮТНЫЙ ЗАПРЕТ (всегда НЕТ, без исключений):\n"
            "- ЛЮБАЯ политика и государственные деятели: Песков, Лавров, Захарова, Путин, Мишустин, "
            "Медведев, Шойгу, Кремль, Госдума, депутаты, министры, чиновники, заявления политиков, "
            "санкции, СВО, Украина, Зеленский, обстрелы, дроны, ракеты — это НЕ музыка, это политика;\n"
            "- спорт любого вида (футбол, хоккей, биатлон, чемпионаты, тренеры, голы);\n"
            "- происшествия и криминал (ДТП, пожары, убийства, ограбления);\n"
            "- K-pop и айдол-сцена (BTS, BLACKPINK, aespa, NewJeans, Stray Kids, TWICE, Seventeen, ENHYPEN);\n"
            "- классическая поп-музыка (Тейлор Свифт, Селена Гомез, Демиа Ловато, Меган Трейнор, Бритни Спирс, Ариана Гранде);\n"
            "- кантри (Carrie Underwood, Morgan Wallen, Kacey Musgraves), рок, инди, металл "
            "(Foo Fighters, Sepultura, любые рок-группы), фолк, классика;\n"
            "- электронная танцевальная музыка без рэп/R&B-контекста;\n"
            "- комедийные шоу и стендап (SNL и его варианты), мюзиклы;\n"
            "- кино- и теле-премьеры даже про музыкантов;\n"
            "- светские новости и шоу-бизнес не из рэп/R&B-сцены."
        ),
        "feeds": [
            # Telegram-каналы (русский рэп — первый приоритет)
            {"name": "@rapsmi",          "url": "rapsmi",          "lang": "ru", "type": "telegram"},
            {"name": "@rapnewstelegram", "url": "rapnewstelegram", "lang": "ru", "type": "telegram"},
            {"name": "@hiphop4real",     "url": "hiphop4real",     "lang": "ru", "type": "telegram"},
            {"name": "@theflow_ru",      "url": "theflow_ru",      "lang": "ru", "type": "telegram"},
            {"name": "@rapinfo",         "url": "rapinfo",         "lang": "ru", "type": "telegram"},
            {"name": "@hiphopru",        "url": "hiphopru",        "lang": "ru", "type": "telegram"},
            {"name": "@rhymestg",        "url": "rhymestg",        "lang": "ru", "type": "telegram"},
            # Русские RSS
            {"name": "InterMedia",      "url": "https://www.intermedia.ru/rss/news.xml",    "lang": "ru"},
            # Зарубежные RSS — крупные издания
            {"name": "XXL Magazine",    "url": "https://www.xxlmag.com/feed/",              "lang": "en"},
            {"name": "HotNewHipHop",    "url": "https://www.hotnewhiphop.com/feed",         "lang": "en"},
            {"name": "Complex Music",   "url": "https://www.complex.com/music.xml",         "lang": "en"},
            {"name": "Pitchfork News",  "url": "https://pitchfork.com/rss/news/",           "lang": "en"},
            {"name": "The Fader",       "url": "https://www.thefader.com/feed",             "lang": "en"},
            {"name": "Stereogum",       "url": "https://stereogum.com/feed",                "lang": "en"},
            {"name": "Billboard",       "url": "https://www.billboard.com/feed/",           "lang": "en"},
        ],
    },
    "street": {
        "emoji": "🎨",
        "title": "Стритвир, дизайн, искусство",
        "hashtag": "#стритвир",
        "interests": (
            "Стритвир, уличная мода, дизайн, современное искусство — с акцентом на "
            "АКТУАЛЬНУЮ молодёжную сцену.\n\n"
            "ВЫСШИЙ ПРИОРИТЕТ — РОССИЙСКАЯ МОЛОДЁЖНАЯ СЦЕНА (любые их новости — ДА):\n"
            "- русские дизайн-бренды и инди-марки (Volchok, GR8, OFF the GRID, Solli, "
            "Karelin, Lesyanebo, Outlaw Moscow, Walk of Shame, Ruh Hides, ЦУМ Marketplace);\n"
            "- Y2K-эстетика, нулевые, 90-е возвращение, гранж, нео-готика, alt-fashion;\n"
            "- молодые российские дизайнеры, художники, кастомщики, граффитчики;\n"
            "- российские арт-выставки и галереи (Гараж, ГЭС-2, Винзавод, ЦСИ Винзавод, MMOMA);\n"
            "- русские дропы, коллабы, поп-апы, маркеты молодых брендов.\n\n"
            "ТАКЖЕ ДА:\n"
            "- зарубежный стритвир (Supreme, Stüssy, Nike, Jordan, Yeezy, Corteiz, Aimé Leon Dore), "
            "дропы и коллабы;\n"
            "- кроссовки и сникер-релизы (Air Force, Air Max, Samba, New Balance);\n"
            "- граффити, стрит-арт, паблик-арт;\n"
            "- современное искусство и арт-инсталляции;\n"
            "- авторский дизайн мебели и интерьеров, архитектура с концепцией.\n\n"
            "НЕ нужны: коммерческая реклама, корпоративные интервью без содержания, "
            "сухие отчёты о выставках без сути, чистый haute couture без уличного контекста, "
            "масс-маркет (Zara/H&M/Uniqlo без коллаба)."
        ),
        "feeds": [
            # Русские тг-каналы — Y2K, молодёжные бренды, российский дизайн, арт
            {"name": "@futurmag",           "url": "futurmag",           "lang": "ru", "type": "telegram"},
            {"name": "@theblueprintru",     "url": "theblueprintru",     "lang": "ru", "type": "telegram"},
            {"name": "@theartnewspaperru",  "url": "theartnewspaperru",  "lang": "ru", "type": "telegram"},
            # Русские RSS
            {"name": "The Blueprint",        "url": "https://theblueprint.ru/rss",                      "lang": "ru"},
            # Стритвир / мода
            {"name": "Hypebeast",            "url": "https://hypebeast.com/feed",                       "lang": "en"},
            {"name": "Highsnobiety",         "url": "https://www.highsnobiety.com/feed/",               "lang": "en"},
            {"name": "Dazed",                "url": "https://www.dazeddigital.com/rss",                 "lang": "en"},
            # Дизайн / архитектура
            {"name": "Dezeen",               "url": "https://www.dezeen.com/feed/",                     "lang": "en"},
            {"name": "Designboom",           "url": "https://www.designboom.com/feed/",                 "lang": "en"},
            {"name": "ArchDaily",            "url": "https://feeds.feedburner.com/Archdaily",           "lang": "en"},
            {"name": "Design Milk",          "url": "https://design-milk.com/feed/",                    "lang": "en"},
            {"name": "Wallpaper",            "url": "https://www.wallpaper.com/rss",                    "lang": "en"},
            {"name": "Architectural Digest", "url": "https://www.architecturaldigest.com/feed/rss",     "lang": "en"},
            # Искусство / визуальная культура
            {"name": "It's Nice That",       "url": "https://feeds2.feedburner.com/itsnicethat/SlXC",   "lang": "en"},
            {"name": "Cool Hunting",         "url": "https://coolhunting.com/feed/",                    "lang": "en"},
            {"name": "Juxtapoz",             "url": "https://www.juxtapoz.com/feed/",                   "lang": "en"},
            {"name": "Colossal",             "url": "https://www.thisiscolossal.com/feed/",             "lang": "en"},
            {"name": "Hyperallergic",        "url": "https://hyperallergic.com/feed/",                  "lang": "en"},
        ],
    },
    "russia": {
        "emoji": "🇷🇺",
        "title": "Россия",
        "hashtag": "#россия",
        "interests": (
            "ТОЛЬКО важные федеральные события России — то, что реально влияет на страну. "
            "Подходит: ключевые решения Кремля и правительства, новые законы общегосударственного уровня, "
            "военная операция и её итоги, серьёзные ЧП федерального масштаба с большим резонансом, "
            "крупные политические заявления первых лиц (Путин, Мишустин, Лавров) по существу, "
            "санкции и международные отношения на высшем уровне, "
            "крупные экономические указы, демография, миграция, безопасность страны. "
            "КАТЕГОРИЧЕСКИ НЕ подходит и должно отклоняться: "
            "спорт любого вида (тренеры, матчи, голы, поражения, чемпионаты, биатлон, хоккей, футбол), "
            "мелкие происшествия (водитель сбил, кого-то ограбили, локальные ДТП и пожары), "
            "курьёзные истории и анекдотичные цитаты чиновников ('министр посоветовал футболисту'), "
            "поражения российских клубов и спортсменов, "
            "светские новости и шоу-бизнес, "
            "обычные региональные новости без федерального резонанса, "
            "пустая пропагандистская риторика без конкретных фактов и решений, "
            "криминальная мелочёвка. "
            "Только новости уровня 'это важно для всей страны' — иначе отклоняй."
        ),
        "feeds": [
            {"name": "Лента.ру",     "url": "https://lenta.ru/rss/news",                         "lang": "ru"},
            {"name": "ТАСС",         "url": "https://tass.ru/rss/v2.xml",                        "lang": "ru"},
            {"name": "РИА Новости",  "url": "https://ria.ru/export/rss2/archive/index.xml",      "lang": "ru"},
            {"name": "Интерфакс",    "url": "https://www.interfax.ru/rss.asp",                   "lang": "ru"},
            {"name": "Коммерсантъ",  "url": "https://www.kommersant.ru/RSS/news.xml",            "lang": "ru"},
            {"name": "Газета.ру",    "url": "https://www.gazeta.ru/export/rss/first.xml",        "lang": "ru"},
        ],
    },
    "economy": {
        "emoji": "💰",
        "title": "Экономика, финансы, крипта",
        "hashtag": "#экономика",
        "interests": (
            "Экономика и финансы с фокусом на ИНВЕСТИЦИОННЫЕ ИДЕИ и РОСТ АКТИВОВ "
            "частного инвестора — что покупать, во что вкладываться, где есть апсайд.\n\n"
            "ВЫСШИЙ ПРИОРИТЕТ:\n"
            "- конкретные инвест-идеи и разборы активов (российские и зарубежные акции "
            "с потенциалом роста, перспективные облигации, ETF, фонды);\n"
            "- IPO и pre-IPO с понятной тезой роста, M&A с переоценкой бумаг;\n"
            "- ключевые отчёты компаний (Сбер, Газпром, Yandex, Магнит, Apple, Nvidia, "
            "Tesla, Meta) — выручка, прибыль, прогнозы, дивиденды;\n"
            "- решения ЦБ РФ и ФРС по ставке — как влияет на акции, облигации, рубль;\n"
            "- крипто-идеи: BTC/ETH циклы, перспективные альты, DeFi, стейкинг-доходности, "
            "крупные айрдропы, новые L1/L2, RWA-токенизация, регуляция крипты;\n"
            "- сырьё с инвест-углом (нефть, золото, медь, литий — что покупать);\n"
            "- валюты как инструмент (USD/RUB, юань, токенизированные доллары).\n\n"
            "ТАКЖЕ ДА:\n"
            "- макро-новости, у которых есть ясный вывод для инвестора;\n"
            "- санкции и геополитика — только если меняют инвест-картину.\n\n"
            "НЕ нужны:\n"
            "- голая макро-статистика без выводов 'что делать инвестору';\n"
            "- спорт, культура, шоу-бизнес, бытовые истории;\n"
            "- технологии без финансовой стороны;\n"
            "- политика без экономического контекста;\n"
            "- скам-схемы 'X100 за неделю', пирамиды, агрессивные крипто-промо."
        ),
        "feeds": [
            # Русские крупные
            {"name": "RBC",              "url": "https://rssexport.rbc.ru/rbcnews/news/30/full.rss",     "lang": "ru"},
            {"name": "Коммерсантъ",      "url": "https://www.kommersant.ru/RSS/section-economics.xml",   "lang": "ru"},
            {"name": "Forbes.ru",        "url": "https://www.forbes.ru/newrss.xml",                      "lang": "ru"},
            # Русские независимые премиум-качество
            {"name": "The Bell",         "url": "https://thebell.io/feed",                               "lang": "ru"},
            {"name": "Frank Media",      "url": "https://frankmedia.ru/feed",                            "lang": "ru"},
            # Зарубежные крупные
            {"name": "CNBC Business",    "url": "https://search.cnbc.com/rs/search/combinedcms/view.xml?partnerId=wrss01&id=10001147", "lang": "en"},
            # Крипта (русские)
            {"name": "ForkLog",          "url": "https://forklog.com/feed",                              "lang": "ru"},
            {"name": "Incrypted",        "url": "https://incrypted.com/feed/",                           "lang": "ru"},
            # Крипта (зарубежные)
            {"name": "CoinDesk",         "url": "https://www.coindesk.com/arc/outboundfeeds/rss/",       "lang": "en"},
            {"name": "Decrypt",          "url": "https://decrypt.co/feed",                               "lang": "en"},
            {"name": "The Block",        "url": "https://www.theblock.co/rss.xml",                       "lang": "en"},
            {"name": "CoinTelegraph",    "url": "https://cointelegraph.com/rss",                         "lang": "en"},
            {"name": "Bankless",         "url": "https://www.bankless.com/feed",                         "lang": "en"},
            {"name": "The Defiant",      "url": "https://thedefiant.io/feed",                            "lang": "en"},
        ],
    },
}

# Сколько постов публиковать за один прогон на категорию
# 3 прогона в день × 1 пост = 3 новости в каждой категории в день
POSTS_PER_CATEGORY = 1

# Насколько свежими должны быть новости (часы)
FRESHNESS_HOURS = 24

# Жёсткий блэклист по regex — режется ДО проверки LLM на релевантность.
# Срабатывает по полю title или summary (без учёта регистра).
# Используется когда LLM-фильтр пропускает явный мусор (политика в музыке, K-pop, спорт и т.п.).
HARD_REJECT_PATTERNS = {
    "hiphop": [
        # --- Политика и государственные деятели РФ ---
        r"песк[оа]в",                # Песков, Пескова
        r"лавров",
        r"захарова",
        r"\bпутин",
        r"мишустин",
        r"медведев",
        r"шойгу",
        r"кремл",                    # Кремль, кремлёвский
        r"госдум",
        r"\bдепутат",
        r"\bсенатор",
        r"совет\s+федерации",
        r"\bминистр\b",
        r"чиновник",
        r"\bмид\s+рф\b",
        # --- Война / геополитика ---
        r"\bсво\b",
        r"спецоперац",
        r"\bукраин",
        r"зеленский",
        r"\bтрамп",
        r"\bбайден",
        r"\bпентагон",
        r"\bнато\b",
        r"\bобстрел",
        r"\bдрон",
        r"\bракет",
        r"всу\b",
        # --- Спорт ---
        r"\bматч\b",
        r"чемпионат",
        r"биатлон",
        r"\bхоккей",
        r"\bфутбол",
        r"волейбол",
        r"\bтренер",
        r"сборная",
        r"\bгол\s+(в\s+ворота|на\s+\d)",
        # --- Происшествия ---
        r"\bдтп\b",
        r"\bпожар\b",
        r"\bограбил",
        r"\bубил\b|\bубит\b",
        # --- K-pop ---
        r"\bk-?pop\b",
        r"\bbts\b",
        r"blackpink",
        r"\baespa\b",
        r"newjeans",
        r"stray\s+kids",
        r"\btwice\b",
        r"seventeen",
        r"enhypen",
        r"айдол",
        # --- Поп-музыка и другие жанры вне рэп/R&B ---
        r"тейлор\s+свифт|taylor\s+swift",
        r"селена\s+гомес|selena\s+gomez",
        r"бритни\s+спирс|britney\s+spears",
        r"ариана\s+гранде|ariana\s+grande",
        r"\bsnl\b",
        r"saturday\s+night\s+live",
        # --- Кантри (мейнстрим-имена и ключевые слова) ---
        r"\bcountry\s+(music|singer|star|artist|song|album)",
        r"кантри-(музык|певи|звезд|артист)",
        r"carrie\s+underwood",
        r"kacey\s+musgraves",
        r"luke\s+combs",
        r"morgan\s+wallen",
        r"chris\s+stapleton",
        r"jelly\s+roll",
        r"zach\s+bryan",
        r"ella\s+langley",
        r"stagecoach",
        r"tennessee\s+farm",       # Carrie Underwood про ферму в Теннесси
        r"\bnashville\b.{0,40}(country|farm|hometown)",
        # --- Рок, инди, металл ---
        r"\brock\s+(band|album|song|legend|hall\s+of\s+fame)",
        r"\bmetal\s+(band|album)",
        r"foo\s+fighters",
        r"sepultura",
        r"metallica",
        r"\bnirvana\b",
        # --- URL-разделы Billboard/Pitchfork — ловим жанр прямо из ссылки ---
        r"billboard\.com/music/country/",
        r"billboard\.com/music/pop/",
        r"billboard\.com/music/rock/",
        r"billboard\.com/music/latin/",
        r"billboard\.com/music/dance-electronic/",
        r"billboard\.com/music/k-pop/",
        # --- Лайфстайл-байоты не про музыку (фермы, дети, свадьбы) ---
        r"\b(farm\s+life|wedding|engagement|baby\s+shower|pregnancy)\b",
    ],
}
