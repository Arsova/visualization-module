# imports
from bokeh.io import output_file, show
from bokeh.models import (
GMapPlot, GMapOptions, ColumnDataSource, Circle, Triangle, Range1d, PanTool, WheelZoomTool, HoverTool,
ResetTool, Legend, LegendItem, CheckboxGroup, TapTool, Button, TextInput, LinearColorMapper,
    BasicTicker, PrintfTickFormatter, ColorBar, BoxAnnotation, Band, LogColorMapper, FuncTickFormatter,
PrintfTickFormatter, NumeralTickFormatter, LinearAxis, Range1d, Legend, Div, BoxAnnotation, Slider
)
from bokeh.models.widgets.sliders import DateRangeSlider
from collections import OrderedDict
import bokeh.plotting as bk
import pandas as pd
import numpy as np
from datetime import date, datetime, timedelta
from bokeh.models.callbacks import CustomJS
from bokeh.models.widgets import (
        DateRangeSlider, DataTable, TableColumn, HTMLTemplateFormatter, Panel, Tabs
        )
from bokeh.layouts import layout, widgetbox, column, row, gridplot
from misc_functions import *
from bokeh.plotting import figure, curdoc
from bokeh.transform import linear_cmap, log_cmap
from bokeh.events import Tap
from bokeh.models.glyphs import Rect, VBar, Line
from bokeh.models.markers import Square, Circle
from bokeh.models.ranges import Range1d
from calculate_water_balance import *
########################################################################
# read data files and process
########################################################################
df_elog_coor = pd.read_csv('visualization-module/data/coordinates-codes-updated.csv', delimiter=';')
# limited_occ_with_gps_new.csv (replace / with -)
data_cc = pd.read_csv('visualization-module/data/limited_occ_with_gps_time.csv', delimiter=';')
#booster location data
df_booster_out = pd.read_csv('visualization-module/data/Installaties_Eindhoven_out.txt', delimiter=';')
df_booster_in = pd.read_csv('visualization-module/data/Installaties_Eindhoven_in.txt', delimiter=';')
df_data_aggregated = pd.read_csv('visualization-module/data/aggregated_day_total_2_positives.csv')
df_table = pre_process_total(df_data_aggregated, df_elog_coor = df_elog_coor)

# get selected attribtes for occurrences
lat=list(data_cc['Latitude'])
lon=list(data_cc['Longitude'])
city=list(data_cc['Address'])
issue=list(data_cc['Hoofdtype Melding'])
user=list(data_cc['Verbruiker Omschr'])
dates=list(data_cc['Datum'])
# dates = convert_to_date(dates)
occur_type = set(issue)
occur_type = list(occur_type)
occur_default = list(range(len(occur_type)))

# get selected attribtes for elog
lat_elog=list(df_elog_coor['Lat'])
lon_elog=list(df_elog_coor['Lon'])
place_elog=list(df_elog_coor['Place'])
location_elog=list(df_elog_coor['Location'])
zipcode_elog=list(df_elog_coor['Zipcode'])
value_elog = return_value_list(locations=location_elog)

booster_lat_out = list(df_booster_out['Lat'])
booster_lon_out = list(df_booster_out['Lon'])
booster_name_out = list(df_booster_out['NAAM'])

booster_lat_in = list(df_booster_in['Lat'])
booster_lon_in = list(df_booster_in['Lon'])
booster_name_in = list(df_booster_in['NAAM'])

# exploration charts
def pre_process_Eindhoven(df):
    df['dummy'] = 1
    df = df.groupby(["Datum","Verbruiker Omschr","Hoofdtype Melding"], as_index=False)["dummy"].count()
    df.columns = ["Date","Type_of_facility","Reason_for_complain","Number of complains"]
    df['Date2'] = pd.to_datetime(df['Date']).apply(lambda x: x.strftime('%Y-%m-%d'))

    df_Numb_com = pd.DataFrame(df[["Date","Number of complains"]].groupby("Date", as_index=False).sum())
    return df, df_Numb_com

e_log = pd.read_csv("visualization-module/data/aggregated_day_total_2_positives.csv")
complaints = pd.read_excel('visualization-module/data/export_occurences.xlsx')
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

average_usage_df.sort_values(['Date'], inplace=True)
average_usage_df.reset_index(drop=True, inplace=True)
values = list(Eindhoven2['Reason_for_complain'].unique())

def convert_to_datetime(x):
    return np.array(x, dtype=np.datetime64)

date_list = list(average_usage_df['Date'])

########################################################################
# Event Handlers
########################################################################


def plot_radius(lat=[], lon=[], radius=[]):
    """
    This function calcualte plot a circle that represents the radious of the events selected into a map

    Parameters
    ---------------------------------
        lon: longitid of the eLog location
        lat: latitud of the eLog location
        radius: the circle radious in Km

    Return
    ---------------------------------
        events_selected: vector with the Id of the events selected
    """
    radius = [rad*1000 for rad in radius] #Convert to Km
    print(lat)
    print(lon)
    print(radius)
    source_radius_circle.data['lat_radius'] = lat
    source_radius_circle.data['lon_radius'] = lon
    source_radius_circle.data['rad_radius'] = radius


# create filtering function, calls return_value_list() to get new consumption values
def filter_usage(attr,old,new):

    #val1 and val2 are new slider values in timestamps
    # val0 = str(slider.value[0])
    val0 = source_fake.data['value'][0][0]
    val0 = str(val0)
    val0 = str(val0[:-3])
    val0 = date.fromtimestamp(int(val0))
    # val1 = str(slider.value[1])
    val1 = source_fake.data['value'][0][1]
    val1=str(val1)
    val1 = str(val1[:-3])
    val1 = date.fromtimestamp(int(val1))

    #this function creates dynamicly changes the heat map
    sorce_slider.data['start_date'] = [val0]
    sorce_slider.data['end_date'] = [val1]
    if sorce_slider.data['start_date'] != []:
        filter_sources_HM(start_date = sorce_slider.data['start_date'][0], end_date = sorce_slider.data['end_date'][0])

    # new consumption values for the elog locations
    source_elog.data['value_elog'] = return_value_list(location_elog, str(val0), str(val1))

# Function to filter occurrences based on slider and checkbox selection
# def filter_occurrences(attr,old,new):
#
#     #val1 and val2 are new slider values in timestamps
#     # val0 = str(slider.value[0])
#     val0 = str(source_fake_events.data['value'][0][0])
#     val0 = val0[:-3]
#     val0 = date.fromtimestamp(int(val0))
#     val1 = str(source_fake_events.data['value'][0][1])
#     val1 = val1[:-3]
#     val1 = date.fromtimestamp(int(val1))
#     # checkbox_group.active gives a list of indices corresponding to options selected using checkbox
#     possible_events = [occur_type[i] for i in checkbox_group.active]
#
#     # create new events source to display on map, controlled by slider
#     source.data={key:[value for i, value in enumerate(source_original.data[key])
#     if convert_to_date(source_original.data["dates"][i])>=val0 and convert_to_date(source_original.data["dates"][i])<=val1
#     and source_original.data["issue"][i] in possible_events]
#     for key in source_original.data}
#
#     #this function creates dynamicly changes the heat map
#     sorce_slider.data['start_date'] = [val0]
#     sorce_slider.data['end_date'] = [val1]
#     if sorce_slider.data['start_date'] != []:
#         filter_sources_HM(start_date = sorce_slider.data['start_date'][0], end_date = sorce_slider.data['end_date'][0])



def filter_sources_HM(start_date, end_date):

    def get_data_dates(CDS, start_date, end_date):
        return {
                key:[value for i, value in enumerate(CDS.data[key])
                     if convert_to_date_reverse(CDS.data["date"][i]) >= start_date and
                     convert_to_date_reverse(CDS.data["date"][i]) <= end_date] for key in CDS.data
                }

    source_heat_map_temp.data = get_data_dates(source_heat_map, start_date, end_date)
    source_data_aggregated_day_temp.data = get_data_dates(source_data_aggregated_day, start_date, end_date)
    source_rolling_temp.data = get_data_dates(source_rolling, start_date, end_date)
    source_events_temp.data = get_data_dates(source_events, start_date, end_date)



def heat_map_stuff(df_heat, data_aggregated_day, rolling):
    source_heat_map_update = ColumnDataSource(data=df_heat.reset_index().fillna('NaN').to_dict(orient="list"))
    source_heat_map.data = source_heat_map_update.data
    source_data_aggregated_day.data = ColumnDataSource(data=data_aggregated_day).data
    source_rolling.data = ColumnDataSource(data=rolling).data

    #Define the temporal maps
    source_heat_map_temp.data = source_heat_map_update.data
    source_data_aggregated_day_temp.data = ColumnDataSource(data=data_aggregated_day).data
    source_rolling_temp.data = ColumnDataSource(data=rolling).data




def get_new_heat_map_source(location, flag=0):
    data = pre_process_hour_consuption(location)
    df_heat = pd.DataFrame(data.stack(), columns=['rate']).reset_index()
    data_aggregated_day_local, rolling_local = pre_process_total(df_data_aggregated, location, 30)

    if flag == 1:
        return df_heat
    else:
        heat_map_stuff(df_heat, data_aggregated_day_local, rolling_local)


def get_events(lon, lat, radius, flag = 0):
    if flag == 1:
        return select_events(lon, lat, data_cc, radius)
    else:
        data_cc_filtered_local = select_events(lon, lat, data_cc, radius)
        source_events.data = ColumnDataSource(data = data_cc_filtered_local).data
        source_events_temp.data = ColumnDataSource(data = data_cc_filtered_local).data


def data_table_handler(attr,old,new):
     #Get data
     ind = new['1d']['indices'][0]
     lat = []
     lon =[]
     loc = []
     rad = []

     lat.append(source_table.data['Lat'].data[ind])
     lon.append(source_table.data['Lon'].data[ind])
     loc.append(source_table.data['Location'].data[ind])
     rad.append(float(text_input.value))
     # Print results
     plot_radius(lat, lon, rad)
     get_new_heat_map_source(loc[0], 0)
     get_events(lon, lat, rad, 0)
     if sorce_slider.data['start_date'] != []:
         filter_sources_HM(start_date = sorce_slider.data['start_date'][0], end_date = sorce_slider.data['end_date'][0])




def tap_tool_handler(attr,old,new):
    ind = new['1d']['indices'][0]
    l1 = []
    l2 = []
    r0 = []
    l1.append(lat_elog[ind])
    l2.append(lon_elog[ind])
    r0.append(float(text_input.value))
    plot_radius(l1, l2, r0)
    get_new_heat_map_source(location_elog[ind], 0)
    get_events(lon_elog[ind], lat_elog[ind], float(text_input.value), 0)
    if sorce_slider.data['start_date'] != []:
        filter_sources_HM(start_date = sorce_slider.data['start_date'][0], end_date = sorce_slider.data['end_date'][0])


def reset_radius():
    l1 = []
    l2 = []
    r = []
    plot_radius(l1, l2, r)

def change_radius(attr,old,new):
    new_rad = float(text_input.value)*1000
    r = []
    r.append(new_rad)
    source_radius_circle.data['rad_radius'] = r
    get_events(source_radius_circle.data['lon_radius'], source_radius_circle.data['lat_radius'], float(text_input.value), 0)
    if sorce_slider.data['start_date'] != []:
        filter_sources_HM(start_date = sorce_slider.data['start_date'][0], end_date = sorce_slider.data['end_date'][0])

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
    try:
        index0 = min(new['1d']['indices'])
        index1 = max(new['1d']['indices'])
        print(index0)
        print(index1)
        print(len(new['1d']['indices']))
        date0 = str(date_list[index0]).split(' ')[0]
        date1 = str(date_list[index1]).split(' ')[0]

    except:
        date0 = '2017-01-01'
        date1 = '2017-12-31'

    print(date0)
    print(date1)
    val0 = convert_to_date_reverse(date0)
    val1 = convert_to_date_reverse(date1)

    possible_events = [occur_type[i] for i in checkbox_group.active]

    source.data={key:[value for i, value in enumerate(source_original.data[key])
    if convert_to_date(source_original.data["dates"][i])>=val0 and convert_to_date(source_original.data["dates"][i])<=val1
    and source_original.data["issue"][i] in possible_events]
    for key in source_original.data}

    sorce_slider.data['start_date'] = [val0]
    sorce_slider.data['end_date'] = [val1]

    if sorce_slider.data['start_date'] != []:
        filter_sources_HM(start_date = sorce_slider.data['start_date'][0], end_date = sorce_slider.data['end_date'][0])

    # new consumption values for the elog locations
    source_elog.data['value_elog'] = return_value_list(location_elog, str(val0), str(val1))

    return_df_for_bar_chart(date0, date1)

def checkbox_filter_callback(attr, old, new):
    val0 = sorce_slider.data['start_date'][0]
    val1 = sorce_slider.data['end_date'][0]

    possible_events = [occur_type[i] for i in checkbox_group.active]

    source.data={key:[value for i, value in enumerate(source_original.data[key])
    if convert_to_date(source_original.data["dates"][i])>=val0 and convert_to_date(source_original.data["dates"][i])<=val1
    and source_original.data["issue"][i] in possible_events]
    for key in source_original.data}
########################################################################
# Define data sources
########################################################################
#data source to hadle the dinamic interface
sorce_slider = bk.ColumnDataSource(
    data=dict(
        start_date=[date(2017,1,1)],
        end_date=[date(2017,12,31)]
    )
)

# data source for drawing radius circle
source_radius_circle = bk.ColumnDataSource(
    data=dict(
        lat_radius=[],
        lon_radius=[],
        rad_radius=[]
    )
)

# data source for outflow boosters
source_booster_out = bk.ColumnDataSource(
    data=dict(
        booster_lat=booster_lat_out,
        booster_lon=booster_lon_out,
        booster_name=booster_name_out
    )
)

# data source for inflow pumping stations
source_booster_in = bk.ColumnDataSource(
    data=dict(
        booster_lat=booster_lat_in,
        booster_lon=booster_lon_in,
        booster_name=booster_name_in
    )
)

# original data source for elog data
source_elog_original = bk.ColumnDataSource(
    data=dict(
        lat_elog=lat_elog,
        lon_elog=lon_elog,
        place_elog=place_elog,
        location_elog=location_elog,
        zipcode_elog=zipcode_elog,
        value_elog = value_elog
    )
)

# dynamic data source for elog data
source_elog = bk.ColumnDataSource(
    data=dict(
        lat_elog=lat_elog,
        lon_elog=lon_elog,
        place_elog=place_elog,
        location_elog=location_elog,
        zipcode_elog=zipcode_elog,
        value_elog = value_elog
    )
)

# original data source for events data
source_original = bk.ColumnDataSource(
    data=dict(
        lat=lat,
        lon=lon,
        city=city,
        issue=issue,
        dates=dates
    )
)

# dynamic data source for events data
source = bk.ColumnDataSource(
    data=dict(
        lat=lat,
        lon=lon,
        city=city,
        issue=issue,
        dates=dates
    )
)

# dummy data source to trigger real callback
source_fake = ColumnDataSource(data=dict(value=[]))

# dummy data source to trigger real callback
source_fake_events = ColumnDataSource(data=dict(value=[]))

source_heat_map_misc = bk.ColumnDataSource(
    data=dict(
        date_range_0 = [],
        date_range_1 = [],
        location = [],
        x_range = [],
        y_range = [],
        df_rate_max = []
    )
)

# define sorce for the box
source_table = bk.ColumnDataSource(data = df_table)

# Source for exploration charts
source_usage = ColumnDataSource(data=dict(
                Date=convert_to_datetime(average_usage_df['Date']),
                                value=average_usage_df['delta_total']
))

source_events = ColumnDataSource(data=dict(
                Date=convert_to_datetime(complaints_df['Date']),
                                value=complaints_df["Number of complaints"]
))

bar_chart_source = ColumnDataSource(data=dict(Reason=[], Count=[]))
########################################################################
# Define widgets
########################################################################

# slider and callbacks for water usage
slider = DateRangeSlider(start=date(2017, 1, 1), end=date(2017, 12, 31), value=(date(2017, 1, 1), date(2017, 12, 31)), title="Consumption period",
step=1, callback_policy="mouseup")
slider.callback = CustomJS(args=dict(source=source_fake), code="""
    source.data = { value: [cb_obj.value] }
""")

# change fake data source, which in turn triggers filter function to modify the real data
source_fake.on_change('data', filter_usage)

# slider and callbacks for events
# slider_events = DateRangeSlider(start=date(2017, 1, 1), end=date(2017, 12, 31), value=(date(2017, 1, 1), date(2017, 12, 31)),
# step=1, title="Occurrence period", callback_policy="mouseup")
# slider_events.callback = CustomJS(args=dict(source=source_fake_events), code="""
#     source.data = { value: [cb_obj.value] }
# """)
#
# source_fake_events.on_change("data", filter_occurrences)

# checkbox for event type
checkbox_group = CheckboxGroup(
        labels=occur_type, active=occur_default)

checkbox_group.on_change("active", checkbox_filter_callback)

# Button to remove radius feature
button = Button(label="Remove Radius", button_type="success")
button.on_click(reset_radius)

# Text input for radius
text_input = TextInput(value="3", title="Distance in km:")
text_input.on_change('value', change_radius)

#Create table with summary
#For iteractivity:
#https://github.com/bokeh/bokeh/wiki/Filterable-Data-Source

columns_table = [
        TableColumn(field="Location", title="Location"),
        TableColumn(field="Place", title="Place"),
        TableColumn(field="number_days", title="Number of days recorded"),
        TableColumn(field="number_outliers", title="Number of outliers"),
        TableColumn(field="average_outliers", title="Outliers per day"),
    ]

data_table = DataTable(source = source_table, columns = columns_table, width=600, height=800)
source_table.on_change('selected', data_table_handler)

########################################################################
# Define map layput
########################################################################

# define maps, options
map_options = GMapOptions(lat=51.4416, lng=5.4697, map_type="terrain", zoom=12)
plot = GMapPlot(x_range=Range1d(), y_range=Range1d(), map_options=map_options)
plot.title.text = "Eindhoven"

# use your api key below
plot.api_key = get_api_key()

########################################################################
# Define glyphs
########################################################################

# triangle glyphs on the map
triangle_event = Triangle(x="lon", y="lat", size=12, fill_color="red", fill_alpha=0.5, line_color=None, name="occurrences")
glyph_triangle = plot.add_glyph(source, triangle_event)

# circle glyphs on the map
circle_elog = Circle(x="lon_elog", y="lat_elog", size=12, fill_color=log_cmap("value_elog",
palette = ['#74a9cf', '#3690c0', '#0570b0', '#045a8d', '#023858'],
low=min(source_elog.data["value_elog"]), high=max(source_elog.data["value_elog"]), nan_color='green'),
fill_alpha=0.5, line_color=None, name="elog_locations")
glyph_circle = plot.add_glyph(source_elog, circle_elog)

circle_radius = Circle(x="lon_radius", y="lat_radius", radius= "rad_radius", fill_alpha=0.5, line_color='black')
glyph_circle_radius = plot.add_glyph(source_radius_circle, circle_radius)

square_out = Square(x="booster_lon", y="booster_lat", size=15, fill_color="brown", line_color=None)
glyph_square_out = plot.add_glyph(source_booster_out, square_out)

square_in = Square(x="booster_lon", y="booster_lat", size=15, fill_color="green", line_color=None)
glyph_square_in = plot.add_glyph(source_booster_in, square_in)

########################################################################
# Other misc tools: hovers, taps, etc
########################################################################


# tools to include on the visualization
plot.add_tools(PanTool(), WheelZoomTool(),
	    ResetTool(), TapTool())

# Hover tool for triangles
triangle_hover = HoverTool(renderers=[glyph_triangle],
                         tooltips=OrderedDict([
                             ("Location", "@city"),
                             ("Date", "@dates"),
                             ("Problem", "@issue")
                         ]))
plot.add_tools(triangle_hover)

# Hover tool for circles
circle_hover = HoverTool(renderers=[glyph_circle],
                         tooltips=OrderedDict([
                             ("Place", "@place_elog"),
                             ("Usage", '@value_elog')
                         ]))
plot.add_tools(circle_hover)

# Hover tool for booster out
booster_out_hover = HoverTool(renderers=[glyph_square_out],
                         tooltips=OrderedDict([
                             ("Location", "@booster_name")
                         ]))
plot.add_tools(booster_out_hover)

# Hover tool for booster in
booster_in_hover = HoverTool(renderers=[glyph_square_in],
                         tooltips=OrderedDict([
                             ("Location", "@booster_name")
                         ]))
plot.add_tools(booster_in_hover)

# Tap tool for elog circles
tap_tool = TapTool(names=['elog_locations'], renderers=[glyph_circle])
glyph_circle.data_source.on_change('selected', tap_tool_handler)

# Add legend
legend = Legend(items=[
    LegendItem(label="elog_locations"   , renderers=[glyph_circle]),
    LegendItem(label="occurrences" , renderers=[glyph_triangle]),
    LegendItem(label="Inflow" , renderers=[glyph_square_in]),
    LegendItem(label="Outflow" , renderers=[glyph_square_out])
], orientation="vertical", click_policy="hide")
plot.add_layout(legend, "center")

########################################################################
### Exploration charts
########################################################################
TOOLS_exploration = "save,pan ,reset, wheel_zoom, xbox_select"
######################################Bar chart with line chart#########################################################
#layout settings of chart 1
plot_events_usage = figure(x_axis_type="datetime",
            title="Average usage based on e_log meters and number of events in Eindhoven",
            toolbar_location="left",
            plot_width=1400, plot_height=300,
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

return_df_for_bar_chart()

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
plot_bar_chart_events = figure(x_range=values, plot_height=550, plot_width=700, y_axis_label = 'Number of events',
toolbar_location=None, title="Distribution of events")
plot_bar_chart_events.vbar(x='Reason', top='Count', width=0.9, source=bar_chart_source, legend="Reason",
   line_color='white', fill_color=factor_cmap('Reason', palette=palette, factors=bar_chart_source.data['Reason']))
plot_bar_chart_events.xaxis.major_label_orientation = 0.4
plot_events_usage.min_border_top = 5
########################################################################
# Plot Heat map
#######################################################################


########################################################################
# Define initial parameters
########################################################################
df_heat1 = get_new_heat_map_source(location=1163208, flag=1)
data_aggregated_day, rolling = pre_process_total(df_data_aggregated,1163208, 30)
data_cc = pre_process_cc(data_cc)
data_cc_filtered = get_events(5.47255, 51.4412585, 3, flag = 1)
plot_radius([51.4412585], [5.47255], [3])

start = datetime.strptime("2017-01-01", "%Y-%m-%d")
end = datetime.strptime("2017-12-31", "%Y-%m-%d")
dates_list = list(pd.date_range(start = start, end = end).strftime('%Y-%m-%d'))
dates_list = [str(j) for j in dates_list]
hour_list = [str(x) for x in list(range(24))]

#define sources original
source_heat_map = ColumnDataSource(data=df_heat1)
source_data_aggregated_day = ColumnDataSource(data=data_aggregated_day)
source_rolling = ColumnDataSource(data = rolling)
source_events = ColumnDataSource(data = data_cc_filtered)

source_heat_map_temp = ColumnDataSource(data=df_heat1)
source_data_aggregated_day_temp = ColumnDataSource(data=data_aggregated_day)
source_rolling_temp = ColumnDataSource(data = rolling)
source_events_temp = ColumnDataSource(data = data_cc_filtered)


########################################################################
# Define Create graphs
########################################################################

colors_heat_map = ['#fff7fb', '#ece7f2', '#d0d1e6', '#a6bddb', '#74a9cf', '#3690c0', '#0570b0', '#045a8d', '#023858']
#     mapper = LinearColorMapper(palette=colors, low=df.rate.min(), high=df.rate.max())
mapper_heat_map = LogColorMapper(palette=colors_heat_map, low= 0, high=1000000)

TOOLS_heat_map = "save,pan ,reset, wheel_zoom"
p_heat_map = figure(title="Water consumption in Log(Liters)",x_axis_type="datetime", x_range = dates_list, y_range = list(reversed(hour_list)),
                    tools=TOOLS_heat_map)

heat_map = p_heat_map.rect(x="date", y="hour", width=1, height=1, source = source_heat_map_temp, fill_color={'field': 'rate', 'transform': mapper_heat_map}, line_color=None)
p_events = p_heat_map.triangle(x = 'date', y = 'Hour', legend= "Events", source = source_events_temp, color = 'color', size= 12, line_color="white")


color_bar = ColorBar(color_mapper=mapper_heat_map, border_line_color=None,label_standoff=12, location=(0, 0))
color_bar.formatter = NumeralTickFormatter(format='0.0')
p_heat_map.add_layout(color_bar, 'right')

heat_map_hover = HoverTool(renderers=[heat_map],
                    tooltips=OrderedDict([('Water Consumption (Liters)', '@rate'),
                                        ('date hour', '@date'),
                                         ('hour', '@hour'),
                                       ]))

events_hover = HoverTool(renderers=[p_events],
        tooltips=OrderedDict([('Event description',
        '@{Hoofdtype Melding}'),
        ]))



p_heat_map.grid.grid_line_color = None
p_heat_map.axis.axis_line_color = None
p_heat_map.axis.major_tick_line_color = None
p_heat_map.xaxis.major_label_text_font_size = '0pt'  # turn off x-axis tick labels
p_heat_map.yaxis.axis_label = 'Hour'
p_heat_map.xaxis.axis_label = None
p_heat_map.axis.major_label_standoff = 0

p_heat_map.legend.location = "top_left"
p_heat_map.legend.click_policy= "hide"
p_heat_map.add_tools(heat_map_hover)
p_heat_map.add_tools(events_hover)

#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
p_outliers = figure(title="Daily water consumptions in million of Liters", x_axis_type="datetime", tools=TOOLS_heat_map, x_range = dates_list)
p_circle = p_outliers.circle(x = 'date', y = 'delta_total', size='s', color= 'c', alpha='a', legend= "Consumption in ML",
                             source = source_data_aggregated_day_temp)

p_ub = p_outliers.line(x='date', y='ub', legend='upper_bound (2 sigma)', line_dash = 'dashed', line_width = 4, color = '#984ea3',
                       source = source_rolling_temp)
p_mean = p_outliers.line(x='date', y='y_mean', source = source_rolling_temp, line_dash = 'dashed', line_width = 3,
                         legend='moving_average', color = '#4daf4a')


# To create intervals we can follow:

p_outliers.legend.location = "top_left"
p_outliers.legend.orientation = "horizontal"
p_outliers.legend.click_policy= "hide"
p_outliers.ygrid.band_fill_color = "olive"
p_outliers.ygrid.band_fill_alpha = 0.1
p_outliers.xaxis.axis_label = None
p_outliers.yaxis.axis_label = 'Million of Liters'
p_outliers.xaxis.major_label_orientation = 3.1416 / 3
p_outliers.x_range = p_heat_map.x_range# Same axes as the heatMap
p_outliers.xaxis.formatter = FuncTickFormatter(code=""" var labels = %s; return labels[tick];""" % dates_list)


circle_hover = HoverTool(renderers=[p_circle],
                    tooltips=OrderedDict([('date', '@date'),
                                          ('Water Consumption (ML)', '@delta_total'),
                                         ]))

p_ub_hover = HoverTool(renderers=[p_ub],
                    tooltips=OrderedDict([('date', '@date'),
                                          ('UpperBound water consumption (ML)', '@ub'),
                                         ]))

p_mean_hover = HoverTool(renderers=[p_mean],
                    tooltips=OrderedDict([('date', '@date'),
                                          ('Mean water consumption (ML)', '@y_mean'),
                                         ]))

p_outliers.add_tools(circle_hover)
p_outliers.add_tools(p_ub_hover)
p_outliers.add_tools(p_mean_hover)

########################################################################
# Manage layout
########################################################################

plot_events_usage.min_border_left = 100
plot_bar_chart_events.min_border_right = 50
plot.min_border_right = 50

div1 = Div(text="<img src='visualization-module/static/brabant-water.jpg' margin-left:'45px' height='60' width='250' style='float:center';>")
# div2 = Div(text="<h1 style='color:#045a8d;font-family:verdana;font-size:100%;width=1000;display:inline;'>Interactive visualization of water consumption</h1>")
image_layout = gridplot([[div1]], plot_width=500, plot_height=400, toolbar_options={'logo': None, 'toolbar_location': None})
tools_layout = column([checkbox_group, button, text_input])
map_plot = gridplot([[plot]], plot_width=500, plot_height=600)
# row2 = row([tools_layout, map_plot, data_table])
row1 = row([plot_events_usage, image_layout])
row2 = row([plot_bar_chart_events, map_plot, tools_layout])
col = column([row1, row2])
heat_map_ = gridplot([[p_heat_map],[p_outliers]], plot_width=1000, plot_height=300, toolbar_location = 'left')
col = gridplot([[col]], toolbar_location = 'left')
heat_map_layout = row([heat_map_, data_table])
# row_final = row([row2, heat_map_layout])
tab1 = Panel(child=col, title="Events")
tab2 = Panel(child=heat_map_layout, title="Usage")
tab3 = Panel(child=get_water_balance_plot(plot=0), title="Water balance")
tabs = Tabs(tabs=[ tab1, tab2, tab3 ])
final_layout = gridplot([[tabs]], plot_width=2500, plot_height=700, toolbar_options={'logo': None, 'toolbar_location': None})
curdoc().add_root(final_layout)
