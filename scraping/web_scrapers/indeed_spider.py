import requests
import time
from bs4 import BeautifulSoup
from settings import SCRAPING_SETTINGS

def scrape_indeed(keyword="data", location="France"):
    url = f"https://fr.indeed.com/jobs?q={keyword}&l={location}"
    
    try:
        # On ajoute un délai pour simuler un humain (configuré dans settings.py)
        time.sleep(SCRAPING_SETTINGS["delay"])
        
        response = requests.get(url, headers=SCRAPING_SETTINGS["headers"])
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Indeed change souvent ses classes CSS pour bloquer le scraping
        # Ici structure simplifiée
        return f"Page Indeed récupérée avec succès (Statut: {response.status_code})"
    except Exception as e:
        return f"Erreur Indeed: {e}"