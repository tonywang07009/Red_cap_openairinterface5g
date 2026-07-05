#!/usr/bin/env python3
"""Plot PAPER-07 TDD downlink retest results."""

from __future__ import annotations

import csv
from pathlib import Path


SCRIPT_PATH = Path(__file__).resolve()
PROJECT_DIR = SCRIPT_PATH.parents[2]
IN_CSV = PROJECT_DIR / "analysis" / "data" / "paper07_tdd_dl_retest.csv"
PLOT_DIR = PROJECT_DIR / "analysis" / "plots"


def read_rows() -> list[dict[str, str]]:
    with IN_CSV.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def plot(rows: list[dict[str, str]]) -> None:
    import matplotlib.pyplot as plt

    PLOT_DIR.mkdir(parents=True, exist_ok=True)
    labels = [row["run_id"].replace("PAPER07-TDD-DL-", "").replace("-PRE-PDSCH", "\npre").replace("-TRUE-PDSCH256", "\ntrue") for row in rows]
    x = list(range(len(labels)))
    width = 0.34

    target = [float(row["paper_dl_target_mbps"]) for row in rows]
    measured = [float(row["receiver_mbps"]) for row in rows]
    mcs_table = [float(row["observed_dl_mcs_table"]) for row in rows]
    loss = [float(row["udp_loss_percent"]) for row in rows]

    fig, axes = plt.subplots(2, 1, figsize=(9.4, 7.2), sharex=True)

    axes[0].bar([i - width / 2 for i in x], target, width, label="PAPER-07 DL target", color="#3b6ea8")
    axes[0].bar([i + width / 2 for i in x], measured, width, label="RFsim DL receiver throughput", color="#d9853b")
    axes[0].set_ylabel("DL throughput (Mbps)")
    axes[0].set_title("PAPER-07 TDD Downlink Retest")
    axes[0].grid(axis="y", alpha=0.25)
    axes[0].legend(loc="upper left")

    for i, value in enumerate(measured):
        axes[0].text(i + width / 2, value + 2.0, f"{value:.0f}", ha="center", va="bottom", fontsize=9)

    axes[1].plot(x, mcs_table, marker="o", linewidth=2.0, label="Observed DLSCH MCS table", color="#4d7f57")
    axes[1].bar(x, loss, width=0.42, label="UDP loss percent", color="#bf4c41", alpha=0.45)
    axes[1].set_ylabel("MCS table / loss %")
    axes[1].set_xticks(x)
    axes[1].set_xticklabels(labels)
    axes[1].set_ylim(0, 1.2)
    axes[1].grid(axis="y", alpha=0.25)
    axes[1].legend(loc="upper left")

    for i, row in enumerate(rows):
        axes[1].text(i, mcs_table[i] + 0.06, f"MCS({row['observed_dl_mcs_table']}) {row['observed_dl_mcs_index']}", ha="center", va="bottom", fontsize=9)

    fig.tight_layout()
    fig.savefig(PLOT_DIR / "paper07_tdd_dl_retest.png", dpi=180)
    fig.savefig(PLOT_DIR / "paper07_tdd_dl_retest.pdf")
    plt.close(fig)


def main() -> int:
    plot(read_rows())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
