import pandas as pd
import os

class JobNormalizer:
    def __init__(self):
        self.standard_columns = [
            'job_title', 'company', 'location', 'source', 
            'url', 'description', 'date_extracted'
        ]

    def normalize(self, raw_data):
        """Méthode principale pour le JSON (Scraping)"""
        all_jobs = []
        extraction_date = raw_data.get("metadata", {}).get("date", "N/A")
        jobs_dict = raw_data.get("jobs", {})

        for source, jobs in jobs_dict.items():
            if not isinstance(jobs, list): continue
            for item in jobs:
                all_jobs.append({
                    'job_title': item.get('title', 'N/A'),
                    'company': self._extract_company(item, source),
                    'location': self._extract_location(item, source),
                    'source': source,
                    'url': item.get('link') or item.get('url') or item.get('redirect_url'),
                    'description': item.get('description') or item.get('snippet') or "",
                    'date_extracted': extraction_date
                })
        return pd.DataFrame(all_jobs)

    def normalize_dataset(self, df, source_name):
        """Méthode pour normaliser un DataFrame issu d'un CSV (Datasets)"""
        df_norm = pd.DataFrame()
        # Mapping flexible pour s'adapter à tes différents CSV
        df_norm['job_title'] = df.get('job_title') or df.get('title') or df.get('Poste')
        df_norm['company'] = df.get('company') or df.get('entreprise') or df.get('Entreprise')
        df_norm['location'] = df.get('location') or df.get('ville') or "Maroc"
        df_norm['source'] = source_name
        df_norm['url'] = df.get('url') or df.get('link') or "N/A"
        df_norm['description'] = df.get('description') or ""
        df_norm['date_extracted'] = "Dataset_Reference"
        
        # On s'assure que toutes les colonnes standard sont présentes
        for col in self.standard_columns:
            if col not in df_norm.columns:
                df_norm[col] = "N/A"
                
        return df_norm[self.standard_columns]

    def _extract_company(self, item, source):
        if source == "adzuna" and isinstance(item.get('company'), dict):
            return item.get('company', {}).get('display_name', 'N/A')
        return item.get('company', 'N/A')

    def _extract_location(self, item, source):
        if source == "adzuna" and isinstance(item.get('location'), dict):
            return item.get('location', {}).get('display_name', 'N/A')
        return item.get('location', 'N/A')