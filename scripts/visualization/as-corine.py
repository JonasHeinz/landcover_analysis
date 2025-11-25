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

    # Geodataframe für das Balkendiagramm erstellen
    color_list = [
        ("#006d2c", "#2ca25f"),
        ("#993404", "#d95f0e"),
        ("#d9f0a3", "#ffffcc"),
        ("#253494", "#2c7fb8"),
        ("#bdbdbd", "#d9d9d9"),
        ("#f768a1", "#fa9fb5")
    ]

    # Alle eindeutigen IPCC_AS_IDs sortieren
    ipcc_as_ids = sorted(gdf["IPCC_AS_Id"].unique())

    df_balken_list = []

    for i, ipcc_as_id in enumerate(ipcc_as_ids):
        dark, light = color_list[i]  # falls mehr AS_IDs als Farben, zyklisch
        subset = gdf[gdf["IPCC_AS_Id"] == ipcc_as_id]
        df_temp = pd.DataFrame({
            "IPCC_AS_Id": [ipcc_as_id, ipcc_as_id],
            "Art": ["AS", "AS"],
            "Uebereinstimmende_Klassifikation": ["Wahr", "Falsch"],
            "Farbe": [light, dark],  # hier kannst du je nach Präferenz dark/light tauschen
            "Anzahl": [subset["IPCC_Match"].sum(), len(subset) - subset["IPCC_Match"].sum()],
            "Anteil": [subset["IPCC_Match"].mean(), 1 - subset["IPCC_Match"].mean()]
        })
        df_balken_list.append(df_temp)

    df_balken = pd.concat(df_balken_list, ignore_index=True)
    print("Stats calculated from Geopackage")

    df_balken.to_csv(csv_path, index=False)
    print(f"Stats saved to CSV")

else:
    df_balken = pd.read_csv(csv_path)
    print("Stats loaded from CSV")

# -----------------------------
# 2) UI
# -----------------------------
app_ui = ui.page_fillable(
    ui.layout_columns(
        ui.card(output_widget("karte")),
        ui.card(output_widget("balken")),
        col_widths=(8,4),
    ),
)

# -----------------------------
# 3) Server
# -----------------------------
def server(input, output, session):

    all_layers = {}
    
    ipcc_category_info = {
        1: {"name": "FL","bar_ids": [0, 1]},
        2: {"name": "Zweite", "bar_ids": [2, 3]},
        3: {"name": "Dritte", "bar_ids": [4, 5]},
        4: {"name": "Vierte", "bar_ids": [6, 7]},
        5: {"name": "Fünfte", "bar_ids": [8, 9]},
        6: {"name": "Sechste", "bar_ids": [10, 11]},
    }
    
    category_display = {
        cat_id: {"true": reactive.Value(False), "false": reactive.Value(False)}
        for cat_id in ipcc_category_info.keys()
    }
    
    #Karteneinstellungen
    m = Map(
        center=(46.8, 8.3), #Kartenzentrum
        zoom=8, #Zoomstufe
        layout=Layout(width='100%', height='80vh') # Layout der Kartenbox
    )
    
    # Hintergrundkarte festlegen
    tiles = basemap_to_tiles(basemaps.CartoDB.Positron)
    m.add(tiles)
    
    # @reactive.Effect
    # @reactive.event(input.action_button1)
    # def counter():
    #     for layer0, layer1 in all_layers:
    #         m.add(layer0)
    #         m.add(layer1)
    #     #return f"Button wurde geklickt! Anzahl Klicks: {input.action_button()}"
    
    # Balkendiagram
    @output
    @render_plotly
    def balken():
        fig = go.Figure([go.Bar(x=df_balken["Anteil"], y=df_balken["IPCC_AS_Id"],orientation='h', marker_color=df_balken["Farbe"])])
        fig.update_layout(barmode='stack')
        fig.update_xaxes(categoryorder='total ascending')

        w = go.FigureWidget(fig)
        w.data[0].on_click(on_point_click)

        return w
    
    #@reactive.Effect
    # Reaktion auf den Klick in das Balkendiagramm
    def on_point_click(trace, points, state): 
        
        #for ipcc_category_id, ipcc_category in ipcc_category_info.items():

        for ipcc_category, ipcc_category_values in ipcc_category_info.items():
                # Layer-Paar aus all_layers
            idx = points.point_inds[0]
            layer0, layer1 = all_layers[ipcc_category]  # assuming all_layers in order 1..6
        
            if idx == ipcc_category_values["bar_ids"][0]:
                if category_display[ipcc_category]["true"].get():
                    m.remove(layer1)
                    category_display[ipcc_category]["true"].set(False)
                else:
                    m.add(layer1)
                    category_display[ipcc_category]["true"].set(True)

            if idx == ipcc_category_values["bar_ids"][1]:
                if category_display[ipcc_category]["false"].get():
                    m.remove(layer0)
                    category_display[ipcc_category]["false"].set(False)
                else:
                    m.add(layer0)
                    category_display[ipcc_category]["false"].set(True)
            
    
    
    
    
    
    
    
    @output
    @render_widget
    def karte():
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

        for ipcc_as_id, path, colors in zip(ipcc_category_info.keys(), tif_paths, color_list):
            layer0 = tif_to_png_overlay_value(path, colors, value_to_show=0)
            layer1 = tif_to_png_overlay_value(path, colors, value_to_show=1)
            layer0.visible = True
            layer1.visible = True
            
            # Speichern nach ID
            all_layers[ipcc_as_id] = (layer0, layer1)
            

        return m

# -----------------------------
# 4) App starten
# -----------------------------
app = App(app_ui, server)


# ----------------------------------------------
# Funktion zum Erzeugen eines Karten Overlay PNG
# ----------------------------------------------
def tif_to_png_overlay_value(path, colors, value_to_show=255, upscale=2):

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
