import os
import sys
import json
from datetime import datetime
import boto3
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



def upload_to_minio(data, filename):
    """Envoie les données JSON directement dans le bucket MinIO 'raw-data'"""
    try:
        # Configuration de la connexion MinIO
        # Note : Dans Docker, l'URL est 'http://minio-job:9000'
        # Si tu testes hors Docker, utilise 'http://localhost:9000'
        s3 = boto3.client(
            's3',
            endpoint_url='http://localhost:9000', 
            aws_access_key_id='admin',
            aws_secret_access_key='password123',
            region_name='us-east-1'
        )

        # Conversion du dictionnaire en bytes JSON
        json_data = json.dumps(data, ensure_ascii=False, indent=4).encode('utf-8')
        
        # Envoi vers le bucket 'raw-data'
        bucket_name = "raw-data"
        s3.put_object(
            Bucket=bucket_name,
            Key=filename,
            Body=json_data,
            ContentType='application/json'
        )
        print(f"☁️ ✅ Succès : Données sauvegardées dans MinIO -> {bucket_name}/{filename}")

    except Exception as e:
        print(f"❌ Erreur lors de l'envoi vers MinIO : {e}")

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
    results["jobs"]["jobicy"] = fetch_jobicy_jobs(keyword, "remote") 

    # --- 2. Exécution des Spiders Web ---
    print("🕸️ Lancement du Web Scraping (LinkedIn, Rekrute, Indeed)...")
    results["jobs"]["linkedin"] = scrape_linkedin(keyword, location)
    results["jobs"]["rekrute"] = scrape_rekrute(keyword, "France")
    results["jobs"]["indeed"] = scrape_indeed(keyword, location)

    # --- 3. Sauvegarde dans le Data Lake (MinIO) ---
    timestamp = datetime.now().strftime("%Y/%m/%d/%H%M%S") # Dossiers par date YYYY/MM/DD
    filename = f"{timestamp}_raw_jobs.json"
    
    upload_to_minio(results, filename)

    print("\n✨ Terminé ! Le Data Lake a été mis à jour.")

if __name__ == "__main__":
    run_all_scrapers()