from bokeh.plotting import figure
from bokeh.transform import linear_cmap, log_cmap
from collections import OrderedDict
from bokeh.models import (
NumeralTickFormatter, ColorBar, FuncTickFormatter, HoverTool, LogColorMapper, Range1d, LinearAxis, Circle, Triangle,
GMapPlot, GMapOptions, PanTool, WheelZoomTool, TapTool, ResetTool, Legend, LegendItem
)
from misc_functions import *


def make_plots_tab2(source_heat_map_temp, source_events_temp, source_boundaries, source_rolling_temp, source_data_aggregated_day_temp, dates_list, hour_list):

    colors_heat_map = ['#fff7fb', '#ece7f2', '#d0d1e6', '#a6bddb', '#74a9cf', '#3690c0', '#0570b0', '#045a8d', '#023858']
    mapper_heat_map = LogColorMapper(palette=colors_heat_map, low= 0, high=1000000)

    TOOLS_heat_map = "save,pan ,reset, xwheel_zoom"

    p_heat_map = figure(title="Water consumption in Log(Litres)",x_axis_type="datetime", x_range = dates_list, y_range = list(reversed(hour_list)),
                        tools=TOOLS_heat_map)

    heat_map = p_heat_map.rect(x="date", y="hour", width=1, height=1, source = source_heat_map_temp, fill_color={'field': 'rate', 'transform': mapper_heat_map}, line_color=None)
    p_events = p_heat_map.triangle(x = 'date', y = 'Hour', legend= "Events", source = source_events_temp, color = 'color', size= 12, line_color="black")

    #boundaries
    p_boundary_start = p_heat_map.line(x = 'start_date', y = 'hour', source =source_boundaries, line_dash = 'dashed', color = "firebrick", line_width = 4 )
    p_boundary_end = p_heat_map.line(x = 'end_date', y = 'hour', source =source_boundaries, line_dash = 'dashed', color = "firebrick", line_width = 4 )


    color_bar = ColorBar(color_mapper=mapper_heat_map, border_line_color=None,label_standoff=12, location=(0, 0))
    color_bar.formatter = NumeralTickFormatter(format='0.0')
    p_heat_map.add_layout(color_bar, 'right')

    heat_map_hover = HoverTool(renderers=[heat_map],
                        tooltips=OrderedDict([('Water Consumption (Litres)', '@rate'),
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

    p_outliers = figure(title="Daily water consumptions in Litres", x_axis_type="datetime", tools=TOOLS_heat_map, x_range = dates_list)
    p_circle = p_outliers.circle(x = 'date', y = 'delta_total', size='s', color= 'c', alpha='a', legend= "Consumption in L",
                                 source = source_data_aggregated_day_temp)

    p_ub = p_outliers.line(x='date', y='ub', legend='upper_bound (2 sigma)', line_dash = 'dashed', line_width = 4, color = '#984ea3',
                           source = source_rolling_temp)
    p_mean = p_outliers.line(x='date', y='y_mean', source = source_rolling_temp, line_dash = 'dashed', line_width = 3,
                             legend='moving_average', color = '#4daf4a')

    #Dynamic boundaries
    p_boundary_start = p_outliers.line(x = 'start_date', y = 'y', source =source_boundaries, line_dash = 'dashed', color = "firebrick", line_width = 4 )
    p_boundary_end = p_outliers.line(x = 'end_date', y = 'y', source =source_boundaries, line_dash = 'dashed', color = "firebrick", line_width = 4 )


    p_outliers.legend.location = "top_left"
    p_outliers.legend.orientation = "horizontal"
    p_outliers.legend.click_policy= "hide"
    p_outliers.ygrid.band_fill_color = "olive"
    p_outliers.ygrid.band_fill_alpha = 0.1
    p_outliers.xaxis.axis_label = None
    p_outliers.yaxis.axis_label = 'Litres'
    p_outliers.xaxis.major_label_orientation = 3.1416 / 3
    p_outliers.x_range = p_heat_map.x_range# Same axes as the heatMap

    p_outliers.xaxis.formatter = FuncTickFormatter(code=""" var labels = %s; return labels[tick];""" % dates_list)


    circle_hover = HoverTool(renderers=[p_circle],
                        tooltips=OrderedDict([('date', '@date'),
                                              ('Water Consumption (L)', '@delta_total'),
                                             ]))

    p_ub_hover = HoverTool(renderers=[p_ub],
                        tooltips=OrderedDict([('date', '@date'),
                                              ('UpperBound water consumption (L)', '@ub'),
                                             ]))

    p_mean_hover = HoverTool(renderers=[p_mean],
                        tooltips=OrderedDict([('date', '@date'),
                                              ('Mean water consumption (L)', '@y_mean'),
                                             ]))

    p_outliers.add_tools(circle_hover)
    p_outliers.add_tools(p_ub_hover)
    p_outliers.add_tools(p_mean_hover)

    return p_heat_map, p_outliers


def return_exploration_plot(df, average_usage_df, source_usage, source_events, length=1300, height=300):

    TOOLS_exploration = "save,reset, xwheel_zoom, xbox_select, pan"

    #layout settings of chart 1
    plot_events_usage = figure(x_axis_type="datetime",
                title="Average Elog water consumption and events in Eindhoven",
                toolbar_location="left",
                plot_width=length, plot_height=height,
                y_range=Range1d(start=0, end=max(df["Number of complains"]+5)),
                tools=TOOLS_exploration, active_drag="xbox_select"
                )

    plot_events_usage.toolbar.active_drag = None
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

    plot_events_usage.vbar(x="Date", top="value", source=source_events,
            width=1, color="green", line_width =2, legend='Number of events')

    plot_events_usage.circle('Date', 'value', size=1, source=source_usage, selection_color="firebrick",
              nonselection_fill_color="firebrick", y_range_name='water_usage')
    line_hover = HoverTool(renderers=[line_plot],
                             tooltips=OrderedDict([
                                 ("Usage", "@value{int}"),
                                 ("Date", "@Date{%F %T}")
                             ]),
                          formatters={"Date": "datetime"})
    plot_events_usage.add_tools(line_hover)


    plot_events_usage.legend.location = "top_left"
    plot_events_usage.legend.click_policy="hide"

    return plot_events_usage


def get_map_plot(source, source_elog, source_radius_circle):

    #define maps, options
    map_options = GMapOptions(lat=51.4416, lng=5.4697, map_type="terrain", zoom=12)
    plot = GMapPlot(x_range=Range1d(), y_range=Range1d(), map_options=map_options)

    # use your api key below
    plot.api_key = get_api_key()

    ########################################################################
    # Define glyphs
    ########################################################################

    # triangle glyphs on the map
    triangle_event = Triangle(x="lon", y="lat", size=12, fill_color="red", fill_alpha=0.5, line_color=None, name="events")
    glyph_triangle = plot.add_glyph(source, triangle_event, nonselection_glyph=triangle_event)

    # circle glyphs on the map
    circle_elog = Circle(x="lon_elog", y="lat_elog", size=12, fill_color="color",
    fill_alpha=0.8, line_color=None, name="elog_locations")
    glyph_circle = plot.add_glyph(source_elog, circle_elog, nonselection_glyph=circle_elog, )

    circle_radius = Circle(x="lon_radius", y="lat_radius", radius= "rad_radius", fill_alpha=0.3, line_color='black')
    glyph_circle_radius = plot.add_glyph(source_radius_circle, circle_radius)

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
                                 ("Usage", '@value_elog'),
                                 ("Classification", '@classes')
                             ]))
    plot.add_tools(circle_hover)

    # Add legend
    legend = Legend(items=[
        LegendItem(label="elog_locations"   , renderers=[glyph_circle]),
        LegendItem(label="events" , renderers=[glyph_triangle])
    ], orientation="vertical", click_policy="hide")
    plot.add_layout(legend, "center")

    return glyph_circle, plot

def get_events_bar_chart_plot(bar_chart_source, values):

    # bar chart events
    event_dic = {'Afwijkende geur en/of smaak':'#a6cee3', 'Afwijkende kleur': '#1f78b4', 'Afwijkende temperatuur': '#b2df8a',
                 'Afwijkende waterdruk':'#33a02c', 'Geen water':'#fb9a99', 'Geluid in de (drink)waterinstallatie':'#e31a1c',
                 'Lekkage binnenshuis':'#fdbf6f', 'Lekkage buitenshuis':'#ff7f00', 'Meteropstelling (geen lekkage)':'#cab2d6',
                 'Monteursinzet n.a.v. eerdere melding': '#6a3d9a'}

    palette = [event_dic[i] for i in bar_chart_source.data['Reason']]

    plot_bar_chart_events = figure(y_range=values, plot_height=500, plot_width=800, x_axis_label = 'Number of events',
    toolbar_location=None, title="Distribution of events")

    plot_bar_chart_events.hbar(y='Reason', right='Count', height=0.9, source=bar_chart_source, legend="Reason",
       line_color='white', fill_color=factor_cmap('Reason', palette=palette, factors=bar_chart_source.data['Reason']))

    plot_bar_chart_events.xaxis.major_label_orientation = 0.0

    return plot_bar_chart_events
