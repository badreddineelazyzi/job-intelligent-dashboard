import os
import sys
import pandas as pd
import boto3
import logging
from io import BytesIO
from sqlalchemy.orm import sessionmaker
from datetime import datetime

# Configuration du PATH pour importer 'database'
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from database.db_session import engine
from database.models import FactJobs, DimCompany, DimLocation, DimTime, DimCategory, DimSkills

# Configuration Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Configuration MinIO
MINIO_URL = os.getenv("MINIO_ENDPOINT_URL", "http://localhost:9000")
s3_client = boto3.client('s3', endpoint_url=MINIO_URL, aws_access_key_id='admin', aws_secret_access_key='password123')

def get_or_create(session, model, **kwargs):
    """Vérifie si une entrée existe en DB, sinon la crée et retourne l'objet."""
    instance = session.query(model).filter_by(**kwargs).first()
    if not instance:
        instance = model(**kwargs)
        session.add(instance)
        session.flush()  # Pour récupérer l'ID immédiatement
    return instance

def run_export():
    logging.info("📤 [EXPORT PIPELINE] Début de l'export vers PostgreSQL...")
    
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        # 1. Lire le dernier CSV depuis MinIO
        obj = s3_client.get_object(Bucket="processed-data", Key="unified_job_market_latest.csv")
        df = pd.read_csv(BytesIO(obj['Body'].read()))
        logging.info(f"📄 CSV chargé : {len(df)} lignes à traiter.")

        for _, row in df.iterrows():
            # 2. Gérer les Dimensions
            # On utilise .get() pour éviter que le script crash si une colonne manque
            company_name = row.get('company') or row.get('company_name') or "Inconnu"
            location_name = row.get('location') or row.get('city') or "France"
            
            company = get_or_create(session, DimCompany, company_name=str(company_name))
            location = get_or_create(session, DimLocation, city=str(location_name), country="France")
            category = get_or_create(session, DimCategory, category_name="Data Science")
            
            job_date = datetime.now()
            time_dim = get_or_create(session, DimTime, 
                                     date=job_date.date(),
                                     day=job_date.day, 
                                     month=job_date.month, 
                                     year=job_date.year)

            # 3. Créer le Fait (FactJobs)
            # --- CHANGEMENT ICI : job_title au lieu de title ---
            exists = session.query(FactJobs).filter_by(url=row['url']).first()
            if not exists:
                new_job = FactJobs(
                    title=row['job_title'],  # <--- Correction faite ici
                    description=row.get('description', ''),
                    salary_min=row.get('salary_min', 0),
                    salary_max=row.get('salary_max', 0),
                    source=row.get('source', 'unknown'),
                    url=row['url'],
                    company_id=company.company_id,
                    location_id=location.location_id,
                    category_id=category.category_id,
                    date_id=time_dim.date_id
                )
                
                # 4. Gérer les Skills
                if 'skills' in row and pd.notna(row['skills']):
                    skill_list = str(row['skills']).split(',')
                    for s in skill_list:
                        skill_name = s.strip()
                        if skill_name:
                            skill_obj = get_or_create(session, DimSkills, skill_name=skill_name)
                            new_job.skills.append(skill_obj)

                session.add(new_job)

        session.commit()
        logging.info("✨ [SUCCESS] Données exportées avec succès dans le schéma en étoile !")

    except Exception as e:
        session.rollback()
        logging.error(f"❌ Erreur lors de l'export : {e}")
    finally:
        session.close()

if __name__ == "__main__":
    run_export()