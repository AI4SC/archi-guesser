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

mask = False

archig_image = Image.open("archiguesser_logo.png")
style_image = Image.open("styles_crop.png")
ai4sc_image = Image.open("ai4sc_logo.png")
urost_image = Image.open("uni-rostock.png.webp")

style_img = {}
for fn in os.listdir("styles120"):
    if fn.endswith(".png"):
        img = Image.open(os.path.join("styles120", fn))
        style_img[fn.replace(".png", "").replace("_", " ").title()] = img

style_img = {i: style_img[i] for i in sorted(list(style_img.keys()))}

examples_img = {}
for fn in os.listdir("style_generated"):
    if os.path.isdir(os.path.join("style_generated", fn)):
        for fni in os.listdir(os.path.join("style_generated", fn)):
            if fni.endswith(".png"):
                img = Image.open(os.path.join("style_generated", fn, fni))
                examples_img[fn + "_" + fni.replace(".png", "")] = img

pil_image = random.choice(list(examples_img.values()))

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
                    width=7,
                ),
                dbc.Col(html.Img(src=ai4sc_image, style={"height": "60px"}), width=2),
                dbc.Col(html.Img(src=urost_image, style={"height": "60px"}), width=2),
                dbc.Col(
                    dbc.Button(
                        html.I(className="bi bi-gear"),
                        style={"height": "60px"},
                        id="SETUP",
                        color="dark",
                        outline=True,
                        className="border-0",
                    ),
                    width=1,
                ),
            ]
        ),
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.Img(
                            src=pil_image,
                            style={"width": "100%", "padding-left": "20px"},
                            id="example_img",
                        )
                    ],
                    width=6,
                ),
                dbc.Col(
                    [
                        dbc.Label("STYLE"),
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
                                                color=None,
                                                name=n,
                                                style={
                                                    "width": "130px",
                                                    "height": "160px",
                                                },
                                                id={
                                                    "type": "style-selection",
                                                    "index": n,
                                                },
                                            )
                                        )
                                        for n, img in style_img.items()
                                    ],
                                    className="no-gutters no-padders",
                                ),
                                html.Div(
                                    [
                                        html.H3(
                                            "Please select a 3D object that represents the style",
                                            style={
                                                "text-align": "center",
                                                "width": "100%",
                                                "height": "50px",
                                                "position": "absolute",
                                                "top": "100px",
                                            },
                                        )
                                    ],
                                    style={
                                        "width": "50%",
                                        "height": "320px",
                                        "position": "fixed",
                                        "top": "100px",
                                        "left": "50%",
                                        "z-index": "10",
                                        "background-color": "rgba(34, 34, 34, 0.8)",
                                    },
                                    hidden=True,  # mask,
                                    id="style-mask",
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
                        dbc.Label("LOCATION"),
                        # dcc.Graph(
                        #  figure=mapfig, id='map', style={
                        #    'width': '100%',
                        #    'height': '30%'
                        #  }),
                        dl.Map(
                            children=layers,  # url=bwtileurl
                            id="map",
                            style={
                                "width": "100%",
                                "height": "40vh",
                                "margin": "auto",
                                "z-index": "10",
                                "display": "block",
                            },
                            maxZoom=4,
                            zoom=1,
                        ),
                        html.Div(
                            [
                                html.H3(
                                    "Please place the 3D object on the map",
                                    style={
                                        "text-align": "center",
                                        "width": "100%",
                                        "height": "50px",
                                        "position": "absolute",
                                        "top": "100px",
                                    },
                                )
                            ],
                            style={
                                "width": "50%",
                                "height": "460px",
                                "position": "fixed",
                                "top": "455px",
                                "left": "50%",
                                "z-index": "20",
                                "background-color": "rgba(34, 34, 34, 0.8)",
                            },
                            hidden=mask,
                            id="map-mask",
                        ),
                        dbc.Label("EPOCHE"),
                        dcc.Slider(
                            0,
                            2025,
                            step=5,
                            marks={
                                500: "Ancient and Classical Periods",
                                1500: "Medieval Period",
                                1700: "Renaissance",
                                1800: "18th",
                                1900: "19th",
                                2000: "20th",
                                2025: "21th",
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
                                        "text-align": "center",
                                        "width": "100%",
                                        "height": "50px",
                                        "position": "absolute",
                                        "top": "10px",
                                    },
                                )
                            ],
                            style={
                                "width": "50%",
                                "height": "50px",
                                "position": "fixed",
                                "top": "920px",
                                "left": "50%",
                                "z-index": "20",
                                "background-color": "rgba(34, 34, 34, 0.8)",
                            },
                            hidden=mask,
                            id="epoche-mask",
                        ),
                        dbc.Row(
                            [
                                dbc.Col(
                                    dbc.Button(
                                        "GUESS",
                                        style={"height": "40px"},
                                        id="SUBMIT_GUESS",
                                        disabled=True,
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
                html.Video(
                    id="video",
                    autoPlay=True,
                    width=640,
                    height=480,
                    style={"display": "none"},
                ),  #
                html.Canvas(
                    id="canvas", width=640, height=480
                ),  # , style={"display":"none"}
                html.Div(id="info", style={"margin": "15px"}),
            ],
            id="video_body",
            style={"visibility": "hidden"},
            className="setupdiv",
        ),
        dbc.Modal(
            [
                dbc.ModalHeader(dbc.ModalTitle("You got 0 points", id="points")),
                dbc.ModalBody([], id="style_body"),
                dbc.ModalFooter(
                    [dbc.Button("Close", id="style_body_close", class_name="ms-auto")]
                ),
            ],
            id="resultmodal",
        ),
        html.Button(
            "", id="new_run", style={"visibility": "hidden"}, disabled=True
        ),  # used as event notifier
        dcc.Interval(id="demo-interval", interval=5000),
        dcc.Interval(id="camera-update", interval=1000, n_intervals=0),
        dcc.Store(id="guess-data"),
        html.Div(id="clientside-output", children="Dash: A web application framework for your data.")
    ],
    fluid=True,
)