"""
Helper functions for temporal analysis of landcover datasets.

This module provides reusable functions for comparing landcover datasets
across different time periods, including transition matrix calculation,
change detection, and visualization.
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.metrics import ConfusionMatrixDisplay
from pathlib import Path


def calculate_transition_matrix(raster_t1, raster_t2, nodata_t1=None, nodata_t2=None, 
                                  max_value=256):
    """
    Calculate transition matrix between two raster datasets.
    
    Parameters
    ----------
    raster_t1 : numpy.ndarray
        First time period raster data
    raster_t2 : numpy.ndarray
        Second time period raster data
    nodata_t1 : int or None
        NoData value for first raster
    nodata_t2 : int or None
        NoData value for second raster
    max_value : int
        Maximum expected value in rasters (default 256)
        
    Returns
    -------
    pd.DataFrame
        Transition matrix as DataFrame with used classes only
    """
    # Flatten arrays if needed
    r1 = raster_t1.flatten() if raster_t1.ndim > 1 else raster_t1
    r2 = raster_t2.flatten() if raster_t2.ndim > 1 else raster_t2
    
    # Create mask for nodata values
    mask = np.zeros(len(r1), dtype=bool)
    if nodata_t1 is not None:
        mask |= (r1 == nodata_t1)
    if nodata_t2 is not None:
        mask |= (r2 == nodata_t2)
    
    # Remove nodata pixels
    r1 = r1[~mask]
    r2 = r2[~mask]
    
    # Calculate transition matrix
    combined = r1.astype(np.int32) * max_value + r2.astype(np.int32)
    counts = np.bincount(combined, minlength=max_value * max_value)
    matrix = counts.reshape((max_value, max_value))
    
    # Only keep classes that appear
    used = np.where(matrix.sum(axis=1) + matrix.sum(axis=0) > 0)[0]
    
    transition_matrix = pd.DataFrame(
        matrix[np.ix_(used, used)],
        index=used,
        columns=used
    )
    
    return transition_matrix


def calculate_change_statistics(transition_matrix):
    """
    Calculate change statistics from transition matrix.
    
    Parameters
    ----------
    transition_matrix : pd.DataFrame
        Transition matrix from calculate_transition_matrix
        
    Returns
    -------
    dict
        Dictionary containing change statistics:
        - total_pixels: Total number of pixels analyzed
        - unchanged_pixels: Pixels that didn't change
        - changed_pixels: Pixels that changed
        - change_percentage: Percentage of changed pixels
        - class_persistence: Percentage of each class that remained stable
        - class_gains: Pixels gained by each class
        - class_losses: Pixels lost by each class
        - net_change: Net change for each class (gains - losses)
    """
    # Total pixels
    total_pixels = transition_matrix.values.sum()
    
    # Unchanged pixels (diagonal)
    unchanged_pixels = np.diag(transition_matrix.values).sum()
    
    # Changed pixels
    changed_pixels = total_pixels - unchanged_pixels
    
    # Change percentage
    change_percentage = (changed_pixels / total_pixels * 100) if total_pixels > 0 else 0
    
    # Class statistics
    class_labels = transition_matrix.index.tolist()
    
    # Class persistence (stability)
    class_totals_t1 = transition_matrix.sum(axis=1)  # Row sums = total in time 1
    class_persistence = {}
    for cls in class_labels:
        if class_totals_t1[cls] > 0:
            persistence = (transition_matrix.loc[cls, cls] / class_totals_t1[cls] * 100)
            class_persistence[cls] = persistence
        else:
            class_persistence[cls] = 0.0
    
    # Class gains and losses
    class_gains = {}
    class_losses = {}
    net_change = {}
    
    for cls in class_labels:
        # Gains: pixels that became this class (column sum - diagonal)
        gains = transition_matrix[cls].sum() - transition_matrix.loc[cls, cls]
        class_gains[cls] = int(gains)
        
        # Losses: pixels that were this class but changed (row sum - diagonal)
        losses = transition_matrix.loc[cls].sum() - transition_matrix.loc[cls, cls]
        class_losses[cls] = int(losses)
        
        # Net change
        net_change[cls] = int(gains - losses)
    
    return {
        'total_pixels': int(total_pixels),
        'unchanged_pixels': int(unchanged_pixels),
        'changed_pixels': int(changed_pixels),
        'change_percentage': float(change_percentage),
        'class_persistence': class_persistence,
        'class_gains': class_gains,
        'class_losses': class_losses,
        'net_change': net_change
    }


def create_change_summary_table(stats, class_names=None):
    """
    Create a summary table of change statistics.
    
    Parameters
    ----------
    stats : dict
        Statistics dictionary from calculate_change_statistics
    class_names : dict or None
        Optional mapping of class IDs to names
        
    Returns
    -------
    pd.DataFrame
        Summary table with change statistics per class
    """
    # Extract class-level data
    classes = list(stats['class_gains'].keys())
    
    data = []
    for cls in classes:
        class_name = class_names.get(cls, str(cls)) if class_names else str(cls)
        data.append({
            'Class_ID': cls,
            'Class_Name': class_name,
            'Persistence_%': round(stats['class_persistence'][cls], 2),
            'Gains_pixels': stats['class_gains'][cls],
            'Losses_pixels': stats['class_losses'][cls],
            'Net_Change_pixels': stats['net_change'][cls]
        })
    
    df = pd.DataFrame(data)
    return df


def plot_transition_matrix(transition_matrix, title="Transition Matrix", 
                           figsize=(10, 8), cmap="YlOrRd", 
                           class_names=None, save_path=None):
    """
    Plot transition matrix as a heatmap.
    
    Parameters
    ----------
    transition_matrix : pd.DataFrame
        Transition matrix to plot
    title : str
        Plot title
    figsize : tuple
        Figure size (width, height)
    cmap : str
        Colormap name
    class_names : dict or None
        Optional mapping of class IDs to names for labels
    save_path : Path or None
        If provided, save figure to this path
        
    Returns
    -------
    matplotlib.figure.Figure
        The created figure
    """
    labels = transition_matrix.index.tolist()
    
    # Map to names if provided
    if class_names:
        display_labels = [class_names.get(lbl, str(lbl)) for lbl in labels]
    else:
        display_labels = [str(lbl) for lbl in labels]
    
    fig, ax = plt.subplots(figsize=figsize)
    
    # Use ConfusionMatrixDisplay for professional look
    disp = ConfusionMatrixDisplay(
        confusion_matrix=transition_matrix.values, 
        display_labels=display_labels
    )
    disp.plot(cmap=cmap, ax=ax, xticks_rotation=45)
    
    ax.set_title(title)
    ax.set_xlabel("Time 2 (To)")
    ax.set_ylabel("Time 1 (From)")
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Figure saved to: {save_path}")
    
    return fig


def plot_change_heatmap(transition_matrix, title="Change Heatmap",
                        figsize=(10, 8), cmap="RdYlGn",
                        class_names=None, save_path=None):
    """
    Plot a heatmap showing only changes (excluding diagonal).
    
    Parameters
    ----------
    transition_matrix : pd.DataFrame
        Transition matrix
    title : str
        Plot title
    figsize : tuple
        Figure size
    cmap : str
        Colormap name
    class_names : dict or None
        Optional mapping of class IDs to names
    save_path : Path or None
        If provided, save figure to this path
        
    Returns
    -------
    matplotlib.figure.Figure
        The created figure
    """
    # Create change matrix (set diagonal to 0)
    change_matrix = transition_matrix.copy()
    np.fill_diagonal(change_matrix.values, 0)
    
    labels = change_matrix.index.tolist()
    if class_names:
        display_labels = [class_names.get(lbl, str(lbl)) for lbl in labels]
    else:
        display_labels = [str(lbl) for lbl in labels]
    
    fig, ax = plt.subplots(figsize=figsize)
    
    im = ax.imshow(change_matrix.values, cmap=cmap, interpolation='nearest')
    
    # Add colorbar
    cbar = plt.colorbar(im, ax=ax)
    cbar.set_label('Number of pixels changed', rotation=270, labelpad=20)
    
    # Set ticks and labels
    ax.set_xticks(np.arange(len(labels)))
    ax.set_yticks(np.arange(len(labels)))
    ax.set_xticklabels(display_labels, rotation=45, ha='right')
    ax.set_yticklabels(display_labels)
    
    ax.set_xlabel("Time 2 (To)")
    ax.set_ylabel("Time 1 (From)")
    ax.set_title(title)
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Figure saved to: {save_path}")
    
    return fig


def plot_net_change_bar(stats, title="Net Change by Class",
                        figsize=(10, 6), class_names=None,
                        save_path=None):
    """
    Create bar plot showing net change for each class.
    
    Parameters
    ----------
    stats : dict
        Statistics from calculate_change_statistics
    title : str
        Plot title
    figsize : tuple
        Figure size
    class_names : dict or None
        Optional mapping of class IDs to names
    save_path : Path or None
        If provided, save figure to this path
        
    Returns
    -------
    matplotlib.figure.Figure
        The created figure
    """
    classes = list(stats['net_change'].keys())
    net_changes = [stats['net_change'][cls] for cls in classes]
    
    if class_names:
        labels = [f"{cls}: {class_names.get(cls, str(cls))}" for cls in classes]
    else:
        labels = [str(cls) for cls in classes]
    
    fig, ax = plt.subplots(figsize=figsize)
    
    # Color bars based on positive/negative change
    colors = ['green' if nc > 0 else 'red' if nc < 0 else 'gray' 
              for nc in net_changes]
    
    bars = ax.barh(labels, net_changes, color=colors, alpha=0.7)
    
    ax.set_xlabel('Net Change (pixels)')
    ax.set_title(title)
    ax.axvline(x=0, color='black', linewidth=0.8, linestyle='--')
    ax.grid(axis='x', alpha=0.3)
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Figure saved to: {save_path}")
    
    return fig


def save_analysis_results(transition_matrix, stats, output_dir, 
                          dataset_name, class_names=None):
    """
    Save all analysis results to files.
    
    Parameters
    ----------
    transition_matrix : pd.DataFrame
        Transition matrix
    stats : dict
        Statistics dictionary
    output_dir : Path
        Directory to save results
    dataset_name : str
        Name of dataset for file naming
    class_names : dict or None
        Optional class name mapping
        
    Returns
    -------
    dict
        Paths to saved files
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    saved_files = {}
    
    # Save transition matrix
    matrix_path = output_dir / f"{dataset_name}_transition_matrix.csv"
    transition_matrix.to_csv(matrix_path)
    saved_files['transition_matrix'] = matrix_path
    print(f"Transition matrix saved: {matrix_path}")
    
    # Save change summary table
    summary_df = create_change_summary_table(stats, class_names)
    summary_path = output_dir / f"{dataset_name}_change_summary.csv"
    summary_df.to_csv(summary_path, index=False)
    saved_files['change_summary'] = summary_path
    print(f"Change summary saved: {summary_path}")
    
    # Save overall statistics
    overall_stats = {
        'Total_Pixels': stats['total_pixels'],
        'Unchanged_Pixels': stats['unchanged_pixels'],
        'Changed_Pixels': stats['changed_pixels'],
        'Change_Percentage': stats['change_percentage']
    }
    stats_df = pd.DataFrame([overall_stats])
    stats_path = output_dir / f"{dataset_name}_overall_statistics.csv"
    stats_df.to_csv(stats_path, index=False)
    saved_files['overall_statistics'] = stats_path
    print(f"Overall statistics saved: {stats_path}")
    
    # Create visualizations
    fig1 = plot_transition_matrix(
        transition_matrix, 
        title=f"Transition Matrix - {dataset_name}",
        class_names=class_names,
        save_path=output_dir / f"{dataset_name}_transition_matrix.png"
    )
    plt.close(fig1)
    saved_files['transition_plot'] = output_dir / f"{dataset_name}_transition_matrix.png"
    
    fig2 = plot_change_heatmap(
        transition_matrix,
        title=f"Change Heatmap - {dataset_name}",
        class_names=class_names,
        save_path=output_dir / f"{dataset_name}_change_heatmap.png"
    )
    plt.close(fig2)
    saved_files['change_heatmap'] = output_dir / f"{dataset_name}_change_heatmap.png"
    
    fig3 = plot_net_change_bar(
        stats,
        title=f"Net Change - {dataset_name}",
        class_names=class_names,
        save_path=output_dir / f"{dataset_name}_net_change.png"
    )
    plt.close(fig3)
    saved_files['net_change_plot'] = output_dir / f"{dataset_name}_net_change.png"
    
    return saved_files
