import os

import dash_bootstrap_components as dbc
import json
from dash import (
    html,
    Dash,
    ALL,
    callback_context,
    clientside_callback,
    ClientsideFunction,
)
from dash.dependencies import Input, Output, State
import random
import flask
import shapely
import math

mask = False
demo_mode = False
weight_time_score  = 1.0 # max 2600
weight_map_score   = 10.0 # max 180
weight_style_score = 2000.0 # max 1.0
marker_to_style={}

# Load architect styles
with open("architect_styles_sub.json", "tr", encoding='utf-8') as fi:
    architects_by_style = json.load(fi)

# Load region GeoJSON
with open("cultural_regions_simplified.geojson", "tr", encoding='utf-8') as fi:
    regions = json.load(fi)

for k, v in architects_by_style.items():
    marker_to_style[v["marker"]] = k
    if "architects" not in v:
        print("MISSING architects", k)
    for a in v["architects"]:
        if "name" not in a:
            print("MISSING architect name", k, a)
    if "terms" not in v:
        print("MISSING terms", k)
    if "style" not in v:
        print("MISSING style", k)
    if "time_range" not in v["style"]:
        print("MISSING time_range", k)
    if "period" not in v["style"]:
        print("MISSING period", k)
    if "description" not in v["style"]:
        print("MISSING description", k)
    if "characteristics" not in v["style"]:
        print("MISSING characteristics", k)
    if "examples" not in v["style"]:
        print("MISSING examples", k)
    if "continent" not in v["style"]:
        print("MISSING continent", k)
    if "country" not in v["style"]:
        print("MISSING country", k)
    # print(k)

from app_html import *
if demo_mode:
    import app_demo

# print(examples_img.keys())

style_ccc = [None for c in style_img.keys()]
sel_style = None
sel_location = None
sel_epoche = None
submit_disabled = True
last_submit_n_clicks = 0
resultmodal_isopen = False
rnd_style = random.choice(list(architects_by_style.keys()))
correct_style = architects_by_style[rnd_style]
lastdata = {'state':"ERR"}

# Build App
server = flask.Flask(__name__)
app = Dash(
    server=server, external_stylesheets=[dbc.themes.DARKLY, dbc.icons.BOOTSTRAP]
)  # , dbc.icons.FONT_AWESOME
app.title = "ArchiGuesser"

# layout from app_html
app.layout = init_webpage()

# marker callback
clientside_callback(
    ClientsideFunction(namespace="clientside", function_name="test_client_side"),
    Output("guess-data", "data"),
    Input("camera-update", "n_intervals"),
    # State("guess-data", "data"),
)

@app.callback(
    Output("clientside-output", "children"),
    Output("SUBMIT_GUESS", "n_clicks"),
    Input("guess-data", "data"),
    State("SUBMIT_GUESS", "n_clicks"),
)
def print_guess_data(data, n_clicks):
    global lastdata, last_submit_n_clicks, submit_disabled, resultmodal_isopen
    ldata = lastdata
    lastdata = data
    if not data or not ldata or 'state' not in data or 'state' not in ldata:
        return str(data), n_clicks

    data['total_score'] = 0
    if 'obj' in data:
        sel_style = data['style'] = marker_to_style[data['obj']]
        data['style_score'] = compute_style_score(sel_style)
        data['total_score'] += round(weight_style_score * data['style_score'])
    if not data or 'lat' not in data or 'lon' not in data or not correct_style:
        sel_location = [data['lat'], data['lon']]
        data['map_score'] = compute_map_score(sel_location[0], sel_location[1])
        data['total_score'] += round(weight_map_score * data['map_score'])
    if not data or 'year' not in data or not correct_style:
        sel_epoche = data['year']
        data['time_score'] = compute_time_score(sel_epoche)
        data['total_score'] += round(weight_time_score * data['time_score'])

    if data['state'] == "GO" and ldata['state'] != "GO" and not data['err']:
        resultmodal_isopen = True
        print("1", data, ldata, n_clicks)
        return str(data), (n_clicks + 1) if n_clicks else 1
    elif data['state'] == "STOP" and ldata['state'] != "STOP" and not data['err']:
        resultmodal_isopen = False
        print("1", data, ldata, n_clicks)
    return str(data), n_clicks


def tostr(obj):
    if isinstance(obj, str):
        return obj
    if isinstance(obj, list):
        return ", ".join(obj)
    else:
        return str(obj)


def compute_map_score(lat, lon):
    if not correct_style or not lat or not lon:
        return 0
    guess_coord = shapely.Point(lon, lat)
    #Find correct polygon, convert to shapely geometry
    region_poly = None
    for reg in regions["features"]:
        if reg["properties"]["Region"] == correct_style["style_area"]:
            region_poly = shapely.geometry.shape(reg["geometry"])
            break
    if guess_coord and region_poly:
        #Map score: angular error
        return shapely.distance(guess_coord, region_poly)
    else:
        #Upon error, return maximum distance
        return 180


def compute_time_score(year):
    if not correct_style or not year:
        return 0
    if year < correct_style["Start_Year"]:
        return correct_style["Start_Year"] - year
    if year > correct_style["End_Year"]:
        return year - correct_style["End_Year"]
    return 0


def compute_style_score(style):
    if not correct_style or not style:
        return 0
    return correct_style["style_similarity"][style]["weighted"]


@app.callback(
    Output("epoche-mask", "hidden", allow_duplicate=True),
    Output("SUBMIT_GUESS", "disabled", allow_duplicate=True),
    Output("layer", "children"),
    Input("map", "click_lat_lng"),
    prevent_initial_call=True,
)
def display_selected_map_position(click_lat_lng):
    global sel_location
    if click_lat_lng is None:
        return True, True, []
    sel_location = click_lat_lng
    print(sel_location, sel_style, sel_epoche)
    return (
        True,
        sel_location is None or sel_style is None or sel_epoche is None,
        [
            dl.Marker(
                position=click_lat_lng,
                children=dl.Tooltip("({:.3f}, {:.3f})".format(*click_lat_lng)),
            )
        ],
    )


@app.callback(
    Output("SUBMIT_GUESS", "disabled", allow_duplicate=True),
    Input("epoche", "value"),
    prevent_initial_call=True,
)
def display_selected_epoche(value):
    global sel_epoche, submit_disabled
    if value is None:
        return True
    sel_epoche = value
    submit_disabled=sel_location is None or sel_style is None or sel_epoche is None
    return submit_disabled


@app.callback(
    Output("map-mask", "hidden", allow_duplicate=True),
    Output("SUBMIT_GUESS", "disabled", allow_duplicate=True),
    Output({"type": "style-selection", "index": ALL}, "color", allow_duplicate=True),
    Input({"type": "style-selection", "index": ALL}, "n_clicks"),
    State({"type": "style-selection", "index": ALL}, "name"),
    prevent_initial_call=True,
)
def select_style(n, names):
    global sel_style, submit_disabled
    if callback_context.triggered_prop_ids:
        for v in callback_context.triggered_prop_ids.values():
            sel_style = v["index"]
            styles = ["primary" if sel_style == n else None for n in names]
            submit_disabled=sel_location is None or sel_style is None or sel_epoche is None
            return (
                False,
                submit_disabled,
                styles,
            )
    else:
        return True, submit_disabled, style_ccc


@app.callback(
    Output("style-mask", "hidden", allow_duplicate=True),
    Output("map-mask", "hidden", allow_duplicate=True),
    Output("epoche-mask", "hidden", allow_duplicate=True),
    Output("SUBMIT_GUESS", "disabled", allow_duplicate=True),
    Output("example_img", "src"),
    Output("style_body", "children"),
    #Input("new_run", "disabled"),  # used as event notifier
    Input("new_run_btn", "n_clicks"),  # used as event notifier
    prevent_initial_call=True,
)
def select_random_style(new_run):
    global rnd_style, sel_style, sel_epoche, sel_location, correct_style, resultmodal_isopen
    print("2", new_run)
    rnd_style = random.choice(list(architects_by_style.keys()))
    rnd_img = random.choice(examples_img[rnd_style])
    correct_style = architects_by_style[rnd_style]
    astyle = correct_style["style"]
    aarch = correct_style["architects"]
    print(rnd_style, astyle, aarch)
    sel_style, sel_epoche, sel_location = None, None, None
    resultmodal_isopen = False
    return (
        True,
        mask,
        mask,
        True,
        rnd_img,
        [
            html.H3(rnd_style),
            html.Label("Epoche"),
            html.P(f'{astyle["Start_Year"]}&mdash;{astyle["End_Year"]}'),
            html.Label("Location"),
            html.P(f'{astyle["style_area"]}'),
            html.Label("Description"),
            html.P(astyle["description"]),
            html.Label("Characteristics"),
            html.Ul([html.Li(c) for c in astyle["characteristics"]]),
            html.Label("Examples"),
            html.Ul([html.Li(c) for c in astyle["examples"]]),
            html.Label("Architects"),
            html.Ul([html.Li(c["name"]) for c in aarch]),
        ],
    )


@app.callback(
    Output("SUBMIT_GUESS", "disabled", allow_duplicate=True),
    Output("resultmodal", "is_open", allow_duplicate=True),
    Output("points", "children"),
    Input("SUBMIT_GUESS", "n_clicks"),
    #State("resultmodal", "is_open"),
    prevent_initial_call=True,
)
def evaluate_run(n_clicks):
    global last_submit_n_clicks, submit_disabled, resultmodal_isopen
    if not n_clicks or n_clicks <= last_submit_n_clicks:
        resultmodal_isopen = True
        submit_disabled = True
        last_submit_n_clicks = n_clicks
        print("3", n_clicks, last_submit_n_clicks, resultmodal_isopen)
    return [submit_disabled, resultmodal_isopen, f"You got {lastdata.get('total_score',0)} points"]


@app.callback(  # Output("setup_modal", "is_open"),
    Output("video_body", "style"), Input("SETUP", "n_clicks"), prevent_initial_call=True
)
def display_setup_modall(n):
    return {"visibility": "hidden"} if n % 2 == 0 else {"visibility": "visible"}


@app.server.route("/marker")
def get_marker():
    return flask.send_from_directory("assets", "index.html")


if __name__ == "__main__":
    # run application
    if "DASH_DEBUG_MODE" in os.environ:
        app.run_server(
            host="0.0.0.0",
            dev_tools_ui=True,
            dev_tools_hot_reload=True,
            debug=True,
            threaded=True,
        )
    else:
        app.run_server(host="0.0.0.0", debug=False, threaded=True)
