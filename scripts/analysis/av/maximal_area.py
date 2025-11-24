import os
os.environ['PROJ_LIB'] = r"C:\Users\LeonardoS\miniconda3\envs\corine\Library\share\proj"

import pandas as pd
import geopandas as gpd
from scripts import DATA_DIR
from scripts.helpers import raster_helper

# Polygone des AV Datensatzes
polygons = gpd.read_file(DATA_DIR / "analysis/av/BB_CH_Gesamt.gpkg")

# Punktraster der Arealstatistik
points = gpd.read_file(DATA_DIR / "analysis/arealstatistik/Arealstatistik_Zeitreihe.gpkg")

# Länge resp. Breite der Boxen um die Punnkte der Arealstatistik
cell_size = 100  

# Erstellen von Boxen um jeden Punkt der Arealstatistik
points["grid"] = points.geometry.apply(lambda p: raster_helper.calculate_vectorbox(p, cell_size))

# Überschreiben des ursprünglichen Geometriefeld der Arealstatistik durch die neuen Boxen
points["geometry"] = points["grid"]
squares = points.drop(columns="grid")  

reduced_squares = squares[["RELI", "geometry"]]

# Erstellen von Verschnitten zwischen den Quadraten der Arealstatistik und den Polygonen der amtlichen Vermessung 
intersections = gpd.overlay(reduced_squares, polygons, how="intersection")

# Berechnen der Fläche der Verschnitte
intersections["polygon_area"] = intersections.geometry.area

# Berechnen der Fläche der Quadrate der Arealstatistik
intersections["square_area"] = intersections.groupby("RELI")["polygon_area"].transform("sum")

# Berechnen der prozentualen Flächenanteile der Veschnitte pro Fläche der Quadrate der Arealstatistik
intersections["percent_per_square"] = intersections["polygon_area"] / intersections["square_area"] * 100

# Gruppieren nach den Quadraten der Arealstatistik mit einer bestimmten AV Kategorie und danach Aufsummieren der prozentualen Flächenanteilen der Veschnitte pro Fläche
intersections_of_category = intersections.groupby(["RELI", "Art"])["percent_per_square"].sum().reset_index()

# Gruppieren nach den Quadraten der Arealstatistik und Erstellen einer Liste, die für jedes Quadrat die AV Kategorien mit ihren aufsummierten prozentualen Flächenanteilen enthält
intersections_of_category_from_square = intersections_of_category.groupby("RELI")[["Art", "percent_per_square"]].apply(lambda df: {row["Art"]: row["percent_per_square"] for _, row in df.iterrows()}).rename("av_categories").reset_index()

# Zusammenführen des Arealstatistikdatensatzes mit den neu berechneten Werten 
squares_with_categories = squares.merge(intersections_of_category_from_square, on="RELI", how="left")

# Feststellen der maximal vorkommenden AV Kategorie pro Quadrat der Arealstatistik 
squares_with_categories["Art_max"] = squares_with_categories["av_categories"].apply(lambda di: max(di, key=di.get) if isinstance(di, dict) and di else None)

# Laden der Zuordnungstabellen von AV zu IPCC und von Arealstatistik zu IPCC
ipcc_av_mapping_dict = pd.read_csv(DATA_DIR / "analysis/av/mapping_ipcc_av.csv", sep=";" ).set_index("AV_ID")["IPCC_ID"].to_dict()
ipcc_arealstatistik_mapping_dict = pd.read_csv(DATA_DIR / "analysis/arealstatistik/mapping_ipcc_arealstatistik.csv", sep=";" ).set_index("AS_ID")["IPCC_ID"].to_dict()

# Speichern der AV Kategorie und der Arealstatistik Kategorie als IPCC Kategorie
squares_with_categories["IPCC_AV_Id"] = squares_with_categories["Art_max"].map(ipcc_av_mapping_dict)
squares_with_categories["IPCC_AS_Id"] = squares_with_categories["AS18_72"].astype(int).map(ipcc_arealstatistik_mapping_dict)

# Prüfen der Gleichheit der IPCC Kategorien
squares_with_categories["IPCC_Match"] = squares_with_categories["IPCC_AV_Id"] == squares_with_categories["IPCC_AS_Id"]

# Speichern der Daten als Geopackage
squares_with_categories.to_file(DATA_DIR / "analysis/av/AV_As_Maximal_Area.gpkg")
