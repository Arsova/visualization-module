import os
import numpy as np
import pandas as pd



def preprocessing_elog(data, year = None, save = True):
    """
    This funtion preprocess the elog raw file. Because the significant amount of data, this funtion can take a while to compute
    """
    to_delete = ['Unnamed: 0', 'index']
    data.drop(to_delete, axis=1, inplace=True)
    #Sorth the data
    data.sort_values(['location', 'UTC_time' ], ascending=[True, True], inplace=True)
    def calculate_diff(data): 
        """
        In this function the consumption difference is calculated per user.
        """
        def diff_func(df): return df.diff()
        data['delta_total'] = data.groupby('location')['total'].apply(diff_func)

        return data.reset_index(drop=True)

    data = calculate_diff(data)
    #Create new varianbles
    data['dummy'] = 1
    data['datetime64'] = pd.to_datetime(data['UTC_time'])
    data['norm_date'] = data['datetime64'].dt.normalize()
    
    #Only the year selected
    data['year'] = data['datetime64'].dt.year
    
    if year is not None: data = data[data['year'] == year] 
    data['month'] = data['datetime64'].dt.month
    data['day'] = data['datetime64'].dt.day
    data['hour'] = data['datetime64'].dt.hour
    
    if save:    data.to_csv('data/data_processed.csv')

    return data

def data_aggregation(data, aggegation_method = 'sum'):
    """
    This funtion creates the matrices that will be use to generate the heat maps
    Params:
    data: the elog data set
    aggegation_method: how to aggregate the data ['sum', 'mean', 'median']
    Return:
    hour_consuption: Matrix with the average water consuption per time slot (hour)
    """
    # Here we create the matrices that will be shown at the heat-map
    data = data.dropna()
    
    if aggegation_method == 'median':
        hour_consuption = data.groupby(by = ['norm_date', 'hour'])['delta_total'].median()
   
    elif aggegation_method == 'sum':
        hour_consuption = data.groupby(by = ['norm_date', 'hour'])['delta_total'].sum()
        
    elif aggegation_method == 'mean':
        hour_consuption = data.groupby(by = ['norm_date', 'hour'])['delta_total'].mean() 
        
    else:
        print('The option {} does not exist, please select [sum, mean, median]'.format(aggegation_method))
        sys.exit()
        
    num_locations = data.groupby(by = ['norm_date', 'hour'] , as_index=False).apply(lambda x: x.location.nunique()) #This must be cheched, all values are 5
    # Change formats
    def format_change(df):
        df = df.unstack()
        df.index = df.index.astype(str)
        df.columns = df.columns.astype(str)  
        df = df.T
        df.columns.name = 'date'
        return df
    
    hour_consuption = format_change(hour_consuption)
    num_locations = format_change(num_locations)
    
    assert hour_consuption.shape == num_locations.shape, 'different shapes'

    return hour_consuption, num_locations

def create_files_HM(data, total = False):
    """
    This function creates a csv file for every customer. This Information is later used to create heat maps
    
    data: the elog data set
    Total: Boolean function. If is true, it will create the total consumption 
    
    Return:
    hour_consuption: Matrix with the average water consuption per time slot (hour)
    """
        
    unique_location = data['location'].unique()
    
    for i in unique_location:
        temp_data = data[data['location'] == i]
        hour_consuption, num_locations = data_aggregation(temp_data, 'sum')
        aggregated_day = hour_consuption.sum(axis=0)
        aggregated_day = aggregated_day.reset_index()
        aggregated_day.columns = ['norm_date', 'total_consuption']
        
        hour_consuption.to_csv('data/Data_heat_maps/hour_consuption/{}.csv'.format(str(i)),index = False)
        num_locations.to_csv('data/Data_heat_maps/num_locations/{}.csv'.format(str(i)), index = False)
        aggregated_day.to_csv('data/Data_heat_maps/aggregated_day/{}.csv'.format(str(i)), index = False)
    
    if total:
        aggregated_day_total = pd.DataFrame(data.groupby(by = ['location', 'norm_date'])['delta_total'].sum())
        aggregated_day_total.to_csv('data/Data_heat_maps/aggregated_day/aggregated_day_total.csv')
        hour_consuption, num_locations = data_aggregation(data, 'median')
        hour_consuption.to_csv('data/Data_heat_maps/hour_consuption/hour_consuption_total_median.csv',index = False)
        num_locations.to_csv('data/Data_heat_maps/num_locations/num_locations_total_median.csv',index = False)
        

def setup_files_HeatMap(eLog_name = 'data_elog_eindhoven_2.csv'):
    #Create the data directory
    def create_dir(data_dir):
        if not os.path.exists(data_dir): os.makedirs(data_dir)
    
    data_dir = 'data'
    create_dir(data_dir)
    create_dir('static')
    dir_data_HM = data_dir + '/Data_heat_maps'
    create_dir(dir_data_HM)
    #Nested directories
    create_dir(dir_data_HM + '/aggregated_day')
    create_dir(dir_data_HM + '/Customer Contacts')
    create_dir(dir_data_HM + '/hour_consuption')
    create_dir(dir_data_HM + '/num_locations')
    
    dir_WB = data_dir + '/water_balance'
    create_dir(dir_WB)
    create_dir(dir_WB + '/Data water balance')
    
    #Preprcess the data
    print('Retrieving eLog data from the system')
    data = pd.read_csv('data/'+ eLog_name, sep = ';')
    print('Preprocessing the eLog file')
    data = preprocessing_elog(data, year=2017)
    print('Creating filer per location')
    create_files_HM(data, True)


if __name__ == "__main__":
    setup_files_HeatMap(eLog_name = 'data_elog_eindhoven_2.csv')
