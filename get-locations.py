import pandas as pd
import googlemaps
from datetime import datetime

# Credits: https://github.com/djvanderlaan/rijksdriehoek/blob/master/Python/rijksdriehoek.py
from rd_to_wgs import rd_to_wgs

'''
Just some code to convert coordinates from rd-new to WGS84. Creates new file with list of locations
'''

df = pd.read_csv('data/Verbruiken_Eindhoven.txt', delimiter=';')
df['POSTCODE_N'] = df['POSTCODE_N'].str.replace(',', '')
df['LOC_AANSLU'] = df['LOC_AANSLU'].str.replace(',', '')
df['LOC_AANSLU'] = df['LOC_AANSLU'].apply(pd.to_numeric)
df['LOC_AANSLU'] = df['LOC_AANSLU'].astype(int)
# df['BRANCHE_OM'] = df['BRANCHE_OM'].str.replace(',', '')
# df['BRANCHE_OM'] = df['BRANCHE_OM'].apply(pd.to_numeric)
df['X'] = df['X'].str.replace(',', '')
df['X'] = df['X'].apply(pd.to_numeric)
df['Y'] = df['Y'].str.replace(',', '')
df['Y'] = df['Y'].apply(pd.to_numeric)
df['Address'] = df["STRAAT"].map(str) + " " + df["HUISNR"].map(str) + \
", " + df["POSTCODE_N"].map(str) + df["POSTCODE_L"].map(str)
df['Latitude'] = df.apply(lambda row: rd_to_wgs(float(row['X']), float(row['Y']))[0], axis=1)
df['Longitude'] = df.apply(lambda row: rd_to_wgs(float(row['X']), float(row['Y']))[1], axis=1)

new_df = df[['LOC_AANSLU', 'STRAAT', 'HUISNR', 'POSTCODE_N', 'POSTCODE_L', \
'Address', 'Latitude', 'Longitude']]
new_df.to_csv('data/locations.csv', index=False, encoding='utf-8')
