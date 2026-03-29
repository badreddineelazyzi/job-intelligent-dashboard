import os
import sys
import json
from datetime import datetime

# Détermination de la racine du projet
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# CRUCIAL : On insère la racine en POSITION 0
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Maintenant, on importe TOUT via le préfixe 'scraping.'
from scraping.api_scrapers.adzuna import fetch_adzuna_jobs
from scraping.api_scrapers.jooble import fetch_jooble_jobs
from scraping.api_scrapers.jobicy import fetch_jobicy_jobs
from scraping.web_scrapers.linkedin_spider import scrape_linkedin
from scraping.web_scrapers.rekrute_spider import scrape_rekrute
from scraping.web_scrapers.indeed_spider import scrape_indeed
from scraping.settings import GENERAL_SETTINGS



def save_data(data, filename):
    """Sauvegarde les données dans le dossier raw_data_path défini dans settings.py"""
    path = GENERAL_SETTINGS["raw_data_path"]
    
    # Créer le dossier s'il n'existe pas
    if not os.path.exists(path):
        os.makedirs(path)
    
    full_path = os.path.join(path, filename)
    with open(full_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    print(f"✅ Données sauvegardées dans : {full_path}")

def run_all_scrapers():
    print("🚀 Démarrage du processus de récupération des offres...")
    
    keyword = GENERAL_SETTINGS["default_keyword"]
    location = GENERAL_SETTINGS["default_location"]
    
    results = {
        "metadata": {
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "keyword": keyword,
            "location": location
        },
        "jobs": {}
    }

    # --- 1. Exécution des APIs ---
    print("📡 Interrogation des APIs...")
    results["jobs"]["adzuna"] = fetch_adzuna_jobs(keyword, location)
    results["jobs"]["jooble"] = fetch_jooble_jobs(keyword, location)
    results["jobs"]["jobicy"] = fetch_jobicy_jobs(keyword, "remote") # USAJOBS spécifique US

    # --- 2. Exécution des Spiders Web ---
    print("🕸️ Lancement du Web Scraping (LinkedIn, Rekrute, Indeed)...")
    results["jobs"]["linkedin"] = scrape_linkedin(keyword, location)
    results["jobs"]["rekrute"] = scrape_rekrute(keyword, "Maroc")
    results["jobs"]["indeed"] = scrape_indeed(keyword, location)

    # --- 3. Sauvegarde ---
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"raw_jobs_{timestamp}.json"
    save_data(results, filename)

    print("\n✨ Terminé ! Toutes les sources ont été traitées.")

if __name__ == "__main__":
    run_all_scrapers()