import requests
import zipfile
import io
import os
import subprocess
import warnings

# -------------------------------------
# Alle Warnungen ignorieren
# -------------------------------------
warnings.filterwarnings("ignore")
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# -------------------------------------
# Einstellungen
# -------------------------------------
url = "https://geodienste.ch/info/services.json"
download_dir = "av_downloads"
gpkg_dir = "av_gpkg"

os.makedirs(download_dir, exist_ok=True)
os.makedirs(gpkg_dir, exist_ok=True)

# -------------------------------------
# JSON abrufen
# -------------------------------------
print("Lade Service-Informationen herunter ...")
resp = requests.get(url, verify=False)
resp.raise_for_status()
data = resp.json()
services = data.get("services", data)

# -------------------------------------
# Frei erhältliche AV-Daten extrahieren
# -------------------------------------
freie_datasets = []
for item in services:
    if isinstance(item, dict):
        if item.get("publication_data") == "Frei erhältlich":
            dataset_url = item.get("dataset_url")
            if dataset_url and "/downloads/interlis/av/" in dataset_url:
                freie_datasets.append(dataset_url)

print(f"Gefundene AV-Datasets: {len(freie_datasets)}")

# -------------------------------------
# Download, Entpacken & GPkg-Konvertierung
# -------------------------------------
for dataset_url in freie_datasets:
    kanton = dataset_url.split("/")[-2]
    zip_path = os.path.join(download_dir, f"{kanton}.zip")

    print(f"Lade herunter: {kanton} ...")
    try:
        r = requests.get(dataset_url, verify=False, timeout=60)
        r.raise_for_status()
        with open(zip_path, "wb") as f:
            f.write(r.content)
        print(f"{kanton}: Download abgeschlossen")
    except Exception as e:
        print(f"{kanton}: Download fehlgeschlagen – {e}")
        continue

    # Entpacken
    extract_path = os.path.join(download_dir, kanton)
    os.makedirs(extract_path, exist_ok=True)
    try:
        with zipfile.ZipFile(io.BytesIO(r.content)) as z:
            z.extractall(extract_path)
        print(f"{kanton}: Entpackt nach {extract_path}")
    except Exception as e:
        print(f"{kanton}: Entpacken fehlgeschlagen – {e}")
        continue

    # GPkg-Konvertierung nur für .itf/.xtf
    # try:
    #     for file in os.listdir(extract_path):
    #         if file.lower().endswith((".itf", ".xtf")):
    #             input_file = os.path.join(extract_path, file)
    #             output_file = os.path.join(gpkg_dir, f"{kanton}.gpkg")

    #             print(f"{kanton}: Konvertiere nach GeoPackage ...")
    #             subprocess.run(
    #                 ["ogr2ogr", "-f", "GPKG", output_file, input_file, "-nln", "Bodenbedeckung"],
    #                 check=False,
    #                 stdout=subprocess.DEVNULL,
    #                 stderr=subprocess.DEVNULL
    #             )
    #             print(f"{kanton}: GPKG gespeichert unter {output_file}")
    # except Exception as e:
    #     print(f"{kanton}: Fehler bei der Konvertierung – {e}")

print("Fertig! Alle AV-Daten wurden heruntergeladen, entpackt und als GPKG gespeichert.")
