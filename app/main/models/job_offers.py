from dataclasses import dataclass
from sqlalchemy.sql import func
from datetime import datetime
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql.json import JSONB
from sqlalchemy import Column, ForeignKey, Integer, String, Text, DateTime, Float, Boolean
from sqlalchemy import event
from app.main.models.db.base_class import Base
from enum import Enum

# Enum for contract types
class ContractType(str, Enum):
    """Enum representing the different contract types."""
    CDI = "CDI"
    CDD = "CDD"
    Freelance = "Freelance"
    Internship = "Internship"

# Enum for job offer status
class JobStatus(str, Enum):
    """Enum representing the status of a job offer."""
    active = "active"
    closed = "closed"
    expired = "expired"

# Enum for work mode (e.g., full-time, part-time)
class WorkMode(str, Enum):
    """Enum representing the work mode for a job offer."""
    full_time = "Full-Time"
    part_time = "Part-Time"
    remote = "Remote"
    hybrid = "Hybrid"

class JobOffer(Base):
    """
    Represents a job offer in the system.

    Attributes:
        uuid (str): Unique identifier for the job offer.
        title (str): The title of the job offer.
        description (str): Detailed description of the job.
        company_name (str): Name of the company offering the job.
        location (str): Location of the job.
        currency (str): The currency for the salary (default is FCFA).
        salary (float): The salary offered for the position.
        full_salary (str): String representation of the salary.
        employment_type (str): The type of employment (e.g., CDI, CDD).
        requirements (str): Required skills for the job.
        posted_date (datetime): The date when the job offer was posted.
        expiration_date (datetime): The expiration date for the job offer.
        status (str): The status of the job offer (e.g., active, closed).
        work_mode (str): The mode of work (e.g., full-time, part-time).
        contact_email (str): Email address for job-related inquiries.
        is_deleted (bool): Flag indicating if the job offer has been deleted.
        created_at (datetime): Timestamp when the job offer was created.
        updated_at (datetime): Timestamp when the job offer was last updated.
    """
    __tablename__ = "job_offers"

    uuid = Column(String, primary_key=True)  # Unique identifier (UUID)
    title = Column(String, nullable=False)  # Job title
    description = Column(Text, nullable=False)  # Detailed job description
    company_name = Column(String, nullable=False)  # Name of the company
    location = Column(String, nullable=False)  # Job location
    currency = Column(String, nullable=False, default="FCFA")  # Currency for the salary
    salary = Column(Float, nullable=False)  # Salary offered
    full_salary = Column(String, nullable=False)  # Full salary representation
    employment_type = Column(String, nullable=False, default=ContractType.CDD)  # Employment contract type
    requirements = Column(Text)  # Required skills for the job
    posted_date = Column(DateTime, default=func.now())  # Job offer posted date
    expiration_date = Column(DateTime, default=func.now())  # Job offer expiration date
    status = Column(String, nullable=False, default=JobStatus.active)  # Job status
    work_mode = Column(String, nullable=False, default=WorkMode.full_time)  # Work mode
    contact_email = Column(String, nullable=False)  # Contact email for inquiries
    is_deleted = Column(Boolean, default=False)  # Flag for soft deletion

    created_at = Column(DateTime, default=func.now())  # Creation timestamp
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())  # Update timestamp

    def __repr__(self):
        """
        String representation of the JobOffer object.

        Returns:
            str: A string representing the JobOffer object with job ID and title.
        """
        return f"<JobOffer(job_id={self.uuid}, title={self.title})>"
