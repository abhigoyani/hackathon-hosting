from pydantic import BaseModel
from typing import Optional


class PrizeCreateRequest(BaseModel):
    title: str
    description: str


class PrizePatchRequest(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
