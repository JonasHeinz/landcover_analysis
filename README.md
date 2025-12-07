# LULC Analysis | Landuse and Landcover Analysis

Landnutzungs- und Landbedeckungsdaten (LULC) spielen eine zentrale Rolle in Umweltanalysen, der Raumplanung und der Klimaberichterstattung. In der Schweiz existieren mehrere nationale und internationale Datensätze, die sich in Auflösung, Klassifikation, Erfassungsmethode und zeitlicher Abdeckung unterscheiden. Diese Heterogenität erschwert ihre direkte Vergleichbarkeit sowie die Integration in das internationale Bewertungssysteme IPCC. Ziel dieser Arbeit ist es, die Datensätze Arealstatistik, Amtliche Vermessung, CORINE Land Cover sowie ESA WorldCover hinsichtlich ihrer thematischen, räumlichen und zeitlichen Eigenschaften systematisch zu vergleichen und deren Eignung für konsistente LULC-Analysen zu beurteilen.
Die Arbeit beinhaltet eine umfassende Literaturrecherche zu Harmonisierungsmethoden, Unsicherheitsquellen und Klassifikationslogiken, gefolgt von einer methodischen Aufarbeitung aller Datensätze und deren Überführung in das Intergovernmental Panel on Climate Change (IPCC)-Kompatible Kategorienmodell. Mittels Raster- und Vektoranalysen, punktbasierter Validierung und statistischen Genauigkeitsmetriken wie «accuracy», «F1-Score» und «Cohen’s Kappa» wird die Übereinstimmung der Datensätze mit der Arealstatistik als Referenz bewertet. Ergänzend werden zeitliche Veränderungen analysiert sowie erste Szenario basierte Interpolations- und Modellierungsansätze mittels Cellular Automata und Markov-basierten Methoden angeschaut. Interaktive Visualisierungen unterstützen die räumliche Interpretation der Ergebnisse.
Die Resultate zeigen deutliche Qualitätsunterschiede zwischen den Datensätzen. Während die Bodenbedeckung der Amtlichen Vermessung thematisch und geometrisch detailliert ist, weist sie im Abgleich mit der Arealstatistik die geringste Übereinstimmung auf. CORINE 2018 liefert konsistentere Resultate als CORINE 2012, bleibt jedoch klar hinter den ESA WorldCover-Produkten zurück. WorldCover 2020 und insbesondere WorldCover 2021 erreichen die höchsten Genauigkeitswerte und stellen damit die zuverlässigste Grundlage für nationale LULC-Vergleiche im Kontext des IPCC dar. Die Analyse verdeutlicht zudem, dass methodische Harmonisierung, transparente Unsicherheitsbewertung und geeignete Transformationen zentrale Voraussetzungen für eine robuste Nutzung heterogener LULC-Daten sind.

---

Genauere Informationen bezüglich Literatur und Vorgehen kann unter https://jonasheinz.github.io/landcover_analysis/ gefunfen werden.

## Voreinstellungen

Das Git-Repo auf lokalen PC klonen. Ordnerstrucktur nicht anpassen! <br>
Die für die verschiednen Skripts benötigten Lybaries sind alle im _Requirements.txt_ zu finden.

## Preprocessing

Alle Datensätze müssen in den Ordner Data/ Preprocessing und anschliessendn in den ensprechenden Ordner abgelegt werden. der Ganze Ablauf wird Datengetrennt gehlaten. Der ganze Prozess muss pro Datenwuelle einzeln durchgeführt werden.

| Datensatz           | Skritps                                                |
| ------------------- | ------------------------------------------------------ |
| Corine              | _pp_corine_raster.ipynb_ oder _pp_corine_vector.ipynb_ |
| Amtliche Vermessung | _Vollstaendigkeit_                                     |
| ESA WordCover       | _preprocessing.py_                                     |

## Analyse

Die Daten werden durch den Preprocessing Schritt im Ordner Analysis oder Preprocessing abgelegt. Dies wird je nach Datensatz in diesem Schritt wieder richtig aufgegriffen und muss nicht angepasst werden.

| Datensatz           | Skritps                                  |
| ------------------- | ---------------------------------------- |
| Corine              | _center_area.py_ oder _maximal_area.py_  |
| Amtliche Vermessung | _center_pixel.py_ oder _maximal_Area.py_ |
| ESA WordCover       | _vergleichsanalyse.py_                   |

### Zeitvergleich

Bei den Datensätzen ESA WordCover, Corine sowie Arealstatistik kann ein Zeitvergleichs durchgeführt werden

| Datensatz     | Skritps                              |
| ------------- | ------------------------------------ |
| Corine        | _vector_zeitvergleich_pro_kanton.py_ |
| ESA WordCover | _zeitvergleich.py_                   |

## Qualitätstest

Das Jupyternotebook _Qualitaet.ipynb_ beinhaltet in der ersten Zelle die Funktion die Folgenden Zellen sind die einzelnen Datensätze angegeben. <br>
Die Pfade und Dateinamen müssen auf richtigkeit überprüft und auf evt. Individuelle Namensgebung angepasst werden.

| Variabeln  | Erklährung                                    |
| ---------- | --------------------------------------------- |
| gdf        | Geodataframe                                  |
| field_true | als Richtig anerkanntes Feld (arealstatistik) |
| field_pred | Das Feld dass man vergleichen möchte          |
| csv_path   | Speicherpfad für -csv mit confusion Matrix    |

## Visualisierungen

Mit den erstellten Datensätzen können diverse Visualisierungen erstellt werden.
| Skripte | Erklährung |
| ---------- | --------------------------------------------- |
| Vis_Kategorien.ipynb | Grafische Darstellung von Übereinstimmung mit Analytischerlegende |
| DatatoIPCC.py | Mapping Übersicht aller Datensätze auf IPCC (standarmässig Settlment ausgeschalten) |
| matrix_prozentual.py | Confusion Matrix für Präsentation obtimiert |
| geographic_aggregation.R | Visualisierung der Übereinstimmung nach Geometrien aggregiert (Kantone, Gemeinden oder andere Gebiete) |
| Datensätze_Vergleich.R | Vergleich aller datensätze mittels Alluviel Diagramm|
