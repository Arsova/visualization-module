import os
import pandas as pd
def get_booster_data(axis):
    listBoosters = os.listdir('Data/Booster')
    boosters=pd.DataFrame()
    count=0

    # for now only look at 2017 data
    boosters['TimeStamp'] = pd.date_range(start='2017-01-01 00:00', end='2018-01-01 00:00', freq='2min')

    for column in listBoosters:
        df = pd.DataFrame(pd.read_csv('Data/Booster/' + column, delimiter=',', header=None))
        df[0] = pd.to_datetime(df[0].str.split('+', expand=True)[0])
        df.columns=['TimeStamp', column]
        boosters=boosters.merge(df.drop_duplicates(subset=['TimeStamp']), how='left')
        count = count + 1
    boosters.columns=['TimeStamp', 'Eindhoven_AanjVeldhoven1', 'Eindhoven_AanjVeldhoven2','Eindhoven_AanjNuenen','Eindhoven_AanjGeldrop']
    cols = boosters.columns.drop('TimeStamp')
    boosters[cols] = boosters[cols].apply(pd.to_numeric, errors='coerce')
    if (axis==1):
        boosters[cols] = -boosters[cols]
    else:
        boosters[cols] = boosters[cols]
    return boosters
def aggr_booster(data, level):
    data = data.set_index('TimeStamp')
    data=data.drop(data.index[len(data)-1])
    data=data*1000/30
    print('Booster')
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
    print(data)
    print(data.sum())
    data = data.reset_index()
    return data
