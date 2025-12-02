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

Die GitPage ist so aufgebaut, dass jedes Kapitel als eigene Seite vorliegt und direkt geöffnet werden kann. Die theoretischen Grundlagen, Methoden, Datensätze und Ansätze zur Analyse und Harmonisierung von LULC sind in der Seite [Literaturrecherche](02_literaturrecherche.html) dargestellt.

Die vollständige Dokumentation der Datenaufbereitung und Vorprozessierung steht unter [Vorprozessierung](03_vorprozessierung.html). Darauf folgen die drei Vergleichsanalysen zwischen Arealstatistik und weiteren Datensätzen. Die Analyse zwischen Arealstatistik und der amtlichen Vermessung findet sich unter [Arealstatistik – Amtliche Vermessung](04_arealstatistik_vs_av.html). Die Gegenüberstellung von Arealstatistik und CORINE LandCover ist unter [Arealstatistik – CORINE LandCover](05_arealstatistik_vs_corine.html) abgelegt. Der Vergleich zwischen Arealstatistik und ESA WorldCover ist in [Arealstatistik – ESA WorldCover](06_arealstatistik_vs_worldcover.html) dokumentiert. Der zusammenfassende Vergleich aller Resultate steht unter [Vergleich aller Analysen](07_vergleich_aller_analysen.html).

Die zeitliche Entwicklung der LULC-Klassen ist in [Zeitliche Veränderungen](08_zeitliche_veraenderungen.html) dargestellt. Eine verdichtete Darstellung aller Resultate ist in [Ergebnisse](09_ergebnisse.html) abgelegt. Ein methodischer Ansatz zur Prognose und Modellierung von LULC-Änderungen wird unter [Prognose und Modellierung](10_prognose_modellierung.html) beschrieben.

Interaktive Visualisierungen zur Unterstützung der Analyse stehen in [Interaktive Visualisierung](11_interaktive_visualisierung.html). Der Ausblick und die Schlussfolgerungen sind in [Schlussfolgerung](12_schlussfolgerung.html) zusammengefasst. Die verwendeten Quellen und Python-Module sind unter [Quellenverzeichnis](13_quellenverzeichnis.html) dokumentiert.


[↑](#top)

<div style="display: flex; justify-content: space-between;">
  <div>
    <a href="02_literaturrecherche.md">Literaturrecherche →</a>
  </div>
</div>
