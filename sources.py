"""
RSS-источники по категориям. lang='ru' — не переводим, 'en' — переводим через Google.
"""

SOURCES = {
    "ai": {
        "emoji": "🤖",
        "title": "Нейросети и ИИ",
        "feeds": [
            {"name": "Habr AI",            "url": "https://habr.com/ru/rss/hub/artificial_intelligence/all/?fl=ru", "lang": "ru"},
            {"name": "Habr ML",            "url": "https://habr.com/ru/rss/hub/machine_learning/all/?fl=ru",         "lang": "ru"},
            {"name": "OpenAI",             "url": "https://openai.com/news/rss.xml",                                 "lang": "en"},
            {"name": "Google AI",          "url": "https://blog.google/technology/ai/rss/",                          "lang": "en"},
            {"name": "DeepMind",           "url": "https://deepmind.google/blog/rss.xml",                            "lang": "en"},
            {"name": "MIT Tech Review AI", "url": "https://www.technologyreview.com/topic/artificial-intelligence/feed", "lang": "en"},
            {"name": "VentureBeat AI",     "url": "https://venturebeat.com/category/ai/feed/",                       "lang": "en"},
            {"name": "The Verge AI",       "url": "https://www.theverge.com/ai-artificial-intelligence/rss/index.xml", "lang": "en"},
        ],
    },
    "music": {
        "emoji": "🎵",
        "title": "Музыка",
        "feeds": [
            {"name": "The Flow",          "url": "https://the-flow.ru/feed",                                 "lang": "ru"},
            {"name": "Афиша Daily",       "url": "https://daily.afisha.ru/music/rss/",                       "lang": "ru"},
            {"name": "Pitchfork",         "url": "https://pitchfork.com/feed/feed-news/rss",                 "lang": "en"},
            {"name": "Mixmag",            "url": "https://mixmag.net/rss.xml",                               "lang": "en"},
            {"name": "Resident Advisor",  "url": "https://ra.co/xml/rss.xml",                                "lang": "en"},
            {"name": "Billboard",         "url": "https://www.billboard.com/feed/",                          "lang": "en"},
            {"name": "Rolling Stone",     "url": "https://www.rollingstone.com/music/music-news/feed/",      "lang": "en"},
            {"name": "Consequence",       "url": "https://consequence.net/feed/",                            "lang": "en"},
        ],
    },
    "design": {
        "emoji": "🎨",
        "title": "Дизайн и искусство",
        "feeds": [
            {"name": "Designcollector",   "url": "https://designcollector.net/feed",       "lang": "ru"},
            {"name": "It's Nice That",    "url": "https://www.itsnicethat.com/rss",        "lang": "en"},
            {"name": "Smashing Magazine", "url": "https://www.smashingmagazine.com/feed/", "lang": "en"},
            {"name": "Creative Boom",     "url": "https://www.creativeboom.com/feed/",     "lang": "en"},
            {"name": "Designer News",     "url": "https://www.designernews.co/?format=rss","lang": "en"},
            {"name": "Hyperallergic",     "url": "https://hyperallergic.com/feed/",        "lang": "en"},
            {"name": "Artnet News",       "url": "https://news.artnet.com/feed",           "lang": "en"},
            {"name": "Colossal",          "url": "https://www.thisiscolossal.com/feed/",   "lang": "en"},
        ],
    },
    "economy": {
        "emoji": "💰",
        "title": "Экономика, финансы, крипта",
        "feeds": [
            # Русские
            {"name": "RBC",              "url": "https://rssexport.rbc.ru/rbcnews/news/20/full.rss", "lang": "ru"},
            {"name": "Forbes.ru",        "url": "https://www.forbes.ru/newrss.xml",                  "lang": "ru"},
            {"name": "ForkLog",          "url": "https://forklog.com/feed",                          "lang": "ru"},
            {"name": "Bits.media",       "url": "https://bits.media/rss/news/",                      "lang": "ru"},
            {"name": "Cointelegraph RU", "url": "https://ru.cointelegraph.com/rss",                  "lang": "ru"},
            # Зарубежные
            {"name": "CoinDesk",         "url": "https://www.coindesk.com/arc/outboundfeeds/rss/",   "lang": "en"},
            {"name": "Decrypt",          "url": "https://decrypt.co/feed",                           "lang": "en"},
            {"name": "The Block",        "url": "https://www.theblock.co/rss.xml",                   "lang": "en"},
            {"name": "CNBC Business",    "url": "https://search.cnbc.com/rs/search/combinedcms/view.xml?partnerId=wrss01&id=10001147", "lang": "en"},
        ],
    },
}

# Сколько постов публиковать в день на категорию
POSTS_PER_CATEGORY = 3

# Сколько часов назад максимум могла выйти новость, чтобы она считалась свежей
FRESHNESS_HOURS = 30
