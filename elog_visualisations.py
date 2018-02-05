# -*- coding: utf-8 -*-
"""
Created on Mon Feb  5 15:48:23 2018

@author: s157084
"""
import numpy as np
import pandas as pd

from bokeh.plotting import figure, show, output_file
from bokeh.io import show
from bokeh.layouts import column, row, gridplot
from collections import OrderedDict
from bokeh.models.markers import Triangle

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
    Range1d
)


from math import pi
import sys
pd.options.mode.chained_assignment = None

def pre_process_hour_consuption(location):
    retrieve = str(location) + '.csv'
    data = pd.read_csv('data/Data_heat_maps/hour_consuption/' + retrieve)
    output_file("heat_map.html", title="heat_map.py")
    data.columns.name = 'date'
    data.index.name = 'hour'
    data.index = data.index.astype(str)
    return data

def pre_process_total(data, location, window_size):
    data = data[data['location'] == location]
    data.is_copy = False
    data['date'] = pd.to_datetime(data['norm_date']).apply(lambda x: x.strftime('%Y-%m-%d'))
    data['delta_total'] = data['delta_total']/1000000
    sem = lambda x: x.std() / np.sqrt(x.size)
    rolling = data['delta_total'].rolling(window = window_size).agg({"y_mean": np.mean, "y_std": np.std, "y_sem": sem})
    rolling = rolling.fillna(method='bfill')
    rolling['ub'] = rolling.y_mean + 2 * rolling.y_std
    rolling['date'] = data['norm_date']
    # Identify Outliers
    data['c'] = '#377eb8'
    data['c'][data['delta_total']>rolling['ub']] = '#d53e4f'
    data['s'] = 6
    data[data['delta_total']>rolling['ub']]['s'] = 8
    
    data['a'] = 0.4
    data[data['delta_total']>rolling['ub']]['a'] = 1
    
    return data, rolling

def pre_process_cc(data_cc, date_range):
    data_cc['Datum'] = pd.to_datetime(data_cc['Datum'])
    data_cc = data_cc[(data_cc['Datum'] >= date_range[0]) & (data_cc['Datum'] <= date_range[1])]
    data_cc.is_copy = False
    data_cc['date'] = pd.to_datetime(data_cc['Datum']).apply(lambda x: x.strftime('%Y-%m-%d')) 
    return data_cc
      
def multiple_plot(location, data_aggregated, data_cc, window_size = 30, plot_fig = False):
    #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    #heat_map
    data = pre_process_hour_consuption(location)
    hours = list(data.index)
    date = list(data.columns)
    date_range = [date[0], date[-1]]
    date = list(pd.date_range(start = date[0], end = date[-1]).strftime('%Y-%m-%d'))
    df = pd.DataFrame(data.stack(), columns=['rate']).reset_index()
    # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    
    output_file("eLog_info_{}.html".format(location), title="eLog_info_{}.py".format(location))
    colors = ['#fff7fb', '#ece7f2', '#d0d1e6', '#a6bddb', '#74a9cf', '#3690c0', '#0570b0', '#045a8d', '#023858']
#     mapper = LinearColorMapper(palette=colors, low=df.rate.min(), high=df.rate.max())
    mapper = LogColorMapper(palette=colors, low= 0, high=df.rate.max())
    
    TOOLS = "save,pan ,reset, wheel_zoom"
    p1 = figure(title="Water consumption in Log(Liters) from {0} to {1} - Location: {2}".format(date_range[0], date_range[1], str(location)), 
                x_axis_type="datetime", x_range = date, y_range = list(reversed(hours)), tools=TOOLS)
    
    source = ColumnDataSource(df)
    heat_map = p1.rect(x="date", y="hour", width=1, height=1, source = source, fill_color={'field': 'rate', 'transform': mapper},
            line_color=None) 
    
#     color_events = ['#a50026', '#d73027', '#f46d43', '#fdae61', '#fee08b', '#ffffbf', '#d9ef8b', '#a6d96a', '#66bd63', 
#                     '#1a9850', '#00683']
    
    data_cc = pre_process_cc(data_cc, date_range)
    source_events = ColumnDataSource(data_cc)
    p_events = p1.circle(x = 'date', y = 'Hour', legend= "Events", source = source_events, color = '#fdae61', size = 6)
    
    
    color_bar = ColorBar(color_mapper=mapper, border_line_color=None,label_standoff=12, location=(0, 0))
    color_bar.formatter = NumeralTickFormatter(format='0.0')
    p1.add_layout(color_bar, 'right')
    
    heat_map_hover = HoverTool(renderers=[heat_map],
                        tooltips=OrderedDict([('Water Consumption (Liters)', '@rate'),
                                            ('date hour', '@date'), 
                                             ('hour', '@hour'), 
                                           ]))
    events_hover = HoverTool(renderers=[p_events],
                        tooltips=OrderedDict([('Event description', '@{Hoofdtype Melding}'),]))
    
    p1.grid.grid_line_color = None
    p1.axis.axis_line_color = None
    p1.axis.major_tick_line_color = None
    p1.xaxis.major_label_text_font_size = '0pt'  # turn off x-axis tick labels
    p1.yaxis.axis_label = 'Hour'
    p1.axis.major_label_standoff = 0
    #This may be useful for the legend:
    #http://bokeh.pydata.org/en/latest/docs/user_guide/styling.html#legends
    
    p1.legend.location = "top_left"
    p1.legend.click_policy= "hide"
    p1.add_tools(heat_map_hover)
    p1.add_tools(events_hover)
    #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    
    # Aggregated water consumption
    data, rolling = pre_process_total(data_aggregated.copy(), location, window_size)     
    mean_plot = round(np.mean(data['delta_total']),3)
    std_plot = round(np.std(data['delta_total']),3)
 
    #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    p2 = figure(title="Daily water consumptions in million of Liters", x_axis_type="datetime", tools=TOOLS, x_range = date)
    
    source2 = ColumnDataSource(data)
    p_circle = p2.circle(x = 'date', y = 'delta_total', size='s', color= 'c', alpha='a', 
              legend= "Consumption in ML (mean = {0}, std = {1})".format(mean_plot,std_plot), source = source2)

    source3 = ColumnDataSource(rolling)
    p_line_1 = p2.line(x='date', y='ub', legend='upper_bound (2 sigma)', line_dash = 'dashed', line_width = 4, 
            color = '#984ea3',source = source3)
    
    p_line_2 = p2.line(x='date', y='y_mean', source = source3, line_dash = 'dashed', line_width = 3, 
            legend='moving_average (window = {0} days)'.format(window_size), color = '#4daf4a')
    
    p2.legend.location = "top_left"
    p2.legend.click_policy= "hide"
    p2.ygrid.band_fill_color = "olive"
    p2.ygrid.band_fill_alpha = 0.1
    p2.xaxis.axis_label = 'Date'
    p2.yaxis.axis_label = 'Million of Liters'
    p2.xaxis.major_label_orientation = pi / 3
    p2.x_range = p1.x_range# Same axes as the heatMap
    p2.xaxis.formatter = FuncTickFormatter(code=""" var labels = %s; return labels[tick];""" % date)
    
    circle_hover = HoverTool(renderers=[p_circle],
                        tooltips=OrderedDict([('date', '@date'), 
                                              ('Water Consumption (ML)', '@delta_total'),
                                             ]))
    
    p_line_1_hover = HoverTool(renderers=[p_line_1],
                        tooltips=OrderedDict([('date', '@date'), 
                                              ('UpperBound water consumption (ML)', '@ub'),
                                             ]))
    
    p_line_2_hover = HoverTool(renderers=[p_line_2],
                        tooltips=OrderedDict([('date', '@date'), 
                                              ('Mean water consumption (ML)', '@y_mean'),
                                             ]))
    
    p2.add_tools(circle_hover)
    p2.add_tools(p_line_1_hover)
    p2.add_tools(p_line_2_hover)
    
    if plot_fig:
        show(gridplot([[p1,None],[p2,None]] , plot_width=1200, plot_height=400, toolbar_location = 'below'))
    
    return p1, p2
    
    
if __name__ == "__main__":
    data_aggregated = pd.read_csv('data/Data_heat_maps/aggregated_day/aggregated_day_total.csv')
    data_cc = pd.read_csv('data/Data_heat_maps/Customer Contacts/limited_occ_with_gps_time.csv', sep = ';')
    p1, p2 = multiple_plot(1163208, data_aggregated, data_cc, plot_fig = True)
    #multiple_plot(1255365, data_aggregated, data_cc, plot_fig = True)
    #multiple_plot(1813229, data_aggregated, data_cc, plot_fig = True)
    