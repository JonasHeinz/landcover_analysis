# Datenaufarbeitung

Alle Datensätze wurden heruntergeladen und vorprozessiert, um einen konsistenten Datenstand für die Analyse bereitzustellen. Die Metadaten wurden vereinheitlicht und strukturiert.

---

## Metadaten der verwendeten LULC-Datensätze

Arealstatistik, Amtliche Vermessung, CORINE LandCover und ESA WorldCover werden in den folgenden Abschnitten dokumentiert.

---

## Metadaten Arealstatistik der Schweiz

**Quelle:** Bundesamt für Statistik (BFS)  
**Jahr:** 1979–1985, 1992–1997, 2004–2009, 2013–2018, 2020–2025  
**Koordinatensystem:** EPSG 2056 (LV95)  
**Auflösung:** 100m Stichprobenraster, geometrische Unsicherheit ±50m  

**Erfassungsmethode**  
Luftbilder von swisstopo und Stichprobenraster mit 4.1 Mio. Punkten (BFS 2024b). Punkte repräsentieren 1ha. Klassifikation nach NOLC04, NOLU04 und NOAS04 (BFS 2006, 2013, 2015, 2018).

**Attributstruktur**  
RELI, E_COORD, N_COORD, GMDE, GMDE_HISTID, FJ85–FJ25, METHOD25, REVISION25, ASaa_xx, LCaa_xx, LUaa_xx. Vollständige Beschreibung in BFS 2024a und 2024b.

**Qualität**  
Geometrische Unsicherheit ±50m. Hohe methodische Konsistenz.

**Dokumentation**  
Nomenklatur, Metadaten und Datenbeschreibung über die BFS-Webseite.

**Bemerkungen**  
Nationale Referenz, konsistente Zeitreihe seit Ende der 1970er Jahre.

---

## Metadaten Amtliche Vermessung

**Quelle:** geodienste.ch  
**Jahr:** 2025  
**Koordinatensystem:** EPSG 3035 (ETRS89)  
**Auflösung:** abhängig von Toleranzstufen TS  

**Erfassungsmethode**  
Erhebung gemäss AV93 und VAV Art. 29 (1992).

**Attributstruktur**  
fid, BFSNr., Qualitaet, Art, GWR_EGID, Kanton. Klassen gemäss AV-Bodenbedeckungskatalog (Grüter 2024).

**Klassifikationssystem**  
Attribut Art.

**Qualität**  
TS2 ±0.10m, TS3 ±0.20m, TS4 ±0.50m, TS5 ±1.00m (swisstopo 2024).

**Dokumentation**  
Beschreibungen über geodienste.ch.

**Bemerkungen**  
Vektorbasierte Datengrundlage. Vollständigkeit variiert regional.

---

## Metadaten CORINE Land Cover (CLC)

**Quelle:** EEA  
**Jahr:** 2018  
**Koordinatensystem:** EPSG 4326  
**Auflösung:** 100m Raster, Mindestkartiereinheit 25ha  

**Erfassungsmethode**  
Visuelle Interpretation und halbautomatische Verfahren basierend auf Satellitenbildern (Büttner et al. 2017).

**Attributstruktur**  
CLC_CODE, LABEL3, RGB.

**Klassifikationssystem**  
44 Klassen auf Level 3, hierarchisch aufgebaut.

**Qualität**  
Europaweit harmonisierte Methodik, Validierung über nationale Stellen.

**Dokumentation**  
Produktbeschreibung und Richtlinien des Jahres 2018.

**Bemerkungen**  
Für grossräumige Vergleiche geeignet. Detailgrad in urbanen Gebieten eingeschränkt.

---

## Metadaten ESA WorldCover 10m

**Quelle:** ESA  
**Jahr:** 2021  
**Koordinatensystem:** EPSG 4326  
**Auflösung:** 10m Raster  

**Erfassungsmethode**  
Automatische Klassifikation basierend auf Sentinel 1 und 2, Random Forest (Van De Kerchove et al. 2022).

**Attributstruktur**  
Rasterwerte 10–100.

**Klassifikationssystem**  
11 Klassen. Farben und Codes gemäss ESA-Dokumentation.

**Qualität**  
Globale Abdeckung. Genauigkeit 75 bis 80 Prozent.

**Dokumentation**  
ESA WorldCover und GEE Dokumente.

---

## Vorprozessierung

Alle Datensätze wurden in EPSG 2056 transformiert.  
Für CORINE und WorldCover wurde ein 1km Puffer um die Schweizer Landesgrenze erzeugt und die Datensätze entsprechend zugeschnitten. Exklaven wurden entfernt.

Die Bodenbedeckung der Amtlichen Vermessung wurde geprüft und mit swissBOUNDARIES3D abgeglichen. Gemeinden mit weniger als 99 Prozent Abdeckung wurden ausgeschlossen. Betroffen waren vor allem Wallis und einzelne Gemeinden im Tessin. Luzerner Daten wurden an NOAS04 angepasst und vereinheitlicht. Sämtliche Gemeinden wurden zusammengeführt.

Anschliessend wurden alle Daten in ein Geopackage integriert und die Geometrien geprüft. Rund 150 fehlerhafte Polygone von 7.2 Mio. wurden korrigiert.

Für die Analyse wurde der Kanton Zug als Testgebiet ausgewählt.

---

## Kategorien LULC zu IPCC

Zur Vergleichbarkeit wurden alle Klassenstrukturen auf IPCC Hauptkategorien harmonisiert.  
Für die Arealstatistik wurde die Zuordnungstabelle FOEN 2022 p. 352 genutzt.  
Für CORINE, WorldCover und Amtliche Vermessung wurden eigene Zuordnungen modelliert, geprüft und iterativ angepasst. Für unklare Klassen erfolgte die Prüfung im Testgebiet Zug.

Abbildung 11 zeigt die resultierende Harmonisierung sämtlicher Kategorien.  
Tabellen und Python Skript zur automatischen Generierung der Visualisierung sind im GitHub Repository hinterlegt.

---

<p align="center">
  <img src="Bilder/image12.png" alt="Startseite" style="width: 100%">
</p>

**Abbildung 11:** Zuordnungen der Kategorien aller Datensätze auf die IPCC Kategorien

[↑](#top)


<div style="display: flex; justify-content: space-between;">
  <div>
    <a href="02_literaturrecherche.html">← Literaturrecherche</a>
  </div>
  <div>
    <a href="04_arealstatistik_vs_av.html">Vergleich Arealstatistik vs Amtliche Vermessung →</a>
  </div>
</div>