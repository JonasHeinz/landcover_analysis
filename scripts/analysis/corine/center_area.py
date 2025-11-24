import os
os.environ['PROJ_LIB'] = r"C:\Users\LeonardoS\miniconda3\envs\corine\Library\share\proj"

import pandas as pd
import geopandas as gpd
from scripts import DATA_DIR
from scripts.helpers import raster_helper

# Polygone des CORINE Datensatzes
polygons = gpd.read_file(DATA_DIR / "analysis/corine/2018/U2018_CLC2018_V2020_20u1.gpkg")

# Punktraster der Arealstatistik
points = gpd.read_file(DATA_DIR / "analysis/arealstatistik/ag-b-00.03-37-area-all-gpkg.gpkg")

# CORINE Kategorie auf dem Punkt der Arealstatistik bestimmen
joined_points = gpd.sjoin(points, polygons[["Code_18", "geometry"]], how="left", predicate="within")
joined_points = joined_points.drop(columns="geometry")
points["Code_18_point"] = joined_points["Code_18"].values

# Länge resp. Breite der Boxen um die Punnkte der Arealstatistik
cell_size = 100  

# Erstellen von Boxen um jeden Punkt der Arealstatistik
points["grid"] = points.geometry.apply(lambda p: raster_helper.calculate_vectorbox(p, cell_size))

# Überschreiben des ursprünglichen Geometriefeld der Arealstatistik durch die neuen Boxen
points["geometry"] = points["grid"]
squares = points.drop(columns="grid")  
squares = squares[["RELI", "AS18_72", "Code_18_point", "geometry"]]

reduced_squares = squares[["RELI", "geometry"]]

# Erstellen von Verschnitten zwischen den Quadraten der Arealstatistik und den Polygonen von CORINE 
intersections = gpd.overlay(reduced_squares, polygons, how="intersection")

# Berechnen der Fläche der Verschnitte
intersections["polygon_area"] = intersections.geometry.area

# Berechnen der Fläche der Quadrate der Arealstatistik
intersections["square_area"] = intersections.groupby("RELI")["polygon_area"].transform("sum")

# Berechnen der prozentualen Flächenanteile der Veschnitte pro Fläche der Quadrate der Arealstatistik
intersections["percent_per_square"] = intersections["polygon_area"] / intersections["square_area"] * 100

# Gruppieren nach den Quadraten der Arealstatistik mit einer bestimmten CORINE Kategorie und danach Aufsummieren der prozentualen Flächenanteilen der Veschnitte pro Fläche
intersections_of_category = intersections.groupby(["RELI", "Code_18"])["percent_per_square"].sum().reset_index()

# Gruppieren nach den Quadraten der Arealstatistik und Erstellen einer Liste, die für jedes Quadrat die CORINE Kategorien mit ihren aufsummierten prozentualen Flächenanteilen enthält
intersections_of_category_from_square = intersections_of_category.groupby("RELI")[["Code_18", "percent_per_square"]].apply(lambda df: {row["Code_18"]: row["percent_per_square"] for _, row in df.iterrows()}).rename("corine_categories").reset_index()

# Zusammenführen des Arealstatistikdatensatzes mit den neu berechneten Werten 
squares_with_categories = squares.merge(intersections_of_category_from_square, on="RELI", how="left")

# Laden der Zuordnungstabellen von CORINE zu IPCC und von Arealstatistik zu IPCC
ipcc_corine_mapping_dict = pd.read_csv(DATA_DIR / "analysis/corine/mapping_ipcc_corine.csv", sep=";" ).set_index("CORINE_ID")["IPCC_ID"].to_dict()
ipcc_arealstatistik_mapping_dict = pd.read_csv(DATA_DIR / "analysis/arealstatistik/mapping_ipcc_arealstatistik.csv", sep=";" ).set_index("AS_ID")["IPCC_ID"].to_dict()

# Speichern der CORINE Kategorie und der Arealstatistik Kategorie als IPCC Kategorie
squares_with_categories["IPCC_CORINE_Id"] = squares_with_categories["Code_18_point"].astype(int).map(ipcc_corine_mapping_dict)
squares_with_categories["IPCC_AS_Id"] = squares_with_categories["AS18_72"].astype(int).map(ipcc_arealstatistik_mapping_dict)

# Prüfen der Gleichheit der IPCC Kategorien
squares_with_categories["IPCC_Match"] = squares_with_categories["IPCC_CORINE_Id"] == squares_with_categories["IPCC_AS_Id"]

# Speichern der Daten als Geopackage
squares_with_categories.to_file(DATA_DIR / "analysis/corine/2018/result.gpkg")
