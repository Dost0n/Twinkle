from typing import List, Optional
from pydantic import BaseModel
from schemas.comment import CommentShowSchema
from schemas.users import UserShow

class PostCreateSchema(BaseModel):
    caption: Optional[str] = None


class PostShowSchema(BaseModel):
    caption   :Optional[str] = None
    
    file_url  :str
    file_type :str
    user      :UserShow
    comments  :List[CommentShowSchema]
