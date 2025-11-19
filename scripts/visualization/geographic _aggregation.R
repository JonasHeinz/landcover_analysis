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
# Beispiel: Klassen erstellen
# Definierte Farben für den Verlauf von niedrig zu hoch
my_colors <- c("#fef0d9", "#fdcc8a", "#fc8d59", "#e34a33", "#b30000")

# Plot
p <- ggplot(result) +
  geom_sf(aes(fill = change_percent), color = NA) +
  geom_sf_text(aes(label = name), size = 3, color = "black") +  # Gemeindenamen hinzufügen
  scale_fill_gradientn(colors = my_colors, name = "Änderung (%)") +
  annotation_scale(
    location = "bl",
    width_hint = 0.2,
    unit_category = "metric",
    bar_cols = c("black", "white"),
    line_width = 1
  ) +
  annotation_north_arrow(
    location = "tr",
    which_north = "true",
    style = north_arrow_fancy_orienteering(),
    height = unit(2, "cm"),  # Höhe des Pfeils
    width  = unit(2, "cm")   #
  ) +
  labs(
    title = "Prozentuale Änderungen der Landnutzung pro Gemeinde im Kanton Zug",
    subtitle = "Die Werte zeigen, wie viel Prozent der Gemeindefläche sich zwischen Arealstatistik und ESA WorldCover sich unterscheiden",
    caption = "Datenquelle: Arealstatistik 2018 & ESA WorldCover 2020"
  ) +
  theme_minimal() +
  theme(axis.text = element_blank(),
        axis.ticks = element_blank(), 
        panel.grid = element_blank(),
        axis.title.x = element_blank(), # Achsentitel entfernen
        axis.title.y = element_blank(), # Achsentitel entfernen
        axis.text.x = element_blank(), # Achsentext entfernen
        axis.text.y = element_blank(), # Achsentext entfernen
        plot.title = element_text(face = "bold", size = 16),
        plot.subtitle = element_text( size = 11)
        ) # Achsengitter entfernen

ggsave(
  filename = "data/visualizations/landnutzung_aenderung_pro_gemeinde_zug.pdf",
  plot = p,
  width = 10,
  height = 8
)

print(p)


# ---------------------------------------------------
# Mini-Karten + Balkendiagramme pro Gemeinde erzeugen
# ---------------------------------------------------
# ----------------------------
# Kartenbasis vorbereiten: nur Kanton Zug
# ----------------------------
karte <- gemeinden %>% summarise()  

# Sicherstellen, dass die Prozentwerte existieren
result <- result %>%
  mutate(correct_percent = 100 - change_percent)

# Liste zum Sammeln der Panels
plots_list <- list()

# Durch alle Gemeinden iterieren
for (g in result$name) {
  
  gemeinde_poly <- result %>% filter(name == g)
  changes_g <- st_intersection(changes, gemeinde_poly)
  
  # ----------------------------
  # 1) Karte von Zug mit Highlight der Gemeinde
  # ----------------------------
  map_plot <- ggplot() +
    geom_sf(data = karte, fill = "grey95", color = "white") +
    geom_sf(data = gemeinde_poly, fill = "red", alpha = 0.8) +
    labs(title = g) +
    theme_void() +
    theme(
      plot.title = element_text(size = 12, face = "bold")
    )
  
  # ----------------------------
  # 2) Balkendiagramm
  # ----------------------------
  df_bar <- data.frame(
    category = c("Richtig", "Falsch"),
    value = c(gemeinde_poly$correct_percent, gemeinde_poly$change_percent)
  )
  
  bar_plot <- ggplot(df_bar, aes(x = category, y = value, fill = category)) +
    geom_col() +
    scale_fill_manual(values = c("Richtig" = "darkgreen", "Falsch" = "red")) +
    labs(y = "Prozent", x = NULL) +
    theme_minimal() +
    theme(
      legend.position = "none",
      axis.title.x = element_blank()
    )
  
  # ----------------------------
  # 3) Panel horizontal
  # ----------------------------
  panel <- map_plot + bar_plot + plot_layout(widths = c(2, 1))
  plots_list[[g]] <- panel
}

# ----------------------------
# Alle Panels untereinander
# ----------------------------
final_plot <- wrap_plots(plots_list, ncol = 1)

# ----------------------------
# Speichern
# ----------------------------
ggsave("data/visualizations/alle_gemeinden_vertical.pdf",
       final_plot,
       width = 10, height = 3 * length(plots_list))

print(final_plot)
