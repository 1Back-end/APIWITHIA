import os
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.main.core.dependencies import get_db
from app.main.models.applications import Application
from app.main.models.job_offers import JobOffer
from app.main.core.i18n import __
import openai
import urllib3
from dotenv import load_dotenv

# Charger les variables d'environnement depuis le fichier .env
load_dotenv()
# Récupérer la clé API OpenAI depuis les variables d'environnement
openai.api_key = os.getenv("OPENAI_API_KEY")
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

router = APIRouter(prefix="/analyse", tags=["analyse"])

# Fonction utilitaire pour appeler l'API OpenAI pour prédire les résultats
def call_ai_prediction(candidate_data, job_offer_data):
    """
    Appel à l'API OpenAI pour prédire les résultats des candidatures.
    """
    try:
        # Utilisation de la nouvelle interface
        response = openai.Completion.create(
            model="gpt-3.5-turbo",  # Utilise un modèle valide
            prompt=f"Analyser les candidatures pour cette offre d'emploi: {job_offer_data}. Candidats: {candidate_data}",
            max_tokens=50  # Réduction du nombre de tokens
        )
        return response.choices[0].text.strip()  # Retourner le contenu de la réponse

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la prédiction de l'IA: {str(e)}")

# Fonction utilitaire pour récupérer les données des candidats et préparer la prédiction
def prepare_candidates_data(applications, job_offer):
    """
    Prépare les données des candidats et de l'offre d'emploi pour l'appel à l'API OpenAI.
    """
    candidate_data = []
    job_offer_data = {
        "salary": job_offer.salary,
        "employment_type": job_offer.employment_type,
    }

    for app in applications:
        candidate = app.candidate
        if candidate:
            candidate_data.append({
                "uuid": candidate.uuid,
                "first_name": candidate.first_name,
                "last_name": candidate.last_name,
                "experience": [exp.job_title for exp in candidate.experiences],
            })

    return candidate_data, job_offer_data

# Fonction générique pour obtenir les candidats acceptés, rejetés ou incertains
def get_candidates_by_status(job_offer_uuid: str, db: Session, status: str):
    """
    Fonction générique pour obtenir les candidats en fonction du statut (accepté, rejeté, incertain).
    """
    # Récupérer l'offre d'emploi par UUID
    job_offer = db.query(JobOffer).filter(JobOffer.uuid == job_offer_uuid).first()
    if not job_offer:
        raise HTTPException(status_code=404, detail=__(key="offer-not-found"))

    # Récupérer les candidatures associées à cette offre d'emploi
    applications = db.query(Application).filter(Application.job_offer_uuid == job_offer_uuid).all()
    if not applications:
        raise HTTPException(status_code=404, detail=__(key="no-applications-found-for-this-job-offer"))

    # Préparer les données des candidats pour l'IA
    candidate_data, job_offer_data = prepare_candidates_data(applications, job_offer)

    # Appeler l'API d'OpenAI pour prédire les résultats
    ai_results = call_ai_prediction(candidate_data, job_offer_data)

    # Analyser les résultats et extraire les candidats en fonction du statut
    filtered_candidates = [result for result in ai_results.split("\n") if status in result]

    return filtered_candidates

# Endpoint pour obtenir les candidats acceptés
@router.get("/applications/{job_offer_uuid}/accepted_candidates")
def get_accepted_candidates(
    job_offer_uuid: str,
    db: Session = Depends(get_db)
):
    """
    Endpoint pour prédire et obtenir les candidats acceptés pour une offre d'emploi.
    """
    accepted_candidates = get_candidates_by_status(job_offer_uuid, db, "ACCEPTED")
    return {
        "accepted_candidates": accepted_candidates,
        "message": __(key="prediction-completed")
    }

# Endpoint pour obtenir les candidats rejetés
@router.get("/applications/{job_offer_uuid}/rejected_candidates")
def get_rejected_candidates(
    job_offer_uuid: str,
    db: Session = Depends(get_db)
):
    """
    Endpoint pour prédire et obtenir les candidats rejetés pour une offre d'emploi.
    """
    rejected_candidates = get_candidates_by_status(job_offer_uuid, db, "REJECTED")
    return {
        "rejected_candidates": rejected_candidates,
        "message": __(key="prediction-completed")
    }

# Endpoint pour obtenir les candidats incertains
@router.get("/applications/{job_offer_uuid}/uncertain_candidates")
def get_uncertain_candidates(
    job_offer_uuid: str,
    db: Session = Depends(get_db)
):
    """
    Endpoint pour prédire et obtenir les candidats incertains pour une offre d'emploi.
    """
    uncertain_candidates = get_candidates_by_status(job_offer_uuid, db, "INCERTAIN")
    return {
        "uncertain_candidates": uncertain_candidates,
        "message": __(key="prediction-completed")
    }
