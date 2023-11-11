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
    no_update
)
from dash.dependencies import Input, Output, State
import random
import flask
import shapely
import math
from dash.exceptions import PreventUpdate

demo_mode = False
weight_time_score  = 1.0 # max 2600
weight_map_score   = 10.0 # max 180
weight_style_score = 2000.0 # max 1.0

# Load region GeoJSON
with open("cultural_regions_simplified.geojson", "tr", encoding='utf-8') as fi:
    regions = json.load(fi)

from app_html import *
if demo_mode:
    import app_demo

#print(style_img.keys())
#print(examples_img.keys())
#print(architects_by_style.keys())

style_ccc = [None for c in style_img.keys()]
sel_style = None
sel_map = None
sel_year = None
submit_n_clicks = 0
newrun_n_clicks = 0
correct_style = architects_by_style[rnd_style]
resultmodal_isopen = False
rnd_img = None
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
    Output("style-mask", "hidden", allow_duplicate=True),
    Output("map-mask", "hidden", allow_duplicate=True),
    Output("epoche-mask", "hidden", allow_duplicate=True),
    Output({'type': "style-selection-col",'index': ALL}, 'className'),
    Output("layer", "children", allow_duplicate=True),
    Output("epoche", "value"),
    Output("clientside-output", "children"),
    Output("SUBMIT_GUESS", "n_clicks"),
    Output("new_run_btn", "n_clicks"),  # used as event notifier
    Input("guess-data", "data"),
    State({"type": "style-selection","index": ALL}, "name"),
    State("SUBMIT_GUESS", "n_clicks"),
    State("new_run_btn", "n_clicks"),
    prevent_initial_call=True
)
def print_guess_data(data, names, sub_n_clicks, new_n_clicks):
    global lastdata, resultmodal_isopen, sel_style, sel_map, sel_year
    ldata = lastdata
    lastdata = data
    styles = ["" for n in names]
    layers = []
    if data and ldata and 'state' in data and 'state' in ldata:
        data['total_score'] = 0
        if data and 'obj' in data and correct_style:
            sel_style = data['style'] = marker_to_style[data['obj']]
            data['style_score'] = compute_style_score(sel_style)
            data['total_score'] += round(weight_style_score * data['style_score'])
            styles = ["" if sel_style == n else "hidden" for n in names]
        if data and 'lat' in data and 'lon' in data and correct_style:
            sel_map = [data['lon'], data['lat']]
            data['map_score'] = compute_map_score(sel_map[0], sel_map[1])
            data['total_score'] += round(weight_map_score * data['map_score'])
            layers.append(dl.Marker(position=sel_map, children=dl.Tooltip("({:.3f}, {:.3f})".format(*sel_map))))
        if data and 'year' in data and correct_style:
            sel_year = data['year']
            data['time_score'] = compute_time_score(sel_year)
            data['total_score'] += round(weight_time_score * data['time_score'])
        else:
            sel_year = None

        if data['state'] == "GO" and ldata['state'] != "GO" and not data['err']:
            resultmodal_isopen = True
            sub_n_clicks = (sub_n_clicks + 1) if sub_n_clicks else 1
        elif data['state'] == "STOP" and ldata['state'] != "STOP" and not data['err']:
            resultmodal_isopen = False
            new_n_clicks = (new_n_clicks + 1) if new_n_clicks else 1
            sub_n_clicks = no_update
        else:
            sub_n_clicks = no_update
            new_n_clicks = no_update
    return (
            sel_style is not None or mask,
            sel_map is not None or mask,
            sel_year is not None or mask,
            styles,
            layers,
            sel_year,
            str(data), 
            sub_n_clicks,
            new_n_clicks
    )


@app.callback(
    Output("epoche-mask", "hidden", allow_duplicate=True),
    Output("SUBMIT_GUESS", "disabled", allow_duplicate=True),
    Output("layer", "children", allow_duplicate=True),
    Input("map", "click_lat_lng"),
    prevent_initial_call=True,
)
def display_selected_map_position(click_lat_lng):
    global sel_map
    if click_lat_lng is None:
        return True, True, []
    sel_map = click_lat_lng
    return (
        True,
        submit_disabled(),
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
    global sel_year
    if value is None or value == 0:
        return True
    else:
        sel_year = value
    return submit_disabled()


@app.callback(
    Output("map-mask", "hidden", allow_duplicate=True),
    Output("SUBMIT_GUESS", "disabled", allow_duplicate=True),
    Output({"type": "style-selection", "index": ALL}, "color", allow_duplicate=True),
    Input({"type": "style-selection", "index": ALL}, "n_clicks"),
    State({"type": "style-selection", "index": ALL}, "name"),
    prevent_initial_call=True,
)
def select_style(n, names):
    global sel_style
    if callback_context.triggered_prop_ids:
        for v in callback_context.triggered_prop_ids.values():
            sel_style = v["index"]
            styles = ["primary" if sel_style == n else None for n in names]
            return (
                mask,
                submit_disabled(),
                styles,
            )
    else:
        return True, submit_disabled(), style_ccc

def submit_disabled():
    return sel_map is None or sel_style is None or sel_year is None or resultmodal_isopen

def get_style_body():
    style = correct_style
    astyle = style["style"]
    aarch = style["architects"]
    startY=f"{style['Start_Year']} CE" if style["Start_Year"]>0 else f"{-style['Start_Year']} BCE"
    endY=f"{style['End_Year']} CE" if style["End_Year"]>0 else f"{-style['End_Year']} BCE"
    return [
            dbc.Container([
                dbc.Row([
                    dbc.Col([
                        html.H3(rnd_style),
                        html.Label("Epoche"),
                        html.P(f'{startY} to {endY}'),
                        html.Label("Location"),
                        html.P(f'{style["style_area"]}'),
                        html.Label("Description"),
                    ]),
                    dbc.Col(html.Img(src=rnd_img, style={"width":"50%","margin-left":"auto","display":"block"})),
                ]),
                html.P(astyle["description"]),
                html.Label("Characteristics"),
                html.Ul([html.Li(c) for c in astyle["characteristics"]]),
                html.Label("Examples"),
                html.Ul([html.Li(c) for c in astyle["examples"]]),
                html.Label("Architects"),
                html.Ul([html.Li(c["name"]) for c in aarch]),
            ])
        ]

def new_run():
    global rnd_style, rnd_img, correct_style, sel_style, sel_year, sel_map, resultmodal_isopen
    rnd_style = random.choice(list(architects_by_style.keys()))
    rnd_img = random.choice(examples_img[rnd_style])
    correct_style = architects_by_style[rnd_style]
    sel_style, sel_year, sel_map = None, None, None
    resultmodal_isopen = False
    print("NEW Run", rnd_style)


@app.callback(
    Output("style-mask", "hidden", allow_duplicate=True),
    Output("map-mask", "hidden", allow_duplicate=True),
    Output("epoche-mask", "hidden", allow_duplicate=True),
    Output("SUBMIT_GUESS", "disabled", allow_duplicate=True),
    Output("resultmodal", "is_open", allow_duplicate=True),
    Output("example_img", "src"),
    Output("style_body", "children"),
    #Input("new_run", "disabled"),  # used as event notifier
    Input("new_run_btn", "n_clicks"),  # used as event notifier
    prevent_initial_call=True,
)
def select_random_style(n_clicks):
    global newrun_n_clicks, resultmodal_isopen
    new_n_clicks = newrun_n_clicks
    newrun_n_clicks = n_clicks
    if n_clicks and new_n_clicks and n_clicks > new_n_clicks:
        new_run()
        return (
            sel_style is not None or mask,
            sel_map is not None or mask,
            sel_year is not None or mask,
            submit_disabled(),
            resultmodal_isopen,
            rnd_img,
            get_style_body(),
        )
    else:
        raise PreventUpdate


@app.callback(
    Output("SUBMIT_GUESS", "disabled", allow_duplicate=True),
    Output("resultmodal", "is_open", allow_duplicate=True),
    Output("points", "children"),
    Input("SUBMIT_GUESS", "n_clicks"),
    #State("resultmodal", "is_open"),
    prevent_initial_call=True,
)
def evaluate_run(n_clicks):
    global submit_n_clicks, resultmodal_isopen
    sub_n_clicks = submit_n_clicks
    submit_n_clicks = n_clicks
    if n_clicks and sub_n_clicks and n_clicks > sub_n_clicks:
        print("SUBMIT ", lastdata.get('total_score',0))
        resultmodal_isopen = True
        return [submit_disabled(), resultmodal_isopen, f"You got {lastdata.get('total_score',0)} points"]
    else:
        raise PreventUpdate


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
    #if True:
        app.run_server(
            host="0.0.0.0",
            dev_tools_ui=True,
            dev_tools_hot_reload=True,
            debug=True,
            threaded=True,
        )
    else:
        app.run_server(host="0.0.0.0", debug=False, threaded=True)
