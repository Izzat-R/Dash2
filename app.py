#gauges and value boxes
import dash
from dash import html, dcc
from dash.dependencies import Input, Output
import pandas as pd
import plotly.express as px
from dash import dash_table
import plotly.graph_objects as go

# -------------------------------------------------------------
# Load dataset
# -------------------------------------------------------------
df = pd.read_csv("mtcars.csv")
df["cyl"] = df["cyl"].astype(str)
df["gear"] = df["gear"].astype(str)

cyl_list = sorted(df["cyl"].unique())
gear_list = sorted(df["gear"].unique())

# -------------------------------------------------------------
# Gauge helper
# -------------------------------------------------------------
def gauge(value, min_v, max_v, title, color):
    return go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        title={"text": title},
        gauge={
            "axis": {"range": [min_v, max_v]},
            "bar": {"color": color}
        }
    ))

# -------------------------------------------------------------
# DASHBOARD 1 — COLUMN LAYOUT
# -------------------------------------------------------------
app = dash.Dash(__name__)

app.layout = html.Div([

    html.H1("Dashboard 1 — GRAPHICS IN COLUMNS", style={"textAlign": "center"}),

    # ---------------------- TABS ----------------------
    dcc.Tabs(id="tabs", value="tab-graphics", children=[
        dcc.Tab(label="Graphics", value="tab-graphics"),
        dcc.Tab(label="Value Boxes & Gauges", value="tab-values"),
        dcc.Tab(label="Data Table", value="tab-table"),
    ]),

    html.Hr(),

    # ---------------------- FILTERS BELOW TABS ----------------------
    html.Div([

        html.Div([
            html.Label("Cylinder:"),
            dcc.Dropdown(
                id="cylFilter",
                options=[{"label": "All", "value": "All"}] +
                        [{"label": c, "value": c} for c in cyl_list],
                value=["All"], multi=True
            )
        ], style={"width": "30%", "display": "inline-block"}),

        html.Div([
            html.Label("Gear:"),
            dcc.Dropdown(
                id="gearFilter",
                options=[{"label": "All", "value": "All"}] +
                        [{"label": g, "value": g} for g in gear_list],
                value=["All"], multi=True
            )
        ], style={"width": "30%", "display": "inline-block"}),

        html.Div([
            html.Label("MPG Range:"),
            dcc.RangeSlider(
                id="mpgFilter",
                min=df["mpg"].min(),
                max=df["mpg"].max(),
                value=[df["mpg"].min(), df["mpg"].max()],
                step=0.5,
                marks={i: str(i) for i in range(10, 35, 5)},
            )
        ], style={"width": "35%", "display": "inline-block", "paddingLeft": "2%"})

    ], style={"padding": "20px"}),

    html.Hr(),

    # Dynamic tab content
    html.Div(id="tab-content"),

    # Hidden store for filtered dataframe
    dcc.Store(id="filteredData")

])

# -------------------------------------------------------------
# FILTER CALLBACK
# -------------------------------------------------------------
@app.callback(
    Output("filteredData", "data"),
    Input("cylFilter", "value"),
    Input("gearFilter", "value"),
    Input("mpgFilter", "value")
)
def filter_data(cyl, gear, mpg_range):
    low, high = mpg_range
    dff = df.copy()

    if "All" not in cyl:
        dff = dff[dff["cyl"].isin(cyl)]

    if "All" not in gear:
        dff = dff[dff["gear"].isin(gear)]

    dff = dff[(dff["mpg"] >= low) & (dff["mpg"] <= high)]
    return dff.to_dict("records")

# -------------------------------------------------------------
# RENDER TAB CONTENT
# -------------------------------------------------------------
@app.callback(
    Output("tab-content", "children"),
    Input("tabs", "value"),
    Input("filteredData", "data")
)
def render_tabs(tab, data):
    dff = pd.DataFrame(data)

    # ---------------------- GRAPHICS IN COLUMNS ----------------------
    if tab == "tab-graphics":
        return html.Div([

            html.Div([
                dcc.Graph(figure=px.scatter(
                    dff, x="mpg", y="hp", color="cyl",
                    title="Scatter Plot: MPG vs HP"))
            ], style={"width": "32%", "display": "inline-block"}),

            html.Div([
                dcc.Graph(figure=px.histogram(
                    dff, x="mpg", title="Histogram: MPG"))
            ], style={"width": "32%", "display": "inline-block", "paddingLeft": "2%"}),

            html.Div([
                dcc.Graph(figure=px.box(
                    dff, x="cyl", y="mpg", title="Boxplot: MPG by Cylinder"))
            ], style={"width": "32%", "display": "inline-block", "paddingLeft": "2%"})

        ])

    # ---------------------- VALUE BOXES & GAUGES (COLUMNS) ----------------------
    if tab == "tab-values":
        return html.Div([

            html.Div([
                html.Div([
                    html.H3("Mean MPG"),
                    html.H2(round(dff["mpg"].mean(), 2))
                ], style={"background": "#E8F4FF", "padding": "15px"}),

                html.Div([
                    html.H3("Max HP"),
                    html.H2(dff["hp"].max())
                ], style={"background": "#FFECEC", "padding": "15px"}),

                dcc.Graph(figure=gauge(
                    dff["mpg"].mean(),
                    df["mpg"].min(),
                    df["mpg"].max(),
                    "MPG Gauge",
                    "blue"
                ))
            ], style={"width": "32%", "display": "inline-block"}),

            html.Div([
                dcc.Graph(figure=gauge(
                    dff["hp"].max(),
                    df["hp"].min(),
                    df["hp"].max(),
                    "HP Gauge",
                    "red"
                ))
            ], style={"width": "32%", "display": "inline-block", "paddingLeft": "3%"})

        ])

    # ---------------------- DATA TABLE ----------------------
    if tab == "tab-table":
        return dash_table.DataTable(
            columns=[{"name": c, "id": c} for c in df.columns],
            data=dff.to_dict("records"),
            page_size=12,
            style_table={"overflowX": "auto"}
        )


# -------------------------------------------------------------
# RUN DASHBOARD 1
# -------------------------------------------------------------
if __name__ == "__main__":
    app.run_server(debug=False)
