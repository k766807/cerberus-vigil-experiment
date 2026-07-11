# CERBERUS Vigil Experiment

> A reproducible synthetic experiment for detecting runtime independence decay before a predefined behavioral symptom.

[![Reproduce experiment](https://github.com/k766807/cerberus-vigil-experiment/actions/workflows/reproduce.yml/badge.svg)](https://github.com/k766807/cerberus-vigil-experiment/actions/workflows/reproduce.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

This repository isolates one implemented experiment from the broader [CERBERUS Runtime Assurance](https://github.com/k766807/cerberus-runtime-assurance) architecture.

CERBERUS treats assurance-layer independence as a perishable runtime quantity. This experiment tests a much narrower proposition: after removing a measured common environmental signal from two synthetic channels, a rising hidden shared pathway can be detected through residual dependence, and a conservative upper bound can trigger illustrative authority contraction.

![Representative fixed-seed result](results/vigil_independence_decay.svg)

## Fixed-seed result

| Metric | Result |
|---|---:|
| Nominal sustained-alarm runs | **0 / 200** |
| Coupling detections | **200 / 200** |
| Median detection sample | **1061.5** |
| Median lead before symptom | **238.5 samples** |
| 10th-90th percentile lead | **160.9-319.6 samples** |
| Representative detection | **sample 984** |

These results describe only the supplied synthetic model and fixed seed protocol. They are not estimates of spacecraft or production performance.

## Run it

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
python -m pip install -e ".[dev]"
pytest
python run_experiment.py
```

Generated outputs are written to `results/`:

- `summary.json` — machine-readable metrics and configuration
- `monte_carlo_results.csv` — compact metric table
- `representative_trace.csv` — generated full representative signal and authority trace
- `vigil_independence_decay.png` — generated review figure

The repository commits the small reference SVG and summary tables; CI regenerates the full outputs as an artifact.

## Experimental protocol

1. Simulate two channels driven by a measured common environment and independent noise.
2. Estimate each channel's environment response during commissioning.
3. Monitor rolling residual correlation after conditioning.
4. Convert `|r|` to a one-sided 95% Fisher upper confidence bound.
5. Calibrate a sustained-alarm threshold on 100 independent nominal runs.
6. Evaluate on separate sets of 200 nominal and 200 coupling runs.
7. Map higher overlap-proxy values to illustrative A3-A0 authority contraction.

The full method, valid claim, and non-claims are in [docs/method.md](docs/method.md).

## Repository layout

```text
src/cerberus_vigil/    simulation, monitor, output code
run_experiment.py      reproducible entry point
tests/                 deterministic and scientific guardrail tests
results/               committed reference outputs
docs/method.md         protocol, interpretation, and non-claims
.github/workflows/     CI reproduction check
```

## Evidence boundary

**Implemented here:** synthetic data generation, commissioning residualization, rolling residual-correlation monitor, Fisher upper bound, fixed-seed calibration/evaluation, illustrative authority contraction, tests, and reproducible outputs.

**Not implemented or validated here:** structural or probabilistic FCOI, transfer entropy, sentinel injection, spacecraft FDIR, hardware-in-the-loop behavior, promotion/recovery safety, and flight certification.

## License

The code and repository documentation are released under the [MIT License](LICENSE), copyright © 2026 Emily Echterhoff.

## Citation

Citation metadata is provided in [`CITATION.cff`](CITATION.cff).
