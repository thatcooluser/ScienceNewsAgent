import os

RECIPIENT_EMAIL = os.environ.get("RECIPIENT_EMAIL", "")
SENDER_EMAIL = os.environ.get("GMAIL_SENDER", "")
GMAIL_APP_PASSWORD = os.environ.get("GMAIL_APP_PASSWORD", "")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")

TOPICS = [
    "nuclear fusion", "fusion energy", "plasma", "tokamak", "iter",
    "pharmaceutical", "drug", "clinical trial", "FDA", "medicine", "therapy",
    "biotechnology", "biotech", "CRISPR", "gene editing", "gene therapy", "mRNA",
    "genomics", "protein", "cancer", "vaccine",
    "research", "study", "paper", "scientists", "breakthrough", "discovery",
]

# RSS_FEEDS is a dict of:  "Display Name" -> {"url": ..., "topic_specific": bool}
# topic_specific=True  → always include all articles (feed is already on-topic)
# topic_specific=False → filter by TOPICS keywords
RSS_FEEDS = {
    # --- Nuclear Fusion & Energy ---
    "ScienceDaily – Nuclear Energy": {
        "url": "https://www.sciencedaily.com/rss/matter_energy/nuclear_energy.xml",
        "topic_specific": True,
    },
    "Phys.org – Nuclear": {
        "url": "https://phys.org/rss-feed/physics-news/nuclear/",
        "topic_specific": True,
    },
    "arXiv – Plasma Physics": {
        "url": "https://arxiv.org/rss/physics.plasm-ph",
        "topic_specific": True,
    },

    # --- Pharmaceuticals ---
    "ScienceDaily – Pharmacology": {
        "url": "https://www.sciencedaily.com/rss/health_medicine/pharmacology.xml",
        "topic_specific": True,
    },
    "ScienceDaily – Drug Discovery": {
        "url": "https://www.sciencedaily.com/rss/health_medicine/diseases_conditions.xml",
        "topic_specific": True,
    },

    # --- Biotechnology ---
    "ScienceDaily – Biotechnology": {
        "url": "https://www.sciencedaily.com/rss/plants_animals/biotechnology.xml",
        "topic_specific": True,
    },
    "arXiv – Quantitative Biology": {
        "url": "https://arxiv.org/rss/q-bio.GN",
        "topic_specific": True,
    },

    # --- Broad science & tech (keyword-filtered) ---
    "MIT Technology Review": {
        "url": "https://www.technologyreview.com/feed/",
        "topic_specific": False,
    },
    "WIRED – Science": {
        "url": "https://www.wired.com/feed/category/science/latest/rss",
        "topic_specific": False,
    },
    "The Economist – Science & Technology": {
        "url": "https://www.economist.com/science-and-technology/rss.xml",
        "topic_specific": False,
    },
    "Science Magazine – News": {
        "url": "https://www.science.org/rss/news_current.xml",
        "topic_specific": False,
    },
    "Quanta Magazine": {
        "url": "https://api.quantamagazine.org/feed/",
        "topic_specific": False,
    },
    "The Guardian – Science": {
        "url": "https://www.theguardian.com/science/rss",
        "topic_specific": False,
    },
    "Ars Technica – Science": {
        "url": "https://feeds.arstechnica.com/arstechnica/science",
        "topic_specific": False,
    },
    "Science News": {
        "url": "https://www.sciencenews.org/feed",
        "topic_specific": False,
    },
    "Physics World": {
        "url": "https://physicsworld.com/feed/",
        "topic_specific": False,
    },
    "New Scientist": {
        "url": "https://www.newscientist.com/feed/home/",
        "topic_specific": False,
    },
}

# How many articles to fetch per source (keep low to save tokens)
MAX_ARTICLES_PER_SOURCE = 3

# Only look at articles from the past N days
LOOKBACK_DAYS = 30

# OpenAI model — gpt-4o-mini is cheapest, ~$0.15/1M input tokens
OPENAI_MODEL = "gpt-4o-mini"
