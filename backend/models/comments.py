from pydantic import BaseModel
from typing import Optional

class Comment(BaseModel):
    comment_id: int
    parent_comment_id: Optional[int]
    content: str
    comment_created_at: str
    comment_likes: int
    
class CommentRequest(BaseModel):
    content: str
    parent_comment_id: Optional[int] = None
