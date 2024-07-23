import matplotlib.pyplot as plt
from pysheds.grid import Grid
import numpy as np
import seaborn as sns

# Cargar el DEM
grid = Grid.from_raster('/home/tidop/2024/usal/tidop/github/api-watershed/data/guadiana_wgs84.tif')
dem = grid.read_raster('/home/tidop/2024/usal/tidop/github/api-watershed/data/guadiana_wgs84.tif')

#dem[dem == -99999] = np.nan
print(dem)

""" # Configurar los parámetros de la figura
fig, ax = plt.subplots(figsize=(8, 6))
fig.patch.set_alpha(0)

# Mostrar el mapa de elevación con la escala de colores adecuada
plt.imshow(dem, extent=grid.extent, cmap='terrain', vmin=0, vmax=1507.52, zorder=1)
plt.colorbar(label='Elevation (m)')
plt.grid(zorder=0)
plt.title('Digital Elevation Map', size=14)
plt.xlabel('Longitude')
plt.ylabel('Latitude')
plt.tight_layout()
plt.show() """

# Condition DEM
# ----------------------
# Fill pits in DEM
pit_filled_dem = grid.fill_pits(dem, nodata_in=-9999, nodata_out=-9999)

# Fill depressions in DEM
flooded_dem = grid.fill_depressions(pit_filled_dem, nodata_in=-9999, nodata_out=-9999)
    
# Resolve flats in DEM
inflated_dem = grid.resolve_flats(flooded_dem, nodata_in=-9999, nodata_out=-9999)

# Determine D8 flow directions from DEM
# ----------------------
# Specify directional mapping
dirmap = (64, 128, 1, 2, 4, 8, 16, 32)
    
# Compute flow directions
# -------------------------------------
fdir = grid.flowdir(inflated_dem, dirmap=dirmap, nodata_in=-9999, nodata_out=-9999)
grid.to_raster(fdir, '/home/tidop/2024/usal/tidop/github/api-watershed/data/flow_fdir.tif', nodata=-9999)
""" 
fig = plt.figure(figsize=(8,6))
fig.patch.set_alpha(0)

plt.imshow(fdir, extent=grid.extent, cmap='viridis', vmin=0, vmax=128, zorder=2)
boundaries = ([0] + sorted(list(dirmap)))
plt.colorbar(boundaries= boundaries,
             values=sorted(dirmap))
plt.xlabel('Longitude')
plt.ylabel('Latitude')
plt.title('Flow direction grid', size=14)
plt.grid(zorder=-1)
plt.tight_layout()
plt.show() """

# Calculate flow accumulation
# --------------------------
acc = grid.accumulation(fdir, dirmap=dirmap, nodata_in=-9999, nodata_out=-9999)

grid.to_raster(acc, '/home/tidop/2024/usal/tidop/github/api-watershed/data/flow_accumulation.tif', nodata=-9999)

# Delineate a catchment
# ---------------------
# Specify pour point
direc = grid.read_raster('/home/tidop/2024/usal/tidop/github/api-watershed/data/flow_fdir.tif')
acumula = grid.read_raster('/home/tidop/2024/usal/tidop/github/api-watershed/data/flow_accumulation.tif')
#x, y = -3.147179, 38.839411
#x, y = -2.9183, 38.7941
x, y = -2.589, 39.0935
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

# Extract river network
# ---------------------
branches = grid.extract_river_network(direc, acumula > 500, dirmap=dirmap)

sns.set_palette('husl')
fig, ax = plt.subplots(figsize=(8.5,6.5))

plt.xlim(grid.bbox[0], grid.bbox[2])
plt.ylim(grid.bbox[1], grid.bbox[3])
ax.set_aspect('equal')

for branch in branches['features']:
    line = np.asarray(branch['geometry']['coordinates'])
    plt.plot(line[:, 0], line[:, 1])
    
_ = plt.title('D8 channels', size=14)
plt.show()