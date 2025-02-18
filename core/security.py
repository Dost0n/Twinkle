from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from fastapi import status,HTTPException
from db.session import get_db
from db.hashing import Hasher
from db.models import User
from schemas.users import UserShow
from datetime import datetime,timedelta
from typing import Optional
from jose import jwt, JWTError
from core.config import settings
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import or_


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/token")


def get_user(user_input:str, db: Session):
    user = db.query(User).filter(or_(User.username == user_input, User.phone_number == user_input, User.email == user_input)).first()
    return user


def authenticate_user(user_input: str, password: str, db: Session):
    user = get_user(user_input=user_input, db=db)
    if not user:
        return False
    if not Hasher.verify_password(password, user.password):
        return False
    return user


def get_current_user(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_input: str = payload.get("sub")
        if user_input is None:
            raise credentials_exception
        user = get_user(user_input, db )
        if user is None:
            raise credentials_exception
        return user
    except JWTError:
        raise credentials_exception


def get_current_admin_user(current_user: UserShow = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to perform this action",
        )
    return current_user    
    

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt