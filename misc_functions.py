from datetime import date
import pandas as pd
from bokeh.transform import factor_cmap

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

def return_value_list(locations, start='2017-1-1', end='2017-12-31'):
    value_list = []
    start = convert_to_date_reverse(start)
    end = convert_to_date_reverse(end)
    df = pd.read_csv('data/aggregated_day_total_positive.csv')
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
