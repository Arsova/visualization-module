import numpy as np
from bokeh.plotting import figure, output_file, show
from bokeh.core.properties import value
import pandas as pd
from os.path import join, dirname
import datetime as dt

import pandas as pd
from scipy.signal import savgol_filter

from bokeh.io import curdoc
from bokeh.layouts import row, column
from bokeh.models import ColumnDataSource, DataRange1d, Select, Dropdown, CheckboxGroup, CustomJS, HoverTool, Legend, Paragraph, PreText
from bokeh.plotting import figure
from collections import OrderedDict
from bokeh.command.bootstrap import main

def get_water_balance_plot(plot=0):
    def get_dataset(lvl, axis, pattern):
        if (lvl=='20 minutes'):
            lvl='20min'
        if (lvl=='four weeks'):
            lvl='4weeks'
        if (axis=='Show values on both negative and positive axis'):
            axis_number=1
        else:
            axis_number=0
        if (pattern=='Follow the inflow pattern'):
            pattern=0
        else:
            pattern=1
        usage = pd.read_csv('visualization-module/data/water_balance/usage_water_balance_' + lvl +'_'+ str(axis_number)+ '.csv')
        inflow = pd.read_csv('visualization-module/data/water_balance/inflow_water_balance_' + lvl + '_'+ str(axis_number)+ '.csv')
        booster = pd.read_csv('visualization-module/data/water_balance/booster_water_balance_' + lvl + '_'+ str(axis_number)+ '.csv')
        usage['TimeStamp'] = pd.to_datetime(usage['TimeStamp'])
        inflow['TimeStamp'] = pd.to_datetime(inflow['TimeStamp'])
        booster['TimeStamp'] = pd.to_datetime(booster['TimeStamp'])
        total=pd.concat([usage, inflow, booster], axis=1)
        if (pattern==0):
            if (lvl == '4weeks' or lvl == 'week'):
                total['Households2']=total['Households'].iloc[1:] * (total['TotalInflow'].iloc[1:] / total['TotalInflow'].iloc[1:].mean())
                total['Households2']=total['Households2'].fillna(total.Households)
                total['Households'] = total['Households2']
                total=total.drop(['Households2'], axis=1)
            else:
                total['Households'] = total['Households'] * (total['TotalInflow'] / total['TotalInflow'].mean())
        #print(total['Households'])
        if (axis_number==0):
            total['Loss']=total['TotalInflow']-total['TotalBooster']-total['Households']
        if (axis_number==1):
            total['Loss']=total['TotalInflow']+total['TotalBooster']+total['Households']
        total_bar=total.apply(lambda x: x.abs() if np.issubdtype(x.dtype, np.number) else x)
        total_bar['Loss']=total['Loss']
        print('In 2017 there was in total '+str(round(total['Loss'].sum()))+' million liters of non registered water. This '+str(total['Loss'].sum()/total['TotalInflow'].sum()*100)+'% of the total inflow')
        print('total inflow: '+str(round(total['TotalInflow'].sum())))
        print('total outflow: '+str(round(total['TotalBooster'].sum())))
        print('total usage: '+str(round(total['Households'].sum())))
        print('total loss: ' + str(round(total['Loss'].sum())))
        print('In 2017 there was in total '+str(round(total_bar['Loss'].sum()))+' million liters of non registered water. This '+str(total_bar['Loss'].sum()/total_bar['TotalInflow'].sum()*100)+'% of the total inflow')
        if (lvl=='20min'):
            total_bar['width']=0.05
        elif (lvl=='hour'):
            total_bar['width']=0.15
        elif (lvl=='day'):
            total_bar['width']=2.2
        elif (lvl=='week'):
            total_bar['width']=16
        else:
            total_bar['width']=60
        return ColumnDataSource(data=total), ColumnDataSource(data=total_bar)

    # create a new plot with a datetime axis type

    def make_line_plot(source):
        p = figure(plot_width=1100, plot_height=450, x_axis_type='datetime', tools='box_zoom, pan, xwheel_zoom, reset', toolbar_location="above")
        p.title.text = 'The water balance of Eindhoven'
        p.xaxis.axis_label = "Time"
        p.yaxis.axis_label = "Million liters of water used"
        columns = ['Households', 'TotalInflow', 'TotalWelschap', 'TotalEindhoven', 'TotalBooster',
                   'Eindhoven_AanjVeldhoven1', 'Eindhoven_AanjVeldhoven2', 'Eindhoven_AanjNuenen',
                   'Eindhoven_AanjGeldrop', 'Loss']
        names = ['Usage in Eindhoven', 'Total inflow', 'Inflow Welschap', 'Inflow Eindhoven', 'Total outflow',
                 'Outflow Veldhoven 1', 'Outflow Veldhoven 2', 'Outflow Nuenen', 'Outflow Geldrop',
                 'Non registered water']
        colors = ['purple', '#084594', '#2171b5', '#6baed6', '#005a32', '#a1d99b', '#74c476', '#41ab5d', '#238b45',
                  'red']
        #for data, name, color in zip (columns, names, colors):
            #p.line('TimeStamp', data, color=color, line_width=2, legend=name, source=source)
        line0 = p.line('TimeStamp', columns[0], color=colors[0], line_width=2, source=source)
        line1 = p.line('TimeStamp', columns[1], color=colors[1], line_width=2, source=source)
        line2 = p.line('TimeStamp', columns[2], color=colors[2], line_width=2, source=source)
        line3 = p.line('TimeStamp', columns[3], color=colors[3], line_width=2, source=source)
        line4 = p.line('TimeStamp', columns[4], color=colors[4], line_width=2, source=source)
        line5 = p.line('TimeStamp', columns[5], color=colors[5], line_width=2, source=source)
        line6 = p.line('TimeStamp', columns[6], color=colors[6], line_width=2, source=source)
        line7 = p.line('TimeStamp', columns[7], color=colors[7], line_width=2, source=source)
        line8 = p.line('TimeStamp', columns[8], color=colors[8], line_width=2, source=source)
        line9 = p.line('TimeStamp', columns[9], color=colors[9], line_width=2, source=source)
        # inset usage line
        line2.visible = False
        line3.visible = False
        line5.visible = False
        line6.visible = False
        line7.visible = False
        line8.visible = False
        legend=Legend(items=[
            (names[0], [line0]),
            (names[1], [line1]),
            (names[2], [line2]),
            (names[3], [line3]),
            (names[4], [line4]),
            (names[5], [line5]),
            (names[6], [line6]),
            (names[7], [line7]),
            (names[8], [line8]),
            (names[9], [line9]),
        ], location =(0,-30))
        p.add_layout(legend, 'right')
        p.legend.click_policy = "hide"
        return p

    def make_bar_chart(source):
        stacks=['Households', 'Loss']
        names=['Usage in Eindhoven', 'Non registered water']
        colors=['purple', 'red']
        p = figure(plot_width=1100, plot_height=300, x_axis_type='datetime',
                   tools='box_zoom, pan, xwheel_zoom, reset')#, x_range=plot1.x_range)
        p.xaxis.axis_label = "Time"
        p.yaxis.axis_label = "Million liters of water used"
        p.vbar_stack(stacks, x='TimeStamp', line_width='width', width=2, source=source, color=colors, legend=[value(x) for x in names])
        p.legend.location = "bottom_right"
        p.legend.click_policy = "hide"
        return p

    def update_stats(source):
        text_box.text='In 2017 there was in total '+str(round(source['Loss'].sum()))+' million liters of non registered water. \nThis is '+str(round(source['Loss'].sum()/source['TotalInflow'].sum()*100,2))+'% of the total inflow. \nTotal inflow: '+str(round(source['TotalInflow'].sum()))+' million liters. \nTotal outflow: '+str(round(source['TotalBooster'].sum()))+' million liters. \nTotal usage: '+str(round(source['Households'].sum()))+' million liters.'

    def update_plot(attr, old, new):
        src_line, src_bar= get_dataset(level_select.value, axis_select.value, pattern_select.value)
        source_line.data=src_line.data
        source_bar.data = src_bar.data
        update_stats(source_bar.data)
        hover.tooltips = [
            ('Consumption', '$y million liters per %s' % (level_select.value)),
            ('Timestamp', '@TimeStamp'),
        ]





#show(widgetbox(p))


    pattern = 'Follow the inflow pattern'
    pattern_options=['Use the average usage', 'Follow the inflow pattern']
    pattern_select = Select(value=pattern, title='Usage pattern', options=pattern_options)
    axis = 'Show all values on the positive axis'
    axis_options=['Show all values on the positive axis', 'Show values on both negative and positive axis']
    axis_select = Select(value=axis, title='How to visualize positive and negative values?', options=axis_options)
    level = 'week'
    level_options=['20 minutes', 'hour', 'day', 'week', 'four weeks']
    level_select = Select(value=level, title='Aggregation level', options=level_options)

    source_line, source_bar=get_dataset(level, axis, pattern)
    plot1 = make_line_plot(source_line)
    plot2 = make_bar_chart(source_bar)
    level_select.on_change('value', update_plot)
    axis_select.on_change('value', update_plot)
    pattern_select.on_change('value', update_plot)
    #hover = plot1.select(dict(type=HoverTool))
    #hover.tooltips = [
    #    ('Consumption', '$y million liters per %s'%(level_select.value)),
    #    ('Timestamp', '@TimeStamp'),
    #]
    hover = HoverTool(tooltips=OrderedDict([
                                     ("Consumption", '$y million liters per %s'%(level_select.value)),
                                     ("Date", "@TimeStamp")
                                 ]))
    plot1.add_tools(hover)
    text_box = PreText(text='In 2017 there was in total '+str(round(source_bar.data['Loss'].sum(),0))+' million liters of non registered water. \nThis is '+str(round(source_bar.data['Loss'].sum()/source_bar.data['TotalInflow'].sum()*100,2))+'% of the total inflow. \nTotal inflow: '+str(round(source_bar.data['TotalInflow'].sum()))+' million liters. \nTotal outflow: '+str(round(source_bar.data['TotalBooster'].sum()))+' million liters. \nTotal usage: '+str(round(source_bar.data['Households'].sum()))+' million liters. '
    , width=550)
    controls = column(level_select, axis_select, pattern_select)
    column1=column(controls)
    row1=row(children=[plot1, column1])
    row2=row(children=[plot2, text_box])
    layout=column(row1,row2)
    if plot == 1:
        curdoc().add_root(layout)
        curdoc().title = "Water Balance"
    else:
        return layout

# get_water_balance_plot(plot=1)
