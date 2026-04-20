from __future__ import annotations

import numpy as np
import xarray as xr


_TIME_DIMS = ("time",)
_LEV_DIMS = ("lev", "ilev")
_LAT_DIMS = ("lat", "ilat")
_LON_DIMS = ("lon", "ilon")


def inspect_nc(filepath: str) -> dict:
    """Inspect a NetCDF file and summarize variables for plotting."""
    ds = _open_dataset(filepath)
    try:
        sizes = {name: int(size) for name, size in ds.sizes.items()}
        variables = []
        has_levels = False

        for name, var in ds.data_vars.items():
            dims = tuple(var.dims)
            lev_dim = _first_matching_dim(dims, _LEV_DIMS)
            if lev_dim is not None and sizes.get(lev_dim, 1) > 1:
                has_levels = True

            variables.append(
                {
                    "name": name,
                    "dims": dims,
                    "shape": tuple(int(length) for length in var.shape),
                    "long_name": var.attrs.get("long_name", ""),
                    "units": var.attrs.get("units", ""),
                    "plot_type": classify_variable(name, dims, sizes),
                }
            )

        time_dim = _first_matching_dim(ds.sizes.keys(), _TIME_DIMS)
        return {
            "dims": sizes,
            "variables": variables,
            "time_steps": sizes.get(time_dim, 0) if time_dim is not None else 0,
            "has_levels": has_levels,
        }
    finally:
        ds.close()


def classify_variable(var_name: str, dims: tuple, sizes: dict) -> str:
    """Classify a variable into a plotting-friendly shape category."""
    del var_name

    time_dim = _first_matching_dim(dims, _TIME_DIMS)
    has_time = time_dim is not None and sizes.get(time_dim, 0) > 0

    lat_dim = _first_matching_dim(dims, _LAT_DIMS)
    lon_dim = _first_matching_dim(dims, _LON_DIMS)
    lev_dim = _first_matching_dim(dims, _LEV_DIMS)

    lat_active = lat_dim is not None and sizes.get(lat_dim, 1) > 1
    lon_active = lon_dim is not None and sizes.get(lon_dim, 1) > 1
    lev_active = lev_dim is not None and sizes.get(lev_dim, 1) > 1

    active_non_time_dims = [
        dim for dim in dims if dim not in _TIME_DIMS and sizes.get(dim, 1) > 1
    ]

    if lat_active and lon_active and lev_active:
        return "map_2d_with_level"

    if lat_active and lon_active:
        if has_time:
            return "map_2d"
        return "static_map"

    if lat_active and lev_active and not lon_active:
        return "lat_height"

    if lon_active and lev_active and not lat_active:
        return "lon_height"

    if has_time and not active_non_time_dims:
        if sizes.get(time_dim, 0) > 1:
            return "time_series"
        return "scalar"

    if not dims or not [dim for dim in dims if sizes.get(dim, 1) > 1]:
        return "scalar"

    return "unknown"


def load_variable_slice(
    filepath: str,
    var_name: str,
    time_idx: int = None,
    level_idx: int = None,
    view_mode: str = "horizontal",
) -> tuple:
    """Load a plotting slice and the corresponding coordinates.

    ``view_mode`` selects the cross-section for ``map_2d_with_level`` variables:

    - ``"horizontal"`` — isel level, return a ``(lat, lon)`` map (default).
    - ``"zonal"`` — isel latitude, return a ``(lev, lon)`` cross-section
      (x-direction vertical section). ``level_idx`` is reused as the lat index.
    - ``"meridional"`` — isel longitude, return a ``(lev, lat)`` cross-section
      (y-direction vertical section). ``level_idx`` is reused as the lon index.
    """
    ds = _open_dataset(filepath)
    try:
        data = ds[var_name]
        sizes = {name: int(size) for name, size in ds.sizes.items()}
        plot_type = classify_variable(var_name, tuple(data.dims), sizes)

        time_dim = _first_matching_dim(data.dims, _TIME_DIMS)
        lev_dim = _first_matching_dim(data.dims, _LEV_DIMS)
        lat_dim = _first_matching_dim(data.dims, _LAT_DIMS)
        lon_dim = _first_matching_dim(data.dims, _LON_DIMS)

        coords = {}

        if plot_type != "time_series" and time_dim is not None:
            idx = 0 if time_idx is None else int(time_idx)
            coords["time"] = _coord_scalar(data, time_dim, idx, _TIME_DIMS)
            data = data.isel({time_dim: idx})
        elif plot_type == "time_series" and time_dim is not None:
            coords["time"] = _axis_values(data, time_dim, _TIME_DIMS)

        if plot_type == "map_2d_with_level":
            if lev_dim is None:
                raise ValueError(f"Variable {var_name!r} has no level dimension.")

            if view_mode == "zonal":
                if lat_dim is None:
                    raise ValueError(f"Variable {var_name!r} has no latitude dim.")
                idx = data.sizes[lat_dim] // 2 if level_idx is None else int(level_idx)
                coords["slice_lat"] = _coord_scalar(data, lat_dim, idx, _LAT_DIMS)
                data = data.isel({lat_dim: idx})
                data = data.squeeze(drop=True).transpose(lev_dim, lon_dim)
                coords["lev"] = _axis_values(data, lev_dim, _LEV_DIMS)
                coords["lon"] = _axis_values(data, lon_dim, _LON_DIMS)
                return np.asarray(data.values), coords

            if view_mode == "meridional":
                if lon_dim is None:
                    raise ValueError(f"Variable {var_name!r} has no longitude dim.")
                idx = data.sizes[lon_dim] // 2 if level_idx is None else int(level_idx)
                coords["slice_lon"] = _coord_scalar(data, lon_dim, idx, _LON_DIMS)
                data = data.isel({lon_dim: idx})
                data = data.squeeze(drop=True).transpose(lev_dim, lat_dim)
                coords["lev"] = _axis_values(data, lev_dim, _LEV_DIMS)
                coords["lat"] = _axis_values(data, lat_dim, _LAT_DIMS)
                return np.asarray(data.values), coords

            # Default: horizontal slice at a level.
            idx = data.sizes[lev_dim] // 2 if level_idx is None else int(level_idx)
            coords["lev"] = _coord_scalar(data, lev_dim, idx, _LEV_DIMS)
            data = data.isel({lev_dim: idx})
            data = data.squeeze(drop=True).transpose(lat_dim, lon_dim)
            coords["lat"] = _axis_values(data, lat_dim, _LAT_DIMS)
            coords["lon"] = _axis_values(data, lon_dim, _LON_DIMS)
            return np.asarray(data.values), coords

        if plot_type in {"map_2d", "static_map"}:
            data = data.squeeze(drop=True).transpose(lat_dim, lon_dim)
            coords["lat"] = _axis_values(data, lat_dim, _LAT_DIMS)
            coords["lon"] = _axis_values(data, lon_dim, _LON_DIMS)
            return np.asarray(data.values), coords

        if plot_type == "lat_height":
            if lon_dim is not None and lon_dim in data.dims:
                data = data.mean(dim=lon_dim)
            data = data.squeeze(drop=True).transpose(lev_dim, lat_dim)
            coords["lev"] = _axis_values(data, lev_dim, _LEV_DIMS)
            coords["lat"] = _axis_values(data, lat_dim, _LAT_DIMS)
            return np.asarray(data.values), coords

        if plot_type == "lon_height":
            if lat_dim is not None and lat_dim in data.dims:
                data = data.mean(dim=lat_dim)
            data = data.squeeze(drop=True).transpose(lev_dim, lon_dim)
            coords["lev"] = _axis_values(data, lev_dim, _LEV_DIMS)
            coords["lon"] = _axis_values(data, lon_dim, _LON_DIMS)
            return np.asarray(data.values), coords

        if plot_type == "time_series":
            data = data.squeeze(drop=True)
            if time_dim is not None and time_dim in data.dims:
                data = data.transpose(time_dim)
            return np.asarray(data.values), coords

        data = data.squeeze(drop=True)
        if data.ndim == 0:
            return np.asarray(data.values), coords

        for dim, key, aliases in (
            (lat_dim, "lat", _LAT_DIMS),
            (lon_dim, "lon", _LON_DIMS),
            (lev_dim, "lev", _LEV_DIMS),
        ):
            if dim is not None and dim in data.dims:
                coords[key] = _axis_values(data, dim, aliases)

        return np.asarray(data.values), coords
    finally:
        ds.close()


_TERRAIN_CANDIDATES: tuple[str, ...] = ("gzs", "zs", "phis", "topo", "hs")


def load_terrain_field(filepath: str) -> tuple[np.ndarray, np.ndarray, np.ndarray] | None:
    """Return ``(topo, lat, lon)`` from *filepath* or ``None`` if not present.

    Tries common terrain names (``gzs`` — surface geopotential, ``zs`` —
    surface height, etc.) and returns the first match collapsed to 2-D.
    """
    try:
        ds = _open_dataset(filepath)
    except Exception:
        return None
    try:
        for name in _TERRAIN_CANDIDATES:
            if name in ds.data_vars:
                var = ds[name]
                lat_dim = _first_matching_dim(var.dims, _LAT_DIMS)
                lon_dim = _first_matching_dim(var.dims, _LON_DIMS)
                if lat_dim is None or lon_dim is None:
                    continue
                # Collapse any extra dims (time, lev) by taking the first slice.
                for dim in list(var.dims):
                    if dim not in (lat_dim, lon_dim):
                        var = var.isel({dim: 0})
                var = var.squeeze(drop=True).transpose(lat_dim, lon_dim)
                lat = _axis_values(var, lat_dim, _LAT_DIMS)
                lon = _axis_values(var, lon_dim, _LON_DIMS)
                return np.asarray(var.values), lat, lon
        return None
    except Exception:
        return None
    finally:
        ds.close()


_G_ACC = 9.80616  # m / s^2, used to convert geopotential → height.


def load_terrain_slice(
    filepath: str, view_mode: str, slice_idx: int | None,
) -> tuple[np.ndarray, np.ndarray] | None:
    """Return ``(terrain_m, coord)`` for a vertical cross-section.

    - ``view_mode == "zonal"``: terrain along longitude at given latitude index.
    - ``view_mode == "meridional"``: terrain along latitude at given longitude index.

    The terrain is normalized to **meters** (geopotential fields are divided
    by ``g``). Returns ``None`` if no terrain variable is present.
    """
    if view_mode not in {"zonal", "meridional"}:
        return None
    try:
        ds = _open_dataset(filepath)
    except Exception:
        return None
    try:
        for name in _TERRAIN_CANDIDATES:
            if name not in ds.data_vars:
                continue
            var = ds[name]
            lat_dim = _first_matching_dim(var.dims, _LAT_DIMS)
            lon_dim = _first_matching_dim(var.dims, _LON_DIMS)
            if lat_dim is None or lon_dim is None:
                continue
            for dim in list(var.dims):
                if dim not in (lat_dim, lon_dim):
                    var = var.isel({dim: 0})
            var = var.squeeze(drop=True).transpose(lat_dim, lon_dim)
            if view_mode == "zonal":
                size = var.sizes[lat_dim]
                idx = size // 2 if slice_idx is None else int(slice_idx)
                idx = max(0, min(idx, size - 1))
                strip = var.isel({lat_dim: idx})
                coord = _axis_values(strip, lon_dim, _LON_DIMS)
            else:
                size = var.sizes[lon_dim]
                idx = size // 2 if slice_idx is None else int(slice_idx)
                idx = max(0, min(idx, size - 1))
                strip = var.isel({lon_dim: idx})
                coord = _axis_values(strip, lat_dim, _LAT_DIMS)
            values = np.asarray(strip.values, dtype=float)
            if name in {"gzs", "phis"}:
                values = values / _G_ACC  # geopotential → height
            return values, np.asarray(coord)
        return None
    except Exception:
        return None
    finally:
        ds.close()


def load_slice_axis(
    filepath: str, var_name: str, view_mode: str = "horizontal",
) -> np.ndarray | None:
    """Return the coordinate array for the axis the slider indexes.

    ``view_mode`` selects the axis — level for horizontal, latitude for zonal,
    longitude for meridional. Returns ``None`` if the dimension or variable
    cannot be located.
    """
    try:
        ds = _open_dataset(filepath)
    except Exception:
        return None
    try:
        if var_name not in ds.variables:
            return None
        data = ds[var_name]
        if view_mode == "zonal":
            dim, aliases = _first_matching_dim(data.dims, _LAT_DIMS), _LAT_DIMS
        elif view_mode == "meridional":
            dim, aliases = _first_matching_dim(data.dims, _LON_DIMS), _LON_DIMS
        else:
            dim, aliases = _first_matching_dim(data.dims, _LEV_DIMS), _LEV_DIMS
        if dim is None:
            return None
        return np.asarray(_axis_values(data, dim, aliases))
    except Exception:
        return None
    finally:
        ds.close()


def load_variable_global_range(
    filepath: str,
    var_name: str,
    slice_idx: int | None = None,
    view_mode: str = "horizontal",
) -> tuple[float | None, float | None]:
    """Compute min/max across all time steps for the active slice.

    ``view_mode`` controls which dimension ``slice_idx`` indexes:

    - ``"horizontal"`` — isel along level (unchanged original behaviour).
    - ``"zonal"`` — isel along latitude (x-direction vertical cross-section).
    - ``"meridional"`` — isel along longitude (y-direction vertical cross-section).
    """
    ds = _open_dataset(filepath)
    try:
        data = ds[var_name]

        if view_mode == "zonal":
            target_dim = _first_matching_dim(data.dims, _LAT_DIMS)
        elif view_mode == "meridional":
            target_dim = _first_matching_dim(data.dims, _LON_DIMS)
        else:
            target_dim = _first_matching_dim(data.dims, _LEV_DIMS)

        if target_dim is not None:
            idx = data.sizes[target_dim] // 2 if slice_idx is None else int(slice_idx)
            idx = max(0, min(idx, data.sizes[target_dim] - 1))
            data = data.isel({target_dim: idx})

        v_min = float(data.min(skipna=True).compute().values)
        v_max = float(data.max(skipna=True).compute().values)
        return v_min, v_max
    except Exception:
        return None, None
    finally:
        ds.close()


def get_smart_colormap(var_name: str, data: "np.ndarray") -> tuple:
    """Choose a sensible Plotly-style colorscale and symmetry hint."""
    name = var_name.lower()
    finite = np.asarray(data, dtype=float)
    finite = finite[np.isfinite(finite)]

    if finite.size == 0:
        return "Viridis", False

    data_min = float(finite.min())
    data_max = float(finite.max())
    symmetric = _looks_symmetric(data_min, data_max)
    straddles_zero = _straddles_zero(data_min, data_max)

    if _is_known_symmetric_name(name):
        return "RdBu_r", True

    if _is_known_positive_name(name):
        return "Viridis", False

    if symmetric:
        return "RdBu_r", True

    if straddles_zero:
        return "RdBu_r", False

    return "Viridis", False


def _open_dataset(filepath: str) -> xr.Dataset:
    try:
        return xr.open_dataset(filepath)
    except Exception as first_error:
        try:
            return xr.open_dataset(filepath, decode_times=False)
        except Exception:
            raise first_error


def _first_matching_dim(dims, aliases):
    for dim in dims:
        if dim in aliases:
            return dim
    return None


def _axis_values(data: xr.DataArray, dim: str, aliases: tuple) -> np.ndarray:
    coord = _find_coord(data, dim, aliases)
    if coord is not None:
        return np.asarray(coord.values)
    return np.arange(data.sizes[dim])


def _coord_scalar(data: xr.DataArray, dim: str, idx: int, aliases: tuple):
    coord = _find_coord(data, dim, aliases)
    if coord is None:
        return idx

    value = np.asarray(coord.isel({dim: idx}).values)
    if value.size == 1:
        return value.reshape(()).item()
    return value


def _find_coord(data: xr.DataArray, dim: str, aliases: tuple):
    for name in aliases:
        if name in data.coords and data.coords[name].dims == (dim,):
            return data.coords[name]

    if dim in data.coords:
        return data.coords[dim]

    return None


def _is_known_symmetric_name(name: str) -> bool:
    return (
        "pv" in name
        or "vor" in name
        or "w_lev" in name
        or name == "w"
        or name.startswith("w_")
        or name.startswith("dpt")
        or name.startswith("du")
    )


def _is_known_positive_name(name: str) -> bool:
    return name in {"t", "ph", "gz", "q"}


def _looks_symmetric(data_min: float, data_max: float) -> bool:
    if data_min >= 0 or data_max <= 0:
        return False

    scale = max(abs(data_min), abs(data_max))
    if scale == 0:
        return False

    return abs(abs(data_min) - abs(data_max)) / scale <= 0.2


def _straddles_zero(data_min: float, data_max: float) -> bool:
    if data_min >= 0 or data_max <= 0:
        return False

    scale = max(abs(data_min), abs(data_max))
    if scale == 0:
        return False

    return min(abs(data_min), abs(data_max)) / scale >= 0.1
