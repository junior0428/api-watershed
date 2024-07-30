from pydantic import BaseModel
from typing import List, Dict

class CoordinateSchema(BaseModel):
    latitude: float
    longitude: float

class CatchmentResponse(BaseModel):
    catchment: Dict
    max_elevation: float
    min_elevation: float
    max_point: List
    min_point: List