from fastapi import Depends, APIRouter, HTTPException, status
from sqlalchemy.orm import Session
from fastapi import status,HTTPException
from db.session import get_db
from schemas.login import LoginSchema
from schemas.users import AuthStatus
from datetime import timedelta
from core.config import settings
from core.security import authenticate_user, create_access_token
from db.models import User
from sqlalchemy import or_


router = APIRouter()


@router.post("")
def login_for_access_token(login: LoginSchema,db: Session= Depends(get_db)):
    print(login.user_input, login.password)
    db_user = db.query(User).filter(User.username == login.user_input or User.phone_number == login.user_input or User.email == login.user_input).filter(User.auth_status == AuthStatus.done).first()
    if db_user:
        raise HTTPException(status_code=400, detail="User not found!")
    user = authenticate_user(login.user_input, login.password, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username, phone number, email or password",
        )
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.phone_number}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}