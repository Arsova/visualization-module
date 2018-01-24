from bokeh.io import output_file, show
from bokeh.models import (
GMapPlot, GMapOptions, ColumnDataSource, Circle, Range1d, PanTool, WheelZoomTool, BoxSelectTool, BoxZoomTool, HoverTool,
ResetTool)
from collections import OrderedDict
import bokeh.plotting as bk
import pandas as pd
map_options = GMapOptions(lat=51.4416, lng=5.4697, map_type="terrain", zoom=12)
bk.output_file("maps.html",  mode="cdn")
plot = GMapPlot(x_range=Range1d(), y_range=Range1d(), map_options=map_options)
plot.title.text = "Eindhoven"


# For GMaps to function, Google requires you obtain and enable an API key:
#
#     https://developers.google.com/maps/documentation/javascript/get-api-key
#
# Replace the value below with your personal API key:
plot.api_key = ""

df = pd.read_csv('data/coordinates-codes.csv', delimiter=';', header=0)

lat=list(df['Lat'])
lon=list(df['Lon'])
city=list(df['Place'])

source = bk.ColumnDataSource(
    data=dict(
        lat=lat,
        lon=lon,
        city=city
    )
)

circle = Circle(x="lon", y="lat", size=15, fill_color="blue", fill_alpha=0.8, line_color=None)
plot.add_glyph(source, circle)

plot.add_tools(PanTool(), WheelZoomTool(), BoxSelectTool(), BoxZoomTool(match_aspect=True), HoverTool(),
	    ResetTool())
hover = plot.select(dict(type=HoverTool))
hover.tooltips = OrderedDict([
    ("(lat,lon)", "(@lat, @lon)"),
    ("Place", "@city")
])
output_file("gmap_plot.html")
bk.show(plot)
