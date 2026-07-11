# Experiment roadmap

## Phase 1 — Baseline reproducibility

- Fixed-seed synthetic environment and hidden-coupling process
- Residual-correlation detector after conditioning
- Independent calibration and evaluation ensembles
- Automated tests and CI reproduction

## Phase 2 — Robustness envelope

- Missing, bursty, delayed, and corrupted telemetry
- Nonstationary noise and maneuver transients
- Degrading environment sensors
- Benign unmodeled common stimuli
- Sensitivity curves across coupling strength and rolling-window size

## Phase 3 — Comparator study

- Raw correlation baseline
- Partial correlation and regression residuals
- Rank-based dependence
- Change-point detectors
- Conditional mutual-information estimators

## Phase 4 — Authority behavior

- Hysteresis and dwell-time analysis
- Chattering metrics
- Conservative unknown handling
- Evidence-expiry and restoration experiments

## Phase 5 — External validity

- Public spacecraft or robotics telemetry surrogate
- Hardware-in-the-loop testbed
- Pre-registered acceptance criteria
- Independent reproduction by an outside contributor

Every phase must preserve the distinction between an explanatory research result and evidence suitable for safety certification.
