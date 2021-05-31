import warnings
warnings.filterwarnings("ignore")

import numpy as np
import pandas as pd
import geopandas as gpd # GeoPandas library for spatial analytics

collision = pd.read_csv('../01_Data/Motor vehicle collisions/Motor Collision_2019.csv')
collision.shape
collision.head()
# %% codecell
collision_gdf = gpd.GeoDataFrame(
    collision, geometry=gpd.points_from_xy(collision['LONGITUDE'],collision['LATITUDE']))

collision_gdf = collision_gdf.dropna(subset=['LONGITUDE', 'LATITUDE'])

collision_gdf = collision_gdf[collision_gdf['LATITUDE']>0]

len (collision_gdf)

collision_gdf.set_crs(epsg=2263, inplace=True)

collision_gdf.head()

collision_gdf.to_file("../01_Data/collision_2019.shp")

collision_gdf_severe = collision_gdf[(
                        collision_gdf['NUMBER OF PEDESTRIANS INJURED']!= 0) |
                        (collision_gdf['NUMBER OF PEDESTRIANS KILLED']!= 0) |
                        (collision_gdf['NUMBER OF CYCLIST INJURED']!= 0) |
                        (collision_gdf['NUMBER OF CYCLIST KILLED']!= 0)]
# %% codecell
collision_gdf_severe.to_file("../01_Data/collision_severe_2019.shp")
# %% codecell
