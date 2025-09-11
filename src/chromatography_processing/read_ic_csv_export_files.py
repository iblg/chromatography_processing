import pandas as pd
import shutil


def copy_csvs_to_from_import(path_to_files):
    """If a from_import folder exists, nothing happens. If no from_import
    folder exists, this function creates one and transfers all .csv files in
    the given path to path_to_files/from_import.

    :param path_to_files: Path Path to find the collection of IC files
        to process
    :return:
    """
    from_import_path = path_to_files / "from_import"
    if from_import_path.exists():
        print("Folder {} exists".format(str(from_import_path)))
        print("Not copying any files")
        return
    else:
        from_import_path.mkdir()
        original_file_paths = list(path_to_files.glob("*.csv"))
        destination_file_paths = [
            from_import_path / file.name for file in original_file_paths
        ]
        [
            print("Original {}, destination {}".format(src, dest))
            for src, dest in zip(original_file_paths, destination_file_paths)
        ]
        [
            shutil.copy(src, dest)
            for src, dest in zip(original_file_paths, destination_file_paths)
        ]
    return


def open_ic_file(path_to_file):
    """Open an IC file and set the Ident column to be the index. Requires that
    the Ident column have format '*posX' where * is any text, pos is the
    characters pos, and X is an integer. Also rewrites all column titles to be
    lower-case.

    :param path_to_file: Path Path to fild data files
    :return:
    """
    print("reading {}".format(path_to_file))
    # help(pd.read_csv)
    df = pd.read_csv(path_to_file, delimiter=";")
    idx = df["Ident"].iloc[0]
    idx = idx.split("pos")[1]
    idx = int(idx)
    df["index_col"] = idx
    df = df.set_index("index_col")
    df.columns = [x.lower() for x in df.columns]
    return df


def open_list_of_ic_files(parent_dir):
    """Opens a list of ic files.

    :param parent_dir: pathlib.Path Path to directory containing IC
        files
    :return:
    """
    files = list(parent_dir.glob("*.csv"))
    print("In open_list_of_ic_files")
    print(files)
    data = [open_ic_file(file) for file in files]
    data = pd.concat(data, axis="rows")
    data = data.sort_index()
    return data


def save_to_dir(data, filename, target_dir):

    if target_dir.exists():
        pass
    else:
        target_dir.mkdir()

    path_out = (target_dir / filename).with_suffix(".csv")
    data.to_csv(path_out, index=False)
    return
