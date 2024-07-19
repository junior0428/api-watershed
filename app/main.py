from pysheds.grid import Grid
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import colors
import seaborn as sns

# Cargar el DEM
grid = Grid.from_raster('../data/elevation.tiff')
dem = grid.read_raster('../data/elevation.tiff')


# ...................... Condition DEN ......................
# Fill pits in the DEM
pit_filled_dem = grid.fill_pits(dem)

# Fill depressions in the DEM
flooded_dem = grid.fill_depressions(pit_filled_dem)

# Resolve flats in the DEM
inflated_dem = grid.resolve_flats(flooded_dem)

# ............. Determine D8 flow directions from DEM ...........

# Specify directional mapping
dirmap = (64, 128, 1, 2, 4, 8, 16, 32)
    
# Compute flow directions
fdir = grid.flowdir(inflated_dem, dirmap=dirmap)

# Plot the DEM
fig = plt.figure(figsize=(8,6))
fig.patch.set_alpha(0)

plt.imshow(fdir, extent=grid.extent, cmap='viridis', zorder=2)
boundaries = ([0] + sorted(list(dirmap)))
plt.colorbar(boundaries= boundaries, values=sorted(dirmap))
plt.xlabel('Longitude')
plt.ylabel('Latitude')
plt.title('Flow direction grid', size=14)
plt.grid(zorder=-1)
plt.tight_layout()
plt.show()