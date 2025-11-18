"""
General purpose temporal analysis script for comparing any two landcover rasters.

This script can be used as a template or run directly to compare any two raster datasets.
"""

import argparse
import rasterio
import pandas as pd
from pathlib import Path
from scripts.helpers.temporal_analysis_helper import (
    calculate_transition_matrix,
    calculate_change_statistics,
    save_analysis_results
)


def run_temporal_analysis(raster_t1_path, raster_t2_path, output_dir, 
                          dataset_name, class_mapping_csv=None):
    """
    Run temporal analysis between two raster files.
    
    Parameters
    ----------
    raster_t1_path : str or Path
        Path to first time period raster
    raster_t2_path : str or Path
        Path to second time period raster
    output_dir : str or Path
        Directory for output files
    dataset_name : str
        Name for output files (e.g., 'dataset_2010_2020')
    class_mapping_csv : str or Path, optional
        Path to CSV with class ID to name mapping
        Expected columns: 'class_id', 'class_name'
        
    Returns
    -------
    dict
        Results dictionary with transition matrix and statistics
    """
    raster_t1_path = Path(raster_t1_path)
    raster_t2_path = Path(raster_t2_path)
    output_dir = Path(output_dir)
    
    print("="*60)
    print(f"Temporal Analysis: {dataset_name}")
    print("="*60)
    print(f"Time 1: {raster_t1_path}")
    print(f"Time 2: {raster_t2_path}")
    print(f"Output: {output_dir}")
    print("="*60)
    
    # Load class names if provided
    class_names = None
    if class_mapping_csv:
        mapping_path = Path(class_mapping_csv)
        if mapping_path.exists():
            df = pd.read_csv(mapping_path)
            if 'class_id' in df.columns and 'class_name' in df.columns:
                class_names = dict(zip(df['class_id'], df['class_name']))
                print(f"\nLoaded {len(class_names)} class names from {mapping_path}")
            else:
                print(f"\nWarning: CSV must have 'class_id' and 'class_name' columns")
        else:
            print(f"\nWarning: Class mapping file not found: {mapping_path}")
    
    # Load first raster
    print(f"\nLoading time 1 raster...")
    with rasterio.open(raster_t1_path) as src:
        r1 = src.read(1)
        nodata_1 = src.nodata
        print(f"  Shape: {r1.shape}")
        print(f"  NoData: {nodata_1}")
        print(f"  Data type: {r1.dtype}")
    
    # Load second raster
    print(f"\nLoading time 2 raster...")
    with rasterio.open(raster_t2_path) as src:
        r2 = src.read(1)
        nodata_2 = src.nodata
        print(f"  Shape: {r2.shape}")
        print(f"  NoData: {nodata_2}")
        print(f"  Data type: {r2.dtype}")
    
    # Check dimensions match
    if r1.shape != r2.shape:
        raise ValueError(f"Raster dimensions don't match: {r1.shape} vs {r2.shape}")
    
    # Calculate transition matrix
    print("\nCalculating transition matrix...")
    transition_matrix = calculate_transition_matrix(
        r1, r2,
        nodata_t1=nodata_1,
        nodata_t2=nodata_2,
        max_value=256
    )
    print(f"  Matrix dimensions: {transition_matrix.shape}")
    print(f"  Classes found: {len(transition_matrix.index)}")
    
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
    
    if stats['changed_pixels'] > 0:
        print("\nTop changes detected:")
        print(f"  Classes with changes: {len([c for c in stats['net_change'].values() if c != 0])}")
        
        # Show top gains
        top_gains = sorted(stats['net_change'].items(), key=lambda x: x[1], reverse=True)[:5]
        if any(change > 0 for _, change in top_gains):
            print("\n  Top Net Gains:")
            for cls, change in top_gains:
                if change > 0:
                    name = class_names.get(cls, f"Class {cls}") if class_names else str(cls)
                    print(f"    {name}: +{change:,} pixels")
        
        # Show top losses
        top_losses = sorted(stats['net_change'].items(), key=lambda x: x[1])[:5]
        if any(change < 0 for _, change in top_losses):
            print("\n  Top Net Losses:")
            for cls, change in top_losses:
                if change < 0:
                    name = class_names.get(cls, f"Class {cls}") if class_names else str(cls)
                    print(f"    {name}: {change:,} pixels")
    
    # Save results
    print("\n" + "="*60)
    print("SAVING RESULTS")
    print("="*60)
    saved_files = save_analysis_results(
        transition_matrix,
        stats,
        output_dir,
        dataset_name,
        class_names=class_names
    )
    
    print("\n" + "="*60)
    print("ANALYSIS COMPLETE")
    print("="*60)
    
    return {
        'transition_matrix': transition_matrix,
        'statistics': stats,
        'class_names': class_names,
        'saved_files': saved_files
    }


def main():
    """Command line interface for temporal analysis."""
    parser = argparse.ArgumentParser(
        description='Temporal analysis of landcover raster datasets',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic usage
  python temporal_analysis_general.py time1.tif time2.tif output/ my_dataset
  
  # With class name mapping
  python temporal_analysis_general.py time1.tif time2.tif output/ my_dataset \\
      --class-mapping mapping.csv
        """
    )
    
    parser.add_argument('raster_t1', type=str,
                        help='Path to first time period raster')
    parser.add_argument('raster_t2', type=str,
                        help='Path to second time period raster')
    parser.add_argument('output_dir', type=str,
                        help='Output directory for results')
    parser.add_argument('dataset_name', type=str,
                        help='Dataset name for output files')
    parser.add_argument('--class-mapping', type=str, default=None,
                        help='CSV file with class_id and class_name columns')
    
    args = parser.parse_args()
    
    results = run_temporal_analysis(
        args.raster_t1,
        args.raster_t2,
        args.output_dir,
        args.dataset_name,
        args.class_mapping
    )
    
    print("\n✓ Analysis complete!")


if __name__ == "__main__":
    main()
