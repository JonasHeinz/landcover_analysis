from scripts import DATA_DIR
import geopandas as gpd
import rasterio
import numpy as np
import pandas as pd
import xml.etree.ElementTree as ET
import os

# Eingabedateien
areal_gpkg = (
    DATA_DIR / "analysis/arealstatistik/ag-b-00.03-37-area-all-gpkg_zug.gpkg"
)  # Arealstatistik Punkte
corine_raster = (
    DATA_DIR / "analysis/corine/2018/U2018_CLC2018_V2020_20u1_zug.tif"
)  # Corine Raster
ipcc_mapping_file_corine = (
    DATA_DIR / "analysis/corine/mapping_ipcc_corine.csv"
)  # Zuordnungstabelle Corine mit IPCC
ipcc_mapping_file_as = (
    DATA_DIR / "analysis/arealstatistik/mapping_ipcc_arealstatistik.csv"
)  # Zuordnungstabelle Arealstatistik mit IPCC
output_csv = DATA_DIR / "analysis/corine/2018/Tabelle_Zug.csv"  # Output csv Tabelle
output_gpkg = (
    DATA_DIR / "analysis/corine/2018/Punkte_Zug.gpkg"
)  # Output Geopackage Punkte


# Hilfsfunktionen
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

# Arealstatistik laden
gdf = gpd.read_file(areal_gpkg)
print(f"{len(gdf):,} Arealstatistik Punkte aus GeoPackage geladen.")

if "AS18_72" not in gdf.columns:
    raise KeyError("Spalte 'AS18_72' fehlt im GeoPackage!")

# Umbenennen der Arealspalte AS18_72 zu areal_label
gdf = gdf.rename(columns={"AS18_72": "areal_value"})
gdf["areal_label"] = gdf["areal_value"].map(areal_labels).fillna("Unknown")

# CORINE-Werte sampeln
with rasterio.open(corine_raster) as src:
    coords = [(geom.x, geom.y) for geom in gdf.geometry]
    corine_vals = [val[0] if val is not None else np.nan for val in src.sample(coords)]

gdf["corine_value"] = corine_vals
gdf["corine_label"] = gdf["corine_value"].apply(
    lambda v: corine_labels.get(int(v), "NODATA") if not pd.isna(v) else "NODATA"
)
print("CORINE-Werte erfolgreich gesampelt und gelabelt.")


# Mapping-Tabelle laden (IPCC – CORINE)
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


# Mapping-Tabelle laden (IPCC – Arealstatistik)
map_df_areal = pd.read_csv(ipcc_mapping_file_as, sep=";", encoding="utf-8-sig")
required_cols_a = {"IPCC_ID", "IPCC_NAME", "AS_ID", "AS_NAME"}
if not required_cols_a.issubset(map_df_areal.columns):
    raise ValueError(f"Mapping-Datei muss Spalten enthalten: {required_cols_a}")

areal_to_ipcc_name = dict(zip(map_df_areal["AS_ID"], map_df_areal["IPCC_NAME"]))
areal_to_ipcc_id = dict(zip(map_df_areal["AS_ID"], map_df_areal["IPCC_ID"]))

gdf["ipcc_areal_label"] = gdf["areal_value"].map(areal_to_ipcc_name).fillna("Unknown")
gdf["ipcc_areal_value"] = gdf["areal_value"].map(areal_to_ipcc_id).astype("Int64")

# Vergleich (Unterschiede)
gdf["diff_ipcc"] = (
    gdf["ipcc_areal_value"].fillna(-1) != gdf["ipcc_corine_value"].fillna(-1)
).astype(int)

# x,y-Koordinaten hinzufügen
gdf["x"] = gdf.geometry.x
gdf["y"] = gdf.geometry.y

# Spaltenreihenfolge
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
gdf[desired_order + ["geometry"]].to_file(output_gpkg, driver="GPKG")


print("Tabelle gespeichert unter:", {output_csv})
print("Geopackage gespeichert unter:", {output_gpkg})
