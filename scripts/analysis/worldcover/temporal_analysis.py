"""
Enhanced Temporal Analysis for WorldCover Dataset.

Compares WorldCover 2020 and 2021 datasets to identify land cover changes,
calculate transition matrices, and visualize trends.

This is an enhanced version of zeitvergleich.py using the temporal_analysis_helper module.
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
WORLDCOVER_2020 = DATA_DIR / "preprocessing" / "worldcover" / "2020" / "worldcover_2020_clipped.tif"
WORLDCOVER_2021 = DATA_DIR / "preprocessing" / "worldcover" / "2021" / "worldcover_2021_clipped.tif"
OUTPUT_DIR = DATA_DIR / "analysis" / "worldcover" / "temporal_analysis"

# ------------------------------------------
# WORLDCOVER CLASS NAMES
# ------------------------------------------
WORLDCOVER_CLASSES = {
    10: "Tree cover",
    20: "Shrubland",
    30: "Grassland",
    40: "Cropland",
    50: "Built-up",
    60: "Bare / sparse vegetation",
    70: "Snow and ice",
    80: "Permanent water bodies",
    90: "Herbaceous wetland",
    95: "Mangroves",
    100: "Moss and lichen"
}

# ------------------------------------------
# MAIN ANALYSIS
# ------------------------------------------
def run_worldcover_temporal_analysis():
    """
    Run complete temporal analysis for WorldCover 2020 vs 2021.
    
    Returns
    -------
    dict
        Dictionary containing transition matrix, statistics, and file paths
    """
    print("="*60)
    print("WorldCover Temporal Analysis: 2020 → 2021")
    print("="*60)
    
    # Check if files exist
    if not WORLDCOVER_2020.exists():
        raise FileNotFoundError(f"WorldCover 2020 file not found: {WORLDCOVER_2020}")
    if not WORLDCOVER_2021.exists():
        raise FileNotFoundError(f"WorldCover 2021 file not found: {WORLDCOVER_2021}")
    
    # Load rasters
    print("\nLoading WorldCover 2020 raster...")
    with rasterio.open(WORLDCOVER_2020) as src:
        r2020 = src.read(1)
        nodata_2020 = src.nodata
        print(f"  Shape: {r2020.shape}")
        print(f"  NoData: {nodata_2020}")
    
    print("\nLoading WorldCover 2021 raster...")
    with rasterio.open(WORLDCOVER_2021) as src:
        r2021 = src.read(1)
        nodata_2021 = src.nodata
        print(f"  Shape: {r2021.shape}")
        print(f"  NoData: {nodata_2021}")
    
    # Calculate transition matrix
    print("\nCalculating transition matrix...")
    transition_matrix = calculate_transition_matrix(
        r2020, r2021,
        nodata_t1=nodata_2020,
        nodata_t2=nodata_2021,
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
        name = WORLDCOVER_CLASSES.get(cls, f"Class {cls}")
        print(f"  {name:30s}: {persistence:6.2f}%")
    
    print("\nTop 5 Net Gains (pixels):")
    top_gains = sorted(stats['net_change'].items(), key=lambda x: x[1], reverse=True)[:5]
    for cls, change in top_gains:
        if change > 0:
            name = WORLDCOVER_CLASSES.get(cls, f"Class {cls}")
            print(f"  {name:30s}: +{change:,}")
    
    print("\nTop 5 Net Losses (pixels):")
    top_losses = sorted(stats['net_change'].items(), key=lambda x: x[1])[:5]
    for cls, change in top_losses:
        if change < 0:
            name = WORLDCOVER_CLASSES.get(cls, f"Class {cls}")
            print(f"  {name:30s}: {change:,}")
    
    # Save results
    print("\n" + "="*60)
    print("SAVING RESULTS")
    print("="*60)
    saved_files = save_analysis_results(
        transition_matrix,
        stats,
        OUTPUT_DIR,
        "worldcover_2020_2021",
        class_names=WORLDCOVER_CLASSES
    )
    
    # Also save to legacy location for backwards compatibility
    legacy_path = DATA_DIR / "analysis" / "worldcover" / "transition_matrix_zeitvergleich.csv"
    transition_matrix.to_csv(legacy_path)
    print(f"Legacy transition matrix saved: {legacy_path}")
    
    print("\n" + "="*60)
    print("ANALYSIS COMPLETE")
    print("="*60)
    print(f"Results saved to: {OUTPUT_DIR}")
    
    return {
        'transition_matrix': transition_matrix,
        'statistics': stats,
        'class_names': WORLDCOVER_CLASSES,
        'saved_files': saved_files
    }


if __name__ == "__main__":
    results = run_worldcover_temporal_analysis()
    print("\nDone!")
