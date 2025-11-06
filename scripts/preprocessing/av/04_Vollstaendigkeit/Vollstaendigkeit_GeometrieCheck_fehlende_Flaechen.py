import geopandas as gpd
from shapely.validation import explain_validity, make_valid
import os

# -------------------------------
# Schritt 0: Pfad definieren
# -------------------------------

path = os.getcwd()
path = os.path.normpath(path)  # normalize path separators

gem_CH_datei = r"data\swissBOUNDARIES3D_1_5_LV95_LN02.gpkg"
BB_CH_datei = r"data\preprocessing\av\BB_CH_Gesamt.gpkg"

gem_CH_dir = os.path.join(path,gem_CH_datei)
BB_CH_dir = os.path.join(path,BB_CH_datei)

print("Pfade Definiert")

# -------------------------------
# Schritt 1: Layer einlesen (GeoPackage)
# -------------------------------
Gem_CH = gpd.read_file(gem_CH_datei, layer = "tlm_hoheitsgebiet")

BB_CH = gpd.read_file(BB_CH_dir)
print("Layer einlesen erfolgreich.")

# -------------------------------
# Schritt 2: Eindeutige ID für Gem_CH erzeugen
# -------------------------------
if "fid" not in Gem_CH.columns:
    Gem_CH = Gem_CH.reset_index().rename(columns={'index': 'fid'})
print("FID für Gem_CH erfolgreich erstellt.")

# -------------------------------
# Schritt 3: Fläche jedes Gem_CH-Polygons berechnen
# -------------------------------
Gem_CH["area_total"] = Gem_CH.geometry.area
print("Flächen der Gem_CH-Polygone berechnet erfolgreich.")
print("Gemeindeflächen Berechnet")

# 2. Überprüfen, ob alle Geometrien gültig sind
BB_CH["is_valid"] = BB_CH.geometry.is_valid
print(BB_CH["is_valid"].value_counts())

# 3. Anzeigen der ungültigen Geometrien
invalid = BB_CH[~BB_CH["is_valid"]]
print(invalid.shape)
print(invalid.apply(lambda row: explain_validity(row.geometry), axis=1))

# 4. Reparieren der Geometrien (Shapely 2.x)
BB_CH["geometry"] = BB_CH["geometry"].apply(make_valid)
print("Geometrien repariert.")
# 5. Erneut prüfen
print(BB_CH.geometry.is_valid.value_counts())

# -------------------------------
# Schritt 5: BB Flächen vereinigen für Overlay
# -------------------------------

BB_CH_Union = BB_CH.union_all()
print("BB Flächen vereinigt erfolgreich.")


# -------------------------------
# Schritt 4: Overlay zur Berechnung der Schnittflächen
# -------------------------------

# geometrie aus gdf ziehen
BB_gdf = gpd.GeoDataFrame(geometry=[BB_CH_Union], crs=Gem_CH.crs)

# ausfführung Overlay
differenz_Union = gpd.overlay(Gem_CH, BB_gdf, how="difference")
print("Overlay zur Berechnung der Schnittflächen erfolgreich.")

# -------------------------------
# Schritt 5: Abdeckung in Prozent berechnen
# -------------------------------

differenz_Union["area_diff"] = differenz_Union.geometry.area
differenz_Union["prozent_diff"] = (differenz_Union["area_diff"] / differenz_Union["area_total"]) * 100
print("Abdeckung in Prozent berechnet erfolgreich.")

# -------------------------------
# Schritt 7: erstellen von Mulipolygons für fehlende Abdeckung (fehlende Flächen > 99% Abdeckung)
# -------------------------------
fehlende_Flaeche = differenz_Union[differenz_Union["prozent_diff"] > 99]
print("Fehlende Flächen mit mehr als 99% Abdeckung extrahiert erfolgreich.")
# -------------------------------
# Schritt 8: Neues GeoPackage speichern
# -------------------------------

fehlende_Flaeche.to_file(
    "C:/Users/aebim/Documents/02_Ausbildung/Studium/05_Semester/5230_Geoniformatik_Raumanalyse/Projektarbeit/05_Daten/fehlende_Flaeche.gpkg", layer = "fehlende_Fla", driver="GPKG")
print("Neues GeoPackage mit fehlenden Flächen gespeichert erfolgreich.")