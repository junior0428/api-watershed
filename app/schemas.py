from pydantic import BaseModel

class CoordinateSchema(BaseModel):
    latitude: float
    longitude: float

class RasterModel (BaseModel):
    catchment: list