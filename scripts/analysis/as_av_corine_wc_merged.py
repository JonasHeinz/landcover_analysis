# AS AV CORINE WorldCover zusammenführen mit Centerpixel Methode

from scripts import DATA_DIR
import geopandas as gpd
import pandas as pd

# Dateien laden
g1 = gpd.read_file(DATA_DIR / "analysis/av/Av_As_Center_Pixel.gpkg")  # AV
g2 = gpd.read_file(DATA_DIR / "analysis/corine/2018/result_center_point.gpkg")  # Corine
g3 = gpd.read_file(
    DATA_DIR / "analysis/worldcover/arealstatistik_mapped_points_2020.gpkg"
)  # Worldcover


# Polygone zu Zentroide
g2_points = g2.copy()
g2_points.geometry = g2_points.geometry.centroid

g3_points = g3.copy()
g3_points.geometry = g3_points.geometry.centroid

# Spatial Join AV mit Corine
merged = gpd.sjoin_nearest(g1, g2_points, how="left")
if "index_right" in merged.columns:
    merged = merged.drop(columns=["index_right"])

# Spatial Join AV, Corine mit WorldCover
merged = gpd.sjoin_nearest(merged, g3_points, how="left")
if "index_right" in merged.columns:
    merged = merged.drop(columns=["index_right"])

merged.columns = [c.replace("_left", "").replace("_right", "") for c in merged.columns]

# Doppelte Spalten entfernen
merged = merged.loc[:, ~merged.columns.duplicated()]

# Speichern
merged.to_file(DATA_DIR / "as_av_corine_wc_merged.gpkg", driver="GPKG")
print("Merge abgeschlossen, doppelte Spalten entfernt und gespeichert")
