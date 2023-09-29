import pandas as pd
import plotly.express as px
import numpy as np
import plotly.graph_objects as go

pd.options.display.max_colwidth = 150

#Establish list of terms for each style with more fitting format than originally
style_terms = {
    "Ancient Egyptian": [
        "pyramids", "temples", "monumental", "ornate", "hieroglyphics",
        "sandstone", "symmetry", "vast", "impressive"
    ],
    "Ancient Roman": [
        "columns", "symmetrical", "arches", "vaults", "Doric", "Ionic",
        "elegant", "enduring"
    ],
    "Romanesque":
    ["rounded arches", "pillars", "thick walls", "carvings", "symmetrical"],
    "Gothic": [
        "pointed arches", "ribbed vaults", "flying buttresses", "ornate",
        "verticality", "towering spires", "majestic cathedrals"
    ],
    "Renaissance": [
        "domes", "arches", "symmetry", "proportion", "elegant", "ornate",
        "classical", "grand"
    ],
    "Baroque": [
        "ornate", "extravagant", "curved lines", "grandeur", "opulence",
        "elaborate ornamentation"
    ],
    "Neoclassical": [
        "classical forms", "symmetry", "columns", "domes", "pediments",
        "simple", "elegant", "harmonious"
    ],
    "Victorian": [
        "mansions", "Gothic revival", "symmetry", "ornate", "intricate",
        "historic"
    ],
    "Art Nouveau": [
        "decorative", "asymmetrical", "organic", "floral motifs",
        "stained glass", "Japanese art"
    ],
    "Art Deco": [
        "geometric shapes", "bold colors", "streamlined", "decorative motifs",
        "modernist"
    ],
    "Brutalism": [
        "concrete", "angular", "functional", "monolithic", "stark",
        "industrial", "austere", "utilitarian"
    ],
    "Bauhaus": [
        "geometric shapes", "minimalism", "industrial materials", "functional",
        "modernism", "clean", "sleek"
    ],
    "Colonial":
    ["columns", "arches", "grand", "symmetrical", "decorative", "historical"],
    "Colonial Revival": [
        "traditional", "symmetrical", "nostalgic", "historicist",
        "neoclassical", "Georgian", "patriotic"
    ],
    "Mesoamerican": [
        "pyramids", "hierarchical", "symbolic", "monumental", "geometrical",
        "ornate"
    ],
    "Constructivism": [
        "unique spaces", "sustainable", "innovative", "dynamic", "holistic",
        "environmentally conscious"
    ],
    "Muscovite":
    ["onion domes", "Kremlin", "ornate", "medieval", "iconic", "distinctive"],
    "Chinese Imperial": [
        "roof tiles", "eaves", "courtyards", "colorful", "symmetric",
        "traditional", "spiritual"
    ],
    "Gupta": [
        "ornate", "symmetrical", "Sanskritized", "Hindu", "Buddhist",
        "magnificent"
    ],
    "Edo Period": [
        "wooden", "minimalist", "sliding doors", "tatami mats",
        "high-pitched roof"
    ],
    "Khmer Empire": [
        "temples", "step pyramids", "ornate", "symbolic", "monumental",
        "mystical"
    ],
    "Timurid Period": [
        "vibrant tiles", "glazed bricks", "geometric motifs", "majestic domes",
        "monumental"
    ],
    "Modern Islamic": [
        "clean lines", "geometric shapes", "innovative materials",
        "contemporary", "culturally influenced"
    ],
    "Mud Brick": [
        "primitive", "sustainable", "vernacular", "low-tech", "earthy",
        "organic", "community-oriented"
    ],
    "Stilt House":
    ["stilts", "elevated", "bamboo flooring", "thatched roof", "eco-friendly"],
    "Indo-Saracenic": [
        "fusion", "Islamic", "Mughal", "Gothic", "Hindu", "Victorian",
        "ornate", "fusion"
    ],
    "Contemporary":
    ["minimal", "innovative", "sleek", "geometric", "dynamic", "experimental"],
    "Thai": ["pagodas", "wood", "ornate carvings", "vibrant", "spiritual"],
    "Persian": [
        "domes", "minarets", "courtyards", "tile work", "ornate", "geometric",
        "historic"
    ],
    "Swahili": ["traditional", "coastal", "Arabic-influenced", "vibrant"]
}


def read_csv_file(csv_filename):
  """
    Read a CSV file with a custom separator and return its content as a pandas DataFrame.
    """
  try:
    # Create empty lists to store data
    styles = []
    descriptions = []

    # Read file line by line and split at the first comma
    with open(csv_filename, 'r', encoding = 'cp850') as f:
      next(f)  # Skip the first line

      for line in f:
        if ',' not in line:
          continue
        line.replace('"', '')
        filepath, description = line.split(',', 1)

        # Extract the substring between "building_in_" and "_architecture_"
        start_index = filepath.find("building_in_")
        end_index = filepath.find("_architecture_")

        if start_index != -1 and end_index != -1:
          # Adjust the start_index to account for the length of "building_in_"
          style = filepath[start_index + 12:end_index]
          #replace any underscores
          style = style.replace("_", " ")
          styles.append(style)
          descriptions.append(description.strip('"'))
        else:
          print(f"Skipping line due to missing style pattern: {line.strip()}")
          continue

    # Convert lists to DataFrame
    df_csv = pd.DataFrame({'filepath': styles, 'description': descriptions})

    print(f"Successfully read the CSV file: {csv_filename}")
    return df_csv

  except Exception as e:
    print(f"Error reading the CSV file: {csv_filename}. Error: {e}")
    return None


def read_geojson_file(geojson_filename):
  """
    Read a GeoJSON file and return its content as a pandas DataFrame.
    """
  try:
    df_geojson = pd.read_json(geojson_filename)
    print(f"Successfully read the GeoJSON file: {geojson_filename}")
    return df_geojson
  except Exception as e:
    print(f"Error reading the GeoJSON file: {geojson_filename}. Error: {e}")
    return None


if __name__ == "__main__":
  csv_path = "describes.csv"
  geojson_path = "architect_styles_adjusted.json"

  df_describes = read_csv_file(csv_path)
  df_styles = read_geojson_file(geojson_path)

  # Create lists to store styles and their counts
  styles = []
  count_name = []
  count_terms = []
  misattribution_matrix = {key: {inner_key: 0 for inner_key in df_styles.keys()} for key in df_styles.keys()}

  for key in df_styles.keys():
    filtered_rows = df_describes.loc[df_describes.iloc[:, 0] == key]

    # Get the relevant part of the name and the major elements (terms) for each style
    relevant_words = df_styles[key]['relevant']
    major_elements = style_terms[key]

    # Check for occurrences of the relevant name-part
    matches = filtered_rows.iloc[:, 1].str.contains('|'.join(relevant_words),
                                                    case=False,
                                                    na=False)
    matching_rows_count = matches.sum()

    # Check for occurrences of any of the descirption terms
    major_element_matches = filtered_rows.iloc[:, 1].str.contains(
        '|'.join(major_elements), case=False, na=False)
    major_element_matching_rows_count = major_element_matches.sum()
    
    #Check for misattributions to other styles
    for other_key in df_styles.keys():
      if other_key == key:
        misattribution_matrix[key][other_key] = float("NaN")
        continue
      other_style = df_styles[other_key]['relevant']
      misidentification_count = filtered_rows.iloc[:, 1].str.contains(
            '|'.join(other_style), case=False, na=False).sum()
      misattribution_matrix[key][other_key] += misidentification_count

    styles.append(key)
    count_name.append(matching_rows_count)
    count_terms.append(major_element_matching_rows_count) 

  # Sort styles based on count_name
  sorted_indices = sorted(range(len(count_name)),
                          key=lambda k: count_name[k],
                          reverse=True)
  styles = [styles[i] for i in sorted_indices]
  count_name = [count_name[i] for i in sorted_indices]
  count_terms = [count_terms[i] for i in sorted_indices]

  df = pd.DataFrame({
    'styles': reversed(styles),
    'count_name': reversed(count_name),
    'count_terms': reversed(count_terms)
  })

  # Bar chart
  topN = 25
  figw = 600
  figh = 600
  figm = dict(l=10, r=10, b=10, t=10, pad=4)
  figlBR = dict(orientation="h", yanchor="top", y=1.10, xanchor="right", x=0.99)
  figfnt = dict(size=14)

  fig = px.bar(df, 
    x=['count_terms', 'count_name'], y='styles', barmode="group", orientation='h',
    color_discrete_sequence=['#FFD580', 'purple']
  )

  # Updating legend names and bar labels
  for i, trace in enumerate(fig.data):
    if 'count_terms' in trace.name:
        trace.name = "Elements"
    elif 'count_name' in trace.name:
        trace.name = "Name"

  # Update axis titles
  fig.update_layout(
    legend=figlBR,
    width=figw,
    height=figh,
    margin=figm,
    yaxis_tickmode='linear',
    font=figfnt,
    yaxis_title="Styles",
    xaxis_title="Occurrences in Descriptions",
    legend_title_text="Occurrence Type",
    legend_traceorder="reversed"
  )
  print("Printing...")
  fig.write_image("StyleDescriptions.pdf")
  #fig.write_html('first_figure.html', auto_open=True)


  # Matrix-style visualization
  df_misattributions = pd.DataFrame(misattribution_matrix)
  
  custom_color_scale = ["#E5ECF5", "Purple"] ##512A8C
  fig = px.imshow(df_misattributions.T,
    labels=dict(x="Mistaken For", y="True Style", color="Count"),
    x=df_misattributions.index,
    y=df_misattributions.columns,
    color_continuous_scale=custom_color_scale)

  # Vertical gridlines
  for i in range(len(styles)+1):
    fig.add_shape(
        go.layout.Shape(
            type="line",
            x0=i-0.5, x1=i-0.5,
            y0=-0.5, y1=len(styles)-0.5,
            line=dict(color="lightgray")
        )
  )
  # Horizontal gridlines
  for j in range(len(styles)+1):
    fig.add_shape(
        go.layout.Shape(
            type="line",
            x0=-0.5, x1=len(styles)-0.5,
            y0=j-0.5, y1=j-0.5,
            line=dict(color="lightgray")
        )
  )

  # Similar formatting to bar chart
  topN = 25
  figw = 650
  figh = 600
  figm = dict(l=10, r=10, b=10, t=10, pad=4)
  figfnt = dict(size=12)
  fig.update_layout(
    xaxis_side="top",
    width=figw,
    height=figh,
    margin=figm,
    yaxis_tickmode='linear',
    font=figfnt,
    coloraxis_colorbar_thickness=12
    xaxis_showgrid=True, 
    yaxis_showgrid=True,
    #xaxis_tickangle=45
  )
  
  fig.write_image("misattributions.pdf")
  #fig.write_html('misattributions.html', auto_open=True)