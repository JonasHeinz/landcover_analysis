# landcover_analysis

## Project Overview

This project provides tools for analyzing and comparing different landcover datasets, including temporal analysis to track changes over time.

## Features

### Temporal Analysis
Compare landcover datasets across different time periods to identify changes and trends:
- **Transition Matrices**: Quantify pixel transitions between land cover categories
- **Change Statistics**: Calculate change percentages, class persistence, gains, and losses
- **Visualizations**: Generate heatmaps, difference maps, and trend plots

Supported datasets:
- **CORINE Land Cover** (2012 → 2018)
- **ESA WorldCover** (2020 → 2021)
- **Custom raster datasets** via general-purpose tools

### Analysis Scripts

#### Quick Start: CORINE Temporal Analysis
```bash
cd /home/runner/work/landcover_analysis/landcover_analysis
python -m scripts.analysis.corine.temporal_analysis
```

Outputs transition matrices, change statistics, and visualizations to:
`data/analysis/corine/temporal_analysis/`

#### Quick Start: WorldCover Temporal Analysis
```bash
python -m scripts.analysis.worldcover.temporal_analysis
```

#### General Purpose Analysis
For any two raster files:
```bash
python scripts/analysis/temporal_analysis_general.py \
    path/to/time1.tif \
    path/to/time2.tif \
    output_directory/ \
    dataset_name
```

## Documentation

- **Temporal Analysis**: See [docs/temporal_analysis_documentation.md](docs/temporal_analysis_documentation.md) for detailed usage instructions, examples, and API reference

## Project Structure

```
landcover_analysis/
├── data/                      # Data files (excluded from git)
│   ├── preprocessing/         # Preprocessed datasets
│   └── analysis/              # Analysis results
├── scripts/
│   ├── helpers/               # Reusable helper functions
│   │   ├── temporal_analysis_helper.py  # Temporal analysis core functions
│   │   └── raster_helper.py
│   ├── analysis/              # Analysis scripts
│   │   ├── temporal_analysis_general.py  # General temporal analysis
│   │   ├── corine/
│   │   │   └── temporal_analysis.py      # CORINE-specific analysis
│   │   └── worldcover/
│   │       └── temporal_analysis.py      # WorldCover-specific analysis
│   └── preprocessing/         # Data preprocessing scripts
└── docs/                      # Documentation
```

## Requirements

- Python 3.8+
- rasterio
- pandas
- numpy
- matplotlib
- scikit-learn

Install dependencies:
```bash
pip install rasterio pandas numpy matplotlib scikit-learn
```