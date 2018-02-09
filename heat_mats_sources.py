# -*- coding: utf-8 -*-
"""
Created on Thu Feb  8 12:51:47 2018

@author: s157084
"""

# -*- coding: utf-8 -*-
"""
Created on Mon Feb  5 15:48:23 2018

@author: s157084
"""
import numpy as np
import pandas as pd

from bokeh.plotting import figure, show, output_file, curdoc
from bokeh.io import show
from bokeh.layouts import column, row, gridplot
from collections import OrderedDict
from bokeh.models.markers import Triangle
from bokeh.models.widgets import TextInput

from bokeh.models import (
    ColumnDataSource,
    HoverTool,
    LinearColorMapper,
    BasicTicker,
    PrintfTickFormatter,
    ColorBar,
    BoxAnnotation,
    Band,
    LogColorMapper,
    FuncTickFormatter,
    PrintfTickFormatter,
    NumeralTickFormatter,
    LinearAxis, 
    Range1d,
    Legend
)


from math import pi
import sys
pd.options.mode.chained_assignment = None

def pre_process_hour_consuption(location = 1163208):
    retrieve = str(location) + '.csv'
    data = pd.read_csv('data/Data_heat_maps/hour_consuption/' + retrieve)
    data.columns.name = 'date'
    data.index.name = 'hour'
    data.index = data.index.astype(str)
    hours = pd.DataFrame(list(data.index), columns = ['hours'])
    date = data.columns
    date_range = pd.DataFrame([[date[0], date[-1]]], columns = ['start', 'end'])
    date = list(pd.date_range(start = date[0], end = date[-1]).strftime('%Y-%m-%d'))
    date =pd.DataFrame(date, columns = ['date'])
    data_stack = pd.DataFrame(data.stack(), columns=['rate']).reset_index()
    
    return ColumnDataSource(data), ColumnDataSource(data_stack), ColumnDataSource(hours), ColumnDataSource(date), ColumnDataSource(date_range)


      
def multiple_plot(data_heat_s, data__heat_stack_s, hours_s, date_s, date_range_s):

    
    output_file("eLog_info_{}.html".format(location), title="eLog_info_{}.py".format(location))
    colors = ['#fff7fb', '#ece7f2', '#d0d1e6', '#a6bddb', '#74a9cf', '#3690c0', '#0570b0', '#045a8d', '#023858']
#     mapper = LinearColorMapper(palette=colors, low=df.rate.min(), high=df.rate.max())
    mapper = LogColorMapper(palette=colors, low= 0, high=max(data__heat_stack_s.data['rate']))
    
    TOOLS = "save,pan ,reset, wheel_zoom"
    p1 = figure(title="Water consumption in Log(Liters) from {0} to {1} - Location: {2}".format(date_range_s.data['start'], date_range_s.data['end'], str(location)), 
                 x_axis_type="datetime", x_range = list(date_s.data['date']), y_range = list(reversed(hours_s.data['hours'])), tools=TOOLS)

    
    heat_map = p1.rect(x="date", y="hour", width=1, height=1, source = data__heat_stack_s, fill_color={'field': 'rate', 'transform': mapper},
            line_color=None)
    

    return p1

source_radius_circle = ColumnDataSource(data=dict(value=[]))
data_heat_s = ColumnDataSource(data=dict(value=[]))
data__heat_stack_s = ColumnDataSource(data=dict(value=[]))
hours_s = ColumnDataSource(data=dict(value=[]))
date_s = ColumnDataSource(data=dict(value=[]))
date_range_s = ColumnDataSource(data=dict(value=[]))

def change_radius(attr,old,new):
    new_rad = float(text_input.value)*1000
    r = []
    r.append(new_rad)
    source_radius_circle.data['location'] = r
    
    
text_input = TextInput(value="1163208", title="Location")
text_input.on_change('value', change_radius)


    
data_heat_s.data, data__heat_stack_s.data, hours_s.data, date_s.data, date_range_s.data = pre_process_hour_consuption(1163208)
p1 = multiple_plot(data_heat_s, data__heat_stack_s, hours_s, date_s, date_range_s)
#source_radius_circle.data['location']

layout = gridplot([[p1, text_input]] , plot_width=1200, plot_height=400, toolbar_location = 'below')
curdoc().add_root(layout)
    
    
    