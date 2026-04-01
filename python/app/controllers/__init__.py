"""
Controllers package
"""
from fastapi import APIRouter

from .order import router as order_router
from .export import router as export_router

# Create main API router
api_router = APIRouter()

# Include sub-routers
api_router.include_router(order_router, prefix="/orders", tags=["orders"])
api_router.include_router(export_router, prefix="/exports", tags=["exports"])

__all__ = ["api_router", "order_router", "export_router"]
