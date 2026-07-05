#!/usr/bin/env python3
"""Plot paper-vs-local placeholder comparisons for RedCap BWP/SDT validation."""

from __future__ import annotations

import csv
import os
from pathlib import Path

MPLCONFIGDIR = Path("/tmp/redcap_bwp_sdt_mplconfig")
MPLCONFIGDIR.mkdir(parents=True, exist_ok=True)
os.environ.setdefault("MPLCONFIGDIR", str(MPLCONFIGDIR))

import matplotlib
import numpy as np

matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
RESULT_DIR = ROOT / "exp_result"
PICTURE_DIR = ROOT / "exp_pictture"


def _to_float(value: str) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return np.nan


def load_rows(csv_path: Path) -> list[dict]:
    with csv_path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def plot_csv(csv_name: str, output_name: str, title: str) -> None:
    all_rows = load_rows(RESULT_DIR / csv_name)
    paper_rows = [row for row in all_rows if not np.isnan(_to_float(row["paper_value"]))]
    rows = paper_rows if paper_rows else all_rows
    scenarios = [row["scenario"] for row in rows]
    metrics = [row["metric"] for row in rows]
    labels = metrics if len(set(scenarios)) == 1 else [f"{scenario}\n{metric}" for scenario, metric in zip(scenarios, metrics)]
    paper = [_to_float(row["paper_value"]) for row in rows]
    local = [_to_float(row["local_value"]) for row in rows]

    x_axis = np.arange(len(labels))
    plt.figure(figsize=(12, 6))
    plt.plot(x_axis, paper, label="paper curve", color="blue", linewidth=2, marker="o")
    plt.plot(x_axis, local, label="local curve", color="red", linestyle="--", linewidth=2, marker="s")
    if np.isnan(paper).all() and np.isnan(local).all():
        plt.text(
            0.5,
            0.5,
            "TBD values pending paper digitization and local RFsim metrics",
            transform=plt.gca().transAxes,
            ha="center",
            va="center",
        )
    elif not np.isnan(paper).all() and np.isnan(local).all():
        plt.text(
            0.5,
            0.92,
            "local paper-comparable values are TBD",
            transform=plt.gca().transAxes,
            ha="center",
            va="center",
        )

    plt.legend()
    plt.title(title)
    plt.xlabel("Scenario / metric")
    plt.ylabel("Metric value")
    plt.xticks(x_axis, labels, rotation=45, ha="right")
    plt.grid(True, linestyle=":")
    plt.tight_layout()
    PICTURE_DIR.mkdir(parents=True, exist_ok=True)
    plt.savefig(PICTURE_DIR / output_name, dpi=160)
    plt.close()


def main() -> int:
    plot_csv("BWP_results.csv", "BWP_paper_vs_local.png", "BWP Paper vs Local Comparison")
    plot_csv("SDT_results.csv", "SDT_paper_vs_local.png", "SDT Paper vs Local Comparison")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
