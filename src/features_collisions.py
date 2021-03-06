import warnings
warnings.filterwarnings("ignore")

import numpy as np
import pandas as pd
import geopandas as gpd # GeoPandas library for spatial analytics

# Collisions Features
# Produce the count of collisions and severe collision rates within the buffer area of each the intersections.

# Read data
buffer = gpd.read_file('../data/Buffer_OSM')
collisions = gpd.read_file('../data/collisions_2019')
#collisions = collisions.set_crs(4326, allow_override=True)
#collisions = collisions.to_crs(2263)

### Collisions -------------------------------------------------------

buffer_collision = gpd.sjoin(buffer, collisions, how='left')
#buffer_collision.head()
buffer_collision = buffer_collision.groupby('id').size().rename('count').reset_index()
buffer_collision = buffer_collision.rename(columns={"count":"collision"})

buffer_collision = pd.merge(buffer, buffer_collision, how = 'left', on = 'id')
buffer_collision.to_file('../data/buffer_collisions_joined')


### Severe Collisions ------------------------------------------------

buffer = gpd.read_file('../data/Buffer_OSM')
severe = gpd.read_file('../data/collisionsevere_2019')
#severe = severe.set_crs(4326, allow_override=True)
#severe = severe.to_crs(2263)

buffer_severe = gpd.sjoin(buffer, severe, how='left')
#buffer_severe.head()
buffer_severe = buffer_severe.groupby('id').size().rename('count').reset_index()
buffer_severe = buffer_severe.rename(columns={"count":"collision_severe"})
buffer_severe = pd.merge(buffer, buffer_severe, how = 'left', on = 'id')
buffer_severe_rate = buffer_severe.merge(buffer_collision,how='left', on = 'id')
buffer_severe_rate['%severe'] = buffer_severe_rate['collision_severe']/buffer_severe_rate['collision']

buffer_severe_rate.to_file('../data/buffer_severe_joined')
