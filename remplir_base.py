from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base, GrammaticalAnalysis  # Ceci doit maintenant fonctionner

# Connexion à la base de données SQLite
SQLALCHEMY_DATABASE_URL = "sqlite:///./latin_analysis.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Insérer des mots dans la base de données
def remplir_base():
    session = SessionLocal()

    # Liste des mots à insérer
    mots = [
    {'latin': 'profuit', 'categorie': 'Verbe', 'fonction': '3e personne du singulier (parfait)', 'relation': 'Verbe principal', 'racine': 'prodesse', 'sens': 'a été utile', 'derive': 'profitable'},
    {'latin': 'suppositumque', 'categorie': 'Adjectif', 'fonction': 'Accusatif singulier', 'relation': 'Complément direct', 'racine': 'supponere', 'sens': 'placé en dessous', 'derive': 'supposition'}
]




    # Ajouter chaque mot à la base de données
    for mot in mots:
        nouveau_mot = GrammaticalAnalysis(
            latin=mot['latin'],
            categorie=mot['categorie'],
            fonction=mot['fonction'],
            relation=mot['relation'],
            racine=mot['racine'],
            sens=mot['sens'],
            derive=mot['derive']
        )
        session.add(nouveau_mot)

    # Sauvegarder les changements dans la base de données
    session.commit()
    session.close()

# Exécuter le remplissage de la base
if __name__ == '__main__':
    remplir_base()
