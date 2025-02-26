from datetime import datetime
from pydantic import BaseModel,EmailStr,ConfigDict
from typing import Optional

from app.main.models.job_offers import ContractType, WorkMode


class JobOffersBase(BaseModel):
    title:str
    description:str
    company_name:str
    location:str
    currency:str
    salary:float
    employment_type:ContractType
    posted_date:datetime
    expiration_date:datetime
    work_mode:WorkMode
    contact_email:EmailStr


class JobOffersCreate(JobOffersBase):
    pass

class JobOffersUpdate(BaseModel):
    uuid:str
    title:Optional[str]=None
    description:Optional[str]=None
    company_name:Optional[str]=None
    location:Optional[str]=None
    currency:Optional[str]=None
    salary:Optional[float]=None
    employment_type:Optional[ContractType]=None
    posted_date:Optional[datetime]=None
    expiration_date:Optional[datetime]=None
    work_mode:Optional[WorkMode]=None
    contact_email:Optional[EmailStr]=None


class JobOffersResponse(BaseModel):
    uuid:str
    title:str
    description:str
    company_name:str
    location:str
    full_salary:Optional[str]=None
    employment_type:ContractType
    posted_date:datetime
    expiration_date:datetime
    work_mode:WorkMode
    contact_email:EmailStr
    created_at:datetime
    updated_at:datetime
    model_config = ConfigDict(from_attributes=True)


class JobOffersUpdateStatus(BaseModel):
    uuid:str
class JobOffersDetails(BaseModel):
    uuid:str

class JobOffersDelete(BaseModel):
    uuid:str

class JobOffersResponseList(BaseModel):
    total: int
    pages: int
    per_page: int
    current_page:int
    data: list[JobOffersResponse]

    model_config = ConfigDict(from_attributes=True)


class JobOffersSlim(BaseModel):
    uuid:str
    title:str
    description:str
    company_name:str
    location:str
    full_salary:Optional[str]
    employment_type:ContractType
    posted_date:datetime
    expiration_date:datetime
    work_mode:WorkMode
    contact_email:EmailStr
    created_at:datetime
    model_config = ConfigDict(from_attributes=True)