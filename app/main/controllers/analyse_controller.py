from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sklearn.ensemble import RandomForestClassifier
import numpy as np
import pickle
from sklearn.preprocessing import LabelEncoder
from app.main.core.dependencies import get_db
from app.main.models.applications import Application
from app.main.models.job_offers import JobOffer
from app.main.models.candidates import Candidat, Diploma, Experience
from app.main.core.i18n import __
from datetime import datetime
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

# Fonction pour récupérer l'offre d'emploi par UUID
def get_job_offer_by_uuid(job_offer_uuid: str, db: Session):
    job_offer = db.query(JobOffer).filter(JobOffer.uuid == job_offer_uuid).first()
    if not job_offer:
        raise HTTPException(status_code=404, detail=__("offer-not-found"))
    return job_offer

# Préparer les données des candidats
def prepare_candidates_data(applications, job_offer, db):
    candidate_data = []
    job_offer_data = {
        "salary": adjust_salary(job_offer.salary),
        "employment_type": job_offer.employment_type,
    }

    for app in applications:
        candidate = app.candidate
        if candidate:
            experiences = db.query(Experience).filter(Experience.candidate_uuid == candidate.uuid).all()
            diplomas = db.query(Diploma).filter(Diploma.candidate_uuid == candidate.uuid).all()
            
            job_titles = [exp.job_title for exp in experiences] if experiences else []
            years_of_experience = 0
            for exp in experiences:
                if exp.end_date == "Present":
                    end_date = datetime.now().strftime('%Y-%m-%d')
                else:
                    end_date = exp.end_date
                
                start_date = datetime.strptime(exp.start_date, '%Y-%m-%d')
                end_date = datetime.strptime(end_date, '%Y-%m-%d')
                years_of_experience += (end_date - start_date).days // 365

            candidate_data.append({
                "uuid": candidate.uuid,
                "first_name": candidate.first_name,
                "last_name": candidate.last_name,
                "experience": job_titles,
                "years_of_experience": years_of_experience,
                "job_title": job_offer.title if job_offer else "Titre non trouvé",
                "diplomas": [{"degree_name": diploma.degree_name, "institution_name": diploma.institution_name, "start_year": diploma.start_year, "end_year": diploma.end_year} for diploma in diplomas],
                "experiences": [{"job_title": exp.job_title, "company_name": exp.company_name, "start_date": exp.start_date, "end_date": exp.end_date, "description": exp.description} for exp in experiences]
            })

    return candidate_data, job_offer_data

# Transformer les données en format utilisable par le modèle
def transform_for_model(candidate_data, job_offer_data):
    X = []
    label_encoder = LabelEncoder()
    
    for candidate in candidate_data:
        experience_matches = any(
            job_offer_data["employment_type"].lower() in job_title.lower() for job_title in candidate["experience"]
        )
        
        job_title_encoded = label_encoder.fit_transform([candidate["job_title"]])[0]
        
        X.append([
            candidate["years_of_experience"],
            job_offer_data["salary"],
            experience_matches
        ])
    
    return np.array(X)

# Classifier les candidats avec le modèle IA
def classify_candidates(candidate_data, job_offer_data):
    X = transform_for_model(candidate_data, job_offer_data)
    predictions = model.predict(X)

    pre_employment_candidates = [] 
    rejected_candidates = []         
    accepted_candidates = []         

    for candidate, prediction in zip(candidate_data, predictions):
        if candidate["years_of_experience"] == 1:
            pre_employment_candidates.append(candidate)
        elif prediction == 2:
            pre_employment_candidates.append(candidate)
        elif prediction == 0:
            rejected_candidates.append(candidate)
        elif prediction == 1:
            accepted_candidates.append(candidate)

    return accepted_candidates, pre_employment_candidates, rejected_candidates

# Recommendations by domain
recommendations = {
    'Tech': {
        'Développeur Backend': 'Apprenez les frameworks comme Laravel, Symfony, Node.js et maîtrisez les bases de données SQL et NoSQL.',
        'Développeur Laravel': 'Maîtrisez Laravel, PHP, Eloquent ORM, et les bonnes pratiques du framework.',
        'Développeur Angular': 'Maîtrisez Angular, TypeScript, RxJS, et les concepts d\'architecture SPA.',
        'Développeur Frontend': 'Maîtrisez HTML, CSS, JavaScript et les frameworks comme React.js et Angular.',
        'Data Scientist': 'Approfondissez vos compétences en Python, R et apprentissage automatique.',
        'Développeur Node.js': 'Apprenez à utiliser Node.js, Express, et les API RESTful.',
        'Développeur Mobile (React Native)': 'Maîtrisez React Native pour créer des applications mobiles performantes.',
        'Ingénieur DevOps': 'Apprenez à automatiser les processus de développement avec des outils comme Docker, Kubernetes, et CI/CD.',
    },
    'Healthcare': {
        'Médecin': 'Acquérez des compétences en gestion de la santé numérique et dans l\'utilisation des technologies médicales modernes.',
        'Infirmier': 'Renforcez vos compétences dans l\'utilisation des technologies médicales.',
    },
    'Education': {
        'Professeur d\'Informatique': 'Renforcez vos connaissances en pédagogie et apprenez à enseigner des langages comme Python, JavaScript, ou C++.',
    },
    'Business': {
        'Responsable Marketing': 'Approfondissez vos compétences en marketing digital et SEO.',
        'Chef de Projet': 'Apprenez la gestion de projet Agile et la coordination d\'équipes.',
    }
}

# Fonction pour obtenir les recommandations d'apprentissage en fonction du titre de poste
def get_learning_recommendation(job_title):
    domain_recommendations = recommendations.get("Tech", {})  # Par défaut Tech

    for domain, jobs in recommendations.items():
        if job_title in jobs:
            domain_recommendations = jobs
            break
    
    return domain_recommendations.get(job_title, "Pas de recommandations disponibles pour ce titre.")

# Fonction principale pour analyser les candidatures avec l'IA
def get_candidates_by_status(job_offer_uuid: str, db: Session):
    job_offer = db.query(JobOffer).filter(JobOffer.uuid == job_offer_uuid).first()
    
    if not job_offer:
        raise HTTPException(status_code=404, detail=__(key="offer-not-found"))

    applications = db.query(Application).filter(Application.job_offer_uuid == job_offer_uuid).all()
    if not applications:
        raise HTTPException(status_code=404, detail=__(key="no-applications-found-for-this-job-offer"))

    candidate_data, job_offer_data = prepare_candidates_data(applications, job_offer, db)
    
    return classify_candidates(candidate_data, job_offer_data)

@router.get("/applications/{job_offer_uuid}/candidates_status")
def get_candidates_status(
    job_offer_uuid: str,
    db: Session = Depends(get_db)
):
    try:
        accepted_candidates, pre_employment_candidates, rejected_candidates = get_candidates_by_status(job_offer_uuid, db)
        
        # Ajouter des recommandations d'apprentissage pour les candidats en pré-emploi
        for candidate in pre_employment_candidates:
            candidate['learning_recommendations'] = get_learning_recommendation(candidate['job_title'])

        return {
            "message": "Je suis une IA qui analyse les candidatures en fonction des offres d'emploi et des expériences des candidats.",
            "accepted_candidates": accepted_candidates,
            "pre_employment_candidates": pre_employment_candidates,
            "rejected_candidates": rejected_candidates,
            "status_message": __(key="prediction-completed")
        }
    except HTTPException as e:
        raise e
