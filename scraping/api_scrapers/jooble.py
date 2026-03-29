import requests
import json
from scraping.settings import API_KEYS, API_ENDPOINTS

def fetch_jooble_jobs(keyword="data", location="France"):
    key = API_KEYS["jooble"]["api_key"]
    url = f"{API_ENDPOINTS['jooble']}{key}"
    
    body = {
        "keywords": keyword,
        "location": location
    }
    
    try:
        response = requests.post(url, json=body)
        response.raise_for_status()
        data = response.json()
        return data.get('jobs', [])
    except Exception as e:
        print(f"Erreur Jooble: {e}")
        return []