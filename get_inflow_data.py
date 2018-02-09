import os
import pandas as pd
def get_inflow_data():
    listInflowStations = os.listdir('Data/Inflow')
    inflowStations=pd.DataFrame()
    count=0

    #for now only look at 2017 data
    inflowStations['TimeStamp'] = pd.date_range(start='2017-01-01 00:00', end='2018-01-01 00:00', freq='2min')

    for column in listInflowStations:
        df=pd.DataFrame(pd.read_csv('Data/Inflow/'+column, delimiter=',', header=None))
        df[0]=pd.to_datetime(df[0].str.split('+',expand=True)[0])
        #df[1]=pd.to_numeric(df[1])
        df.columns=['TimeStamp', column]
        inflowStations=inflowStations.merge(df.drop_duplicates(subset=['TimeStamp']), how='left')
        count=count+1
    inflowStations.columns=['TimeStamp', 'WpbEindhoven_Eindhoven1', 'WpbEindhoven_Eindhoven2','WpbEindhoven_Eindhoven3','WpbEindhoven_Eindhoven4','WpbWelschap_Eindhoven1','WpbWelschap_Eindhoven2']
    cols = inflowStations.columns.drop('TimeStamp')
    inflowStations[cols] = inflowStations[cols].apply(pd.to_numeric, errors='coerce')
    return inflowStations
def aggr_inflow(data, level):
    data = data.set_index('TimeStamp')
    data = data.drop(data.index[len(data) - 1])
    data = data * 1000 / 30
    if (level=='20min'):
        data = data.resample("20min").sum()
    elif (level=='hour'):
        data = data.resample("H").sum()
    elif (level=='day'):
        data = data.resample("D").sum()
    elif (level=='week'):
        data = data.resample("W").sum()
    elif (level=='4weeks'):
        data = data.resample("4W").sum()
    else:
        print('The level of aggregation is incorrect')
    data = data / 1000000
    data = data.reset_index()
    return data