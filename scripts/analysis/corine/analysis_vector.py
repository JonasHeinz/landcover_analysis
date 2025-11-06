import os
os.environ['PROJ_LIB'] = r"C:\Users\LeonardoS\miniconda3\envs\corine\Library\share\proj"

import geopandas as gpd
from scripts import DATA_DIR
from scripts.helpers import raster_helper

# Polygone des CORINE Datensatzes
polygons = gpd.read_file(DATA_DIR / "analysis/corine/2012/U2018_CLC2012_V2020_20u1_zug.gpkg")

# Punktraster der Arealstatistik
points = gpd.read_file(DATA_DIR / "analysis/arealstatistik/ag-b-00.03-37-area-all-gpkg_zug.gpkg")

# Länge resp. Breite der Boxen um die Punnkte der Arealstatistik
cell_size = 100  

# Erstellen von Boxen um jeden Punkt der Arealstatistik
points["grid"] = points.geometry.apply(lambda p: raster_helper.calculate_vectorbox(p, cell_size))

# Überschreiben des ursprünglichen Geometriefeld der Arealstatistik durch die neuen Boxen
points["geometry"] = points["grid"]
points = points.drop(columns="grid")  

# points.to_file(DATA_DIR / "analysis/corine/2012/test.gpkg")
