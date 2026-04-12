# settings.py
# -----------------------------
# Configuration des API et scraping pour le projet Job-Intelligent-Dashboard

# -----------------------------
# Clés API
API_KEYS = {
    "adzuna": {
        "app_id": "d7095dc1",
        "app_key": "2163b239c6b939f0395ec3c58cf23a75"
    },
    "jooble": {
        "api_key": "1d130e18-2d6b-43cd-8e8a-918f47b3eb0c"
    },
    "usajobs": {
        "user_agent": "wissalselmane1@gmail.com",  # requis par USAJobs
        "api_key": "pNDUdbDbGOL7el3d1N/Go6/1htQYwDELw1iH5CnbIvc"
    }
}

# -----------------------------
# Endpoints API
API_ENDPOINTS = {
    "adzuna": "https://api.adzuna.com/v1/api/jobs/fr/search/1",
    "jooble": "https://jooble.org/api/",
    "usajobs": "https://data.usajobs.gov/api/search"
}

# -----------------------------
# Paramètres scraping
# -----------------------------
# Paramètres scraping
SCRAPING_SETTINGS = {
    "headers": {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36"
    },
    "delay": 2,      
    "max_pages": 5,  
    "retry": 3,
    # --- AJOUTEZ CECI ---
    "selectors": {
        "rekrute": {
            "container": "li.post-id",
            "title": "h2 a",
            "company": "img.logo"
        },
        "linkedin": {
            "container": "div.base-search-card__info",
            "title": "h3.base-search-card__title",
            "company": "h4.base-search-card__subtitle"
        }
    }
}
# -----------------------------
# Paramètres généraux
GENERAL_SETTINGS = {
    "raw_data_path": "data/raw/",
    "processed_data_path": "data/processed/",
    "export_path": "data/exports/",
    "default_keyword": "data",
    "default_location": "France"
}