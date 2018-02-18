from bokeh.io import output_file, show
import pandas as pd
from bokeh.layouts import column
import numpy as np
from datetime import datetime,timedelta
from bokeh.layouts import column, row
from bokeh.layouts import gridplot
from bokeh.plotting import figure, show, output_file
from bokeh.models.ranges import Range1d
from bokeh.models import ColumnDataSource, HoverTool,LinearAxis, NumeralTickFormatter
from bokeh.plotting import figure, curdoc
from bokeh.models.glyphs import VBar, Line
from bokeh.models.markers import Circle
from collections import OrderedDict
from misc_functions import *

def pre_process_Eindhoven(df):
    df['dummy'] = 1
    df = df.groupby(["Datum","Verbruiker Omschr","Hoofdtype Melding"], as_index=False)["dummy"].count()
    df.columns = ["Date","Type_of_facility","Reason_for_complain","Number of complains"]
    df['Date2'] = pd.to_datetime(df['Date']).apply(lambda x: x.strftime('%Y-%m-%d'))

    df_Numb_com = pd.DataFrame(df[["Date","Number of complains"]].groupby("Date", as_index=False).sum())
    return df, df_Numb_com



def plot_function(average_usage_df, complaints_df, Eindhoven2):

    average_usage_df.sort_values(['Date'], inplace=True)
    average_usage_df.reset_index(drop=True, inplace=True)
    values = list(Eindhoven2['Reason_for_complain'].unique())

    def convert_to_datetime(x):
        return np.array(x, dtype=np.datetime64)

    date_list = list(average_usage_df['Date'])

    source_usage = ColumnDataSource(data=dict(
                    Date=convert_to_datetime(average_usage_df['Date']),
                                    value=average_usage_df['delta_total']
    ))

    source_events = ColumnDataSource(data=dict(
                    Date=convert_to_datetime(complaints_df['Date']),
                                    value=complaints_df["Number of complaints"]
    ))




    TOOLS_exploration = "save,pan ,reset, wheel_zoom, xbox_select"
    ######################################Bar chart with line chart#########################################################
    #layout settings of chart 1
    plot_events_usage = figure(x_axis_type="datetime",
                title="Average usage based on e_log meters and number of events in Eindhoven",
                toolbar_location="above",
                plot_width=1400, plot_height=400,
                y_range=Range1d(start=0, end=max(df["Number of complains"]+5)),
                tools=TOOLS_exploration, active_drag="xbox_select"
                )


    plot_events_usage.grid.grid_line_alpha=1
    plot_events_usage.xaxis.axis_label = 'Date'
    plot_events_usage.yaxis.axis_label= "Number of events"

    # Define 1st y-axis
    plot_events_usage.yaxis.axis_label = 'Number of events'
    plot_events_usage.y_range = Range1d(start=0, end=max(df["Number of complains"]+20))

    # Create 2nd LHS y-axis
    plot_events_usage.extra_y_ranges['water_usage'] = Range1d(start=min(average_usage_df['delta_total']-10),
                                               end=max(average_usage_df['delta_total']+10000))
    plot_events_usage.add_layout(LinearAxis(y_range_name='water_usage', axis_label='Water usage [l]'), 'right')

    line_plot = plot_events_usage.line('Date', 'value',source=source_usage, color="firebrick",
            legend='Water usage', line_width =3, y_range_name='water_usage')
    # line_plot = plot_events_usage.add_glyph(source_usage, line_glyph)



    plot_events_usage.vbar(x="Date", top="value", source=source_events,
            width=1, color="green", line_width =2, legend='Number of events')

    plot_events_usage.circle('Date', 'value', size=1, source=source_usage, selection_color="firebrick",
              nonselection_fill_color="firebrick", y_range_name='water_usage')
    bar_chart_source = ColumnDataSource(data=dict(Reason=[], Count=[]))

    def return_df_for_bar_chart(start='2017-01-01', end = '2017-12-31'):
        start = convert_to_date_reverse(start)
        end = convert_to_date_reverse(end)
        values = list(Eindhoven2['Reason_for_complain'].unique())
        values = pd.DataFrame(values)
        values.columns = ['Reason']
        new_df = Eindhoven2.loc[Eindhoven2['Date']>=start]
        new_df = new_df.loc[new_df['Date']<=end]
        new_df = new_df.groupby(['Reason_for_complain'])['Number of complains'].agg('sum')
        new_df = pd.DataFrame(new_df)
        new_df.columns = ['Count']
        new_df['Reason'] = new_df.index
        average_usage_df=pd.merge(rng,average_usage, how='outer',on='Date')
        new_df.reset_index(inplace=True, drop=True)
        new_df = pd.merge(values, new_df, how='outer', on='Reason')
        new_df = new_df.fillna(0)
        # print(new_df)
        bar_chart_source.data['Reason'] = new_df['Reason']
        bar_chart_source.data['Count'] = new_df['Count']


    # plot_events_usage.tool_events.on_change('geometries', cb)
    def selectedCallback(attr, old, new):
        print(new['1d']['indices'])

        index0 = min(new['1d']['indices'])
        index1 = max(new['1d']['indices'])
        print(index0)
        print(index1)
        print(len(new['1d']['indices']))
        date0 = str(date_list[index0]).split(' ')[0]
        date1 = str(date_list[index1]).split(' ')[0]
        print(date0)
        print(date1)
        return_df_for_bar_chart(date0, date1)

    return_df_for_bar_chart()
        # val0 = val0[:-3]
        # val0 = date.fromtimestamp(int(val0))
        # val1 = str(slider_events.value[1])
        # val1 = val1[:-3]
        # val1 = date.fromtimestamp(int(val1))

    source_usage.on_change('selected', selectedCallback)

    line_hover = HoverTool(renderers=[line_plot],
                             tooltips=OrderedDict([
                                 ("Usage", "@value{int}"),
                                 ("Date", "@Date{%F %T}")
                             ]),
                          formatters={"Date": "datetime"})
    plot_events_usage.add_tools(line_hover)


    plot_events_usage.legend.location = "top_left"
    plot_events_usage.legend.click_policy="hide"
    palette = ['#a6cee3', '#1f78b4', '#b2df8a', '#33a02c', '#fb9a99', '#e31a1c', '#fdbf6f', '#ff7f00', '#cab2d6', '#6a3d9a']
    plot_bar_chart_events = figure(x_range=values, plot_height=550, y_axis_label = 'Number of events',
    plot_width=900, toolbar_location=None, title="Distribution of events")
    plot_bar_chart_events.vbar(x='Reason', top='Count', width=0.9, source=bar_chart_source, legend="Reason",
       line_color='white', fill_color=factor_cmap('Reason', palette=palette, factors=bar_chart_source.data['Reason']))
    plot_bar_chart_events.xaxis.major_label_orientation = 0.3
    # plot_bar_chart_events.legend.click_policy="hide"
    return plot_events_usage,plot_bar_chart_events

e_log = pd.read_csv("data/aggregated_day_total_2_positives.csv")
complaints = pd.read_excel('data/export_occurences.xlsx')
complaints = complaints.loc[complaints['Storingslocatie plaats']=='EINDHOVEN']

Eindhoven2, df = pre_process_Eindhoven(complaints)

# Create range of dates

rng = pd.DataFrame(pd.date_range(start='01/01/2017', end='12/31/2017'), columns = ['Date'])

df_dates_complaints=Eindhoven2[["Date","Number of complains"]].groupby("Date").sum()
df_dates_complaints.reset_index(inplace=True)
complaints_df = pd.merge(rng, df_dates_complaints, on='Date', how='outer')
complaints_df.columns = ['Date', 'Number of complaints']
average_usage=e_log.groupby("norm_date")["delta_total"].mean()
average_usage=average_usage.reset_index(drop=False)
average_usage["Date"]=pd.to_datetime(average_usage["norm_date"])
average_usage.drop("norm_date", axis=1, inplace=True)
average_usage_df=pd.merge(rng,average_usage, how='outer',on='Date')
plot1, plot2 = plot_function(average_usage_df, complaints_df, Eindhoven2)
layout = column([plot1, plot2])
curdoc().add_root(layout)
