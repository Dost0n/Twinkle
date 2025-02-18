from typing import Optional
from pydantic import BaseModel
from schemas.users import UserShow


class PostLikeShowSchema(BaseModel):
    id   :int
    user : UserShow