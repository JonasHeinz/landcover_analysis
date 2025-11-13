def centerpoint_harmonisation(points, worldcover_raster):
    from rasterstats import point_query

    # Rasterwert an jedem Punkt abfragen
    values = point_query(points, worldcover_raster, interpolate='nearest', nodata=0)

    # Werte als neue Spalte speichern
    points["WorldCover_2020_class"] = values

    return points
