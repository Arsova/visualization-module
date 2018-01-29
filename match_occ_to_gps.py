import pandas as pd
from datetime import datetime
import numpy as np

df1 = pd.read_csv('data/export_occurences.csv', delimiter=';')
df1 = df1.loc[df1['Storingslocatie plaats']=='EINDHOVEN']
df2 = pd.read_csv('data/locations.csv')

df3 = df1.join(df2.set_index('Location'), on='Locatienummer')
df3.to_csv('data/occ_with_gps.csv', index=False, encoding='utf-8', sep=';')

df3 = df3[np.isfinite(df3['Latitude'])]
df3 = df3[['Locatienummer', 'Verbruiker Omschr', 'Datum', 'Hoofdtype Melding', 'Address', 'Latitude', 'Longitude']]
df3.to_csv('data/limited_occ_with_gps.csv', index=False, encoding='utf-8', sep=';')
