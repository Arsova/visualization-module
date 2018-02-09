import pandas as pd
import numpy as np
import datetime
def get_elog_usage(axis):
    df = pd.read_csv('Data/data_elog_eindhoven_5.csv')
    return df
def aggr_elog_usage(data, level):
    data['UTC_time'] = pd.to_datetime(data['UTC_time'])
    data = data.set_index('UTC_time')
    if (level == '15min'):
        data = data.resample("15min").mean() * 1000 / 4 / 1000000
    elif (level == 'hour'):
        data = data.resample("H").mean() * 1000 / 1000000
    elif (level == 'day'):
        data = data.resample("D").mean() * 1000 * 24 / 1000000
    elif (level == 'week'):
        data = data.resample("W").mean() * 1000 * 24 * 7 / 1000000
    elif (level == '4weeks'):
        data = data.resample("4W").mean() * 1000 * 24 * 7 * 4 / 1000000
    else:
        print('The level of aggregation is incorrect')
    data = data.reset_index()
    return data
def get_yearly_usage(axis):
    df = pd.read_csv('Data/Verbruiken_Eindhoven.txt', delimiter=';')
    #elog_location=pd.read_csv('Data/unique_loc_data_ehv.csv')
    #elog_loc=elog_location['location'].values
    #remove unnecessary columns
    columns_to_keep = ["LOC_AANSLU",
        "POSTCODE_N",
        "WOONPLAATS",
        "HERB_JAA_1",
        "HERB_JAA_2",
        "HERB_JAA_3",
        "HERB_JAA_4",
        "HERB_JAA_5"]
    df = df.loc[:,columns_to_keep]
    #change format of the columns
    change_format = ["LOC_AANSLU",
        "HERB_JAA_1",
        "HERB_JAA_2",
        "HERB_JAA_3",
        "HERB_JAA_4",
        "HERB_JAA_5"]
    for column in change_format:
        df[column]=df[column].str.split('.', expand=True)[0].replace(',', '', regex=True)
        df[column]=pd.to_numeric(df[column])

    #keep only usages in Eindhoven
    #108 adresses are removed
    df=df[df['WOONPLAATS']=='EINDHOVEN']
    df=df.drop('WOONPLAATS', axis=1)
    """
    #create data set with only non elog data
    df_non_elog=df[~df['LOC_AANSLU'].isin(elog_loc)]

    #create data set with only elog data
    df_elog=df[df['LOC_AANSLU'].isin(elog_loc)]
    df_elog=df_elog[['LOC_AANSLU', 'HERB_JAA_1']].reset_index(drop=True)
    df_elog=pd.merge(df_elog, elog_location, left_on='LOC_AANSLU', right_on='location', how='left')
    df_elog=df_elog[['location', 'HERB_JAA_1', 'UTC_time']]
    df_elog['UTC_time'] = pd.to_datetime(df_elog['UTC_time'])
    df_elog['end_time']=pd.to_datetime('2018-01-01 00:01:00')
    df_elog['minutes_in_elog']=df_elog['end_time'].sub(df_elog['UTC_time'], axis=0)/np.timedelta64(1,'D')*24*60
    df_elog['total_minutes']=365*24*60
    df_elog['part_in_elog']=df_elog['minutes_in_elog']/df_elog['total_minutes']
    df_elog=df_elog[['location', 'HERB_JAA_1', 'UTC_time', 'part_in_elog']]
    df_elog['usage_till_install']=df_elog['HERB_JAA_1']*(1/df_elog['part_in_elog'])
    print(df_elog.head())
"""
    #print(df_elog.head())
    #sum up the usage of all house holds
    total_usage=pd.DataFrame()
    #total_usage['year']=pd.to_numeric([2017, 2016, 2015, 2014, 2013])
    if (axis==1):
        total_usage['yearly_usage']=-df[['HERB_JAA_1','HERB_JAA_2','HERB_JAA_3','HERB_JAA_4','HERB_JAA_5']].sum()
    else:
        total_usage['yearly_usage'] = df[['HERB_JAA_1', 'HERB_JAA_2', 'HERB_JAA_3', 'HERB_JAA_4', 'HERB_JAA_5']].sum()
    total_usage['startOfYear']=[pd.to_datetime('2017-01-01 00:00'), pd.to_datetime('2016-01-01 00:00'), pd.to_datetime('2015-01-01 00:00'), pd.to_datetime('2014-01-01 00:00'), pd.to_datetime('2013-01-01 00:00')]
    total_usage['endOfYear'] = [pd.to_datetime('2018-01-01 00:00'), pd.to_datetime('2017-01-01 00:00'), pd.to_datetime('2016-01-01 00:00'), pd.to_datetime('2015-01-01 00:00'), pd.to_datetime('2014-01-01 00:00')]
    total_usage['number_of_days']=[365, 366, 365, 365, 365]
    total_usage['daily_usage']=total_usage['yearly_usage']/total_usage['number_of_days']
    total_usage['hourly_usage']=total_usage['daily_usage']/24
    return total_usage
def aggr_usage(data, level):
    usage=pd.DataFrame()
    usage['TimeStamp'] = pd.to_datetime(pd.date_range(start='2017-01-01 00:00', end='2017-12-31 23:58', freq='2min'))
    usage['Households'] = data['hourly_usage'].iloc[0]
    usage = usage.set_index('TimeStamp')
    usage=usage*1000/30
    print('usage')
    #print(usage)
    if (level=='20min'):
        usage = usage.resample("20min").sum()
    elif (level=='hour'):
        usage = usage.resample("H").sum()
    elif (level=='day'):
        usage = usage.resample("D").sum()
    elif (level=='week'):
        usage = usage.resample("W").sum()
    elif (level=='4weeks'):
        usage = usage.resample("4W").sum()
    else:
        print('The level of aggregation is incorrect')
    usage = usage / 1000000
    usage = usage.reset_index()
    return usage



