import numpy as np
from bokeh.plotting import figure, output_file, show
from bokeh.palettes import Blues3, BuGn5
from get_inflow_data import *
from get_yearly_usage import *
from get_booster_data import *
import pandas as pd

#to aggregate on four weeks level: type=4weeks
#to aggregate on week level: type=week
#to aggregate on day level: type=day
#to aggregate on hour level: type=hour
#to aggregate on 20 minutes level: type=20min
level='4weeks'
#type of axis. If only positive axis: axis=0. If both negative and positive axis: axis=1.
axis=1
usage=get_yearly_usage(axis)
usage=aggr_usage(usage, level)
#elog_usage=get_elog_usage(axis)
#elog_usage=aggr_elog_usage(elog_usage, level)
#inflow=get_inflow_data()
#inflow=aggr_inflow(inflow, level)
#inflow['TotalInflow']=inflow.sum(numeric_only=True, axis=1)
#inflow['TotalEindhoven']=inflow[['WpbEindhoven_Eindhoven1', 'WpbEindhoven_Eindhoven2','WpbEindhoven_Eindhoven3','WpbEindhoven_Eindhoven4']].sum(axis=1)
#inflow['TotalWelschap']=inflow[['WpbWelschap_Eindhoven1','WpbWelschap_Eindhoven2']].sum(axis=1)
#booster=get_booster_data(axis)
#booster=aggr_booster(booster, level)
#booster['TotalBooster']=booster.sum(numeric_only=True, axis=1)
usage.to_csv('Data/usage_water_balance_'+level+'_'+ str(axis) + '.csv')
#inflow.to_csv('Data/inflow_water_balance_'+level+'_'+ str(axis) + '.csv')
#booster.to_csv('Data/booster_water_balance_'+level+'_'+ str(axis)+ '.csv')

