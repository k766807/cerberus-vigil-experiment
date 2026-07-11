from __future__ import annotations

import numpy as np
import pytest

from cerberus_vigil import (
    ExperimentConfig,
    first_sustained_crossing,
    illustrative_authority_level,
    rolling_pearson,
    simulate,
)


def small_config() -> ExperimentConfig:
    return ExperimentConfig(
        n_samples=600,
        commissioning_end=180,
        coupling_onset=250,
        behavioral_symptom=480,
        rolling_window=60,
        calibration_runs=5,
        evaluation_runs=5,
    )


def test_simulation_is_deterministic() -> None:
    cfg = small_config()
    first = simulate(42, cfg, coupling=True)
    second = simulate(42, cfg, coupling=True)
    for key in first:
        np.testing.assert_allclose(first[key], second[key], equal_nan=True)


def test_conditioning_suppresses_nominal_shared_environment() -> None:
    cfg = small_config()
    data = simulate(7, cfg, coupling=False)
    window = slice(cfg.commissioning_end, cfg.coupling_onset)
    raw = np.nanmedian(np.abs(data["raw_corr"][window]))
    residual = np.nanmedian(np.abs(data["residual_corr"][window]))
    assert residual < raw


def test_first_sustained_crossing() -> None:
    values = np.array([0.0, 0.6, 0.7, 0.8, 0.1])
    assert first_sustained_crossing(values, 0.5, start=0, run_length=3) == 1
    assert first_sustained_crossing(values, 0.75, start=0, run_length=2) is None


def test_authority_mapping_is_monotone_conservative() -> None:
    assert illustrative_authority_level(np.nan) == "A3"
    assert illustrative_authority_level(0.20) == "A3"
    assert illustrative_authority_level(0.40) == "A2"
    assert illustrative_authority_level(0.60) == "A1"
    assert illustrative_authority_level(0.80) == "A0"


def test_invalid_configuration_rejected() -> None:
    with pytest.raises(ValueError):
        ExperimentConfig(coupling_onset=400, commissioning_end=500).validate()


def test_rolling_pearson_matches_numpy_for_final_window() -> None:
    a = np.arange(20, dtype=float)
    b = a * 2.0 + 1.0
    result = rolling_pearson(a, b, 10)
    expected = np.corrcoef(a[-10:], b[-10:])[0, 1]
    assert result[-1] == pytest.approx(expected)
