from fastapi import APIRouter, HTTPException
from schemas import CoordinateSchema
from app.utils.function_watershed import delineate_watershed


router = APIRouter()

@router.post('/delineate', response_model=dict)
async def delineate_watershed_route(coordinates: CoordinateSchema):
    """
    Delimita la cuenca hidrográfica a partir de un punto dado (latitud, longitud).
    
    :param coordinates: CoordinateSchema, latitud y longitud del punto de interés
    :return: dict, información de la cuenca delimitada o error
    """
    try:
        result = delineate_watershed(coordinates.latitude, coordinates.longitude)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))