from pydantic import BaseModel, ConfigDict, EmailStr, Field
from typing import List, Optional
from datetime import datetime

from app.main.schemas.file import FileSlim1


# --- Experience Models ---
class ExperienceBase(BaseModel):
    job_title: str
    company_name: str
    start_date: str
    end_date: Optional[str] = None
    description: str


class ExperienceCreate(ExperienceBase):
    pass


class Experience(ExperienceBase):
    uuid: str
    candidate_uuid: str
    model_config = ConfigDict(from_attributes=True)


# --- Diploma Models ---
# class DiplomaSlim(BaseModel):
#     uuid: str
#     degree_name: str
#     institution_name: str
#     graduation_year: str
#     model_config = ConfigDict(from_attributes=True)


class DiplomaBase(BaseModel):
    degree_name: str
    institution_name: str
    start_year: int
    end_year: int
    model_config = ConfigDict(from_attributes=True)


class DiplomaCreate(DiplomaBase):
    pass


class Diploma(DiplomaBase):
    uuid: str
    candidate_uuid: str
    model_config = ConfigDict(from_attributes=True)
# --- Candidate Models ---
class CandidateBase(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    code_country: str
    phone_number: str
    address: Optional[str] = None
    avatar_uuid: Optional[str] = None
    cv_uuid: Optional[str] = None
    password: str


class CandidateCreate(CandidateBase):
    experiences: List[ExperienceCreate]
    diplomas: List[DiplomaCreate]


class CandidateResponse(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    code_country: str
    phone_number: str
    full_phone_number: str
    address: Optional[str] = None
    avatar: Optional[FileSlim1] = None
    cv: Optional[FileSlim1] = None


class Candidate(CandidateResponse):
    uuid: str
    experiences: List[Experience] = []
    diplomas: List[Diploma] = []
    graduation_year:str
    model_config = ConfigDict(from_attributes=True)


class CandidateResponseList(BaseModel):
    total: int
    pages: int
    per_page: int
    current_page: int
    data: List[Candidate]
    model_config = ConfigDict(from_attributes=True)


class CandidateSlim(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    code_country: str
    phone_number: str
    full_phone_number: str
    address: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)


# --- Authentication Models ---
class Token(BaseModel):
    access_token: Optional[str] = None
    token_type: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)


class CandidateAuthentication(BaseModel):
    candidat: CandidateSlim
    token: Optional[Token] = None
    model_config = ConfigDict(from_attributes=True)


class CandidateLogin(BaseModel):
    email: EmailStr
    password: str
