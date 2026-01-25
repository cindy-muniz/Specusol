from dash import Dash, html, dcc, Input, Output
import dash_leaflet as dl
import numpy as np
from datetime import datetime
import plotly.graph_objects as go

# ------------------------------
# ERCOT ZONES (SIMPLIFIED GEOJSON)
# ------------------------------
ercot_zones = {
    "type": "FeatureCollection",
    "features": [
        {"type":"Feature","properties":{"zone":"North"},
         "geometry":{"type":"Polygon","coordinates":[[[-103,36],[-94,36],[-94,33],[-103,33],[-103,36]]]}},

        {"type":"Feature","properties":{"zone":"South"},
         "geometry":{"type":"Polygon","coordinates":[[[-102,29],[-96,29],[-96,26],[-102,26],[-102,29]]]}},

        {"type":"Feature","properties":{"zone":"West"},
         "geometry":{"type":"Polygon","coordinates":[[[-106,33],[-102,33],[-102,29],[-106,29],[-106,33]]]}},

        {"type":"Feature","properties":{"zone":"Houston"},
         "geometry":{"type":"Polygon","coordinates":[[[-96,31],[-94,31],[-94,29],[-96,29],[-96,31]]]}},

        {"type":"Feature","properties":{"zone":"Coastal"},
         "geometry":{"type":"Polygon","coordinates":[[[-98,29],[-94,29],[-94,26],[-98,26],[-98,29]]]}}

    ]
}

# ------------------------------
# SOLAR SUPPLY MODEL
# ------------------------------
def get_solar_supply(lat, lon):
    timestamps = pd.date_range(datetime.now(), periods=168, freq="h")

    ghi = np.maximum(0, 1000 * np.sin((timestamps.hour - 6) / 12 * np.pi))
    cloud = 1 - np.random.uniform(0, 0.25, len(timestamps))

    res_kw = ghi * cloud * (10000 * 0.18 / 1000)
    comm_kw = ghi * cloud * (50000 * 0.18 * 0.75 / 1000)

    return pd.DataFrame({
        "timestamp": timestamps,
        "res_supply": res_kw,
        "comm_supply": comm_kw
    })

# ------------------------------
# FIGURE BUILDER (same as before)
# ------------------------------
def build_figure(lat, lon):
    df = get_solar_supply(lat, lon)

    res_demand = df.res_supply * np.random.uniform(0.7, 1.0, len(df))
    comm_demand = df.comm_supply * np.random.uniform(0.7, 1.0, len(df))

    hour = df.timestamp.dt.hour
    tou_price = np.select(
        [hour < 6, hour < 14, hour < 20, hour < 22],
        [0.07, 0.11, 0.22, 0.13],
        default=0.07
    )

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=df.timestamp, y=df.res_supply,
        name="Residential Supply",
        line=dict(color="orange")
    ))

    fig.add_trace(go.Scatter(
        x=df.timestamp, y=res_demand,
        name="Residential Demand",
        line=dict(color="red", dash="dash")
    ))

    fig.add_trace(go.Scatter(
        x=df.timestamp, y=df.comm_supply,
        name="Commercial Supply",
        line=dict(color="blue")
    ))

    fig.add_trace(go.Scatter(
        x=df.timestamp, y=comm_demand,
        name="Commercial Demand",
        line=dict(color="navy", dash="dash")
    ))

    fig.add_trace(go.Scatter(
        x=df.timestamp, y=tou_price,
        name="TOU Price ($/kWh)",
        yaxis="y2",
        line=dict(color="black")
    ))

    fig.update_layout(
        title=f"Texas Solar Supply, Demand & TOU Pricing<br>LAT={lat:.3f}, LON={lon:.3f}",
        xaxis_title="Time",
        yaxis=dict(title="Power (kW)"),
        yaxis2=dict(
            title="Price ($/kWh)",
            overlaying="y",
            side="right"
        ),
        template="plotly_white",
        legend=dict(orientation="h")
    )

    return fig

# ------------------------------
# DASH APP
# ------------------------------
app = Dash(__name__)

app.layout = html.Div([
    html.H2("Specusol - Texas Solar Dashboard"),

    html.Div([
        "Disclaimer: This is a mock dashboard to visualize Texas solar energy supply and demand data. It does not provide real-time data and is for educational purposes only."
    ], style={"fontStyle": "italic", "marginBottom": "20px"}),

    html.H3("ERCOT Zones (Interactive Map)"),
    dl.Map(
        id="map",
        center=[31, -100],
        zoom=6,
        style={"height": "420px"},
        children=[
            dl.TileLayer(),
            dl.GeoJSON(
                data=ercot_zones,
                style={
                    "fillColor": "#1f77b4",
                    "color": "black",
                    "weight": 1,
                    "fillOpacity": 0.25
                }
            ),
            dl.Marker(
                id="marker",
                position=[30.26, -97.74]
            )
        ]
    ),

    html.Div([
        "Latitude:",
        dcc.Input(id="lat", value=30.26, type="number", step=0.001),
        "Longitude:",
        dcc.Input(id="lon", value=-97.74, type="number", step=0.001)
    ], style={"marginTop": "10px"}),

    dcc.Graph(
        id="chart",
        figure=build_figure(30.26, -97.74)
    ),

    # Solar Stock ETF Graph
    html.H3("Solar Stock ETF"),
    dcc.Graph(id="solar-stock-chart")
])

# ------------------------------
# CALLBACKS
# ------------------------------
@app.callback(
    Output("lat", "value"),
    Output("lon", "value"),
    Output("marker", "position"),
    Input("map", "clickData")
)
def update_coords(clickData):
    if clickData is None:
        lat, lon = 30.26, -97.74
        return lat, lon, [lat, lon]

    lat = clickData["latlng"]["lat"]
    lon = clickData["latlng"]["lng"]
    return lat, lon, [lat, lon]

@app.callback(
    Output("chart", "figure"),
    Input("lat", "value"),
    Input("lon", "value")
)
def update_chart(lat, lon):
    return build_figure(lat, lon)

@app.callback(
    Output("solar-stock-chart", "figure"),
    Input("lat", "value"),  # Keeping this just in case
    Input("lon", "value")
)
def update_solar_stock_chart(lat, lon):
    import yfinance as yf

    # Solar ETF Stock symbol (example: TAN, the Invesco Solar ETF)
    symbol = "TAN"

    # Download the data
    stock_data = yf.download(symbol, period="1mo", interval="1d")

    # Create the plot
    fig = go.Figure()

    fig.add_trace(go.Candlestick(
        x=stock_data.index,
        open=stock_data['Open'],
        high=stock_data['High'],
        low=stock_data['Low'],
        close=stock_data['Close'],
        name="Solar ETF"
    ))

    fig.update_layout(
        title="Solar Stock ETF Performance (TAN)",
        xaxis_title="Date",
        yaxis_title="Price ($)",
        template="plotly_white"
    )

    return fig

# ------------------------------
# RUN (RENDER)
# ------------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8050)
