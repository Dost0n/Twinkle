from fastapi import APIRouter
from routers import (user_route, login_route, post_route)

api_router = APIRouter()

api_router.include_router(login_route.router,    prefix="/login",  tags=["login"])
api_router.include_router(user_route.router,     prefix="/user",   tags=["user"])
api_router.include_router(post_route.router,     prefix="/post",   tags=["post"])