# Temporal Analysis Documentation

## Overview

This module provides comprehensive tools for temporal analysis of landcover datasets. It enables comparison of landcover classifications across different time periods to identify changes, quantify transitions between categories, and detect trends.

## Features

- **Transition Matrix Calculation**: Quantifies pixel transitions between categories across time periods
- **Change Statistics**: Computes detailed statistics including:
  - Total and percentage of changed pixels
  - Class persistence (stability) rates
  - Net gains and losses per class
  - Pixel-level transition counts
- **Visualization**: Generates multiple types of visualizations:
  - Transition matrix heatmaps
  - Change-only heatmaps (excluding stable pixels)
  - Net change bar plots
- **Multi-dataset Support**: Works with WorldCover, CORINE, and other raster datasets

## Usage

### CORINE (2012 → 2018)

```bash
cd /home/runner/work/landcover_analysis/landcover_analysis
python -m scripts.analysis.corine.temporal_analysis
```

### WorldCover (2020 → 2021)

```bash
cd /home/runner/work/landcover_analysis/landcover_analysis
python -m scripts.analysis.worldcover.temporal_analysis
```

### General Purpose

```bash
python scripts/analysis/temporal_analysis_general.py \
    path/to/time1.tif \
    path/to/time2.tif \
    output_directory/ \
    dataset_name \
    --class-mapping class_names.csv
```

For detailed documentation, see the full documentation file.
