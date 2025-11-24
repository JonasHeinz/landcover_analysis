# Pakete laden
library(sf)
library(ggplot2)
library(ggalluvial)
library(dplyr)

# GeoPackage einlesen
gdf <- st_read(DATA_DIR,"/analysis/as_av_corine_wc_merged.gpkg")

# Mapping der numerischen Codes 1-6 auf IPCC-Klassen + No Data
ipcc_levels <- c("Forest land", "Cropland", "Grassland", "Wetlands",
                 "Settlements", "Other Land", "No Data")

code_to_ipcc <- function(x) ipcc_levels[x]

# Neue Spalten erzeugen und No Data ersetzen
gdf <- gdf %>%
  mutate(
    AS = code_to_ipcc(IPCC_AS_Id),
    WORLDCOVER = code_to_ipcc(IPCC_WC_Id),
    CORINE = code_to_ipcc(IPCC_Corine_Id),
    AV = code_to_ipcc(IPCC_AV_Id)
  ) %>%
  mutate(across(c(AS, WORLDCOVER, CORINE, AV),
                ~ ifelse(is.na(.x), "No Data", .x)))

# Häufigkeiten pro Kombination berechnen
data_long <- aggregate(
  x = list(Freq = rep(1, nrow(gdf))),
  by = list(AS = gdf$AS,
            CORINE = gdf$CORINE,
            WORLDCOVER = gdf$WORLDCOVER,
            AV = gdf$AV),
  FUN = sum
)

# Faktorlevels festlegen
data_long <- data_long %>%
  mutate(across(c(AS, WORLDCOVER, CORINE, AV),
                ~ factor(.x, levels = ipcc_levels)))

# Farben inkl. No Data
ipcc_colors <- c(
  "Forest land" = "#228B22",
  "Cropland"    = "#8B4513",
  "Grassland"   = "#BCFF1E",
  "Settlements" = "#A9A9A9",
  "Wetlands"    = "#1E90FF",
  "Other Land"  = "#F31383",
  "No Data"     = "#808080" 
)

comma_apostrophe <- function(x) {
  format(x, big.mark = "'", scientific = FALSE)
}

# Alluvial-Plot
ggplot(data_long,
       aes(axis1 = AS,
           axis2 = WORLDCOVER,
           axis3 = CORINE,
           axis4 = AV,
           y = Freq)) +
  geom_alluvium(aes(fill = AS), width = 1/12, alpha = 0.7) +
  geom_stratum(aes(fill = after_stat(stratum)), width = 1/6, color = "NA") +
  scale_fill_manual(values = ipcc_colors, drop = FALSE) +
  scale_x_discrete(
    limits = c("AS", "WORLDCOVER", "CORINE", "AV"),
    labels = c("Arealstatistik", "WorldCover", "CORINE", "Amtliche\nVermessung"),
    expand = c(.20, .1)
  ) +
  scale_y_continuous(labels = comma_apostrophe) +
  labs(
    fill = "IPCC Kategorien:",
    x = "Datensatz",
    y = "Häufigkeit",
    title = "Vergleich der IPCC-Landbedeckungskategorien in Datensätzen für die Schweiz",
    subtitle = "Abweichungen und Übereinstimmungen der Klassifizierungen zwischen Arealstatistik, CORINE, WorldCover und Amtlicher Vermessung"
  ) +
  theme_minimal(base_size = 12) +
  theme(
    plot.title = element_text(hjust = 0.5, face = "bold", size = 16),
    plot.subtitle = element_text(hjust = 0.5, size = 14),
    panel.grid.major.x = element_blank(),
    panel.grid.minor.x = element_blank()
  )

