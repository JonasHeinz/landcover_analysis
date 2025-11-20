# --- Luzern AV-Daten mit BB_CH.gpkg zusammenführen ---

import geopandas as gpd
import pandas as pd

# --- Dateipfade anpassen ---
shp_path = r"C:\Users\aebim\Documents\02_Ausbildung\Studium\05_Semester\5230_Geoniformatik_Raumanalyse\Projektarbeit\03_GitHub\data\preprocessing\av\GEO.AVBBXXXX_V2_PY.shp"       # dein Shapefile
gpkg_path = r"C:\Users\aebim\Documents\02_Ausbildung\Studium\05_Semester\5230_Geoniformatik_Raumanalyse\Projektarbeit\03_GitHub\data\preprocessing\av\BB_CH_Gesamt_ohne_LU.gpkg"    # dein GeoPackage
output_path = r"C:\Users\aebim\Documents\02_Ausbildung\Studium\05_Semester\5230_Geoniformatik_Raumanalyse\Projektarbeit\03_GitHub\data\preprocessing\av\BB_CH_LU.gpkg"   # gewünschte Ausgabe

# --- Daten laden ---
gdf1 = gpd.read_file(shp_path)
gdf2 = gpd.read_file(gpkg_path)

# --- Mapping-Tabellen ---
art_map = {
    0: "Gebäude",
    1: "Strasse, Weg",
    2: "Trottoir",
    3: "Verkehrsinsel",
    4: "Bahn",
    5: "Flugplatz",
    6: "Wasserbecken",
    7: "übrige befestigte Fläche",
    8: "Acker, Wiese, Weide",
    9: "Reben",
    10: "übrige Intensivkultur",
    11: "Gartenanlage",
    12: "Hoch-, Flachmoor",
    13: "übrige humusierte Fläche",
    14: "stehendes Gewässer",
    15: "fliessendes Gewässer",
    16: "Schilfgürtel",
    17: "geschlossener Wald",
    18: "dichte Wytweide",
    19: "offene Wytweide",
    20: "übrige bestockte Fläche",
    21: "Fels",
    22: "Gletscher, Firn",
    23: "Geröll, Sand",
    24: "Abbau, Deponie",
    25: "übrige vegetationslose Fläche"
}

qualitaet_map = {
    0: "AV93",
    1: "PV74",
    2: "PN",
    3: "PEP",
    4: "weitere"
}

# --- gdf1 anpassen ---
gdf1["Art"] = gdf1["ART"].map(art_map)
gdf1["Qualitaet"] = gdf1["QUALITAET"].map(qualitaet_map)
gdf1["BFSNr"] = gdf1["BFS_NR"]
gdf1["Kanton"] = "LU"  # Standardwert

# --- Nur relevante Spalten auswählen ---
gdf1 = gdf1[["BFSNr", "Qualitaet", "Art", "GWR_EGID", "Kanton", "geometry"]]

# --- Fehlende Spalten (aus gpkg_2) ergänzen ---
for col in ["layer", "Path"]:
    if col not in gdf1.columns:
        gdf1[col] = None

# --- Spaltenreihenfolge an gpkg_2 angleichen ---
cols = [c for c in gdf2.columns if c in gdf1.columns or c in ["layer", "Path", "geometry"]]
gdf1 = gdf1[cols]
gdf2 = gdf2[cols]

# --- Zusammenführen ---
merged = gpd.GeoDataFrame(pd.concat([gdf2, gdf1], ignore_index=True), crs=gdf2.crs)

# --- Neues GeoPackage speichern ---
merged.to_file(output_path, driver="GPKG")

print(f"✅ Zusammenführung abgeschlossen: {output_path}")
