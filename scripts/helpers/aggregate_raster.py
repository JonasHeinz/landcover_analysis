import os
os.environ["PROJ_LIB"] = r"C:\Users\LeonardoS\miniconda3\envs\corine\Library\share\proj"

import geopandas as gpd
import numpy as np
import rasterio
from rasterio.transform import from_origin
from scripts import DATA_DIR

# -----------------------------
# 1) Geodaten laden
# -----------------------------
gdf = gpd.read_file(DATA_DIR / "analysis/corine/2012/result_max_area_zug.gpkg")

# Wir setzen voraus:
# - gdf enthält Quadrate (100 m x 100 m)
# - Spalten: 'IPCC_AS_Id' (1–6) und 'IPCC_Match' (bool)
# - CRS ist metrisch (z.B. 2056 oder 3857)
# -----------------------------

# Raster-Auflösung
cellsize = 100  # 100m × 100m
nodata_value = 255

# Bounding Box bestimmen
minx, miny, maxx, maxy = gdf.total_bounds

# Rastergröße bestimmen
width = int((maxx - minx) / cellsize)
height = int((maxy - miny) / cellsize)

# Affine Transform
transform = from_origin(minx, maxy, cellsize, cellsize)

# -----------------------------
# 2) Raster pro Band erstellen
# -----------------------------
for band_id in range(1, 7):
    # Raster für dieses Band initialisieren
    raster = np.full((height, width), nodata_value, dtype=np.uint8)
    
    # Filtern auf die aktuelle IPCC_AS_Id
    gdf_band = gdf[gdf["IPCC_AS_Id"] == band_id]

    # Werte in Raster schreiben
    for idx, row in gdf_band.iterrows():
        x_center = row.geometry.centroid.x
        y_center = row.geometry.centroid.y
        
        col = int((x_center - minx) / cellsize)
        row_ = int((maxy - y_center) / cellsize)
        
        if 0 <= row_ < height and 0 <= col < width:
            raster_value = 1 if row["IPCC_Match"] else 0
            raster[row_, col] = raster_value

    # -----------------------------
    # 3) Raster speichern
    # -----------------------------
    out_path = DATA_DIR / f"analysis/corine/2012/op/output_band_{band_id}.tif"
    profile = {
        "driver": "GTiff",
        "height": height,
        "width": width,
        "count": 1,
        "dtype": rasterio.uint8,
        "crs": gdf.crs,
        "transform": transform,
        "nodata": nodata_value
    }

    with rasterio.open(out_path, "w", **profile) as dst:
        dst.write(raster, 1)

    print(f"Band {band_id} gespeichert: {out_path}")

print("FERTIG → alle 6 Bänder erzeugt")
