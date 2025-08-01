from fastapi import APIRouter

from .endpoints import auth

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])

# TODO: Add other routers as they are created
# api_router.include_router(accounts.router, prefix="/accounts", tags=["accounts"])
# api_router.include_router(transactions.router, prefix="/transactions", tags=["transactions"])
# api_router.include_router(notifications.router, prefix="/notifications", tags=["notifications"])
# api_router.include_router(admin.router, prefix="/admin", tags=["admin"])