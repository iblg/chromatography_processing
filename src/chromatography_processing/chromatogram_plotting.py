import xarray as xr
import matplotlib.pyplot as plt
from pathlib import Path
from matplotlib import colormaps
from matplotlib.colors import Normalize


def plot_all_from_run(data: xr.Dataset, path: Path, show_flag: bool = False):

    cmap = colormaps["viridis"]
    norm = Normalize(vmin=data.ident.min(), vmax=data.ident.max())

    anion = data.sel(ion_type="anion")
    cation = data.sel(ion_type="cation")

    parent_dir = path.parent
    parent_dir.mkdir(parents=True, exist_ok=True)
    filename = path.stem
    anion_filename = filename + "_anion.png"
    cation_filename = filename + "_cation.png"

    def plot_anion_or_cation(ds, parent_dir, filename, show_flag):
        fig, ax = plt.subplots()
        for i in range(ds.ident.shape[0]):
            to_plot = ds.isel(measurement_time=i).dropna(dim="time", how="all")
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
