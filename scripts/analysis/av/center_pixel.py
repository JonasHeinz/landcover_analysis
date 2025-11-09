import os
import pandas as pd
import geopandas as gpd
from scripts import DATA_DIR
from scripts.helpers import raster_helper

# Polygone des CORINE Datensatzes
polygons = gpd.read_file(DATA_DIR / "analysis/av/BB_Zug.gpkg")

# Punktraster der Arealstatistik
points = gpd.read_file(DATA_DIR / "analysis/arealstatistik/ag-b-00.03-37-area-all-gpkg_zug.gpkg")

# Länge resp. Breite der Boxen um die Punnkte der Arealstatistik
cell_size = 100  

# Erstellen von Boxen um jeden Punkt der Arealstatistik
points["grid"] = points.geometry.apply(lambda p: raster_helper.calculate_vectorbox(p, cell_size))

# Überschreiben des ursprünglichen Geometriefeld der Arealstatistik durch die neuen Boxen
points["geometry"] = points["grid"]
squares = points.drop(columns="grid")  

reduced_squares = squares[["RELI", "geometry"]]

# Geometrien der Boxen in ihre Mittelpunkt-Punkte umwandeln
raster_points = reduced_squares.geometry.centroid

# Räumliche Verknüpfung der Punkte mit den Polygonen von AV
squares_with_categories = gpd.sjoin(
    gpd.GeoDataFrame(geometry=raster_points, crs=reduced_squares.crs),
    polygons[['Art', 'geometry']],
    how='left',
    predicate='within'
)

# Umbennenen der 'Art' Spalte zu 'AV_ID' für Klarheit
squares['AV_ID'] = squares_with_categories['Art']

# Laden der Zuordnungstabellen von AV zu IPCC und von Arealstatistik zu IPCC
ipcc_av_mapping_dict = pd.read_csv(DATA_DIR / "analysis/av/mapping_ipcc_av.csv", sep=";" ).set_index("AV_ID")["IPCC_ID"].to_dict()
ipcc_arealstatistik_mapping_dict = pd.read_csv(DATA_DIR / "analysis/arealstatistik/mapping_ipcc_arealstatistik.csv", sep=";" ).set_index("AS_ID")["IPCC_ID"].to_dict()

# AV_ID contains string categories (e.g. 'Gewaesser_fliessendes'), so don't cast to int — map directly
squares_with_categories["IPCC_Av_Id"] = squares_with_categories["AV_ID"].map(ipcc_av_mapping_dict)

# AS18_72 may be numeric but possibly stored as string; convert safely and map
squares_with_categories["IPCC_AS_Id"] = pd.to_numeric(squares_with_categories["AS18_72"], errors="coerce").map(ipcc_arealstatistik_mapping_dict)

# Check für unmapped Werte
print("Unmapped AV_ID rows:", squares_with_categories["IPCC_Av_Id"].isna().sum())
print("Unmapped AS18_72 rows:", squares_with_categories["IPCC_AS_Id"].isna().sum())

# Prüfen der Gleichheit der IPCC Kategorien
squares_with_categories["IPCC_Match"] = squares_with_categories["IPCC_AV_Id"] == squares_with_categories["IPCC_AS_Id"]

# Speichern der Daten als Geopackage
squares_with_categories.to_file(DATA_DIR / "analysis/av/test3.gpkg")
