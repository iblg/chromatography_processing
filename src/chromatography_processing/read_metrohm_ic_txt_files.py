import pandas as pd
from pathlib import Path


def read_metrohm_ic_txt_file(path_to_data: Path) -> pd.DataFrame:
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

    return an, cat


def main():
    return


if __name__ == "__main__":
    main()
