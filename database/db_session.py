from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os

# Dans Docker, utilise le nom du service 'postgres-dw'
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user_dw:password_dw@localhost:5432/job_data_warehouse")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()