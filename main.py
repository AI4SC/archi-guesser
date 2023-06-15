import os

import dash_bootstrap_components as dbc
import json
from dash import dcc, html, Dash, ALL, callback_context
from dash.dependencies import Input, Output, State
from PIL import Image
import dash_leaflet as dl
import random
from flask import Flask

demo_mode = False
demo_step = 0
demo_sub  = 0


demo_steps = [{
    "sel_style": "Gothic Revival",
    "sel_location": [45.43162972000005, 2.8125],
    "sel_epoche": 1884,
    "rnd_style": "Gothic Revival",
    "points": 1000,
    "rnd_img": "Neuschwanstein"
},{
    "sel_style": "Gothic Revival",
    "sel_location": [45.43162972000005, 2.8125],
    "sel_epoche": 1884,
    "rnd_style": "Gothic Revival",
    "points": 1000,
    "rnd_img": "Neuschwanstein"
}, {
    "sel_style": "Parametricism",
    "sel_location": [47.040182144806664, 25.312500000000004],
    "sel_epoche": 1990,
    "rnd_style": "Parametricism",
    "points": 2000,
    "rnd_img": "Neuschwanstein_Parametric"
}, {
    "sel_style": "Chinese",
    "sel_location": [49.38237278700955, 16.875000000000004],
    "sel_epoche": 1600,
    "rnd_style": "Chinese Imperial",
    "points": 1000,
    "rnd_img": "Neuschwanstein_Chinese_Imperial"
}, {
    "sel_style": "Chinese",
    "sel_location": [33.7243396617476, 135.70312500000003],
    "sel_epoche": 1600,
    "rnd_style": "Chinese Imperial",
    "points": 1000,
    "rnd_img": "Pagoda"
}, {
    "sel_style": "Bauhaus",
    "sel_location": [36.59788913307022, 111.79687500000001],
    "sel_epoche": 1930,
    "rnd_style": "Bauhaus",
    "points": 1000,
    "rnd_img": "Pagoda_Bauhaus"
}, {
    "sel_style": "Mud Brick",
    "sel_location": [19.973348786110613, 101.25000000000001],
    "sel_epoche": 1400,
    "rnd_style": "Mud Brick",
    "points": 1000,
    "rnd_img": "Pagoda_MudBrickHouse"
}, {
    "sel_style": "Mud Brick",
    "sel_location": [11.938881539525834, 5.625],
    "sel_epoche": 1884,
    "rnd_style": "Mud Brick",
    "points": 1000,
    "rnd_img": "MudBrickHouse"
}, {
    "sel_style": "Art Nouveau",
    "sel_location": [7.710991655433217, 33.75000000000001],
    "sel_epoche": 1920,
    "rnd_style": "Art Nouveau",
    "points": 2000,
    "rnd_img": "MudBrickHouse_Art_Nouveau"
}, {
    "sel_style": "Art Deco",
    "sel_location": [19.973348786110613, -11.25],
    "sel_epoche": 1930,
    "rnd_style": "Art Deco",
    "points": 1000,
    "rnd_img": "MudBrickHouse_Art_Deco"
}, {
    "sel_style": "Art Deco",
    "sel_location": [41.50857729743935, -76.640625],
    "sel_epoche": 1930,
    "rnd_style": "Art Deco",
    "points": 1000,
    "rnd_img": "NewYorkArtDeco"
}, {
    "sel_style": "Georgian",
    "sel_location": [50.736455137010665, -66.09375000000001],
    "sel_epoche": 1750,
    "rnd_style": "Georgian",
    "points": 2000,
    "rnd_img": "NewYorkArtDeco_Georgian"
}, {
    "sel_style": "Indoislamic",
    "sel_location": [29.53522956294847, 27.421875000000004],
    "sel_epoche": 1930,
    "rnd_style": "Ancient Persian",
    "points": 1000,
    "rnd_img": "NewYorkArtDeco_Persian"
}, {
    "sel_style": "Indoislamic",
    "sel_location": [25.25320751294064, 41.48437500000001],
    "sel_epoche": 1884,
    "rnd_style": "Ancient Persian",
    "points": 1000,
    "rnd_img": "qom-art-monument"
}, {
    "sel_style": "Stilt House",
    "sel_location": [15.961329081596647, 103.35937500000001],
    "sel_epoche": 1920,
    "rnd_style": "Stilt House",
    "points": 2000,
    "rnd_img": "qom-art-monument_stilt_house"
}, {
    "sel_style": "Expressionism",
    "sel_location": [-27.059125784374054, 135.00000000000003],
    "sel_epoche": 1970,
    "rnd_style": "Neo-Expressionism",
    "points": 1000,
    "rnd_img": "qom-art-monument_sidney_opera"
}]

try:
    with open("architect_styles.json", 'tr') as fi:
        architects_by_style = json.load(fi)
except:
    architects_by_style = {}

for k, v in architects_by_style.items():
    if 'architects' not in v: print("MISSING architects", k)
    for a in v['architects']:
        if 'name' not in a: print("MISSING architect name", k, a)
    if 'terms' not in v: print("MISSING terms", k)
    if 'style' not in v: print("MISSING style", k)
    if 'time_range' not in v['style']: print("MISSING time_range", k)
    if 'period' not in v['style']: print("MISSING period", k)
    if 'description' not in v['style']: print("MISSING description", k)
    if 'characteristics' not in v['style']: print("MISSING characteristics", k)
    if 'examples' not in v['style']: print("MISSING examples", k)
    if 'continent' not in v['style']: print("MISSING continent", k)
    if 'country' not in v['style']: print("MISSING country", k)
    # print(k)

bwtileurl = 'http://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}.png'

archig_image = Image.open("archiguesser_logo.png")
style_image = Image.open("styles_crop.png")
ai4sc_image = Image.open("ai4sc_logo.png")
urost_image = Image.open("uni-rostock.png.webp")

style_img = {}
for fn in os.listdir('styles120'):
    if fn.endswith(".png"):
        img = Image.open(os.path.join('styles120', fn))
        style_img[fn.replace('.png', '').replace('_', ' ').title()] = img

style_img = {i: style_img[i] for i in sorted(list(style_img.keys()))}

if demo_mode:
    demo_keys=list(set([s["sel_style"] for s in demo_steps]))
    style_img= {k:style_img[k] for k in demo_keys}

examples_img = {}
for fn in os.listdir('examples'):
    if fn.endswith(".png"):
        img = Image.open(os.path.join('examples', fn))
        examples_img[fn.replace('.png', '')] = img
        pil_image = img

# print(examples_img.keys())

style_ccc = [None for c in style_img.keys()]
sel_style = None
sel_location = None
sel_epoche = None
rnd_style = "Bauhaus architecture"


for demostep in demo_steps:
    if demostep['rnd_style'] not in architects_by_style: print("MISSING rnd_style", demostep['rnd_style'])
    if demostep['sel_style'] not in style_img: print("MISSING sel_style", demostep['sel_style'])
    if demostep['rnd_img'] not in examples_img: print("MISSING rnd_img", demostep['rnd_img'])

# Open region GeoJSON
with open("cultural_regions_simplified.geojson", 'tr') as fi:
    regions = json.load(fi)

# Establish which countries belong to which cultural region
countries_by_region = {
    "Anglo World": [
        "United Kingdom", "Australia", "New Zealand", "Ireland", "United States",
        "Canada"
    ],
    "Europe": [
        "Poland", "Czechia", "Hungary", "Bulgaria", "Serbia", "Slovakia",
        "Croatia", "Bosnia & Herzegovina", "North Macedonia", "Slovenia",
        "Montenegro", "Germany", "France", "Netherlands", "Belgium", "Austria",
        "Switzerland", "Italy", "Spain", "Portugal", "Luxembourg", "Sweden",
        "Denmark", "Finland", "Norway", "Lithuania", "Latvia", "Estonia", "Greece",
        "Cyprus", "Iceland", "Greenland", "Romania", "Albania"
    ],
    "North Eurasia":
        ["Russia", "Ukraine", "Belarus", "Georgia", "Armenia", "Moldova"],
    "Central & South America": [
        "Jamaica", "Trinidad & Tobago", "Bahamas", "Guyana", "Suriname", "Belize",
        "Mexico", "Colombia", "Peru", "Venezuela", "Guatemala", "Ecuador",
        "Dominican Rep.", "Honduras", "Nicaragua", "El Salvador", "Costa Rica",
        "Panama", "Puerto Rico", "Argentina", "Chile", "Uruguay", "Bolivia",
        "Paraguay", "Cuba", "Brazil", "French Guiana", "Cape Verde", "Mauritius",
        "Reunion"
    ],
    "Middle East & North Africa": [
        "Saudi Arabia", "U.A.E.", "Kuwait", "Oman", "Qatar", "Bahrain", "Egypt",
        "Iraq", "Syria", "Jordan", "Libya", "Palestine", "Morocco", "Algeria",
        "Tunisia", "Yemen", "Lebanon", "Israel", "Iran", "Afghanistan", "Pakistan"
    ],
    "Sahel & Sub-Saharan Africa": [
        "Sudan", "Mauritania", "Niger", "Mali", "Chad", "Somalia", "Djibouti",
        "Ivory Coast", "Burkina Faso", "Senegal", "Guinea", "Benin", "Togo",
        "Gambia", "Guinea-Bissau", "Tanzania", "Kenya", "Uganda", "Malawi",
        "Zambia", "Rwanda", "Burundi", "D.R. Congo", "Cameroon",
        "Central African Rep.", "Rep. Congo", "Gabon", "Equatorial Guinea",
        "Nigeria", "Ghana", "Sierra Leone", "Liberia", "Mozambique", "Angola",
        "Madagascar", "South Sudan", "Haiti", "South Africa", "Namibia",
        "Botswana", "Lesotho", "Eswatini", "Zimbabwe", "Ethiopia", "Eritrea"
    ],
    "South Asia": ["India", "Nepal", "Bhutan", "Bangladesh", "Sri Lanka"],
    "Central Asia": [
        "Uzbekistan", "Kazakhstan", "Kyrgyzstan", "Turkmenistan", "Turkey",
        "Azerbaijan", "Tajikistan", "Mongolia"
    ],
    "East Asia": ["China", "Taiwan", "Japan", "South Korea", "North Korea"],
    "Southeast Asia & South Pacific": [
        "Cambodia", "Laos", "Myanmar", "Thailand", "Vietnam", "Singapore",
        "Malaysia", "Brunei", "Indonesia", "Philippines", "Papua New Guinea",
        "Solomon Islands", "Vanuatu", "New Caledonia", "Fiji", "Samoa",
        "French Polynesia", "East Timor"
    ]
}

# Mapping of identifiers to colors.
# region_colors = {
#  "Anglo World": '#27BEB6',
#  "Europe": '#518BC9',
#  "North Eurasia": '#8B91F5',
#  "Central & South America": '#F4AE1A',
#  "Middle East & North Africa": '#EFD31A',
#  "Sahel & Sub-Saharan Africa": '#F36B28',
#  "South Asia": '#67BF6B',
#  "Central Asia": '#EC468B',
#  "East Asia": '#F5A051',
#  "Southeast Asia & South Pacific": '#BAF87F',
#  "Antarctica": '#000000'
# }
region_colors = {
    "Anglo World": '#b3de69',
    "Europe": '#8dd3c7',
    "North Eurasia": '#80b1d3',
    "Central & South America": '#fb8072',
    "Middle East & North Africa": '#ffed6f',
    "Sahel & Sub-Saharan Africa": '#fdb462',
    "South Asia": '#ffffb3',
    "Central Asia": '#B3B9FF',
    "East Asia": '#bc80bd',
    "Southeast Asia & South Pacific": '#fccde5',
    "Antarctica": '#000000'
}

# Create a GeoJSON layer for each feature (polygon) in the GeoJSON file and assign the color from the dictionary
layers = [
    dl.TileLayer(url='http://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}.png',
                 attribution='© OpenStreetMap contributors, © CartoDB')
]
for feature in regions['features']:
    # Replace 'id' with the name of the property that holds your identifiers
    identifier = feature['properties']['Region']
    color = region_colors.get(
        identifier,
        "#000000")  # default to black if the id is not found in the dictionary
    layers.append(
        dl.GeoJSON(
            data=dict(type='FeatureCollection', features=[feature]),
            options=dict(style=dict(color=color, fillColor=color, fillOpacity=1))))

# Add layer that later contains the map marker
layers.append(dl.LayerGroup(id="layer"))


# Build App
server = Flask(__name__)
app = Dash(server=server, external_stylesheets=[dbc.themes.DARKLY])
app.title = "ArchiGuessr"

app.layout = dbc.Container(
    [
        dbc.Row([
            dbc.Col(
                [
                    html.Img(src=archig_image, style={
                        'height': '80px'
                    })  # , html.P("An AI Art Architecture Educational Game")
                ],
                width=8),
            dbc.Col(html.Img(src=ai4sc_image, style={'height': '60px'}), width=2),
            dbc.Col(html.Img(src=urost_image, style={'height': '60px'}), width=2),
        ]),
        dbc.Row([
            dbc.Col(
                [html.Img(src=pil_image, style={'width': '100%', "padding-left": "20px"}, id='example_img')],
                width=6),
            dbc.Col(
                [
                    dbc.Label("STYLE"),
                    html.Section([dbc.Row([
                        dbc.Col(
                            dbc.Button([
                                html.Img(src=img, alt=n),
                                html.Br(),
                                html.P(n, style={}),
                            ],
                                color=None,
                                name=n,
                                style={
                                    "width": "130px",
                                    "height": "160px"
                                },
                                id={
                                    "type": "style-selection",
                                    "index": n
                                })) for n, img in style_img.items()
                    ],
                        className="no-gutters no-padders"),
                        html.Div([
                            html.H3("Please select a 3D object that represents the style",
                                    style={
                                        "text-align": "center",
                                        "width": "100%",
                                        "height": "50px",
                                        "position": "absolute",
                                        "top": "100px",
                                    })
                        ], style={"width": "50%",
                                  "height": "320px",
                                  "position": "fixed",
                                  "top": "100px",
                                  "left": "50%",
                                  "z-index": "10",
                                  "background-color": "rgba(34, 34, 34, 0.8)"
                                  }, hidden= demo_mode, id="style-msg")],
                        style={
                            "width": "100%",
                            "height": "320px",
                            "overflow": "scroll",
                            "position": "static"
                        },
                        className="scrollable"),
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
                            'width': '100%',
                            'height': '40vh',
                            'margin': "auto",
                            "z-index": "10",
                            "display": "block"
                        },
                        maxZoom=4,
                        zoom=1),
                    html.Div([
                        html.H3("Please place the 3D object on the map",
                                style={
                                    "text-align": "center",
                                    "width": "100%",
                                    "height": "50px",
                                    "position": "absolute",
                                    "top": "100px",
                                })
                    ], style={"width": "50%",
                              "height": "460px",
                              "position": "fixed",
                              "top": "455px",
                              "left": "50%",
                              "z-index": "20",
                              "background-color": "rgba(34, 34, 34, 0.8)"
                              }, hidden= demo_mode, id="map-msg"),
                    dbc.Label("EPOCHE"),
                    dcc.Slider(0,
                               2025,
                               step=5,
                               marks={
                                   500: 'Ancient and Classical Periods',
                                   1500: 'Medieval Period',
                                   1700: 'Renaissance',
                                   1800: '18th',
                                   1900: '19th',
                                   2000: '20th',
                                   2025: '21th'
                               },
                               value=1200,
                               included=False,
                               tooltip={
                                   "placement": "bottom",
                                   "always_visible": True
                               },
                               id="epoche"),
                    html.Div([
                        html.H3("Please select an epoche",
                                style={
                                    "text-align": "center",
                                    "width": "100%",
                                    "height": "50px",
                                    "position": "absolute",
                                    "top": "10px",
                                })
                    ], style={"width": "50%",
                              "height": "50px",
                              "position": "fixed",
                              "top": "920px",
                              "left": "50%",
                              "z-index": "20",
                              "background-color": "rgba(34, 34, 34, 0.8)"
                              }, hidden= demo_mode, id="epoche-msg"),
                    dbc.Row([
                        dbc.Col(
                            dbc.Button(
                                "GUESS",
                                style={'height': '40px'}, id="GUESS", disabled=True)),
                    ]),
                    dbc.Label("", id="out1")
                ],
                width=6)
        ]),
        dbc.Modal([
            dbc.ModalHeader(dbc.ModalTitle("You got 0 points", id="points")),
            dbc.ModalBody([], id="style_body"),
            dbc.ModalFooter([dbc.Button("Close", id="close", class_name="ms-auto")])
        ],
            id="resultmodal"),
        html.Button("", id="new_run", style={"visibility": "hidden"
                                      }, disabled=True),  # used as event notifier
        dcc.Interval(id='interval1', interval=5000)
    ],
    fluid=True)


def tostr(obj):
    if isinstance(obj, str): return obj
    if isinstance(obj, list):
        return ", ".join(obj)
    else:
        return str(obj)

if demo_mode:

    @app.callback(
        Output('GUESS', 'disabled', allow_duplicate=True),
        Output("example_img", "src"),
        Output("style_body", "children"),
        Output("resultmodal", "is_open", allow_duplicate=True),
        Output("points", "children"),
        Output({
            'type': "style-selection",
            'index': ALL
        }, 'color', allow_duplicate=True),
        Output("style-msg", "hidden"),
        Output("map-msg", "hidden"),
        Output("epoche-msg", "hidden"),
        Output('epoche', 'value'),
        Output("layer", "children"),
        Input('interval1', 'n_intervals'),
        State({
            "type": "style-selection",
            "index": ALL
        }, "name"),
        prevent_initial_call=True)
    def demo_mode_cnt(cnt, names):
        global rnd_style, sel_style, sel_epoche, sel_location, demo_step, demo_sub
        #print(cnt, demo_step, demo_sub)
        demostep = demo_steps[demo_step]
        if demo_sub == 0:
            print(f"DEMO {demo_step}: {demostep['rnd_style']} ({demostep['rnd_img']})")
            demo_step += 1
            if demo_step >= len(demo_steps): demo_step = 0
            sel_style, sel_location, sel_epoche = None, None, 0
        elif demo_sub == 2:
            sel_style = demostep['sel_style']
        elif demo_sub == 3:
            sel_location = demostep['sel_location']
        elif demo_sub == 4:
            sel_epoche = demostep['sel_epoche']
        elif demo_sub == 5:
            result_modal_open = True
        hide_style = demo_sub >= 2
        hide_map = demo_sub >= 3
        hide_epoche = demo_sub >= 4
        guess_btn_disabled = demo_sub < 4
        result_modal_open = demo_sub >= 5

        rnd_img = examples_img[demostep['rnd_img']]
        rnd_style = demostep['rnd_style']
        astyle = architects_by_style[rnd_style]["style"]
        aarch = architects_by_style[rnd_style]["architects"]
        styles = ['primary' if sel_style == n else None for n in names]
        print(rnd_style, astyle, aarch)

        demo_sub += 1
        if demo_sub == 6: demo_sub = 0

        return guess_btn_disabled, \
               rnd_img, \
               [
                   html.H3(rnd_style),
                   html.Label("Epoche"),
                   html.P(f'{astyle["time_range"]} ({astyle["period"]})'),
                   html.Label("Location"),
                   html.P(f'{tostr(astyle["country"])} ({tostr(astyle["continent"])})'),
                   html.Label("Description"),
                   html.P(astyle["description"]),
                   html.Label("Characteristics"),
                   html.Ul([html.Li(c) for c in astyle["characteristics"]]),
                   html.Label("Examples"),
                   html.Ul([html.Li(c) for c in astyle["examples"]]),
                   html.Label("Architects"),
                   html.Ul([html.Li(c["name"]) for c in aarch]),
               ], \
               result_modal_open, \
               f"You got {demostep['points']} points", \
               styles, \
               hide_style, \
               hide_map, \
               hide_epoche, \
               sel_epoche, \
               [dl.Marker(position=sel_location, children=dl.Tooltip("({:.3f}, {:.3f})".format(*sel_location)))] if sel_location else []

else:
    @app.callback(Output('GUESS', 'disabled', allow_duplicate=True),
                  Output("layer", "children"),
                  Input('map', 'click_lat_lng'),
                  prevent_initial_call=True)
    def display_selected_data(click_lat_lng):
        global sel_location
        if click_lat_lng is None: return True, []
        sel_location = click_lat_lng
        print(sel_location, sel_style, sel_epoche)
        return sel_location is None or sel_style is None or sel_epoche is None, [
            dl.Marker(position=click_lat_lng,
                      children=dl.Tooltip("({:.3f}, {:.3f})".format(*click_lat_lng)))
        ]


    @app.callback(Output('GUESS', 'disabled', allow_duplicate=True),
                  Input('epoche', 'value'),
                  prevent_initial_call=True)
    def display_selected_epoche(value):
        global sel_epoche
        if value is None: return True
        sel_epoche = value
        return sel_location is None or sel_style is None or sel_epoche is None


    @app.callback(Output('GUESS', 'active', allow_duplicate=True),
                  Output({
                      'type': "style-selection",
                      'index': ALL
                  }, 'color', allow_duplicate=True),
                  Input({
                      "type": "style-selection",
                      "index": ALL
                  }, "n_clicks"),
                  State({
                      "type": "style-selection",
                      "index": ALL
                  }, "name"),
                  prevent_initial_call=True)
    def select_style(n, names):
        global sel_style
        if callback_context.triggered_prop_ids:
            for v in callback_context.triggered_prop_ids.values():
                sel_style = v['index']
                styles = ['primary' if sel_style == n else None for n in names]
                return sel_location is None or sel_style is None or sel_epoche is None, styles
        else:
            return True, style_ccc


    @app.callback(
        Output('GUESS', 'disabled', allow_duplicate=True),
        Output("example_img", "src"),
        Output("style_body", "children"),
        Input("new_run", "disabled"),  # used as event notifier
        prevent_initial_call=True)
    def select_random_style(new_run):
        global rnd_style, sel_style, sel_epoche, sel_location
        rnd_style = random.choice(list(architects_by_style.keys()))
        rnd_img = random.choice(list(examples_img.values()))
        print(rnd_style)
        astyle = architects_by_style[rnd_style]["style"]
        aarch = architects_by_style[rnd_style]["architects"]
        print(rnd_style, astyle, aarch)
        sel_style, sel_epoche, sel_location = None, None, None
        return True, rnd_img, [
            html.H3(rnd_style),
            html.Label("Epoche"),
            html.P(f'{astyle["time_range"]} ({astyle["period"]})'),
            html.Label("Location"),
            html.P(f'{tostr(astyle["country"])} ({tostr(astyle["continent"])})'),
            html.Label("Description"),
            html.P(astyle["description"]),
            html.Label("Characteristics"),
            html.Ul([html.Li(c) for c in astyle["characteristics"]]),
            html.Label("Examples"),
            html.Ul([html.Li(c) for c in astyle["examples"]]),
            html.Label("Architects"),
            html.Ul([html.Li(c["name"]) for c in aarch]),
        ]

if __name__ == '__main__':
    # run application
    if 'DASH_DEBUG_MODE' in os.environ:
        app.run_server(host='0.0.0.0',
                       dev_tools_ui=True,
                       debug=True,
                       dev_tools_hot_reload=True,
                       threaded=True)
    else:
        app.run_server(host='0.0.0.0', debug=False)
