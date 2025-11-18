"""
Temporal Analysis for CORINE Land Cover Dataset.

Compares CORINE 2012 and 2018 datasets to identify land cover changes,
calculate transition matrices, and visualize trends.
"""

import rasterio
import numpy as np
import pandas as pd
from pathlib import Path
from scripts import DATA_DIR
from scripts.helpers.temporal_analysis_helper import (
    calculate_transition_matrix,
    calculate_change_statistics,
    save_analysis_results
)

# ------------------------------------------
# PATHS
# ------------------------------------------
CORINE_2012 = DATA_DIR / "analysis" / "corine" / "2012" / "U2018_CLC2012_V2020_20u1_zug.tif"
CORINE_2018 = DATA_DIR / "analysis" / "corine" / "2018" / "U2018_CLC2018_V2020_20u1_zug.tif"
MAPPING_FILE = DATA_DIR / "analysis" / "corine" / "mapping_ipcc_corine.csv"
OUTPUT_DIR = DATA_DIR / "analysis" / "corine" / "temporal_analysis"

# ------------------------------------------
# LOAD CLASS NAMES
# ------------------------------------------
def load_corine_class_names():
    """Load CORINE class names from mapping file."""
    mapping_df = pd.read_csv(MAPPING_FILE, sep=";", encoding="utf-8-sig")
    # Create mapping from RASTER_ID to CORINE_NAME
    class_names = dict(zip(mapping_df["RASTER_ID"], mapping_df["CORINE_NAME"]))
    return class_names

# ------------------------------------------
# MAIN ANALYSIS
# ------------------------------------------
def run_corine_temporal_analysis():
    """
    Run complete temporal analysis for CORINE 2012 vs 2018.
    
    Returns
    -------
    dict
        Dictionary containing transition matrix, statistics, and file paths
    """
    print("="*60)
    print("CORINE Temporal Analysis: 2012 → 2018")
    print("="*60)
    
    # Check if files exist
    if not CORINE_2012.exists():
        raise FileNotFoundError(f"CORINE 2012 file not found: {CORINE_2012}")
    if not CORINE_2018.exists():
        raise FileNotFoundError(f"CORINE 2018 file not found: {CORINE_2018}")
    
    # Load class names
    class_names = load_corine_class_names()
    print(f"Loaded {len(class_names)} CORINE class names")
    
    # Load rasters
    print("\nLoading CORINE 2012 raster...")
    with rasterio.open(CORINE_2012) as src:
        r2012 = src.read(1)
        nodata_2012 = src.nodata
        print(f"  Shape: {r2012.shape}")
        print(f"  NoData: {nodata_2012}")
    
    print("\nLoading CORINE 2018 raster...")
    with rasterio.open(CORINE_2018) as src:
        r2018 = src.read(1)
        nodata_2018 = src.nodata
        print(f"  Shape: {r2018.shape}")
        print(f"  NoData: {nodata_2018}")
    
    # Calculate transition matrix
    print("\nCalculating transition matrix...")
    transition_matrix = calculate_transition_matrix(
        r2012, r2018, 
        nodata_t1=nodata_2012, 
        nodata_t2=nodata_2018,
        max_value=256
    )
    print(f"  Matrix dimensions: {transition_matrix.shape}")
    print(f"  Classes found: {len(transition_matrix.index)}")
    print(f"  Class IDs: {transition_matrix.index.tolist()}")
    
    # Calculate statistics
    print("\nCalculating change statistics...")
    stats = calculate_change_statistics(transition_matrix)
    
    # Print summary
    print("\n" + "="*60)
    print("SUMMARY STATISTICS")
    print("="*60)
    print(f"Total pixels analyzed:     {stats['total_pixels']:,}")
    print(f"Unchanged pixels:          {stats['unchanged_pixels']:,}")
    print(f"Changed pixels:            {stats['changed_pixels']:,}")
    print(f"Change percentage:         {stats['change_percentage']:.2f}%")
    
    print("\nClass Persistence (Stability):")
    for cls, persistence in sorted(stats['class_persistence'].items()):
        name = class_names.get(cls, f"Class {cls}")
        print(f"  {name:40s}: {persistence:6.2f}%")
    
    print("\nTop 5 Net Gains (pixels):")
    top_gains = sorted(stats['net_change'].items(), key=lambda x: x[1], reverse=True)[:5]
    for cls, change in top_gains:
        if change > 0:
            name = class_names.get(cls, f"Class {cls}")
            print(f"  {name:40s}: +{change:,}")
    
    print("\nTop 5 Net Losses (pixels):")
    top_losses = sorted(stats['net_change'].items(), key=lambda x: x[1])[:5]
    for cls, change in top_losses:
        if change < 0:
            name = class_names.get(cls, f"Class {cls}")
            print(f"  {name:40s}: {change:,}")
    
    # Save results
    print("\n" + "="*60)
    print("SAVING RESULTS")
    print("="*60)
    saved_files = save_analysis_results(
        transition_matrix, 
        stats, 
        OUTPUT_DIR,
        "corine_2012_2018",
        class_names=class_names
    )
    
    print("\n" + "="*60)
    print("ANALYSIS COMPLETE")
    print("="*60)
    print(f"Results saved to: {OUTPUT_DIR}")
    
    return {
        'transition_matrix': transition_matrix,
        'statistics': stats,
        'class_names': class_names,
        'saved_files': saved_files
    }


if __name__ == "__main__":
    results = run_corine_temporal_analysis()
    print("\nDone!")
