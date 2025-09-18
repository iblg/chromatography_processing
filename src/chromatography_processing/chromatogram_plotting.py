import xarray as xr
import matplotlib.pyplot as plt
from pathlib import Path
from matplotlib import colormaps
from matplotlib.colors import Normalize


def plot_all_from_run(
    data: xr.Dataset, save_plots_to: Path, show_flag: bool = False
):
    """
    data: xr.Dataset
    Dataset containing chromatography data

    save_plots_to: Path
    Path where you want to save plots. Should include filename. '_anion.png' or
    '_cation.png' will be added as applicable.

    show_flag: bool, default False.
    If True, show the plot in addition to saving it.
    """

    cmap = colormaps["viridis"]
    # norm = Normalize(vmin=data.ident.shape)
    norm = Normalize(vmin=0, vmax=data.measurement_time.shape[0])

    anion = data.sel(ion_type="anion")
    cation = data.sel(ion_type="cation")

    parent_dir = save_plots_to.parent
    parent_dir.mkdir(parents=True, exist_ok=True)
    filename = save_plots_to.stem
    anion_filename = filename + "_anion.png"
    cation_filename = filename + "_cation.png"

    def plot_anion_or_cation(ds, parent_dir, filename, show_flag):
        fig, ax = plt.subplots()
        for i in range(ds.ident.shape[0]):
            print("i is {}".format(i))
            to_plot = ds.isel(measurement_time=i).dropna(dim="time", how="all")
            print(to_plot)
            ax.plot(
                to_plot.time,
                to_plot.signal,
                ".",
                label=str(i),
                color=cmap(norm(i)),
            )
        plt.legend(ncol=3)
        save_to = parent_dir / filename
        plt.savefig(save_to, bbox_inches="tight", dpi=300)
        if show_flag:
            plt.show()
        return

    plot_anion_or_cation(anion, parent_dir, anion_filename, show_flag)
    plot_anion_or_cation(cation, parent_dir, cation_filename, show_flag)

    return
