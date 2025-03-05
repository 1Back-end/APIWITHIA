from datetime import datetime
from sqlalchemy import Column, ForeignKey, String, Text, DateTime, Boolean, Integer
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import ARRAY
from app.main.models.db.base_class import Base


class Candidat(Base):
    """
    Represents a candidate in the system.

    Attributes:
        uuid (str): The unique identifier for the candidate.
        first_name (str): The first name of the candidate.
        last_name (str): The last name of the candidate.
        email (str): The email address of the candidate.
        code_country (str): The country code for the candidate's phone number.
        phone_number (str): The phone number of the candidate.
        full_phone_number (str): The full phone number, including country code.
        address (str): The address of the candidate.
        avatar_uuid (str): The UUID for the candidate's avatar image.
        avatar (Storage): The relationship to the Storage model for the avatar.
        cv_uuid (str): The UUID for the candidate's CV.
        cv (Storage): The relationship to the Storage model for the CV.
        experiences (list): The list of experiences for the candidate.
        diplomas (list): The list of diplomas for the candidate.
        password (str): The candidate's password (hashed).
        is_new_user (bool): Indicates whether the candidate is a new user.
        otp (str): The one-time password for the candidate.
        otp_expired_at (datetime): The expiration date of the OTP.
        otp_password (str): The OTP password for the candidate.
        otp_password_expired_at (datetime): The expiration date of the OTP password.
        is_deleted (bool): Indicates whether the candidate is deleted.
        date_added (datetime): The date when the candidate was added.
        date_modified (datetime): The date when the candidate's data was last modified.
    """
    __tablename__ = "candidates"

    uuid = Column(String, primary_key=True, index=True)  # Unique identifier for the candidate
    first_name = Column(String, index=True, nullable=False)  # First name of the candidate
    last_name = Column(String, index=True, nullable=False)  # Last name of the candidate
    email = Column(String, unique=True, nullable=False)  # Email address of the candidate
    code_country = Column(String, nullable=False)  # Country code for phone number
    phone_number = Column(String, nullable=False)  # Phone number of the candidate
    full_phone_number = Column(String, unique=True, nullable=False)  # Full phone number including country code
    address = Column(String, nullable=True)  # Candidate's address
    avatar_uuid = Column(String, ForeignKey('storages.uuid'), nullable=True)  # Avatar UUID
    avatar = relationship("Storage", foreign_keys=[avatar_uuid], uselist=False)  # Avatar relationship with Storage
    cv_uuid = Column(String, ForeignKey('storages.uuid'), nullable=True)  # CV UUID
    cv = relationship("Storage", foreign_keys=[cv_uuid], uselist=False)  # CV relationship with Storage
    experiences = relationship("Experience", back_populates="candidate")  # Candidate's experiences
    diplomas = relationship("Diploma", back_populates="candidate")  # Candidate's diplomas
    password = Column(String(100), nullable=True, default="")  # Candidate's password (hashed)
    is_new_user = Column(Boolean, nullable=True, default=False)  # Indicates if the candidate is new
    otp = Column(String(5), nullable=True, default="")  # One-time password for the candidate
    otp_expired_at = Column(DateTime, nullable=True, default=None)  # OTP expiration time
    otp_password = Column(String(5), nullable=True, default="")  # OTP password for the candidate
    otp_password_expired_at = Column(DateTime, nullable=True, default=None)  # OTP password expiration time
    is_deleted = Column(Boolean, default=False)  # Indicates if the candidate is deleted

    date_added = Column(DateTime, nullable=False, default=datetime.now())  # Date candidate was added
    date_modified = Column(DateTime, nullable=False, default=datetime.now())  # Date candidate was last modified


class Experience(Base):
    """
    Represents a work experience of a candidate.

    Attributes:
        uuid (str): The unique identifier for the experience.
        job_title (str): The job title held by the candidate.
        company_name (str): The name of the company where the candidate worked.
        start_date (str): The start date of the experience.
        end_date (str): The end date of the experience.
        description (str): A description of the experience.
        candidate_uuid (str): The UUID of the candidate this experience belongs to.
        candidate (Candidat): The relationship to the Candidat model.
        date_added (datetime): The date when the experience was added.
        date_modified (datetime): The date when the experience was last modified.
    """
    __tablename__ = "experiences"

    uuid = Column(String, primary_key=True, index=True)  # Unique identifier for the experience
    job_title = Column(String, nullable=False)  # Job title held by the candidate
    company_name = Column(String, nullable=False)  # Company name
    start_date = Column(String, nullable=False)  # Start date of the experience
    end_date = Column(String, nullable=True)  # End date of the experience (optional)
    description = Column(Text, nullable=False)  # Description of the experience
    candidate_uuid = Column(String, ForeignKey("candidates.uuid"))  # Foreign key for the candidate
    candidate = relationship("Candidat", foreign_keys=[candidate_uuid])  # Bidirectional relationship with Candidat
    date_added = Column(DateTime, nullable=False, default=datetime.now())  # Date experience was added
    date_modified = Column(DateTime, nullable=False, default=datetime.now())  # Date experience was last modified

    @property
    def years_of_experience(self):
        """
        Calculates the number of years of experience based on the start and end dates.

        Returns:
            int: The number of years of experience.
        """
        start_date = datetime.strptime(self.start_date, "%Y-%m-%d")  # Ensure correct format
        end_date = datetime.strptime(self.end_date, "%Y-%m-%d") if self.end_date else datetime.now()  # Use current date if no end date

        delta = end_date - start_date
        return delta.days // 365  # Convert days to years


class Diploma(Base):
    """
    Represents a diploma obtained by a candidate.

    Attributes:
        uuid (str): The unique identifier for the diploma.
        degree_name (str): The name of the degree (e.g., Bachelor's, Master's, etc.).
        institution_name (str): The name of the institution where the diploma was obtained.
        start_year (int): The year the candidate started the program.
        end_year (int): The year the candidate finished the program.
        graduation_year (str): The year the diploma was awarded.
        candidate_uuid (str): The UUID of the candidate this diploma belongs to.
        candidate (Candidat): The relationship to the Candidat model.
        date_added (datetime): The date when the diploma was added.
        date_modified (datetime): The date when the diploma was last modified.
    """
    __tablename__ = "diplomas"

    uuid = Column(String, primary_key=True, index=True)  # Unique identifier for the diploma
    degree_name = Column(String, nullable=False)  # Degree name (e.g., Bachelor's, Master's)
    institution_name = Column(String, nullable=False)  # Institution where the diploma was obtained
    start_year = Column(Integer, nullable=False)  # Start year of the program
    end_year = Column(Integer, nullable=False)  # End year of the program
    graduation_year = Column(String, nullable=False)  # Year the diploma was awarded
    candidate_uuid = Column(String, ForeignKey("candidates.uuid"))  # Foreign key for the candidate
    candidate = relationship("Candidat", foreign_keys=[candidate_uuid])  # Bidirectional relationship with Candidat
    date_added = Column(DateTime, nullable=False, default=datetime.now())  # Date diploma was added
    date_modified = Column(DateTime, nullable=False, default=datetime.now(), onupdate=datetime.now())  # Date diploma was last modified
