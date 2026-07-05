#!/usr/bin/env python3
"""Plot PAPER-07 TDD reproduction results collected on 2026-05-23."""

from __future__ import annotations

import csv
from pathlib import Path


SCRIPT_PATH = Path(__file__).resolve()
PROJECT_DIR = SCRIPT_PATH.parents[2]
IN_CSV = PROJECT_DIR / "analysis" / "data" / "paper07_tdd_reproduction_2026-05-23.csv"
PLOT_DIR = PROJECT_DIR / "analysis" / "plots"


def read_rows() -> list[dict[str, str]]:
    with IN_CSV.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def as_float(value: str, default: float = 0.0) -> float:
    value = value.strip()
    if not value:
        return default
    return float(value)


def plot(rows: list[dict[str, str]]) -> None:
    import matplotlib.pyplot as plt

    PLOT_DIR.mkdir(parents=True, exist_ok=True)

    labels = [row["traffic_direction"] for row in rows]
    x = list(range(len(labels)))
    width = 0.34

    target = [as_float(row["paper_target_mbps"]) for row in rows]
    measured = [as_float(row["receiver_mbps"]) for row in rows]
    jitter = [as_float(row["jitter_ms"]) for row in rows]
    loss = [as_float(row["udp_loss_percent"]) for row in rows]

    fig, axes = plt.subplots(2, 1, figsize=(8.8, 7.0), sharex=True)

    axes[0].bar([i - width / 2 for i in x], target, width, label="PAPER-07 target", color="#3b6ea8")
    axes[0].bar([i + width / 2 for i in x], measured, width, label="RFsim measured", color="#d9853b")
    axes[0].set_ylabel("Throughput (Mbps)")
    axes[0].set_title("PAPER-07 TDD 20MHz 256QAM Reproduction")
    axes[0].grid(axis="y", alpha=0.25)
    axes[0].legend(loc="upper left")

    for i, value in enumerate(measured):
        axes[0].text(i + width / 2, value + 2.0, f"{value:.0f}", ha="center", va="bottom", fontsize=9)

    axes[1].bar([i - width / 2 for i in x], jitter, width, label="Jitter (ms)", color="#4d7f57")
    axes[1].bar([i + width / 2 for i in x], loss, width, label="UDP loss (%)", color="#bf4c41")
    axes[1].set_ylabel("Jitter / loss")
    axes[1].set_xticks(x)
    axes[1].set_xticklabels(labels)
    axes[1].grid(axis="y", alpha=0.25)
    axes[1].legend(loc="upper left")

    fig.tight_layout()
    fig.savefig(PLOT_DIR / "paper07_tdd_reproduction_2026-05-23.png", dpi=180)
    fig.savefig(PLOT_DIR / "paper07_tdd_reproduction_2026-05-23.pdf")
    plt.close(fig)


def main() -> int:
    plot(read_rows())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
