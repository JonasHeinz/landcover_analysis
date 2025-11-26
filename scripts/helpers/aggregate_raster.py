import os
os.environ["PROJ_LIB"] = r"C:\Users\LeonardoS\miniconda3\envs\corine\Library\share\proj"

import geopandas as gpd
import pandas as pd
import numpy as np
import rasterio
from rasterio.transform import from_origin
from scripts import DATA_DIR

onlystats=False

files = [
    {"dataset": "corine_vector", "year": "2012", "method": "center_point", "filename": "result_center_point", "as_id": "IPCC_AS_Id", "match": "IPCC_Match"},
    {"dataset": "corine_vector", "year": "2012", "method": "max_area", "filename": "result_max_area", "as_id": "IPCC_AS_Id", "match": "IPCC_Match"},
    {"dataset": "corine_vector", "year": "2018", "method": "center_point", "filename": "result_center_point", "as_id": "IPCC_AS_Id", "match": "IPCC_Match"},
    {"dataset": "corine_vector", "year": "2018", "method": "max_area", "filename": "result_max_area", "as_id": "IPCC_AS_Id", "match": "IPCC_Match"},
    
    {"dataset": "corine_raster", "year": "2012", "method": "center_point", "filename": "areal_corine_ipcc_2012", "as_id": "IPCC_AS_Id", "match": "diff_ipcc"},
    {"dataset": "corine_raster", "year": "2018", "method": "center_point", "filename": "areal_corine_ipcc_2018", "as_id": "IPCC_AS_Id", "match": "diff_ipcc"},
    
    {"dataset": "worldcover", "year": "2020", "method": "center_point", "filename": "arealstatistik_mapped_points_2020_cp", "as_id": "IPCC_AS_Id", "match": "IPCC_Match"},
    {"dataset": "worldcover", "year": "2020", "method": "max_area", "filename": "arealstatistik_mapped_2020_ma", "as_id": "IPCC_AS_Id", "match": "IPCC_Match"},
    {"dataset": "worldcover", "year": "2021", "method": "center_point", "filename": "arealstatistik_mapped_points_2021_cp", "as_id": "IPCC_AS_Id", "match": "IPCC_Match"},
    {"dataset": "worldcover", "year": "2021", "method": "max_area", "filename": "arealstatistik_mapped_2021_ma", "as_id": "IPCC_AS_Id", "match": "IPCC_Match"},
    
    {"dataset": "av", "year": "2025", "method": "center_point", "filename": "AV_As_Center_Pixel", "as_id": "IPCC_AS_Id", "match": "IPCC_Match"},
    {"dataset": "av", "year": "2025", "method": "max_area", "filename": "AV_As_Maximal_Area", "as_id": "IPCC_AS_Id", "match": "IPCC_Match"}
]

# Kategorien inkl. Farben zusammenfassen
ipcc_category_info = {
    1: {"name": "Forest Land", "bar_ids": [0, 1], "colors": ("#006d2c", "#2ca25f")},
    2: {"name": "Cropland", "bar_ids": [2, 3], "colors": ("#993404", "#d95f0e")},
    3: {"name": "Grasslands", "bar_ids": [4, 5], "colors": ("#d9f0a3", "#ffffcc")},
    4: {"name": "Wetlands", "bar_ids": [6, 7], "colors": ("#253494", "#2c7fb8")},
    5: {"name": "Settlements", "bar_ids": [8, 9], "colors": ("#bdbdbd", "#d9d9d9")},
    6: {"name": "Other Land", "bar_ids": [10,11], "colors": ("#f768a1", "#fa9fb5")},
}

# -----------------------------
# 1) Geodaten laden
# -----------------------------

for file in files:
    dataset = file["dataset"]
    year = file["year"]
    method = file["method"]
    filename = file["filename"]
    as_id = file["as_id"]
    match = file["match"]
    
    print(f"Prozessierung der Daten von {dataset} {year} aus der Datei {DATA_DIR}\analysis\{dataset}\{year}\{method}\{filename}.gpkg...")
            
    gdf = gpd.read_file(DATA_DIR / f"analysis/{dataset}/{year}/{method}/{filename}.gpkg")

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

    if not onlystats:
        print(f"Rasterisierung der Daten von {dataset} {year} gestartet...")
        for band_id in range(1, 7):
            # Raster für dieses Band initialisieren
            out_path = DATA_DIR / f"analysis/{dataset}/{year}/{method}/ipcc_category_{band_id}.tif"
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

            print(f"Band {band_id} der Daten von {dataset} {year} gespeichert: {out_path}")
        
        print(f"Alle Bänder der Daten von {dataset} {year} gespeichert!")
    
    print(f"Statistikberechnung für Daten von {dataset} {year} gestartet...")
    
    csv_path =  DATA_DIR / f"analysis/{dataset}/{year}/{method}/ipcc_category_stats.csv"
    
    if not csv_path.exists():
        gdf = gdf.to_crs(epsg=3857)
        
        if file["dataset"] == "worldcover":
            gdf["IPCC_Match"] = gdf["IPCC_AS_Id"] == gdf["IPCC_WC_Id"]
        
        df_balken_list = []

        for ipcc_as_id in sorted(gdf[as_id].unique()):
            subset = gdf[gdf[as_id] == ipcc_as_id]
            cat_info = ipcc_category_info.get(ipcc_as_id)
            name = cat_info["name"]
            dark, light = cat_info["colors"]

            df_temp = pd.DataFrame({
                "IPCC_AS_Id": [ipcc_as_id, ipcc_as_id],
                "IPCC_AS_Name": [name, name],
                "Art": ["AS", "AS"],
                "Uebereinstimmende_Klassifikation": ["Wahr", "Falsch"],
                "Farbe": [light, dark],
                "Anzahl": [subset[match].sum(), len(subset) - subset[match].sum()],
                "Anteil": [subset[match].mean(), 1 - subset[match].mean()]
            })
            df_balken_list.append(df_temp)

        df_balken = pd.concat(df_balken_list, ignore_index=True)

        df_balken.to_csv(csv_path, index=False)
        print(f"Statistiken für Daten von {dataset} {year} als CSV gespeichert: {csv_path}")
    else:
        print(f"Statistiken für Daten von {dataset} {year} bereits als CSV gespeichert: {csv_path}")
    print("")
    
print(f"Alle Daten vollständig prozessiert!")
print("")
