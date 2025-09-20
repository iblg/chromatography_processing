import pandas as pd
from pybaselines import Baseline
import numpy as np
import xarray as xr


def fit_dataset_with_custom_bc_baseline(
    data,
    anion_time_range,
    cation_time_range,
    x: str = "time",
    y: str = "signal",
    crossover_index_number: int = 160,
    lam: float = 1e8,
    lam_flexible: float = 1e8,
    method: str = "arpls",
    sampling: int = 15,
):

    results = []
    for ion_type in data.ion_type.values:
        # trim by time before fitting
        if ion_type == "anion":
            time_range = anion_time_range
        elif ion_type == "cation":
            time_range = cation_time_range
        d = data.sel(ion_type=ion_type)
        d = d.where(d.time >= time_range[0], drop=True)
        d = d.where(d.time <= time_range[1], drop=True)

        for i in range(d.ident.shape[0]):  # for sample in samples
            # select this sample and drop nans
            to_fit = d.isel(measurement_time=i).dropna(dim="time", how="all")

            bck, params = find_custom_bc_baseline(
                to_fit.to_dataframe(),
                x=x,
                y=y,
                crossover_index_number=crossover_index_number,
                lam=lam,
                lam_flexible=lam_flexible,
                method=method,
                sampling=sampling,
            )

            bck = pd.DataFrame(bck, columns=["bck"])
            bck["ion_type"] = ion_type
            bck["time"] = to_fit.time.values
            bck["measurement_time"] = to_fit.measurement_time.values
            bck["ident"] = to_fit.ident.values
            # with pd.option_context('display.max_columns', None,):
            #     print(bck)
            bck = bck.set_index(["ion_type", "time", "measurement_time"])
            bck = bck.to_xarray()
            results.append(bck)

    background = xr.combine_by_coords(results, join="outer")
    data["background"] = background["bck"]
    data["reduced_signal"] = data["signal"] - data["background"]

    return data


def find_custom_bc_baseline(
    data: pd.DataFrame,
    x: str = "time",
    y: str = "signal",
    crossover_index_number: int = 160,
    lam: float = 1e8,
    lam_flexible: float = 1e6,
    method: str = "arpls",
    sampling: int = 15,
) -> (np.ndarray, dict):
    """
    data: pd.DataFrame
    The data for which you want to find the baseline signal.

    x: str, default 'time'
    The name of the column in data which serves as the x-axis.
    Note: if x is not 'time', it currently causes problems with HPLC-py.
    It is recommended to name it 'time'.

    y: str
    The name of the column in data which serves as the y-axis.

    crossover_index_number: int, default 160

    lam: float, default 1e8

    lam_flexible: float, default 1e6
    Increase lam_flexible to make the fitting less sensitive.
    Decrease lam_flexible to make the fitting more sensitive.

    method: str, default 'arpls'

    sampling: int, default 15

    Returns:
    bck: np.ndarray
    The data points of the baseline.

    params: dict
    The params of the baseline
    """
    data = data.reset_index()
    x = data[x]
    y = data[y]
    crossover_index = np.argmin(abs(x - crossover_index_number))
    baseline_fitter = Baseline(x_data=x)

    bck, params = baseline_fitter.custom_bc(
        y,
        method,
        regions=([crossover_index, None],),
        sampling=sampling,
        method_kwargs={"lam": lam_flexible},
        lam=lam,
    )

    return bck, params
