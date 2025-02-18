from fastapi import APIRouter, Query
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException
from db.session import get_db
from typing import List
from db.models import User, Confirmation
from schemas.users import UserShow, UserCreate, UserUpdate,UserUpdatePassword, AuthType, AuthStatus, AuthRole, UserConfirmation
from db.hashing import Hasher
from core.security import get_current_user, get_current_admin_user
from core.config import settings
import random
import uuid
from datetime import datetime, timedelta
from core.security import create_access_token

router = APIRouter()


def create_first_admin(db):
    admin_exists = db.query(User).filter(User.auth_role == AuthRole.admin).first()
    if not admin_exists:
        admin = User(username=settings.ADMIN_FIRST_NAME, phone_number=settings.ADMIN_FIRST_PHONE, auth_role=AuthRole.admin,
                     auth_status=AuthStatus.done, password=Hasher.get_password_hash(settings.ADMIN_FIRST_PASSWORD))
        db.add(admin)
        db.commit()
        db.refresh(admin)
    db.close()


@router.post("/create")
def create_confirmation(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.phone_number == user.user_input or User.email == user.user_input).first()
    if db_user:
        raise HTTPException(status_code=400, detail="This user already registered")
    temp_username = f"instagram-{uuid.uuid4().__str__().split('-')[-1]}"
    temp_password = f"password-{uuid.uuid4().__str__().split('-')[-1]}"
    hashed_password = Hasher.get_password_hash(temp_password)
    if user.auth_type =="via_email":
        new_user = User(username=temp_username, auth_type=user.auth_type, email=user.user_input, auth_role=AuthRole.user,
                        auth_status=AuthStatus.new, password=hashed_password)
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        code = create_verify_code(db, new_user.id, new_user.auth_type)
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.user_input}, expires_delta=access_token_expires
        )
        return {"code": code, "access_token": access_token, "token_type": "bearer"}
    if user.auth_type == "via_phone":
        new_user = User(username=temp_username, auth_type=user.auth_type, phone_number=user.user_input, auth_role=AuthRole.user,
                        auth_status=AuthStatus.new, password=hashed_password)
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        code = create_verify_code(db, new_user.id, new_user.auth_type)
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.user_input}, expires_delta=access_token_expires
        )
        return {"code": code, "access_token": access_token, "token_type": "bearer"}
    else:
        return {"error": "Auth type error"}
        

def create_verify_code(db, user_id, verify_type):
    code = "".join([str(random.randint(0,100) % 10) for _ in range(4)])
    if verify_type == "via_email":
        expiration_time = datetime.now()+timedelta(minutes=5)
    else:
        expiration_time = datetime.now()+timedelta(minutes=2)
    new_confirmation = Confirmation(user_id = user_id, verify_type= verify_type, expiration_time=expiration_time, code = code)
    db.add(new_confirmation)
    db.commit()
    db.refresh(new_confirmation)
    return code


@router.post("/confirmation")
def confirmation_user(confirmation: UserConfirmation, db: Session = Depends(get_db), current_user: UserShow = Depends(get_current_user)):
    if current_user.auth_status!=AuthStatus.new:
        raise HTTPException(status_code=400, detail="This user not access")
    else:
        code = confirmation.code
        verify = db.query(Confirmation).filter(Confirmation.expiration_time>=datetime.now()).filter(Confirmation.code == code).filter(Confirmation.is_isconfirmed == False).first()
        if verify:
            current_user.auth_status = AuthStatus.code_verified
            db.commit()
            db.refresh(current_user)
            access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
            if current_user.auth_type == AuthType.via_email:
                access_token = create_access_token(data={"sub": current_user.email}, expires_delta=access_token_expires)
            if current_user.auth_type == AuthType.via_phone:
                access_token = create_access_token(data={"sub": current_user.phone_number}, expires_delta=access_token_expires)
            return {"access_token": access_token, "token_type": "bearer"}
        else:
            return {"message":"Tasdiqlash kodingiz xato yoki eskirgan"}


@router.get("/all")
def get_users(db: Session = Depends(get_db), skip: int = Query(0, ge=0), limit: int = Query(10, le=100)):
    users = db.query(User).all()[skip: skip + limit]
    total_users = len(db.query(User).all())
    if skip >= total_users:
        raise HTTPException(status_code=400, detail="Skip value is too large")
    return {"users": users, "total_users": total_users}


@router.get("/get", response_model=UserShow)
def get_user(db: Session = Depends(get_db), current_user: UserShow = Depends(get_current_user)):
    db_user = db.query(User).filter(User.id == current_user.id).first()
    return db_user


@router.patch("/update", response_model=UserShow)
def update_user_status(update: UserUpdate, db: Session = Depends(get_db), current_user: UserShow = Depends(get_current_user)):
    db_user = db.query(User).filter(User.id == current_user.id).first()
    if update.username:
        db_user = db.query(User).filter(User.username == update.username).first()
        if db_user:
            raise HTTPException(status_code=400, detail="This username already registered")
        db_user.username = update.username
    if update.first_name:
        db_user.first_name = update.first_name
    if update.last_name:
        db_user.last_name = update.last_name
    if update.photo:
        db_user.photo = update.photo
    db_user.auth_status = AuthStatus.done
    db.commit()
    db.refresh(db_user)
    return db_user


@router.patch("/update-password", response_model=UserShow)
def update_user(user_id:int, password: UserUpdatePassword, db: Session = Depends(get_db), current_user: UserShow = Depends(get_current_user)):
    db_user = db.query(User).filter(User.id == user_id).first()
    if not Hasher.verify_password(password.password, db_user.hashed_password):
        raise HTTPException(status_code=404, detail="User password incorrect!")
    if password.new_password!=password.confirm_new_password:
        raise HTTPException(status_code=400, detail="New Password and confirm new pasword not equal!")
    db_user.hashed_password = Hasher.get_password_hash(password.new_password)
    db.commit()
    db.refresh(db_user)
    return db_user