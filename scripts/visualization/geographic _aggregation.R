# -----------------------------
# Pakete laden
# -----------------------------
library(sf)
library(dplyr)
library(ggplot2)
library(ggspatial)  # für Maßstab & Nordpfeil
library(patchwork)  # für Multi-Panel Layouts



# -----------------------------
# Aggregation Funktion: Prozentuale Änderungen pro Gemeinde
# -----------------------------
aggregate_lulc_percent <- function(changes, targets, target_id = "name", title, subtitle, rowtitle) {
  
  # Spatial Join: Jede Änderung bekommt die Info der Gemeinde
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
  
  # Zusammenführen
  agg_df <- agg %>% st_set_geometry(NULL)  # Geometrie entfernen
  result <- left_join(gemeinden, agg_df, by = "name") %>%
    mutate(
      change_area_m2 = ifelse(is.na(change_area_m2), 0, change_area_m2),
      change_percent = as.numeric(change_area_m2 / total_area_m2 * 100)
    )
  
  st_write(result, "data/analysis/worldcover/aggregated_as_kantone.gpkg", layer = "change")


# -----------------------------
# Mini-Karten + Balkendiagramme pro Gemeinde
# -----------------------------
karte <- gemeinden %>% summarise()
result <- result %>% mutate(correct_percent = 100 - change_percent) %>%
  arrange(desc(correct_percent))

plots_list <- list()

for (g in result$name) {
  gemeinde_poly <- result %>% filter(name == g)
  
  # Titel Panel
  title_plot <- ggplot() +
    annotate("text", x = 0.05, y = 0.5, label = g, size = 4, hjust = 0) +
    xlim(0, 1) + ylim(0, 1) +
    theme_void()
  
  # Karte Panel
  map_plot <- ggplot() +
    geom_sf(data = karte, fill = NA, color = "black") +
    geom_sf(data = gemeinde_poly, fill = "black", alpha = 0.8, color = NA) +
    theme_void()
  
  # Balken Panel
  cp  <- gemeinde_poly$correct_percent
  chp <- gemeinde_poly$change_percent
  
  legend_df <- data.frame(
    IPCC_Match = c("TRUE", "FALSE"),
    perc = c(cp, chp)
  ) %>%
    mutate(perc = as.numeric(perc),
           cum = cumsum(perc),
           pos = cum - perc/2)
  
  bar_plot <- ggplot(legend_df, aes(x = "bar", y = perc, fill = IPCC_Match)) +
    geom_col() +
    scale_fill_manual(values = c("TRUE" = "#fee0d2", "FALSE" = "#de2d26")) +
    geom_text(aes(x = "bar", y = pos, label = paste0(round(perc, 1), "%")),
              color = "black", size = 4) +
    coord_flip() +
    theme_minimal() +
    theme(axis.title = element_blank(),
          axis.text = element_blank(),
          axis.ticks = element_blank(),
          panel.grid = element_blank(),
          legend.position = "none")
  
  # Panels kombinieren
  panel <- title_plot + map_plot + bar_plot +
    plot_layout(widths = c(0.25, 0.25, 0.5))
  
  plots_list[[g]] <- panel
}

# -----------------------------
# Globaler Titel + Untertitel
# -----------------------------
global_title <- ggplot() +
  annotate("text", x = 0.5, y = 0.2,
           label = title,
           size = 6, fontface = "bold", hjust = 0.5) +
  theme_void()

global_subtitle <- ggplot() +
  annotate("text", x = 0.5, y = 0.9,
           label = subtitle,
           size = 4, hjust = 0.5) +
  theme_void()

# -----------------------------
# Header: Spaltenüberschriften + globale Legende
# -----------------------------
col_title1 <- ggplot() +
  annotate("text",x = 0, y = 0.5 , label = rowtitle, size = 4, hjust = 0, fontface = "bold")+
  xlim(0, 1) + ylim(0, 1) +
  theme_void()

legend_df_global <- data.frame(
  label = c("Übereinstimmung", "Abweichung"),
  fill  = c("#fee0d2", "#de2d26"),
  x_point  = 1:2,
  y = 1
)

global_legend <- ggplot(legend_df_global, aes(y = y)) +
  geom_point(aes(x = x_point, color = fill), size = 5) +
  geom_text(aes(x = x_point + 0.08, label = label), hjust = 0, size = 4, fontface = "bold") +
  scale_color_identity() +
  xlim(1, 2.5) + ylim(0.8, 1.2) +
  theme_void()

header_row <- (col_title1 + global_legend) +
  plot_layout(widths = c(1, 1))

# -----------------------------
# Alle Panels zusammenfügen
# -----------------------------
plots_list_all <- c(list(global_title), list(global_subtitle), list(header_row), plots_list)
final_plot <- wrap_plots(plots_list_all, ncol = 1) +
  plot_annotation(theme = theme(
    plot.margin = margin(t = 30, r = 30, b = 30, l = 30) # oben, rechts, unten, links
  ))


return(final_plot)
}

# -----------------------------
# Funktionsaufruf
# -----------------------------

gemeinden_path <- "data/base/swissBOUNDARIES3D/swissBOUNDARIES3D_1_5_LV95_LN02.gpkg"
mapped_wc_path <- "data/analysis/worldcover/maxarea/arealstatistik_mapped_2021.gpkg"


gemeinden <- st_read(gemeinden_path, layer = "tlm_kantonsgebiet")

changes <- st_read(mapped_wc_path) %>%
  filter(AS_auf_WorldCover != WorldCover_2020_class_1)  # nur Änderungen

result <- aggregate_lulc_percent(changes, 
                                 gemeinden, 
                                 target_id = "name", 
                                 "Übereinstimmung der Klassifikation pro Kanton", 
                                 "Vergleich der ESA Landnutzungsklassifikation 2021 mit der Arealstatistik (in Prozent)",
                                 "Kantonsname & Position"
                                 )
print(result)
ggsave(
  "data/visualizations/lulcc_pro_kanton_esa_2021.pdf",
  plot = result,
  width = 10, height = 15, dpi = 300
)
0

