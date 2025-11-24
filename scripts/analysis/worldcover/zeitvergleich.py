import rasterio
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.colors import to_rgb, ListedColormap, BoundaryNorm
from matplotlib.ticker import ScalarFormatter
import matplotlib.patches as mpatches
import seaborn as sns
from sklearn.metrics import confusion_matrix
from scripts import DATA_DIR
import matplotlib as mpl

# ------------------------------------------
# Eingabedateien
# ------------------------------------------
fp20 = DATA_DIR / "preprocessing/worldcover/2020/worldcover_2020_merged_epsg2056.tif"
fp21 = DATA_DIR / "preprocessing/worldcover/2021/worldcover_2021_merged_epsg2056.tif"

# ------------------------------------------
# Raster laden
# ------------------------------------------
with rasterio.open(fp20) as src20:
    arr20 = src20.read(1)
    profile = src20.profile

with rasterio.open(fp21) as src21:
    arr21 = src21.read(1)

assert arr20.shape == arr21.shape, "Raster unterschiedlich groß!"
h, w = arr20.shape

# ------------------------------------------
# Farben definieren
# ------------------------------------------
category_colors = {
    10: "#228B22",  # Forest
    20: "#8B4513",  # Shrubland
    30: "#BCFF1E",  # Grassland
    40: "#1E90FF",  # Cropland
    50: "#A9A9A9",  # Settlements
    60: "#F31383",  # Sparse vegetation
    70: "#9932CC",  # Snow/Ice
    80: "#00CED1",  # Water
}

# Nur Kategorien, die im Raster vorkommen
categories = sorted([c for c in np.unique(arr20) if c in category_colors])

# ------------------------------------------
# Einkanal-Bild erzeugen (RAM-schonend)
# ------------------------------------------
new = np.zeros((h, w), dtype=np.uint8)
for cat in categories:
    mask = arr20 == cat
    # Korrekt
    new[mask & (arr21 == cat)] = cat / 10
    # Falsch
    new[mask & (arr21 != cat)] = cat


# 2Neues GeoTIFF abspeichern
out_fp = DATA_DIR / "visualizations/2020_2021_comparison_wc.tif"

with rasterio.open(
    out_fp,
    'w',
    driver='GTiff',
    height=h,
    width=w,
    count=1,               # nur ein Band
    dtype=new.dtype,
    crs=profile['crs'],    # CRS übernehmen
    transform=profile['transform'],
) as dst:
    dst.write(new, 1)  # Band 1 schreiben

print(f"Raster gespeichert unter: {out_fp}")
# ------------------------------------------
# Accuracy pro Kategorie berechnen
# ------------------------------------------
accuracy_per_class = []
for c in categories:
    total = np.sum(arr20 == c)
    correct = np.sum((arr20 == c) & (arr21 == c))
    pct = (correct / total * 100) if total else 0
    accuracy_per_class.append((c, pct))

# ------------------------------------------
# Funktion zum Anpassen der Helligkeit
# ------------------------------------------
def adjust_brightness(color, factor):
    rgb = np.array(to_rgb(color))
    return np.clip(rgb * factor, 0, 1)

# Farbzuweisung für Balken / Raster
color_low  = {c: (np.array(to_rgb(category_colors[c])) * 255).astype(np.uint8)          # korrekt/unverändert
              for c in categories}
color_high = {c: (adjust_brightness(category_colors[c], 1.5) * 255).astype(np.uint8) # falsch/geändert
              for c in categories}

# ------------------------------------------
# Karte + Balkendiagramm plotten
# ------------------------------------------
fig, (ax_map, ax_bar) = plt.subplots(1, 2, figsize=(16, 9), width_ratios=[3, 1])

transform = profile["transform"]

# Colormap für Raster: unverändert = originalfarbe, geändert = heller
cmap_colors = [(1,1,1)]  # weiß
for c in categories:
    cmap_colors.append(to_rgb(category_colors[c]))          # unverändert
for c in categories:
    cmap_colors.append(adjust_brightness(category_colors[c], 1.5))  # geändert = heller

cmap_vals = [0] +[c /10 for c in categories] + [c for c in categories]
cmap = ListedColormap(cmap_colors)
bounds = cmap_vals + [cmap_vals[-1] + 1]
norm = BoundaryNorm(bounds, cmap.N)


# Karte
ax_map.imshow(new, extent=[
    transform.c,
    transform.c + transform.a * w,
    transform.f + transform.e * h,
    transform.f
], cmap=cmap, norm=norm)
ax_map.axis("on")
ax_map.grid(True, linestyle='--', linewidth=0.5, alpha=0.5)

# Normale Zahlen für Achsen
ax_map.set_title("WorldCover 2020 → 2021: Pixelgenaue Übereinstimmung", fontsize=18, fontweight="bold")
ax_map.xaxis.set_major_formatter(ScalarFormatter(useOffset=False))
ax_map.yaxis.set_major_formatter(ScalarFormatter(useOffset=False))
ax_map.xaxis.get_major_formatter().set_scientific(False)
ax_map.yaxis.get_major_formatter().set_scientific(False)

# Maßstab
xlim = ax_map.get_xlim()
ylim = ax_map.get_ylim()
scalebar_length = 1000
sb_x = xlim[0] + (xlim[1] - xlim[0]) * 0.05
sb_y = ylim[0] + (ylim[1] - ylim[0]) * 0.05
ax_map.plot([sb_x, sb_x + scalebar_length], [sb_y, sb_y], color='black', linewidth=3)
ax_map.text(sb_x + scalebar_length / 2, sb_y + (ylim[1] - ylim[0]) * 0.015,
            "1000 m", ha='center', fontsize=10)

# Balkendiagramm: hell = geändert, dunkel = korrekt
category_names = {
    10: "Wald", 20: "Buschland", 30: "Grasland", 40: "Ackerfläche",
    50: "Siedlungsfläche", 60: "Karge Fläche", 70: "Schnee/Eis", 80: "Wasserfläche"
}

for idx, (c, pct) in enumerate(accuracy_per_class):
    incorrect_pct = 100 - pct
    ax_bar.barh(idx, pct, color=color_low[c]/255, edgecolor='black')      # korrekt/unverändert
    ax_bar.barh(idx, incorrect_pct, left=pct, color=color_high[c]/255, edgecolor='black')  # geändert

ax_bar.set_xlim(0, 100)
ax_bar.set_xlabel("Prozentuale Übereinstimmung")
ax_bar.set_title("Accuracy pro Klasse", fontsize=12)
ax_bar.set_yticks(range(len(categories)))
ax_bar.set_yticklabels([f"{category_names[cat]} {pct:.0f}%" for (cat, pct) in accuracy_per_class])

legend_patches = [
    mpatches.Patch(color="lightgrey", label="hell = korrekt"),
    mpatches.Patch(color="darkgrey", label="dunkel = falsch")
]
ax_bar.legend(handles=legend_patches, loc="upper center", fontsize=8, ncol=2, frameon=False)

plt.tight_layout()
plt.savefig(DATA_DIR / "2020_2021_comparison_wc_map.png", dpi=300, bbox_inches='tight')
plt.show()

# ------------------------------------------
# Übergangsmatrix berechnen und als Heatmap
# ------------------------------------------
y_true = arr20.flatten()
y_pred = arr21.flatten()
mask = np.isin(y_true, categories) & np.isin(y_pred, categories)
y_true_valid = y_true[mask]
y_pred_valid = y_pred[mask]

cm = confusion_matrix(y_true_valid, y_pred_valid, labels=categories)
cm_df = pd.DataFrame(cm, index=categories, columns=categories)
cm_percent = cm_df.div(cm_df.sum(axis=1), axis=0) * 100
cm_percent = cm_percent.fillna(0.0)
cm_percent_named = cm_percent.rename(index=category_names, columns=category_names)
annot_matrix = cm_percent_named.map(lambda x: f"{x:.1f}%" if x >= 2 else "")

colors = [
    (1,1,1,0),
    "#fef0d9","#fdcc8a","#fc8d59","#e34a33","#b30000"
]
cmap = ListedColormap(colors)
bounds = [0,2,10,20,50,75,100]
norm = BoundaryNorm(bounds, cmap.N)

plt.figure(figsize=(10, 8))
ax = sns.heatmap(
    cm_percent_named,
    annot=annot_matrix,
    fmt="",
    cmap=cmap,
    norm=norm,
    xticklabels=cm_percent_named.columns,
    yticklabels=cm_percent_named.index,
    cbar=False
)
for spine in ax.spines.values(): spine.set_visible(False)
ax.tick_params(axis='both', which='both', length=0)
plt.title("Confusion Matrix 2020 → 2021 WorldCover", fontsize=16, fontweight='bold', pad=20)
plt.xlabel("WorldCover Klasse 2021", fontsize=12, fontweight='bold', labelpad=15)
plt.ylabel("WorldCover Klasse 2020", fontsize=12, fontweight='bold', labelpad=15)
plt.tight_layout()

# Custom colorbar
sm = mpl.cm.ScalarMappable(cmap=cmap, norm=norm)
sm.set_array([])
cbar = plt.colorbar(sm, ax=ax, boundaries=bounds, spacing="proportional", ticks=bounds, extend='neither')
cbar.set_ticklabels([f"{b}%" for b in bounds])
cbar.set_label("", rotation=270, labelpad=20)
cbar.outline.set_visible(False)
cbar.ax.tick_params(length=0)
plt.savefig(DATA_DIR / "2020_2021_comparison_wc_matrix.png")
plt.show()
