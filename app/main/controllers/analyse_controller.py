from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.main.core.dependencies import get_db
from app.main.models.applications import Application
from app.main.models.job_offers import JobOffer
from app.main.core.i18n import __

router = APIRouter(prefix="/analyse", tags=["analyse"])

# Fonction utilitaire pour récupérer et préparer les données
def prepare_candidates_data(applications, job_offer):
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
                "years_of_experience": sum([exp.years_of_experience for exp in candidate.experiences]),  # Utilisation de la méthode years_of_experience
            })

    return candidate_data, job_offer_data

# Fonction de filtrage des candidats en fonction des règles
def filter_candidates_by_rules(candidate_data, job_offer_data):
    accepted_candidates = []
    pre_employment_candidates = []
    rejected_candidates = []

    for candidate in candidate_data:
        # Règles pour la prédiction des candidats acceptés directement
        if candidate["years_of_experience"] >= 5 and "Software Engineer" in candidate["experience"]:
            accepted_candidates.append(candidate)
        # Règles pour les candidats en période de pré-emploi
        elif candidate["years_of_experience"] >= 2 and candidate["years_of_experience"] < 5:
            pre_employment_candidates.append(candidate)
        # Règles pour les candidats rejetés
        else:
            rejected_candidates.append(candidate)

    return accepted_candidates, pre_employment_candidates, rejected_candidates

# Fonction d'analyse des candidatures sans IA
def get_candidates_by_status(job_offer_uuid: str, db: Session):
    job_offer = db.query(JobOffer).filter(JobOffer.uuid == job_offer_uuid).first()
    if not job_offer:
        raise HTTPException(status_code=404, detail=__(key="offer-not-found"))

    applications = db.query(Application).filter(Application.job_offer_uuid == job_offer_uuid).all()
    if not applications:
        raise HTTPException(status_code=404, detail=__(key="no-applications-found-for-this-job-offer"))

    candidate_data, job_offer_data = prepare_candidates_data(applications, job_offer)

    # Appliquer les règles de filtrage pour les candidats
    accepted_candidates, pre_employment_candidates, rejected_candidates = filter_candidates_by_rules(candidate_data, job_offer_data)

    return accepted_candidates, pre_employment_candidates, rejected_candidates

@router.get("/applications/{job_offer_uuid}/accepted_candidates")
def get_accepted_candidates(
    job_offer_uuid: str, 
    db: Session = Depends(get_db)
):
    accepted_candidates, _, _ = get_candidates_by_status(job_offer_uuid, db)
    return {"accepted_candidates": accepted_candidates, "message": __(key="prediction-completed")}

@router.get("/applications/{job_offer_uuid}/pre_employment_candidates")
def get_pre_employment_candidates(
    job_offer_uuid: str, 
    db: Session = Depends(get_db)
):
    _, pre_employment_candidates, _ = get_candidates_by_status(job_offer_uuid, db)
    return {"pre_employment_candidates": pre_employment_candidates, "message": __(key="prediction-completed")}

@router.get("/applications/{job_offer_uuid}/rejected_candidates")
def get_rejected_candidates(
    job_offer_uuid: str, 
    db: Session = Depends(get_db)
):
    _, _, rejected_candidates = get_candidates_by_status(job_offer_uuid, db)
    return {"rejected_candidates": rejected_candidates, "message": __(key="prediction-completed")}

