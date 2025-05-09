from pydantic import BaseModel
from typing import Optional, List
from fastapi import UploadFile
from mobile_app.backend.models.location import Location

class VLMIssueCategoriserInput(BaseModel):
    text: str
    location: Location
    images: Optional[List[UploadFile]] = None