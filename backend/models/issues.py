
from pydantic import BaseModel, Field, validator
from typing import Optional, List
from fastapi import UploadFile

class IssueReport(BaseModel):
    user_id: int
    latitude: float
    longitude: float
    address: Optional[str]
    description: str
    severity: Optional[int]
    status: str
    datetime_reported: str
    datetime_acknowledged: Optional[str]
    datetime_closed: Optional[str]
    datetime_updated: Optional[str]
    authority_id: int
    subzone_id: Optional[int]
    planning_area_id: Optional[int]
    is_public: bool

    @validator('latitude')
    def validate_latitude(cls, v):
        if not -90 <= v <= 90:
            raise ValueError('Latitude must be between -90 and 90')
        return v

    @validator('longitude')
    def validate_longitude(cls, v):
        if not -180 <= v <= 180:
            raise ValueError('Longitude must be between -180 and 180')
        return v

class Location(BaseModel):
    latitude: float
    longitude: float
    address: str

    @validator('latitude')
    def validate_latitude(cls, v):
        if not -90 <= v <= 90:
            raise ValueError('Latitude must be between -90 and 90')
        return v

    @validator('longitude')
    def validate_longitude(cls, v):
        if not -180 <= v <= 180:
            raise ValueError('Longitude must be between -180 and 180')
        return v


class Proximity(BaseModel):
    latitude: float
    longitude: float
    radius: float  # in meters

    @validator('latitude')
    def validate_latitude(cls, v):
        if not -90 <= v <= 90:
            raise ValueError('Latitude must be between -90 and 90')
        return v

    @validator('longitude')
    def validate_longitude(cls, v):
        if not -180 <= v <= 180:
            raise ValueError('Longitude must be between -180 and 180')
        return v
    
class IssueFilter(BaseModel):
    from_: Optional[str] = Field(None, alias="from")
    to: Optional[str] = None
    types: Optional[str] = None
    subtypes: Optional[str] = None
    severity: Optional[str] = None
    status: Optional[str] = None
    subzone_name: Optional[str] = None
    page: Optional[int] = 1
    limit: Optional[int] = 10000
    proximity: Optional[Proximity] = None


# class VLMIssueCategoriserInput(BaseModel):
#     text: str
#     location: Location
#     images: Optional[List[UploadFile]] = None