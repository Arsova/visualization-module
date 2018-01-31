from bokeh.io import output_file, show
from bokeh.models import (
GMapPlot, GMapOptions, CustomJS, ColumnDataSource, Circle, Triangle, Range1d, PanTool, WheelZoomTool, BoxSelectTool, BoxZoomTool, HoverTool,
ResetTool)
from bokeh.models.widgets.sliders import DateRangeSlider
from collections import OrderedDict
import bokeh.plotting as bk
import pandas as pd
from datetime import date, datetime
from bokeh.models.widgets import DateRangeSlider
from bokeh.layouts import layout, widgetbox, column, row
from misc_functions import *
from bokeh.plotting import figure, curdoc

# limited_occ_with_gps_new.csv (replace / with -)
df = pd.read_csv('data/limited_occ_with_gps_new.csv', delimiter=';')

lat=list(df['Latitude'])
lon=list(df['Longitude'])
city=list(df['Address'])
issue=list(df['Hoofdtype Melding'])
user=list(df['Verbruiker Omschr'])
dates=list(df['Datum'])
# dates = convert_to_date(dates)

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
    # print('value 0: ', slider.value[0])
    # print('value 1: ', slider.value[1])
    val0 = str(slider.value[0])
    val0 = val0[:-3]
    val0 = date.fromtimestamp(int(val0))
    val1 = str(slider.value[1])
    val1 = val1[:-3]
    val1 = date.fromtimestamp(int(val1))
    source.data={key:[value for i, value in enumerate(source_original.data[key])
    if convert_to_date(source_original.data["dates"][i])>=val0 and convert_to_date(source_original.data["dates"][i])<=val1]
    for key in source_original.data}

slider = DateRangeSlider(start=date(2017, 1, 1), end=date(2017, 12, 31), value=(date(2017, 1, 1), date(2017, 12, 31)),
step=1)
slider.on_change("value", filter_occurrences)

map_options = GMapOptions(lat=51.4416, lng=5.4697, map_type="terrain", zoom=12)
plot = GMapPlot(x_range=Range1d(), y_range=Range1d(), map_options=map_options)
plot.title.text = "Eindhoven city"
plot.api_key = "AIzaSyDxSgu79SAfdCxfdla-WYA-qPq7uERoP9M"

triangle = Triangle(x="lon", y="lat", size=12, fill_color="red", fill_alpha=0.5, line_color=None)
plot.add_glyph(source, triangle)

# plot.update()

plot.add_tools(PanTool(), WheelZoomTool(), BoxSelectTool(), BoxZoomTool(match_aspect=True), HoverTool(),
	    ResetTool())
hover = plot.select(dict(type=HoverTool))
hover.tooltips = OrderedDict([
    ("(lat,lon)", "(@lat, @lon)"),
    ("Place", "@city"),
    ("Date", "@dates"),
    ("Problem", "@issue")
])
# output_file("figures/gmap_plot.html")
layout = column(slider, plot)
curdoc().add_root(layout)
