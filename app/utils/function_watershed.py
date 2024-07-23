from pysheds.grid import Grid
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

def delineate_watershed(latitude, longitude):
    """
    Delimita la cuenca hidrográfica a partir de un punto dado (latitud, longitud).

    :param latitude: float, latitud del punto de interés
    :param longitude: float, longitud del punto de interés
    :return: Dictionary containing 'catchment' array, 'flow_direction', and 'flow_accumulation' arrays
    """
    try:
        # Cargar el DEM
        grid = Grid.from_raster('/home/tidop/2024/usal/tidop/github/api-watershed/data/MDT_25_Guadiana.tif')
        dem = grid.read_raster('/home/tidop/2024/usal/tidop/github/api-watershed/data/MDT_25_Guadiana.tif')
        print(dem)
        

        # Process DEM to prepare for hydrological analysis
        pit_filled_dem = grid.fill_pits(dem, nodata_in=-9999, nodata_out=-9999)
        flooded_dem = grid.fill_depressions(pit_filled_dem, nodata_in=-9999, nodata_out=-9999)
        inflated_dem = grid.resolve_flats(flooded_dem, nodata_in=-9999, nodata_out=-9999)
        
        dirmap = (64, 128, 1, 2, 4, 8, 16, 32) 
        fdir = grid.flowdir(inflated_dem, dirmap=dirmap)

        # Flow accumulation
        acc = grid.accumulation(fdir, dirmap=dirmap)  

        # Delineate the catchment
        x, y = longitude, latitude
        # Snap pour point to high accumulation cell
        x_snap, y_snap = grid.snap_to_mask(acc > 1000, (x, y))
        catch = grid.catchment(x=x_snap, y=y_snap, fdir=fdir, dirmap=dirmap, 
                       xytype='coordinate')
        grid.clip_to(catch)
        clipped_catch = grid.view(catch)
        clipped_catch = clipped_catch.data.tolist()
        """ # Plot the catchment
        fig, ax = plt.subplots(figsize=(8,6))
        fig.patch.set_alpha(0)

        plt.grid('on', zorder=0)
        im = ax.imshow(np.where(clipped_catch, clipped_catch, np.nan), extent=grid.extent,
                    zorder=1, cmap='Greys_r')
        plt.xlabel('Longitude')
        plt.ylabel('Latitude')
        plt.title('Delineated Catchment', size=14)
        plt.show() """

        return {
            'catchment': clipped_catch,
            'flow_direction': fdir,
            'flow_accumulation': acc
        }

    except Exception as e:
        print(f"Error processing the DEM: {e}")
        return {'error': str(e)}
