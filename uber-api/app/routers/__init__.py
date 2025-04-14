from fastapi import APIRouter
from .incoming import router as incoming_router
from .usage_history import router as usage_history_router
from .riser_management import router as risermanagement_router
from .riser_usage_history import router as riserusage_router

router = APIRouter()

router.include_router(incoming_router, prefix="/nic/incoming", tags=["Incoming NICs"])
router.include_router(usage_history_router, prefix="/nic/usage", tags=["Usage History"])
router.include_router(risermanagement_router, prefix="/riser/management", tags=["Riser 관리"])
router.include_router(riserusage_router, prefix="/riser/usage", tags=["Riser 사용 이력"])
