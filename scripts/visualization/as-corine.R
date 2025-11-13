# Pakete laden
library(sf)
library(ggplot2)
library(dplyr)
library(patchwork)

# --------------
# Datengrundlage
# --------------


# Geopackage laden
gdf <- st_read("data/analysis/corine/2018/result_zug.gpkg")

# Dataframe für die Legende erstellen
legend_df <- gdf |>
  st_drop_geometry() |> # Entfernen der Geometrie
  count(IPCC_Match) |> # Erstellen eines Dataframes mit den Kategorien und Anzahl Zeilen der Kategorien
  mutate(
    perc = n / sum(n) * 100,
    IPCC_Match = factor(IPCC_Match, levels = c("TRUE", "FALSE"))
  ) # Hinzufügen einer Spalte mit den Prozentwerten der Kategorie


# --------------
# Visualisierung
# --------------


# Kartendarstellung
map_plot <- ggplot(gdf) +
  
  geom_sf(
    aes(fill = IPCC_Match) # Definieren der Füllung nach der Spalte IPCC_Match
  )+ 
  
  scale_fill_manual(
    values = c("TRUE" = "#fee0d2", "FALSE" = "#de2d26") # Festlegen der Farbwerte für TRUE und FALSE
  )+ 
  
  theme_minimal()+
  
  theme(
    plot.title = element_text(hjust = 0.5), # Zentrieren des Titels
    legend.position = "none" # Entfernen der Legende (wird durch eine analytische Legende abgebildet)
  )+ 
  
  ggtitle("Vorkommen von Klassifikationsunterschieden pro Flächeneinheit der Arealstatistik") # Festlegen des Titels


# Analytische Legende
bar_plot <- ggplot(legend_df, aes(x = IPCC_Match, y = perc)) +
  
  geom_col(
    aes(fill = IPCC_Match), # Definieren der Füllung nach der Spalte IPCC_Match 
    width = 0.5 # Festlegen der Balkenbreite
  )+ 
  
  scale_fill_manual(
    values = c("TRUE" = "#fee0d2", "FALSE" = "#de2d26"), # Festlegen der Farbwerte für TRUE und FALSE
  )+  
  
  scale_x_discrete(
    labels = c("TRUE" = "Übereinstimmende\nKlassifikation", "FALSE" = "Abweichende\nKlassifikation")
  )+
  
  geom_text( 
    aes(label = paste0(round(perc, 1), "%")), # Anzeigen einer Prozentzahl auf eine Kommastelle gerundet
    vjust = -0.5, # Aneigen der Werte oberhalb des Balkens
    size = 5 # Festlegen der Schriftgrösse
  )+
  
  theme_minimal()+
  
  theme(
    plot.title = element_text(hjust = 0.5), # Zentrieren des Titels
    axis.title.x = element_blank(), # Achsentitel entfernen
    axis.title.y = element_blank(), # Achsentitel entfernen
    axis.text.x = element_text(size = 12), # Achsentext entfernen
    axis.text.y = element_blank(), # Achsentext entfernen
    axis.ticks = element_blank(),  # Achsenticks entfernen
    panel.grid = element_blank(), # Achsengitter entfernen
    legend.position = "none" # Legende entfernen
  )+
  
  ggtitle("Übereinstimmung der Klassifikation\nin Prozent")


# Darstellung in einer Grafik  
final_plot <- map_plot + bar_plot + plot_layout(widths = c(3, 1))

final_plot <- map_plot + bar_plot +
  plot_layout(widths = c(3, 1)) +
  plot_annotation(
    title = "Vorkommen von Klassifikationsunterschieden zwischen der Arealstatistik und CORINE Landcover im Jahr 2018",
    theme = theme(plot.title = element_text(size = 15, face = "bold", hjust = 0.5))
  )

final_plot
