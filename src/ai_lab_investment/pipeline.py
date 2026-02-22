import logging
import time

import hydra
from dotenv import load_dotenv
from omegaconf import DictConfig

from .utils.directories import get_data_directories, get_results_directories
from .utils.files import timestamp_file

load_dotenv()


@hydra.main(version_base=None, config_path="../../conf", config_name="config")
def pipeline(cfg: DictConfig):
    start_time = time.time()
    logging.getLogger().setLevel(cfg.logging_level)

    data_dirs = get_data_directories()
    # results_dirs = get_results_directories()

    # n_bs = cfg.params.n_bootstrap_samples
    # mp = cfg.params.multiprocessing

    panel_path = data_dirs.clean / "panel.parquet"

    if cfg.data.download:
        logging.info("Downloading data")
    if cfg.data.preprocess:
        logging.info("Preprocessing data")
    if cfg.data.build_panel:
        logging.info("Building panel data")
    if cfg.data.save_panel:
        logging.info("Saving panel data")
        panel_file = timestamp_file(panel_path)
        logging.info(f"Panel saved to {panel_file}")

    if cfg.tasks.simulations:
        logging.info("Running simulation")

    if cfg.tasks.main_regressions:
        logging.info("Running regression analysis")

    if cfg.tasks.phase1_base_model:
        from .figures.phase1 import generate_all_phase1_figures
        from .models import ModelParameters, SingleFirmModel

        logging.info("Running Phase 1: Single-firm base model")
        params = ModelParameters()
        model = SingleFirmModel(params)
        summary = model.summary()
        for regime, results in summary.items():
            logging.info(f"Regime {regime}: {results}")

        results_dirs = get_results_directories()
        generate_all_phase1_figures(params, results_dirs.figures)
        logging.info("Phase 1 figures saved")

    logging.info(f"Complete. Total runtime: {time.time() - start_time:.2f} seconds")


if __name__ == "__main__":
    pipeline()
