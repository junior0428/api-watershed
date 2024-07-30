import matplotlib.pyplot as plt
import numpy as np
import geopandas as gpd
import rasterio
from rasterio.features import shapes
from shapely.geometry import shape
import json
from pysheds.grid import Grid

with rasterio.open('/home/tidop/2024/usal/tidop/github/api-watershed/data/guadiana_wgs84.tif') as src:
    transform = src.transform
    data = src.read(1)  # Leer los datos del DEM

grid = Grid()
grid.add_gridded_data(data, 'dem', affine=transform, crs=src.crs, nodata=src.nodata)

# Define el mapa de direcciones y lee los rasters necesarios
fdir = grid.read_raster('/home/tidop/2024/usal/tidop/github/api-watershed/data/flow_fdir.tif')
acc = grid.read_raster('/home/tidop/2024/usal/tidop/github/api-watershed/data/flow_accumulation.tif')

dirmap = (64, 128, 1, 2, 4, 8, 16, 32)
x, y = -4.758253, 38.491025
x_snap, y_snap = grid.snap_to_mask(acc > 1000, (x, y), return_indices=True)

catch = grid.catchment(x=x_snap, y=y_snap, fdir=fdir, dirmap=dirmap, xytype='index')
grid.clip_to(catch)
clipped_catch = grid.view(catch, nodata=np.nan)

# raster to geojson
mask = clipped_catch != grid.nodata
polygon_shapes = [shape(geom) for geom, value in shapes(clipped_catch, mask=mask, transform=transform) if value == 1]
gdf = gpd.GeoDataFrame({'geometry': polygon_shapes}, crs='EPSG:4326')
geojson = json.loads(gdf.to_json())

# Plot the catchment
fig, ax = plt.subplots(figsize=(8,6))
fig.patch.set_alpha(0)

plt.grid('on', zorder=0)
im = ax.imshow(np.where(clipped_catch, clipped_catch, np.nan), extent=grid.extent,
               zorder=1, cmap='Greys_r')
gdf.plot(ax=ax, color='blue')  # Puedes cambiar el color
plt.xlabel('Longitude')
plt.ylabel('Latitude')
plt.title('Delineated Catchment', size=14)
plt.show()

# Suponiendo que `geojson` es tu variable que contiene el GeoJSON como un dict
gdf = gpd.GeoDataFrame.from_features(geojson['features'])

# Configuración del plot
fig, ax = plt.subplots(figsize=(10, 10))  # Ajusta el tamaño según necesidad
gdf.plot(ax=ax, color='blue')  # Puedes cambiar el color
fig.patch.set_alpha(0)
plt.grid('on', zorder=0)
# Configuración adicional
ax.set_title('Visualización de GeoJSON')
ax.set_xlabel('Longitud')
ax.set_ylabel('Latitud')
# Mostrar el plot
plt.show()