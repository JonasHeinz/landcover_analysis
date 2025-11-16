# -----------------------------
# Pakete laden
# -----------------------------
library(sf)
library(dplyr)
library(ggplot2)
library(ggspatial) # für Maßstab & Nordpfeil

# -----------------------------
# Dateipfade
# -----------------------------
gemeinden_path <- "data/base/swissBOUNDARIES3D/swissBOUNDARIES3D_1_5_LV95_LN02.gpkg"
mapped_wc_path <- "data/analysis/worldcover/maxarea/arealstatistik_zug_mapped.gpkg"


# -----------------------------
# Daten laden
# -----------------------------
gemeinden <- st_read(gemeinden_path, layer = "tlm_hoheitsgebiet") %>%
  filter(kantonsnummer == 9)  # Kanton Zug

changes <- st_read(mapped_wc_path) %>%
  filter(AS_auf_WorldCover != WorldCover_2020_class_1)  # nur Änderungen

# -----------------------------
# Aggregation Funktion
# -----------------------------
aggregate_lulc_percent <- function(changes, targets, target_id = "name") {

# Spatial Join: jede Änderung bekommt die Info der Gemeinde
joined <- st_join(changes, gemeinden, join = st_intersects)

# Fläche der Änderungen berechnen
joined <- joined %>%
  mutate(change_area_m2 = st_area(.))

# Aggregation pro Gemeinde
agg <- joined %>%
  group_by(name) %>%
  summarise(change_area_m2 = sum(change_area_m2)) %>%
  ungroup()

# Gesamtfläche der Gemeinden
gemeinden <- gemeinden %>%
  mutate(total_area_m2 = st_area(.))

# Mergen / Join
agg_df <- agg %>% st_set_geometry(NULL) # entfernt Geometrie
result <- left_join(gemeinden, agg_df, by = "name") %>%
mutate(
  change_area_m2 = ifelse(is.na(change_area_m2), 0, change_area_m2),
  change_percent = as.numeric(change_area_m2 / total_area_m2 * 100)
)
return(result)
}

# -----------------------------
# Aggregation durchführen
# -----------------------------
result <- aggregate_lulc_percent(changes, gemeinden, target_id = "name")

# -----------------------------
# Ergebnis speichern
# -----------------------------
st_write(result, "data/analysis/worldcover/maxareageographic_aggregation_zug.gpkg", delete_dsn = TRUE)

# -----------------------------
# Karte plotten mit ggplot2 + ggspatial
# -----------------------------
p <- ggplot(result) +
  geom_sf(aes(fill = change_percent), color = "black", size = 0.2) +
  scale_fill_viridis_c(option = "YlOrRd", name = "Änderung (%)") +
  annotation_scale(location = "bl", width_hint = 0.7) +   # Maßstab unten links
  annotation_north_arrow(location = "tr", which_north = "true",
                         style = north_arrow_fancy_orienteering()) + # Nordpfeil oben rechts
  labs(title = "LULC Veränderungen in % der Gemeindefläche") +
  theme_minimal() +
  theme(axis.text = element_blank(), axis.ticks = element_blank())
