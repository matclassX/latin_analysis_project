from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import GrammaticalAnalysis

# Connexion à la base de données SQLite
SQLALCHEMY_DATABASE_URL = "sqlite:///./latin_analysis.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Fonction pour modifier la colonne 'derive' pour un mot spécifique
def modifier_derive(mot, nouvelle_derive):
    session = SessionLocal()
    # Modifier la colonne 'derive' pour le mot donné
    session.query(GrammaticalAnalysis).filter(GrammaticalAnalysis.latin == mot).update({"derive": nouvelle_derive})
    session.commit()
    session.close()

# Exécuter la modification pour 'esse'
if __name__ == '__main__':
    modifier_derive("sunt", "essentiel")
