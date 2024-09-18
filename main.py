import re
import string
import json
from fastapi import FastAPI, Request, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Configuration de la base de données SQLite
SQLALCHEMY_DATABASE_URL = "sqlite:///./latin_analysis.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
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

# Créer la base de données si elle n'existe pas
Base.metadata.create_all(bind=engine)

# Créer l'application FastAPI
app = FastAPI()

# Dossier où se trouvent les templates HTML
templates = Jinja2Templates(directory="app/templates")

# Charger les phrases à partir du fichier texte lors du démarrage de l'application
def charger_phrases(fichier):
    with open(fichier, 'r', encoding='utf-8') as file:
        texte = file.read()
    # Diviser le texte en phrases en utilisant la ponctuation tout en préservant celle-ci
    phrases = [phrase.strip() for phrase in re.split(r'(?<=[.!?])\s+', texte) if phrase]
    return phrases

# Charger les phrases latines et les traductions
phrases_latines = charger_phrases('satireX.txt')
traductions = charger_phrases('traductions.txt')

# Fonction pour charger les groupes de phrases
def charger_groupes_phrases(fichier):
    with open(fichier, 'r', encoding='utf-8') as file:
        return json.load(file)


# Charger les groupes au démarrage de l'application
groupes_phrases = charger_groupes_phrases('groupes_phrases.json')


# Fonction pour ajouter des infobulles avec les détails des mots
def rendre_mots_avec_bulles(phrase):
    session = SessionLocal()
    mots = session.query(GrammaticalAnalysis).all()
    session.close()

    # Diviser la phrase en mots tout en gardant la ponctuation
    phrase_mots = re.findall(r'\w+|[^\w\s]', phrase)

    # Parcourir chaque mot dans la phrase
    for i, mot_phrase in enumerate(phrase_mots):
        mot_phrase_sans_ponctuation = mot_phrase.strip(string.punctuation)

        # Chercher chaque mot dans la base de données
        for mot in mots:
            mot_latin = mot.latin

            # Si le mot est trouvé, ajouter toutes les informations dans l'infobulle
            if mot_phrase_sans_ponctuation.lower() == mot_latin.lower():
                tooltip_content = (f"Catégorie: {mot.categorie},<br>"
                                   f"Fonction: {mot.fonction},<br>"
                                   f"Relation: {mot.relation},<br>"
                                   f"Racine: {mot.racine},<br>"
                                   f"Sens: {mot.sens},<br>"
                                   f"Dérivé: {mot.derive}")
                
                # Créer le span avec l'infobulle
                phrase_mots[i] = (f'<span class="tooltip-container">'
                                  f'<span>{mot_phrase}</span>'
                                  f'<span class="tooltip">{tooltip_content}</span>'
                                  f'</span>')

    # Rejoindre la phrase modifiée avec des espaces
    return " ".join(phrase_mots)


# Fonction pour colorer les mots selon leur catégorie grammaticale
def colorer_mots_par_categorie(phrase):
    session = SessionLocal()
    mots = session.query(GrammaticalAnalysis).all()
    session.close()

    categories_couleurs = {
        'Nom': 'blue',
        'Verbe': 'green',
        'Adjectif': 'purple',
        'Adverbe': 'orange',
        'Conjonction': 'red',
    }

    phrase_mots = phrase.split()

    for i, mot_phrase in enumerate(phrase_mots):
        mot_phrase_sans_ponctuation = mot_phrase.strip(string.punctuation)
        for mot in mots:
            if mot_phrase_sans_ponctuation.lower() == mot.latin.lower():
                couleur = categories_couleurs.get(mot.categorie.split()[0], 'black')
                phrase_mots[i] = f'<span style="color:{couleur};">{mot_phrase}</span>'

    return " ".join(phrase_mots)

# Route pour afficher la liste des phrases
@app.get("/liste", response_class=HTMLResponse)
def liste_phrases(request: Request):
    extraits = []
    for i, phrase in enumerate(phrases_latines):
        extrait = " ".join(phrase.split()[:3]) + "..."
        extraits.append((i + 1, extrait))

    return templates.TemplateResponse("liste.html", {"request": request, "extraits": extraits})

@app.get("/groupe/{numero_groupe}", response_class=HTMLResponse)
def afficher_groupe(request: Request, numero_groupe: int):
    groupe = next((g for g in groupes_phrases['groupes'] if g['groupe'] == numero_groupe), None)
    if not groupe:
        raise HTTPException(status_code=404, detail="Groupe non trouvé")
    
    debut = groupe['debut_phrase'] - 1
    fin = groupe['fin_phrase']
    phrases_groupe = phrases_latines[debut:fin]

    return templates.TemplateResponse("groupe.html", {
        "request": request,
        "groupe": groupe,
        "total_groupes": len(groupes_phrases['groupes']),
        "phrases_groupe": phrases_groupe,
        "enumerate": enumerate  # Injecte enumerate dans le contexte
    })






@app.get("/phrase/{numero_phrase}", response_class=HTMLResponse)
def afficher_phrase(request: Request, numero_phrase: int):
    if numero_phrase < 1 or numero_phrase > len(phrases_latines):
        raise HTTPException(status_code=404, detail="Phrase non trouvée")

    phrase = phrases_latines[numero_phrase - 1]
    phrase_modifiee = rendre_mots_avec_bulles(phrase)
    phrase_colorée = colorer_mots_par_categorie(phrase)

    traduction = traductions[numero_phrase - 1] if numero_phrase - 1 < len(traductions) else "Traduction indisponible"

    # Ajout de total_phrases ici
    return templates.TemplateResponse("phrase.html", {
        "request": request,
        "phrase": phrase_modifiee,
        "phrase_coloree": phrase_colorée,
        "numero_phrase": numero_phrase,
        "total_phrases": len(phrases_latines),  # Ajout de cette ligne
        "traduction": traduction
    })




# Route pour afficher les détails d'un mot spécifique
@app.get("/mot/{mot_id}", response_class=HTMLResponse)
def afficher_mot(request: Request, mot_id: int):
    session = SessionLocal()
    mot = session.query(GrammaticalAnalysis).filter(GrammaticalAnalysis.id == mot_id).first()
    session.close()

    if not mot:
        raise HTTPException(status_code=404, detail="Mot non trouvé")

    return templates.TemplateResponse("mot.html", {
        "request": request,
        "mot": mot
    })

@app.get("/groupes", response_class=HTMLResponse)
def liste_groupes(request: Request):
    return templates.TemplateResponse("liste_groupes.html", {
        "request": request,
        "groupes": groupes_phrases['groupes']
    })

