# --- Luzern AV-Daten mit BB_CH.gpkg zusammenführen ---

import geopandas as gpd
import pandas as pd

# --- Dateipfade anpassen ---
shp_path = r"C:\Users\st1179523\Documents\GitHub\landcover_analysis\data\preprocessing\av\LUAVBB.shp"       # dein Shapefile
gpkg2_path = r"C:\Users\st1179523\Documents\GitHub\landcover_analysis\data\preprocessing\av\BB_CH_Gesamt_ohne_LU.gpkg"    # dein GeoPackage
output_path = r"C:\Users\st1179523\Documents\GitHub\landcover_analysis\data\preprocessing\av\BB_CH_LU.gpkg"   # gewünschte Ausgabe

# --- Daten laden ---
gdf1 = gpd.read_file(shp_path)
gdf2 = gpd.read_file(gpkg2_path)

# --- Mapping-Tabellen ---
art_map = {
    0: "Gebaeude",
    1: "Strasse_Weg",
    2: "Trottoir",
    3: "Verkehrsinsel",
    4: "Bahn",
    5: "Flugplatz",
    6: "Wasserbecken",
    7: "uebrige_befestigte",
    8: "Acker_Wiese_Weide",
    9: "Reben",
    10: "uebrige_Intensivkultur",
    11: "Gartenanlage",
    12: "Hoch_Flachmoor",
    13: "uebrige_humusierte",
    14: "Gewaesser_stehendes",
    15: "Gewaesser_fliessendes",
    16: "Schilfguertel",
    17: "geschlossener_Wald",
    18: "Wytweide_dicht",
    19: "Wytweide_offen",
    20: "uebrige_bestockte",
    21: "Fels",
    22: "Gletscher_Firn",
    23: "Geroell_Sand",
    24: "Abbau_Deponie",
    25: "uebrige_vegetationslose"
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
