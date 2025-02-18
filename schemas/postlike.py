from typing import Optional
from pydantic import BaseModel


class PostLikeSchema(BaseModel):
    post_id: str