import os
import sys
import json
import pandas as pd
import logging
from datetime import datetime
import boto3
from io import StringIO, BytesIO

# Config pour Windows (Localhost) ou Docker (minio-job)
MINIO_URL = os.getenv("MINIO_ENDPOINT_URL", "http://localhost:9000")
S3_CLIENT = boto3.client(
    's3',
    endpoint_url=MINIO_URL,
    aws_access_key_id='admin',
    aws_secret_access_key='password123',
    region_name='us-east-1'
)

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

        # --- ÉTAPE 1 : RÉCUPÉRATION DEPUIS MINIO (RAW) ---
        response = S3_CLIENT.list_objects_v2(Bucket="raw-data")
        if 'Contents' in response:
            # Récupère le fichier le plus récent
            latest_file = max(response['Contents'], key=lambda x: x['LastModified'])
            obj = S3_CLIENT.get_object(Bucket="raw-data", Key=latest_file['Key'])
            raw_data = json.load(obj['Body'])
            
            logging.info(f"📦 Lecture MinIO : {latest_file['Key']}")
            df_scraping = normalizer.normalize(raw_data)
            if not df_scraping.empty:
                all_dataframes.append(df_scraping)

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

            # --- ÉTAPE 3 : SAUVEGARDE VERS MINIO (PROCESSED) ---
            csv_buffer = StringIO()
            final_df.to_csv(csv_buffer, index=False, encoding='utf-8-sig')
            
            # Sauvegarde 'Latest' pour la suite du pipeline
            S3_CLIENT.put_object(
                Bucket="processed-data",
                Key="unified_job_market_latest.csv",
                Body=csv_buffer.getvalue(),
                ContentType='text/csv'
            )
            
            logging.info("✨ TERMINÉ : Fichier sauvegardé dans le bucket 'processed-data'")
            
        else:
            logging.warning("⚠️ Aucune donnée disponible pour le traitement.")

    except Exception as global_err:
        logging.critical(f"💥 Erreur fatale du pipeline : {global_err}")

if __name__ == "__main__":
    run_processing()