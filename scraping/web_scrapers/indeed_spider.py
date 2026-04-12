import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from scraping.settings import SCRAPING_SETTINGS

def scrape_indeed(keyword="data", location="France"):
    print(f"🔍 [INDEED] Recherche de '{keyword}' à '{location}'...")
    
    # 1. Configuration des options Chrome pour éviter la détection
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Mode sans fenêtre (obligatoire pour Docker/Serveur)
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    # Cache le fait que Selenium pilote le navigateur
    chrome_options.add_argument("--disable-blink-features=AutomationControlled") 
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    # User-Agent réaliste (à récupérer dans tes settings)
    chrome_options.add_argument(f"user-agent={SCRAPING_SETTINGS['headers']['User-Agent']}")

    try:
        # 2. Initialisation du Driver
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
        
        # On injecte un script pour masquer l'attribut 'webdriver' dans le navigateur
        driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
            "source": "const newProto = navigator.__proto__; delete newProto.webdriver; navigator.__proto__ = newProto;"
        })

        url = f"https://fr.indeed.com/jobs?q={keyword}&l={location}"
        driver.get(url)
        
        # 3. Attente aléatoire pour simuler un humain
        time.sleep(SCRAPING_SETTINGS.get("delay", 5)) 

        # 4. Récupération du contenu
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        
        # Vérification sommaire si on a été bloqué par un CAPTCHA
        if "hCaptcha" in driver.page_source or "Cloudflare" in driver.page_source:
             print("⚠️ [INDEED] Bloqué par un CAPTCHA/Cloudflare malgré Selenium.")
             driver.quit()
             return []

        # --- LOGIQUE D'EXTRACTION (Exemple de structure actuelle) ---
        jobs = []
        # Indeed utilise souvent des IDs ou classes génériques type 'jobCard_mainContent'
        job_cards = soup.find_all('div', class_='job_seen_beacon') 

        for card in job_cards:
            title_tag = card.find('h2', class_='jobTitle')
            company_tag = card.find('span', {'data-testid': 'company-name'})
            location_tag = card.find('div', {'data-testid': 'text-location'})
            link_tag = card.find('a', class_='jcs-JobTitle')

            jobs.append({
                "title": title_tag.text.strip() if title_tag else "N/A",
                "company": company_tag.text.strip() if company_tag else "N/A",
                "location": location_tag.text.strip() if location_tag else location,
                "url": "https://fr.indeed.com" + link_tag['href'] if link_tag else "N/A",
                "source": "indeed"
            })

        driver.quit()
        print(f"✅ [INDEED] {len(jobs)} offres récupérées.")
        return jobs

    except Exception as e:
        print(f"❌ [INDEED] Erreur : {e}")
        return []