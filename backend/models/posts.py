from pydantic import BaseModel
from typing import List, Optional
from comments import Comment

class Post(BaseModel):
    issue_id: int
    user_id: int
    issue_type_id: List[int]
    issue_subcategory_id: Optional[List[int]]
    latitude: float
    longitude: float
    address: Optional[str]
    location: str
    description: Optional[str]
    severity: Optional[int]
    status: str
    datetime_reported: str
    datetime_acknowledged: Optional[str]
    datetime_closed: Optional[str]
    datetime_updated: str
    agency_id: Optional[int]
    town_council_id: Optional[int]
    subzone_id: Optional[int]
    planning_area_id: Optional[int]
    is_public: bool
    post_id: Optional[int]
    created_at: str
    comment_count: int
    post_likes: int
    comments: List[Comment] = []