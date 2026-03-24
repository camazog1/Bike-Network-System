from typing import List, Optional

from pydantic import BaseModel, Field

from app.models.bike import BikeState, BikeType


class BikeCreate(BaseModel):
    brand: str = Field(..., min_length=1, max_length=100)
    type: BikeType
    colour: str = Field(..., min_length=1, max_length=50)
    state: BikeState = BikeState.Free


class BikeUpdate(BaseModel):
    brand: Optional[str] = Field(None, min_length=1, max_length=100)
    type: Optional[BikeType] = None
    colour: Optional[str] = Field(None, min_length=1, max_length=50)
    state: Optional[BikeState] = None


class BikeResponse(BaseModel):
    id: str
    brand: str
    type: BikeType
    colour: str
    state: BikeState

    model_config = {"from_attributes": True}


class BikeListResponse(BaseModel):
    bikes: List[BikeResponse]
    total: int
    page: int
    page_size: int
