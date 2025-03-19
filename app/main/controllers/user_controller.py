from datetime import timedelta, datetime
from typing import Any
from fastapi import APIRouter, Depends, Body, HTTPException, Query
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

@router.put("/update-status",response_model=schemas.Msg)
def update_status(
    *,
    db: Session = Depends(get_db),
    obj_in:schemas.UpdateStatus,
    status: str = Query(..., enum=[st.value for st in models.UserStatus]),
):
    crud.user.update(
        db,
        uuid=obj_in.uuid,
        status=status
    )
    return schemas.Msg(message=__(key="user-status-updated-successfully"))