import xarray as xr
from pathlib import Path
import matplotlib.pyplot as plt


def diagnostic_plot_bck_sub(
    data: xr.Dataset,
    ion_type: str,
    plot_dir: Path | str,
    meas_date: str,
    ion_times: dict | str = "default",
    show_flag: bool = False,
    close_flag: bool = True,
    dpi: int = 100,
) -> None:
    """
    :param: data (xarray.Dataset)
    :param: ion_type (str)
    'cation' or 'anion'
    :param: plot_dir (pathlib.Path | str)
    Tells the program which directory to save figures to.
    :param: meas_date (str)
    Date of the measurement. This date tells the program how to save the plots.

    :param: ion_times (dict | str), default = 'default'
    Dict showing the time ranges in minutes where you expect ions to show up.
    Format is dict of dicts. First layer down is a dict with key 'anion' or
    'cation'. Inside this dict, keys are ion names. Vals are tuples with the
    time ranges to integrate over.
    If ion_times == default,
        ion_times= {
            'anion': {
                'nitrite': (6.55, 7.5),
                'nitrate': (9.1, 10.7),
                },
            'cation': {
                'ammonium': (3.6, 4.10)
                }

    :param: show_flag (bool), default = False.
    If True, plots are shown. Otherwise, plots are not shown.

    :param: close_flag (bool), default = True.
    If True, plots close after showing, to prevent Matplotlib error from too
    many windows open.
    :param: dpi (int), default = 100.
    The dots per inch to save the plots.
    """

    if ion_times == "default":
        ion_times = {
            "anion": {
                "nitrite": (6.55, 7.5),
                "nitrate": (9.1, 10.7),
            },
            "cation": {"ammonium": (3.6, 4.10)},
        }

    for idx, i in enumerate(data.measurement_time.values):
        d = data.sel(measurement_time=i)
        d = d.sel(ion_type=ion_type)
        d = d.dropna(dim="time", how="all")
        fig, ax = plt.subplots(nrows=2, ncols=1, sharex=True)
        ax[0].plot(d.time, d.signal)
        ax[0].plot(d.time, d.background)
        ax[1].fill_between(
            d.time, 0 * d.reduced_signal, d.reduced_signal, alpha=0.5
        )
        # plot ion_peaks
        it = ion_times[ion_type]
        for ion, times in it.items():
            ion_data = d.where(d.time < times[1]).where(d.time > times[0])
            ax[1].fill_between(
                ion_data.time,
                0 * ion_data.reduced_signal,
                ion_data.reduced_signal,
                alpha=0.5,
                label=ion,
            )
        ax[1].set_xlabel("Time (sec)")
        ax[0].set_ylabel("Conductivity")
        ax[1].set_ylabel("Conductivity")
        ax[1].legend()
        plt.savefig(
            plot_dir / f"{ion_type}_{meas_date}_sample_{idx}.pdf",
            dpi=dpi,
            bbox_inches="tight",
        )
        if show_flag:
            plt.show()
        if close_flag:
            plt.close()
    return
