import os
os.environ['PROJ_LIB'] = r"C:\Users\LeonardoS\miniconda3\envs\corine\Library\share\proj"

import geopandas as gpd
import json
import pandas as pd
import plotly.graph_objects as go
from scripts import DATA_DIR
from shiny import App, ui, reactive
from shinywidgets import output_widget, render_plotly

# -----------------------------
# 1) Daten laden
# -----------------------------
gdf = gpd.read_file(DATA_DIR / "analysis/corine/2018/result_zug.gpkg") 
gdf = gdf.to_crs(epsg=4326)

# Geodataframe und Geojson für True und False erstellen
gdf["IPCC_Match"] = gdf["IPCC_Match"].astype(bool)
gdf_true = gdf[gdf["IPCC_Match"] == True]
gdf_false = gdf[gdf["IPCC_Match"] == False]

gjson = json.loads(gdf.to_json())
gjson_true = json.loads(gdf_true.to_json())
gjson_false = json.loads(gdf_false.to_json())

# Geodataframe für das Balkendiagramm erstellen
df_balken = pd.DataFrame({
    "Art": ["AS","AS"],
    "Uebereinstimmende_Klassifikation": ["Wahr", "Falsch"],
    "Farbe":["#fee0d2","#de2d26"],
    "Anzahl": [gdf["IPCC_Match"].sum(), len(gdf) - gdf["IPCC_Match"].sum()],
    "Anteil": [gdf["IPCC_Match"].sum()/len(gdf), (len(gdf)-gdf["IPCC_Match"].sum())/len(gdf)]
})

# -----------------------------
# 2) UI
# -----------------------------
app_ui = ui.page_fluid(
    ui.h2("Choropleth-Karte Zug"),
    output_widget("balken"), 
    output_widget("karte")
)

# -----------------------------
# 3) Server
# -----------------------------
def server(input, output, session):
    
    karte_fig = go.FigureWidget()

    # True Punkte darstellen
    karte_fig.add_choropleth(
        geojson=gjson_true,
        locations=gdf_true.index,
        z = gdf_true["IPCC_Match"].map({False:0, True:1}),
        colorscale=[[0, "white"], [1, "white"]],
        showscale=False,
        name="True"
    )

    # False Punkte darstellen
    karte_fig.add_choropleth(
        geojson=gjson_false,
        locations=gdf_false.index,
        z = gdf_false["IPCC_Match"].map({False:0, True:1}),
        colorscale=[[0, "red"], [1, "red"]],
        showscale=False,
        name="False"
    )
    
    # Position der Karte auf die Daten zoomen
    karte_fig.update_geos(
        fitbounds="locations",
        visible=False
    )

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
        w.data[0].on_click(on_point_click)

        return w
    
    # Reaktion auf den Klick in das Balkendiagramm
    def on_point_click(trace, points, state): 

        if points.point_inds[0] in [0,2]:
            selected_category.set("True") 

        if points.point_inds[0] in [1,3]:
            selected_category.set("False") 
            
        if selected_category.get() == "True":
            karte_fig.data[0].visible = True
            karte_fig.data[1].visible = "legendonly"
        elif selected_category.get() == "False":
            karte_fig.data[0].visible = "legendonly"
            karte_fig.data[1].visible = True
        else:
            karte_fig.data[0].visible = True
            karte_fig.data[1].visible = True
    
    # Karte        
    @output
    @render_plotly 
    def karte():
        return karte_fig
    
# -----------------------------
# 4) App starten
# -----------------------------
app = App(app_ui, server)
