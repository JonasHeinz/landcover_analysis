import rasterio
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
from scripts import DATA_DIR
from sklearn.metrics import ConfusionMatrixDisplay

# ------------------------------------------
# EINZELRASTER EINLESEN
# ------------------------------------------
fp20 = DATA_DIR / "preprocessing" / "worldcover" / "2020" / "worldcover_2020_clipped.tif"
fp21 = DATA_DIR / "preprocessing" / "worldcover" / "2021" / "worldcover_2021_clipped.tif"

with rasterio.open(fp20) as src20, rasterio.open(fp21) as src21:
    r20 = src20.read(1)
    r21 = src21.read(1)

    mask = (r20 == src20.nodata) | (r21 == src21.nodata)
    r20 = r20[~mask]
    r21 = r21[~mask]

# ------------------------------------------
# Übergangsmatrix berechnen
# ------------------------------------------
combined = r20.astype(np.int32) * 256 + r21.astype(np.int32)
counts = np.bincount(combined, minlength=256*256)
matrix = counts.reshape((256, 256))

# ------------------------------------------
# Nur vorkommende Klassen
# ------------------------------------------
used = np.where(matrix.sum(axis=1) + matrix.sum(axis=0) > 0)[0]

transition_matrix = pd.DataFrame(
    matrix[np.ix_(used, used)],
    index=used,
    columns=used
)

out_path = DATA_DIR / "analysis" / "worldcover" / "transition_matrix_zeitvergleich.csv"
transition_matrix.to_csv(out_path)
print("Gespeichert:", out_path)

# ------------------------------------------
# CONFUSION MATRIX DISPLAY (sklearn)
# ------------------------------------------
cm = transition_matrix.values
labels = transition_matrix.index.tolist()

plt.figure(figsize=(10, 8))
disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=labels)
disp.plot(cmap="YlOrRd", xticks_rotation=45)
plt.title("Übergangsmatrix WorldCover 2020 → 2021 (ConfusionMatrixDisplay)")
plt.tight_layout()
plt.show()

# ------------------------------------------
# HEATMAP (matplotlib)
# ------------------------------------------
plt.figure(figsize=(10, 8))
plt.imshow(transition_matrix, interpolation='nearest')
plt.colorbar(label="Pixel count")
plt.xlabel("2021 classes")
plt.ylabel("2020 classes")
plt.title("Transition Matrix Heatmap")
plt.tight_layout()
plt.show()

print("Fertig!")
