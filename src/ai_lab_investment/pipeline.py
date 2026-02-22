import logging
import time

import hydra
from dotenv import load_dotenv
from omegaconf import DictConfig

from .utils.directories import get_data_directories, get_results_directories
from .utils.files import timestamp_file

load_dotenv()


def _run_phase1():
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


def _run_phase2():
    from .figures.phase2 import generate_all_phase2_figures
    from .models import DuopolyModel, ModelParameters

    logging.info("Running Phase 2: Duopoly with default risk")
    p = ModelParameters()

    # All-equity equilibrium
    duo_eq = DuopolyModel(p, leverage=0.0)
    summary = duo_eq.summary()
    for key, val in summary.items():
        logging.info(f"  {key}: {val}")

    # Levered equilibrium
    duo_lev = DuopolyModel(p, leverage=0.4, coupon_rate=0.05, bankruptcy_cost=0.30)
    summary_lev = duo_lev.summary()
    logging.info("Levered equilibrium:")
    for key, val in summary_lev.items():
        logging.info(f"  {key}: {val}")

    results_dirs = get_results_directories()
    generate_all_phase2_figures(p, results_dirs.figures)
    logging.info("Phase 2 figures saved")


@hydra.main(version_base=None, config_path="../../conf", config_name="config")
def pipeline(cfg: DictConfig):
    start_time = time.time()
    logging.getLogger().setLevel(cfg.logging_level)

    data_dirs = get_data_directories()
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
        _run_phase1()
    if cfg.tasks.phase2_duopoly:
        _run_phase2()

    logging.info(f"Complete. Total runtime: {time.time() - start_time:.2f} seconds")


if __name__ == "__main__":
    pipeline()
