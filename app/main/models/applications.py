from sqlalchemy import Column, ForeignKey, String, DateTime, Text,Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import ENUM
from datetime import datetime
from app.main.models.db.base_class import Base
from enum import Enum

class ApplicationStatusEnum(str, Enum):
    """
    Enum representing the possible statuses of an application.
    
    Attributes:
        PENDING: The application is awaiting review.
        ACCEPTED: The application has been accepted.
        REJECTED: The application has been rejected.
    """
    PENDING = "Pending"
    ACCEPTED = "Accepted"
    REJECTED = "Rejected"


class Application(Base):
    """
    Represents an application submitted by a candidate for a job offer.
    
    Attributes:
        uuid (str): The unique identifier for the application.
        candidate_uuid (str): The unique identifier for the candidate submitting the application.
        candidate (Candidat): The candidate who submitted the application.
        job_offer_uuid (str): The unique identifier for the job offer the application is for.
        job_offer (JobOffer): The job offer associated with the application.
        status (str): The status of the application, defaulting to 'Pending'.
        cover_letter_uuid (str): The unique identifier for the cover letter document.
        cover_letter (Storage): The storage location for the cover letter.
        cv_uuid (str): The unique identifier for the CV document.
        cv (Storage): The storage location for the CV.
        applied_date (datetime): The date and time the application was submitted.
        is_deleted (bool): Flag indicating if the application is marked as deleted.
        date_added (datetime): The date and time the application was created.
        date_modified (datetime): The date and time the application was last modified.
    """
    
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
    is_deleted = Column(Boolean, default=False)

    date_added = Column(DateTime, nullable=False, default=datetime.now())
    date_modified = Column(DateTime, nullable=False, default=datetime.now())
