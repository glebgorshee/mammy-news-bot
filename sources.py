"""
RSS-источники по категориям. lang='ru' — не переводим, 'en' — переводим через Google.
Все URL проверены 2026-04-20.
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
    "music": {
        "emoji": "🎵",
        "title": "Музыка",
        "hashtag": "#музыка",
        "feeds": [
            {"name": "InterMedia",        "url": "https://www.intermedia.ru/rss/news.xml",                    "lang": "ru"},
            {"name": "Pitchfork News",    "url": "https://pitchfork.com/rss/news/",                           "lang": "en"},
            {"name": "Pitchfork Reviews", "url": "https://pitchfork.com/feed/feed-news/rss",                  "lang": "en"},
            {"name": "Mixmag",            "url": "https://mixmag.net/rss.xml",                                "lang": "en"},
            {"name": "Billboard",         "url": "https://www.billboard.com/feed/",                           "lang": "en"},
            {"name": "Rolling Stone",     "url": "https://www.rollingstone.com/music/music-news/feed/",       "lang": "en"},
            {"name": "Consequence",       "url": "https://consequence.net/feed/",                             "lang": "en"},
        ],
    },
    "design": {
        "emoji": "🎨",
        "title": "Дизайн и искусство",
        "hashtag": "#дизайн",
        "feeds": [
            {"name": "DesignPub",         "url": "https://designpub.ru/feed",              "lang": "ru"},
            {"name": "Dezeen",            "url": "https://www.dezeen.com/feed/",           "lang": "en"},
            {"name": "Design Week",       "url": "https://www.designweek.co.uk/feed/",     "lang": "en"},
            {"name": "Smashing Magazine", "url": "https://www.smashingmagazine.com/feed/", "lang": "en"},
            {"name": "Hyperallergic",     "url": "https://hyperallergic.com/feed/",        "lang": "en"},
            {"name": "Artnet News",       "url": "https://news.artnet.com/feed",           "lang": "en"},
            {"name": "Colossal",          "url": "https://www.thisiscolossal.com/feed/",   "lang": "en"},
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
# Запусков 3 в день → 3 новости в каждой категории в день
POSTS_PER_CATEGORY = 1

# Насколько свежими должны быть новости (часы)
# Между прогонами 6-8 часов, берём запас
FRESHNESS_HOURS = 10
