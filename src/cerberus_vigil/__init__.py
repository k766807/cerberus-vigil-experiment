"""CERBERUS Vigil synthetic experiment package."""

from .core import (
    ExperimentConfig,
    RunSummary,
    first_sustained_crossing,
    illustrative_authority_level,
    rolling_pearson,
    run_monte_carlo,
    simulate,
)

__all__ = [
    "ExperimentConfig",
    "RunSummary",
    "first_sustained_crossing",
    "illustrative_authority_level",
    "rolling_pearson",
    "run_monte_carlo",
    "simulate",
]
