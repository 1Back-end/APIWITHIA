from sqlalchemy import Column, ForeignKey, String, DateTime, Text,Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import ENUM
from datetime import datetime
from app.main.models.db.base_class import Base
from enum import Enum

class ApplicationStatusEnum(str, Enum):
    PENDING = "Pending"
    ACCEPTED = "Accepted"
    REJECTED = "Rejected"

class Application(Base):
    __tablename__ = "applications"
    
    uuid = Column(String, primary_key=True, index=True)  # UUID unique
    candidate_uuid = Column(String, ForeignKey('candidates.uuid'), nullable=False)  # Candidat postulant
    candidate = relationship("Candidat", foreign_keys=[candidate_uuid])
    job_offer_uuid = Column(String, ForeignKey('job_offers.uuid'), nullable=False)  # Offre d'emploi concernée
    job_offer = relationship("JobOffer", foreign_keys=[job_offer_uuid])
    status = Column(String, nullable=False, default=ApplicationStatusEnum.PENDING)  # Statut de la candidature
    cover_letter_uuid = Column(String, ForeignKey('storages.uuid'), nullable=True)  # Lien vers le CV
    cover_letter = relationship("Storage", foreign_keys=[cover_letter_uuid], uselist=False)  # Relation avec le modèle Storage pour le CV
    cv_uuid = Column(String, ForeignKey('storages.uuid'), nullable=True)  # Lien vers le CV
    cv = relationship("Storage", foreign_keys=[cv_uuid], uselist=False)  # Relation avec le modèle Storage pour le CV
    applied_date = Column(DateTime, nullable=False, default=datetime.now())  # Date de candidature
    is_deleted = Column(Boolean,default=False)

    
    date_added = Column(DateTime, nullable=False, default=datetime.now())
    date_modified = Column(DateTime, nullable=False, default=datetime.now())

