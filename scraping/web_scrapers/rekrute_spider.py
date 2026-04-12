import requests
from bs4 import BeautifulSoup
from scraping.settings import SCRAPING_SETTINGS

def scrape_rekrute(keyword="data", location="France"):
    # Construction de l'URL (exemple simplifié)
    url = f"https://www.rekrute.com/offres.html?s=1&p=1&st=1&keyword={keyword}"
    
    try:
        response = requests.get(url, headers=SCRAPING_SETTINGS["headers"])
        soup = BeautifulSoup(response.text, 'html.parser')
        
        jobs = []
        # Les offres sont souvent dans des balises 'li' avec la classe 'post-id'
        job_listings = soup.find_all('li', class_='post-id')
        
        for item in job_listings:
            job = {
                "title": item.find('h2').text.strip() if item.find('h2') else "N/A",
                "company": item.find('img')['alt'] if item.find('img') else "N/A",
                "link": "https://www.rekrute.com" + item.find('a')['href']
            }
            jobs.append(job)
        return jobs
    except Exception as e:
        print(f"Erreur Rekrute Spider: {e}")
        return []