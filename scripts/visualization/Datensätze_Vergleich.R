# Pakete laden
library(ggplot2)
library(ggalluvial)

# CSV einlesen
data <- read.csv("../mapping_alle.csv", sep=";", stringsAsFactors = FALSE)

# Häufigkeiten pro Kombination berechnen
data_long <- aggregate(
  x = list(Freq = rep(1, nrow(data))),
  by = list(AS = data$AS, CORINE = data$CORINE, WORLDCOVER = data$WORLDCOVER, AV = data$AV),
  FUN = sum
)

# IPCC Klassen und Farbe definieren
ipcc_levels <- c("Forest land", "Grassland", "Cropland", "Settlements", "Wetlands", "Other Land")

ipcc_colors <- c(
  "Forest land"      = "#decbe4",
  "Grassland"   = "#ccebc5",
  "Cropland"    = "#fed9a6",
  "Settlements"       = "#fbb4ae",
  "Wetlands"       = "#b3cde3",
  "Other Land"    = "#ffffcc"
)

# Spalten als Faktoren mit definierter Reihenfolge
data_long$AS <- factor(data_long$AS, levels = ipcc_levels)
data_long$CORINE <- factor(data_long$CORINE, levels = ipcc_levels)
data_long$WORLDCOVER <- factor(data_long$WORLDCOVER, levels = ipcc_levels)
data_long$AV <- factor(data_long$AV, levels = ipcc_levels)

# Alluvial-Plot
ggplot(data_long,
       aes(axis1 = AS,
           axis2 = CORINE,
           axis3 = WORLDCOVER,
           axis4 = AV,
           y = Freq)) +
  scale_x_discrete(
    limits = c("AS", "CORINE", "WORLDCOVER", "AV"), 
    labels = c("Arealstatistik", "CORINE", "WorldCover", "Amtliche Vermessung"),
    expand = c(.20, .1)) +
  xlab("Datensatz") +
  ylab("Häufigkeit") +  
  geom_alluvium(aes(fill = AS), width = 1/12, alpha = 0.7) +
  geom_stratum(aes(fill = after_stat(stratum)), width = 1/6, color = "grey") +
  scale_fill_manual(values = ipcc_colors) +
  labs(
    fill = "Legende:",
    title = "Vergleich der IPCC-Landbedeckungskategorien in Datensätzen für die Schweiz",
    subtitle = "Abweichungen und Übereinstimmungen der Klassifizierungen zwischen Arealstatistik, CORINE, WorldCover und Amtlicher Vermessung"
  ) +
  theme_minimal() +
  theme(
    plot.title = element_text(hjust = 0.5, face = "bold", size = 16),
    plot.subtitle = element_text(hjust = 0.5, size = 14),
    axis.title.y = element_text(margin = margin(r = 20)),
    axis.title.x = element_text(margin = margin(t = 10)),
    panel.grid.major.x = element_blank(),
    panel.grid.minor.x = element_blank()
  )


