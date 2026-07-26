from fastapi import APIRouter
from app.api import plan, user, product

api_router = APIRouter()

api_router.include_router(plan.router, prefix="/plan", tags=["plan"])
api_router.include_router(user.router, prefix="/user", tags=["user"])
api_router.include_router(product.router, prefix="/product", tags=["product"])
