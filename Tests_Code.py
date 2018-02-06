# -*- coding: utf-8 -*-
"""
Created on Mon Feb  5 16:48:27 2018

@author: s157084
"""
from elog_visualisations import *
from display_occ_elog import *
# imports
from bokeh.io import output_file, show
from bokeh.models import (
GMapPlot, GMapOptions, ColumnDataSource, Circle, Triangle, Range1d, PanTool, WheelZoomTool, BoxSelectTool, BoxZoomTool, HoverTool,
ResetTool, Legend, LegendItem,LassoSelectTool, CheckboxGroup)
from bokeh.models.widgets.sliders import DateRangeSlider
from collections import OrderedDict
import bokeh.plotting as bk
import pandas as pd
from datetime import date, datetime
from bokeh.models.callbacks import CustomJS
from bokeh.models.widgets import DateRangeSlider
from bokeh.layouts import layout, widgetbox, column, gridplot
from misc_functions import *
from bokeh.plotting import figure, curdoc
from bokeh.transform import linear_cmap, log_cmap



data_aggregated = pd.read_csv('data/Data_heat_maps/aggregated_day/aggregated_day_total.csv')
data_cc = pd.read_csv('data/Data_heat_maps/Customer Contacts/limited_occ_with_gps_time.csv', sep = ';')
p1, p2 = multiple_plot(1163208, data_aggregated, data_cc, plot_fig = False)
Tmap_layout = return_layout()

heatmap_layout = gridplot([[p1,None],[p2,None]] , plot_width=1200, plot_height=400, toolbar_location = 'below')
layout=column([map_layout, heatmap_layout])
curdoc().add_root(layout)
