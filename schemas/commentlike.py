from typing import Optional
from pydantic import BaseModel


class CommentLikeSchema(BaseModel):
    comment_id: str