# Prognose und Modellierung von LULC-Änderungen

Ziel der Prognose ist die Ableitung plausibler zukünftiger LULC-Zustände aus beobachteten historischen Zeitständen sowie die Interpolation von Zwischenjahren zwischen bekannten Erhebungszeitpunkten. Die Frage stellt sich, ob und wie sich aus bestehenden LULC-Daten mithilfe der in Kapitel 2.9 beschriebenen Modelle und Methoden zuverlässige Interpolationen ableiten lassen oder Szenarien projektiert werden können.

---

##	Methoden und Modellansatz

Für die Prognose und räumliche Modellierung von LULC-Änderungen wird im Rahmen dieser Arbeit der Ansatz von Black et al. (2024) aufgegriffen, der auf einer Kombination aus Random Forest für die Berechnung des Übergangspotentials und einem Cellular Automata Model für die räumliche Allokation basiert. Das Übergangspotential beschreibt die Wahrscheinlichkeit, mit der eine Zelle in eine Zielklasse übergeht, und werden aus erklärenden Variablen wie Topografie, Erreichbarkeit, Klima oder sozioökonomischen Indikatoren abgeleitet. Die räumliche Allokation erfolgt in ebenfalls in einem CA-Verfahren, bei dem jene Zellen umklassiert werden, die die höchsten Übergangspotenziale aufweisen und gleichzeitig den Nachbarschaftsregeln entsprechen. Die technische Umsetzung dieses Ansatzes ist im öffentlichen GitHub-Repository 
LULCC-CH  verfügbar. Die Random Forest Modelle zur Berechnung des Übergangspotentials liegen in R-Skripts im Ordner «Scripts», während die räumliche Allokation über die im Ordner «Model/Dinamica_models» bereitgestellten Dinamica EGO Modelle erfolgt. Der Release mit der Version 1.0.1 vom August 2025 stellt zusätzlich das vollständige Model Setup für das explorative Szenario NCCS SharedEconomics bereit, welches auf den gleichen Übergangsmodellen aufbaut, aber eigene Szenarioparameter verwendet.

---

##	Ergebnisse der Prognose / Interpolation

Für die Umsetzung des beschriebenen Modellansatzes wurde das GitHub-Repository 
LULCC-CH genauer untersucht. Dieses enthält die komplette Verarbeitungskette für die Modellierung der Landnutzungsänderungen. Gesteuert wird alles über das Hauptskript «LULCC_CH_master.R», das Schritt für Schritt weitere Skripts ausführt. Andere Skripts sind für die automatische Datenbeschaffung, die Aufbereitung der LULC-Eingangsdaten, die Erstellung von Prädiktorvariablen, die Modellierung von Landnutzungsübergängen sowie das Setup zur Simulation in Dinamica EGO verwantwortlich.
Im Hauptskript gibt es einen Abschnitt, in dem die benötigten Eingangsdaten automatisch von Zenodo  heruntergeladen werden sollen. Dies funktioniert aber nicht, weil diese Daten nur mit spezieller Berechtigung heruntergeladen werden können. Die automatisierte Datenbeschaffung ist daher momentan nicht möglich. Bei der Ausführung der anderen Skripts kamen weitere Probleme hinzu. Die Modelpipeline verweist auf viele zusätzliche R-Skripts, die nur dann laufen, wenn alle benötigten Pakete korrekt installiert sind. Mehrere dieser Pakete haben jedoch Kompatibilitätsprobleme. Das Paket «doMC» ist unter Windows nicht verfügbar. Die Pakete «rgdal» und «rgeos» sind veraltet und lassen sich nur noch schwer installieren. Stattdessen sollten aktuell «sf» und «terra» verwendet werden. Aufgrund dieser technischen Einschränkungen konnte der bereitgestellte Workflow nicht vollständig ausgeführt werden. Um das Projekt nutzbar zu machen, müsste der Programmcode aktualisiert und an moderne R-Pakete angepasst werden.
Trotzdem zeigt das GitHub-Repository gut, wie der Modellansatz von Black et al. (2024) technisch aufgebaut ist. Für eine eigene Anwendung wären jedoch Anpassungen und eine alternative Datenbeschaffung notwendig. 


[↑](#top)


<div style="display: flex; justify-content: space-between;">
  <div>
    <a href="09_ergebnisse.html">← Ergebnisse</a>
  </div>
  <div>
    <a href="11_interaktive_visualisierung.html">Interaktive Visualisierungen →</a>
  </div>
</div>