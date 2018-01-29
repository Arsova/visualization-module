from bokeh.io import output_file, show
from bokeh.models import (
GMapPlot, GMapOptions, ColumnDataSource, Circle, Triangle, Range1d, PanTool, WheelZoomTool, BoxSelectTool, BoxZoomTool, HoverTool,
ResetTool)
from collections import OrderedDict
import bokeh.plotting as bk
import pandas as pd
map_options = GMapOptions(lat=51.4416, lng=5.4697, map_type="terrain", zoom=12)
plot = GMapPlot(x_range=Range1d(), y_range=Range1d(), map_options=map_options)
plot.title.text = "Eindhoven"


# For GMaps to function, Google requires you obtain and enable an API key:
#
#     https://developers.google.com/maps/documentation/javascript/get-api-key
#
# Replace the value below with your personal API key:
plot.api_key = ""

df = pd.read_csv('data/limited_occ_with_gps.csv', delimiter=';')

lat=list(df['Latitude'])
lon=list(df['Longitude'])
city=list(df['Address'])
issue=list(df['Hoofdtype Melding'])
user=list(df['Verbruiker Omschr'])
date=list(df['Datum'])

source = bk.ColumnDataSource(
    data=dict(
        lat=lat,
        lon=lon,
        city=city,
        issue=issue,
        date=date
    )
)

triangle = Triangle(x="lon", y="lat", size=12, fill_color="red", fill_alpha=0.5, line_color=None)
plot.add_glyph(source, triangle)

plot.add_tools(PanTool(), WheelZoomTool(), BoxSelectTool(), BoxZoomTool(match_aspect=True), HoverTool(),
	    ResetTool())
hover = plot.select(dict(type=HoverTool))
hover.tooltips = OrderedDict([
    ("(lat,lon)", "(@lat, @lon)"),
    ("Place", "@city"),
    ("Date", "@date"),
    ("Problem", "@issue")
])
output_file("figures/gmap_plot.html")
bk.show(plot)
