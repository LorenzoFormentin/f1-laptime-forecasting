# F1 Laptime Forecasting

Machine learning project scaffold for training and evaluating lap time prediction models using the [FastF1](https://docs.fastf1.dev/) ecosystem.

## Goals (scope)

- Build reproducible datasets from FastF1 sessions (race/quali/practice) with a clear cache strategy.
- Support multiple model families (baselines, classical ML, PyTorch) behind a consistent training/evaluation interface.
- Train and evaluate lap time prediction under different conditions (e.g., clean air vs traffic, different stints/compounds, different sessions).

## Non-goals (for now)

- Locking down a single feature set or a single model architecture.
- Picking a mandatory experiment tracker/config framework. These may be added later if/when needed.

## Repository layout

- `data/`  
  - `cache/fastf1/` is the local FastF1 cache directory (gitignored).
  - `raw/`, `interim/`, `processed/` are reserved for dataset artifacts.
- `notebooks/` exploratory analysis and sanity checks.
- `src/f1laptime/` library code (dataset building, features, models, training).
- `scripts/` thin CLI wrappers (build/train/predict).

## Setup

### Create the conda environment

```bash
conda env create -f environment.yml
conda activate f1-laptime-forecasting
```

### initialize project and test

```bash
pip install -e .
pytest
```
