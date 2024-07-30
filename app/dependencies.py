import matplotlib.pyplot as plt
from pysheds.grid import Grid
import numpy as np
import seaborn as sns
import matplotlib.colors as colors
from shapely.geometry import LineString
from math import radians, sin, cos, sqrt, atan2
import geopandas as gpd
import rasterio
from rasterio.features import shapes
from shapely.geometry import shape
import json

grid = Grid.from_raster('/home/tidop/2024/usal/tidop/github/api-watershed/data/guadiana_wgs84.tif')
dem = grid.read_raster('/home/tidop/2024/usal/tidop/github/api-watershed/data/guadiana_wgs84.tif')

direc = grid.read_raster('/home/tidop/2024/usal/tidop/github/api-watershed/data/flow_fdir.tif')
acumula = grid.read_raster('/home/tidop/2024/usal/tidop/github/api-watershed/data/flow_accumulation.tif')
dirmap = (64, 128, 1, 2, 4, 8, 16, 32)

x, y = -4.758253, 38.491025
# Snap pour point to high accumulation cell
x_snap, y_snap = grid.snap_to_mask(acumula > 1000, (x, y))

# Delineate the catchment
catch = grid.catchment(x=x_snap, y=y_snap, fdir=direc, dirmap=dirmap, 
                       xytype='coordinate')

# Crop and plot the catchment
# ---------------------------
# Clip the bounding box to the catchment
grid.clip_to(catch)
clipped_catch = grid.view(catch)
print(catch)

# raster to geojson
# -----------------
mask = clipped_catch != grid.nodata
transform = grid.transform
polygons = [shape(geom) for geom, value in shapes(clipped_catch, mask=mask, transform=transform) if value == 1]
gdf = gpd.GeoDataFrame({'geometry': polygons}, crs='EPSG:4326')
geojson = json.loads(gdf.to_json())
print(type(geojson))
# Extract river network
# ---------------------
branches = grid.extract_river_network(direc, acumula > 500, dirmap=dirmap)
print(type(branches))


# Convertir el DEM a un array para un acceso más rápido
dem_array = grid.view(dem, apply_mask=False)
# Obtener la transformación afín del grid
affine = grid.affine
# Función para obtener la elevación usando la transformación afín
def get_elevation(x, y, no_data=-99999.0):
    col, row = ~affine * (x, y)
    col, row = int(round(col)), int(round(row))  # Asegurar redondeo correcto para índices
    if 0 <= row < dem_array.shape[0] and 0 <= col < dem_array.shape[1]:
        elevation = dem_array[row, col]
        if elevation == no_data:  # Verificar explícitamente el valor de 'no data'
            return None
        return elevation
    return None

# Recalcular para el punto bajo específico
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

print(f"El punto más alto del río está en las coordenadas {max_point} con una altitud de {max_elevation} metros")
print(f"El punto más bajo del río debería estar en las coordenadas {min_point} con una altitud de {min_elevation} metros")

# Simulando una función que devuelve la ruta del río (esto es solo un placeholder)
def find_river_path(branches, max_point, min_point):
    # Implementación específica necesaria aquí, este es un ejemplo genérico
    return [max_point, min_point]  # Ruta simplificada entre los puntos

def haversine_distance(coords1, coords2):
    """ Calcula la distancia del haversine entre dos puntos geográficos en metros. """
    R = 6371000  # Radio de la Tierra en metros
    lat1, lon1 = radians(coords1[1]), radians(coords1[0])
    lat2, lon2 = radians(coords2[1]), radians(coords2[0])

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    distance = R * c
    return distance

def calculate_river_path_length(branches, max_point, min_point):
    river_path = find_river_path(branches, max_point, min_point)  # Esta función necesita ser desarrollada
    total_length = 0
    for i in range(len(river_path) - 1):
        distance = haversine_distance(river_path[i], river_path[i + 1])
        total_length += distance
    return total_length

river_length = calculate_river_path_length(branches, max_point, min_point)
print(f"Longitud total del río principal desde el punto más alto al más bajo: {river_length} metros")

# Plot the catchment
sns.set_palette('husl')
fig, ax = plt.subplots(figsize=(8.5,6.5))
# Graficar el punto
ax.plot(x, y, 'ro')  # 'ro' significa color rojo, puntos redondos

plt.xlabel('Longitude')
plt.ylabel('Latitude')
plt.xlim(grid.bbox[0], grid.bbox[2])
plt.ylim(grid.bbox[1], grid.bbox[3])
ax.set_aspect('equal')
plt.grid('on', zorder=0)
im = ax.imshow(np.where(clipped_catch, clipped_catch, np.nan), extent=grid.extent,
               zorder=1, cmap='Greys_r')

for branch in branches['features']:
    line = np.asarray(branch['geometry']['coordinates'])
    plt.plot(line[:, 0], line[:, 1])
    
_ = plt.title('D8 channels', size=14)
plt.show()




