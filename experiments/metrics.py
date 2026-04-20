from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np
import xarray as xr

from .models import MetricRecord
from .store import Store, utcnow


def _coarsen_time(ds: xr.Dataset, hours_per_sol: int) -> xr.Dataset:
    if "time" not in ds.dims or hours_per_sol <= 1 or ds.sizes.get("time", 0) < hours_per_sol:
        return ds
    return ds.coarsen(time=hours_per_sol, boundary="trim").mean()


def _select_mars_year(ds: xr.Dataset, my: int) -> xr.Dataset:
    if "MY" not in ds or "time" not in ds["MY"].dims:
        return ds
    valid_times = ds["time"].where(ds["MY"] == my, drop=True)
    if valid_times.size == 0:
        return ds
    return ds.sel(time=valid_times)


def _peak_payload(values: np.ndarray, lat: np.ndarray, ls: np.ndarray, top_n: int = 2) -> list[dict[str, float]]:
    flat = np.asarray(values, dtype=float)
    if flat.size == 0:
        return []
    flat = np.where(np.isfinite(flat), flat, -np.inf)
    candidate_count = min(flat.size, max(32, top_n * 16))
    flat_indices = np.argpartition(flat.ravel(), -candidate_count)[-candidate_count:]
    flat_indices = flat_indices[np.argsort(flat.ravel()[flat_indices])[::-1]]
    peaks: list[tuple[int, int, float]] = []
    for flat_index in flat_indices:
        lat_index, time_index = np.unravel_index(flat_index, flat.shape)
        value = float(flat[lat_index, time_index])
        if not np.isfinite(value):
            continue
        if any(abs(lat_index - other_lat) <= 2 and abs(time_index - other_time) <= 2 for other_lat, other_time, _ in peaks):
            continue
        peaks.append((lat_index, time_index, value))
        if len(peaks) >= top_n:
            break
    payload = []
    for lat_index, time_index, value in peaks:
        payload.append(
            {
                "lat": float(lat[lat_index]),
                "ls": float(ls[time_index]),
                "value": value,
            }
        )
    return payload


def _extract_cdod_metrics(ds: xr.Dataset, my: int, hours_per_sol: int) -> dict[str, Any]:
    if "tausurf" not in ds or "phs" not in ds:
        raise KeyError("tausurf/phs missing from h0 output")
    wanted = [name for name in ("tausurf", "phs", "Ls", "MY") if name in ds]
    subset = _select_mars_year(ds[wanted], my)
    subset = _coarsen_time(subset, hours_per_sol)
    cdod = subset["tausurf"] * 610.0 / subset["phs"] / 3.67
    zonal = cdod.mean(dim="lon") if "lon" in cdod.dims else cdod
    lat_name = "lat" if "lat" in zonal.dims else zonal.dims[0]
    time_name = "time" if "time" in zonal.dims else zonal.dims[-1]
    field = zonal.transpose(lat_name, time_name)
    lat = np.asarray(field[lat_name].values)
    if "Ls" in subset and "time" in subset["Ls"].dims:
        ls = np.asarray(subset["Ls"].values, dtype=float)
    else:
        ls = np.arange(field.sizes[time_name], dtype=float)
    peaks = _peak_payload(np.asarray(field.values), lat, ls, top_n=2)
    primary = peaks[0] if peaks else {"lat": np.nan, "ls": np.nan, "value": np.nan}
    secondary = peaks[1] if len(peaks) > 1 else {"lat": np.nan, "ls": np.nan, "value": np.nan}
    peak_ratio = np.nan
    if np.isfinite(primary["value"]) and np.isfinite(secondary["value"]) and primary["value"] != 0:
        peak_ratio = secondary["value"] / primary["value"]
    peak_separation = np.nan
    if np.isfinite(primary["ls"]) and np.isfinite(secondary["ls"]):
        peak_separation = abs(secondary["ls"] - primary["ls"])
    return {
        "primary_peak": primary,
        "secondary_peak": secondary,
        "peak_ratio": float(peak_ratio) if np.isfinite(peak_ratio) else None,
        "peak_separation_ls": float(peak_separation) if np.isfinite(peak_separation) else None,
        "annual_mean": float(zonal.mean(skipna=True).item()),
        "global_max": float(zonal.max(skipna=True).item()),
    }


def _extract_dust_metrics(ds: xr.Dataset) -> dict[str, Any] | None:
    ddl = ds["dstflx_ddl"] if "dstflx_ddl" in ds else None
    wsl = ds["dstflx_wsl"] if "dstflx_wsl" in ds else None
    if ddl is None and wsl is None:
        return None
    payload: dict[str, Any] = {}
    if ddl is not None:
        payload["ddl_flux_time_mean"] = float(ddl.mean(skipna=True).item())
        payload["ddl_flux_integral"] = float(ddl.sum(skipna=True).item())
    if wsl is not None:
        payload["wsl_flux_time_mean"] = float(wsl.mean(skipna=True).item())
        payload["wsl_flux_integral"] = float(wsl.sum(skipna=True).item())
    ddl_integral = payload.get("ddl_flux_integral")
    wsl_integral = payload.get("wsl_flux_integral")
    if ddl_integral not in (None, 0) and wsl_integral is not None:
        payload["wsl_to_ddl_ratio"] = float(wsl_integral / ddl_integral)
    else:
        payload["wsl_to_ddl_ratio"] = None
    return payload


def extract_metrics(exp_id: str, *, store: Store | None = None) -> MetricRecord:
    store = store or Store()
    metadata = store.load_metadata(exp_id)
    experiment_dir = Path(metadata["paths"]["experiment_dir"])
    case_name = str(metadata["derived"]["case_name"])
    h0_files = sorted(experiment_dir.glob(f"{case_name}.h0*.nc"))
    if not h0_files:
        raise FileNotFoundError(f"No h0 files found for case {case_name}")
    if len(h0_files) == 1:
        ds = xr.open_dataset(str(h0_files[0]))
    else:
        ds = xr.open_mfdataset([str(path) for path in h0_files], combine="by_coords").load()
    try:
        metrics: dict[str, Any] = {
            "cdod610": _extract_cdod_metrics(
                ds,
                int(metadata.get("my", 1)),
                int(metadata.get("hours_per_sol", 24)),
            )
        }
        dust_metrics = _extract_dust_metrics(ds)
        if dust_metrics is not None:
            metrics["dust_lifting"] = dust_metrics
    finally:
        ds.close()
    payload = {
        "schema_version": 1,
        "experiment_id": exp_id,
        "computed_at": utcnow(),
        "inputs": {
            "my": int(metadata.get("my", 1)),
            "hours_per_sol": int(metadata.get("hours_per_sol", 24)),
            "source_files": [str(path.resolve()) for path in h0_files],
        },
        "metrics": metrics,
        "diagnostic_artifacts": metadata.get("diagnostics", {}),
    }
    store.update_metrics(exp_id, payload)
    return MetricRecord(
        experiment_id=exp_id,
        computed_at=payload["computed_at"],
        metrics=metrics,
        source_files=h0_files,
    )
