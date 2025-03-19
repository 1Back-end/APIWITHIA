from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sklearn.ensemble import RandomForestClassifier
import numpy as np
import pickle
from sklearn.preprocessing import LabelEncoder
from app.main.core.dependencies import get_db
from app.main.models.applications import Application
from app.main.models.job_offers import JobOffer
from app.main.models.candidates import Candidat  # Assurez-vous d'avoir un modèle de candidat
from app.main.models.candidates import Diploma  # Importer le modèle des diplômes
from app.main.models.candidates import Experience  # Importer le modèle des expériences
from app.main.core.i18n import __

router = APIRouter(prefix="/analyse", tags=["analyse"])

# Charger le modèle entraîné
try:
    with open("app/main/models/ml_model.pkl", "rb") as f:
        model = pickle.load(f)
except FileNotFoundError:
    raise HTTPException(status_code=500, detail="Le modèle ML n'a pas été trouvé")

# Fonction pour ajuster le salaire (min 50 000 FCFA)
def adjust_salary(salary):
    return max(salary, 50000)

# Préparer les données des candidats
def prepare_candidates_data(applications, job_offer, db):
    candidate_data = []
    job_offer_data = {
        "salary": adjust_salary(job_offer.salary),  # Applique la fonction d'ajustement du salaire
        "employment_type": job_offer.employment_type,
    }

    for app in applications:
        candidate = app.candidate
        if candidate:
            # Récupérer les expériences et diplômes
            experiences = db.query(Experience).filter(Experience.candidate_uuid == candidate.uuid).all()
            diplomas = db.query(Diploma).filter(Diploma.candidate_uuid == candidate.uuid).all()

            # Vérifier les expériences du candidat et les titres de poste
            job_titles = [exp.job_title for exp in experiences] if experiences else []
            years_of_experience = sum([exp.years_of_experience for exp in experiences]) if experiences else 0
            
            candidate_data.append({
                "uuid": candidate.uuid,
                "first_name": candidate.first_name,
                "last_name": candidate.last_name,
                "experience": job_titles,  # Liste des intitulés de poste
                "years_of_experience": years_of_experience,
                "job_title": job_titles[0] if job_titles else "Non spécifié",  # Utiliser le premier titre ou une valeur par défaut
                "diplomas": [{"degree_name": diploma.degree_name, "institution_name": diploma.institution_name, "start_year": diploma.start_year, "end_year": diploma.end_year} for diploma in diplomas],
                "experiences": [{"job_title": exp.job_title, "company_name": exp.company_name, "start_date": exp.start_date, "end_date": exp.end_date, "description": exp.description} for exp in experiences]
            })

    return candidate_data, job_offer_data

# Transformer les données en format utilisable par le modèle
def transform_for_model(candidate_data, job_offer_data):
    X = []
    label_encoder = LabelEncoder()
    
    for candidate in candidate_data:
        # Vérification si l'expérience du candidat correspond à l'offre d'emploi
        experience_matches = any(
            job_offer_data["employment_type"].lower() in job_title.lower() for job_title in candidate["experience"]
        )
        
        # Encodage du titre de poste du candidat
        job_title_encoded = label_encoder.fit_transform([candidate["job_title"]])[0]
        
        # Les 3 caractéristiques principales à envoyer au modèle
        X.append([
            candidate["years_of_experience"],  # Nombre d'années d'expérience
            job_offer_data["salary"],  # Salaire de l'offre d'emploi
            experience_matches  # Ajouter une colonne pour vérifier si l'expérience correspond
        ])
    
    return np.array(X)

# Classifier les candidats avec le modèle IA
def classify_candidates(candidate_data, job_offer_data):
    X = transform_for_model(candidate_data, job_offer_data)
    predictions = model.predict(X)

    pre_employment_candidates = []  # Candidats en pré-emploi
    rejected_candidates = []         # Candidats rejetés
    accepted_candidates = []         # Candidats retenus

    # Séparer les candidats en fonction des prédictions
    for candidate, prediction in zip(candidate_data, predictions):
        if candidate["years_of_experience"] == 1:  # Candidat avec 1 an d'expérience doit aller en pré-emploi
            pre_employment_candidates.append(candidate)
        elif prediction == 2:  # Pré-emploi
            pre_employment_candidates.append(candidate)
        elif prediction == 0:  # Rejeté
            rejected_candidates.append(candidate)
        elif prediction == 1 : # Exclure l'infirmière
            accepted_candidates.append(candidate)

    return accepted_candidates, pre_employment_candidates, rejected_candidates

# Fonction principale pour analyser les candidatures avec l'IA
def get_candidates_by_status(job_offer_uuid: str, db: Session):
    job_offer = db.query(JobOffer).filter(JobOffer.uuid == job_offer_uuid).first()
    
    if not job_offer:
        raise HTTPException(status_code=404, detail=__(key="offer-not-found"))

    applications = db.query(Application).filter(Application.job_offer_uuid == job_offer_uuid).all()
    if not applications:
        raise HTTPException(status_code=404, detail=__(key="no-applications-found-for-this-job-offer"))

    candidate_data, job_offer_data = prepare_candidates_data(applications, job_offer, db)  # Pass db here
    
    # Effectuer la classification
    return classify_candidates(candidate_data, job_offer_data)

@router.get("/applications/{job_offer_uuid}/candidates_status")
def get_candidates_status(
    job_offer_uuid: str,
    db: Session = Depends(get_db)
):
    try:
        accepted_candidates, pre_employment_candidates, rejected_candidates = get_candidates_by_status(job_offer_uuid, db)
        
        # Créer un dictionnaire avec les candidats retenus, pré-emploi et rejetés
        return {
            "accepted_candidates": accepted_candidates,
            "pre_employment_candidates": pre_employment_candidates,
            "rejected_candidates": rejected_candidates,
            "message": __(key="prediction-completed")
        }
    except HTTPException as e:
        raise e  # Propager l'exception HTTPException pour retourner une réponse d'erreur appropriée
