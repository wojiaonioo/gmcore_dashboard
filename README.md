# gmcore-dashboard

Standalone experiment management and visualization dashboard for GMCORE.

## Installation

```bash
# From GMCORE root (development mode)
pip install -e tools/gmcore_dashboard

# Or with uv
uv pip install -e tools/gmcore_dashboard
```

## Usage

### Dashboard Web UI

```bash
# Auto-detect GMCORE root (works when installed inside GMCORE tree)
gmcore-dashboard

# Explicit GMCORE root
gmcore-dashboard --gmcore-root /path/to/gmcore

# Or via environment variable
GMCORE_ROOT=/path/to/gmcore gmcore-dashboard

# Custom host/port
gmcore-dashboard --host 0.0.0.0 --port 8080
```

### Experiment CLI

```bash
# List experiments
gmcore-experiments list

# Create and run an experiment
gmcore-experiments create cdod_baseline
gmcore-experiments run <experiment_id>

# Sweep
gmcore-experiments sweep ddl_wsl_sweep --run

# Diagnostics
gmcore-experiments diag <experiment_id> --set-name core
```

## Configuration

The package resolves paths relative to `GMCORE_ROOT`. Resolution order:

1. `--gmcore-root` CLI flag
2. `GMCORE_ROOT` environment variable
3. Auto-detection by walking up the directory tree

### `registry.yaml`

All paths in `registry.yaml` are relative to `GMCORE_ROOT`:
- `workspace_root` — where experiment data is stored
- `executable` — path to compiled `gmcore_driver.exe`
- `template` — namelist template path

## As a Git Submodule

When this package lives in its own repository, pull it with:

```bash
git submodule update --init tools/gmcore_dashboard
```

Or via `pull_libs.py` which handles this automatically.
