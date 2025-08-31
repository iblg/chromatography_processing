import pandas as pd
from pathlib import Path
import re
import xarray as xr


def read_metrohm_ic_txt_file(path_to_data: Path) -> pd.DataFrame:
    data = pd.read_csv(path_to_data, encoding="unicode-escape")
    data = data.iloc[:, 0]  # convert to a series

    # get rack positions
    rack_position = data.iloc[0]
    rack_position = re.findall(r"\d+", rack_position)
    rack_position = int(rack_position[0])

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

    return an, cat, rack_position


def read_metrohm_ic_files_to_xarray(file_paths: list) -> xr.Dataset:
    anion_dfs, cation_dfs = [], []
    for file in file_paths:
        anion_df, cation_df, rack_position = read_metrohm_ic_txt_file(file)

        cation_df["rack_position"] = rack_position
        anion_df["rack_position"] = rack_position
        anion_dfs.append(anion_df)
        cation_dfs.append(cation_df)

    anion_df = pd.concat(anion_dfs)
    cation_df = pd.concat(cation_dfs)
    # anion_df = anion_df.rename(columns={'signal':'anion_signal'})
    # cation_df = cation_df.rename(columns={'signal':'cation_signal'})
    anion_df["type"] = "anion"
    cation_df["type"] = "cation"
    anion_df = anion_df.set_index(["type", "rack_position", "time"])
    cation_df = cation_df.set_index(["type", "rack_position", "time"])
    anion_data = anion_df.to_xarray()
    cation_data = cation_df.to_xarray()
    data = xr.concat([anion_data, cation_data], dim="type", join="outer")
    return data


def main():
    return


if __name__ == "__main__":
    main()
