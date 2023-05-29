import os

import pandas as pd
import dash_bootstrap_components as dbc
import json
from dash import dcc, html, Dash, ALL, MATCH, callback_context
import plotly.express as px
from dash.dependencies import Input, Output, State
from urllib.request import urlopen
from PIL import Image
import dash_leaflet as dl
import random

try:
    with open("architect_styles.json", 'tr') as fi:
        architects_by_style = json.load(fi)
except:
    architects_by_style = {}

for k,v in architects_by_style.items():
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

bwtileurl = 'https://tiles.stadiamaps.com/tiles/alidade_smooth_dark/{z}/{x}/{y}{r}.png?api_key='
bwtileurl2 = "http://{{s}}.tile.stamen.com/{}/{{z}}/{{x}}/{{y}}.png"

style_image = Image.open("styles_crop.png")
ai4sc_image = Image.open("ai4sc_logo.png")
urost_image = Image.open("uni-rostock.png.webp")

style_img = {}
for fn in os.listdir('styles120'):
    if fn.endswith(".png"):
        img = Image.open(os.path.join('styles120', fn))
        style_img[fn.replace('.png', '').replace('_', ' ')] = img

style_img = {i: style_img[i] for i in sorted(list(style_img.keys()))}

examples_img = {}
for fn in os.listdir('examples'):
    if fn.endswith(".png"):
        img = Image.open(os.path.join('examples', fn))
        examples_img[fn.replace('.png', '').replace('_', ' ')] = img
        pil_image = img


style_ccc=[None for c in style_img.keys()]
sel_style=None
sel_location=None
sel_epoche=None
rnd_style="Bauhaus architecture"

with open("countries.geojson", 'tr') as fi:
    counties = json.load(fi)

sub_regions = {
    "Anglo World": ["United Kingdom", "Australia", "New Zealand", "Ireland", "United States of America", "Canada"],
    "Europe": ["Poland", "Czechia", "Hungary", "Bulgaria", "Serbia", "Slovakia", "Croatia", "Bosnia & Herzegovina", "North Macedonia", "Slovenia", "Montenegro", "Germany",
               "France", "Netherlands", "Belgium", "Austria", "Switzerland", "Italy", "Spain", "Portugal", "Luxembourg", "Sweden", "Denmark", "Finland", "Norway", "Lithuania",
               "Latvia", "Estonia", "Greece", "Cyprus", "Iceland", "Greenland", "Romania", "Albania"],
    "North Eurasia": ["Russia", "Ukraine", "Belarus", "Georgia", "Armenia", "Moldova"],
    "The Caribbean": ["Jamaica", "Trinidad & Tobago", "Bahamas", "Guyana", "Suriname", "Belize"],
    "Latin America": ["Mexico", "Colombia", "Peru", "Venezuela", "Guatemala", "Ecuador", "Dominican Rep.", "Honduras", "Nicaragua", "El Salvador", "Costa Rica", "Panama",
                      "Puerto Rico", "Argentina", "Chile", "Uruguay", "Bolivia", "Paraguay", "Cuba", "Brazil", "French Guiana"],
    "Atlantic Ocean": ["Cape Verde"],
    "Indian Ocean": ["Mauritius", "Reunion"],
    "Arab World": ["Saudi Arabia", "U.A.E.", "Kuwait", "Oman", "Qatar", "Bahrain", "Egypt", "Iraq", "Syria", "Jordan", "Libya", "Palestine", "Morocco", "Algeria", "Tunisia",
                   "Yemen", "Lebanon"],
    "Israel": ["Israel"],
    "Nastaliq Region": ["Iran", "Afghanistan", "Pakistan"],
    "The Sahel": ["Sudan", "Mauritania", "Niger", "Mali", "Chad", "Somalia", "Djibouti"],
    "Tropical Africa": ["Ivory Coast", "Burkina Faso", "Senegal", "Guinea", "Benin", "Togo", "Gambia", "Guinea-Bissau", "Tanzania", "Kenya", "Uganda", "Malawi", "Zambia", "Rwanda",
                        "Burundi", "D.R. Congo", "Cameroon", "Central African Rep.", "Rep. Congo", "Gabon", "Equatorial Guinea", "Nigeria", "Ghana", "Sierra Leone", "Liberia",
                        "Mozambique", "Angola", "Madagascar", "South Sudan", "Haiti"],
    "Southern Africa": ["South Africa", "Namibia", "Botswana", "Lesotho", "Eswatini", "Zimbabwe"],
    "Ethiopic Africa": ["Ethiopia", "Eritrea"],
    "South Asia": ["India", "Nepal", "Bhutan", "Bangladesh", "Sri Lanka"],
    "Central Asia": ["Uzbekistan", "Kazakhstan", "Kyrgyzstan", "Turkmenistan", "Turkey", "Azerbaijan", "Tajikistan", "Mongolia"],
    "East Asia": ["China", "Taiwan", "Japan", "South Korea", "North Korea"],
    "Mainland Southeast Asia": ["Cambodia", "Laos", "Myanmar", "Thailand", "Vietnam"],
    "Singapore": ["Singapore"],
    "Insular Southeast Asia": ["Malaysia", "Brunei", "Indonesia", "Philippines"],
    "South Pacific": ["Papua New Guinea", "Solomon Islands", "Vanuatu", "New Caledonia", "Fiji", "Samoa", "French Polynesia", "East Timor"]
}

regions = {
    "The North & Australasia": ["United Kingdom", "Australia", "New Zealand", "Ireland", "United States of America", "Canada", "Poland", "Czechia", "Hungary", "Bulgaria", "Serbia",
                                "Slovakia", "Croatia", "Bosnia & Herzegovina", "North Macedonia", "Slovenia", "Montenegro", "Germany", "France", "Netherlands", "Belgium",
                                "Austria", "Switzerland", "Italy", "Spain", "Portugal", "Luxembourg", "Sweden", "Denmark", "Finland", "Norway", "Lithuania", "Latvia", "Estonia",
                                "Greece", "Cyprus", "Iceland", "Greenland", "Romania", "Albania", "Russia", "Ukraine", "Belarus", "Georgia", "Armenia", "Moldova"],
    "Central & South America": ["Jamaica", "Trinidad & Tobago", "Bahamas", "Guyana", "Suriname", "Belize", "Mexico", "Colombia", "Peru", "Venezuela", "Guatemala", "Ecuador",
                                "Dominican Rep.", "Honduras", "Nicaragua", "El Salvador", "Costa Rica", "Panama", "Puerto Rico", "Argentina", "Chile", "Uruguay", "Bolivia",
                                "Paraguay", "Cuba", "Brazil", "French Guiana", "Cape Verde", "Mauritius", "Reunion"],
    "Middle East & North Africa": ["Saudi Arabia", "U.A.E.", "Kuwait", "Oman", "Qatar", "Bahrain", "Egypt", "Iraq", "Syria", "Jordan", "Libya", "Palestine", "Morocco", "Algeria",
                                   "Tunisia", "Yemen", "Lebanon", "Israel", "Iran", "Afghanistan", "Pakistan"],
    "The Sahel": ["Sudan", "Mauritania", "Niger", "Mali", "Chad", "Somalia", "Djibouti"],
    "Sub-Saharan Africa": ["Ivory Coast", "Burkina Faso", "Senegal", "Guinea", "Benin", "Togo", "Gambia", "Guinea-Bissau", "Tanzania", "Kenya", "Uganda", "Malawi", "Zambia",
                           "Rwanda", "Burundi", "D.R. Congo", "Cameroon", "Central African Rep.", "Rep. Congo", "Gabon", "Equatorial Guinea", "Nigeria", "Ghana", "Sierra Leone",
                           "Liberia", "Mozambique", "Angola", "Madagascar", "South Sudan", "Haiti", "South Africa", "Namibia", "Botswana", "Lesotho", "Eswatini", "Zimbabwe",
                           "Ethiopia", "Eritrea"],
    "South Asia": ["India", "Nepal", "Bhutan", "Bangladesh", "Sri Lanka"],
    "Central Asia": ["Uzbekistan", "Kazakhstan", "Kyrgyzstan", "Turkmenistan", "Turkey", "Azerbaijan", "Tajikistan", "Mongolia"],
    "East Asia": ["China", "Taiwan", "Japan", "South Korea", "North Korea"],
    "Southeast Asia": ["Cambodia", "Laos", "Myanmar", "Thailand", "Vietnam", "Singapore", "Malaysia", "Brunei", "Indonesia", "Philippines"],
    "South Pacific": ["Papua New Guinea", "Solomon Islands", "Vanuatu", "New Caledonia", "Fiji", "Samoa", "French Polynesia", "East Timor"]
}

countries = set([c for cc in sub_regions.values() for c in cc] + [c for cc in regions.values() for c in cc])
sub_regions_by_c = {c: r for r, cc in sub_regions.items() for c in cc}
regions_by_c = {c: r for r, cc in sub_regions.items() for c in cc}
countries_acr = {f['properties']['name']: f['id'] for f in counties['features']}

dfc = []
for c in countries:
    if c in countries_acr:
        dfc.append({'id': countries_acr[c], 'country': c, "region": regions_by_c[c], "sub_region": sub_regions_by_c[c]})
dfc = pd.DataFrame(dfc)

mapfig = px.choropleth_mapbox(dfc, geojson=counties, locations='id', color='region', hover_data=['country', 'region', 'sub_region'],
                              # color_continuous_scale="Viridis",
                              mapbox_style="carto-darkmatter",
                              opacity=0.5, zoom=0, center={'lat': 0, 'lon': 0}
                              )
mapfig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0}, showlegend=False)

# Build App
app = Dash(__name__, external_stylesheets=[dbc.themes.DARKLY])

app.layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            html.H1("Architecture Guesser")
        ], width=8),
        dbc.Col(html.Img(src=ai4sc_image, style={'height': '60px'}), width=2),
        dbc.Col(html.Img(src=urost_image, style={'height': '60px'}), width=2),
    ]),
    dbc.Row([
        dbc.Col([
            html.Img(src=pil_image, style={'width': '100%'}, id='example_img')
        ], width=6),
        dbc.Col([
            dbc.Label("Style"),
            html.Section(
                dbc.Row([
                    dbc.Col(
                        dbc.Button([
                            html.Img(src=img, alt=n), html.Br(),
                            html.P(n, style={}),
                        ],
                        color=None,
                        name=n,
                        style={"width": "130px", "height": "160px"},
                        id={"type": "style-selection", "index": n})) for n, img in style_img.items()
                ], className="no-gutters no-padders"),
                style={"width": "100%", "height": "320px", "overflow": "scroll"},
                className="scrollable"),
            dbc.Label("Location"),
            #dcc.Graph(figure=mapfig, id='map', style={'width': '100%', 'height': '30%'}),
            dl.Map([dl.TileLayer(),
                    #dl.GeoJSON(data=counties),
                    dl.LayerGroup(id="layer")], #url=bwtileurl
                 id="map", style={'width': '100%', 'height': '30vh', 'margin': "auto", "display": "block",
                                 #'filter': 'brightness(0.6) invert(1) contrast(3) hue-rotate(200deg) saturate(0.3) brightness(0.7)'},
                                'filter': 'invert(1) hue-rotate(180deg) brightness(.95) contrast(.9)'},
                    maxZoom=4, zoom=1),
            dbc.Label("Epoche"),
            dcc.Slider(0, 2025,
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
                       value=1200, included=False,
                       tooltip={"placement": "bottom", "always_visible": True},
                       id="epoche"
                       ),
            dbc.Row([
                dbc.Col(dbc.Button("GUESS", style={'height': '40px'}, id="GUESS", disabled=True)),
            ]),
            dbc.Label("", id="out1")
        ], width=6)
    ]),
    dbc.Modal([
        dbc.ModalHeader(dbc.ModalTitle("You got 0 points", id="points")),
        dbc.ModalBody([], id="style_body"),
        dbc.ModalFooter([
            dbc.Button("Close",id="close",class_name="ms-auto")
        ])
    ],id="resultmodal"),
    html.Button("1",id="new_run", style={'visibility':'hidden'}, disabled=True) # used as event notifier
], fluid=True)

#@app.callback(
#    Output('GUESS', 'disabled', allow_duplicate=True),
#    Input('map', 'clickData'), prevent_initial_call=True)
#def display_selected_data(clickData):
#    global sel_location
#    if clickData is None: return True
#    sel_location=clickData['points'][0]['location']
#    print(sel_location, sel_style, sel_epoche)
#    return sel_location is None or sel_style is None or sel_epoche is None

@app.callback(
    Output('GUESS', 'disabled', allow_duplicate=True),
    Output("layer", "children"),
    Input('map', 'click_lat_lng'), prevent_initial_call=True)
def display_selected_data(click_lat_lng):
    global sel_location
    if click_lat_lng is None: return True, []
    sel_location=click_lat_lng
    print(sel_location, sel_style, sel_epoche)
    return  sel_location is None or sel_style is None or sel_epoche is None, [dl.Marker(position=click_lat_lng, children=dl.Tooltip("({:.3f}, {:.3f})".format(*click_lat_lng)))]


@app.callback(
    Output('GUESS', 'disabled', allow_duplicate=True),
    Input('epoche', 'value'), prevent_initial_call=True)
def display_selected_epoche(value):
    global sel_epoche
    if value is None: return True
    sel_epoche=value
    return sel_location is None or sel_style is None or sel_epoche is None


@app.callback(
    Output('GUESS', 'active', allow_duplicate=True),
    Output({'type': "style-selection", 'index': ALL}, 'color'),
    Input({"type": "style-selection", "index": ALL}, "n_clicks"),
    Input({"type": "style-selection", "index": ALL}, "name"),
    prevent_initial_call=True
)
def select_style(n, names):
    global sel_style
    if callback_context.triggered_prop_ids:
        for v in callback_context.triggered_prop_ids.values():
            sel_style=v['index']
            styles = ['primary' if sel_style==n else None for n in names]
            return sel_location is None or sel_style is None or sel_epoche is None, styles
    else:
        return True, style_ccc

@app.callback(
    Output("resultmodal", "is_open"),
    Output("new_run", "disabled"), # used as event notifier
    [Input("GUESS", "n_clicks"),
     Input("close", "n_clicks")],
    [State("resultmodal", "is_open"),
     State("new_run", "disabled")],
)
def toggle_modal(n1, n2, is_open, new_run):
    if n1 or n2:
        return not is_open, not new_run
    return is_open, new_run

def tostr(obj):
    if isinstance(obj, str): return obj
    if isinstance(obj, list): return ", ".join(obj)
    else: return str(obj)

@app.callback(
    Output('GUESS', 'disabled', allow_duplicate=True),
    Output("example_img", "src"),
    Output("style_body", "children"),
    Input("new_run", "disabled"), # used as event notifier
    prevent_initial_call=True
)
def select_random_style(new_run):
    global rnd_style
    rnd_style=random.choice(list(architects_by_style.keys()))
    rnd_img=random.choice(list(examples_img.values()))
    print(rnd_style)
    astyle=architects_by_style[rnd_style]["style"]
    aarch=architects_by_style[rnd_style]["architects"]
    print(rnd_style, astyle, aarch)
    return True, rnd_img, [
            html.H3(rnd_style),
            html.Label("Epoche"), html.Br(),
            html.P(f'{astyle["time_range"]} ({astyle["period"]})'),
            html.Label("Location"), html.Br(),
            html.P(f'{tostr(astyle["country"])} ({astyle["continent"]})'),
            html.Label("Description"), html.Br(),
            html.P(astyle["description"]),
            html.Label("Characteristics"), html.Br(),
            html.Ul([html.Li(c) for c in astyle["characteristics"]]),
            html.Label("Examples"), html.Br(),
            html.Ul([html.Li(c) for c in astyle["examples"]]),
            html.Label("Architects"), html.Br(),
            html.Ul([html.Li(c["name"]) for c in aarch]),
    ]


if __name__ == '__main__':
    # run application
    # if 'DEBUG' in os.environ:
    app.run_server(host='0.0.0.0', dev_tools_ui=True, debug=True, dev_tools_hot_reload=True, threaded=True)
# else:
#    app.app.run_server(host='0.0.0.0', debug=False)
