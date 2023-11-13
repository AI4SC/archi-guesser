import json
import dash_leaflet as dl

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
    "Anglo World": "#b3de69",
    "Europe": "#8dd3c7",
    "North Eurasia": "#80b1d3",
    "Central & South America": "#fb8072",
    "Middle East & North Africa": "#ffed6f",
    "Sahel & Sub-Saharan Africa": "#fdb462",
    "South Asia": "#ffffb3",
    "Central Asia": "#B3B9FF",
    "East Asia": "#bc80bd",
    "Southeast Asia & South Pacific": "#fccde5",
    "Antarctica": "#000000",
}

# Load countries by region 
# establishing which countries belong to which cultural region
with open("countries_by_region.json", "tr") as fi:
    countries_by_region = json.load(fi)

# Load region GeoJSON
with open("cultural_regions_simplified.geojson", "tr") as fi:
    regions = json.load(fi)

# Create a GeoJSON layer for each feature (polygon) in the GeoJSON file and assign the color from the dictionary
layers = [
    dl.TileLayer(
        url="http://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}.png",
        attribution="© OpenStreetMap contributors, © CartoDB",
    )
    #dl.TileLayer()
]
for feature in regions["features"]:
    # Replace 'id' with the name of the property that holds your identifiers
    identifier = feature["properties"]["Region"]
    color = region_colors.get(identifier, "#000000")  # default to black if the id is not found in the dictionary
    layers.append(
        dl.GeoJSON(
            data=dict(type="FeatureCollection", features=[feature]),
            options=dict(style=dict(color=color, fillColor=color, fillOpacity=1)),
        )
    )

# Add layer that later contains the map marker
layers.append(dl.LayerGroup(id="layer"))
