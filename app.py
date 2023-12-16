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
import plotly.express as px
import pandas as pd
from collections import defaultdict

max_time_score  = 2025 # max 2600
weight_time_score  = 1.0 # max 2025
max_map_score = 1800
weight_map_score   = 10.0 # max 180
max_style_score = 2000
weight_style_score = 2000.0 # max 1.0

# Load region GeoJSON
with open("datasets/cultural_regions_simplified.geojson", "tr", encoding='utf-8') as fi:
    regions = json.load(fi)

from app_html import *

#print(style_img.keys())
#print(examples_img.keys())
#print(architects_by_style.keys())

style_ccc = [None for c in style_img.keys()]
sel_style = None
sel_map = None
sel_year = None
submit_n_clicks = -1
newrun_n_clicks = -1
correct_style = architects_by_style[rnd_style]
resultmodal_isopen = False
rnd_img = None
lastdata = {'state':"ERR"}
scoreboard = []
scoreboard_hist = defaultdict(int)
scoreboard_hist_pd = []
dot_state = "col_gray"

# Build App
server = flask.Flask(__name__)
app = Dash(server=server, external_stylesheets=[dbc.themes.DARKLY, dbc.icons.BOOTSTRAP])
app.title = "ArchiGuesser"

# layout from app_html
app.layout = init_webpage()

# marker callback
clientside_callback(
    ClientsideFunction(namespace="clientside", function_name="test_client_side"),
    Output("guess-data", "data"),
    Input("camera-update", "n_intervals")
)


def tostr(obj):
    if isinstance(obj, str):
        return obj
    if isinstance(obj, list):
        return ", ".join(obj)
    else:
        return str(obj)


def compute_map_score(lat_lon):
    if not correct_style or not lat_lon:
        return 0
    guess_coord = shapely.Point(lat_lon[0], lat_lon[1])
    #Find correct polygon, convert to shapely geometry
    region_poly = None
    closest_region = None
    closest_region_dist = 999
    for reg in regions["features"]:
        if "shape" not in reg:
            reg['shape'] = shapely.geometry.shape(reg["geometry"])
        if reg["properties"]["Region"] == correct_style["style_area"]:
            region_poly = reg['shape']
        dist = shapely.distance(guess_coord, reg['shape'])
        if dist < closest_region_dist:
            closest_region = reg["properties"]["Region"]
            closest_region_dist = dist
            #print(closest_region, closest_region_dist)
    if correct_style["style_area"]=="Intercultural":
        return 0, closest_region, closest_region_dist
    if guess_coord and region_poly:
        #Map score: angular error
        return shapely.distance(guess_coord, region_poly), closest_region, closest_region_dist
    else:
        #Upon error, return maximum distance
        return 180, closest_region, closest_region_dist


def compute_time_score(year):
    if not correct_style or not year:
        return max_time_score
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
    Output("state_dot", "className"),
    Output("state_style", "className"),
    Output("state_map", "className"),
    Output("state_time", "className"),
    Output("state_on", "className"),
    Input("guess-data", "data"),
    State({"type": "style-selection","index": ALL}, "name"),
    State("SUBMIT_GUESS", "n_clicks"),
    State("new_run_btn", "n_clicks"),
    prevent_initial_call=True
)
def print_guess_data(data, names, sub_n_clicks, new_n_clicks):
    global lastdata, resultmodal_isopen, sel_style, sel_map, sel_year, dot_state, web_mode
    if web_mode:
        return no_update
    styles = ["" for _ in names]
    layers = []
    print("Got Data")
    map_state = "col_gray"
    time_state = "col_gray"
    style_state = "col_gray"
    run_state = "col_gray"
    dot_state = "col_green" if dot_state == "col_gray" else "col_gray"
    sel_year = no_update
    if data and 'state' in data:
        data['total_score'] = 0
        if data and 'obj' in data and correct_style:
            if data['obj'] in marker_to_style:
                sel_style = data['style'] = marker_to_style.get(data['obj'])
                if sel_style:
                    data['style_score'] = compute_style_score(sel_style)
                    data['total_score'] += max_style_score-round(weight_style_score * data['style_score'])
                    styles = ["" if sel_style == n else "hidden" for n in names]
                    style_state = "col_green"
            else:
                print(f"Error marker id {data['obj']} not found")
                style_state = "col_yellow"
        if data and 'lat' in data and 'lon' in data and correct_style:
            sel_map = [data['lat'],data['lon']]
            data['map_score'], _, _ = compute_map_score(sel_map)
            data['total_score'] += max_map_score-round(weight_map_score * data['map_score'])
            layers.append(dl.Marker(position=(sel_map[1], sel_map[0]), children=dl.Tooltip("({:.3f}, {:.3f})".format(*sel_map))))
            map_state = "col_green"
        if data and 'year' in data and correct_style:
            sel_year = data['year']
            data['time_score'] = compute_time_score(sel_year)
            data['total_score'] += max_time_score-round(weight_time_score * data['time_score'])
            time_state = "col_green"
        else:
            sel_year = None
            time_state = "col_yellow"

        run_state = "col_green" if data['state'] == "GO" else "col_yellow" if data['state'] == "STOP" else "col_red"
        if not data['err']:
            ldata = lastdata
            lastdata = data
            if data['state'] == "GO" and ldata['state'] != "GO":
                resultmodal_isopen = True
                sub_n_clicks = (sub_n_clicks + 1) if sub_n_clicks else 1
                new_n_clicks = no_update
                print("Step 1: Detect Init Submit")
            elif data['state'] == "STOP" and ldata['state'] != "STOP":
                resultmodal_isopen = False
                new_n_clicks = (new_n_clicks + 1) if new_n_clicks else 1
                sub_n_clicks = no_update
                print("Step 3: Detect Init New Run")
            else:
                sub_n_clicks = no_update
                new_n_clicks = no_update
        else:
            sub_n_clicks = no_update
            new_n_clicks = no_update
    else:
        sub_n_clicks = no_update
        new_n_clicks = no_update
    if data and "err" in data:
        if "MapCorner" in data['err']:
            map_state = "col_red"
        if "TimeCorner" in data['err'] or "TimeMarker" in data['err']:
            time_state = "col_red"
        if "place" in data['err']:
            style_state = "col_red"
    return (
        web_mode or sel_style is not None,
        sel_map is not None,
        sel_year is not None,
        styles,
        layers,
        sel_year,
        str(data), 
        sub_n_clicks,
        new_n_clicks,
        dot_state,
        style_state,
        map_state,
        time_state,
        run_state,
    )


@app.callback(
    Output("epoche-mask", "hidden", allow_duplicate=True),
    Output("SUBMIT_GUESS", "disabled", allow_duplicate=True),
    Output("layer", "children", allow_duplicate=True),
    #Input("map", "click_lat_lng"),
    Input("map", "clickData"),
    prevent_initial_call=True,
)
def select_map_update(click_data):
    global sel_map
    print("Map Update")
    #print(click_data)
    if click_data is None:
        sel_map = None
        marker = None
    else:
        sel_map = [click_data['latlng']['lng'], click_data['latlng']['lat']]
        marker=[dl.Marker(
                position=(sel_map[1], sel_map[0]),
                children=dl.Tooltip("({:.3f}, {:.3f})".format(*sel_map)),
            )]
    return (
        sel_map is not None,
        submit_disabled(),
        marker
    )


@app.callback(
    Output("SUBMIT_GUESS", "disabled", allow_duplicate=True),
    Input("epoche", "value"),
    prevent_initial_call=True,
)
def select_year_update(value):
    global sel_year
    print("Year Update")
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
def select_style_update(n, names):
    global sel_style
    print("Style Update")
    if callback_context.triggered_prop_ids:
        for v in callback_context.triggered_prop_ids.values():
            sel_style = v["index"]
            styles = ["primary" if sel_style == n else None for n in names]
            #styles = ["" if sel_style == n else "hidden" for n in names]
            #print(sel_style,sel_style is None)
            return (
                sel_style is not None,
                submit_disabled(),
                styles,
            )
    else:
        sel_style = None
        return (
            sel_style is not None,
            submit_disabled(),
            style_ccc
        )


def submit_disabled():
    #return sel_map is None or sel_style is None or sel_year is None or resultmodal_isopen
    return False


def new_run():
    global rnd_style, rnd_img, correct_style, sel_style, sel_year, sel_map, resultmodal_isopen
    rnd_style = random.choice(list(architects_by_style.keys()))
    rnd_img = random.choice(examples_img[rnd_style])
    correct_style = architects_by_style[rnd_style]
    sel_style, sel_year, sel_map = None, None, None
    resultmodal_isopen = False
    print("Step 5: NEW RUN", rnd_style, resultmodal_isopen)


@app.callback(
    Output("style-mask", "hidden", allow_duplicate=True),
    Output("map-mask", "hidden", allow_duplicate=True),
    Output("epoche-mask", "hidden", allow_duplicate=True),
    Output("SUBMIT_GUESS", "disabled", allow_duplicate=True),
    Output("resultmodal", "is_open", allow_duplicate=True),
    Output("example_img", "src"),
    Output("example_poem", "children"),
    #Input("new_run", "disabled"),  # used as event notifier
    Input("new_run_btn", "n_clicks"),  # used as event notifier
    prevent_initial_call=True,
)
def press_new_run(n_clicks):
    global newrun_n_clicks, resultmodal_isopen
    print("Step 4: NEW RUN")
    new_n_clicks = newrun_n_clicks
    newrun_n_clicks = n_clicks
    if n_clicks and new_n_clicks and n_clicks > new_n_clicks:
        new_run()
        return (
            web_mode or sel_style is not None,
            sel_map is not None,
            sel_year is not None,
            submit_disabled(),
            resultmodal_isopen,
            rnd_img,
            select_audio(rnd_style)
        )
    else:
        raise PreventUpdate


def update_scoreboard_hist(cat, value):
    global scoreboard_hist
    scoreboard_hist[cat+"_last"]=value
    scoreboard_hist[cat+"_sum"]+=value
    if value < scoreboard_hist[cat+"_min"]:
        scoreboard_hist[cat+"_min"]=value
    if value > scoreboard_hist[cat+"_max"]:
        scoreboard_hist[cat+"_max"]=value


def get_scoreboard_pd():
    global scoreboard_hist, scoreboard
    run = len(scoreboard)
    scoreboard_pd = []

    scoreboard_pd.append({ "score":"total", "cat":"max", "value":scoreboard_hist["total_max"]})
    scoreboard_pd.append({ "score":"style", "cat":"max", "value":scoreboard_hist["style_max"]})
    scoreboard_pd.append({ "score":"map", "cat":"max", "value":scoreboard_hist["map_max"]})
    scoreboard_pd.append({ "score":"year", "cat":"max", "value":scoreboard_hist["year_max"]})

    scoreboard_pd.append({ "score":"total", "cat":"mean", "value":scoreboard_hist["total_sum"]/run})
    scoreboard_pd.append({ "score":"style", "cat":"mean", "value":scoreboard_hist["style_sum"]/run})
    scoreboard_pd.append({ "score":"map", "cat":"mean", "value":scoreboard_hist["map_sum"]/run})
    scoreboard_pd.append({ "score":"year", "cat":"mean", "value":scoreboard_hist["year_sum"]/run})
    
    scoreboard_pd.append({ "score":"total", "cat":"min", "value":scoreboard_hist["total_min"]})
    scoreboard_pd.append({ "score":"style", "cat":"min", "value":scoreboard_hist["style_min"]})
    scoreboard_pd.append({ "score":"map", "cat":"min", "value":scoreboard_hist["map_min"]})
    scoreboard_pd.append({ "score":"year", "cat":"min", "value":scoreboard_hist["year_min"]})

    scoreboard_pd.append({ "score":"total", "cat":"current", "value":scoreboard_hist["total_last"]})
    scoreboard_pd.append({ "score":"style", "cat":"current", "value":scoreboard_hist["style_last"]})
    scoreboard_pd.append({ "score":"map", "cat":"current", "value":scoreboard_hist["map_last"]})
    scoreboard_pd.append({ "score":"year", "cat":"current", "value":scoreboard_hist["year_last"]})

    return pd.DataFrame(scoreboard_pd)


@app.callback(
    Output("SUBMIT_GUESS", "disabled", allow_duplicate=True),
    Output("resultmodal", "is_open", allow_duplicate=True),
    Output("points", "children"),
    Output("res_style", "children"),
    Output("res_year", "children"),
    Output("res_loc", "children"),
    Output("res_plot", "figure"),
    Output("res_desc", "children"),
    Output("res_char", "children"),
    Output("res_examp", "children"),
    Output("res_arch", "children"),
    Output("guess_style", "children"),
    Output("guess_year", "children"),
    Output("guess_loc", "children"),
    Input("SUBMIT_GUESS", "n_clicks"),
    #State("resultmodal", "is_open"),
    prevent_initial_call=True,
)
def press_submit(n_clicks):
    global submit_n_clicks, resultmodal_isopen, scoreboard, scoreboard_hist, scoreboard_hist_pd
    sub_n_clicks = submit_n_clicks
    submit_n_clicks = n_clicks
    print("SUBMIT", sub_n_clicks, n_clicks)
    if n_clicks and sub_n_clicks and n_clicks > sub_n_clicks:
        style = correct_style
        astyle = style["style"]
        aarch = style["architects"]
        startY = f"{style['Start_Year']} CE" if style["Start_Year"]>0 else f"{-style['Start_Year']} BCE"
        endY = f"{style['End_Year']} CE" if style["End_Year"]>0 else f"{-style['End_Year']} BCE"
        # compute scores
        style_score = round(weight_style_score * compute_style_score(sel_style)) #max_style_score-
        update_scoreboard_hist("style", style_score*3)
        map_score0, closest_reg, closest_reg_dist=compute_map_score(sel_map)
        map_score = max_map_score - round(weight_map_score * map_score0)
        print(map_score, map_score0, closest_reg, closest_reg_dist)
        update_scoreboard_hist("map", map_score*3)
        time_score = max_time_score-round(weight_time_score * compute_time_score(sel_year))
        update_scoreboard_hist("year", time_score*3)
        total_score = style_score + map_score + time_score
        update_scoreboard_hist("total", total_score)
        for h in scoreboard_hist_pd: 
            h["col"]='old'
        run=len(scoreboard_hist_pd)//4
        scoreboard_hist_pd.extend([
            {"score": "Total", "value": total_score, "run":run, "col":'new'},
            {"score": "Style", "value": style_score, "run":run, "col":'new'},
            {"score": "Time", "value": time_score, "run":run, "col":'new'},
            {"score": "Map", "value": map_score, "run":run, "col":'new'}])
        resultmodal_isopen = True
        print("Step 2: SUBMIT Score: ", total_score, resultmodal_isopen)
        # compute rank
        scoreboard.append(total_score)
        scoreboard.sort(reverse=True)
        rank = scoreboard.index(total_score) + 1
        # compute plot
        fig = px.line_polar(pd.DataFrame(scoreboard_hist_pd), r='value', theta='score', color="col", line_group="run", line_close=True, template="plotly_dark",color_discrete_map={"new": "rgba(255,105,180, 1)", "old":"rgba(100,136,234,0.5)"})
        fig.update_layout(paper_bgcolor= "rgba(48,48,48, 0)",plot_bgcolor= "rgba(48,48,48, 0)", showlegend=False)
        #fig = px.line_polar(get_scoreboard_pd(), r='value', theta='score', color="cat", line_close=True, template="plotly_dark")
        #fig.update_layout({"paper_bgcolor": "rgba(0, 0, 0, 0)","plot_bgcolor": "rgba(0, 0, 0, 0)"})
        #fig.update_layout(legend=dict(orientation= 'h', y=-0.15))
        with open("game_stats.json", "at") as fo:
            json.dump({"total_score":style_score,
                       "style_score":style_score, 
                       "time_score":time_score,
                       "map_score":map_score,
                       'cor_style':correct_style['name'], 
                       "sel_style":sel_style, 
                       "startY":style["Start_Year"],
                       "endY":style["End_Year"], 
                       "sel_year":sel_year,
                        "cor_region":correct_style["style_area"],
                        "sel_region":closest_reg,
                        "sel_lat":sel_map[0],
                        "sel_lon":sel_map[1]},fo)
            fo.write("\n")
        return [
            submit_disabled(), 
            resultmodal_isopen, 
            f"You got {total_score} points (Rank: {rank} of {len(scoreboard)})",
            rnd_style,
            f'{startY} to {endY}',
            f'{style["style_area"]}',
            fig,
            astyle["description"],
            [html.Li(c) for c in astyle["characteristics"]],
            [html.Li(c) for c in astyle["examples"]],
            [html.Li(c["name"]) for c in aarch],
            f"\n (You: {sel_style}, {style_score} Pt.)",
            f"  (You: {sel_year}, {time_score} Pt.)",
            f"  (You: {closest_reg}, {map_score} Pt.)"
        ]
    else:
        raise PreventUpdate


@app.callback(  # Output("setup_modal", "is_open"),
    Output("video_body", "style"), Input("SETUP", "n_clicks"), prevent_initial_call=True
)
def display_setup_modall(n):
    return {"visibility": "hidden"} if n % 2 == 0 else {"visibility": "visible"}


@app.callback(
    Output("example_img", "hidden"),
    Output("example_poem", "hidden"),
    Input("MODE", "n_clicks"), prevent_initial_call=True
)
def mode_switch(n):
    global game_mode_img
    game_mode_img = not game_mode_img
    return [game_mode_img, not game_mode_img]

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
