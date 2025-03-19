from datetime import timedelta, datetime
from typing import Any, List, Optional
from fastapi import APIRouter, Depends, Body, HTTPException, Query
from sqlalchemy.orm import Session
from app.main.core.dependencies import get_db, TokenRequired
from app.main import schemas, crud, models
from app.main.core.i18n import __
from app.main.core.config import Config
from app.main.core.dependencies import CandidateTokenRequired

router = APIRouter(prefix="/application", tags=["application"])

@router.post("/create",response_model=schemas.Msg)
def applied_offers(
    *,
    db: Session = Depends(get_db),
    obj_in:schemas.ApplicationCreate,
    current_user: models.Candidat = Depends(CandidateTokenRequired())
):
    candidate_uuid = current_user.uuid
    crud.application.create(db=db,obj_in=obj_in,candidate_uuid=candidate_uuid)
    return schemas.Msg(message=__(key="offer-applied-successfully"))

@router.post("/update-status",response_model=schemas.Msg)
def create_offers(
    *,
    db: Session = Depends(get_db),
    obj_in:schemas.ApplicationDetails,
    status: str = Query(..., enum=[st.value for st in models.ApplicationStatusEnum]),
    current_user: models.User = Depends(TokenRequired(roles=["SUPER_ADMIN"]))
):
    crud.application.update_status(db=db,uuid=obj_in.uuid,status=status)
    return schemas.Msg(message=__(key="application-status-update-successfully"))

@router.delete("/delete",response_model=schemas.Msg)
def delete_offers(
    *,
    db: Session = Depends(get_db),
    obj_in:schemas.ApplicationDetails,
    current_user: models.User = Depends(TokenRequired(roles=["SUPER_ADMIN"]))
):
    crud.application.delete(db=db,obj_in=obj_in)
    return schemas.Msg(message=__(key="application-delete-successfully"))

@router.get("/get_many", response_model=None)
async def get_many_offers(
    *,
    db: Session = Depends(get_db),
    page: int = 1,
    per_page: int = 30,
    order: str = Query(None, enum=["ASC", "DESC"]),
    status: str = Query(..., enum=[st.value for st in models.ApplicationStatusEnum]),
    keyword: Optional[str] = None,
    order_field: Optional[str] = None,  # Correction de order_filed → order_field
    current_user: models.User = Depends(TokenRequired(roles=["SUPER_ADMIN"]))
):
    return crud.application.get_multi(
        db=db,
        page=page,
        per_page=per_page,
        order=order,
        status=status,
        order_field=order_field,  # Correction ici aussi
        keyword=keyword,
        
    )

@router.get("/get_candidate_by_offers", response_model=List[schemas.CandidateResponse])
def get_candidate_by_offers(
    *,
    db: Session = Depends(get_db),
    application_uuid: str
):
    return crud.application.get_candidates_by_application(db=db, application_uuid=application_uuid)