import os
import pandas as pd
import geopandas as gpd
from scripts import DATA_DIR
from scripts.helpers import raster_helper

# Polygone des AV Datensatzes
import geopandas as gpd

point = gpd.read_file(DATA_DIR/"analysis/arealstatistik/Arealstatistik_Zug.gpkg")
polygon = gpd.read_file(DATA_DIR/"analysis/av/BB_Zug.gpkg")

import os
cwd = os.getcwd()
print(cwd)

# ensure CRS is metric (LV95 / EPSG:2056 or similar)
print("point.crs:", point.crs)

# if point geometries are polygons use centroids, otherwise geometry if already points
points = point.geometry.centroid

boxsize = 100  # meters

# create GeoSeries of boxes
boxes = points.apply(lambda p: raster_helper.calculate_vectorbox(p, boxsize))

# Make GeoDataFrame with same attributes + new geometry
point_Raster = gpd.GeoDataFrame(point.drop(columns="geometry"), geometry=boxes, crs=point.crs)

# First ensure same CRS
if point_Raster.crs != polygon.crs:
    polygon = polygon.to_crs(point_Raster.crs)

# Get centroids of the raster boxes for point-in-polygon operation
raster_points = point_Raster.geometry.centroid

# Perform spatial join
joined = gpd.sjoin(
    gpd.GeoDataFrame(geometry=raster_points, crs=point_Raster.crs),
    polygon[['Art', 'geometry']],
    how='left',
    predicate='within'
)

# Add the joined Art values back to point_Raster
point_Raster['Art_AV'] = joined['Art']

point_Raster["AV_ID"] = point_Raster["Art_AV"]

import pandas as pd
ipcc_av_mapping_dict = pd.read_csv(DATA_DIR/"analysis/av/mapping_ipcc_av.csv", sep=";" ).set_index("AV_ID")["IPCC_ID"].to_dict()
ipcc_arealstatistik_mapping_dict = pd.read_csv(DATA_DIR/"analysis/arealstatistik/mapping_ipcc_arealstatistik.csv", sep=";" ).set_index("AS_ID")["IPCC_ID"].to_dict()

# AV_ID contains string categories (e.g. 'Gewaesser_fliessendes'), so don't cast to int — map directly
point_Raster["IPCC_AV_Id"] = point_Raster["AV_ID"].map(ipcc_av_mapping_dict)

# AS18_72 may be numeric but possibly stored as string; convert safely and map
point_Raster["IPCC_AS_Id"] = pd.to_numeric(point_Raster["AS18_72"], errors="coerce").map(ipcc_arealstatistik_mapping_dict)

# quick diagnostics for unmapped values
print("Unmapped AV_ID rows:", point_Raster["IPCC_AV_Id"].isna().sum())
print("Unmapped AS18_72 rows:", point_Raster["IPCC_AS_Id"].isna().sum())

point_Raster["IPCC_Match"] = point_Raster["IPCC_Av_Id"] == point_Raster["IPCC_AS_Id"]

point_Raster.to_file(DATA_DIR/"analysis/av/AV_As_Center_Pixel.gpkg")
