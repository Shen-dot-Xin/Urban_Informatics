# %% codecell
import warnings
warnings.filterwarnings("ignore")

import numpy as np
import pandas as pd
import geopandas as gpd # GeoPandas library for spatial analytics


import statsmodels.api as sm

Data = pd.read_csv('../01_Data/metrics_cleaned/data.csv')

Data = Data.drop('Unnamed: 0', axis=1)
Data = Data.fillna(0)

Data.columns

X = Data[['pedestrian_plaza', 'Rating',
       'One & Two Family Buildings', 'Multi-Family Walk-Up Buildings',
       'Multi-Family Elevator Buildings',
       'Mixed Residential & Commercial Buildings',
       'Commercial & Office Buildings', 'Industrial & Manufacturing',
       'Transportation & Utility', 'Public Facilities & Institutions',
       'Open Space & Outdoor Recreation', 'Parking Facilities', 'Vacant Land',
       '311count', 'busstop', 'sidewalk_width']]
Y = pd.DataFrame(Data['%severe'])

X = sm.add_constant(X)
model = sm.OLS(Y,X)
results = model.fit()
# %% codecell
results.summary()
# %% codecell
X = Data[['Rating','busstop']]
Y = pd.DataFrame(Data['%severe'])

X = sm.add_constant(X)
model = sm.OLS(Y,X)
results = model.fit()

results.summary()

#Data Standardization
from sklearn.preprocessing import StandardScaler
scaler = StandardScaler().fit(Data)
datastd = scaler.transform(Data)

rating = pd.read_csv('../01_Data/metrics_cleaned/pavementrating_final.csv')

rating.head()

fig, ax = plt.subplots(figsize=(6,5))

plt.hist(rating['Rating'], bins = 20, color = '0.9', edgecolor = '0.2')
plt.xticks(fontsize=12)
plt.yticks(fontsize=12)
plt.title('Street Pavement Rating',fontsize=15)
plt.savefig('../03_OutPut/pavement_hist', dpi=300, bbox_inches='tight')
plt.show()

from pandas.plotting import scatter_matrix
# %% codecell
scatter_matrix(Data[['%severe', 'pedestrian_plaza', 'Rating',
       '311count', 'busstop', 'sidewalk_width']],
               figsize=(12,12), hist_kwds={'color':'Navy', 'edgecolor':'k', 'alpha':0.5},
              s=13, color='Navy')

plt.savefig('../03_OutPut/scatter', dpi=300, bbox_inches='tight')


plt.show()
