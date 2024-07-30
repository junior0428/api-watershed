import matplotlib.pyplot as plt
import numpy as np
import geopandas as gpd
import rasterio
from rasterio.features import shapes
from shapely import geometry, ops
import json
from pysheds.grid import Grid

with rasterio.open('/home/tidop/2024/usal/tidop/E-HYDRO/data/guadiana_wgs84.tif') as src:
    transform = src.transform
    data = src.read(1)  # Leer los datos del DEM

grid = Grid.from_raster('/home/tidop/2024/usal/tidop/E-HYDRO/data/guadiana_wgs84.tif')
dem = grid.read_raster('/home/tidop/2024/usal/tidop/E-HYDRO/data/guadiana_wgs84.tif')

# Define el mapa de direcciones y lee los rasters necesarios
fdir = grid.read_raster('/home/tidop/2024/usal/tidop/E-HYDRO/data/flow_fdir.tif')
acc = grid.read_raster('/home/tidop/2024/usal/tidop/E-HYDRO/data/flow_accumulation.tif')

dirmap = (64, 128, 1, 2, 4, 8, 16, 32)
x, y = -4.758253, 38.491025
x_snap, y_snap = grid.snap_to_mask(acc > 1000, (x, y))

catch = grid.catchment(x=x_snap, y=y_snap, fdir=fdir, dirmap=dirmap, 
                       xytype='coordinate')
grid.clip_to(catch)
clipped_catch = grid.view(catch)
print(type(dem))
# raster to polygon
shapes = grid.polygonize()
catchment_polygon = ops.unary_union([geometry.shape(shape)for shape, value in shapes])
print(type(catchment_polygon))
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