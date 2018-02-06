# imports
from bokeh.io import output_file, show
from bokeh.models import (
GMapPlot, GMapOptions, ColumnDataSource, Circle, Triangle, Range1d, PanTool, WheelZoomTool, BoxSelectTool, BoxZoomTool, HoverTool,
ResetTool, Legend, LegendItem,LassoSelectTool, CheckboxGroup, TapTool)
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
from elog_visualisations import *
from bokeh.events import Tap

def return_layout():
    # read data files
    df1 = pd.read_csv('data/coordinates-codes-updated.csv', delimiter=';')
    # limited_occ_with_gps_new.csv (replace / with -)
    df2 = pd.read_csv('data/limited_occ_with_gps_new.csv', delimiter=';')

    # get selected attribtes for occurrences
    lat=list(df2['Latitude'])
    lon=list(df2['Longitude'])
    city=list(df2['Address'])
    issue=list(df2['Hoofdtype Melding'])
    user=list(df2['Verbruiker Omschr'])
    dates=list(df2['Datum'])
    # dates = convert_to_date(dates)
    occur_type = set(issue)
    occur_type = list(occur_type)
    occur_default = list(range(len(occur_type)))

    # get selected attribtes for elog
    lat_elog=list(df1['Lat'])
    lon_elog=list(df1['Lon'])
    place_elog=list(df1['Place'])
    location_elog=list(df1['Location'])
    zipcode_elog=list(df1['Zipcode'])
    value_elog = return_value_list(locations=location_elog)


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
        print(lat_elog[ind])
        print(lon_elog[ind])
        print(place_elog[ind])

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


    # Define slider and callbacks
    slider = DateRangeSlider(start=date(2017, 1, 1), end=date(2017, 12, 31), value=(date(2017, 1, 1), date(2017, 12, 31)), title="Consumption period",
    step=1, callback_policy="mouseup")
    slider.callback = CustomJS(args=dict(source=source_fake), code="""
        source.data = { value: [cb_obj.value] }
    """)


    #change fake data source, which in turn triggers filter function to modify the real data
    # slider.on_change(data, filter_occurrences)
    source_fake.on_change('data', filter_usage)


    slider_events = DateRangeSlider(start=date(2017, 1, 1), end=date(2017, 12, 31), value=(date(2017, 1, 1), date(2017, 12, 31)),
    step=1, title="Occurrence period")
    slider_events.on_change("value", filter_occurrences)

    checkbox_group = CheckboxGroup(
            labels=occur_type, active=occur_default)

    checkbox_group.on_change("active", filter_occurrences)


    # def tap_tool_handler(attr, old, new):
    #     print('Hello')
    # tap_tool = TapTool(names=['elog_locations'])
    # tap_tool.on_change('value', tap_tool_handler)



    # define maps, options
    map_options = GMapOptions(lat=51.4416, lng=5.4697, map_type="terrain", zoom=12)
    plot = GMapPlot(x_range=Range1d(), y_range=Range1d(), map_options=map_options)
    plot.title.text = "Eindhoven"

    # use your api key below
    plot.api_key = get_api_key()

    # triangle glyphs on the map
    triangle = Triangle(x="lon", y="lat", size=12, fill_color="red", fill_alpha=0.5, line_color=None, name="occurrences")
    glyph_triangle = plot.add_glyph(source, triangle)

    # circle glyphs on the map
    circle = Circle(x="lon_elog", y="lat_elog", size=12, fill_color=log_cmap("value_elog",
    palette = ['#74a9cf', '#3690c0', '#0570b0', '#045a8d', '#023858'],
    low=min(source_elog.data["value_elog"]), high=max(source_elog.data["value_elog"]), nan_color='green'),
    fill_alpha=0.5, line_color=None, name="elog_locations")
    glyph_circle = plot.add_glyph(source_elog, circle)


    # tools to include on the visualization
    plot.add_tools(PanTool(), WheelZoomTool(), BoxSelectTool(), BoxZoomTool(match_aspect=True),
    	    ResetTool(), LassoSelectTool(), TapTool())

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


    tap_tool = TapTool(names=['elog_locations'], renderers=[glyph_circle])
    # tap_tool.callback = CustomJS(args=dict(source=source_tap_tool), code="""
    #     source.data = { value: [cb_data.index['1d'].indices[0]] }
    # """)

    glyph_circle.data_source.on_change('selected', tap_tool_handler)
    # # in the broswer console, you will see messages when circles are clicked
    # tool = plot.select(dict(type=TapTool))
    # # tool.names.append("elog locations")
    #
    # def on_selection_change(obj, attr, old, new):
    #     print ("HIT!", old, new)
    #
    # renderer = plot.select(dict(name="elog locations"))
    # scatter_ds = renderer[0].data_source
    #
    # scatter_ds.on_change('selected', on_selection_change)
    #
    # show(p)  # open a browser


    # def function_test(attr, old, new):
    #
    #     print('Clicked..')
    #
    # source_elog_original.on_change('selected', function_test)
    # source_elog.on_change('selected', function_test)


    # Add legend
    legend = Legend(items=[
        LegendItem(label="elog_locations"   , renderers=[glyph_circle]),
        LegendItem(label="occurrences" , renderers=[glyph_triangle])
    ], orientation="vertical", click_policy="hide")
    plot.add_layout(legend, "center")

    # Add stuff to the app

    row1 = row([slider, slider_events])
    row2 = row([plot, checkbox_group])
    layout = column([row1, row2])
    return layout
    # curdoc().add_root(layout)
    # curdoc().add_root(source_fake)
