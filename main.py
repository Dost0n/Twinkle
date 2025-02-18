from fastapi import FastAPI
from db.session import engine, Base
from core.config import settings
from routers.base import api_router
from routers.user_route import create_first_admin
from db.session import SessionLocal
import os


os.makedirs("uploaded_files", exist_ok=True)


def include_router(app):
    app.include_router(api_router, prefix="/api/v1")


def create_tables():
    Base.metadata.create_all(bind=engine)


def start_application():
    app = FastAPI(title=settings.PROJECT_NAME, version=settings.PROJECT_VERSION)
    include_router(app)
    create_tables()
    create_first_admin(db=SessionLocal())
    return app

app = start_application()
