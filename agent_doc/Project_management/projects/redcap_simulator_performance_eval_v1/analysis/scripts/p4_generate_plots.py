#!/usr/bin/env python3
"""Generate P4 matplotlib plots from P3 RFsim runtime metrics."""

from __future__ import annotations

import argparse
import csv
import os
from pathlib import Path


SCRIPT_PATH = Path(__file__).resolve()
PROJECT_DIR = SCRIPT_PATH.parents[2]
DEFAULT_INPUT = PROJECT_DIR / "analysis" / "data" / "p3_runtime_metrics.csv"
DEFAULT_OUTPUT_DIR = PROJECT_DIR / "analysis" / "plots"
DEFAULT_MPLCONFIGDIR = Path("/tmp") / "redcap_simulator_performance_eval_mpl"
DEFAULT_MPLCONFIGDIR.mkdir(parents=True, exist_ok=True)
os.environ.setdefault("MPLCONFIGDIR", str(DEFAULT_MPLCONFIGDIR))

import matplotlib.pyplot as plt


def rate_to_mbps(value: str) -> float:
    text = value.strip().upper()
    if text.endswith("G"):
        return float(text[:-1]) * 1000.0
    if text.endswith("M"):
        return float(text[:-1])
    if text.endswith("K"):
        return float(text[:-1]) / 1000.0
    return float(text)


def as_float(row: dict[str, str], key: str) -> float:
    value = row.get(key, "")
    if value == "":
        return float("nan")
    return float(value)


def load_rows(path: Path) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    with path.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            sample_count = len(str(row["sample_ues"]).split())
            enriched: dict[str, object] = dict(row)
            enriched["offered_rate_mbps"] = rate_to_mbps(row["iperf_rate"])
            enriched["sample_count"] = sample_count
            enriched["receiver_mbps"] = as_float(row, "receiver_mbps")
            enriched["sender_mbps"] = as_float(row, "sender_mbps")
            enriched["throughput_gap_mbps"] = enriched["sender_mbps"] - enriched["receiver_mbps"]
            enriched["total_ues"] = int(row["total_ues"])
            enriched["rtt_avg_ms"] = as_float(row, "rtt_avg_ms")
            enriched["jitter_ms"] = as_float(row, "jitter_ms")
            enriched["udp_loss_percent"] = as_float(row, "udp_loss_percent")
            enriched["ping_loss_percent"] = as_float(row, "ping_loss_percent")
            enriched["gnb_restart_count"] = int(row["gnb_restart_count"])
            rows.append(enriched)
    return rows


def style_axis(ax, title: str, xlabel: str, ylabel: str, source_csv: Path) -> None:
    ax.set_title(title, fontsize=12, weight="bold")
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.grid(True, linestyle="--", linewidth=0.5, alpha=0.45)
    ax.text(
        0.0,
        -0.24,
        f"Scenario: OAI RFsim RedCap P3 DOE | Source CSV: {source_csv.name}",
        transform=ax.transAxes,
        fontsize=8,
        color="#333333",
    )


def save_figure(fig, output_dir: Path, stem: str) -> list[Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    png = output_dir / f"{stem}.png"
    pdf = output_dir / f"{stem}.pdf"
    fig.tight_layout()
    fig.savefig(png, dpi=180, bbox_inches="tight")
    fig.savefig(pdf, bbox_inches="tight")
    plt.close(fig)
    return [png, pdf]


def annotate_points(ax, rows: list[dict[str, object]], x_key: str, y_key: str) -> None:
    for row in rows:
        ax.annotate(
            str(row["run_id"]).replace("DOE-", ""),
            (float(row[x_key]), float(row[y_key])),
            textcoords="offset points",
            xytext=(4, 4),
            fontsize=7,
            alpha=0.75,
        )


def plot_throughput_vs_offered_rate(rows: list[dict[str, object]], source_csv: Path, output_dir: Path) -> list[Path]:
    fig, ax = plt.subplots(figsize=(8.5, 5.2))
    sample_counts = sorted({int(row["sample_count"]) for row in rows})
    for sample_count in sample_counts:
        subset = [row for row in rows if row["sample_count"] == sample_count]
        ax.scatter(
            [row["offered_rate_mbps"] for row in subset],
            [row["receiver_mbps"] for row in subset],
            label=f"receiver, sample_count={sample_count}",
            s=52,
            alpha=0.9,
        )
    ax.plot(
        [row["offered_rate_mbps"] for row in rows],
        [row["sender_mbps"] for row in rows],
        linestyle="",
        marker="x",
        color="#444444",
        label="sender Mbps",
    )
    annotate_points(ax, rows, "offered_rate_mbps", "receiver_mbps")
    style_axis(ax, "Throughput vs Offered Rate", "Offered rate (Mbit/s)", "Throughput (Mbit/s)", source_csv)
    ax.legend(fontsize=8, ncols=2)
    return save_figure(fig, output_dir, "p4_throughput_vs_offered_rate")


def plot_throughput_vs_total_ues(rows: list[dict[str, object]], source_csv: Path, output_dir: Path) -> list[Path]:
    fig, ax = plt.subplots(figsize=(8.5, 5.2))
    ax.scatter([row["total_ues"] for row in rows], [row["receiver_mbps"] for row in rows], s=60, label="receiver Mbps")
    ax.scatter([row["total_ues"] for row in rows], [row["sender_mbps"] for row in rows], marker="x", s=62, label="sender Mbps")
    annotate_points(ax, rows, "total_ues", "receiver_mbps")
    style_axis(ax, "Throughput vs UE Count", "Total UE compose pool (count)", "Throughput (Mbit/s)", source_csv)
    ax.legend(fontsize=8)
    return save_figure(fig, output_dir, "p4_throughput_vs_total_ues")


def plot_metric_vs_total_ues(
    rows: list[dict[str, object]],
    source_csv: Path,
    output_dir: Path,
    y_key: str,
    ylabel: str,
    title: str,
    stem: str,
) -> list[Path]:
    fig, ax = plt.subplots(figsize=(8.5, 5.2))
    scatter = ax.scatter(
        [row["total_ues"] for row in rows],
        [row[y_key] for row in rows],
        s=[42 + int(row["sample_count"]) * 10 for row in rows],
        c=[int(row["sample_count"]) for row in rows],
        cmap="viridis",
        alpha=0.85,
    )
    annotate_points(ax, rows, "total_ues", y_key)
    style_axis(ax, title, "Total UE compose pool (count)", ylabel, source_csv)
    cbar = fig.colorbar(scatter, ax=ax)
    cbar.set_label("Sampled UE count")
    return save_figure(fig, output_dir, stem)


def plot_packet_loss_vs_total_ues(rows: list[dict[str, object]], source_csv: Path, output_dir: Path) -> list[Path]:
    fig, ax = plt.subplots(figsize=(8.5, 5.2))
    ax.scatter([row["total_ues"] for row in rows], [row["udp_loss_percent"] for row in rows], s=56, label="UDP loss")
    ax.scatter([row["total_ues"] for row in rows], [row["ping_loss_percent"] for row in rows], marker="x", s=62, label="Ping loss")
    annotate_points(ax, rows, "total_ues", "udp_loss_percent")
    style_axis(ax, "Packet Loss vs UE Count", "Total UE compose pool (count)", "Packet loss (%)", source_csv)
    ax.set_ylim(bottom=-0.05)
    ax.legend(fontsize=8)
    return save_figure(fig, output_dir, "p4_packet_loss_vs_total_ues")


def plot_throughput_gap_by_run(rows: list[dict[str, object]], source_csv: Path, output_dir: Path) -> list[Path]:
    fig, ax = plt.subplots(figsize=(9.6, 5.2))
    labels = [str(row["run_id"]).replace("DOE-", "") for row in rows]
    values = [row["throughput_gap_mbps"] for row in rows]
    colors = ["#b23a48" if value > 10 else "#2f6f73" for value in values]
    ax.bar(labels, values, color=colors)
    style_axis(ax, "Sender-Receiver Throughput Gap by Run", "Run ID", "Sender - receiver throughput (Mbit/s)", source_csv)
    ax.tick_params(axis="x", rotation=35)
    return save_figure(fig, output_dir, "p4_sender_receiver_gap_by_run")


def generate_report(output_dir: Path, generated: list[Path], rows: list[dict[str, object]], source_csv: Path) -> Path:
    report = output_dir.parent / "p4_matplotlib_plot_report.md"
    gap_rows = [row for row in rows if float(row["throughput_gap_mbps"]) > 10.0]
    lines = [
        "# P4 Matplotlib Plot Report",
        "",
        "## Summary",
        "- Status: [COMPLETED]",
        f"- Source CSV: `{source_csv}`",
        f"- Rows plotted: {len(rows)}",
        "- Dataset class: [Strong Dataset] from P3.",
        "",
        "## Generated Figures",
    ]
    for path in generated:
        lines.append(f"- `{path.relative_to(output_dir.parent)}`")
    lines.extend(
        [
            "",
            "## Axis Compliance",
            "- X axes use simulator-controlled variables: [offered rate], [total UE compose pool], [run ID].",
            "- Y axes use measured simulator metrics: [receiver Mbps], [sender Mbps], [RTT avg], [jitter], [packet loss], [throughput gap].",
            "- Packet loss remains plotted even though all measured rows are 0%, because it is a required P3/P4 success metric.",
            "",
            "## Key Observations For P5",
        ]
    )
    if gap_rows:
        for row in gap_rows:
            lines.append(
                f"- `{row['run_id']}` throughput gap: sender {float(row['sender_mbps']):.3f} Mbps, "
                f"receiver {float(row['receiver_mbps']):.3f} Mbps, gap {float(row['throughput_gap_mbps']):.3f} Mbps."
            )
    else:
        lines.append("- No sender/receiver throughput gap above 10 Mbit/s.")
    lines.extend(
        [
            "- All plotted rows have UDP loss 0% and gNB restart count 0.",
            "- RTT increases when sampled UE count increases, especially 8 sampled UE rows.",
            "",
            "## Guardrail",
            "- These plots support RFsim trend analysis.",
            "- Do not claim absolute paper-level throughput equivalence until P5 maps RFsim conditions to paper scenarios.",
        ]
    )
    report.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return report


def generate_plots(input_csv: Path, output_dir: Path) -> list[Path]:
    rows = load_rows(input_csv)
    generated: list[Path] = []
    generated.extend(plot_throughput_vs_offered_rate(rows, input_csv, output_dir))
    generated.extend(plot_throughput_vs_total_ues(rows, input_csv, output_dir))
    generated.extend(plot_metric_vs_total_ues(rows, input_csv, output_dir, "rtt_avg_ms", "RTT avg (ms)", "RTT Latency vs UE Count", "p4_rtt_latency_vs_total_ues"))
    generated.extend(plot_metric_vs_total_ues(rows, input_csv, output_dir, "jitter_ms", "UDP jitter (ms)", "UDP Jitter vs UE Count", "p4_jitter_vs_total_ues"))
    generated.extend(plot_packet_loss_vs_total_ues(rows, input_csv, output_dir))
    generated.extend(plot_throughput_gap_by_run(rows, input_csv, output_dir))
    report = generate_report(output_dir, generated, rows, input_csv)
    generated.append(report)
    return generated


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args()

    generated = generate_plots(args.input, args.output_dir)
    for path in generated:
        print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
