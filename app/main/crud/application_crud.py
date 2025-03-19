from datetime import datetime
import math
import bcrypt
from fastapi import HTTPException
from sqlalchemy import or_
import re
from typing import List, Optional, Union
import uuid
from app.main.core.i18n import __
from sqlalchemy.orm import Session
from app.main.crud.base import CRUDBase
from app.main import models,schemas,crud

class CRUDApplication(CRUDBase[models.Application,schemas.ApplicationDetails,schemas.ApplicationResponse]):

    @classmethod
    def get_by_uuid(cls,db:Session,*,uuid:str):
        return db.query(models.Application).filter(models.Application.uuid==uuid,models.Application.is_deleted==False).first()
    
    @classmethod
    def get_by_candidate_uuid(cls,db:Session,*,candidate_uuid:str):
        return db.query(models.Application).filter(models.Application.candidate_uuid==candidate_uuid,models.Application.is_deleted==False).all()
    

    @classmethod
    def get_by_job_offer_uuid(cls,db:Session,*,job_offer_uuid:str):
        return db.query(models.Application).filter(models.Application.job_offer_uuid==job_offer_uuid,models.Application.is_deleted==False).all()
    

    @classmethod
    def create(cls,db:Session,*,obj_in:schemas.ApplicationCreate,candidate_uuid:str):
        job_offer = crud.offers.get_by_uuid(db=db,uuid=obj_in.job_offer_uuid)
        if not job_offer:
            raise HTTPException(status_code=404,detail=__(key="offers-not-found"))
        cover_letter= crud.storage_crud.get_file_by_uuid(db=db,file_uuid=obj_in.cover_letter_uuid)
        if not cover_letter:
            raise HTTPException(status_code=404,detail=__(key="cover-letter-not-found"))
        cv = crud.storage_crud.get_file_by_uuid(db=db,file_uuid=obj_in.cv_uuid)
        if not cv:
            raise HTTPException(status_code=404,detail=__(key="cv-not-found"))
        
        existing_application = db.query(models.Application).filter(
            models.Application.candidate_uuid == candidate_uuid,
            models.Application.job_offer_uuid == obj_in.job_offer_uuid
        ).first()

        if existing_application:
            raise HTTPException(status_code=400, detail=__(key="candidate-already-applied"))
        # Vérifier si l'offre est expirée
        if job_offer.expiration_date and job_offer.expiration_date < datetime.now():
            raise HTTPException(status_code=400, detail=__(key="offer-expired"))
        
        db_obj = models.Application(
            uuid=str(uuid.uuid4()),
            candidate_uuid=candidate_uuid,
            job_offer_uuid=obj_in.job_offer_uuid,
            cover_letter_uuid=obj_in.cover_letter_uuid,
            cv_uuid=obj_in.cv_uuid,    
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    

    @classmethod
    def update_status(cls,db:Session,*,uuid:str,status:str):
        db_obj = cls.get_by_uuid(db=db,uuid=uuid)
        if not db_obj:
            raise HTTPException(status_code=404,detail=__(key="application-not-found"))
        db_obj.status = status
        db.commit()

    @classmethod
    def delete(cls,db:Session,*,uuid:str):
        db_obj = cls.get_by_uuid(db=db,uuid=uuid)
        if not db_obj:
            raise HTTPException(status_code=404,detail=__(key="application-not-found"))
        db_obj.is_deleted = True
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
        status:Optional[str]=None
    ):
        
        if page < 1:
            page = 1

        record_query = db.query(models.Application).filter(models.Application.is_deleted==False)

        if keyword:
            record_query = record_query.filter(
                or_(
                    models.Application.candidate_uuid.ilike(f'%{keyword}%'),
                    models.Application.cover_letter.ilike(f'%{keyword}%'),
                )
            )

        if order and order_field and hasattr(models.Application, order_field):
            if order == "asc":
                record_query = record_query.order_by(getattr(models.Application, order_field).asc())
            else:
                record_query = record_query.order_by(getattr(models.Application, order_field).desc())
        if status:
            record_query = record_query.filter(models.Application.status==status)
        
        total = record_query.count()

        record_query = record_query.offset((page - 1) * per_page).limit(per_page).all()

        return schemas.ApplicationResponseList(
            total=total,
            pages=math.ceil(total / per_page),
            per_page=per_page,
            current_page=page,
            data=record_query
        )
    
    @classmethod
    def get_candidates_by_application(cls, db: Session, *, application_uuid: str):
        return db.query(models.Application).filter(
            models.Application.job_offer_uuid == application_uuid,
            models.Application.is_deleted == False
        ).all()
        
application = CRUDApplication(models.Application)