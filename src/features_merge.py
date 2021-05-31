import warnings
warnings.filterwarnings("ignore")

import numpy as np
import pandas as pd
import geopandas as gpd # GeoPandas library for spatial analytics

# ## Read Features ------------------------------------------------------------------

busstop = gpd.read_file('../01_Data/BusStop_Buffer.shp')
busstop = busstop[['ID','stop_id_co']]
#busstop.to_csv('../01_Data/busstop_final.csv')

pavement = gpd.read_file('../01_Data/buffer_pavement_rating.shp')
#pavement.to_csv('../01_Data/pavementrating_final.csv')

sidewalkwidth = gpd.read_file('../01_Data/sidewalkwidth_power.shp')
#sidewalkwidth_score.to_csv('../01_Data/sidewalkwidth_final.csv')

severe_collision = gpd.read_file('../01_Data/metrics_cleaned/%severe_collision.shp')
severe_collision = severe_collision[['ID','%severe']]
# severe_collision.to_csv('../01_Data/metrics_cleaned/severe_final.csv')

landuse = pd.read_csv('../01_Data/table/pct_landuse (1).csv')
landuse = landuse.rename(columns={"Unnamed: 0": "ID"})
# landuse.to_csv('../01_Data/metrics_cleaned/landuse.csv')

complaints = gpd.read_file('../01_Data/buffer_311_joined/')
complaints = complaints[['index','311count']]
complaints = complaints.rename(columns={"index": "ID"})
#complaints.to_csv('../01_Data/metrics_cleaned/complaints.csv')

pedplaza = gpd.read_file('../01_Data/buffer_plaza_joined/')
pedplaza = pedplaza[['index','plzcount']]
pedplaza = pedplaza.rename(columns={"index": "ID","plzcount":"pedplaza"})
pedplaza.to_csv('../01_Data/metrics_cleaned/pedplaza.csv')

### Merge Features ---------------------------------------------------------------------

df = severe_collision.merge(pedplaza, how='left')
df = df.merge(pavement, how='left')
df = df.merge(landuse, how='left')
df = df.merge(complaints, how='left')
df = df.merge(busstop, how='left')
df = df.merge(sidewalkwidth_score, how='left')
df = df.rename(columns={"pedplaza":"pedestrian_plaza","rating":"pavement_rating","stop_id_co":"busstop","Width":"sidewalk_width"})

df.head()

df.to_csv('../01_Data/metrics_cleaned/data.csv')
