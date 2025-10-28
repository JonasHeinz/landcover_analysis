import fiona
from multiprocessing import Pool, cpu_count

# Pfad zu deinem Shapefile mit Forward-Slashes
shapefile_path = "C:/Users/aebim/Documents/02_Ausbildung/Studium/05_Semester/5230_Geoniformatik_Raumanalyse/Projektarbeit/Daten/AV/SHP_BB/lcsf.shp"

# Funktion zum Verarbeiten eines Feature-Blocks
def process_features(features):
    qualitaet_set = set()
    art_set = set()
    for feature in features:
        props = feature['properties']
        qualitaet_set.add(props.get('Qualitaet'))
        art_set.add(props.get('Art'))
    return qualitaet_set, art_set

# Chunkgröße für jeden Prozess (z.B. 100.000 Features pro Chunk)
CHUNK_SIZE = 100_000

def chunks(iterator, size):
    """Teilt Iterator in Chunks der Größe size"""
    chunk = []
    for item in iterator:
        chunk.append(item)
        if len(chunk) == size:
            yield chunk
            chunk = []
    if chunk:
        yield chunk

if __name__ == "__main__":
    qualitaet_values = set()
    art_values = set()
    
    # Fiona öffnet das Shapefile
    with fiona.open(shapefile_path, 'r') as shp:
        # Pool mit allen verfügbaren CPU-Kernen
        with Pool(cpu_count()) as pool:
            # Chunks erzeugen und parallel verarbeiten
            for q_sets, a_sets in pool.imap_unordered(process_features, chunks(shp, CHUNK_SIZE)):
                qualitaet_values.update(q_sets)
                art_values.update(a_sets)
    
    # In Listen umwandeln
    qualitaet_list = list(qualitaet_values)
    art_list = list(art_values)

    # Ergebnisse ausgeben
    print(f"Eindeutige Qualitaet-Werte ({len(qualitaet_list)}):")
    print(qualitaet_list)
    print(f"\nEindeutige Art-Werte ({len(art_list)}):")
    print(art_list)
