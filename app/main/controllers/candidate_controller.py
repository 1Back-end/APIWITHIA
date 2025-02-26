from datetime import timedelta, datetime
from typing import Any, Optional
from fastapi import APIRouter, Depends, Body, HTTPException, Query
from sqlalchemy.orm import Session
from app.main.core.dependencies import get_db, TokenRequired
from app.main import schemas, crud, models
from app.main.core.i18n import __
from app.main.core.security import create_access_token, get_password_hash
from app.main.core.config import Config
from app.main.core.dependencies import TokenRequired

router = APIRouter(prefix="/candidate", tags=["candidate"])


@router.post("/login", response_model=schemas.CandidateAuthentication)
async def login(
        obj_in: schemas.CandidateLogin,
        db: Session = Depends(get_db),
) -> Any:
    """
    Sign in with email and password
    """
    candidate = crud.candidate.authenticate(
        db, email=obj_in.email, password=obj_in.password
    )
    if not candidate:
        raise HTTPException(status_code=400, detail=__(key="auth-login-failed"))
    if candidate.is_deleted==True:
        raise HTTPException(status_code=400, detail=__(key="auth-login-failed"))
    access_token_expires = timedelta(minutes=Config.ACCESS_TOKEN_EXPIRE_MINUTES)

    # Convertir le candidat en modèle Pydantic avec from_orm
    return {
        "candidat": schemas.CandidateSlim.from_orm(candidate),  # Utiliser from_orm pour transformer en modèle Pydantic
        "token": {
            "access_token": create_access_token(
                candidate.uuid, expires_delta=access_token_expires
            ),
            "token_type": "bearer",
        }
    }



@router.post("/create", response_model=schemas.Candidate)
def create_candidate(
    candidate: schemas.CandidateCreate, 
    db: Session = Depends(get_db)
):
    exist_email = crud.candidate.get_by_email(db=db,email=candidate.email)
    if exist_email:
        raise HTTPException(status_code=404, detail=__(key="email-is-already-exist"))
    
    exist_phone_number = crud.candidate.get_by_phone_number(db=db,phone_number=candidate.phone_number)
    if exist_phone_number:
        raise HTTPException(status_code=404, detail=__(key="phone-number-is-already-exist"))

    if candidate.avatar_uuid:
        avatar = crud.storage_crud.get_file_by_uuid(db=db,file_uuid=candidate.avatar_uuid)
        if not avatar:
            raise HTTPException(status_code=404, detail=__(key="avatar-not-found"))
    if candidate.cv_uuid:
        cv = crud.storage_crud.get_file_by_uuid(db=db,file_uuid=candidate.cv_uuid)
        if not cv:
            raise HTTPException(status_code=404, detail=__(key="cv-not-found"))
        
    # Appel au CRUD pour créer un candidat et ses expériences
    return crud.candidate.create(db=db,candidate=candidate)
    

@router.get("/get_many", response_model=None)
async def get_many_candidate(
    *,
    db: Session = Depends(get_db),
    page: int = 1,
    per_page: int = 30,
    order: str = Query(None, enum=["ASC", "DESC"]),
    keyword: Optional[str] = None,
    order_field: Optional[str] = None,  # Correction de order_filed → order_field
    current_user: models.User = Depends(TokenRequired(roles=["SUPER_ADMIN"]))
):
    return crud.candidate.get_multi(
        db=db,
        page=page,
        per_page=per_page,
        order=order,
        order_field=order_field,  # Correction ici aussi
        keyword=keyword,
        
    )

@router.get("/get_by_uuid",response_model=schemas.Candidate)
def get_candidate_by_uuid(
    *,
    uuid:str, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(TokenRequired(roles=["SUPER_ADMIN"]))
):
    return crud.candidate.get_by_uuid(db=db, uuid=uuid)
    
