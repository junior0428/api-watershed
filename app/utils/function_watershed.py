import rasterio
from pysheds.grid import Grid
import numpy as np

lat = 30.842202
lon = -96.677951

def delineate_watershed(latitude, longitude, dem_path='../../data/elevation.tiff'):
    """
    Delimita la cuenca hidrográfica a partir de un punto dado (latitud, longitud).
    
    :param latitude: float, latitud del punto de interés
    :param longitude: float, longitud del punto de interés
    :param dem_path: str, ruta al archivo DEM (Modelo Digital de Elevación)
    :return: dict, información de la cuenca delimitada o error
    """
    try:
        # Carga el DEM
        with rasterio.open(dem_path) as src:
            # Transforma coordenadas geográficas a coordenadas del raster
            row, col = src.index(longitude, latitude)
            
            # Lee los datos del raster
            elevation = src.read(1)

        # Inicializa un objeto Grid de PySheds
        grid = Grid()
        grid.add_gridded_data(elevation, 'elevation', affine=src.transform)

        # Llena los sumideros y resuelve los máximos locales
        grid.fill_depressions('elevation', out_name='flooded_elevation')
        grid.resolve_flats('flooded_elevation', out_name='inflated_elevation')

        # Calcula el flujo de dirección
        grid.flowdir(data='inflated_elevation', out_name='dir')

        # Determina la cuenca a partir del punto dado
        catchment = grid.catchment(x=col, y=row, dirmap=grid.dir, out_name='catchment')

        # Máscara la cuenca para operaciones futuras
        masked_catchment = grid.view('catchment', nodata=np.nan)

        # Genera la información de salida (aquí solo retornamos un resumen)
        output = {
            'catchment_area': np.nansum(masked_catchment) * (src.res[0] * src.res[1])
        }
        return output

    except Exception as e:
        return {'error': str(e)}
    
    if __name__ == '__main__':
        result = delineate_watershed(lat, lon)
        print("Resultado de la delimitación de la cuenca hidrográfica:", result)

