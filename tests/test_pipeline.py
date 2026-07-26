"""End-to-end smoke tests for the Hydra pipeline entry point.

`python -m ai_lab_investment` composes `conf/config.yaml` and dispatches
to the phase runners in `pipeline.py`. These tests drive that same entry
point through Hydra's compose API, with `RESULTS_DIR` redirected to a
temporary directory so nothing is written to the real results tree.

The whole pipeline runs in ~13s, so every phase is exercised by default.
"""

from pathlib import Path

import matplotlib
import pytest
from hydra import compose, initialize_config_dir

matplotlib.use("Agg")

import matplotlib.pyplot as plt

from ai_lab_investment.pipeline import _TASK_RUNNERS, pipeline

CONF_DIR = Path(__file__).resolve().parents[1] / "conf"
TASK_NAMES = sorted(_TASK_RUNNERS)


@pytest.fixture(autouse=True)
def _close_figures():
    yield
    plt.close("all")


def _make_cfg(enabled: set[str]):
    overrides = [
        f"tasks.{name}={'true' if name in enabled else 'false'}" for name in TASK_NAMES
    ]
    with initialize_config_dir(config_dir=str(CONF_DIR), version_base=None):
        return compose(config_name="config", overrides=overrides)


def _redirect_results(monkeypatch, tmp_path: Path) -> Path:
    results = tmp_path / "results"
    for sub in ("figures", "tables", "text"):
        (results / sub).mkdir(parents=True, exist_ok=True)
    monkeypatch.setenv("RESULTS_DIR", str(results))
    return results


def test_config_exposes_every_task_runner():
    """Every runner in `_TASK_RUNNERS` must have a toggle in config.yaml,
    and vice versa, or a phase would silently never run."""
    cfg = _make_cfg(set())
    assert sorted(cfg.tasks) == TASK_NAMES


def test_pipeline_with_all_tasks_disabled(monkeypatch, tmp_path):
    """The entry point composes and runs with every phase off."""
    results = _redirect_results(monkeypatch, tmp_path)
    pipeline(_make_cfg(set()))
    assert not list((results / "figures").iterdir())
    assert not list((results / "tables").iterdir())


@pytest.mark.parametrize("task", TASK_NAMES)
def test_pipeline_phase_runs_and_writes_output(task, monkeypatch, tmp_path):
    """Each phase runs end-to-end and writes to RESULTS_DIR."""
    results = _redirect_results(monkeypatch, tmp_path)
    pipeline(_make_cfg({task}))
    written = list((results / "figures").iterdir()) + list(
        (results / "tables").iterdir()
    )
    assert written, f"{task} produced no output under RESULTS_DIR"
