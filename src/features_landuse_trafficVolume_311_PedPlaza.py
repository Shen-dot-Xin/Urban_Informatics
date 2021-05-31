### Landuse, Traffic Volume and 311 requests feature engineering

import numpy as np
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
from shapely.wkt import load

from urllib.parse import urlencode
import urllib.request, json

# 1.  MapPLUTO Land Use dataset:
#     Find percentage of land use type within the buffered area centered at each intersection
# 2. Traffic Volume Counts, 2019:
#     Find the total traffic volume within the buffered area centered at each intersection: sum of all volume divided by 2
# 3. 311 Service Requests, 2019:
#     Count DOT Street Lights and Traffic Signals complaints within the buffered area centered at each intersection
# 4. Pedestrian Plaza, 2019:
#     Number of Pedestrian Plaza intersecting with the buffered area

### Landuse -----------------------------------------------------------------------
# 1. MapPLUTO Land Use dataset: Find percentage of land use type within the buffered area centered at each intersection
# - spatial join land use to buffer
# - calculate area based on landuse type (group by land use code)
# - divide by buffer area for percentage

# API
# API_traffic = 'https://data.cityofnewyork.us/resource/ertz-hr4r.csv?'
# API_311 = 'https://data.cityofnewyork.us/resource/erm2-nwe9.csv?'

# read buffer
buffer = gpd.read_file('../data/VZV_highlighted_intersections_200ft')
buffer = buffer.reset_index()

landuse = gpd.read_file('../data/nyc_mappluto_20v7_shp')

landuse_buffered =gpd.clip(landuse, buffer)
#landuse_buffered.to_file('../data/landuse_perbuffer')
landuse = gpd.read_file('../data/landuse_buffered_split')

L = []
for ind, row in buffer.iterrows():
    row = pd.DataFrame(row).transpose()
    row = gpd.GeoDataFrame(row, geometry = 'geometry', crs = 2263)
    land = gpd.sjoin(landuse, row, how='inner', op='within')
    land = land.dissolve(by='LandUse')
    land["area"] = land['geometry'].area
    land = pd.DataFrame(land.drop(columns='geometry')).reset_index()
    land = land.pivot_table(columns = 'LandUse', values = 'area', index = 'index')
    L.append(land)
df = pd.concat(L).reset_index()

buffer_landuse = pd.merge(buffer, df, on='index')
buffer_landuse.to_file('../data/buffer_landuse_joined')

### Traffic Volumne -------------------------------------------------------------
# 2. Traffic Volume Counts, 2019: Find the total traffic volume within the buffered area centered at each intersection: sum of all volume divided by 2
# - data query
#     - select Segment ID, Roadway Name, From, To, Direction, sum(12:00-1:00AM), etc.
#     - group by directions and segment
#     - having whole year of 2019
# - sum all hourly columns to get the daily count
# - table join lion_road to each intersection.
# - table join traffic volumn by segment ID

query = {'$select': 'direction, segment_id, avg(_12_00_1_00_am),avg(_1_00_2_00am),avg(_2_00_3_00am),avg(_3_00_4_00am),avg(_4_00_5_00am),avg(_5_00_6_00am),avg(_6_00_7_00am),avg(_7_00_8_00am),avg(_8_00_9_00am),avg(_9_00_10_00am),avg(_10_00_11_00am),avg(_11_00_12_00pm),avg(_12_00_1_00pm),avg(_1_00_2_00pm),avg(_2_00_3_00pm),avg(_3_00_4_00pm),avg(_4_00_5_00pm),avg(_5_00_6_00pm),avg(_6_00_7_00pm),avg(_7_00_8_00pm),avg(_8_00_9_00pm),avg(_9_00_10_00pm),avg(_10_00_11_00pm),avg(_11_00_12_00am)',
'$where':'date>="2019-01-01" and date<"2020-01-01"',
'$group':'direction, segment_id',
'$limit': 100000000000}

df1 = pd.read_csv(API_traffic + urlencode(query))
df1.head()

df1['avg_day'] = np.sum(df1[['avg_12_00_1_00_am', 'avg_1_00_2_00am',
       'avg_2_00_3_00am', 'avg_3_00_4_00am', 'avg_4_00_5_00am',
       'avg_5_00_6_00am', 'avg_6_00_7_00am', 'avg_7_00_8_00am',
       'avg_8_00_9_00am', 'avg_9_00_10_00am', 'avg_10_00_11_00am',
       'avg_11_00_12_00pm', 'avg_12_00_1_00pm', 'avg_1_00_2_00pm',
       'avg_2_00_3_00pm', 'avg_3_00_4_00pm', 'avg_4_00_5_00pm',
       'avg_5_00_6_00pm', 'avg_6_00_7_00pm', 'avg_7_00_8_00pm',
       'avg_8_00_9_00pm', 'avg_9_00_10_00pm', 'avg_10_00_11_00pm',
       'avg_11_00_12_00am']], axis=1)

#df1.to_excel('../data/table/traffic.xlsx')
df2 = df1.groupby('segment_id').agg({'avg_day':'mean'})
#df2.to_excel('../data/table/traffic_cleaned.xlsx')

traffic = pd.read_excel('../data/table/traffic_cleaned.xlsx')
road = gpd.read_file('../data/lion_road')

road_seg = road[['SegmentID', 'TrafDir','XFrom','YFrom','XTo','YTo', 'geometry']]
road_seg['SegmentID'] = road_seg.SegmentID.astype(int)

traffic = traffic.rename(columns={'segment_id':'SegmentID'})
# %% codecell
road_joined = pd.merge(road_seg, traffic, on = 'SegmentID', how = 'left')
road_joined = gpd.GeoDataFrame(road_joined, geometry = 'geometry', crs = 2263)
road_joined.to_file('../data/road_traffic')

### 311 ---------------------------------------------------------------------------
# 3. 311 Service Requests from 2010 to Present: Count DOT Street Lights and Traffic Signals complaints within the buffered area centered at each intersection
# - get all in 2019
# - join to buffer

query = {'$select': '*',
'$where':'complaint_type in("Street Light Condition", "Traffic Signal Condition") and created_date>="2019-01-01" and created_date<"2020-01-01"',
'$limit': 10000000000000}
df311 = pd.read_csv(API_311 + urlencode(query))
df311.head()
#df311.to_csv('../data/table/311_lights_signals_2019.csv')

df311 = pd.read_csv('../data/table/311_lights_signals_2019.csv')
df311 = df311.drop(columns='Unnamed: 0')

gdf311 = gpd.GeoDataFrame(df311, geometry = gpd.points_from_xy(df311['x_coordinate_state_plane'], df311['y_coordinate_state_plane']), crs = 2263)
#gdf311.to_file('../data/311')

gdf311_buffered =gpd.clip(gdf311, buffer)
#gdf311_buffered.to_file('../data/311_clipped')

buffer = gpd.read_file('../data/VZV_highlighted_intersections_200ft')
buffer = buffer.reset_index()
gdf311 = gpd.read_file('../data/311_clipped')

L = []
for ind, row in buffer.iterrows():
    row = pd.DataFrame(row).transpose()
    row = gpd.GeoDataFrame(row, geometry = 'geometry', crs = 2263)
    join311 = gpd.sjoin(row, gdf311, how='inner', op='intersects')
    join311 = pd.DataFrame(join311.drop(columns='geometry')).reset_index()
    #print(join311.columns)
    #print(join311.head())
    join311 = join311.groupby(['index']).agg({'unique_key':'count'}).reset_index()
    # join311['index'] = ind
    #land = land.pivot_table(columns = 'LandUse', values = 'area', index = 'index')
    L.append(join311)

df = pd.concat(L).reset_index()
df = df.rename(columns={'unique_key':'311count'})
df = df.drop('level_0', axis=1)

df_join = pd.merge(buffer, df[['index', '311count']], on = 'index', how = 'left')
df_join.to_file('../data/buffer_311_joined')

### Pedestrian Plaza ---------------------------------------------------------------
# - `objectid` is the unique key

plaza = gpd.read_file('../data/nycdot_PedPlazas')
plaza = plaza.to_crs(2263)

L = []
for ind, row in buffer.iterrows():
    row = pd.DataFrame(row).transpose()
    row = gpd.GeoDataFrame(row, geometry = 'geometry', crs = 2263)
    joinplaz = gpd.sjoin(row, plaza, how='inner', op='intersects')
    joinplaz = pd.DataFrame(joinplaz.drop(columns='geometry')).reset_index()
    #print(join311.columns)
    #print(join311.head())
    joinplaz = joinplaz.groupby(['index']).agg({'objectid':'count'}).reset_index()
    #joinplaz['index'] = ind
    #land = land.pivot_table(columns = 'LandUse', values = 'area', index = 'index')
    L.append(joinplaz)
# %% codecell
df = pd.concat(L).reset_index()
df = df.rename(columns={'objectid':'plzcount'})
df = df.drop('level_0', axis=1)
# %% codecell
df_join = pd.merge(buffer, df[['index', 'plzcount']], on = 'index', how = 'left')
# %% codecell
df_join.to_file('../data/buffer_plaza_joined')
# %% codecell
