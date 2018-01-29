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

map_options = GMapOptions(lat=51.4416, lng=5.4697, map_type="terrain", zoom=12)
plot = GMapPlot(x_range=Range1d(), y_range=Range1d(), map_options=map_options)
plot.title.text = "Eindhoven"



# For GMaps to function, Google requires you obtain and enable an API key:
#
#     https://developers.google.com/maps/documentation/javascript/get-api-key
#
# Replace the value below with your personal API key:
plot.api_key = "AIzaSyDxSgu79SAfdCxfdla-WYA-qPq7uERoP9M"

df = pd.read_csv('data/limited_occ_with_gps.csv', delimiter=';')

lat=list(df['Latitude'])
lon=list(df['Longitude'])
city=list(df['Address'])
issue=list(df['Hoofdtype Melding'])
user=list(df['Verbruiker Omschr'])
dates=list(df['Datum'])
dates = convert_to_date(dates)
print(dates)
source = bk.ColumnDataSource(
    data=dict(
        lat=lat,
        lon=lon,
        city=city,
        issue=issue,
        dates=dates
    )
)

triangle = Triangle(x="lon", y="lat", SOUsize=12, fill_color="red", fill_alpha=0.5, line_color=None)
plot.add_glyph(source, triangle)

plot.add_tools(PanTool(), WheelZoomTool(), BoxSelectTool(), BoxZoomTool(match_aspect=True), HoverTool(),
	    ResetTool())
hover = plot.select(dict(type=HoverTool))
hover.tooltips = OrderedDict([
    ("(lat,lon)", "(@lat, @lon)"),
    ("Place", "@city"),
    ("Date", "@dates"),
    ("Problem", "@issue")
])

def callback(source=source, window=None):
    data = source.data
    f1 = cb_obj.value[0]
    f2 = cb_obj.value[1]
    print(f1)
    print(f2)
    lat, lon, city, issue, dates = data['lat'], data['lon'], data['city'], data['issue'], data['dates']
    lat_new = []
    lon_new = []
    city_new = []
    issue_new = []
    dates_new = []
    for i in range(len(lat)):
        if dates[i] >= f1 and dates[i] <= f2:
            lat_new.append(lat[i])
            lon_new.append(lon[i])
            city_new.append(city[i])
            issue_new.append(issue[i])
            dates_new.append(dates[i])
    lat, lon, city, issue, dates = lat_new, lon_new, city_new, issue_new, dates_new
    source.change.emit()

slider = DateRangeSlider(start=date(2017, 1, 1), end=date(2017, 12, 31), value=(date(2017, 1, 1), date(2017, 12, 31)), \
step=1, callback=CustomJS.from_py_func(callback))

layout = column(slider, plot)
output_file("figures/gmap_plot.html")
bk.show(layout)
# curdoc().add_root(layout)
