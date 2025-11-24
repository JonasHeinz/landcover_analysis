# Start with: python -m shiny run -r scripts/visualization/as-corine.py

import os
os.environ['PROJ_LIB'] = r"C:\Users\LeonardoS\miniconda3\envs\corine\Library\share\proj"

import geopandas as gpd
import json
import pandas as pd
import plotly.graph_objects as go
from scripts import DATA_DIR
from shiny import App, ui, reactive
from shinywidgets import output_widget, render_plotly,render_widget
from ipyleaflet import Map, GeoJSON
from shapely.geometry import box
from ipyleaflet import Map, ImageOverlay
import rasterio
from rasterio.warp import transform_bounds
import numpy as np
from PIL import Image
import io, base64
from io import BytesIO
from rasterio.warp import transform_bounds
from ipyleaflet import Map, TileLayer
from shiny import App, ui, reactive
from shinywidgets import output_widget, render_widget
from ipyleaflet import Map, TileLayer
import rasterio
from rasterio.warp import calculate_default_transform, reproject, Resampling
import numpy as np
from PIL import Image
from io import BytesIO
import base64
from scripts import DATA_DIR
from ipywidgets import Layout
from ipyleaflet import Map
from ipyleaflet import basemaps, basemap_to_tiles

# -----------------------------
# 1) Daten laden
# -----------------------------
gdf = gpd.read_file(DATA_DIR / "analysis/corine/2018/result_center_point.gpkg") 
gdf = gdf.to_crs(epsg=3857)
print("Initial Data loaded")

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
print("Initial Data processed")

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
    
    # Balkendiagram
    @output
    @render_plotly
    def balken():
        fig = go.Figure([go.Bar(x=df_balken["Anteil"], y=df_balken["Art"],orientation='h', marker_color=df_balken["Farbe"])])
        fig.update_layout(barmode='stack')
        fig.update_xaxes(categoryorder='total ascending')

        w = go.FigureWidget(fig)
        # w.data[0].on_click(on_point_click)

        return w
    
    # Reaktion auf den Klick in das Balkendiagramm
    # def on_point_click(trace, points, state): 

    #     if points.point_inds[0] in [0,2]:
    #         selected_category.set("True") 

    #     if points.point_inds[0] in [1,3]:
    #         selected_category.set("False") 
            
    #     if selected_category.get() == "True":
    #         karte_fig.data[0].visible = True
    #         karte_fig.data[1].visible = "legendonly"
    #     elif selected_category.get() == "False":
    #         karte_fig.data[0].visible = "legendonly"
    #         karte_fig.data[1].visible = True
    #     else:
    #         karte_fig.data[0].visible = True
    #         karte_fig.data[1].visible = True
    

    @output
    @render_widget
    def karte():
        
        #Karteneinstellungen
        m = Map(
            center=(46.8, 8.3), #Kartenzentrum
            zoom=8, #Zoomstufe
            layout=Layout(width='100%', height='80vh') # Layout der Kartenbox
        )

        # Raster als ImageOverlay hinzufügen
        layer1 = tif_to_png_overlay(DATA_DIR / "analysis/corine/2018/center_point_raster/ipcc_category_1.tif",("#2ca25f", "#006d2c"))
        layer2 = tif_to_png_overlay(DATA_DIR / "analysis/corine/2018/center_point_raster/ipcc_category_2.tif",("#d95f0e", "#993404"))
        layer3 = tif_to_png_overlay(DATA_DIR / "analysis/corine/2018/center_point_raster/ipcc_category_3.tif", ("#ffffcc", "#d9f0a3"))
        layer4 = tif_to_png_overlay(DATA_DIR / "analysis/corine/2018/center_point_raster/ipcc_category_4.tif", ("#2c7fb8", "#253494"))
        layer5 = tif_to_png_overlay(DATA_DIR / "analysis/corine/2018/center_point_raster/ipcc_category_5.tif", ("#d9d9d9", "#bdbdbd"))
        layer6 = tif_to_png_overlay(DATA_DIR / "analysis/corine/2018/center_point_raster/ipcc_category_6.tif", ("#fa9fb5", "#f768a1"))

        # Raster Overlays zur Karte hinzufügen
        m.add(layer1)
        m.add(layer2)
        m.add(layer3)
        m.add(layer4)
        m.add(layer5)
        m.add(layer6)
        
        # Hintergrundkarte festlegen
        tiles = basemap_to_tiles(basemaps.CartoDB.Positron)
        m.add(tiles)
        
        return m

# -----------------------------
# 4) App starten
# -----------------------------
app = App(app_ui, server)


# ----------------------------------------------
# Funktion zum Erzeugen eines Karten Overlay PNG
# ----------------------------------------------
def tif_to_png_overlay(path, colors, upscale=1):

    # Laden der TIF Datein im Leaflet Koordinatensystem
    with rasterio.open(path) as src:
        arr = src.read(1)
        minx, miny, maxx, maxy = transform_bounds(src.crs, "EPSG:4326", *src.bounds)

    # RGBA-Arrays mit den angegebenen Farben erstellen
    img = np.zeros((arr.shape[0], arr.shape[1], 4), dtype=np.uint8)
    light = tuple(int(colors[0].lstrip("#")[i:i+2], 16) for i in (0,2,4))
    dark  = tuple(int(colors[1].lstrip("#")[i:i+2], 16) for i in (0,2,4))

    # Festlegen der Farben und der Transparent für das Karten Overlay PNG
    img[arr == 0, :3] = dark
    img[arr == 1, :3] = light
    img[arr == 255, 3] = 0   
    img[arr != 255, 3] = 255

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
