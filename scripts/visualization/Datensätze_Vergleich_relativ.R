# Pakete laden
library(sf)
library(ggplot2)
library(ggalluvial)
library(dplyr)
library(scales)

# GeoPackage einlesen
gdf <- st_read(DATA_DIR,"/analysis/as_av_corine_wc_merged.gpkg")

# Mapping der numerischen Codes 1-6 auf IPCC-Klassen + No Datae
ipcc_levels <- c("Forest land", "Cropland", "Grassland", "Wetlands",
                 "Settlements", "Other Land", "No Data")

code_to_ipcc <- function(x) ipcc_levels[x]

gdf <- gdf %>%
  mutate(
    AS = code_to_ipcc(IPCC_AS_Id),
    WORLDCOVER = code_to_ipcc(IPCC_WC_Id),
    CORINE = code_to_ipcc(IPCC_Corine_Id),
    AV = code_to_ipcc(IPCC_AV_Id)
  ) %>%
  mutate(across(c(AS, WORLDCOVER, CORINE, AV),
                ~ ifelse(is.na(.x), "No Data", .x)))

# Häufigkeiten berechnen (relativ)
data_long <- gdf %>%
  count(AS, WORLDCOVER, CORINE, AV, name = "Freq") %>%
  mutate(Freq_rel = Freq / sum(Freq)) %>%
  mutate(across(c(AS, WORLDCOVER, CORINE, AV),
                ~ factor(.x, levels = ipcc_levels)))

# Farben definieren inkl. No Data
ipcc_colors <- c(
  "Forest land" = "#228B22",
  "Cropland"    = "#8B4513",
  "Grassland"   = "#BCFF1E",
  "Settlements" = "#A9A9A9",
  "Wetlands"    = "#1E90FF",
  "Other Land"  = "#F31383",
  "No Data"     = "#808080"
)

# Sichtbarkeits-Schwelle für Alluvien 0.125 %
threshold <- 0.00125

# Alluvial-Plot erstellen
ggplot(data_long,
       aes(axis1 = AS,
           axis2 = WORLDCOVER,
           axis3 = CORINE,
           axis4 = AV,
           y = Freq_rel)) +
  
  # Flüsse abhängig von Häufigkeit sichtbar/unsichtbar machen
  geom_alluvium(
    aes(
      fill = AS,
      alpha = ifelse(Freq_rel >= threshold, 0.6, 0)
    ),
    width = 1/12, na.rm = TRUE
  ) +
  scale_alpha_identity() +
  
  geom_stratum(aes(fill = after_stat(stratum)),
               width = 1/6, color = "NA", na.rm = TRUE) +
  
  scale_fill_manual(values = ipcc_colors, drop = FALSE) +
  
  scale_x_discrete(
    limits = c("AS", "WORLDCOVER", "CORINE", "AV"),
    labels = c("Arealstatistik", "WorldCover", "CORINE", "Amtliche\nVermessung"),
    expand = c(.20, .1)
  ) +
  
  scale_y_continuous(labels = percent_format(accuracy = 0.1)) +
  
  labs(
    fill = "IPCC Kategorien:",
    x = "Datensatz",
    y = "Anteil (%)",
    title = "Vergleich der IPCC-Landbedeckungskategorien in Datensätzen für die Schweiz",
    subtitle = "Abweichungen und Übereinstimmungen der Klassifizierungen zwischen verschiedenen Datensätzen"
  ) +
  
  theme_minimal(base_size = 12) +
  theme(
    plot.title = element_text(hjust = 0.5, face = "bold", size = 16),
    plot.subtitle = element_text(hjust = 0.5, size = 13),
    panel.grid.major.x = element_blank(),
    panel.grid.minor.x = element_blank()
  )
