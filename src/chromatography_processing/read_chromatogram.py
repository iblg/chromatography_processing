from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime
import xarray as xr


def get_chromatogram_indices(data, search_string):
    search_string_index = data[
        data.str.contains(search_string, case=False)
    ].index.tolist()[0]
    data_start_index = search_string_index + 3  # ignore this row and next two
    to_search = data.iloc[data_start_index:]
    # print(to_search)

    lines_without_semicolon = to_search[
        ~to_search.str.contains(";", case=False)
    ].index.tolist()
    data_end_index = (
        -1 if len(lines_without_semicolon) == 0 else lines_without_semicolon[0]
    )
    # for j in range(start_index+3, len(data)):
    #     print(data[j].strip())
    #     if data[j].strip() == '' or data[j].strip(';') == 0:
    #         end_index = j-1
    #     break
    return (data_start_index, data_end_index)


def process_chromatogram_from_list_to_dataframe(data):
    data = data.str.split(pat=";", expand=True)
    data = data.rename(
        columns={data.columns[0]: "time", data.columns[1]: "signal"}
    )
    data = data.astype(float)
    return data


def read_chromatogram(
    path_to_data: Path,
) -> (tuple, str, datetime):
    """
    :param path_to_data: pathlib.Path. Path to the data file.
    Returns: tuple, containing anion data, cation data, sample identity,
    time of measurement
    """
    data = pd.read_csv(path_to_data, encoding="unicode-escape")
    data = data.iloc[:, 0]  # convert to a series
    ident = data.iloc[0]
    meas_time = data.name
    meas_time = meas_time.split(" UTC")[0]
    meas_time = datetime.strptime(meas_time, "%Y-%m-%d %H:%M:%S")

    # drop pressure data, leaving only conductivity
    pressure_indices = data[data.str.contains("Pressure")].index.tolist()
    data = data[: pressure_indices[0]]

    # determine what kind of ions are present
    anion_chromatogram_indices = data[
        data.str.contains("Anion")
    ].index.tolist()
    cation_chromatogram_indices = data[
        data.str.contains("Cation")
    ].index.tolist()

    anions_present = True if len(anion_chromatogram_indices) > 0 else False
    cations_present = True if len(cation_chromatogram_indices) > 0 else False

    if anions_present:
        indices = get_chromatogram_indices(data, "Anion")
        an = data.iloc[indices[0] : indices[1]]
        an = process_chromatogram_from_list_to_dataframe(an)
    else:  # if anioons are not present
        # process the data as if they were, but fill with np.nan
        indices = get_chromatogram_indices(data, "Cation")
        an = data.iloc[indices[0] : indices[1]]
        an = process_chromatogram_from_list_to_dataframe(an)
        an["signal"] = -1  # replace with placeholder data

    if cations_present:
        indices = get_chromatogram_indices(data, "Cation")
        cat = data.iloc[indices[0] : indices[1]]
        cat = process_chromatogram_from_list_to_dataframe(cat)

    else:  # if cations are not present...
        # process as if they were, but replace 'signal' with nan
        indices = get_chromatogram_indices(data, "Anion")
        cat = data.iloc[indices[0] : indices[1]]
        cat = process_chromatogram_from_list_to_dataframe(cat)
        cat["signal"] = -1  # replace with placeholder data

    # an = an.str.split(pat=";", expand=True)
    # an = an.rename(columns={an.columns[0]: "time", an.columns[1]: "signal"})
    # an = an.astype(float)
    #
    #
    # cat = cat.str.split(pat=";", expand=True)
    # cat = cat.rename(
    #     columns={cat.columns[0]: "time", cat.columns[1]: "signal"}
    # )
    # cat = cat.astype(float)

    # print(meas_time.name)
    types = (anions_present, cations_present)
    return (an, cat), ident, meas_time, types


def plot_chromatogram(data):
    fig, ax = plt.subplots()
    ax.plot(data["t"], data["cond"])
    plt.show()
    return


def read_chromatograms_in_folder_to_xarray(path_to_folder):
    # glob the files
    files = path_to_folder.glob("*.txt")
    data = [read_chromatogram(file) for file in files]
    anion_data = [d[0][0] for d in data]
    cation_data = [d[0][1] for d in data]
    idents = [d[1] for d in data]
    measurement_times = [d[2] for d in data]
    anions_present = [d[3][0] for d in data]
    cations_present = [d[3][1] for d in data]

    def process_anion_or_cation_data(data, meas_type):
        data = [
            d.set_index(["ion_type", "time", "measurement_time"]) for d in data
        ]
        data = [d.to_xarray() for d in data]
        # data = xr.concat(data, dim='measurement_time')
        data = xr.combine_by_coords(data, join="outer")
        return data

    if anions_present:
        for d, t, ident in zip(anion_data, measurement_times, idents):
            d["measurement_time"] = t
            d["ident"] = ident
            d["ion_type"] = "anion"
        anion_data = process_anion_or_cation_data(anion_data, "anion")

    if cations_present:
        for d, t, ident in zip(cation_data, measurement_times, idents):
            d["measurement_time"] = t
            d["ident"] = ident
            d["ion_type"] = "cation"
        cation_data = process_anion_or_cation_data(cation_data, "cation")

    to_combine = []
    if anions_present:
        to_combine.append(anion_data)
    if cations_present:
        to_combine.append(cation_data)

    data = xr.combine_by_coords(to_combine, join="outer")

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
    data = interpolated_ds.interp(
        time=np.linspace(data.time.values.min(), data.time.values.max(), 2000)
    )
    return data
