def maxarea_harmonisation(points, worldcover_raster):
    from rasterstats import zonal_stats
    from scripts.helpers import raster_helper
    
    # Quadrat-Geometrien für jeden Punkt erzeugen (100x100 m um Mittelpunkt)
    points["geometry"] = points.geometry.apply(lambda p: raster_helper.calculate_vectorbox(p, 100))
    polygons = points
       
    # Zonal stats für Kategorien zählen (alle Rasterzellen zählen)
    stats = zonal_stats(
        polygons,
        worldcover_raster,
        categorical=True,
        all_touched=True,
        nodata=0,
        geojson_out=False
    )

    # Für alle Polygone
    klass_1 = []
    klass_1_p = []
    klass_2 = []
    klass_2_p = []
    klass_3 = []
    klass_3_p = []

    for stat in stats:
        # Anzahl Zellen pro Klasse, sortieren absteigend
        if not stat:
            # Falls kein Wert (leeres Polygon)
            klass_1.append(-1)
            klass_1_p.append(0)
            klass_2.append(-1)
            klass_2_p.append(0)
            klass_3.append(-1)
            klass_3_p.append(0)
            continue

        gesamt = sum(stat.values())
        sorted_klassen = sorted(stat.items(), key=lambda x: x[1], reverse=True)

        # Top 1
        klass_1.append(sorted_klassen[0][0])
        klass_1_p.append(sorted_klassen[0][1] / gesamt * 100)

        # Top 2 (falls vorhanden)
        if len(sorted_klassen) > 1:
            klass_2.append(sorted_klassen[1][0])
            klass_2_p.append(sorted_klassen[1][1] / gesamt * 100)
        else:
            klass_2.append(-1)
            klass_2_p.append(0)

        # Top 3 (falls vorhanden)
        if len(sorted_klassen) > 2:
            klass_3.append(sorted_klassen[2][0])
            klass_3_p.append(sorted_klassen[2][1] / gesamt * 100)
        else:
            klass_3.append(-1)
            klass_3_p.append(0)

    # Neue Spalten hinzufügen
    polygons["WorldCover_2020_class"] = klass_1
    polygons["WorldCover_2020_class_1_Percent"] = klass_1_p
    polygons["WorldCover_2020_class_2"] = klass_2
    polygons["WorldCover_2020_class_2_Percent"] = klass_2_p
    polygons["WorldCover_2020_class_3"] = klass_3
    polygons["WorldCover_2020_class_3_Percent"] = klass_3_p

    # Ergebnis speichern
    return(polygons)
