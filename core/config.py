import os
from dotenv import load_dotenv

from pathlib import Path
env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)


class Settings:
    PROJECT_NAME           :str = "FastAPI project"
    PROJECT_VERSION        :str = "1.0.0"

    POSTGRES_USER          :str = os.getenv("POSTGRES_USER")
    POSTGRES_PASSWORD           = os.getenv("POSTGRES_PASSWORD")
    POSTGRES_SERVER        :str = os.getenv("POSTGRES_SERVER","localhost")
    POSTGRES_PORT          :str = os.getenv("POSTGRES_PORT",5432)
    POSTGRES_DB            :str = os.getenv("POSTGRES_DB","tdd")
    # DATABASE_URL                = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_SERVER}:{POSTGRES_PORT}/{POSTGRES_DB}"
    DATABASE_URL = "sqlite:///./test.db"

    SECRET_KEY           :str = os.getenv("SECRET_KEY")   
    ALGORITHM            = "HS256"                         
    ACCESS_TOKEN_EXPIRE_MINUTES = 30
    ADMIN_FIRST_NAME :str = os.getenv("ADMIN_FIRST_NAME")
    ADMIN_FIRST_PASSWORD :str = os.getenv("ADMIN_FIRST_PASSWORD")
    ADMIN_FIRST_PHONE :str = os.getenv("ADMIN_FIRST_PHONE")
    
settings = Settings()
