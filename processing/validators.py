import pandas as pd
import logging

class JobValidator:
    def __init__(self):
        # Configuration des règles de validation
        self.min_title_length = 5
        self.required_columns = ['job_title', 'company', 'url']

    def validate(self, df):
        """
        Valide le DataFrame et retourne un tuple (df_valide, df_rejete)
        """
        if df.empty:
            return df, df

        logging.info("⚖️ [VALIDATION] Vérification des règles métier...")

        # 1. Vérification des colonnes obligatoires (Supprime les lignes où le titre ou l'entreprise est vide)
        initial_count = len(df)
        df_clean = df.dropna(subset=self.required_columns).copy()

        # 2. Règle : Longueur du titre (Évite les titres type "Data" ou "Job")
        df_clean = df_clean[df_clean['job_title'].str.len() >= self.min_title_length]

        # 3. Règle : Validité de l'URL (Doit commencer par http)
        df_clean = df_clean[df_clean['url'].str.startswith('http', na=False)]

        # 4. Identification des rejets pour le rapport
        valid_count = len(df_clean)
        rejected_count = initial_count - valid_count

        if rejected_count > 0:
            logging.warning(f"🚫 {rejected_count} offres rejetées par la validation (données incomplètes ou invalides).")
        
        logging.info(f"✅ {valid_count} offres validées avec succès.")
        
        return df_clean

    def check_schema(self, df):
        """Vérifie si toutes les colonnes attendues par le Data Warehouse sont présentes"""
        expected_columns = [
            'job_title', 'company', 'location', 'source', 
            'url', 'description', 'date_extracted'
        ]
        missing = [col for col in expected_columns if col not in df.columns]
        if missing:
            logging.error(f"❌ Schéma invalide ! Colonnes manquantes : {missing}")
            return False
        return True