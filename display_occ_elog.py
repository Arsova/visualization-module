from bokeh.io import output_file, show
from bokeh.models import (
GMapPlot, GMapOptions, CustomJS, ColumnDataSource, Circle, Triangle, Range1d, PanTool, WheelZoomTool, BoxSelectTool, BoxZoomTool, HoverTool,
ResetTool, Legend, LegendItem,LassoSelectTool)
from bokeh.models.widgets.sliders import DateRangeSlider
from collections import OrderedDict
import bokeh.plotting as bk
import pandas as pd
from datetime import date, datetime
from bokeh.models.widgets import DateRangeSlider
from bokeh.layouts import layout, widgetbox, column, row
from misc_functions import *
from bokeh.plotting import figure, curdoc
from bokeh.transform import linear_cmap
df1 = pd.read_csv('data/coordinates-codes.csv', delimiter=';', header=0)

# limited_occ_with_gps_new.csv (replace / with -)
df2 = pd.read_csv('data/limited_occ_with_gps_new.csv', delimiter=';')

lat=list(df2['Latitude'])
lon=list(df2['Longitude'])
city=list(df2['Address'])
issue=list(df2['Hoofdtype Melding'])
user=list(df2['Verbruiker Omschr'])
dates=list(df2['Datum'])
# dates = convert_to_date(dates)

lat_elog=list(df1['Lat'])
lon_elog=list(df1['Lon'])
place_elog=list(df1['Place'])
location_elog=list(df1['Location'])
zipcode_elog=list(df1['Zipcode'])
value_elog = return_value_list(locations=location_elog)



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

source_original = bk.ColumnDataSource(
    data=dict(
        lat=lat,
        lon=lon,
        city=city,
        issue=issue,
        dates=dates
    )
)

source = bk.ColumnDataSource(
    data=dict(
        lat=lat,
        lon=lon,
        city=city,
        issue=issue,
        dates=dates
    )
)

#create filtering function
def filter_occurrences(attr,old,new):
    val0 = str(slider.value[0])
    val0 = val0[:-3]
    val0 = date.fromtimestamp(int(val0))
    val1 = str(slider.value[1])
    val1 = val1[:-3]
    val1 = date.fromtimestamp(int(val1))
    source.data={key:[value for i, value in enumerate(source_original.data[key])
    if convert_to_date(source_original.data["dates"][i])>=val0 and convert_to_date(source_original.data["dates"][i])<=val1]
    for key in source_original.data}
    source_elog.data['value_elog'] = return_value_list(location_elog, str(val0), str(val1))

slider = DateRangeSlider(start=date(2017, 1, 1), end=date(2017, 12, 31), value=(date(2017, 1, 1), date(2017, 12, 31)),
step=1)
slider.on_change("value", filter_occurrences)

map_options = GMapOptions(lat=51.4416, lng=5.4697, map_type="terrain", zoom=12)
plot = GMapPlot(x_range=Range1d(), y_range=Range1d(), map_options=map_options)
plot.title.text = "Eindhoven city"
plot.api_key = "AIzaSyDxSgu79SAfdCxfdla-WYA-qPq7uERoP9M"

triangle = Triangle(x="lon", y="lat", size=12, fill_color="red", fill_alpha=0.5, line_color=None, name="occurrences")
glyph_triangle = plot.add_glyph(source, triangle)

circle = Circle(x="lon_elog", y="lat_elog", size=12, fill_color=linear_cmap("value_elog",
palette = ['#6baed6', '#4292c6', '#2171b5', '#08519c', '#08306b'],
low=min(source_elog.data["value_elog"]), high=max(source_elog.data["value_elog"])),
fill_alpha=0.5, line_color=None, name="elog locations")

glyph_circle = plot.add_glyph(source_elog, circle)

plot.add_tools(PanTool(), WheelZoomTool(), BoxSelectTool(), BoxZoomTool(match_aspect=True),
	    ResetTool(), LassoSelectTool())

triangle_hover = HoverTool(renderers=[glyph_triangle],
                         tooltips=OrderedDict([
                             ("Location", "@city"),
                             ("Date", "@dates"),
                             ("Problem", "@issue")
                         ]))
plot.add_tools(triangle_hover)

circle_hover = HoverTool(renderers=[glyph_circle],
                         tooltips=OrderedDict([
                             ("Place", "@place_elog")
                         ]))
plot.add_tools(circle_hover)

legend = Legend(items=[
    LegendItem(label="elog locations"   , renderers=[glyph_circle]),
    LegendItem(label="occurrences" , renderers=[glyph_triangle])
], orientation="vertical", click_policy="hide")
plot.add_layout(legend, "center")
# output_file("figures/gmap_plot.html")
layout = column(slider, plot)
curdoc().add_root(layout)
