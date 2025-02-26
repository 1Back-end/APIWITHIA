from fastapi import APIRouter
from .migration_controller import router as migration
from .authentification_controller import router as authentication
from .user_controller import router as user
from .storage_controller import router as storage
from .job_offers_controllers import router as offers
from .candidate_controller import router as candidate
from .application_controller import router as application
from .analyse_controller import router as analyse


api_router = APIRouter()

api_router.include_router(migration)
api_router.include_router(authentication)
api_router.include_router(user)
api_router.include_router(storage)
api_router.include_router(offers)
api_router.include_router(candidate)
api_router.include_router(application)
api_router.include_router(analyse)
