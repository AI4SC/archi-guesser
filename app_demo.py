

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

style_img = {}
for fn in os.listdir('styles120'):
    if fn.endswith(".png"):
        img = Image.open(os.path.join('styles120', fn))
        style_img[fn.replace('.png', '').replace('_', ' ').title()] = img

style_img = {i: style_img[i] for i in sorted(list(style_img.keys()))}

if demo_mode:
    demo_keys=list(set([s["sel_style"] for s in demo_steps]))
    style_img= {k:style_img[k] for k in demo_keys}


for demostep in demo_steps:
    if demostep['rnd_style'] not in architects_by_style: print("MISSING rnd_style", demostep['rnd_style'])
    if demostep['sel_style'] not in style_img: print("MISSING sel_style", demostep['sel_style'])
    if demostep['rnd_img'] not in examples_img: print("MISSING rnd_img", demostep['rnd_img'])


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
        Input('demo-interval', 'n_intervals'),
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
