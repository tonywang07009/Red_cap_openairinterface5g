#!/usr/bin/env python3
"""Plot PAPER-07 QAM-observed retest results."""

from __future__ import annotations

import csv
from pathlib import Path


SCRIPT_PATH = Path(__file__).resolve()
PROJECT_DIR = SCRIPT_PATH.parents[2]
IN_CSV = PROJECT_DIR / "analysis" / "data" / "paper07_qam_observed_retest.csv"
PLOT_DIR = PROJECT_DIR / "analysis" / "plots"
REPORT = PROJECT_DIR / "analysis" / "paper07_qam_observed_retest_report.md"


def read_rows() -> list[dict[str, str]]:
    with IN_CSV.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def plot(rows: list[dict[str, str]]) -> None:
    import matplotlib.pyplot as plt

    PLOT_DIR.mkdir(parents=True, exist_ok=True)
    labels = [row["paper_qam_point"] for row in rows]
    x = list(range(len(labels)))
    width = 0.34

    paper = [float(row["paper_pdcp_ul_mbps"]) for row in rows]
    measured = [float(row["receiver_mbps"]) for row in rows]
    expected_qm = [float(row["expected_qm"]) for row in rows]
    observed_qm = [float(row["observed_qm"]) for row in rows]

    fig, axes = plt.subplots(2, 1, figsize=(8.6, 7.0), sharex=True)

    axes[0].bar([i - width / 2 for i in x], paper, width, label="PAPER-07 PDCP UL target", color="#3b6ea8")
    axes[0].bar([i + width / 2 for i in x], measured, width, label="RFsim receiver throughput", color="#d9853b")
    axes[0].set_ylabel("UL throughput (Mbps)")
    axes[0].set_title("PAPER-07 QAM-Distinguished UL Retest")
    axes[0].grid(axis="y", alpha=0.25)
    axes[0].legend(loc="upper left")

    for i, value in enumerate(paper):
        axes[0].text(i - width / 2, value + 0.5, f"{value:.1f}", ha="center", va="bottom", fontsize=9)
    for i, value in enumerate(measured):
        axes[0].text(i + width / 2, value + 0.5, f"{value:.1f}", ha="center", va="bottom", fontsize=9)

    axes[1].plot(x, expected_qm, marker="o", linewidth=2.0, label="Expected Qm from paper point", color="#3b6ea8")
    axes[1].plot(x, observed_qm, marker="s", linewidth=2.0, label="Observed gNB ULSCH Qm", color="#bf4c41")
    axes[1].set_xticks(x)
    axes[1].set_xticklabels(labels)
    axes[1].set_xlabel("PAPER-07 modulation point")
    axes[1].set_ylabel("Qm")
    axes[1].set_yticks([2, 4, 6, 8])
    axes[1].set_ylim(1.5, 8.5)
    axes[1].grid(axis="y", alpha=0.25)
    axes[1].legend(loc="upper left")

    for i, value in enumerate(observed_qm):
        axes[1].text(i, value + 0.15, f"observed {value:.0f}", ha="center", va="bottom", fontsize=9)

    fig.tight_layout()
    fig.savefig(PLOT_DIR / "paper07_qam_observed_retest.png", dpi=180)
    fig.savefig(PLOT_DIR / "paper07_qam_observed_retest.pdf")
    plt.close(fig)


def write_report(rows: list[dict[str, str]]) -> None:
    lines = [
        "# PAPER-07 QAM-Observed UL Retest",
        "",
        "## Status",
        "- [Completed]",
        "- Paper: `evaluation_paper/Research_on_5G_RedCap_Standard_and_Key_Technologies.pdf`",
        "- Paper evidence: PDF page 4, Table IV, RedCap uplink peak-rate test.",
        "- Retest goal: distinguish actual [64QAM] versus [256QAM] using gNB MAC stats, not only offered UDP rate.",
        "",
        "## Measurement Method",
        "- Reused the active healthy RFsim containers.",
        "- UE: `rfsim5g-oai-nr-ue1_redcap`, source IP `10.0.0.2`.",
        "- Server: `oai-ext-dn`, target IP `192.168.72.135`.",
        "- Traffic: UDP UL iperf3, 60 seconds per point.",
        "- QAM evidence: sampled `rfsim5g-oai-gnb_redcap:/opt/oai-gnb/nrMAC_stats.log` during iperf.",
        "",
        "## Code Evidence",
        "- `doc/MAC/mac-usage.md`: scheduler stats define `MCS (Q) M`, where `Q=0` is the 64QAM table and `Q=1` is the 256QAM table.",
        "- `doc/MAC/mac-usage.md`: `Qm 6` maps to 64QAM and `Qm 8` maps to 256QAM.",
        "- `openair2/LAYER2/NR_MAC_COMMON/nr_mac_common.c`: `nr_get_Qm_ul()` maps UL MCS table/index to Qm.",
        "- `openair2/LAYER2/NR_MAC_gNB/nr_radio_config.c`: `set_ul_mcs_table()` only selects PUSCH `qam256` when UE capability exposes `pusch_256QAM` support.",
        "",
        "## Result Table",
        "| Run | Paper point | Expected Qm/table | Observed Qm/table/MCS | Receiver Mbps | Jitter ms | UDP Loss % | Verdict |",
        "|---|---|---:|---:|---:|---:|---:|---|",
    ]
    for row in rows:
        lines.append(
            "| {run_id} | {paper_qam_point} | Qm {expected_qm} / table {expected_mcs_table} | Qm {observed_qm} / table {observed_mcs_table} / MCS {observed_mcs_index} | {receiver_mbps} | {jitter_ms} | {udp_loss_percent} | {qam_verdict} |".format(
                **row
            )
        )
    lines.extend(
        [
            "",
            "## Outputs",
            "- CSV: `analysis/data/paper07_qam_observed_retest.csv`",
            "- PNG: `analysis/plots/paper07_qam_observed_retest.png`",
            "- PDF: `analysis/plots/paper07_qam_observed_retest.pdf`",
            "",
            "## Interpretation",
            "- The 26M point matched [64QAM] behavior: gNB reported `MCS (0) 28` and `Qm 6`.",
            "- The 35M point did not match [256QAM] behavior: gNB still reported `MCS (0) 28` and `Qm 6`.",
            "- Therefore the current active RFsim scenario can reproduce PAPER-07 UL target throughput, but it did not exercise true 256QAM uplink.",
            "- To run a true 256QAM retest, the platform needs a clean restart with UE capability/PUSCH configuration enabling `mcs_Table=qam256`, then MAC stats must show `MCS (1)` and `Qm 8` during traffic.",
        ]
    )
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    rows = read_rows()
    plot(rows)
    write_report(rows)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
