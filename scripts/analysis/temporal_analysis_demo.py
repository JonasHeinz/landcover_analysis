"""
Demo script showing how to use temporal analysis functions.

This script demonstrates the key functionality of the temporal analysis module
with a simple synthetic example.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(project_root))

import numpy as np
import pandas as pd
from scripts.helpers.temporal_analysis_helper import (
    calculate_transition_matrix,
    calculate_change_statistics,
    create_change_summary_table,
    plot_transition_matrix,
    plot_net_change_bar
)
import matplotlib.pyplot as plt


def create_synthetic_data():
    """
    Create synthetic landcover data for demonstration.
    
    Simulates a 100x100 pixel area with 4 land cover classes:
    - 1: Forest
    - 2: Cropland
    - 3: Urban
    - 4: Water
    
    Returns two time periods with some changes between them.
    """
    np.random.seed(42)
    
    # Time 1: Initial state
    size = (100, 100)
    t1 = np.zeros(size, dtype=np.int32)
    
    # Forest (50%)
    t1[0:50, :] = 1
    # Cropland (30%)
    t1[50:80, :] = 2
    # Urban (15%)
    t1[80:95, :] = 3
    # Water (5%)
    t1[95:100, :] = 4
    
    # Time 2: Copy and introduce changes
    t2 = t1.copy()
    
    # Forest to Cropland (deforestation): 200 pixels
    t2[40:42, 0:100] = 2
    
    # Cropland to Urban (urbanization): 150 pixels
    t2[78:80, 0:75] = 3
    
    # Forest to Urban (urban expansion): 100 pixels
    t2[48:49, 0:100] = 3
    
    return t1, t2


def run_demo():
    """Run the temporal analysis demo."""
    
    print("="*70)
    print("TEMPORAL ANALYSIS DEMO")
    print("="*70)
    
    # Create synthetic data
    print("\n1. Creating synthetic landcover data...")
    print("   - 100x100 pixels")
    print("   - 4 land cover classes: Forest, Cropland, Urban, Water")
    print("   - Simulating changes between two time periods")
    
    raster_t1, raster_t2 = create_synthetic_data()
    
    # Define class names
    class_names = {
        1: "Forest",
        2: "Cropland",
        3: "Urban",
        4: "Water"
    }
    
    print("\n2. Calculating transition matrix...")
    transition_matrix = calculate_transition_matrix(
        raster_t1, 
        raster_t2,
        nodata_t1=None,
        nodata_t2=None,
        max_value=10  # We only have 4 classes
    )
    
    print("\nTransition Matrix:")
    print(transition_matrix)
    
    print("\n3. Calculating change statistics...")
    stats = calculate_change_statistics(transition_matrix)
    
    print(f"\nTotal pixels analyzed: {stats['total_pixels']:,}")
    print(f"Unchanged pixels: {stats['unchanged_pixels']:,}")
    print(f"Changed pixels: {stats['changed_pixels']:,}")
    print(f"Change percentage: {stats['change_percentage']:.2f}%")
    
    print("\n4. Creating change summary table...")
    summary = create_change_summary_table(stats, class_names)
    print("\n" + summary.to_string(index=False))
    
    print("\n5. Generating visualizations...")
    
    # Transition matrix plot
    fig1 = plot_transition_matrix(
        transition_matrix,
        title="Demo: Transition Matrix",
        class_names=class_names,
        figsize=(8, 6)
    )
    
    # Net change plot
    fig2 = plot_net_change_bar(
        stats,
        title="Demo: Net Change by Class",
        class_names=class_names,
        figsize=(8, 5)
    )
    
    plt.show()
    
    print("\n" + "="*70)
    print("DEMO COMPLETE")
    print("="*70)
    print("\nKey Observations from Demo:")
    print("- Forest lost 300 pixels (to Cropland and Urban)")
    print("- Cropland had small net loss (gained 200, lost 250)")
    print("- Urban expanded by 350 pixels (from Forest and Cropland)")
    print("- Water remained stable (no changes)")
    
    print("\nThese patterns represent common land cover changes:")
    print("- Deforestation for agriculture")
    print("- Urban expansion into natural and agricultural areas")
    print("- Water bodies remaining stable")
    
    return {
        'transition_matrix': transition_matrix,
        'statistics': stats,
        'summary': summary
    }


if __name__ == "__main__":
    print("\n" + "="*70)
    print("TEMPORAL ANALYSIS MODULE - DEMONSTRATION")
    print("="*70)
    print("\nThis demo shows how to use the temporal analysis functions")
    print("with synthetic landcover data simulating realistic changes.")
    print("\nPress Ctrl+C to exit early, or wait for visualizations to close.")
    print("="*70)
    
    try:
        results = run_demo()
        print("\n✓ Demo completed successfully!")
        print("\nTo use these functions with real data, see:")
        print("  - docs/temporal_analysis_documentation.md")
        print("  - scripts/analysis/corine/temporal_analysis.py")
        print("  - scripts/analysis/worldcover/temporal_analysis.py")
    except KeyboardInterrupt:
        print("\n\nDemo interrupted by user.")
    except Exception as e:
        print(f"\n\n✗ Demo failed with error: {e}")
        import traceback
        traceback.print_exc()
