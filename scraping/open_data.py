import pandas as pd
import requests
from io import BytesIO
import urllib3

# Désactive les avertissements de sécurité dans la console
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def fetch_france_travail_stats():
    url_stable = "https://www.data.gouv.fr/api/1/datasets/r/b161754a-6d59-4bf1-85ef-7906d71a7a85"
    
    try:
        print("⏳ Téléchargement des données France Travail (SSL Bypass)...")
        
        # AJOUT DE verify=False ICI
        response = requests.get(url_stable, verify=False, timeout=15)
        response.raise_for_status()
        
        # Lecture du fichier Excel
        df = pd.read_excel(BytesIO(response.content))
        
        print(f"✅ Données récupérées : {len(df)} lignes trouvées.")
        return df
        
    except Exception as e:
        print(f"❌ Erreur Open Data : {e}")
        return None

if __name__ == "__main__":
    data = fetch_france_travail_stats()
    if data is not None:
        print(data.head())