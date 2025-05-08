from pydantic import BaseModel
from typing import Optional

class CommentRequest(BaseModel):
    content: str
    parent_comment_id: Optional[int] = None
