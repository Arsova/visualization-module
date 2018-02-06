from datetime import date
import pandas as pd
from bokeh.transform import factor_cmap
from math import radians, cos, sin, asin, sqrt
import numpy as np

def convert_list_to_date(list):
    new_list = []
    for item in list:
        split = item.split('/')
        day = int(split[0])
        month = int(split[1])
        year = int(split[2])
        d = date(year, month, day)
        new_list.append(d)
    return new_list


def convert_to_date(entry):

    split = entry.split('-')
    day = int(split[0])
    month = int(split[1])
    year = int(split[2])
    d = date(year, month, day)
    return d

def convert_to_date_reverse(entry):

    split = entry.split('-')
    day = int(split[2])
    month = int(split[1])
    year = int(split[0])
    d = date(year, month, day)
    return d


def fix_dates(datum_list):
    new_list = []
    for line in datum_list:
        line_new = str(line)
        line_new = line_new[:-3]
        line_new = datetime.fromtimestamp(int(line_new)).strftime('%Y-%m-%d')
        new_list.append(line_new)
    new_list = convert_to_date(new_list)
    return new_list

def get_color(value):
    color = ['#6baed6', '#4292c6', '#2171b5', '#08519c', '#08306b']
    for i in range(5):
        if value < ((i+1)*2714028)+2:
            return color[i]
        else:
            return '#08306b'

# returns new aggregaate consumption values
def return_value_list(locations, start='2017-1-1', end='2017-12-31'):
    value_list = []
    start = convert_to_date_reverse(start)
    end = convert_to_date_reverse(end)
    df = pd.read_csv('data/aggregated_day_total_2_positives.csv')
    df['norm_date'] = df.apply(lambda row: convert_to_date_reverse(row['norm_date']), axis=1)
    df = df.loc[(df['norm_date'] >= start) & (df['norm_date'] <= end)]
    for loc in locations:
        df_temp = df[df['location']==int(loc)]
        if len(df_temp) == 0:
            value_list.append(0)
        else:
            consumption = df_temp['delta_total'].sum()
            value_list.append(consumption)
    return value_list



def haversine(lon1, lat1, lon2, lat2):
    """
    Calculate the great circle distance between two points
    on the earth (specified in decimal degrees)
    """
    # convert decimal degrees to radians
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

    # haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    r = 6371 # Radius of earth in kilometers. Use 3956 for miles
    return c * r



def select_events(lon, lat, data_cc, radius):
    """
    This function calcualte the distance of everu event based on the latitud and longitud of the location selected. This equation os based on
    the haversine distance:
        https://en.wikipedia.org/wiki/Haversine_formula

    Parameters
    ---------------------------------
        lon: longitid of the eLog location
        lat: latitud of the eLog location
        data_cc: data frame with events
        radius: distance in Km where the events are selected.

    Return
    ---------------------------------
        events_selected: vector with the Id of the events selected
    """

    data_cc['haversine_distance'] = np.vectorize(haversine)(lon, lat,data_cc['Longitude'], data_cc['Latitude'])
    data_cc = data_cc[data_cc['haversine_distance'] <= radius]

    return data_cc

def get_api_key():
    with open('data/api_key.txt') as infile:
        for line in infile:
            return str(line)

if __name__ == "__main__":
    data_cc = pd.read_csv('data/Data_heat_maps/Customer Contacts/limited_occ_with_gps_time.csv', sep = ';')
    events_selected = select_events(5.487716, 51.479160, data_cc, 30)
