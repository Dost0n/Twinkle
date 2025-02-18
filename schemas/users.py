from pydantic import BaseModel
from enum import Enum
from typing import Optional


class AuthType(str, Enum):
    via_email = 'via_email'
    via_phone = 'via_phone'


class AuthStatus(str, Enum):
    new = 'new'
    code_verified = 'code_verified'
    done = 'done'


class AuthRole(str, Enum):
    user = 'user'
    manager = 'manager'
    admin = 'admin'


class UserCreate(BaseModel):
    user_input :str
    auth_type  :AuthType = AuthType.via_phone


class UserConfirmation(BaseModel):
    code :str


class UserUpdate(BaseModel):
    username   :str
    first_name :Optional[str] = None
    last_name  :Optional[str] = None
    photo      :Optional[str] = None


class UserUpdatePassword(BaseModel):
    password             :str
    new_password         :str
    confirm_new_password :str


class UserShow(BaseModel):
    id           : int
    username     : str
    auth_role    : str
    auth_status  : str


class LoginSchema(BaseModel):
    phone_number :str
    password     :str


class Token(BaseModel):
    access_token : str
    token_type   : str