#!/usr/bin/env python3
"""Plot PAPER-07 true 256QAM retest results."""

from __future__ import annotations

import csv
from pathlib import Path


SCRIPT_PATH = Path(__file__).resolve()
PROJECT_DIR = SCRIPT_PATH.parents[2]
IN_CSV = PROJECT_DIR / "analysis" / "data" / "paper07_true_256qam_retest.csv"
PLOT_DIR = PROJECT_DIR / "analysis" / "plots"


def read_rows() -> list[dict[str, str]]:
    with IN_CSV.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def plot(rows: list[dict[str, str]]) -> None:
    import matplotlib.pyplot as plt

    PLOT_DIR.mkdir(parents=True, exist_ok=True)
    labels = [row["qam_point"] for row in rows]
    x = list(range(len(labels)))
    width = 0.34

    paper_pdcp = [float(row["paper_pdcp_ul_mbps"]) for row in rows]
    measured = [float(row["receiver_mbps"]) for row in rows]
    qm = [float(row["observed_qm"]) for row in rows]
    mcs_table = [float(row["observed_mcs_table"]) for row in rows]

    fig, axes = plt.subplots(2, 1, figsize=(8.8, 7.0), sharex=True)

    axes[0].bar([i - width / 2 for i in x], paper_pdcp, width, label="PAPER-07 PDCP UL target", color="#3b6ea8")
    axes[0].bar([i + width / 2 for i in x], measured, width, label="RFsim receiver throughput", color="#d9853b")
    axes[0].set_ylabel("UL throughput (Mbps)")
    axes[0].set_title("PAPER-07 True 256QAM UL Retest")
    axes[0].grid(axis="y", alpha=0.25)
    axes[0].legend(loc="upper left")

    for i, value in enumerate(paper_pdcp):
        axes[0].text(i - width / 2, value + 0.45, f"{value:.1f}", ha="center", va="bottom", fontsize=9)
    for i, value in enumerate(measured):
        axes[0].text(i + width / 2, value + 0.45, f"{value:.1f}", ha="center", va="bottom", fontsize=9)

    axes[1].plot(x, qm, marker="o", linewidth=2.0, label="Observed ULSCH Qm", color="#bf4c41")
    axes[1].plot(x, [value * 2 + 6 for value in mcs_table], marker="s", linewidth=2.0, label="MCS table marker: table0=6, table1=8", color="#4d7f57")
    axes[1].set_xticks(x)
    axes[1].set_xticklabels(labels)
    axes[1].set_xlabel("PAPER-07 modulation point")
    axes[1].set_ylabel("Qm / table marker")
    axes[1].set_yticks([2, 4, 6, 8])
    axes[1].set_ylim(1.5, 8.5)
    axes[1].grid(axis="y", alpha=0.25)
    axes[1].legend(loc="upper left")

    for i, row in enumerate(rows):
        axes[1].text(i, qm[i] + 0.15, f"MCS({row['observed_mcs_table']}) {row['observed_mcs_index']}", ha="center", va="bottom", fontsize=9)

    fig.tight_layout()
    fig.savefig(PLOT_DIR / "paper07_true_256qam_retest.png", dpi=180)
    fig.savefig(PLOT_DIR / "paper07_true_256qam_retest.pdf")
    plt.close(fig)


def main() -> int:
    plot(read_rows())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
