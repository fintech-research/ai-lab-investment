import logging
import time

import hydra
from dotenv import load_dotenv
from omegaconf import DictConfig

from .utils.directories import get_data_directories, get_results_directories
from .utils.files import timestamp_file

load_dotenv()


def _run_data_steps(cfg: DictConfig):
    """Run data download, preprocessing, and panel building steps."""
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

    duo_eq = DuopolyModel(p, leverage=0.0)
    summary = duo_eq.summary()
    for key, val in summary.items():
        logging.info(f"  {key}: {val}")

    duo_lev = DuopolyModel(p, leverage=0.4, coupon_rate=0.05, bankruptcy_cost=0.30)
    summary_lev = duo_lev.summary()
    logging.info("Levered equilibrium:")
    for key, val in summary_lev.items():
        logging.info(f"  {key}: {val}")

    results_dirs = get_results_directories()
    generate_all_phase2_figures(p, results_dirs.figures)
    logging.info("Phase 2 figures saved")


def _run_phase3():
    from .figures.phase3 import generate_all_phase3_figures
    from .models import ModelParameters, NFirmModel

    logging.info("Running Phase 3: N-firm numerical solution")
    p = ModelParameters()

    for n in [2, 3, 4]:
        m = NFirmModel(p, n_firms=n, leverage=0.0)
        s = m.summary()
        logging.info(f"  N={n}: {len(s.get('entries', []))} entries")
        logging.info(f"    Total capacity: {s.get('total_capacity', 'N/A')}")

    results_dirs = get_results_directories()
    generate_all_phase3_figures(p, results_dirs.figures)
    logging.info("Phase 3 figures saved")


def _run_phase4():
    from .calibration import RevealedBeliefs, get_baseline_calibration
    from .figures.phase4 import generate_all_phase4_figures

    logging.info("Running Phase 4: Calibration and revealed beliefs")
    calib = get_baseline_calibration()
    rb = RevealedBeliefs(calib)

    summary = rb.summary()
    logging.info(f"  Firms analyzed: {summary['n_firms']}")
    for belief in summary["revealed_beliefs"]:
        logging.info(f"  {belief['firm']}: {belief}")

    results_dirs = get_results_directories()
    generate_all_phase4_figures(results_dirs.figures)
    logging.info("Phase 4 figures saved")


def _run_phase5():
    from .figures.phase5 import generate_all_phase5_figures
    from .models import ModelParameters, ValuationAnalysis

    logging.info("Running Phase 5: Valuation analysis")
    p = ModelParameters()
    va = ValuationAnalysis(p)

    summary = va.summary()
    d = summary["decomposition"]
    logging.info(f"  Total value: {d['total_value']:.4f}")
    logging.info(f"  Growth fraction: {d['growth_fraction']:.2%}")

    for lev_key, metrics in summary["credit"].items():
        logging.info(f"  {lev_key}: {metrics}")

    results_dirs = get_results_directories()
    generate_all_phase5_figures(results_dirs.figures)
    logging.info("Phase 5 figures saved")


_TASK_RUNNERS = {
    "simulations": lambda: logging.info("Running simulation"),
    "main_regressions": lambda: logging.info("Running regression analysis"),
    "phase1_base_model": _run_phase1,
    "phase2_duopoly": _run_phase2,
    "phase3_nfirm": _run_phase3,
    "phase4_calibration": _run_phase4,
    "phase5_valuation": _run_phase5,
}


@hydra.main(version_base=None, config_path="../../conf", config_name="config")
def pipeline(cfg: DictConfig):
    start_time = time.time()
    logging.getLogger().setLevel(cfg.logging_level)

    _run_data_steps(cfg)

    for task_name, runner in _TASK_RUNNERS.items():
        if getattr(cfg.tasks, task_name, False):
            runner()

    logging.info(f"Complete. Total runtime: {time.time() - start_time:.2f} seconds")


if __name__ == "__main__":
    pipeline()
