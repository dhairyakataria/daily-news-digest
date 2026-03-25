TOPICS = [
    {
        "name": "World News",
        "gnews_topic": "world",
        # Broad world events — wars, disasters, summits, global crises
        "search_query": "war conflict crisis disaster humanitarian global summit news today",
    },
    {
        "name": "Technology",
        "gnews_topic": "technology",
        # Hardware, software, startups, big tech — not AI (covered separately)
        "search_query": "Apple Google Microsoft Samsung smartphone chip semiconductor startup tech news today",
    },
    {
        "name": "Sports",
        "gnews_topic": "sports",
        "search_query": "cricket football tennis IPL Premier League sports results today",
    },
    {
        "name": "India",
        "gnews_topic": "nation",
        "gnews_country": "in",
        # General India news — economy, society, infrastructure, not politics (covered separately)
        "search_query": "india economy infrastructure rupee GDP unemployment social news today",
    },
    {
        "name": "Geopolitics",
        "gnews_topic": None,
        # Focus on country-to-country relations, alliances, sanctions — distinct from world events
        "search_query": "US China Russia NATO sanctions treaty alliance trade war bilateral geopolitics",
        "gnews_search_query": "geopolitics",  # short fallback for GNews
    },
    {
        "name": "Politics",
        "gnews_topic": None,
        # Indian domestic politics only — parties, elections, parliament
        "search_query": "BJP Congress Modi parliament election state government India politics",
        "gnews_search_query": "BJP Modi India parliament",  # short fallback for GNews
    },
    {
        "name": "Indian Stock Market",
        "gnews_topic": None,
        "search_query": "NSE BSE Nifty Sensex Indian stock market",
        "gnews_search_query": "Nifty Sensex stock market",  # short fallback for GNews
    },
    {
        "name": "Global Markets",
        "gnews_topic": "business",
        # International finance — not Indian market (covered separately)
        "search_query": "S&P500 Dow Nasdaq Fed interest rate dollar euro oil gold commodities global market",
    },
    {
        "name": "AI & Machine Learning",
        "gnews_topic": None,
        "search_query": "artificial intelligence AI OpenAI Anthropic Google DeepMind news",
        "gnews_search_query": "artificial intelligence OpenAI",  # short fallback for GNews
    },
]
