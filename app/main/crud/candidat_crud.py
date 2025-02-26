from http import client
import math
import bcrypt
from fastapi import HTTPException
from sqlalchemy import or_
import re
from typing import List, Optional, Union
import uuid
from app.main.core.i18n import __
from app.main.core.security import generate_password, get_password_hash,verify_password
from sqlalchemy.orm import Session
from app.main.crud.base import CRUDBase
from app.main import models,schemas
from app.main.core.mail import send_account_creation_email
import requests
import tldextract
import openai
import urllib3
from dotenv import load_dotenv
import os

# Charger les variables d'environnement depuis le fichier .env
load_dotenv()
# Récupérer la clé API OpenAI depuis les variables d'environnement
openai.api_key = os.getenv("OPENAI_API_KEY")
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class CRUDCandidat(CRUDBase[models.Candidat,schemas.CandidateBase,schemas.CandidateCreate]):
    @classmethod
    def get_by_email(cls,db:Session,*,email:str):
        return db.query(models.Candidat).filter(models.Candidat.email==email).first()
    @classmethod
    def get_by_phone_number(cls,db:Session,*,phone_number:str):
        return db.query(models.Candidat).filter(models.Candidat.phone_number==phone_number).first()
    @classmethod
    def get_by_uuid(cls,db:Session,*,uuid:str):
        return db.query(models.Candidat).filter(models.Candidat.uuid==uuid).first()
    
    @classmethod
    def verify_company(cls, email: str) -> bool:
        domain = email.split("@")[-1]  # Extraire le domaine de l'email
        extracted = tldextract.extract(domain)
        company_name = extracted.domain  # Récupérer le nom de domaine principal

        # Vérifier l'existence de l'entreprise via une API (Ex: Clearbit, OpenCorporates, etc.)
        api_url = f"https://api.company-check.com/{company_name}"
        
        # Ignorer la vérification SSL (ne pas utiliser en production)
        response = requests.get(api_url, verify=False)
        # Ignorer les avertissements de SSL
        if response.status_code == 200:
            return True  # L'entreprise existe
        return False  # L'entreprise n'est pas trouvée

    @classmethod
    def verify_experience_with_chatgpt(cls, job_title: str, company_name: str, start_date: str, end_date: str) -> bool:
        prompt = f"""
        Un candidat a indiqué avoir travaillé en tant que {job_title} chez {company_name} du {start_date} au {end_date}.
        Peux-tu vérifier si cette expérience est crédible en te basant sur les données publiques et la cohérence des informations ?
        Réponds seulement par 'Vrai' ou 'Faux'.
        """
        
        # Appel à l'API OpenAI pour vérifier l'expérience
        response = openai.Completion.create(
            model="gpt-4",
            prompt=prompt,
            max_tokens=100
        )
        result = response.choices[0].text.strip()
        return result.lower() == "vrai"  # Retourne True si ChatGPT dit que c'est crédible

    @classmethod
    def create(cls, db: Session, *, candidate: schemas.CandidateCreate):
        # Vérifier l'entreprise via son email
        if not cls.verify_company(candidate.email):
            raise HTTPException(status_code=400, detail="L'entreprise liée à cet email n'existe pas.")

        # Créer le candidat
        db_candidate = models.Candidat(
            uuid=str(uuid.uuid4()),
            first_name=candidate.first_name,
            last_name=candidate.last_name,
            email=candidate.email,
            code_country=candidate.code_country,
            phone_number=candidate.phone_number,
            full_phone_number=f"{candidate.code_country}{candidate.phone_number}",
            address=candidate.address,
            avatar_uuid=candidate.avatar_uuid,
            password=get_password_hash(candidate.password),
            cv_uuid=candidate.cv_uuid,
        )
        db.add(db_candidate)
        db.commit()
        db.refresh(db_candidate)

        # Vérifier et ajouter les expériences
        for exp in candidate.experiences:
            if cls.verify_experience_with_chatgpt(exp.job_title, exp.company_name, exp.start_date, exp.end_date):
                db_experience = models.Experience(
                    uuid=str(uuid.uuid4()),
                    job_title=exp.job_title,
                    company_name=exp.company_name,
                    start_date=exp.start_date,
                    end_date=exp.end_date,
                    description=exp.description,
                    candidate_uuid=db_candidate.uuid
                )
                db.add(db_experience)
            else:
                raise HTTPException(status_code=400, detail=f"L'expérience chez {exp.company_name} semble fausse.")

        db.commit()
        return db_candidate

    

    @classmethod
    def get_multi(
        cls,
        *,
        db: Session,
        page: int = 1,
        per_page: int = 30,
        order: Optional[str] = None,
        order_field: Optional[str] = None,
        keyword: Optional[str] = None,
    ):
        
        if page < 1:
            page = 1

        record_query = db.query(models.Candidat)

        if keyword:
            record_query = record_query.filter(
                or_(
                    models.Candidat.first_name.ilike(f'%{keyword}%'),
                    models.Candidat.last_name.ilike(f'%{keyword}%'),
                    models.Candidat.email.ilike(f'%{keyword}%'),
                    models.Candidat.phone_number.ilike(f'%{keyword}%'),
                    models.Candidat.full_phone_number.ilike(f'%{keyword}%'),
                )
            )

        if order and order_field and hasattr(models.Candidat, order_field):
            if order == "asc":
                record_query = record_query.order_by(getattr(models.Candidat, order_field).asc())
            else:
                record_query = record_query.order_by(getattr(models.Candidat, order_field).desc())
        
        total = record_query.count()

        record_query = record_query.offset((page - 1) * per_page).limit(per_page).all()

        return schemas.CandidateResponseList(
            total=total,
            pages=math.ceil(total / per_page),
            per_page=per_page,
            current_page=page,
            data=record_query
        )
    
    @classmethod
    def authenticate(cls, db: Session, *, email: str, password: str):
        db_obj: models.Candidat = db.query(models.Candidat).filter(models.Candidat.email == email).first()
        if not db_obj:
            return None
        if not verify_password(password, db_obj.password):  # Vérifie bien que "password" existe dans la BDD
            return None
        return db_obj


candidate = CRUDCandidat(models.Candidat)