# %% codecell
import warnings
warnings.filterwarnings("ignore")

import numpy as np
import pandas as pd
import geopandas as gpd # GeoPandas library for spatial analytics

import matplotlib.pyplot as plt
import seaborn as sns # visualization styling package
%matplotlib inline

plt.rcParams['figure.dpi']= 150
# %% codecell
# set default font
plt.rcParams['font.sans-serif'] = "Helvetica"
# always use sans-serif fonts
plt.rcParams['font.family'] = "sans-serif"

### Pavement Score ------------------------------------------------------------------

pavement = pd.read_csv('../01_Data/Pavement_Buffer.csv')

ID = pavement.groupby(['ID']).sum().reset_index()
ID = ID.rename(columns={"Length": "Length_total"})
ID = ID[['ID','Length_total']]

pavement_ID = pavement.merge(ID)

pavement_ID['Rating_Power'] = pavement_ID['Rating_B']*pavement_ID['Length']/pavement_ID['Length_total']

pavement_score = pavement_ID.groupby(['ID']).sum().reset_index()[['ID','Rating_Power']]
pavement_score = pavement_score.rename(columns={"Rating_Power": "Rating"})

pavement_score.head()

#### Sidewalk Score -------------------------------------------------------------

sidewalkwidth = gpd.read_file('../01_Data/sidewalkwidth_power.shp')
# sidewalkwidth['ID_2'].nunique()
# ID = sidewalkwidth.groupby(['ID_2']).count()
# ID.shape

sidewalkwidth = sidewalkwidth[['width','ID_2','length']]

sidewalkwidth['power']=sidewalkwidth['width']*sidewalkwidth['length']

ID = sidewalkwidth.groupby(['ID_2']).sum().reset_index()
ID = ID.rename(columns={"length": "Length_total","ID_2":"ID"})

ID = ID[['ID','Length_total']]

sidewalkwidth2 = sidewalkwidth.merge(ID)

sidewalkwidth2['Rating_Power'] = sidewalkwidth2['width']*sidewalkwidth2['length']/sidewalkwidth2['Length_total']

sidewalkwidth_score = sidewalkwidth2.groupby(['ID']).sum().reset_index()
sidewalkwidth_score = sidewalkwidth_score.rename(columns={"Rating": "Width"})

sidewalkwidth_score = sidewalkwidth_score[['ID','Width']]
sidewalkwidth_score.to_csv('../01_Data/sidewalkwidth_final.csv')

### Visualization -----------------------------------------------------------------
buffer = gpd.read_file('../01_Data/Intersection_Buffer.shp')
buffer_pavement = buffer.merge(pavement_score)

buffer_pavement = pavement_gdf.set_crs(crs='epsg:2263',allow_override=True)

fig, ax = plt.subplots(figsize=(12,12))

buffer_pavement.plot(ax=ax,column='Rating', cmap='PiYG', scheme='quantiles',legend=True)
# buffer_pavement.to_file('../01_Data/buffer_pavement_rating.shp')
