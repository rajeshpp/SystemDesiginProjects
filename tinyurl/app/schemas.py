from pydantic import BaseModel, HttpUrl, Field
from typing import Optional
from datetime import datetime

class URLBase(BaseModel):
    url: HttpUrl
    expiry_days: Optional[int] = Field(default=None, gt=0)

class URLInfo(BaseModel):
    long_url: str
    short_code: str
    created_at: datetime
    expiry_date: Optional[datetime]

    class Config:
        orm_mode = True

class URLRequest(BaseModel):
    url: HttpUrl
    expiry_days: Optional[int] = None

class URLResponse(BaseModel):
    short_url: str