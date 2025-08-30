# import pytest
from chromatography_processing.read_metrohm_ic_txt_files import (
    read_metrohm_ic_txt_file,
)
from pathlib import Path

# datapath = (Path(__file__).parent.parent / 'metrohm_ic_test_files' /
#             'ancat_chromatogram.txt')
datapath = Path("/Users/ianbillinge/dev/chromatography_processing/tests/")
datapath = datapath / "metrohm_ic_test_files" / "ancat_chromatogram.txt"


def test_first_data_point_is_correct():
    actual_anion, actual_cation = read_metrohm_ic_txt_file(datapath)
    actual_anion = actual_anion.iloc[0]
    actual_anion = (actual_anion["time"], actual_anion["signal"])
    actual_cation = actual_cation.iloc[0]
    actual_cation = (actual_cation["time"], actual_cation["signal"])

    expected_cation = (0.0, -1416.9620868828902)
    expected_anion = (0.0, 0.9706243877162339)
    assert actual_cation == expected_cation
    assert actual_anion == expected_anion
