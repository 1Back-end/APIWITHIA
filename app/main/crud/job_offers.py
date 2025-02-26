import math
import bcrypt
from fastapi import BackgroundTasks, HTTPException
from sqlalchemy import or_
import re
from typing import List, Optional, Union
import uuid
from app.main.core.i18n import __
from sqlalchemy.orm import Session
from app.main.crud.base import CRUDBase
from app.main import models,schemas
from app.main.core.mail import send_notification_to_candidate

class CRUDJobOffers(CRUDBase[models.JobOffer,schemas.JobOffersCreate,schemas.JobOffersUpdate]):
    

    @classmethod
    def get_by_uuid(cls,db:Session,*,uuid:str):
        return db.query(models.JobOffer).filter(models.JobOffer.uuid==uuid,models.JobOffer.is_deleted==False).first()
    
    @classmethod
    def get_by_employment_type(cls,db:Session,*,employment_type:str):
        return db.query(models.JobOffer).filter(models.JobOffer.employment_type==employment_type,models.JobOffer.is_deleted==False).first()
    
    @classmethod
    def get_by_work_mode(cls,db:Session,work_mode:str):
        return db.query(models.JobOffer).filter(models.JobOffer.work_mode==work_mode,models.JobOffer.is_deleted==False).first()
    
    @classmethod
    def create(cls,db:Session,obj_in:schemas.JobOffersCreate,background_tasks: BackgroundTasks):
        offers = models.JobOffer(
            uuid=str(uuid.uuid4()),
            title=obj_in.title,
            description=obj_in.description,
            company_name=obj_in.company_name,
            location=obj_in.location,
            salary=obj_in.salary,
            currency=obj_in.currency,
            full_salary=f"{obj_in.salary}{obj_in.currency}",
            employment_type=obj_in.employment_type,
            posted_date=obj_in.posted_date,
            expiration_date=obj_in.expiration_date,
            work_mode=obj_in.work_mode,
            contact_email=obj_in.contact_email

        )
        db.add(offers)
        db.commit()
        db.refresh(offers)
        # Récupérer tous les candidats inscrits dans le système
        candidates = db.query(models.Candidat).filter(models.Candidat.is_deleted==False).all()
        
        for candidate in candidates:
            background_tasks.add_task(
                send_notification_to_candidate, 
                email=candidate.email, 
                name=f"{candidate.first_name} {candidate.last_name}", 
                job_title=offers.title, 
                job_description=offers.description
            )
        # Retourner l'offre créée
        return offers
    

    @classmethod
    def update(cls,db:Session,obj_in:schemas.JobOffersUpdate):
        offers = cls.get_by_uuid(db=db,uuid=obj_in.uuid)
        if not offers:
            raise HTTPException(status_code=404,detail=__(key="offers-not-found"))
        offers.title = obj_in.title if obj_in.title else offers.title
        offers.description = obj_in.description if obj_in.description else offers.description
        offers.company_name=obj_in.company_name if obj_in.company_name else offers.company_name
        offers.location = obj_in.location if obj_in.location else offers.location
        offers.salary = obj_in.salary if obj_in.salary else offers.salary
        offers.currency = obj_in.currency if obj_in.currency else offers.currency
        offers.full_salary = f"{obj_in.salary}{obj_in.currency}" if obj_in.salary and  obj_in.currency else offers.full_salary
        offers.employment_type = obj_in.employment_type if obj_in.employment_type else offers.employment_type
        offers.posted_date = obj_in.posted_date if obj_in.posted_date else offers.posted_date
        offers.expiration_date = obj_in.expiration_date if obj_in.expiration_date else offers.expiration_date
        offers.work_mode = obj_in.work_mode if obj_in.work_mode else offers.work_mode
        offers.contact_email = obj_in.contact_email if obj_in.contact_email else offers.contact_email
        db.flush()
        db.commit()
        db.refresh(offers)
        return offers
    

    @classmethod
    def delete(cls, db: Session, obj_in: schemas.JobOffersDelete):
        offers = cls.get_by_uuid(db=db,uuid=obj_in.uuid)
        if not offers:
            raise HTTPException(status_code=404,detail=__(key="offers-not-found"))
        offers.is_deleted = True
        db.commit()

    @classmethod
    def update_status(cls,db:Session,uuid:str,status:str):
        offers = cls.get_by_uuid(db=db,uuid=uuid)
        if not offers:
            raise HTTPException(status_code=404,detail=__(key="offers-not-found"))
        offers.status = status
        db.commit()

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
        status: Optional[str] = None,
        work_mode:Optional[str] = None,
        employment_type:Optional[str]=None
    ):
        
        if page < 1:
            page = 1

        record_query = db.query(models.JobOffer).filter(models.JobOffer.is_deleted==False)

        if keyword:
            record_query = record_query.filter(
                or_(
                    models.JobOffer.title.ilike(f'%{keyword}%'),
                    models.JobOffer.company_name.ilike(f'%{keyword}%'),
                    models.JobOffer.location.ilike(f'%{keyword}%'),
                    models.JobOffer.salary.ilike(f'%{keyword}%'),
                    models.JobOffer.description.ilike(f'%{keyword}%'),
                    models.JobOffer.requirements.ilike(f'%{keyword}%')
                )
            )

        if order and order_field and hasattr(models.Company, order_field):
            if order == "asc":
                record_query = record_query.order_by(getattr(models.JobOffer, order_field).asc())
            else:
                record_query = record_query.order_by(getattr(models.JobOffer, order_field).desc())
        if status:
            record_query = record_query.filter(models.JobOffer.status == status)
        if work_mode:
            record_query = record_query.filter(models.JobOffer.work_mode == work_mode)

        if employment_type:
            record_query = record_query.filter(models.JobOffer.employment_type == employment_type)



        total = record_query.count()

        record_query = record_query.offset((page - 1) * per_page).limit(per_page).all()

        return schemas.JobOffersResponseList(
            total=total,
            pages=math.ceil(total / per_page),
            per_page=per_page,
            current_page=page,
            data=record_query
        )


offers = CRUDJobOffers(models.JobOffer)

