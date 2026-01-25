app.layout = html.Div([
    html.H2("Texas Solar Market Dashboard"),
    html.Div([
        dl.Map(center=[31.0, -97.0], zoom=6, children=[
            dl.TileLayer(),
            *polygons,
            dl.Marker(id="marker", position=[30.26, -97.74], draggable=False)
        ], style={'width': '100%', 'height': '400px'}, id="map")
    ]),
    dcc.Graph(id="chart", figure=build_figure(30.26, -97.74))
])

# Callback: update marker and chart
@app.callback(
    Output("chart", "figure"),
    Output("marker", "position"),
    Input("map", "click_lat_lng")
)
def update_chart(click_lat_lng):
    if click_lat_lng is None:
        lat, lon = 30.26, -97.74
    else:
        lat, lon = click_lat_lng
    return build_figure(lat, lon), [lat, lon]
