from typing import List, Optional
from pydantic import BaseModel
from schemas.users import UserShow


class CommentCreateSchema(BaseModel):
    comment :str


class CommentShowSchema(BaseModel):
    id      :int
    user    : UserShow
    comment :str


class PostShowSchema(BaseModel):
    caption   :Optional[str] = None
    file_url  :str
    file_type :str
    user      :UserShow
    comments  :List[CommentShowSchema]


class PostLikeShowSchema(BaseModel):
    id   :int
    user : UserShow


class PostDislikeShowSchema(BaseModel):
    id   :int
    user : UserShow


class CommentLikeShowSchema(BaseModel):
    id   :int
    user : UserShow


class CommentDislikeShowSchema(BaseModel):
    id   :int
    user : UserShow


