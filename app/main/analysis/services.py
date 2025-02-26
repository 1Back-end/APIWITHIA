# app/analysis/services.py
from sqlalchemy.orm import Session
from app.main.models import Application, Candidat, JobOffer
from typing import List, Dict

def analyze_candidates(db: Session, job_offer_uuid: str) -> Dict[str, List]:
    """
    Analyse les candidatures pour une offre d'emploi donnée.
    Retourne les candidats retenus et non retenus.
    """
    applications = db.query(Application).filter(Application.job_offer_uuid == job_offer_uuid, Application.is_deleted == False).all()
    
    selected_candidates = []
    rejected_candidates = []
    
    for application in applications:
        candidate = db.query(Candidat).filter(Candidat.uuid == application.candidate_uuid).first()
        job_offer = db.query(JobOffer).filter(JobOffer.uuid == job_offer_uuid).first()
        
        if not candidate or not job_offer:
            continue
        
        if meets_criteria(candidate, job_offer):
            selected_candidates.append(candidate)
        else:
            rejected_candidates.append(candidate)
    
    return {"selected": selected_candidates, "rejected": rejected_candidates}


def meets_criteria(candidate: Candidat, job_offer: JobOffer) -> bool:
    """
    Vérifie si un candidat répond aux critères d'une offre d'emploi.
    """
    # Logique avancée d'analyse (exemple simplifié)
    if candidate.experiences and len(candidate.experiences) >= 2:
        return True
    return False
