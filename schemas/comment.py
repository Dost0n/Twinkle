from typing import Optional
from pydantic import BaseModel
from schemas.users import UserShow


class CommentCreateSchema(BaseModel):
    comment :str


class CommentShowSchema(BaseModel):
    id      :int
    user    : UserShow
    comment :str