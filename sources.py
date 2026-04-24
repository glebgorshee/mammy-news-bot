"""
RSS-источники по категориям. lang='ru' — не переводим, 'en' — переводим через Google.
"""

SOURCES = {
    "ai": {
        "emoji": "🤖",
        "title": "Нейросети и ИИ",
        "hashtag": "#нейросети",
        "feeds": [
            {"name": "Habr AI",            "url": "https://habr.com/ru/rss/hub/artificial_intelligence/all/?fl=ru", "lang": "ru"},
            {"name": "Habr ML",            "url": "https://habr.com/ru/rss/hub/machine_learning/all/?fl=ru",         "lang": "ru"},
            {"name": "OpenAI",             "url": "https://openai.com/news/rss.xml",                                 "lang": "en"},
            {"name": "Google AI",          "url": "https://blog.google/technology/ai/rss/",                          "lang": "en"},
            {"name": "DeepMind",           "url": "https://deepmind.google/blog/rss.xml",                            "lang": "en"},
            {"name": "MIT Tech Review AI", "url": "https://www.technologyreview.com/topic/artificial-intelligence/feed", "lang": "en"},
            {"name": "Ars Technica AI",    "url": "https://arstechnica.com/ai/feed/",                                "lang": "en"},
            {"name": "TechCrunch AI",      "url": "https://techcrunch.com/category/artificial-intelligence/feed/",   "lang": "en"},
            {"name": "The Verge",          "url": "https://www.theverge.com/rss/index.xml",                          "lang": "en"},
        ],
    },
    "hiphop": {
        "emoji": "🎤",
        "title": "Хип-хоп и рэп",
        "hashtag": "#хипхоп",
        "feeds": [
            {"name": "InterMedia",      "url": "https://www.intermedia.ru/rss/news.xml",    "lang": "ru"},
            {"name": "XXL Magazine",    "url": "https://www.xxlmag.com/feed/",              "lang": "en"},
            {"name": "HotNewHipHop",    "url": "https://www.hotnewhiphop.com/feed",         "lang": "en"},
            {"name": "Pitchfork News",  "url": "https://pitchfork.com/rss/news/",           "lang": "en"},
            {"name": "The Fader",       "url": "https://www.thefader.com/feed",             "lang": "en"},
            {"name": "Billboard",       "url": "https://www.billboard.com/feed/",           "lang": "en"},
        ],
    },
    "street": {
        "emoji": "🎨",
        "title": "Стритвир, дизайн, искусство",
        "hashtag": "#стритвир",
        "feeds": [
            {"name": "The Blueprint",        "url": "https://theblueprint.ru/rss",                      "lang": "ru"},
            {"name": "Hypebeast",            "url": "https://hypebeast.com/feed",                       "lang": "en"},
            {"name": "Highsnobiety",         "url": "https://www.highsnobiety.com/feed/",               "lang": "en"},
            {"name": "Dezeen",               "url": "https://www.dezeen.com/feed/",                     "lang": "en"},
            {"name": "Designboom",           "url": "https://www.designboom.com/feed/",                 "lang": "en"},
            {"name": "Dazed",                "url": "https://www.dazeddigital.com/rss",                 "lang": "en"},
            {"name": "Wallpaper",            "url": "https://www.wallpaper.com/rss",                    "lang": "en"},
            {"name": "Architectural Digest", "url": "https://www.architecturaldigest.com/feed/rss",     "lang": "en"},
            {"name": "Juxtapoz",             "url": "https://www.juxtapoz.com/feed/",                   "lang": "en"},
            {"name": "Colossal",             "url": "https://www.thisiscolossal.com/feed/",             "lang": "en"},
            {"name": "Hyperallergic",        "url": "https://hyperallergic.com/feed/",                  "lang": "en"},
        ],
    },
    "russia": {
        "emoji": "🇷🇺",
        "title": "Россия",
        "hashtag": "#россия",
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
        "feeds": [
            {"name": "RBC",              "url": "https://rssexport.rbc.ru/rbcnews/news/30/full.rss",     "lang": "ru"},
            {"name": "Коммерсантъ",      "url": "https://www.kommersant.ru/RSS/section-economics.xml",   "lang": "ru"},
            {"name": "Forbes.ru",        "url": "https://www.forbes.ru/newrss.xml",                      "lang": "ru"},
            {"name": "ForkLog",          "url": "https://forklog.com/feed",                              "lang": "ru"},
            {"name": "Incrypted",        "url": "https://incrypted.com/feed/",                           "lang": "ru"},
            {"name": "CoinDesk",         "url": "https://www.coindesk.com/arc/outboundfeeds/rss/",       "lang": "en"},
            {"name": "Decrypt",          "url": "https://decrypt.co/feed",                               "lang": "en"},
            {"name": "The Block",        "url": "https://www.theblock.co/rss.xml",                       "lang": "en"},
            {"name": "CNBC Business",    "url": "https://search.cnbc.com/rs/search/combinedcms/view.xml?partnerId=wrss01&id=10001147", "lang": "en"},
        ],
    },
}

# Сколько постов публиковать за один прогон на категорию
# 3 прогона в день × 1 пост = 3 новости в каждой категории в день
POSTS_PER_CATEGORY = 1

# Насколько свежими должны быть новости (часы)
FRESHNESS_HOURS = 24
