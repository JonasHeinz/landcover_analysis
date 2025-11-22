from scripts import DATA_DIR
import geopandas as gpd
import rasterio
import numpy as np
import pandas as pd
import xml.etree.ElementTree as ET
from helpers import calculate_vectorbox
import os

# Eingabedateien
areal_gpkg = (
    DATA_DIR / "analysis/arealstatistik/ag-b-00.03-37-area-all-gpkg.gpkg"
)  # Arealstatistik Punkte
corine_raster = (
    DATA_DIR / "analysis/corine/2012/U2018_CLC2012_V2020_20u1.tif"
)  # CORINE Raster
ipcc_mapping_file_corine = (
    DATA_DIR / "analysis/corine/mapping_ipcc_corine.csv"
)  # Zuordnungstabelle Corine mit IPCC
ipcc_mapping_file_as = (
    DATA_DIR / "analysis/arealstatistik/mapping_ipcc_arealstatistik.csv"
)  # Zuordnungstabelle Arealstatistik mit IPCC
output_csv = (
    DATA_DIR / "analysis/corine/2012/Resultat_Tabelle_2012.csv"
)  # Output csv Tabelle
output_gpkg = (
    DATA_DIR / "analysis/corine/2012/Punkte_Resultat_2012.gpkg"
)  # Output Geopackage Punkte
output_grid_gpkg = (
    DATA_DIR / "analysis/corine/2012/VektorRaster_Resultat_2012.gpkg"
)  # Output Geopackage Vektorraster 100x100 m


# Hilfsfunktionen zum Auslesen der Arealstatistik labels aus Mapping Tabelle
def read_areal_labels(mapping_path):
    """Liest Arealstatistik-Labels aus CSV mit Spalten 'AS_ID, AS_NAME'."""
    labels = {}
    if os.path.exists(mapping_path):
        try:
            df_labels = pd.read_csv(mapping_path, sep=";", encoding="utf-8-sig")
            if {"AS_ID", "AS_NAME"}.issubset(df_labels.columns):
                labels = dict(zip(df_labels["AS_ID"].astype(int), df_labels["AS_NAME"]))
                print(f"{len(labels)} Arealstatistik-Labels aus CSV geladen.")
            else:
                print("CSV enthält keine Spalten 'AS_ID' und 'AS_NAME'.")
        except Exception as e:
            print("Fehler beim Lesen der Arealstatistik-Label-Tabelle:", e)
    else:
        print("Keine Areal-Label-Datei gefunden:", mapping_path)
    return labels


# Hilfsfunktionen zum Auslesen der CORINE labels aus Mapping Tabelle
def read_corine_labels(mapping_path):
    """Liest Corine-Labels aus CSV mit Spalten 'RASTER_ID, CORINE_NAME'."""
    labels = {}
    if os.path.exists(mapping_path):
        try:
            df_labels = pd.read_csv(mapping_path, sep=";", encoding="utf-8-sig")
            if {"RASTER_ID", "CORINE_NAME"}.issubset(df_labels.columns):
                labels = dict(
                    zip(df_labels["RASTER_ID"].astype(int), df_labels["CORINE_NAME"])
                )
                print(f"{len(labels)} Corine-Labels aus CSV geladen.")
            else:
                print("CSV enthält keine Spalten 'RASTER_ID' und 'CORINE_NAME'.")
        except Exception as e:
            print("Fehler beim Lesen der Corine-Label-Tabelle:", e)
    else:
        print("Keine Corine-Label-Datei gefunden:", mapping_path)
    return labels


# Labels laden
corine_labels = read_corine_labels(ipcc_mapping_file_corine)
areal_labels = read_areal_labels(ipcc_mapping_file_as)

# Arealstatistik Geopackage laden
gdf = gpd.read_file(areal_gpkg)
print(f"{len(gdf):,} Arealstatistik Punkte aus GeoPackage geladen.")

if "AS09_72" not in gdf.columns:
    raise KeyError("Spalte 'AS09_72' fehlt im GeoPackage!")

# Umbenennen der Arealspalte AS09_72 zu areal_value
gdf = gdf.rename(columns={"AS09_72": "areal_value"})
gdf["areal_label"] = gdf["areal_value"].map(areal_labels).fillna("Unknown")

# CORINE-Werte auf Arealstatistikpunkte sampeln
with rasterio.open(corine_raster) as src:
    coords = [(geom.x, geom.y) for geom in gdf.geometry]
    # Liest den CORINE-Rasterwert für jeden Arealstatistikpunkt aus
    corine_vals = [val[0] if val is not None else np.nan for val in src.sample(coords)]

gdf["corine_value"] = corine_vals
gdf["corine_label"] = gdf["corine_value"].apply(
    lambda v: corine_labels.get(int(v), "NODATA") if not pd.isna(v) else "NODATA"
)
print("CORINE-Werte erfolgreich gesampelt und gelabelt.")


# Mapping-Tabelle laden (IPCC - CORINE)
map_df_corine = pd.read_csv(ipcc_mapping_file_corine, sep=";", encoding="utf-8-sig")
required_cols_c = {"IPCC_ID", "IPCC_NAME", "RASTER_ID", "CORINE_NAME"}
if not required_cols_c.issubset(map_df_corine.columns):
    raise ValueError(f"Mapping-Datei muss Spalten enthalten: {required_cols_c}")

corine_to_ipcc_name = dict(zip(map_df_corine["RASTER_ID"], map_df_corine["IPCC_NAME"]))
corine_to_ipcc_id = dict(zip(map_df_corine["RASTER_ID"], map_df_corine["IPCC_ID"]))

gdf["ipcc_corine_label"] = (
    gdf["corine_value"].map(corine_to_ipcc_name).fillna("Unknown")
)
gdf["ipcc_corine_value"] = gdf["corine_value"].map(corine_to_ipcc_id).astype("Int64")


# Mapping-Tabelle laden (IPCC - Arealstatistik)
map_df_areal = pd.read_csv(ipcc_mapping_file_as, sep=";", encoding="utf-8-sig")
required_cols_a = {"IPCC_ID", "IPCC_NAME", "AS_ID", "AS_NAME"}
if not required_cols_a.issubset(map_df_areal.columns):
    raise ValueError(f"Mapping-Datei muss Spalten enthalten: {required_cols_a}")

areal_to_ipcc_name = dict(zip(map_df_areal["AS_ID"], map_df_areal["IPCC_NAME"]))
areal_to_ipcc_id = dict(zip(map_df_areal["AS_ID"], map_df_areal["IPCC_ID"]))

gdf["ipcc_areal_label"] = gdf["areal_value"].map(areal_to_ipcc_name).fillna("Unknown")
gdf["ipcc_areal_value"] = gdf["areal_value"].map(areal_to_ipcc_id).astype("Int64")

# Vergleich zwischen IPCC - Arealstatistik & IPCC - CORINE (0 = gleich, 1 = unterschiedlich)
gdf["diff_ipcc"] = (
    gdf["ipcc_areal_value"].fillna(-1) != gdf["ipcc_corine_value"].fillna(-1)
).astype(int)

# x,y-Koordinaten hinzufügen
gdf["x"] = gdf.geometry.x
gdf["y"] = gdf.geometry.y

# Spaltenreihenfolge anpassen
desired_order = [
    "areal_value",
    "areal_label",
    "corine_value",
    "corine_label",
    "ipcc_areal_value",
    "ipcc_areal_label",
    "ipcc_corine_value",
    "ipcc_corine_label",
    "diff_ipcc",
    "x",
    "y",
]


# Export csv Tabelle
gdf[desired_order].to_csv(output_csv, index=False, encoding="utf-8-sig")

# Export Punkte als gpkg
cols = [c for c in gdf.columns if c not in desired_order] + desired_order
gdf[cols].to_file(output_gpkg, driver="GPKG")

# 100 x 100 Raster Poygone erzeugen
cell_size = 100

gdf_grid = gdf.copy()
gdf_grid["geometry"] = gdf_grid.geometry.apply(
    lambda p: calculate_vectorbox(p, cell_size)
)

# Export Vektorraster als gpkg
gdf_grid.to_file(output_grid_gpkg, driver="GPKG")


print("Tabelle gespeichert unter:", {output_csv})
print("Geopackage gespeichert unter:", {output_gpkg})
print("100x100m Vektor-Raster gespeichert unter:", {output_grid_gpkg})
