from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime
import xarray as xr


def read_chromatogram(
    path_to_data: Path,
) -> (pd.DataFrame, pd.DataFrame, str, datetime):
    """
    :param path_to_data: pathlib.Path. Path to the data file.
    Returns: tuple, containing anion data, cation data, sample identity,
    time of measurement
    """
    data = pd.read_csv(path_to_data, encoding="unicode-escape")
    data = data.iloc[:, 0]  # convert to a series
    anion_chromatogram_indices = data[
        data.str.contains("Anion")
    ].index.tolist()
    cation_chromatogram_indices = data[
        data.str.contains("Cation")
    ].index.tolist()

    an = data.iloc[
        anion_chromatogram_indices[0] + 3 : cation_chromatogram_indices[0]
    ]
    an = an.str.split(pat=";", expand=True)
    an = an.rename(columns={an.columns[0]: "time", an.columns[1]: "signal"})
    an = an.astype(float)

    cat = data.iloc[
        cation_chromatogram_indices[0] + 3 : anion_chromatogram_indices[1]
    ]
    cat = cat.str.split(pat=";", expand=True)
    cat = cat.rename(
        columns={cat.columns[0]: "time", cat.columns[1]: "signal"}
    )
    cat = cat.astype(float)

    ident = data.iloc[0]
    meas_time = data.name
    meas_time = meas_time.split(" UTC")[0]
    meas_time = datetime.strptime(meas_time, "%Y-%m-%d %H:%M:%S")
    # print(meas_time.name)
    return an, cat, ident, meas_time


def plot_chromatogram(data):
    fig, ax = plt.subplots()
    ax.plot(data["t"], data["cond"])
    plt.show()
    return


def read_chromatograms_in_folder_to_xarray(path_to_folder):
    # glob the files
    files = path_to_folder.glob("*.txt")
    data = [read_chromatogram(file) for file in files]
    anion_data = [d[0] for d in data]
    cation_data = [d[1] for d in data]
    idents = [d[2] for d in data]
    measurement_times = [d[3] for d in data]

    for d, t, ident in zip(anion_data, measurement_times, idents):
        d["measurement_time"] = t
        d["ident"] = ident
        d["ion_type"] = "anion"

    for d, t, ident in zip(cation_data, measurement_times, idents):
        d["measurement_time"] = t
        d["ident"] = ident
        d["ion_type"] = "cation"

    def process_anion_or_cation_data(data, meas_type):
        data = [
            d.set_index(["ion_type", "time", "measurement_time"]) for d in data
        ]
        data = [d.to_xarray() for d in data]
        # data = xr.concat(data, dim='measurement_time')
        data = xr.combine_by_coords(data, join="outer")
        return data

    anion_data = process_anion_or_cation_data(anion_data, "anion")
    cation_data = process_anion_or_cation_data(cation_data, "cation")
    data = xr.combine_by_coords([anion_data, cation_data], join="outer")

    idents = data["ident"].isel(time=0, ion_type=0).values.tolist()
    idents = [i.split("ian_pos") for i in idents]
    idents = [i[1] for i in idents]
    idents = [int(i) for i in idents]
    data = data.drop_vars(["ident"])
    data = data.assign_coords(ident=("measurement_time", idents))
    data = data.dropna(dim="time", how="all")

    # interpolate the data to put it all on one time grid
    def interpolate_data(
        ds: xr.Dataset, var_name: str, dim: str = "time"
    ) -> xr.Dataset:
        # Remove NaNs from the coordinate before interpolation
        if ds[dim].isnull().any():
            ds = ds.dropna(dim)

        # Fill NaNs in the dataset data with linear interpolation
        # (choose appropriate method)
        ds[var_name] = ds[var_name].interpolate_na(dim, method="linear")

        return ds

    # Apply interpolation
    interpolated_ds = interpolate_data(data, "signal", dim="time")
    print("\n\n MAX TIME ", data.time.values.max())
    data = interpolated_ds.interp(
        time=np.linspace(data.time.values.min(), data.time.values.max(), 2000)
    )
    return data
