from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Configuration de la base de données SQLite
SQLALCHEMY_DATABASE_URL = "sqlite:///./latin_analysis.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Déclarer le modèle de base
Base = declarative_base()

# Modèle de la table grammatical_analysis
class GrammaticalAnalysis(Base):
    __tablename__ = "grammatical_analysis"
    id = Column(Integer, primary_key=True, index=True)
    latin = Column(String, index=True)
    categorie = Column(String)
    fonction = Column(String)
    relation = Column(String)
    racine = Column(String)
    sens = Column(String)
    derive = Column(String)
