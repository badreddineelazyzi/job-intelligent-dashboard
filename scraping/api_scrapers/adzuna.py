import requests
from scraping.settings import API_KEYS, API_ENDPOINTS

def fetch_adzuna_jobs(keyword="data", location="France"):
    conf = API_KEYS["adzuna"]
    url = API_ENDPOINTS["adzuna"]
    
    params = {
        "app_id": conf["app_id"],
        "app_key": conf["app_key"],
        "what": keyword,
        "where": location,
        "content-type": "application/json"
    }
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        return data.get('results', [])
    except Exception as e:
        print(f"Erreur Adzuna: {e}")
        return []