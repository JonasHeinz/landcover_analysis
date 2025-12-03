#	Erkenntnisse der Vergleichsanalysen
Mit der Arealstatistik als Basis und als Abbildung der Wahrheit, sind in den drei weiteren Datensätzen klare Qualitätsunterschiede feststellbar. Dies lässt sich mit den Kennzahlen Accuracy, Precision, Recall, F1-Score und Cohen’s Kappa deutlich abbilden. Die Werte der verschiedenen Vergleiche zur Arealstatistik sind in Tabelle 6 aufgelistet. 
Die Amtliche Vermessung weist dabei insgesamt die schwächste Übereinstimmung auf. Mit einer geringen Accuracy und einem entsprechend niedrigen Recall liefert sie nur eine moderate Klassifikationsqualität. Auch der F1-Score bleibt auf einem eher schwachen Niveau. Das Kappa zeigt, dass zwar eine echte, aber nur begrenzt zuverlässige Übereinstimmung zwischen Referenz- und Testdaten besteht. Die Precision fällt etwas höher aus, was darauf hindeutet, dass mehrheitlich guter Übereinstimmungen, der Datensatz viele Falschklassierungen aufweist. Insgesamt ist dieser Datensatz damit als eher unzuverlässig einzustufen.
CORINE Landcover 2012 schneidet deutlich besser ab als die Amtliche Vermessung und erreicht eine solide pixelweise Übereinstimmung. Accuracy und Recall liegen im oberen Mittelfeld, und auch Precision sowie F1-Score zeigen eine ausgewogene Leistung. Das Kappa weist auf eine gute und zufällige Übereinstimmung hin. Insgesamt bietet CORINE Land Cover 2012 damit eine brauchbare Grundlage.
CORINE Land Cover 2018 liefert eine nahezu gleich starke, jedoch leicht abweichende Leistung im Vergleich zu CORINE Land Cover 2012. Accuracy, Precision, Recall und F1-Score bewegen sich auf einem sehr ähnlichen Niveau und bestätigen insgesamt eine robuste und konsistente Klassifikationsqualität. Das Kappa zeigt ebenfalls eine verlässliche Übereinstimmung. Insgesamt stellt CORINE Land Cover 2018 damit einen Datensatz dar, der qualitativ mit CORINE Land Cover 2012 vergleichbar ist.
Die besten Resultate erzielen jedoch die beiden ESA WorldCover-Datensätze. ESA WorldCover 2021 erreicht die höchste Übereinstimmung aller verglichenen Datensätze. Accuracy, Precision, Recall und F1-Score liegen jeweils deutlich über jenen der übrigen Produkte und zeigen ein sehr harmonisches und starkes Gesamtbild. Das Kappa bestätigt die hohe Klassifikationsqualität und die starke Nähe zwischen vorhergesagten und tatsächlichen Klassen. Dieser Datensatz ist damit der insgesamt verlässlichste und konsistenteste im Vergleich.
Auch ESA WorldCover 2020 zeigt ein sehr gutes Leistungsniveau, liegt jedoch geringfügig unter der Version von 2021. Sämtliche Metriken weisen dennoch auf eine stabile und qualitativ hochwertige Klassifizierung hin, die nur leicht schwächer ausfällt als jene des Nachfolgedatensatzes. Insgesamt bietet ESA WorldCover 2020 ein sehr hohes Qualitätsniveau und ist ebenfalls bestens geeignet für vergleichende LULC-Analysen.
Zusammenfassend zeigt sich damit eine klare Rangordnung der Datensätze: ESA WorldCover 2021 liefert die beste Übereinstimmung, gefolgt von ESA WorldCover 2020. Dahinter liegen CORINE Land Cover 2012 und CORINE Land Cover 2018, die sich qualitativ sehr ähnlich sind. Am Schluss folgt die Amtliche Vermessung, welche deutlich hinter den anderen Produkten zurückbleibt.

| Datensatz                                   | Accuracy | Precision | Recall | F1-Score | Kappa  |
|---------------------------------------------|----------|-----------|--------|----------|--------|
| Amtlichen Vermessung                        | 0.5953   | 0.6511    | 0.5953 | 0.5361   | 0.5064 |
| CORINE Land Cover Vektordatensatz 2012      | 0.7533   | 0.7679    | 0.7533 | 0.7514   | 0.6819 |
| CORINE Land Cover Vektordatensatz 2018      | 0.7517   | 0.7685    | 0.7517 | 0.7504   | 0.6798 |
| ESA WorldCover 2020                         | 0.7854   | 0.8039    | 0.7854 | 0.7752   | 0.7089 |
| ESA WorldCover 2021                         | 0.8085   | 0.8218    | 0.8085 | 0.8016   | 0.7414 |

**Tabelle 6**: Übersichtstabelle der Klassifikationsmetriken, Ergebnisse der besseren Methode 

---

##	Zentrale Ergebnisse im Vergleich der Vergleichsanalysen
CORINE Land Cover von 2018 und die beiden ESA Wordcover Datensätze zeigen eine gute Übereinstimmung und können für Vergleiche zur Arealstatistik verwendet werden (siehe Abbildung 16: Alluvial-Diagramm der LULC-Datensätze). Über alle Datensätze zeigt sich kein Favorit für eine spezifische IPCC-Kategorie. Forestland und Settlements sind die 
IPCC-Kategorien, die gemäss Tabelle 7 Datensatz übergreifend am besten übereinstimmen.
| Datensatz                                   | Forestland | Grassland | Cropland | Settlements | Wetlands | Other Land |
|---------------------------------------------|------------|-----------|----------|-------------|----------|------------|
| Amtlichen Vermessung                        | 84%        | 10%       | 96%      | 50%         | 70%      | 67%        |
| CORINE Land Cover Vektordatensatz 2012      | 82%        | 56%       | 81%      | 61%         | 76%      | 90%        |
| CORINE Land Cover Vektordatensatz 2018      | 85%        | 58%       | 85%      | 64%         | 77%      | 91%        |
| ESA WorldCover 2020                         | 91%        | 80%       | 58%      | 45%         | 98%      | 79%        |
| ESA WorldCover 2021                         | 95%        | 83%       | 59%      | 44%         | 78%      | 83%        |
| Standardabweichung                          | 5.4%       | 29.2%     | 16.7%    | 9.2%        | 10.6%    | 9.8%       |

**Tabelle 7**: Übereinstimmung der IPCC-Kategorien in Prozent
Bezüglich der Methode für den Vergleich hat Cell Center bessere Ergebnisse erzielt. Dies sieht man am Cohen’s Kappa in Tabelle 8. Die beiden LULC-Datensätze ESA Worldcover und CORINE Land Cover weisen einen kleinen Qualitätsunterschied zwischen den Methoden auf, wobei bei der Amtlichen Vermessung ein signifikanter Unterschied feststellbar ist.

| Datensatz                                   | Methode     | Kappa  |
|---------------------------------------------|-------------|--------|
| Amtlichen Vermessung                        | Cell Center | 0.5064 |
|                                             | Max Area    | 0.4575 |
| CORINE Land Cover Vektordatensatz 2012      | Cell Center | 0.6819 |
|                                             | Max Area    | 0.6801 |
| CORINE Land Cover Vektordatensatz 2018      | Cell Center | 0.6798 |
|                                             | Max Area    | 0.6781 |
| ESA WorldCover 2020                         | Cell Center | 0.7089 |
|                                             | Max Area    | 0.6876 |
| ESA WorldCover 2021                         | Cell Center | 0.7414 |
|                                             | Max Area    | 0.7208 |

**Tabelle 8**: Cohen’s Kappa nach Datensatz und Methoden

---
 
##	Diskussion der Ergebnisse aller Vergleichsanalysen
Die ESA WordCover und CORINE Land Cover Datensätze sind mit Satellitenbildern und die Arealstatistik mit Luftbildern erstellt. Die Amtliche Vermessung wird als einziger Datensatz mit terrestrischen Messmethoden erfasst. Dies zeigt sich vor allem in den Kategorien Cropland und Grassland. Die Kategorie Cropland hat die beste Übereinstimmung in der Amtlichen Vermessung, jedoch gibt es sehr viele irrtümlich als Grassland eingestufte. Zum Zeitpunkt der Luftbildaufnahmen sind viele Landwirtschaftsflächen grün. Dies ist in Abbildung 30 gut zu erkennen. Die Amtliche Vermessung bezieht ihre Daten vom Zonenplan, wobei die Arealstatistik auf rein visuellen Aspekten klassiert.
 
<p align="center">
  <img src="Bilder/image36.png" alt="Startseite" style="width: 100%">
</p>

**Abbildung 30**: Luftbild Region Zürichsee
Bezüglich des Einflusses auf die Quantifizierung von CO2-Emissionen muss beachtet werden, dass die Standardabweichungen aus Tabelle 7 miteinbezogen werden. Um diese Werte noch zu verbessern, könnte durch eine spezifische Zuordnung der Kategorien eine genauere Übereinstimmung erzielt werden. Bei diesem Vorgang wurde alles auf die Kategorie des IPCC genormt, was zu der globalen Übereinstimmung führte und die Werte der verschiedenen Datensätze zum Vergleich zuliess. Einige Informationsdetails gingen bei diesem Vorgang jedoch verloren. Die Methode Cell Center ergab wie erwartet die besseren Ergebnisse. Dies ist auf die Methodik wie die LULC-Datensätze erstellt werden zurückzuführen. 


[↑](#top)


<div style="display: flex; justify-content: space-between;">
  <div>
    <a href="08_zeitliche_veraenderungen.html">← Zeitliche Veränderung der LULC-Daten</a>
  </div>
  <div>
    <a href="10_prognose_modellierung.html">Prognose und Vorhersage der LULC-Daten →</a>
  </div>
</div>