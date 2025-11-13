import os
import geopandas as gpd
import rasterio
from rasterio.mask import mask
from scripts.analysis.worldcover.maxarea_harmonisation import maxarea_harmonisation
from scripts.analysis.worldcover.centerpoint_harmonisation import centerpoint_harmonisation

os.environ["PROJ_LIB"] = r"C:\Users\alexa\anaconda3\envs\WC\Library\share\proj"
os.environ["GDAL_DATA"] = r"C:\Users\alexa\anaconda3\envs\WC\Library\share\gdal"

from scripts import DATA_DIR

ANALYSES_PATH = DATA_DIR / "analysis" / "worldcover" 
PREPROCESSING_PATH = DATA_DIR  / "preprocessing"/"worldcover"/"2020"
WORLDCOVER = PREPROCESSING_PATH / "worldcover_2020_clipped.tif"
AREALSTATISTIC =  DATA_DIR / "analysis"/"arealstatistik"/"ag-b-00.03-37-area-all-gpkg_zug.gpkg"

# RASTER ZUSCHNEIDEN AUF STUDIENGEBIET ZUG
mask_gdf = gpd.read_file(AREALSTATISTIC)
mask_geom = [mask_gdf.union_all()]  # Combine if multiple polygons
with rasterio.open(WORLDCOVER) as src:
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
out_path =  ANALYSES_PATH/"worldcover_2020_clipped_zug.tif"
with rasterio.open(out_path, "w", **clipped_meta) as dest:
    dest.write(clipped_array)



def vergleichsanalyse(harmonised):
    import pandas as pd
    import matplotlib.pyplot as plt
    from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay
    polygons = harmonised.copy()
    # Excel-Mappingtabelle laden
    mapping_df = pd.read_excel(DATA_DIR/"analysis"/"worldcover"/"Mapping_AS_WC.xlsx")

    # Angenommen, die Excel-Datei hat zwei Spalten: "AS18_72" und "WorldCover_class"
    # Erstelle ein Mapping-Dictionary
    mapping_dict = dict(zip(mapping_df["AS18_72"], mapping_df["WorldCover_class"]))

    # Neue Spalte mit WorldCover Klassen erstellen basierend auf der Zuordnung
    polygons["AS_auf_WorldCover"] = polygons["AS18_72"].map(mapping_dict)

    # Fehlende Werte mit -1 ersetzen, ohne inplace=True
    polygons["AS_auf_WorldCover"] = polygons["AS_auf_WorldCover"].fillna(-1)
  
    #------------------------------------------------------------------------------------------#
    # Klassen vergleichen
    #------------------------------------------------------------------------------------------#
    
    y_true = polygons["AS_auf_WorldCover"]
    y_pred = polygons["WorldCover_2020_class"]

    # Alle Klassen bestimmen
    labels = sorted(set(y_true).union(set(y_pred)))

    # Confusion Matrix erstellen
    cm = confusion_matrix(y_true, y_pred, labels=labels)

    # Deutsche Achsen und Matrix anzeigen
    plt.figure(figsize=(8, 6))
    disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=labels)
    disp.plot(cmap="YlOrRd", xticks_rotation=45)
    plt.title("Vergleich Arealstatistik zu WorldCover (Confusion Matrix)")
    plt.xlabel("WorldCover Klasse (Vorhersage)")
    plt.ylabel("Arealstatistik Klasse (Wahrheit)")
    plt.tight_layout()
    plt.show()

    # Kreuztabelle erstellen:
    crosstab = pd.crosstab(
        polygons["AS18_72"],                      # Zeilen: originale AS Klassen
        polygons["WorldCover_2020_class"],      # Spalten: WorldCover Klassen
        rownames=["AS18_72"],               # Deutsche Achsen-Beschriftungen
        colnames=["WorldCover_2020_class"]
    )

    # Tabelle zeigen/prüfen
    print(crosstab)
    return crosstab
 



# Polygonlayer laden
points = gpd.read_file(AREALSTATISTIC)
# Pfad zum Raster
# worldcover_raster Pfad erstellen (Path-Objekt)
worldcover_raster = ANALYSES_PATH / "worldcover_2020_clipped_zug.tif"
# Datensätze Harmonisierung mit maxarea-Methode
# harmonised_maxarea = maxarea_harmonisation(points, worldcover_raster)
# harmonised_maxarea.to_file(
#     ANALYSES_PATH / "maxarea" / "arealstatistik_grid_zug_100m_with_wc_top3.gpkg",
#     driver="GPKG"
# )
# crosstab = vergleichsanalyse(harmonised_maxarea)
# # Optional: Als Excel oder CSV abspeichern
# crosstab.to_csv(ANALYSES_PATH / "maxarea" / "AS_WC_kreuztabelle_zug.csv")
# crosstab.to_excel(ANALYSES_PATH / "maxarea" / "AS_WC_kreuztabelle_zug.xlsx")

# Datensätze Harmonisierung mit centerpoint-Methode
harmonised_centerpoint = centerpoint_harmonisation(points, worldcover_raster)
harmonised_centerpoint.to_file(
    ANALYSES_PATH / "centerpoint" / "arealstatistik_grid_zug_100m_with_wc_top3.gpkg",
    driver="GPKG"
)
crosstab = vergleichsanalyse(harmonised_centerpoint)
# Optional: Als Excel oder CSV abspeichern
crosstab.to_csv(ANALYSES_PATH / "centerpoint" / "AS_WC_kreuztabelle_zug.csv")
crosstab.to_excel(ANALYSES_PATH / "centerpoint" / "AS_WC_kreuztabelle_zug.xlsx")
