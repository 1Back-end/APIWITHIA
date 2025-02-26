from dataclasses import dataclass
from sqlalchemy.sql import func
from datetime import datetime
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql.json import JSONB
from sqlalchemy import Column, ForeignKey, Integer, String, Text, DateTime,Float,Boolean
from sqlalchemy import event
from app.main.models.db.base_class import Base
from enum import Enum

# Enum pour le type de contrat
class ContractType(str,Enum):
    CDI = "CDI"
    CDD = "CDD"
    Freelance = "Freelance"
    Internship = "Internship"

# Enum pour le statut de l'offre
class JobStatus(str,Enum):
    active = "active"
    closed = "closed"
    expired = "expired"

# Enum pour le mode de travail (full-time, part-time)
class WorkMode(str,Enum):
    full_time = "Full-Time"
    part_time = "Part-Time"
    remote = "Remote"
    hybrid = "Hybrid"

class JobOffer(Base):
    __tablename__ = "job_offers"

    uuid = Column(String, primary_key=True)  # Identifiant unique (UUID)
    title = Column(String, nullable=False)  # Titre du poste
    description = Column(Text, nullable=False)  # Description détaillée
    company_name = Column(String, nullable=False)  # Nom de l'entreprise
    location = Column(String,nullable=False)  # Lieu du travail
    currency = Column(String, nullable=False, default="FCFA")
    salary = Column(Float,nullable=False)  # Salaire proposé
    full_salary = Column(String,nullable=False) 
    employment_type = Column(String,nullable=False,default=ContractType.CDD)  # Type de contrat
    requirements = Column(Text)  # Compétences requises
    posted_date = Column(DateTime, default=func.now())  # Date de publication
    expiration_date = Column(DateTime, default=func.now())  # Date limite
    status = Column(String,nullable=False, default=JobStatus.active)  # Statut de l'offre (enum)
    work_mode = Column(String,nullable=False, default=WorkMode.full_time)  # Mode de travail (enum
    contact_email = Column(String, nullable=False)  # Email de contact
    is_deleted = Column(Boolean,default=False)

    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())


    def __repr__(self):
        return f"<JobOffer(job_id={self.job_id}, title={self.title})>"
