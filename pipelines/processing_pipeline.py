import os
import sys
import json
import pandas as pd
import logging
from datetime import datetime

# 1. CONFIGURATION DU PATH ET DES LOGS
# On remonte de 'pipelines/' vers la racine du projet
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Création du dossier logs s'il n'existe pas
log_dir = os.path.join(project_root, "logs")
os.makedirs(log_dir, exist_ok=True)

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(log_dir, "processing.log"), encoding='utf-8'),
        logging.StreamHandler()
    ]
)

# Imports des modules de traitement (Dossier processing/)
try:
    from processing.normalizer import JobNormalizer
    from processing.cleaner import JobCleaner
    from processing.validators import JobValidator
except ImportError as e:
    logging.critical(f"❌ Impossible d'importer les modules de traitement : {e}")
    sys.exit(1)

def run_processing():
    logging.info("🚀 [PIPELINE PROCESSING] Démarrage de l'unification...")
    
    try:
        # Initialisation des outils
        normalizer = JobNormalizer()
        cleaner = JobCleaner()
        validator = JobValidator()
        
        all_dataframes = []

        # --- ÉTAPE 1 : RÉCUPÉRATION DES DONNÉES (RAW & DATASETS) ---

        # A. Traitement du Scraping (JSON)
        raw_dir = os.path.join(project_root, "data", "raw")
        if os.path.exists(raw_dir):
            try:
                json_files = [f for f in os.listdir(raw_dir) if f.endswith('.json')]
                if json_files:
                    # On prend le fichier le plus récent
                    latest_json = max(json_files, key=lambda x: os.path.getctime(os.path.join(raw_dir, x)))
                    logging.info(f"📦 Normalisation du dernier scraping : {latest_json}")
                    
                    with open(os.path.join(raw_dir, latest_json), 'r', encoding='utf-8') as f:
                        raw_data = json.load(f)
                        df_scraping = normalizer.normalize(raw_data)
                        if not df_scraping.empty:
                            all_dataframes.append(df_scraping)
                else:
                    logging.warning("⚠️ Aucun fichier JSON trouvé dans data/raw")
            except Exception as e:
                logging.error(f"❌ Erreur lors de la normalisation du JSON : {e}")

        # B. Traitement des Datasets Externes (CSV)
        datasets_dir = os.path.join(project_root, "datasets")
        if os.path.exists(datasets_dir):
            try:
                csv_files = [f for f in os.listdir(datasets_dir) if f.endswith('.csv')]
                for csv_file in csv_files:
                    logging.info(f"📄 Normalisation du dataset : {csv_file}")
                    path = os.path.join(datasets_dir, csv_file)
                    try:
                        df_raw_csv = pd.read_csv(path)
                        df_norm_csv = normalizer.normalize_dataset(df_raw_csv, csv_file)
                        if not df_norm_csv.empty:
                            all_dataframes.append(df_norm_csv)
                    except Exception as csv_err:
                        logging.error(f"❌ Erreur sur le fichier {csv_file}: {csv_err}")
            except Exception as e:
                logging.error(f"❌ Erreur dossier datasets : {e}")

        # --- ÉTAPE 2 : FUSION, NETTOYAGE ET VALIDATION ---

        if all_dataframes:
            # 1. Fusion (Union)
            merged_df = pd.concat(all_dataframes, ignore_index=True)
            logging.info(f"🔗 Fusion terminée : {len(merged_df)} lignes collectées.")

            # 2. Nettoyage (Cleaning)
            logging.info("🧹 Lancement du nettoyage (JobCleaner)...")
            cleaned_df = cleaner.clean(merged_df)

            # 3. Validation (Validation métier)
            logging.info("⚖️ Lancement de la validation (JobValidator)...")
            final_df = validator.validate(cleaned_df)

            # Vérification finale du schéma
            if not validator.check_schema(final_df):
                logging.error("❌ Le schéma final est invalide. Arrêt du pipeline.")
                return

            # --- ÉTAPE 3 : EXPORTATION ---

            output_dir = os.path.join(project_root, "data", "processed")
            os.makedirs(output_dir, exist_ok=True)
            
            # Sauvegarde avec Timestamp (Historique)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M")
            output_name = f"unified_job_market_{timestamp}.csv"
            output_path = os.path.join(output_dir, output_name)
            
            # Sauvegarde "Latest" (Pour Power BI / Database)
            latest_path = os.path.join(output_dir, "unified_job_market_latest.csv")

            final_df.to_csv(output_path, index=False, encoding='utf-8-sig')
            final_df.to_csv(latest_path, index=False, encoding='utf-8-sig')

            logging.info(f"✨ TERMINÉ : {len(final_df)} offres prêtes et validées.")
            logging.info(f"📂 Fichier disponible : {latest_path}")
            
        else:
            logging.warning("⚠️ Aucune donnée disponible pour le traitement.")

    except Exception as global_err:
        logging.critical(f"💥 Erreur fatale du pipeline : {global_err}")

if __name__ == "__main__":
    run_processing()