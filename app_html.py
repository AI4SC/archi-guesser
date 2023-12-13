import dash_bootstrap_components as dbc
from dash import (
    dcc,
    html
)
from PIL import Image
import os
import random
import dash_leaflet as dl
from app_map import *
import uuid

mask = True

archig_image = Image.open("archiguesser_logo.png")
style_image = Image.open("styles_crop.png")
ai4sc_image = Image.open("ai4sc_logo.png")
urost_image = Image.open("uni-rostock.png.webp")
marker_to_style={}
game_mode_img = True

# Load architect styles
with open("architect_styles_sub.json", "tr", encoding='utf-8') as fi:
    architects_by_style = json.load(fi)

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
    if "Start_Year" not in v:
        print("MISSING Start_Year", k)
    if "End_Year" not in v:
        print("MISSING End_Year", k)
    if "description" not in v["style"]:
        print("MISSING description", k)
    if "characteristics" not in v["style"]:
        print("MISSING characteristics", k)
    if "examples" not in v["style"]:
        print("MISSING examples", k)
    if "style_area" not in v:
        print("MISSING style_area", k)
    if "name" not in v:
        print("MISSING name", k)
    if "poems" not in v:
        print("MISSING poems", k)
    else:
        v['poems_uuid']=[str(uuid.uuid3(uuid.NAMESPACE_X500, p)) for p in v['poems']] # compute hash for poem

style_img = {}
for fn in os.listdir("styles120"):
    if fn.endswith(".png"):
        ifn = fn.replace(".png", "").replace("_", " ").title()
        if ifn in architects_by_style:
            style_img[ifn] = Image.open(os.path.join("styles120", fn))

style_img = {i: style_img[i] for i in sorted(list(style_img.keys()))}
#print(sorted(list(style_img.keys())))

examples_img = {}
for fn in os.listdir("style_generated"):
    if os.path.isdir(os.path.join("style_generated", fn)) and fn in architects_by_style and fn in style_img:
        examples_img[fn] = []
        for fni in os.listdir(os.path.join("style_generated", fn)):
            if fni.endswith(".png"):
                img = Image.open(os.path.join("style_generated", fn, fni))
                examples_img[fn].append(img)

#print(sorted(list(examples_img.keys())))

# Remove missing
architects_by_style = {k:architects_by_style[k] for k in architects_by_style.keys() if k in examples_img and k in style_img}
examples_img = {k:examples_img[k] for k in architects_by_style.keys()}
style_img = {k:style_img[k] for k in architects_by_style.keys()}

#print(sorted(list(architects_by_style.keys())))
#print(sorted(list(style_img.keys())))
#print(sorted(list(examples_img.keys())))
#print(marker_to_style)

def select_audio(rnd_style):
    global game_mode_img
    poem=""
    phtml=[]
    pcnt=len(architects_by_style[rnd_style]["poems"])
    for i in range(5):
        rp=random.randint(0,pcnt-1)
        verses=architects_by_style[rnd_style]["poems"][rp].split("\n\n")
        phash=architects_by_style[rnd_style]["poems_uuid"][rp]
        if len(verses) >= i and os.path.exists(f"assets/poems/{rnd_style}/{phash}_{i}.mp3"):
            poem += verses[i]+"\n\n"
            phtml.append(html.Audio(src=f"assets/poems/{rnd_style}/{phash}_{i}.mp3", controls=True, autoPlay= i == 0 and not game_mode_img)) # , onloadeddata="var ap = this; setTimeout(function() { ap.play(); }, "+str(i*17000)+")"
    phtml.insert(0,html.P(poem))
    return phtml

rnd_style = random.choice(list(architects_by_style.keys()))
rnd_img = random.choice(examples_img[rnd_style])
rnd_poem = select_audio(rnd_style)
style = architects_by_style[rnd_style]
astyle = style["style"]
aarch = style["architects"]
startY=f"{style['Start_Year']} CE" if style["Start_Year"]>0 else f"{-style['Start_Year']} BCE"
endY=f"{style['End_Year']} CE" if style["End_Year"]>0 else f"{-style['End_Year']} BCE"

def init_webpage():
    return dbc.Container(
    [
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.Img(
                            src=archig_image, style={"height": "80px"}
                        )  # , html.P("An AI Art Architecture Educational Game")
                    ],
                    width=6,
                ),
                dbc.Col(html.Img(src=ai4sc_image, style={"height": "60px"}), width=2),
                dbc.Col(html.Img(src=urost_image, style={"height": "60px"}), width=2),
                dbc.Col(
                    [
                        html.Span("•", id="state_dot", className="col_gray"),
                        html.Span(html.I(className="bi bi-house"), id="state_style", className="col_gray"),
                        html.Span(html.I(className="bi bi-geo-alt"), id="state_map", className="col_gray"),
                        html.Span(html.I(className="bi bi-clock"), id="state_time", className="col_gray"),
                        html.Span(html.I(className="bi bi-play"), id="state_on", className="col_gray"),
                        dbc.Button(
                            html.I(className="bi bi-image"),
                            style={"height": "60px"},
                            id="MODE",
                            color="dark",
                            outline=True,
                            className="border-0",
                        ),
                        dbc.Button(
                            html.I(className="bi bi-gear"),
                            style={"height": "60px"},
                            id="SETUP",
                            color="dark",
                            outline=True,
                            className="border-0",
                        )
                    ],
                    width=2,
                ),
            ]
        ),
        dbc.Row(
            [
                dbc.Col(
                    html.Div([
                        html.Img(
                            src=rnd_img,
                            id="example_img",
                            hidden = False,
                        ),
                        html.Div(rnd_poem, 
                            id="example_poem",
                            hidden = True)
                    ], className="center"),
                    width=6,
                ),
                dbc.Col(
                    [
                        dbc.Label("STYLE"),
                        html.Div([
                            html.Section(
                                [
                                    dbc.Row(
                                        [
                                            dbc.Col(
                                                dbc.Button(
                                                    [
                                                        html.Img(src=img, alt=n),
                                                        html.Br(),
                                                        html.P(n, style={}),
                                                    ],
                                                    color=None,  #"dark"
                                                    name=n,
                                                    className="stylebtn",
                                                    id={
                                                        "type": "style-selection",
                                                        "index": n,
                                                    },
                                                ),
                                                id={
                                                    "type": "style-selection-col",
                                                    "index": n,
                                                }
                                            )
                                            for n, img in style_img.items()
                                        ],
                                        className="no-gutters no-padders",
                                    ),
                                ],
                                style={
                                    "width": "100%",
                                    "height": "320px",
                                    "overflow": "scroll",
                                    "position": "static",
                                },
                                className="scrollable",
                            ),
                                html.Div(
                                    [
                                        html.H3(
                                            "Please select a 3D object that represents the style",
                                            style={
                                                "textAlign": "center",
                                                "width": "100%",
                                                "height": "50px",
                                                "position": "absolute",
                                                "top": "100px",
                                            },
                                        )
                                    ],
                                    style={
                                        "top": "0px",
                                        "left": "0px",
                                        "width": "100%",
                                        "height": "100%",
                                        "position": "absolute",
                                        "zIndex": "10",
                                        "backgroundColor": "rgba(34, 34, 34, 0.8)",
                                    },
                                    hidden = mask,
                                    id = "style-mask",
                                )
                        ],style={"position": "relative"}),
                        dbc.Label("LOCATION"),
                        html.Div([
                            dl.Map(
                                children=layers,  # url=bwtileurl
                                id="map",
                                maxZoom=4,
                                zoom=1,
                                center=[40,0],
                            ),
                            html.Div(
                                [
                                    html.H3(
                                        "Please place the 3D object on the map",
                                        style={
                                            "textAlign": "center",
                                            "width": "100%",
                                            "height": "50px",
                                            "position": "absolute",
                                            "top": "100px",
                                        },
                                    )
                                ],
                                style={
                                    "top": "0px",
                                    "left": "0px",
                                    "width": "100%",
                                    "height": "100%",
                                    "position": "absolute",
                                    "zIndex": "20",
                                    "backgroundColor": "rgba(34, 34, 34, 0.8)",
                                },
                                hidden = mask,
                                id = "map-mask",
                            ),
                        ],style={"position": "relative"}),
                        dbc.Label("EPOCHE"),
                        html.Div([
                            dcc.Slider(
                                0,
                                2025,
                                step=5,
                                marks={
                                    500: "Ancient Periods",
                                    1500: "Medieval Period",
                                    1700: "Renaissance",
                                    1800: "18th",
                                    1900: "19th",
                                    2000: "20th",
                                },
                                value=1200,
                                included=False,
                                tooltip={"placement": "bottom", "always_visible": True},
                                id="epoche",
                            ),
                            html.Div(
                                [
                                    html.H3(
                                        "Please select an epoche",
                                        style={
                                            "textAlign": "center",
                                            "width": "100%",
                                            "height": "50px",
                                            "position": "absolute",
                                            "top": "10px",
                                        },
                                    )
                                ],
                                style={
                                    "top": "0px",
                                    "left": "0px",
                                    "width": "100%",
                                    "height": "100%",
                                    "position": "absolute",
                                    "zIndex": "20",
                                    "backgroundColor": "rgba(34, 34, 34, 0.8)",
                                },
                                hidden = mask,
                                id = "epoche-mask",
                            ),
                        ],style={"position": "relative"}),
                        dbc.Row(
                            [
                                dbc.Col(
                                    dbc.Button(
                                        "GUESS",
                                        style={"height": "40px"},
                                        id="SUBMIT_GUESS",
                                        disabled=False,
                                    )
                                ),
                            ]
                        ),
                        dbc.Label("", id="out1"),
                    ],
                    width=6,
                ),
            ]
        ),
        # dbc.Modal([
        #  dbc.ModalHeader(dbc.ModalTitle("Video Test")),
        #  dbc.ModalBody([
        #    html.Video(id="video", autoPlay=True, width=640, height=480, style={"display":"none"}), #
        #    html.Canvas(id="canvas", width=640, height=480), # , style={"display":"none"}
        #  ], id="video_body"),
        #  dbc.ModalFooter([html.Div(id="info", style={"margin": "15px"})])
        # ], id="setup_modal", is_open=True, size="lg"),
        html.Div(
            [
                html.Div(id="clientside-output", children="", style={"margin": "15px"}),
                html.Video(
                    id="video",
                    autoPlay=True,
                    width=640,
                    height=480,
                    style={"display": "none"},
                ),  #
                html.Canvas(
                    id="canvas", width=640, height=480
                )  # , style={"display":"none"}
            ],
            id="video_body",
            style={"visibility": "hidden"},
            className="setupdiv",
        ),
        dbc.Modal(
            [
                dbc.ModalHeader(dbc.ModalTitle("You got 0 points", id="points"), close_button=False),
                dbc.ModalBody(dbc.Container([
                    dbc.Row([
                        dbc.Col([
                            html.H3(rnd_style, id="res_style"),
                            html.Label("Epoche"),
                            html.P(f'{startY} to {endY}', id="res_year"),
                            html.Label("Location"),
                            html.P(f'{rnd_style}', id="res_loc"),
                            html.Label("Architects"),
                            html.Ul([html.Li(c["name"]) for c in aarch], id="res_arch"),
                        ]),
                        dbc.Col(dcc.Graph(style={"width":"100%","height":"100%","marginLeft":"auto","display":"block"}, id="res_plot")),
                    ]),
                    html.Label("Description"),
                    html.P(astyle["description"], id="res_desc"),
                    html.Label("Characteristics"),
                    html.Ul([html.Li(c) for c in astyle["characteristics"]], id="res_char"),
                    html.Label("Examples"),
                    html.Ul([html.Li(c) for c in astyle["examples"]], id="res_examp"),
                ]), id="style_body"),
                dbc.ModalFooter([
                    dbc.Button("New Run", id="new_run_btn", class_name="ms-auto")
                ]),
            ],
            id="resultmodal",
            size="lg",
            keyboard=False,
            backdrop="static"
        ),
        #html.Button("", id="new_run", style={"visibility": "hidden"}, disabled=True),  # used as event notifier
        dcc.Interval(id="demo-interval", interval=5000),
        dcc.Interval(id="camera-update", interval=500, n_intervals=0),
        dcc.Store(id="guess-data")
    ],
    fluid=True,
)