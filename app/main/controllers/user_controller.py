from datetime import timedelta, datetime
from typing import Any
from fastapi import APIRouter, Depends, Body, HTTPException
from sqlalchemy.orm import Session
from app.main.core.dependencies import get_db, TokenRequired
from app.main import schemas, crud, models
from app.main.core.i18n import __
from app.main.core.security import create_access_token, get_password_hash
from app.main.core.config import Config
from app.main.core.dependencies import TokenRequired

router = APIRouter(prefix="", tags=["users"])



@router.post("/register",response_model=schemas.Msg)
def register(
    *,
    db: Session = Depends(get_db),
    obj_in:schemas.UserCreate,
    current_user: models.User = Depends(TokenRequired(roles=["SUPER_ADMIN"]))
):
    exist_phone = crud.user.get_by_phone_number(db=db, phone_number=f"{obj_in.country_code}{obj_in.phone_number}")
    if exist_phone:
        raise HTTPException(status_code=409, detail=__(key="phone_number-already-used"))

    exist_email = crud.user.get_by_email(db=db, email=obj_in.email)
    if exist_email:
        raise HTTPException(status_code=409, detail=__(key="email-already-used"))
    crud.user.create(
        db, obj_in=obj_in
    )
    return schemas.Msg(message=__(key="user-created-successfully"))

@router.put("/actived/{uuid}", response_model=schemas.Msg)
def actived(
    uuid: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(TokenRequired(roles=["SUPER_ADMIN"]))
):
    # Appel de la fonction d'activation par UUID
    crud.user.actived_account(db=db, uuid=uuid)
    return schemas.Msg(message=__(key="user-account-activated-successfully"))


@router.put("/deactived/{uuid}", response_model=schemas.Msg)
def deactived(
    uuid: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(TokenRequired(roles=["SUPER_ADMIN"]))
):
    # Appel de la fonction d'activation par UUID
    crud.user.deactived_account(db=db, uuid=uuid)
    return schemas.Msg(message=__(key="user-account-deactivated-successfully"))

@router.put("/blocked/{uuid}", response_model=schemas.Msg)
def blocked(
    uuid: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(TokenRequired(roles=["SUPER_ADMIN"]))
):
    # Appel de la fonction d'activation par UUID
    crud.user.blocked_account(db=db, uuid=uuid)
    return schemas.Msg(message=__(key="user-account-blocked-successfully"))
    
@router.put("/deleted/{uuid}", response_model=schemas.Msg)
def delete(
    uuid: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(TokenRequired(roles=["SUPER_ADMIN"]))
):
    # Appel de la fonction d'activation par UUID
    crud.user.deleted_account(db=db, uuid=uuid)
    return schemas.Msg(message=__(key="user-account-deleted-successfully"))