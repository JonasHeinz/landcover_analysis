import geopandas as gpd

# -------------------------------
# Schritt 1: Layer einlesen (GeoPackage)
# -------------------------------
mbsf = gpd.read_file(
    "C:/Users/aebim/Documents/02_Ausbildung/Studium/05_Semester/5230_Geoniformatik_Raumanalyse/Projektarbeit/Vorprozessierung/04_Vollstaendigkeit/mbsf.gpkg"
)
lcsf = gpd.read_file(
    "C:/Users/aebim/Documents/02_Ausbildung/Studium/05_Semester/5230_Geoniformatik_Raumanalyse/Projektarbeit/Daten/BB_ergaenzung.gpkg"
)
print("Layer eingelesen erfolgreich.")

# -------------------------------
# Schritt 2: Eindeutige ID für mbsf erzeugen
# -------------------------------
if "fid" not in mbsf.columns:
    mbsf = mbsf.reset_index().rename(columns={'index': 'fid'})
print("FID für mbsf erfolgreich erstellt.")

# -------------------------------
# Schritt 3: Fläche jedes mbsf-Polygons berechnen
# -------------------------------
mbsf["area_total"] = mbsf.geometry.area
print("Flächen der mbsf-Polygone berechnet erfolgreich.")

# -------------------------------
# Schritt 4: Overlay zur Berechnung der Schnittflächen
# -------------------------------
intersection = gpd.overlay(mbsf, lcsf, how="intersection")
print("Schnittflächen mit Overlay berechnet erfolgreich.")

# -------------------------------
# Schritt 5: Fläche der Schnittgeometrien berechnen
# -------------------------------
intersection["inter_area"] = intersection.geometry.area
print("Flächen der Schnittgeometrien berechnet erfolgreich.")

# -------------------------------
# Schritt 6: Summiere Schnittflächen pro mbsf-FID
# -------------------------------
inter_sum = intersection.groupby("fid")["inter_area"].sum().reset_index()
print("Schnittflächen pro FID summiert erfolgreich.")

# -------------------------------
# Schritt 7: Prozentwert berechnen und in mbsf übernehmen
# -------------------------------
mbsf = mbsf.merge(inter_sum, on="fid", how="left")
mbsf["inter_area"] = mbsf["inter_area"].fillna(0)
mbsf["cover_percent"] = (mbsf["inter_area"] / mbsf["area_total"]) * 100
print("Prozentwert berechnet und übernommen erfolgreich.")

# -------------------------------
# Schritt 8: Neues GeoPackage speichern
# -------------------------------
mbsf.to_file(
    "C:/Users/aebim/Documents/02_Ausbildung/Studium/05_Semester/5230_Geoniformatik_Raumanalyse/Projektarbeit/Vorprozessierung/04_Vollstaendigkeit/mbsf_abgedeckt.gpkg",
    driver="GPKG"
)
print("Neues GeoPackage gespeichert erfolgreich.")

print("Script erfolgreich abgeschlossen! Feld 'cover_percent' enthält die Abdeckung in Prozent.")
