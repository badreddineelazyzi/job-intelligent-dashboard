import os
import sys

# Ajoute la racine du projet au PATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from database.db_session import engine
from database.models import Base
# ... le reste de ton code

def init_database():
    print("🎬 Création des tables dans le Data Warehouse...")
    try:
        # Cette ligne crée toutes les tables définies dans models.py
        Base.metadata.create_all(bind=engine)
        print("🚀 [SUCCESS] Les tables fact_jobs et dimensions ont été créées.")
    except Exception as e:
        print(f"❌ [ERROR] Erreur lors de l'initialisation : {e}")

if __name__ == "__main__":
    init_database()