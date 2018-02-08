# imports
from bokeh.io import output_file, show
from bokeh.models import (
GMapPlot, GMapOptions, ColumnDataSource, Circle, Triangle, Range1d, PanTool, WheelZoomTool, HoverTool,
ResetTool, Legend, LegendItem, CheckboxGroup, TapTool, Button, TextInput, CustomJS)
from bokeh.models.widgets.sliders import DateRangeSlider
from collections import OrderedDict
import bokeh.plotting as bk
import pandas as pd
from datetime import date, datetime
from bokeh.models.callbacks import CustomJS
from bokeh.models.widgets import DateRangeSlider
from bokeh.layouts import layout, widgetbox, column, row
from misc_functions import *
from bokeh.plotting import figure, curdoc
from bokeh.transform import linear_cmap, log_cmap
#from elog_visualisations import *
from bokeh.events import Tap
from bokeh.models.glyphs import Rect
from bokeh.models.markers import Square
import numpy as np


def visualize():
    ########################################################################
    # read data files and process
    ########################################################################
    df_elog_coor = pd.read_csv('data/coordinates-codes-updated.csv', delimiter=';')
    # limited_occ_with_gps_new.csv (replace / with -)
    data_cc = pd.read_csv('data/limited_occ_with_gps_time.csv', delimiter=';')
    #booster location data
    df_booster_out = pd.read_csv('data/Installaties_Eindhoven_out.txt', delimiter=';')
    df_booster_in = pd.read_csv('data/Installaties_Eindhoven_in.txt', delimiter=';')

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
        source_radius_circle.data['lat_radius'] = lat
        source_radius_circle.data['lon_radius'] = lon
        source_radius_circle.data['rad_radius'] = radius
        
    def pre_process_hour_consuption(location):
        retrieve = str(location) + '.csv'
        data = pd.read_csv('data/Data_heat_maps/hour_consuption/' + retrieve)
        data.columns.name = 'date'
        data.index.name = 'hour'
        data.index = data.index.astype(str)
        hours = list(data.index)
        date = list(data.columns)
        date_range = [date[0], date[-1]]
        date = list(pd.date_range(start = date[0], end = date[-1]).strftime('%Y-%m-%d'))
        
        return data, hours, date, date_range
    
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

        # new consumption values for the elog locations
        source_elog.data['value_elog'] = return_value_list(location_elog, str(val0), str(val1))

    # Function to filter occurrences based on slider and checkbox selection
    def filter_occurrences(attr,old,new):

        #val1 and val2 are new slider values in timestamps
        # val0 = str(slider.value[0])
        val0 = str(slider_events.value[0])
        val0 = val0[:-3]
        val0 = date.fromtimestamp(int(val0))
        val1 = str(slider_events.value[1])
        val1 = val1[:-3]
        val1 = date.fromtimestamp(int(val1))

        # checkbox_group.active gives a list of indices corresponding to options selected using checkbox
        possible_events = [occur_type[i] for i in checkbox_group.active]

        # create new events source to display on map, controlled by slider
        source.data={key:[value for i, value in enumerate(source_original.data[key])
        if convert_to_date(source_original.data["dates"][i])>=val0 and convert_to_date(source_original.data["dates"][i])<=val1
        and source_original.data["issue"][i] in possible_events]
        for key in source_original.data}

    def tap_tool_handler(attr,old,new):
        ind = new['1d']['indices'][0]
        
        l1 = []
        l2 = []
        loc = []
        r = []
        
        l1.append(lat_elog[ind])
        l2.append(lon_elog[ind])
        loc.append(location_elog[ind])
        r.append(float(text_input.value))     
        plot_radius(l1, l2, r)
        #call data frames
        data_heat, hours, date, date_range = pre_process_hour_consuption(loc[0])
        source_heat = ColumnDataSource(data_heat) #Equivalent to data
        
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
        

    ########################################################################
    # Define data sources
    ########################################################################

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
    source_heat = ColumnDataSource(data=dict(value=[]))

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
    slider_events = DateRangeSlider(start=date(2017, 1, 1), end=date(2017, 12, 31), value=(date(2017, 1, 1), date(2017, 12, 31)),
    step=1, title="Occurrence period")
    slider_events.on_change("value", filter_occurrences)

	# checkbox for event type
    checkbox_group = CheckboxGroup(labels=occur_type, active=occur_default)
    checkbox_group.on_change("active", filter_occurrences)

    # Button to remove radius feature
    button = Button(label="Remove Radius", button_type="success")
    button.on_click(reset_radius)

    # Text input for radius
    text_input = TextInput(value="3", title="Distance in km:")
    text_input.on_change('value', change_radius)

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
    # Plot Heat map
    ########################################################################
    colors_heat = ['#fff7fb', '#ece7f2', '#d0d1e6', '#a6bddb', '#74a9cf', '#3690c0', '#0570b0', '#045a8d', '#023858'] #Colors of the heat map
    data_heat = pd.DataFrame.from_dict(source_heat.data)
    
    
    ########################################################################
    # Manage layout
    ########################################################################
    row1 = row([slider, slider_events])
    column1 = column([checkbox_group, button, text_input])
    row2 = row([plot, column1])
    layout = column([row1, row2])

    curdoc().add_root(layout)
    
    	
temp  = visualize()
