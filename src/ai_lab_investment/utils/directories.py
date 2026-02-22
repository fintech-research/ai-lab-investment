import os
from collections import namedtuple
from pathlib import Path

from dotenv import load_dotenv

from ..exceptions import MissingEnvVarError

load_dotenv()


DataDirectories = namedtuple(
    "DataDirectories",
    ["data", "clean", "preprocessing", "download", "open", "restricted", "results"],
)

ResultsDirectories = namedtuple(
    "ResultsDirectories",
    ["results", "figures", "tables", "text"],
)


def get_data_directories() -> DataDirectories:
    """Get standardized data directory paths from environment variables.

    Creates the download directory if it doesn't exist. All other directories
    are expected to be created by the user or other parts of the application.

    Returns:
        DataDirectories: A named tuple containing the following Path objects:
            - data: Root data directory
            - clean: Clean/processed data directory
            - preprocessing: Preprocessing cache directory
            - download: Download cache directory (created if missing)
            - open: Open/public raw data directory
            - restricted: Restricted raw data directory
            - results: Results directory

    Raises:
        MissingEnvVarError: If the DATA_DIR environment variable is not set.

    Example:
        >>> dirs = get_data_directories()
        >>> clean_file = dirs.clean / "dataset.parquet"
    """
    datadir_path = os.getenv("DATA_DIR")
    if not datadir_path:
        raise MissingEnvVarError("DATA_DIR")

    data_dir = Path(datadir_path)
    clean_dir = data_dir / "clean/"
    preprocessing_dir = data_dir / "preprocessing-cache/"
    download_dir = data_dir / "raw" / "download_cache/"
    open_dir = data_dir / "raw" / "open/"
    restricted_dir = data_dir / "raw" / "restricted/"
    results_dir = data_dir / "results/"

    download_dir.mkdir(parents=True, exist_ok=True)

    return DataDirectories(
        data=data_dir,
        clean=clean_dir,
        preprocessing=preprocessing_dir,
        download=download_dir,
        open=open_dir,
        restricted=restricted_dir,
        results=results_dir,
    )


def get_results_directories() -> ResultsDirectories:
    """Get standardized results directory paths from environment variables.

    Returns:
        ResultsDirectories: A named tuple containing the following Path objects:
            - results: Root results directory
            - figures: Figures output directory
            - tables: Tables output directory
            - text: Text output directory

    Raises:
        MissingEnvVarError: If the RESULTS_DIR environment variable is not set.

    Example:
        >>> dirs = get_results_directories()
        >>> figure_path = dirs.figures / "plot.png"
    """
    resultsdir_path = os.getenv("RESULTS_DIR")
    if not resultsdir_path:
        raise MissingEnvVarError("RESULTS_DIR")

    results_dir = Path(resultsdir_path)
    fig_dir = results_dir / "figures/"
    tab_dir = results_dir / "tables/"
    text_dir = results_dir / "text/"

    return ResultsDirectories(
        results=results_dir,
        figures=fig_dir,
        tables=tab_dir,
        text=text_dir,
    )
