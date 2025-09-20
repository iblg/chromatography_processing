import xarray as xr


def fit_dataset(ds: xr.Dataset):
    if isinstance(ds, xr.Dataset):
        pass
    else:
        raise TypeError("ds must be an xr.Dataset object")

    return
