import matplotlib.pyplot as plt
from math import radians, sin, cos, sqrt, atan2
import geopandas as gpd
import rasterio
from rasterio.features import shapes
from shapely import geometry, ops
import json
from pysheds.grid import Grid

with rasterio.open('D:/2024/USAL/TIDOP/E-Hydro/data/guadiana_wgs84.tif') as src:
    transform = src.transform
    data = src.read(1)  # Leer los datos del DEM

grid = Grid.from_raster('D:/2024/USAL/TIDOP/E-Hydro/data/guadiana_wgs84.tif')
dem = grid.read_raster('D:/2024/USAL/TIDOP/E-Hydro/data/guadiana_wgs84.tif')

# Define el mapa de direcciones y lee los rasters necesarios
fdir = grid.read_raster('D:/2024/USAL/TIDOP/E-Hydro/data/flow_fdir.tif')
acc = grid.read_raster('D:/2024/USAL/TIDOP/E-Hydro/data/flow_accumulation.tif')

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
gdf = gpd.GeoDataFrame([{'geometry': catchment_polygon}], crs=grid.crs)
json_catchment = json.loads(gdf.to_json())
print("CRS actual:", gdf.crs)

# Calcular el área de la cuenca
gdf = gdf.to_crs(epsg=32630)  

# Calcular el área en metros cuadrados después de cambiar el CRS
areas_m2 = (gdf['geometry'].area)/10**6
areas_m2[0]
print("Áreas calculadas en kilometro cuadrados:", areas_m2/10**6)

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

json_prueba = {"latitude": 38.491025, "longitude": -4.758253}