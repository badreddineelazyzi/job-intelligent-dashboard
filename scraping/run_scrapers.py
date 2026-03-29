import os
import json
from datetime import datetime
import  sys

# On récupère le chemin du dossier 'scraping'
current_dir = os.path.dirname(os.path.abspath(__file__))
# On l'ajoute au système pour que Python cherche les modules ici
if current_dir not in sys.path:
    sys.path.append(current_dir)

# Importation des scrapers d'API
from api_scrapers.adzuna import fetch_adzuna_jobs
from api_scrapers.jooble import fetch_jooble_jobs
from api_scrapers.jobicy import fetch_jobicy_jobs

# Importation des scrapers Web
from web_scrapers.linkedin_spider import scrape_linkedin
from web_scrapers.rekrute_spider import scrape_rekrute
from web_scrapers.indeed_spider import scrape_indeed

# Importation des réglages
from settings import GENERAL_SETTINGS

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