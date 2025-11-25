import os
os.environ["PROJ_LIB"] = r"C:\Users\LeonardoS\miniconda3\envs\corine\Library\share\proj"

import geopandas as gpd
import numpy as np
import rasterio
from rasterio.transform import from_origin
from scripts import DATA_DIR

files = [
    {"dataset": "corine", "year": "2012", "analysis": "result_center_point", "output": "center_point_raster", "as_id": "IPCC_AS_Id", "match": "IPCC_Match"},
    {"dataset": "corine", "year": "2012", "analysis": "result_max_area", "output": "max_area_raster", "as_id": "IPCC_AS_Id", "match": "IPCC_Match"},
    {"dataset": "corine", "year": "2018", "analysis": "result_center_point", "output": "center_point_raster", "as_id": "IPCC_AS_Id", "match": "IPCC_Match"},
    {"dataset": "corine", "year": "2018", "analysis": "result_max_area", "output": "max_area_raster", "as_id": "IPCC_AS_Id", "match": "IPCC_Match"},
    
    {"dataset": "corine", "year": "2012", "analysis": "areal_corine_ipcc_2012", "output": "center_point_raster_raster", "as_id": "IPCC_AS_Id", "match": "diff_ipcc"},
    {"dataset": "corine", "year": "2018", "analysis": "areal_corine_ipcc_2018", "output": "center_point_raster_raster", "as_id": "IPCC_AS_Id", "match": "diff_ipcc"},
    
    {"dataset": "worldcover", "year": "2020", "analysis": "arealstatistik_mapped_points_2020_cp", "output": "center_point_raster", "as_id": "IPCC_AS_Id", "match": "IPCC_Match"},
    {"dataset": "worldcover", "year": "2020", "analysis": "arealstatistik_mapped_2020_ma", "output": "max_area_raster", "as_id": "IPCC_AS_Id", "match": "IPCC_Match"},
    {"dataset": "worldcover", "year": "2021", "analysis": "arealstatistik_mapped_points_2021_cp", "output": "center_point_raster", "as_id": "IPCC_AS_Id", "match": "IPCC_Match"},
    {"dataset": "worldcover", "year": "2021", "analysis": "arealstatistik_mapped_2021_ma", "output": "max_area_raster", "as_id": "IPCC_AS_Id", "match": "IPCC_Match"},
    
    {"dataset": "av", "year": "jahr", "analysis": "AV_As_Center_Pixel", "output": "center_point_raster", "as_id": "IPCC_AS_Id", "match": "IPCC_Match"}
]

# -----------------------------
# 1) Geodaten laden
# -----------------------------

for f in files:
    dataset = f["dataset"]
    year = f["year"]
    analysis = f["analysis"]
    output = f["output"]
    as_id = f["as_id"]
    match = f["match"]
    
    print(f"Processing {dataset} data from file {analysis}.gpkg...")
    
    if(dataset == "corine"):
        gdf = gpd.read_file(DATA_DIR / f"analysis/{dataset}/{year}/{analysis}.gpkg")
    elif(dataset == "worldcover"):
        gdf = gpd.read_file(DATA_DIR / f"analysis/{dataset}/{year}/{analysis}.gpkg")
        gdf["IPCC_Match"] = gdf["IPCC_AS_Id"] == gdf["IPCC_WC_Id"]
    elif(dataset=="av"):
        gdf = gpd.read_file(DATA_DIR / f"analysis/{dataset}/{analysis}.gpkg")

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
        gdf_band = gdf[gdf[as_id] == band_id]

        # Werte in Raster schreiben
        for idx, row in gdf_band.iterrows():
            x_center = row.geometry.centroid.x
            y_center = row.geometry.centroid.y
            
            col = int((x_center - minx) / cellsize)
            row_ = int((maxy - y_center) / cellsize)
            
            if 0 <= row_ < height and 0 <= col < width:
                raster_value = 1 if row[match] else 0
                raster[row_, col] = raster_value

        # -----------------------------
        # 3) Raster speichern
        # -----------------------------
        out_path = DATA_DIR / f"analysis/{dataset}/{year}/{output}/ipcc_category_{band_id}.tif"
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
