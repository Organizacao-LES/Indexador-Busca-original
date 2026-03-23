# app/api/v1/router.py
from fastapi import APIRouter
from app.api.v1.auth_routes import router as auth_router
from app.api.v1.user_routes import router as user_router

api_router = APIRouter()

api_router.include_router(auth_router)
api_router.include_router(user_router)