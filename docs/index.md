<!-- <!-- <!-- ---
layout: default
title: Vergleich LULC-Datensätze in der Schweiz
--- -->

<a id="top"></a>

# Vergleich LULC-Datensätze in der Schweiz

**_"Wer verstehen will, wie sich Landschaften verändert haben, braucht präzise Daten über ihre Nutzung und Bedeckung."_**

<div style="text-align: center; margin: 20px 0;">
  <video controls style="width: 100%; max-width: 640px; height: auto;">
    <source src="{{ '/Videos/IPCC_Shiny_App.mp4' | relative_url }}" type="video/mp4">
    Dein Browser unterstützt das Video-Tag nicht.
  </video>
</div>

Landnutzungs- und Landbedeckungsdaten (LULC) sind für zahlreiche Bereiche von zentraler Bedeutung. Sie bilden die Grundlage für Umweltanalysen, unterstützen die Raumplanung und werden in der Klimaforschung intensiv genutzt. Unter anderem lassen sich mit ihrer Hilfe Veränderungen in der Landnutzung quantifizieren, Ökosystemleistungen bewerten oder auch Treibhausgasemissionen modellieren (NCCS, 2018). Globale Veränderungen in Landnutzung und Landbedeckung beeinflussen Kohlenstoffkreisläufe, Biodiversität und regionale Klimasysteme erheblich (Matthews et al., 2021). Gleichzeitig erfordert die Umsetzung nationaler Klimaziele, wie sie etwa in der Schweizer Klimastrategie und den CH2018-Klimaszenarien formuliert sind, eine konsistente und vergleichbare Datengrundlage zur Beurteilung von Landnutzungsdynamiken (NCCS, 2018).

## Ausgangslage und Relevanz der LULC-Daten
In der Schweiz werden verschiedene Datensätze zur Erfassung von Landbedeckung und Landnutzung eingesetzt. Die Arealstatistik Schweiz des Bundesamts für Statistik (BFS) erhebt Bodennutzung und Bodenbedeckung in einem 100m-Raster auf Basis von Luftbildinterpretation und ermöglicht dadurch eine langfristige Beobachtung der Landschaftsentwicklung 
(BFS, 2024b). Parallel dazu liefert die Amtliche Vermessung (AV) hochpräzise Informationen zur Bodenbedeckung, insbesondere in Siedlungsgebieten, mit Lagegenauigkeiten im Dezimeterbereich (swisstopo, 2024).
Auch auf europäischer Ebene existieren vergleichbare Datensätze. Das CORINE Land Cover Programm (CLC) stellt einheitliche Landbedeckungsdaten für viele Länder bereit und arbeitet mit einem Mindestkartierstandard von 25ha (Büttner et al., 2017). Ergänzend bieten globale Produkte wie ESA WorldCover (Zanaga et al., 2021) hochaufgelöste, KI-ausgewertete Karten in einem 10m Raster an, die häufig aktualisiert werden.
Trotz dieser Vielfalt bestehen Unterschiede in Klassifikationssystemen, räumlicher Auflösung, methodischer Grundlage und zeitlicher Abdeckung. Diese erschweren die Vergleichbarkeit und die direkte Integration in nationale Analysen. Studien von Leyk et al. (2005) und Black et al. (2023) betonen die Notwendigkeit einer systematischen Harmonisierung von Datensätzen, um Unsicherheiten zu quantifizieren und die Eignung für spezifische Anwendungen zu verbessern.

## Diese Arbeit erfasst die folgenden zentralen Fragestellungen:
•	Wie können nationale und globale LULC-Datensätze trotz unterschiedlicher Klassifikationen, Auflösungen und Genauigkeiten methodisch zusammengeführt werden, um eine bessere und häufigere Abschätzung von LULC-Veränderungen in der Schweiz zu ermöglichen?
•	Mit welcher Auswirkung auf die Vergleichbarkeit unterscheiden sich verschiedenen nationale und globale Landnutzungs- und Landbedeckungsdatensätze in Klassifikation, Auflösung und Genauigkeit und können diese durch methodische Ansätze zusammengeführt werden?
## Aufbau der GitPage

Die GitPage ist so strukturiert, dass alle inhaltlichen Kapitel der Arbeit als eigene gitPage-Seiten vorliegen und direkt sind.

Die Literaturrecherche ist unter [Literaturrecherche](02_literaturrecherche.html) abgelegt und enthält die vollständige Literaturrecherche zu Grundlagen, Methoden, Datensätzen und bestehenden Ansätzen rund um LULC.

Der Abschnitt Vorprozessierung befindet sich in [Vorprozessierung](03_vorprozessierung.html) und dokumentiert die Datenaufbereitung sowie sämtliche Vorprozessierungsschritte.

Die Vergleichsanalysen sind in 4 Seiten strukturiert:  
- Vergleich Arealstatistik - Amtliche Vermessung: [Arealstatistik vs Amtliche Vermessung](04_arealstatistik_vs_av.html)  
- Vergleich Arealstatistik - Corine LandCover: [Arealstatistik vs Corine LandCover](05_arealstatistik_vs_corine.html)  
- Vergleich Arealstatistik - ESA WorldCover: [Arealstatistik vs ESA WorldCover](06_arealstatistik_vs_worldcover.html)  
- Vergleich aller Anlysen: [Vergleich aller Analysen](07_vergleich_aller_analysen.html)

Die zeitliche Vergleichsanalyse liegt in [zeitliche_veraenderungen](08_zeitliche_veraenderungen.html) und zeigt die zeitliche Entwicklung der LULC-Klassen.

Die Zusammenfassung der aller Ergebnisse ist unter [Ergebnisse](09_ergebnisse.html) und fasst die wesentlichen Resultate zusammen.

Ein Ansatz zur Prognose und Modellierung ist gezeigt unter [Prognose Modellierung](10_prognose_modellierung.html) und behandelt Ansätze zur Prognose von LULC-Änderungen.

Die Interaktiven Visualisierungen auf Shiny sind erklärt auf der Seite [Interaktive Visualisierung](11_interaktive_visualisierung.html)

Ausblick und Fazit umfasst den Schluss [Schlussfolgerung](12_schlussfolgerung.html) und die zentralen Erkenntnisse zusammen.

Die Quellen und Verwendeten Pythonmodule sind aufgführt unter: [Quellenverzeichnis](13_quellenverzeichnis.html) 




[↑](#top)

<div style="display: flex; justify-content: space-between;">
  <div>
    <a href="02_literaturrecherche.md">Literaturrecherche →</a>
  </div>
</div>
