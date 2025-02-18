from typing import Optional
from pydantic import BaseModel


class CommentCreateSchema(BaseModel):
    comment :str
    post_id :str


class CommentShowSchema(BaseModel):
    comment :str