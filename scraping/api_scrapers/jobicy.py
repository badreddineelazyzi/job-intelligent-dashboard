import requests

def fetch_jobicy_jobs(keyword="data", location="all"):
    """
    API Jobicy corrigée pour éviter l'erreur 400.
    """
    url = "https://jobicy.com/api/v2/remote-jobs"
    
    # On nettoie le mot-clé (remplacer espaces par %20)
    # Si la localisation est "France" ou "Maroc", Jobicy peut bugger. 
    # On utilise "all" ou on ne met pas le paramètre geo pour tester.
    params = {
        "count": 20,
        "tag": keyword.replace(" ", "-") # Jobicy préfère les tirets pour les tags
    }
    
    # On n'ajoute 'geo' que si c'est une valeur reconnue par Jobicy
    if location.lower() in ['us', 'uk', 'ca', 'de']:
        params["geo"] = location.lower()

    try:
        # Ajout d'un User-Agent basique pour éviter d'être bloqué comme robot
        headers = {
            "User-Agent": "Mozilla/5.0"
        }
        
        response = requests.get(url, params=params, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            jobs = data.get('jobs', [])
            print(f"✅ Jobicy : {len(jobs)} offres récupérées.")
            return jobs
        else:
            # Affichage détaillé pour comprendre pourquoi 400
            print(f"❌ Erreur Jobicy {response.status_code}: {response.text}")
            return []
            
    except Exception as e:
        print(f"⚠️ Erreur Jobicy: {e}")
        return []