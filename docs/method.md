# Method and interpretation

## Research question

Can a model-light monitor detect a gradually emerging shared latent pathway between two channels after conditioning out a measured common environment, before a predefined behavioral symptom time?

## Synthetic data-generating process

Two channels receive different linear responses to a measured autocorrelated environment plus independent noise. In coupling runs, a separate latent process is injected into both channels beginning at sample 700. Its gain rises until sample 1300 and remains fixed afterward.

The commissioning model estimates each channel's response to the measured environment using only samples 0-499. Vigil then computes rolling Pearson correlation between the two residual streams using a 120-sample window.

## Conservative statistic

The detector uses a one-sided 95% Fisher-z upper confidence bound on the magnitude of residual correlation. Higher values are treated as weaker evidence of independence. The statistic is a deliberately narrow overlap proxy, not probabilistic FCOI.

## Threshold protocol

1. Calibrate on 100 independent nominal runs.
2. Take the 95th percentile of each run's post-commissioning maximum upper bound.
3. Evaluate on separate ensembles of 200 nominal and 200 coupling runs.
4. Require ten consecutive samples above threshold.

The calibration, nominal evaluation, coupling evaluation, and representative trace use disjoint fixed seed ranges.

## Authority illustration

The A3-A0 mapping is a demonstration of monotonic authority contraction:

| Upper-bound proxy | Illustrative state |
|---:|:---|
| `< 0.35` | A3 |
| `0.35-0.55` | A2 |
| `0.55-0.70` | A1 |
| `>= 0.70` | A0 |

These thresholds are not certified control law and do not establish safe promotion or recovery logic.

## Valid claim

For the supplied synthetic process and fixed protocol, the detector identifies all 200 evaluated coupling runs before the chosen symptom time, while producing no sustained alarms in the 200 evaluated nominal runs.

## Non-claims

This experiment does not establish:

- flight performance or certification;
- probability-calibrated FCOI;
- causal discovery;
- transfer-entropy validity;
- sentinel-injection safety;
- robustness to telemetry loss, drift, nonstationarity, or adversarial inputs;
- safe authority restoration;
- independence from a shared causal ontology.
