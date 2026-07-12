# CERBERUS Stress Suite v1 Research Plan

**Status:** Planning only; no new detector or robustness result is claimed.  
**Baseline:** Existing fixed-seed matched-model Vigil experiment  
**Parent architecture:** [CERBERUS Runtime Assurance](https://github.com/emilyecht/cerberus-runtime-assurance)

## Purpose

Stress Suite v1 will test how the current Vigil evidence-to-authority pipeline behaves when the detector no longer matches the data generator, telemetry is degraded, and benign operational changes can resemble harmful shared coupling.

The current repository establishes matched-model pipeline correctness and fixed-seed reproducibility. Stress Suite v1 is the next scientific stage: a synthetic robustness map with predeclared claim boundaries, identical seed partitions across detectors, and visible failure regions.

It will not establish spacecraft performance, causal discovery, flight readiness, or robustness outside the published generators.

## Baseline regression target

The existing experiment must remain unchanged and reproducible:

| Metric | Baseline |
|---|---:|
| Calibrated threshold | `0.45832639152918053` |
| Rounded threshold | `0.458326` |
| Nominal sustained-alarm runs | `0 / 200` |
| Coupling detections | `200 / 200` |
| Median detection sample | `1061.5` |
| Median lead before symptom | `238.5 samples` |
| 10th–90th percentile lead | `160.9–319.6 samples` |
| Representative detection | `984` |

Stress Suite work must not overwrite or reinterpret this matched-model result.

## Research question

How does Vigil behave under model mismatch, telemetry degradation, benign confounding, and compound faults while preserving the rule that ambiguous or invalid evidence cannot create authority?

## Seed and protocol discipline

Use three strictly separated partitions:

### 1. Calibration partition

- calibrates each detector to a common nominal run-level alarm budget;
- never supplies final reported performance.

### 2. Development partition

- supports generator debugging;
- supports exploratory severity selection;
- supports detector-specific implementation debugging;
- remains labeled exploratory.

### 3. Frozen confirmatory partition

- generated and hashed before final evaluation;
- used only after detectors, thresholds, metrics, and reporting rules are frozen;
- never used for tuning without declaring a new protocol version.

Every detector receives identical generated runs and seed assignments for paired comparison.

## Scenario matrix

### A. Missing and damaged telemetry

- independent random dropout;
- burst dropout;
- stale-value hold;
- duplicated samples;
- reordered samples;
- channel-specific missingness;
- missing environmental covariates.

### B. Time-base faults

- timestamp jitter;
- linear clock drift;
- step clock offset;
- variable latency;
- channel misalignment.

### C. Noise-model mismatch

- variance ramps;
- heteroskedastic noise;
- heavy-tailed noise;
- isolated outliers;
- autocorrelated residual noise;
- asymmetric noise;
- quantization and clipping.

### D. Environmental-model mismatch

- nonlinear environmental response;
- biased environmental sensor;
- delayed environmental sensor;
- degrading environmental sensor;
- omitted benign common stimulus;
- changing environmental coupling coefficient.

### E. Operational transients

- maneuver-like common transient;
- commissioning-to-operations regime change;
- benign maintenance or calibration step;
- short high-energy disturbance;
- recovery transient.

### F. Harmful coupling forms

- abrupt step coupling;
- gradual ramp coupling;
- intermittent coupling;
- low-and-slow coupling;
- oscillatory coupling;
- sign-changing coupling;
- coupling active only under a particular environmental condition.

### G. Selected compound cases

- missingness plus gradual coupling;
- clock drift plus benign common stimulus;
- degraded environmental sensor plus harmful coupling;
- maneuver transient plus heavy-tailed noise;
- intermittent coupling plus burst dropout.

## Severity levels

Use normalized severity labels:

- `S0` — clean baseline;
- `S1` — mild;
- `S2` — moderate;
- `S3` — severe;
- `S4` — evidence invalid or effectively non-estimable.

Each scenario definition must record:

- generator parameters;
- physical interpretation;
- expected ambiguity;
- whether the conservative target behavior is alarm, no alarm, or unknown.

## Detector comparison set

### Core v1 detectors

1. Current conditioned residual Pearson correlation with Fisher upper bound and persistence.
2. Conditioned residual Spearman rank correlation.
3. CUSUM on a frozen residual-dependence statistic.
4. Page–Hinkley on the same frozen statistic.
5. A simple conservative ensemble.

### Ensemble constraint

The ensemble may contract authority on adverse evidence. Agreement among detectors may not itself promote authority. The v1 rule should remain simple and auditable, such as maximum normalized adverse score or a fixed `k-of-n` alarm rule.

### Optional stretch comparator

Bayesian online changepoint detection may be evaluated later as a research comparator. It is not load-bearing for v1.

## Experimental scale

### Screening stage

- approximately 100 runs per detector/scenario/severity cell;
- broad matrix;
- development seeds only;
- identifies boundary cells and pathological cases.

### Confirmatory stage

Approximately 1,000 runs for the most important cells:

- clean nominal behavior;
- minimum designated harmful-coupling severity;
- selected false-positive challenges;
- selected decision-boundary cells;
- selected compound faults.

The exact count may change before protocol freeze, but the confirmatory manifest must be committed before evaluation.

## Metrics

### Detection metrics

- run-level detection rate;
- run-level false-alarm rate;
- exact confidence intervals;
- detection sample;
- detection lead before the defined symptom;
- minimum detectable coupling severity;
- missed-detection count.

### Evidence-quality metrics

- confidence-bound calibration;
- fraction of invalid or unknown evidence;
- time from evidence degradation to unknown state;
- sensitivity to window length;
- sensitivity to threshold calibration.

### Authority metrics

- first transition to A2, A1, and A0;
- fraction of time at A3, A2, A1, and A0;
- transitions per 1,000 samples;
- reversal count;
- demotion latency;
- recovery latency;
- prolonged-A0 duration;
- promotions while evidence is invalid, which must always equal zero.

### Reproducibility metrics

- runtime per run;
- peak memory;
- deterministic output hash;
- artifact size;
- exact agreement between machine-readable and rendered summaries.

## Hard invariants

These are pass/fail requirements independent of detector accuracy:

- invalid, stale, inconsistent, or non-estimable evidence never increases authority;
- worsening evidence never causes promotion;
- detector tuning never uses confirmatory seeds;
- all reported tables regenerate from committed machine-readable outputs;
- identical seeds and configuration produce identical summaries;
- negative results and failure regions remain visible;
- the original matched-model reproduction remains unchanged.

## Performance gates

Numeric gates should be selected after exploratory screening but before confirmatory evaluation. The protocol should predeclare:

- maximum acceptable nominal sustained-alarm rate;
- minimum detection rate at the designated harmful-coupling severity;
- minimum median lead before the defined symptom;
- maximum authority-transition rate;
- maximum recovery latency after a benign transient;
- maximum prolonged-A0 rate under benign ambiguity.

Changing a gate after viewing confirmatory results requires a new protocol version.

## Proposed repository structure

```text
docs/stress-suite-v1/
  protocol.md
  threat-model.md
  scenario-catalog.md
  detector-specifications.md
  acceptance-criteria.md
  evidence-boundary.md

configs/stress-suite-v1/
  baseline.yaml
  scenarios/
  detectors/
  confirmatory-manifest.yaml

src/cerberus_vigil/stress/
  faults.py
  scenarios.py
  timing.py
  detectors.py
  ensemble.py
  metrics.py
  protocol.py

tests/stress/
  test_fault_generators.py
  test_detector_invariants.py
  test_authority_invariants.py
  test_seed_partitions.py
  test_protocol_freeze.py

results/stress-suite-v1/
  screening-summary.json
  confirmatory-summary.json
  cell-results.csv
  authority-results.csv
  failure-gallery/
```

## Proposed issue sequence

1. **SS-01 — Freeze protocol, seed partitions, and claim boundary**
2. **SS-02 — Specify the fault and mismatch generator schema**
3. **SS-03 — Define detector interfaces and equal-false-alarm calibration**
4. **SS-04 — Define authority and evidence-quality metrics**
5. **SS-05 — Build hand-checkable generator fixtures**
6. **SS-06 — Run exploratory screening matrix**
7. **SS-07 — Freeze confirmatory manifest and acceptance criteria**
8. **SS-08 — Run held-out confirmatory evaluation**
9. **SS-09 — Publish robustness map, failure gallery, and non-claims**

## Exit criteria

Stress Suite v1 is complete only when:

- the baseline reproduction still passes;
- every scenario is defined by a versioned configuration;
- all detectors use identical seed partitions;
- confirmatory thresholds and gates were frozen before evaluation;
- machine-readable and human-readable reports agree;
- failure regions are documented rather than hidden;
- authority never promotes on invalid evidence;
- the release claim remains **synthetic robustness mapping**, not operational validation.
