"""Output helpers for the CERBERUS Vigil experiment."""
from __future__ import annotations

import csv
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from .core import ExperimentConfig, RunSummary


def write_outputs(
    out_dir: Path,
    config: ExperimentConfig,
    summary: RunSummary,
    representative: dict[str, np.ndarray],
    levels: list[str],
) -> None:
    """Write machine-readable results, trace CSV, and review figures."""
    out_dir.mkdir(parents=True, exist_ok=True)
    summary_dict = summary.to_dict()
    (out_dir / "summary.json").write_text(
        json.dumps(summary_dict, indent=2) + "\n",
        encoding="utf-8",
    )

    with (out_dir / "monte_carlo_results.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["metric", "value"])
        for key, value in summary_dict.items():
            if key != "config":
                writer.writerow([key, value])

    threshold = summary.calibrated_alarm_threshold_upper_bound
    with (out_dir / "representative_trace.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow([
            "sample", "environment", "coupling_gain", "channel_1", "channel_2",
            "raw_corr", "conditioned_residual_corr", "upper_bound_abs_corr",
            "alarm_threshold", "authority_level",
        ])
        for i in range(config.n_samples):
            writer.writerow([
                i,
                representative["environment"][i],
                representative["coupling_gain"][i],
                representative["channel_1"][i],
                representative["channel_2"][i],
                representative["raw_corr"][i],
                representative["residual_corr"][i],
                representative["upper_bound"][i],
                threshold,
                levels[i],
            ])

    _write_png(out_dir / "vigil_independence_decay.png", config, summary, representative, levels)
    _write_compact_svg(out_dir / "vigil_independence_decay.svg", config, summary, representative, levels)


def _write_png(
    path: Path,
    config: ExperimentConfig,
    summary: RunSummary,
    representative: dict[str, np.ndarray],
    levels: list[str],
) -> None:
    x = np.arange(config.n_samples)
    level_number = {"A3": 3, "A2": 2, "A1": 1, "A0": 0}
    figure, axes = plt.subplots(3, 1, figsize=(11, 9), sharex=True)

    axes[0].plot(x, representative["raw_corr"], label="Raw channel correlation")
    axes[0].plot(x, representative["residual_corr"], label="Conditioned residual correlation")
    axes[0].axvline(config.coupling_onset, linestyle="--", label="Hidden coupling begins")
    axes[0].set_ylabel("Rolling correlation")
    axes[0].legend(loc="upper left")
    axes[0].grid(alpha=0.25)

    axes[1].plot(x, representative["upper_bound"], label="95% upper bound on |residual r|")
    axes[1].axhline(summary.calibrated_alarm_threshold_upper_bound, linestyle="--", label="Calibrated alarm threshold")
    axes[1].axvline(config.behavioral_symptom, linestyle=":", label="Behavioral symptom time")
    if summary.representative_detection_sample is not None:
        axes[1].axvline(summary.representative_detection_sample, linestyle="-.", label="Vigil detection")
    axes[1].set_ylabel("Conservative overlap proxy")
    axes[1].legend(loc="upper left")
    axes[1].grid(alpha=0.25)

    axes[2].step(x, [level_number[value] for value in levels], where="post")
    axes[2].set_yticks([0, 1, 2, 3], ["A0", "A1", "A2", "A3"])
    axes[2].set_ylabel("Illustrative authority")
    axes[2].set_xlabel("Sample")
    axes[2].grid(alpha=0.25)

    figure.suptitle("CERBERUS Vigil: Synthetic Independence Decay")
    figure.tight_layout()
    figure.savefig(path, dpi=180)
    plt.close(figure)


def _write_compact_svg(
    path: Path,
    config: ExperimentConfig,
    summary: RunSummary,
    representative: dict[str, np.ndarray],
    levels: list[str],
) -> None:
    """Write a small deterministic SVG suitable for GitHub rendering."""
    width, height = 1000, 700
    left, right = 75, 25
    plot_width = width - left - right
    panels = [(70, 190), (285, 190), (505, 130)]
    x_index = np.linspace(0, config.n_samples - 1, 240).astype(int)

    def x_px(index: int | float) -> float:
        return left + float(index) / (config.n_samples - 1) * plot_width

    def polyline(values: np.ndarray, top: float, panel_height: float, lo: float, hi: float) -> str:
        points: list[str] = []
        for index in x_index:
            value = values[index]
            if not np.isfinite(value):
                continue
            y = top + panel_height - (float(value) - lo) / (hi - lo) * panel_height
            points.append(f"{x_px(int(index)):.1f},{y:.1f}")
        return " ".join(points)

    raw_points = polyline(representative["raw_corr"], panels[0][0], panels[0][1], -1.0, 1.0)
    residual_points = polyline(representative["residual_corr"], panels[0][0], panels[0][1], -1.0, 1.0)
    upper_points = polyline(representative["upper_bound"], panels[1][0], panels[1][1], 0.0, 1.0)
    authority_numbers = np.asarray([{"A0": 0, "A1": 1, "A2": 2, "A3": 3}[value] for value in levels])
    authority_points = polyline(authority_numbers, panels[2][0], panels[2][1], 0.0, 3.0)

    coupling_x = x_px(config.coupling_onset)
    symptom_x = x_px(config.behavioral_symptom)
    threshold_y = panels[1][0] + panels[1][1] - summary.calibrated_alarm_threshold_upper_bound * panels[1][1]
    detection_line = ""
    if summary.representative_detection_sample is not None:
        detection_x = x_px(summary.representative_detection_sample)
        detection_line = (
            f'<line x1="{detection_x:.1f}" y1="{panels[1][0]}" '
            f'x2="{detection_x:.1f}" y2="{panels[1][0] + panels[1][1]}" class="detection"/>'
        )

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">
<title id="title">CERBERUS Vigil synthetic independence decay</title>
<desc id="desc">Three panels show raw and conditioned correlation, the conservative residual-correlation upper bound, and illustrative authority contraction.</desc>
<style>
  .bg {{ fill: #fff; }} .axis {{ stroke: #333; stroke-width: 1; }} .grid {{ stroke: #ddd; stroke-width: 1; }}
  .raw {{ fill: none; stroke: #777; stroke-width: 2; }} .residual {{ fill: none; stroke: #1f5f99; stroke-width: 2; }}
  .upper {{ fill: none; stroke: #8b1a1a; stroke-width: 2; }} .authority {{ fill: none; stroke: #333; stroke-width: 2.5; }}
  .event {{ stroke: #777; stroke-width: 1.5; stroke-dasharray: 7 5; }} .symptom {{ stroke: #555; stroke-width: 1.5; stroke-dasharray: 2 5; }}
  .detection {{ stroke: #8b1a1a; stroke-width: 1.5; stroke-dasharray: 8 3 2 3; }} .threshold {{ stroke: #8b1a1a; stroke-width: 1.5; stroke-dasharray: 7 5; }}
  text {{ font-family: system-ui, sans-serif; fill: #222; }} .small {{ font-size: 13px; }} .label {{ font-size: 15px; font-weight: 600; }}
</style>
<rect class="bg" width="100%" height="100%"/>
<text x="{width/2}" y="32" text-anchor="middle" font-size="22" font-weight="700">CERBERUS Vigil: Synthetic Independence Decay</text>
<text x="{width/2}" y="53" text-anchor="middle" class="small">Fixed representative seed {config.representative_seed}; illustrative research prototype</text>
<text x="{left}" y="64" class="label">Conditioning removes measured environment correlation</text>
<line x1="{left}" y1="{panels[0][0]}" x2="{left}" y2="{panels[0][0]+panels[0][1]}" class="axis"/>
<line x1="{left}" y1="{panels[0][0]+panels[0][1]/2}" x2="{width-right}" y2="{panels[0][0]+panels[0][1]/2}" class="grid"/>
<line x1="{left}" y1="{panels[0][0]+panels[0][1]}" x2="{width-right}" y2="{panels[0][0]+panels[0][1]}" class="axis"/>
<polyline points="{raw_points}" class="raw"/><polyline points="{residual_points}" class="residual"/>
<line x1="{coupling_x:.1f}" y1="{panels[0][0]}" x2="{coupling_x:.1f}" y2="{panels[0][0]+panels[0][1]}" class="event"/>
<text x="{left}" y="{panels[1][0]-10}" class="label">Conservative residual-dependence bound and detection</text>
<line x1="{left}" y1="{panels[1][0]}" x2="{left}" y2="{panels[1][0]+panels[1][1]}" class="axis"/>
<line x1="{left}" y1="{panels[1][0]+panels[1][1]}" x2="{width-right}" y2="{panels[1][0]+panels[1][1]}" class="axis"/>
<polyline points="{upper_points}" class="upper"/>
<line x1="{left}" y1="{threshold_y:.1f}" x2="{width-right}" y2="{threshold_y:.1f}" class="threshold"/>
<line x1="{symptom_x:.1f}" y1="{panels[1][0]}" x2="{symptom_x:.1f}" y2="{panels[1][0]+panels[1][1]}" class="symptom"/>{detection_line}
<text x="{left}" y="{panels[2][0]-10}" class="label">Illustrative monotonic authority contraction</text>
<line x1="{left}" y1="{panels[2][0]}" x2="{left}" y2="{panels[2][0]+panels[2][1]}" class="axis"/>
<line x1="{left}" y1="{panels[2][0]+panels[2][1]}" x2="{width-right}" y2="{panels[2][0]+panels[2][1]}" class="axis"/>
<polyline points="{authority_points}" class="authority"/>
<text x="{left-12}" y="{panels[2][0]+5}" text-anchor="end" class="small">A3</text><text x="{left-12}" y="{panels[2][0]+panels[2][1]+5}" text-anchor="end" class="small">A0</text>
<text x="{coupling_x:.1f}" y="{height-30}" text-anchor="middle" class="small">coupling begins</text>
<text x="{symptom_x:.1f}" y="{height-12}" text-anchor="middle" class="small">chosen symptom time</text>
<text x="{width-right}" y="{height-12}" text-anchor="end" class="small">sample</text>
</svg>"""
    path.write_text(svg, encoding="utf-8")
