# Start with: python -m shiny run -r scripts/visualization/ipcc_shiny.py
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
import os
os.environ['PROJ_LIB'] = r"C:\Users\LeonardoS\miniconda3\envs\corine\Library\share\proj"


# -----------------------------
# 1) Daten laden
# -----------------------------

# Kategorien inkl. Farben zusammenfassen
ipcc_category_info = {
    1: {"name": "Forest Land", "bar_ids": [0, 1], "colors": ("#006d2c", "#2ca25f")},
    2: {"name": "Cropland", "bar_ids": [2, 3], "colors": ("#993404", "#d95f0e")},
    3: {"name": "Grasslands", "bar_ids": [4, 5], "colors": ("#d9f0a3", "#ffffcc")},
    4: {"name": "Wetlands", "bar_ids": [6, 7], "colors": ("#253494", "#2c7fb8")},
    5: {"name": "Settlements", "bar_ids": [8, 9], "colors": ("#bdbdbd", "#d9d9d9")},
    6: {"name": "Other Land", "bar_ids": [10, 11], "colors": ("#f768a1", "#fa9fb5")},
}

# Verfügbare Jahre pro Datensatz für Select-Input
dataset_years = {
    "corine_vector": [2012, 2018],
    "corine_raster": [2012, 2018],
    "worldcover": [2020, 2021],
    "av": [2025]
}


def get_tif_paths(dataset, year, method):
    base = DATA_DIR / f"shiny/{dataset}/{year}/{method}"
    return [
        base / f"ipcc_category_{i}.tif"
        for i in range(1, 7)
    ]


# -----------------------------
# 2) UI
# -----------------------------
legend_colors = {"True": "#bdbdbd", "False": "#666666"}
app_ui = ui.page_fillable(
    ui.card(
        ui.layout_columns(
            ui.input_select(
                id="select_dataset",
                label="Wähle einen Datensatz:",
                choices={"corine_vector": "CORINE Land Cover Vektor", "corine_raster": "CORINE Land Cover Raster",
                         "worldcover": "ESA WorldCover", "av": "Amtliche Vermessung"},

            ),
            ui.input_select(
                id="select_year",
                label="Wähle das Jahr:",
                choices=[],
            ),
            ui.input_select(
                id="select_method",
                label="Wähle die Methode:",
                choices={"cell_center": "Cell Center",
                         "max_area": "Max Area"},
            ),
                        style="margin:0px;"
        )
    ),



    ui.layout_columns(
        ui.card(output_widget("karte")),
        ui.card(
            ui.tags.div(
                ui.tags.div(
                    # Legendensymbole
                    ui.tags.span(
                        style=f"display:inline-block;width:15px;height:15px;background-color:{legend_colors['True']};margin-right:5px;"),
                    ui.tags.span("hell = korrekt", style="margin-right:15px;"),
                    ui.tags.span(
                        style=f"display:inline-block;width:15px;height:15px;background-color:{legend_colors['False']};margin-right:5px;"),
                    ui.tags.span("dunkel = falsch", style="margin-right:15px;"),
                ),
                style="text-align:center;margin:0px;"
            ),
            output_widget("balken")
        ),

        col_widths=(8, 4),
    )
)

# -----------------------------
# 3) Server
# -----------------------------


def server(input, output, session):

    all_layers = {}

    category_display = {
        cat_id: {"true": reactive.Value(False), "false": reactive.Value(False)}
        for cat_id in ipcc_category_info.keys()
    }

    # Karteneinstellungen
    m = Map(
        center=(46.8, 8.3),  # Kartenzentrum
        zoom=8,  # Zoomstufe
        layout=Layout(width='100%', height='80vh')  # Layout der Kartenbox
    )
    m.add(basemap_to_tiles(basemaps.CartoDB.Positron))

    # Balkendiagramm
    @output
    @render_plotly
    def balken():
        # CSV dynamisch laden
        dataset = input.select_dataset()
        year = input.select_year()
        method = input.select_method()

        if not dataset or not year or not method:
            return pd.DataFrame()

        match dataset:
            case "av":
                statsfile=f"AV-{year}-AS-{method}-stats.csv"
            case "corine_raster":
                statsfile=f"CORINER-{year}-AS-{method}-stats.csv"
            case "corine_vector":
                statsfile=f"CORINEV-{year}-AS-{method}-stats.csv"
            case "worldcover":
                statsfile=f"WC-{year}-AS-{method}-stats.csv"
            case _:
                statsfile=""
                raise ValueError("Unbekannter Datensatz")

        csv_path = (
            DATA_DIR /
            f"shiny/{dataset}/{year}/{method}/{statsfile}"
        )
        df_balken = pd.read_csv(csv_path)
        df_balken["Anteil"] = df_balken["Anteil"]

        # Balkendiagramm dynamisch darstellen
        fig = go.Figure([go.Bar(
            x=df_balken["Anteil"],
            y=df_balken["IPCC_AS_Name"],
            orientation='h',
            marker_color=df_balken["Farbe"]
        )])
        fig.update_xaxes(tickformat=".0%")
        fig.update_layout(barmode='stack')
        fig.update_xaxes(categoryorder='total ascending')
        

        w = go.FigureWidget(fig)
        w.data[0].on_click(on_point_click)
        w._config = {"displayModeBar": False} 
        return w

    def on_point_click(trace, points, state):
        idx = points.point_inds[0]
        for ipcc_category, cat_info in ipcc_category_info.items():
            layer0, layer1 = all_layers[ipcc_category]
            if idx == cat_info["bar_ids"][0]:  # True
                if category_display[ipcc_category]["true"].get():
                    m.remove(layer1)
                    category_display[ipcc_category]["true"].set(False)
                else:
                    m.add(layer1)
                    category_display[ipcc_category]["true"].set(True)
            if idx == cat_info["bar_ids"][1]:  # False
                if category_display[ipcc_category]["false"].get():
                    m.remove(layer0)
                    category_display[ipcc_category]["false"].set(False)
                else:
                    m.add(layer0)
                    category_display[ipcc_category]["false"].set(True)

    @output
    @render_widget
    def karte():
        # Raster dynamisch laden
        dataset = input.select_dataset()
        year = input.select_year()
        method = input.select_method()
        # Karte darstellen

        # Alte Layer entfernen
        for layers in all_layers.values():
            for layer in layers:
                if layer in m.layers:
                    m.remove(layer)
        all_layers.clear()
        # Status zurücksetzen
        for cat_id in category_display.keys():
            category_display[cat_id]["true"].set(False)
            category_display[cat_id]["false"].set(False)

        tif_paths = get_tif_paths(dataset, year, method)

        for ipcc_as_id, path in zip(ipcc_category_info.keys(), tif_paths):
            colors = ipcc_category_info[ipcc_as_id]["colors"]
            layer0 = tif_to_png_overlay_value(path, colors, value_to_show=0)
            layer1 = tif_to_png_overlay_value(path, colors, value_to_show=1)
            layer0.visible = True
            layer1.visible = True
            all_layers[ipcc_as_id] = (layer0, layer1)
        return m

    @reactive.Effect
    @reactive.event(input.select_dataset)
    def update_years():
        selected = input.select_dataset()
        years = dataset_years.get(selected, [])

        # Jahre im Dropdown ersetzen
        ui.update_select(
            "select_year",
            choices=years,
            selected=years[0] if years else None
        )


# -----------------------------
# 4) App starten
# -----------------------------
app = App(app_ui, server)

# -----------------------------
# Overlay-Funktion
# -----------------------------


def tif_to_png_overlay_value(path, colors, value_to_show=255, upscale=2):
    with rasterio.open(path) as src:
        arr = src.read(1)
        minx, miny, maxx, maxy = transform_bounds(
            src.crs, "EPSG:4326", *src.bounds)

    img = np.zeros((arr.shape[0], arr.shape[1], 4), dtype=np.uint8)
    dark = tuple(int(colors[0].lstrip("#")[i:i+2], 16) for i in (0, 2, 4))
    light = tuple(int(colors[1].lstrip("#")[i:i+2], 16) for i in (0, 2, 4))

    img[arr == 0, :3] = dark
    img[arr == 1, :3] = light
    img[arr == 255, 3] = 0
    img[arr != 255, 3] = 255

    if value_to_show == 0:
        img[arr == 1, 3] = 0
    elif value_to_show == 1:
        img[arr == 0, 3] = 0

    pil = Image.fromarray(img, mode="RGBA")
    pil = pil.resize(
        (arr.shape[1]*upscale, arr.shape[0]*upscale), Image.NEAREST)
    buffer = BytesIO()
    pil.save(buffer, format="PNG")
    encoded = base64.b64encode(buffer.getvalue()).decode()
    leaflet_bounds = ((miny, minx), (maxy, maxx))

    return ImageOverlay(
        url="data:image/png;base64," + encoded,
        bounds=leaflet_bounds
    )
