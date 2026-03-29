import requests
from bs4 import BeautifulSoup
from scraping.settings import SCRAPING_SETTINGS

def scrape_linkedin(keyword="data", location="France"):
    # Utilisation d'une URL de recherche publique
    url = f"https://www.linkedin.com/jobs/search/?keywords={keyword}&location={location}"
    
    try:
        response = requests.get(url, headers=SCRAPING_SETTINGS["headers"], timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        jobs = []
        # Sélecteur typique pour les cartes d'emploi LinkedIn
        cards = soup.find_all('div', class_='base-search-card__info')
        
        for card in cards:
            job = {
                "title": card.find('h3', class_='base-search-card__title').text.strip(),
                "company": card.find('h4', class_='base-search-card__subtitle').text.strip(),
                "location": card.find('span', class_='job-search-card__location').text.strip(),
                "link": card.parent.find('a', class_='base-card__full-link')['href']
            }
            jobs.append(job)
        return jobs
    except Exception as e:
        print(f"Erreur LinkedIn Spider: {e}")
        return []