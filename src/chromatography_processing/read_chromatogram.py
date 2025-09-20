from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime

import xarray
import xarray as xr


def get_chromatogram_indices(data: pd.DataFrame, search_string: str):
    """Finds where the cation and anion chromatograms begin and end.
    search_string should be 'cation' or 'anion'.

    :param data: pandas.DataFrame
    :param search_string: str
    :returns: tuple of ints. Starting and ending indices of the data.
    """

    search_string_index = data[
        data.str.contains(search_string, case=False)
    ].index.tolist()[0]

    # ignore this row of data and next two
    data_start_index = search_string_index + 3
    to_search = data.iloc[data_start_index:]

    lines_without_semicolon = to_search[
        ~to_search.str.contains(";", case=False)
    ].index.tolist()
    data_end_index = (
        -1 if len(lines_without_semicolon) == 0 else lines_without_semicolon[0]
    )
    return (data_start_index, data_end_index)


def process_chromatogram_from_list_to_dataframe(data: list) -> pd.DataFrame:
    """Takes data from a list of strings and cleans it into a dataframe.

    Retrns data, a Dataframe with columns "time" and "signal".
    """
    data = data.str.split(pat=";", expand=True)
    data = data.rename(
        columns={data.columns[0]: "time", data.columns[1]: "signal"}
    )
    data = data.astype(float)
    return data


def read_chromatogram(
    path_to_data: Path,
    unmeasured_ion_placeholder=-1.0,
) -> (tuple, str, datetime):
    """Reads a Metrohm ion chromatogram file, as exported in .txt format.

    Automatically reads sample name as entered into the ion chromatograph by
    the user.

    Also automatically reads the time of measurement.

    Discards cation and anion pressure data.

    If only one of cation and anion was measured, the unmeasured ion is still
    returned. Its values are all set to the value of unmeasured_ion_placeholder
     (default -1).

    # Note: NaN might be more sensible, but causes problems later.

    :param path_to_data: pathlib.Path.
    Path to the data file.


    :param unmeasured_ion_placeholder: The value to assign to any unmeasured
    ion's data.

    I.e., if only anions were measured, all cation chromatogram values are
    rendered as the value of this variable.

    Returns: nested tuple, containing:

    (anion data, cation data), tuple of dataframes in the first position

    sample identity (str), the name of the sample

    time of measurement (datetime.datetime)

    ion_types, tuple of bools. First position of this variable indicates if
    anions are present; second that cations are present.
    """
    data = pd.read_csv(path_to_data, encoding="unicode-escape")
    data = data.iloc[:, 0]  # convert to a series

    # get the identity and measurement time
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
    else:  # if anions are not present
        # process the data as if they were, but fill with unmeasured ion
        # placeholder
        indices = get_chromatogram_indices(data, "Cation")
        an = data.iloc[indices[0] : indices[1]]
        an = process_chromatogram_from_list_to_dataframe(an)
        an["signal"] = (
            unmeasured_ion_placeholder  # replace with placeholder data
        )

    if cations_present:
        indices = get_chromatogram_indices(data, "Cation")
        cat = data.iloc[indices[0] : indices[1]]
        cat = process_chromatogram_from_list_to_dataframe(cat)
    else:  # if cations are not present...
        # process the data as if they were, but fill with unmeasured ion
        # placeholder
        indices = get_chromatogram_indices(data, "Anion")
        cat = data.iloc[indices[0] : indices[1]]
        cat = process_chromatogram_from_list_to_dataframe(cat)
        cat["signal"] = (
            unmeasured_ion_placeholder  # replace with placeholder data
        )

    ion_types = (anions_present, cations_present)
    return (an, cat), ident, meas_time, ion_types


def plot_chromatogram(data):
    fig, ax = plt.subplots()
    ax.plot(data["t"], data["cond"])
    plt.show()
    return


def read_chromatograms_in_folder_to_xarray(
    path_to_folder: Path,
) -> xarray.Dataset:
    """
    :param path_to_folder: pathlib.Path.
    The path to the folder containing all of the data files that will be read.

    :returns:
    data: xarray.Dataset.
    The data for the entire folder.
    """
    # Find all .txt files in the folder.
    files = path_to_folder.glob("*.txt")

    # make a list of chromatograms
    data = [read_chromatogram(file) for file in files]

    # Extract the different things we care about
    # (I know this is shockingly inelegant)
    anion_data = [d[0][0] for d in data]
    cation_data = [d[0][1] for d in data]
    idents = [d[1] for d in data]
    measurement_times = [d[2] for d in data]
    anions_present = [d[3][0] for d in data]
    cations_present = [d[3][1] for d in data]

    def convert_ion_data_to_xarray_and_combine(data: xarray.Dataset):
        """Converts data from list of pandas DataFrames to xarray.Dataset.

        First converts each DataFrame into an xarray.DataArray. Then
        combines automatically. Returns a dataset with ion_type (i.e.
        cation or anion), measurement_time (a proxy for order of
        measurement), and time (time in seconds inside the chromatogram)
        as coords.
        """

        data = [
            d.set_index(["ion_type", "measurement_time", "time"]) for d in data
        ]
        data = [d.to_xarray() for d in data]
        data = xr.combine_by_coords(data, join="outer")
        return data

    if anions_present:  # process anions into dataset
        for d, t, ident in zip(anion_data, measurement_times, idents):
            d["measurement_time"] = t
            d["ident"] = ident
            d["ion_type"] = "anion"
        anion_data = convert_ion_data_to_xarray_and_combine(anion_data)

    if cations_present:  # process cations into dataset
        for d, t, ident in zip(cation_data, measurement_times, idents):
            d["measurement_time"] = t
            d["ident"] = ident
            d["ion_type"] = "cation"
        cation_data = convert_ion_data_to_xarray_and_combine(cation_data)

    # combine cation, anion data
    to_combine = []
    if anions_present:
        to_combine.append(anion_data)
    if cations_present:
        to_combine.append(cation_data)
    data = xr.combine_by_coords(to_combine, join="outer")

    # take the idents data variable and convert it to a coord
    def convert_idents_to_coord(data):
        idents = data["ident"].isel(time=0, ion_type=0).values.tolist()
        new_idents = []
        for ident in idents:
            if "ian_pos" in ident:
                i = int(ident.split("ian_pos")[1])
                new_idents.append(i)
                pass
            else:
                new_idents.append(ident)
        data = data.drop_vars(["ident"])
        data = data.assign_coords(ident=("measurement_time", idents))
        return data

    data = convert_idents_to_coord(data)

    data = data.dropna(dim="time", how="all")

    # interpolate the data to put it all on one time grid
    # this is to avoid times like 1.00067 and 1.00066 seconds
    # from being classified differently.
    # This allows background subtraction later.
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
    time_grid = np.linspace(
        data.time.values.min(), data.time.values.max(), 2000
    )
    data = interpolated_ds.interp(time=time_grid)
    return data
