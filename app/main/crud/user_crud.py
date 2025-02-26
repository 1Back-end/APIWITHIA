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

class CRUDUser(CRUDBase[models.User, schemas.UserCreate, schemas.UserUpdate]):

    @classmethod
    def get_by_phone_number(cls, db: Session, *, phone_number: str) -> Union[models.User, None]:
        return db.query(models.User).filter(models.User.full_phone_number == phone_number).first()

    @classmethod
    def get_by_email(cls, db: Session, *, email: str) -> Union[models.User, None]:
        return db.query(models.User).filter(models.User.email == email).first()
    @classmethod
    def get_by_uuid(cls, db: Session, *, uuid: str) -> Union[models.User, None]:
        return db.query(models.User).filter(models.User.uuid == uuid).first()

    @classmethod
    def create(cls,db:Session,*,obj_in:schemas.UserCreate)->models.User:
        password: str = generate_password(8, 8)
        print(f"User password: {password}")
        # hashed_password = get_password_hash(obj_in.password_hash)
        new_user = models.User(
            uuid=str(uuid.uuid4()),
            email = obj_in.email,
            full_phone_number=f"{obj_in.country_code}{obj_in.phone_number}",
            country_code=obj_in.country_code,
            phone_number=obj_in.phone_number,
            password_hash=get_password_hash(password),
            first_name=obj_in.first_name,
            last_name=obj_in.last_name,
            role=obj_in.role
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        send_account_creation_email(email_to=obj_in.email, first_name=obj_in.first_name,last_name=obj_in.last_name,
                                    password=password)
        return new_user
    @classmethod
    def authenticate(cls, db: Session, *, email: str, password: str) -> Union[models.User, None]:
        db_obj: models.User = db.query(models.User).filter(models.User.email == email).first()
        if not db_obj:
            return None
        if not verify_password(password, db_obj.password_hash):
            return None
        return db_obj
    
    @classmethod
    def actived_account(cls,db:Session,*,uuid:str):
        user = cls.get_by_uuid(db=db,uuid=uuid)
        if user is None:
            raise HTTPException(status_code=404, detail=__("user-not-found"))
        user.status = models.UserStatus.ACTIVED
        db.commit() #
    @classmethod
    def deactived_account(cls,db:Session,*,uuid:str):
        user = cls.get_by_uuid(db=db,uuid=uuid)
        if user is None:
            raise HTTPException(status_code=404, detail=__("user-not-found"))
        user.status = models.UserStatus.UNACTIVED
        db.commit() #
    @classmethod
    def blocked_account(cls,db:Session,*,uuid:str):
        user = cls.get_by_uuid(db=db,uuid=uuid)
        if user is None:
            raise HTTPException(status_code=404, detail=__("user-not-found"))
        user.status = models.UserStatus.BLOCKED
        db.commit() #
    @classmethod
    def deleted_account(cls,db:Session,*,uuid:str):
        user = cls.get_by_uuid(db=db,uuid=uuid)
        if user is None:
            raise HTTPException(status_code=404, detail=__("user-not-found"))
        user.status = models.UserStatus.DELETED
        db.commit() #
    
    
    
    

    



    
user = CRUDUser(models.User)