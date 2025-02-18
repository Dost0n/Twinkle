from pydantic import BaseModel


class LoginSchema(BaseModel):
    user_input: str
    password: str