import pandas as pd
import re

class JobCleaner:
    def __init__(self):
        # Mots-clés pour valider que l'offre est bien dans le domaine Data
        self.data_keywords = [
            'data', 'données', 'analyst', 'scientist', 'engineer', 
            'intelligence artificielle', 'ia', 'ai', 'bi', 'business intelligence',
            'machine learning', 'python', 'sql', 'statist'
        ]

    def clean(self, df):
        """Lance tout le processus de nettoyage sur le DataFrame"""
        if df.empty:
            print("⚠️ DataFrame vide, rien à nettoyer.")
            return df
        
        initial_count = len(df)
        
        # 1. Suppression des doublons (Titre + Entreprise)
        # On garde la première occurrence (souvent la source la plus fraîche)
        df = df.drop_duplicates(subset=['job_title', 'company'], keep='first')

        # 2. Nettoyage des colonnes texte
        df['job_title'] = df['job_title'].apply(self._clean_string)
        df['company'] = df['company'].apply(self._clean_string)
        df['location'] = df['location'].apply(self._clean_string)

        # 3. Filtrage par pertinence (Data Only)
        # On ne garde que les lignes dont le titre contient un de nos mots-clés
        mask = df['job_title'].str.contains('|'.join(self.data_keywords), case=False, na=False)
        df = df[mask].copy()

        # 4. Gestion des valeurs manquantes
        df['description'] = df['description'].fillna('Pas de description disponible')
        df['url'] = df['url'].fillna('#')
        
        # 5. Harmonisation de la casse (Tout en titre pour faire propre)
        df['job_title'] = df['job_title'].str.title()
        df['company'] = df['company'].str.upper()

        final_count = len(df)
        print(f"🧹 Nettoyage terminé : {initial_count} -> {final_count} offres conservées.")
        
        return df

    def _clean_string(self, text):
        """Nettoie une chaîne de caractères : HTML, espaces, caractères spéciaux"""
        if not isinstance(text, str) or text == 'N/A':
            return "Non spécifié"
        
        # Supprimer les balises HTML (ex: <b>...</b>)
        text = re.sub(r'<.*?>', '', text)
        
        # Supprimer les caractères spéciaux bizarres mais garder les accents
        text = re.sub(r'[^\w\s\-\.\(\)\/]', '', text)
        
        # Supprimer les espaces multiples
        text = " ".join(text.split())
        
        return text.strip()