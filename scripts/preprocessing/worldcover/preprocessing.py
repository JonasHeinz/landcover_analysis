from scripts import DATA_DIR
import os

os.environ["PROJ_LIB"] = r"C:\Users\alexa\anaconda3\envs\WC\Library\share\proj"
os.environ["GDAL_DATA"] = r"C:\Users\alexa\anaconda3\envs\WC\Library\share\gdal"

from shapely.geometry import Polygon, MultiPolygon
import geopandas as gpd
import rasterio
from rasterio.merge import merge
from rasterio.plot import show
from rasterio.warp import calculate_default_transform, reproject, Resampling
from rasterio.mask import mask
import glob

# define data paths for worlcover files
WORLDCOVER_PATH = DATA_DIR + "scripts/preprocessing/worldcover/2021"

# Replace this with your actual folder containing the 3 WorldCover rasters
RASTER_FOLDER = WORLDCOVER_PATH  + "/tiles/"


# Replace with your actual file path and layer name if necessary
gpkg_path = DATA_DIR  + "data/base/swissBOUNDARIES3D/swissBOUNDARIES3D_1_5_LV95_LN02.gpkg"
border_gdf = gpd.read_file(gpkg_path)

# Buffer the border by 1000 meters (1 km)
buffered_border_gdf = border_gdf.copy()
buffered_border_gdf["geometry"] = buffered_border_gdf.buffer(1000)
buffered_border_gdf.to_file(WORLDCOVER_PATH  + "/swiss_border_buffered_1km.gpkg", driver="GPKG")

# Fill holes in the buffered geometries
def fill_all_holes(geom):
    return Polygon(geom.exterior) if geom.type == 'Polygon' else MultiPolygon([Polygon(g.exterior) for g in geom.geoms])
buffered_border_gdf["geometry"] = buffered_border_gdf.geometry.apply(fill_all_holes)


# List all .tif files in the folder
raster_files = glob.glob(RASTER_FOLDER = WORLDCOVER_PATH  + "/tiles/"
 + "*.tif") #
print(f"Found {len(raster_files)} raster files.")

# Open all raster files and merge them
src_files_to_mosaic = [rasterio.open(fp) for fp in raster_files]
mosaic, mosaic_transform = merge(src_files_to_mosaic)

# Copy the metadata of one of the source files 
out_meta = src_files_to_mosaic[0].meta.copy()
out_meta.update({
    "driver": "GTiff",
    "height": mosaic.shape[1],
    "width": mosaic.shape[2],
    "transform": mosaic_transform,
    "crs": src_files_to_mosaic[0].crs
})

# Save as GeoTIFF (still in EPSG:4326)
out_fp = WORLDCOVER_PATH+"/worldcover_2021_merged.tif"
with rasterio.open(out_fp, "w", **out_meta) as dest:
    dest.write(mosaic)


# Input: merged raster still in EPSG:4326
src_fp = WORLDCOVER_PATH+"/worldcover_2021_merged.tif"

# Output: reprojected raster
dst_fp = WORLDCOVER_PATH+"/worldcover_2021_merged_epsg2056.tif"

#Open the source raster and perform the reprojection.
#This might take a while depending on the size of the raster and your computer performance
with rasterio.open(src_fp) as src:
    transform, width, height = calculate_default_transform(
        src.crs, "EPSG:2056", src.width, src.height, *src.bounds
    )

    kwargs = src.meta.copy()
    kwargs.update({
        "crs": "EPSG:2056",
        "transform": transform,
        "width": width,
        "height": height
    })

    with rasterio.open(dst_fp, "w", **kwargs) as dst:
        for i in range(1, src.count + 1):
            reproject(
                source=rasterio.band(src, i),
                destination=rasterio.band(dst, i),
                src_transform=src.transform,
                src_crs=src.crs,
                dst_transform=transform,
                dst_crs="EPSG:2056",
                resampling=Resampling.nearest  # keep categorical values intact
            )

#Load merged and transformed raster and geopakage with the buffered border
with rasterio.open(dst_fp) as r:
    print(r.crs)
    print(r.count, r.width, r.height)

# Clip the raster to the buffered border
raster_path = WORLDCOVER_PATH + "/worldcover_2021_merged_epsg2056.tif"
mask_path = WORLDCOVER_PATH  + "/swiss_border_buffered_1km.gpkg"
mask_gdf = gpd.read_file(mask_path)
mask_geom = [mask_gdf.union_all()]  # Combine if multiple polygons
with rasterio.open(raster_path) as src:
    clipped_array, clipped_transform = mask(
        dataset=src,
        shapes=mask_geom,
        crop=True,
        nodata=0
    )
    clipped_meta = src.meta.copy()

clipped_meta.update({
    "driver": "GTiff",
    "height": clipped_array.shape[1],
    "width": clipped_array.shape[2],
    "transform": clipped_transform,
})

out_path = WORLDCOVER_PATH + "worldcover_2021_clipped.tif"
with rasterio.open(out_path, "w", **clipped_meta) as dest:
    dest.write(clipped_array)
