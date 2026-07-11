"""Core simulation and monitoring primitives for the CERBERUS Vigil experiment.

This module is an explanatory research prototype. It is not flight software,
not a certified runtime-assurance component, and not a validated estimator of
failure-mode commonality.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from statistics import NormalDist
from typing import Any

import numpy as np


@dataclass(frozen=True)
class ExperimentConfig:
    """Configuration for the fixed-seed synthetic experiment."""

    n_samples: int = 1800
    commissioning_end: int = 500
    coupling_onset: int = 700
    behavioral_symptom: int = 1300
    rolling_window: int = 120
    coupling_max: float = 1.4
    alpha_one_sided: float = 0.05
    consecutive_alarm_samples: int = 10
    calibration_runs: int = 100
    evaluation_runs: int = 200
    representative_seed: int = 20260711

    def validate(self) -> None:
        if self.n_samples <= 0:
            raise ValueError("n_samples must be positive")
        if not 3 < self.rolling_window <= self.commissioning_end:
            raise ValueError("rolling_window must be > 3 and <= commissioning_end")
        if not 0 < self.commissioning_end < self.coupling_onset:
            raise ValueError("commissioning_end must precede coupling_onset")
        if not self.coupling_onset < self.behavioral_symptom < self.n_samples:
            raise ValueError("coupling_onset < behavioral_symptom < n_samples is required")
        if not 0.0 < self.alpha_one_sided < 0.5:
            raise ValueError("alpha_one_sided must be in (0, 0.5)")
        if self.consecutive_alarm_samples <= 0:
            raise ValueError("consecutive_alarm_samples must be positive")
        if self.calibration_runs <= 0 or self.evaluation_runs <= 0:
            raise ValueError("run counts must be positive")


@dataclass(frozen=True)
class RunSummary:
    """Machine-readable summary of one full experiment execution."""

    experiment: str
    status: str
    config: dict[str, Any]
    calibrated_alarm_threshold_upper_bound: float
    nominal_false_alarm_runs: int
    nominal_evaluation_runs: int
    nominal_run_false_alarm_rate: float
    coupling_detection_runs: int
    coupling_evaluation_runs: int
    coupling_detection_rate: float
    median_detection_sample: float
    median_detection_lead_samples: float
    lead_samples_p10: float
    lead_samples_p90: float
    representative_detection_sample: int | None
    representative_first_A2: int | None
    representative_first_A1: int | None
    representative_first_A0: int | None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def rolling_pearson(a: np.ndarray, b: np.ndarray, window: int) -> np.ndarray:
    """Return rolling Pearson correlation with NaN before the first full window."""
    if a.ndim != 1 or b.ndim != 1:
        raise ValueError("a and b must be one-dimensional")
    if len(a) != len(b):
        raise ValueError("a and b must have equal length")
    if not 3 < window <= len(a):
        raise ValueError("window must be > 3 and <= series length")

    n = len(a)
    out = np.full(n, np.nan, dtype=float)
    ca = np.concatenate(([0.0], np.cumsum(a, dtype=float)))
    cb = np.concatenate(([0.0], np.cumsum(b, dtype=float)))
    ca2 = np.concatenate(([0.0], np.cumsum(a * a, dtype=float)))
    cb2 = np.concatenate(([0.0], np.cumsum(b * b, dtype=float)))
    cab = np.concatenate(([0.0], np.cumsum(a * b, dtype=float)))

    for t in range(window - 1, n):
        start, stop = t - window + 1, t + 1
        sa, sb = ca[stop] - ca[start], cb[stop] - cb[start]
        saa, sbb = ca2[stop] - ca2[start], cb2[stop] - cb2[start]
        sab = cab[stop] - cab[start]
        covariance = sab - sa * sb / window
        variance_a = saa - sa * sa / window
        variance_b = sbb - sb * sb / window
        denominator = np.sqrt(max(variance_a * variance_b, 1e-12))
        out[t] = covariance / denominator
    return out


def fisher_upper_bound_abs_r(
    correlation: np.ndarray,
    window: int,
    alpha_one_sided: float,
) -> np.ndarray:
    """Return a one-sided Fisher-z upper confidence bound on |correlation|."""
    if not 0.0 < alpha_one_sided < 0.5:
        raise ValueError("alpha_one_sided must be in (0, 0.5)")
    z_critical = NormalDist().inv_cdf(1.0 - alpha_one_sided)
    magnitude = np.clip(np.abs(correlation), 0.0, 0.999999)
    return np.tanh(np.arctanh(magnitude) + z_critical / np.sqrt(window - 3))


def simulate(
    seed: int,
    config: ExperimentConfig,
    *,
    coupling: bool,
) -> dict[str, np.ndarray]:
    """Generate a synthetic two-channel run and its monitored statistics."""
    config.validate()
    rng = np.random.default_rng(seed)
    n = config.n_samples

    environment = np.zeros(n)
    latent_common = np.zeros(n)
    for t in range(1, n):
        environment[t] = 0.92 * environment[t - 1] + rng.normal(0.0, 0.35)
        latent_common[t] = 0.75 * latent_common[t - 1] + rng.normal(0.0, 0.50)
    environment += 0.70 * np.sin(np.arange(n) / 45.0)

    coupling_gain = np.zeros(n)
    if coupling:
        start, stop = config.coupling_onset, config.behavioral_symptom
        coupling_gain[start:stop] = np.linspace(
            0.0,
            config.coupling_max,
            stop - start,
            endpoint=False,
        )
        coupling_gain[stop:] = config.coupling_max

    channel_1 = (
        0.90 * environment
        + rng.normal(0.0, 0.75, n)
        + coupling_gain * latent_common
    )
    channel_2 = (
        -0.50 * environment
        + rng.normal(0.0, 0.75, n)
        + coupling_gain * latent_common
    )

    c = config.commissioning_end
    design = np.column_stack((np.ones(c), environment[:c]))
    beta_1 = np.linalg.lstsq(design, channel_1[:c], rcond=None)[0]
    beta_2 = np.linalg.lstsq(design, channel_2[:c], rcond=None)[0]
    residual_1 = channel_1 - (beta_1[0] + beta_1[1] * environment)
    residual_2 = channel_2 - (beta_2[0] + beta_2[1] * environment)

    raw_corr = rolling_pearson(channel_1, channel_2, config.rolling_window)
    residual_corr = rolling_pearson(residual_1, residual_2, config.rolling_window)
    upper_bound = fisher_upper_bound_abs_r(
        residual_corr,
        config.rolling_window,
        config.alpha_one_sided,
    )

    return {
        "environment": environment,
        "latent_common": latent_common,
        "coupling_gain": coupling_gain,
        "channel_1": channel_1,
        "channel_2": channel_2,
        "raw_corr": raw_corr,
        "residual_corr": residual_corr,
        "upper_bound": upper_bound,
    }


def first_sustained_crossing(
    values: np.ndarray,
    threshold: float,
    *,
    start: int,
    run_length: int,
) -> int | None:
    """Return the first index starting a sustained threshold crossing."""
    if run_length <= 0:
        raise ValueError("run_length must be positive")
    count = 0
    for t in range(start, len(values)):
        if np.isfinite(values[t]) and values[t] > threshold:
            count += 1
            if count >= run_length:
                return t - run_length + 1
        else:
            count = 0
    return None


def illustrative_authority_level(upper_bound: float) -> str:
    """Map the overlap proxy to an illustrative A3-A0 state.

    These thresholds are demonstration parameters, not certified control law.
    """
    if not np.isfinite(upper_bound):
        return "A3"
    if upper_bound >= 0.70:
        return "A0"
    if upper_bound >= 0.55:
        return "A1"
    if upper_bound >= 0.35:
        return "A2"
    return "A3"


def run_monte_carlo(config: ExperimentConfig) -> tuple[RunSummary, dict[str, np.ndarray], list[str]]:
    """Calibrate, evaluate, and return the summary and representative trace."""
    config.validate()

    nominal_maxima: list[float] = []
    for seed in range(1000, 1000 + config.calibration_runs):
        data = simulate(seed, config, coupling=False)
        nominal_maxima.append(
            float(np.nanmax(data["upper_bound"][config.commissioning_end :]))
        )
    threshold = float(np.percentile(nominal_maxima, 95))

    false_alarm_count = 0
    for seed in range(3000, 3000 + config.evaluation_runs):
        data = simulate(seed, config, coupling=False)
        hit = first_sustained_crossing(
            data["upper_bound"],
            threshold,
            start=config.commissioning_end,
            run_length=config.consecutive_alarm_samples,
        )
        false_alarm_count += hit is not None

    detections: list[int] = []
    for seed in range(5000, 5000 + config.evaluation_runs):
        data = simulate(seed, config, coupling=True)
        hit = first_sustained_crossing(
            data["upper_bound"],
            threshold,
            start=config.coupling_onset,
            run_length=config.consecutive_alarm_samples,
        )
        if hit is not None:
            detections.append(hit)

    if not detections:
        raise RuntimeError("No coupling detections; summary percentiles are undefined")

    leads = [config.behavioral_symptom - detection for detection in detections]
    representative = simulate(config.representative_seed, config, coupling=True)
    representative_detection = first_sustained_crossing(
        representative["upper_bound"],
        threshold,
        start=config.coupling_onset,
        run_length=config.consecutive_alarm_samples,
    )
    levels = [illustrative_authority_level(value) for value in representative["upper_bound"]]

    summary = RunSummary(
        experiment="CERBERUS Vigil synthetic independence-decay experiment",
        status="implemented explanatory prototype; not flight validation",
        config=asdict(config),
        calibrated_alarm_threshold_upper_bound=threshold,
        nominal_false_alarm_runs=false_alarm_count,
        nominal_evaluation_runs=config.evaluation_runs,
        nominal_run_false_alarm_rate=false_alarm_count / config.evaluation_runs,
        coupling_detection_runs=len(detections),
        coupling_evaluation_runs=config.evaluation_runs,
        coupling_detection_rate=len(detections) / config.evaluation_runs,
        median_detection_sample=float(np.median(detections)),
        median_detection_lead_samples=float(np.median(leads)),
        lead_samples_p10=float(np.percentile(leads, 10)),
        lead_samples_p90=float(np.percentile(leads, 90)),
        representative_detection_sample=representative_detection,
        representative_first_A2=next((i for i, value in enumerate(levels) if value == "A2"), None),
        representative_first_A1=next((i for i, value in enumerate(levels) if value == "A1"), None),
        representative_first_A0=next((i for i, value in enumerate(levels) if value == "A0"), None),
    )
    return summary, representative, levels
