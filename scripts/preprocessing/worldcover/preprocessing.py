
import os
import glob
import geopandas as gpd
import rasterio
from shapely.geometry import Polygon, MultiPolygon
from rasterio.merge import merge
from rasterio.warp import calculate_default_transform, reproject, Resampling
from rasterio.mask import mask

def process_worldcover(year):
    from scripts import DATA_DIR
    """
    Führt die Verarbeitung der WorldCover-Daten für das angegebene Jahr durch.
    
    Schritte:
      1. Buffer der Schweizer Grenze um 1 km
      2. Zusammenführen der WorldCover-Kacheln
      3. Reprojektion nach EPSG:2056
      4. Clipping auf die gepufferte Grenze
    
    Parameter:
      year (int): Jahr der WorldCover-Daten (z. B. 2020 oder 2021)
    """

    # --- Umgebungsvariablen (falls nötig für GDAL/PROJ) ---
    os.environ["PROJ_LIB"] = r"C:\Users\alexa\anaconda3\envs\WC\Library\share\proj"
    os.environ["GDAL_DATA"] = r"C:\Users\alexa\anaconda3\envs\WC\Library\share\gdal"
    # --- Pfade definieren ---
    worldcover_path = DATA_DIR /"preprocessing" / "worldcover" / str(year)
    raster_folder = worldcover_path / "tiles"
    gpkg_path = DATA_DIR / "base" / "swissBOUNDARIES3D" / "swissBOUNDARIES3D_1_5_LV95_LN02.gpkg"
    
    # --- Grenze laden und puffern ---
    border_gdf = gpd.read_file(gpkg_path, layer="tlm_landesgebiet")
    buffered_border_gdf = border_gdf.copy()
    buffered_border_gdf["geometry"] = buffered_border_gdf.buffer(1000)  # 1 km Buffer

    # Löcher füllen
    def fill_all_holes(geom):
        if geom.type == 'Polygon':
            return Polygon(geom.exterior)
        elif geom.type == 'MultiPolygon':
            return MultiPolygon([Polygon(g.exterior) for g in geom.geoms])
        else:
            return geom

    buffered_border_gdf["geometry"] = buffered_border_gdf.geometry.apply(fill_all_holes)

    print(f"Buffered border for {year} created.")
    buffer_path = worldcover_path / f"swiss_border_buffered_1km_{year}.gpkg"
    buffered_border_gdf.to_file(buffer_path, driver="GPKG")
    print(f"Buffered border saved to {buffer_path}.")

    # --- Rasterdateien zusammenführen ---
    raster_files = list(raster_folder.glob("*.tif"))
    print(f"Found {len(raster_files)} raster files for {year}.")
    if not raster_files:
        raise FileNotFoundError(f"Keine Rasterdateien gefunden unter: {raster_folder}")

    src_files_to_mosaic = [rasterio.open(fp) for fp in raster_files]
    mosaic, mosaic_transform = merge(src_files_to_mosaic)

    out_meta = src_files_to_mosaic[0].meta.copy()
    out_meta.update({
        "driver": "GTiff",
        "height": mosaic.shape[1],
        "width": mosaic.shape[2],
        "transform": mosaic_transform,
        "crs": src_files_to_mosaic[0].crs
    })

    merged_fp = worldcover_path / f"worldcover_{year}_merged.tif"
    with rasterio.open(merged_fp, "w", **out_meta) as dest:
        dest.write(mosaic)

    # --- Reprojektion ---
    reprojected_fp = worldcover_path / f"worldcover_{year}_merged_epsg2056.tif"
    with rasterio.open(merged_fp) as src:
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

        with rasterio.open(reprojected_fp, "w", **kwargs) as dst:
            for i in range(1, src.count + 1):
                reproject(
                    source=rasterio.band(src, i),
                    destination=rasterio.band(dst, i),
                    src_transform=src.transform,
                    src_crs=src.crs,
                    dst_transform=transform,
                    dst_crs="EPSG:2056",
                    resampling=Resampling.nearest
                )

    # --- Clipping ---
    mask_gdf = gpd.read_file(buffer_path)
    mask_geom = [mask_gdf.union_all()]
    clipped_fp = worldcover_path / f"worldcover_{year}_clipped.tif"

    with rasterio.open(reprojected_fp) as src:
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
            "transform": clipped_transform
        })

    with rasterio.open(clipped_fp, "w", **clipped_meta) as dest:
        dest.write(clipped_array)

    print(f"✅ Verarbeitung für {year} abgeschlossen.")
    print(f"Ergebnis gespeichert unter: {clipped_fp}")


# Beispielaufruf:
# define data paths for worlcover files

# process_worldcover(2020)
process_worldcover(2021)
