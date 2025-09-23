import xarray as xr
from hplc.quant import Chromatogram


def make_chromatograms_for_ion_type(
    data: xr.Dataset,
    ion_type: str,
    y_variable="reduced_signal",
    x_variable="time",
) -> xr.Dataset:
    data = data.sel(ion_type=ion_type)
    chromatogram_list = []

    for mt in data.coords["measurement_time"]:
        sample = data.sel(measurement_time=mt)
        sample = sample[y_variable]
        sample = sample.dropna(dim="time", how="all")
        sample = sample.to_dataframe().reset_index()
        chrom = Chromatogram(
            sample, cols={"time": x_variable, "signal": y_variable}
        )
        chromatogram_list.append(chrom)

    chromatogram_DataArray = xr.DataArray(
        chromatogram_list,
        coords={
            "measurement_time": data.measurement_time.values,
            "ion_type": ion_type,
        },
        dims=["measurement_time"],
    )

    data["chromatogram"] = chromatogram_DataArray
    return data


def fit_chromatograms_for_ion_type(
    data: xr.Dataset,
    ion_type: str,
) -> xr.Dataset:
    """Fit whole dataset worth of chromatograms.

    NOTE: This is very likely to crash unless your data is sparkly clean. It is
    recommended to get rid of any samples that have odd features before passing
    your dataset to this function.
    """
    data = data.sel(ion_type=ion_type)
    fitting_results_list = []

    for mt in data.coords["measurement_time"]:
        sample = data.sel(measurement_time=mt)
        print(sample.ident)
        chrom = unpack_chromatogram_of_single_sample(sample)
        fitting_results = chrom.fit_peaks()
        fitting_results_list.append(fitting_results)
    print(fitting_results_list)
    fitting_results_DataArray = xr.DataArray(
        fitting_results_list,
        coords={
            "measurement_time": data.measurement_time.values,
            "ion_type": ion_type,
        },
        dims=["measurement_time"],
    )

    data["fitting_results"] = fitting_results_DataArray
    return data


def fit_chromatograms_for_dataset(ds: xr.Dataset) -> xr.Dataset:
    if isinstance(ds, xr.Dataset):
        pass
    else:
        raise TypeError("ds must be an xr.Dataset object")

    anions = fit_chromatograms_for_ion_type(ds, ion_type="anion")
    cations = fit_chromatograms_for_ion_type(ds, ion_type="cation")

    ds = xr.concat([anions, cations], dim="ion_type")
    return ds


def make_chromatograms_for_dataset(ds: xr.Dataset) -> xr.Dataset:
    if isinstance(ds, xr.Dataset):
        pass
    else:
        raise TypeError("ds must be an xr.Dataset object")

    anions = make_chromatograms_for_ion_type(
        ds, ion_type="anion", y_variable="reduced_signal"
    )
    cations = make_chromatograms_for_ion_type(
        ds, ion_type="cation", y_variable="reduced_signal"
    )

    ds = xr.concat([anions, cations], dim="ion_type")
    return ds


def unpack_chromatogram_of_single_sample(sample: xr.Dataset) -> Chromatogram:
    """Given a dataset where you have selected the sample and ion type already,
    returns a Chromatogram object.

    Essentially a helper function to avoid having to unpack.
    """
    ch = sample[
        "chromatogram"
    ]  # get the chromatogram object, without the other variables
    ch = (
        ch.values
    )  # ch.values will return an array with only one object inside it
    # (the chromatogram)
    ch = ch.item()  # ch.item will get the item out from the array
    return ch
