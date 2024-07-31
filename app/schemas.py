from pydantic import BaseModel, validator
from typing import List, Dict, Any

class CoordinateSchema(BaseModel):
    latitude: float
    longitude: float

class CatchmentResponse(BaseModel):
    catchment: Dict
    branches: Dict
    area: float
    max_elevation: float
    min_elevation: float
    max_point: List[float]
    min_point: List[float]
    river_length: float
    slope: float
