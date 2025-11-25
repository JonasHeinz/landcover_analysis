# Start with: python -m shiny run -r scripts/visualization/as-corine.py

import os
os.environ['PROJ_LIB'] = r"C:\Users\LeonardoS\miniconda3\envs\corine\Library\share\proj"

import base64
import geopandas as gpd
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from io import BytesIO
from ipyleaflet import Map, ImageOverlay, basemaps, basemap_to_tiles
from ipywidgets import Layout
from PIL import Image
import rasterio
from rasterio.warp import transform_bounds
from scripts import DATA_DIR
from shiny import App, ui, reactive
from shinywidgets import output_widget, render_plotly, render_widget

# -----------------------------
# 1) Daten laden
# -----------------------------

csv_path = DATA_DIR / "analysis/corine/2018/stats_center_point.csv"

if not csv_path.exists():
    gdf = gpd.read_file(DATA_DIR / "analysis/corine/2018/result_center_point.gpkg") 
    gdf = gdf.to_crs(epsg=3857)
    print("Initial Data loaded from Geopackage")

    # # Geodataframe und Geojson für True und False erstellen
    # gdf["IPCC_Match"] = gdf["IPCC_Match"].astype(bool)
    # gdf_true = gdf[gdf["IPCC_Match"] == True]
    # gdf_false = gdf[gdf["IPCC_Match"] == False]

    # gjson = json.loads(gdf.to_json())
    # gjson_true = json.loads(gdf_true.to_json())
    # gjson_false = json.loads(gdf_false.to_json())

    # Geodataframe für das Balkendiagramm erstellen
    df_balken = pd.DataFrame({
        "Art": ["AS","AS"],
        "Uebereinstimmende_Klassifikation": ["Wahr", "Falsch"],
        "Farbe":["#fee0d2","#de2d26"],
        "Anzahl": [gdf["IPCC_Match"].sum(), len(gdf) - gdf["IPCC_Match"].sum()],
        "Anteil": [gdf["IPCC_Match"].sum()/len(gdf), (len(gdf)-gdf["IPCC_Match"].sum())/len(gdf)]
    })
    print("Stats calculated from Geopackage")

    df_balken.to_csv(csv_path, index=False)
    print(f"Stats saved to CSV")

else:
    df_balken = pd.read_csv(csv_path)
    print("Stats loaded from CSV")

# -----------------------------
# 2) UI
# -----------------------------
app_ui = ui.page_fluid( 
    ui.h2("Datendarstellung"),
    output_widget("balken"), 
    output_widget("karte")
)

# -----------------------------
# 3) Server
# -----------------------------
def server(input, output, session):
    
#     karte_fig = go.FigureWidget()

#     # True Punkte darstellen
#     karte_fig.add_choropleth(
#         geojson=gjson_true,
#         locations=gdf_true.index,
#         z = gdf_true["IPCC_Match"].map({False:0, True:1}),
#         colorscale=[[0, "white"], [1, "white"]],
#         showscale=False,
#         name="True"
#     )

#     # False Punkte darstellen
#     karte_fig.add_choropleth(
#         geojson=gjson_false,
#         locations=gdf_false.index,
#         z = gdf_false["IPCC_Match"].map({False:0, True:1}),
#         colorscale=[[0, "red"], [1, "red"]],
#         showscale=False,
#         name="False"
#     )
    
#     # Position der Karte auf die Daten zoomen
#     karte_fig.update_geos(
#         fitbounds="locations",
#         visible=False
#     )
    

    # Ausgewählte Kategorie speichern
    selected_category = reactive.Value(None)
    all_layers = []
    
    # Balkendiagram
    @output
    @render_plotly
    def balken():
        fig = go.Figure([go.Bar(x=df_balken["Anteil"], y=df_balken["Art"],orientation='h', marker_color=df_balken["Farbe"])])
        fig.update_layout(barmode='stack')
        fig.update_xaxes(categoryorder='total ascending')

        w = go.FigureWidget(fig)
        w.data[0].on_click(on_point_click)

        return w
    
    # Reaktion auf den Klick in das Balkendiagramm
    def on_point_click(trace, points, state): 
        
        if points.point_inds[0] == 0:
            selected_category.set("True")   # Wert=0 sichtbar
        elif points.point_inds[0] == 1:
            selected_category.set("False")  # Wert=1 sichtbar
        else:
            selected_category.set(None)     # alles sichtbar

        # Sichtbarkeit der Layer steuern
        for layer0, layer1 in all_layers:
            if selected_category.get() == "True":
                layer0.visible = False
                layer1.visible = True
            elif selected_category.get() == "False":
                layer0.visible = True
                layer1.visible = False
            else:
                layer0.visible = True
                layer1.visible = True
    
    @output
    @render_widget
    def karte():
        
        #Karteneinstellungen
        m = Map(
            center=(46.8, 8.3), #Kartenzentrum
            zoom=8, #Zoomstufe
            layout=Layout(width='100%', height='80vh') # Layout der Kartenbox
        )
        
        # Hintergrundkarte festlegen
        tiles = basemap_to_tiles(basemaps.CartoDB.Positron)
        m.add(tiles)
        

        # Farben für jede Kategorie (dunkel / hell)
        color_list = [
            ("#006d2c", "#2ca25f"),
            ("#993404", "#d95f0e"),
            ("#d9f0a3", "#ffffcc"),
            ("#253494", "#2c7fb8"),
            ("#bdbdbd", "#d9d9d9"),
            ("#f768a1", "#fa9fb5")
        ]

        tif_paths = [
            DATA_DIR / f"analysis/corine/2018/center_point_raster/ipcc_category_{i}.tif"
            for i in range(1,7)
        ]

        # Funktion, die die Overlays verzögert hinzufügt

        for path, colors in zip(tif_paths, color_list):
            layer0 = tif_to_png_overlay_value(path, colors, value_to_show=0)
            layer1 = tif_to_png_overlay_value(path, colors, value_to_show=1)
            layer0.visible = True
            layer1.visible = True
            m.add(layer0)
            m.add(layer1)
            all_layers.append((layer0, layer1))

        return m

# -----------------------------
# 4) App starten
# -----------------------------
app = App(app_ui, server)


# ----------------------------------------------
# Funktion zum Erzeugen eines Karten Overlay PNG
# ----------------------------------------------
def tif_to_png_overlay_value(path, colors, value_to_show=255, upscale=1):

    # Laden der TIF Datein im Leaflet Koordinatensystem
    with rasterio.open(path) as src:
        arr = src.read(1)
        minx, miny, maxx, maxy = transform_bounds(src.crs, "EPSG:4326", *src.bounds)

    img = np.zeros((arr.shape[0], arr.shape[1], 4), dtype=np.uint8)
    dark  = tuple(int(colors[0].lstrip("#")[i:i+2], 16) for i in (0,2,4))
    light = tuple(int(colors[1].lstrip("#")[i:i+2], 16) for i in (0,2,4))

    # Festlegen der Farben und der Transparent für das Karten Overlay PNG
    img[arr == 0, :3] = dark
    img[arr == 1, :3] = light
    img[arr == 255, 3] = 0   
    img[arr != 255, 3] = 255
    
    if(value_to_show==0):
        img[arr == 1, 3] = 0   
    
    elif(value_to_show==1):
        img[arr == 0, 3] = 0  
    
    # Karten Overlay PNG erstellen und vergrössern
    pil = Image.fromarray(img, mode="RGBA")
    pil = pil.resize((arr.shape[1]*upscale, arr.shape[0]*upscale), Image.NEAREST)
    buffer = BytesIO()
    pil.save(buffer, format="PNG")
    encoded = base64.b64encode(buffer.getvalue()).decode()

    # Berechnen der Boundingbox für Leaflet
    leaflet_bounds = ((miny, minx), (maxy, maxx))

    # Bild für die Leaflet Karte zurückgeben
    return ImageOverlay(
        url="data:image/png;base64," + encoded,
        bounds=leaflet_bounds
    )
