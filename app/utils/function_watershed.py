from pysheds.grid import Grid
from math import radians, sin, cos, sqrt, atan2
import geopandas as gpd
import rasterio
from rasterio.features import shapes
from shapely import geometry, ops
import json

def delineate_watershed(latitude, longitude):
    """
    Delimita la cuenca hidrográfica a partir de un punto dado (latitud, longitud).

    :param latitude: float, latitud del punto de interés
    :param longitude: float, longitud del punto de interés
    :return: Diccionario que contiene el array 'catchment', las elevaciones máxima y mínima,
             los puntos máximo y mínimo, y la longitud del río
    """
    try:
        # Leer el raster de elevación
        grid = Grid.from_raster('D:/2024/USAL/TIDOP/E-Hydro/data/guadiana_wgs84.tif')
        dem = grid.read_raster('D:/2024/USAL/TIDOP/E-Hydro/data/guadiana_wgs84.tif')
        # Determinar las direcciones de flujo D8 a partir del DEM
        fdir = grid.read_raster('D:/2024/USAL/TIDOP/E-Hydro/data/flow_fdir.tif')
        # Acumulación de flujo
        acc = grid.read_raster('D:/2024/USAL/TIDOP/E-Hydro/data/flow_accumulation.tif')

        dirmap = (64, 128, 1, 2, 4, 8, 16, 32)
        # Delimitar una cuenca
        x, y = longitude, latitude

        # Ajustar el punto de vertido a la celda de alta acumulación
        x_snap, y_snap = grid.snap_to_mask(acc > 1000, (x, y))

        # Delimitar la cuenca
        catch = grid.catchment(x=x_snap, y=y_snap, fdir=fdir, dirmap=dirmap, xytype='coordinate')
        
        # Recortar y mostrar la cuenca
        grid.clip_to(catch)
        clipped_catch = grid.view(catch)
        # raster to geojson
        shapes = grid.polygonize()
        catchment_polygon = ops.unary_union([geometry.shape(shape)for shape, value in shapes])
        gdf = gpd.GeoDataFrame([{'geometry': catchment_polygon}], crs=grid.crs)
        json_catchment = json.loads(gdf.to_json())

        # Calcular el área de la cuenca
        gdf = gdf.to_crs(epsg=32630)  

        # Calcular el área en metros cuadrados después de cambiar el CRS
        areas_km2 = (gdf['geometry'].area)/10**6
        areas_km2=areas_km2[0]
        print("Áreas calculadas en kilometro cuadrados:", areas_km2)
        # Extraer la red de ríos
        branches = grid.extract_river_network(fdir, acc > 500, dirmap=dirmap)
        
        # Tamaño del píxel a partir de la transformación afín
        affine = grid.affine
        dem_array = grid.view(dem, apply_mask=False)

        # Función para obtener la elevación usando la transformación afín
        def get_elevation(x, y, no_data=-99999.0):
            col, row = ~affine * (x, y)
            col, row = int(round(col)), int(round(row))
            if 0 <= row < dem_array.shape[0] and 0 <= col < dem_array.shape[1]:
                elevation = dem_array[row, col]
                if elevation == no_data:
                    return None
                return elevation
            return None
        
        # Recalcular para el punto específico más bajo
        max_elevation = float('-inf')
        min_elevation = float('inf')
        max_point = None
        min_point = None

        for branch in branches['features']:
            for coord in branch['geometry']['coordinates']:
                elevation = get_elevation(coord[0], coord[1])
                if elevation is not None:
                    if elevation > max_elevation:
                        max_elevation = elevation
                        max_point = coord
                    if elevation < min_elevation:
                        min_elevation = elevation
                        min_point = coord

        print(f"Elevación máxima: {max_elevation} metros en {max_point}")
        print(f"Elevación mínima: {min_elevation} metros en {min_point}")

        def find_river_path(branches, max_point, min_point):
            return [max_point, min_point]
        
        def haversine_distance(coords1, coords2):
            R = 6371000  # Radio de la Tierra en metros
            lat1, lon1 = radians(coords1[1]), radians(coords1[0])
            lat2, lon2 = radians(coords2[1]), radians(coords2[0])
            dlat = lat2 - lat1
            dlon = lon2 - lon1
            a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
            c = 2 * atan2(sqrt(a), sqrt(1 - a))
            return R * c

        def calculate_river_path_length(branches, max_point, min_point):
            river_path = find_river_path(branches, max_point, min_point)  # Esta función necesita ser desarrollada
            total_length = 0
            for i in range(len(river_path) - 1):
                distance = haversine_distance(river_path[i], river_path[i + 1])
                total_length += distance
            return total_length

        river_length = calculate_river_path_length(branches, max_point, min_point)
        print(f"Longitud del río: {river_length} metros")

        # Calculo de la pendiente de la cuenca
        slope = ((max_elevation - min_elevation) / river_length) * 100
        print(f"Pendiente de la cuenca: {slope} %")

        return {
            'catchment': json_catchment,
            'branches': branches,
            'area': areas_km2,
            'max_elevation': max_elevation,
            'min_elevation': min_elevation,
            'max_point': max_point,
            'min_point': min_point,
            'river_length': river_length,
            'slope': slope
        }

    except Exception as e:
        print(f"Error procesando el DEM: {e}")
        return {'error': str(e)}

