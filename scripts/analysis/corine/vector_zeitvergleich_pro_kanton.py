import os
os.environ['PROJ_LIB'] = r"C:\Users\LeonardoS\miniconda3\envs\corine\Library\share\proj"

import geopandas as gpd
from scripts import DATA_DIR

# Polygone des CORINE Datensatzes
polygons_2012 = gpd.read_file(DATA_DIR / "analysis/corine_vector/2012/U2018_CLC2012_V2020_20u1.gpkg")
polygons_2018 = gpd.read_file(DATA_DIR / "analysis/corine_vector/2018/U2018_CLC2018_V2020_20u1.gpkg")

squares = gpd.read_file(DATA_DIR / "base/swissBOUNDARIES3D/swissBOUNDARIES3D_1_5_LV95_LN02.gpkg", layer="tlm_kantonsgebiet")
reduced_squares = squares[["uuid", "geometry"]]

# Erstellen von Verschnitten zwischen den Quadraten der Arealstatistik und den Polygonen von CORINE 
intersections_2012 = gpd.overlay(reduced_squares, polygons_2012, how="intersection")
intersections_2018 = gpd.overlay(reduced_squares, polygons_2018, how="intersection")

# Berechnen der Fläche der Verschnitte
intersections_2012["polygon_area"] = intersections_2012.geometry.area
intersections_2018["polygon_area"] = intersections_2018.geometry.area

# Berechnen der Fläche der Quadrate der Arealstatistik
intersections_2012["square_area"] = intersections_2012.groupby("uuid")["polygon_area"].transform("sum")
intersections_2018["square_area"] = intersections_2018.groupby("uuid")["polygon_area"].transform("sum")

# Berechnen der prozentualen Flächenanteile der Veschnitte pro Fläche der Quadrate der Arealstatistik
intersections_2012["percent_per_square"] = intersections_2012["polygon_area"] / intersections_2012["square_area"] * 100
intersections_2018["percent_per_square"] = intersections_2018["polygon_area"] / intersections_2018["square_area"] * 100

# Gruppieren nach den Quadraten der Arealstatistik mit einer bestimmten CORINE Kategorie und danach Aufsummieren der prozentualen Flächenanteilen der Veschnitte pro Fläche
intersections_of_category_2012 = intersections_2012.groupby(["uuid", "Code_12"])["percent_per_square"].sum().reset_index()
intersections_of_category_2018 = intersections_2018.groupby(["uuid", "Code_18"])["percent_per_square"].sum().reset_index()

# Gruppieren nach den Quadraten der Arealstatistik und Erstellen einer Liste, die für jedes Quadrat die CORINE Kategorien mit ihren aufsummierten prozentualen Flächenanteilen enthält
intersections_of_category_from_square_2012 = intersections_of_category_2012.groupby("uuid")[["Code_12", "percent_per_square"]].apply(lambda df: {row["Code_12"]: row["percent_per_square"] for _, row in df.iterrows()}).rename("corine_categories").reset_index()
intersections_of_category_from_square_2018 = intersections_of_category_2018.groupby("uuid")[["Code_18", "percent_per_square"]].apply(lambda df: {row["Code_18"]: row["percent_per_square"] for _, row in df.iterrows()}).rename("corine_categories").reset_index()

# Zusammenführen des Arealstatistikdatensatzes mit den neu berechneten Werten 
squares_with_categories_2012 = squares.merge(intersections_of_category_from_square_2012, on="uuid", how="left")
squares_with_categories_2018 = squares.merge(intersections_of_category_from_square_2018, on="uuid", how="left")

# Feststellen der maximal vorkommenden CORINE Kategorie pro Quadrat der Arealstatistik 
squares_with_categories_2012["Code_12_max"] = squares_with_categories_2012["corine_categories"].apply(lambda di: max(di, key=di.get))
squares_with_categories_2018["Code_18_max"] = squares_with_categories_2018["corine_categories"].apply(lambda di: max(di, key=di.get))

intersections = gpd.overlay(squares_with_categories_2012, squares_with_categories_2018, how="intersection")
intersections["IPCC_Match"] = intersections["Code_12_max"] == intersections["Code_18_max"]

# Speichern der Daten als Geopackage
intersections.to_file(DATA_DIR / "analysis/corine_vector/zeitvergleich_max_area.gpkg")
