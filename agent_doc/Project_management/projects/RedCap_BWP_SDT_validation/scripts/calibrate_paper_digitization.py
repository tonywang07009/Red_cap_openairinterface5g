#!/usr/bin/env python3
"""Generate calibrated paper-side digitization anchors from rendered pages."""

from __future__ import annotations

import csv
import math
from dataclasses import dataclass
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
EXP_RESULT = PROJECT_ROOT / "exp_result"
TEMPLATE = EXP_RESULT / "paper_curve_digitization_template.csv"
CALIBRATION = EXP_RESULT / "paper_digitization_calibration.csv"


@dataclass(frozen=True)
class PlotCalibration:
    rendered_page: str
    plot_box: tuple[float, float, float, float]
    x_range: tuple[float, float]
    y_range: tuple[float, float]
    x_scale: str = "linear"


@dataclass(frozen=True)
class Anchor:
    scenario: str
    metric: str
    source_status: str
    note: str
    source_type: str
    calibration: PlotCalibration | None = None
    pixel_point: tuple[float, float] | None = None
    literal_paper_value: float | None = None
    literal_x_value: float | None = None
    output_from_axis: str = "y"
    x_value_from_axis: str = "x"


PLOTS = {
    "bwp_fig5": PlotCalibration(
        "paper_figures/paper1_BWP_switching/page-5.png",
        (139, 668, 534, 969),
        (0, 100),
        (0, 1),
    ),
    "bwp_fig6": PlotCalibration(
        "paper_figures/paper1_BWP_switching/page-5.png",
        (671, 140, 1021, 429),
        (0, 30),
        (0, 1),
    ),
    "bwp_fig7": PlotCalibration(
        "paper_figures/paper1_BWP_switching/page-5.png",
        (651, 1022, 1044, 1325),
        (1, 1000),
        (0, 1),
        x_scale="log10",
    ),
    "sdt_fig3": PlotCalibration(
        "paper_figures/paper2_SDT_small_data/page-5.png",
        (651, 179, 1015, 415),
        (1, 10),
        (0.2, 0.8),
    ),
    "sdt_fig4": PlotCalibration(
        "paper_figures/paper2_SDT_small_data/page-5.png",
        (667, 754, 1015, 973),
        (1, 10),
        (0, 1),
    ),
}


ANCHORS = [
    Anchor(
        "high_load_bwp_8ms_1ms",
        "default_bwp_ratio_percent",
        "text_anchor",
        "Paper text: about 80% of UEs do not stay in Default BWP under high load.",
        "text",
        literal_paper_value=0,
        literal_x_value=80,
    ),
    Anchor(
        "low_load_bwp_8ms_1ms",
        "default_bwp_ratio_percent",
        "calibrated_visual_digitized",
        "Fig.5 calibrated visual point at about the 80th percentile.",
        "pixel",
        calibration=PLOTS["bwp_fig5"],
        pixel_point=(455, 728),
        output_from_axis="x",
        x_value_from_axis="y_percent",
    ),
    Anchor(
        "low_load_bwp_8ms_1ms",
        "power_saving_percent",
        "calibrated_visual_digitized",
        "Fig.6 calibrated visual point at about the 80th percentile.",
        "pixel",
        calibration=PLOTS["bwp_fig6"],
        pixel_point=(945, 198),
        output_from_axis="x",
        x_value_from_axis="y_percent",
    ),
    Anchor(
        "low_load_bwp_8ms_1ms",
        "pdu_scheduling_delay_ms",
        "calibrated_visual_digitized",
        "Fig.7 calibrated visual point at about the 50th percentile on a log-scale x axis.",
        "pixel",
        calibration=PLOTS["bwp_fig7"],
        pixel_point=(758, 1174),
        output_from_axis="x",
        x_value_from_axis="y_percent",
    ),
    Anchor(
        "4_step_ra_slot10",
        "packet_transmission_success_probability",
        "calibrated_visual_digitized",
        "Fig.3 basic-receiver calibrated visual point at slot 10.",
        "pixel",
        calibration=PLOTS["sdt_fig3"],
        pixel_point=(1015, 407),
    ),
    Anchor(
        "2_step_ra_slot10",
        "packet_transmission_success_probability",
        "calibrated_visual_digitized",
        "Fig.3 basic-receiver calibrated visual point at slot 10.",
        "pixel",
        calibration=PLOTS["sdt_fig3"],
        pixel_point=(1015, 344),
    ),
    Anchor(
        "4_step_sdt_slot10",
        "packet_transmission_success_probability",
        "calibrated_visual_digitized",
        "Fig.3 basic-receiver calibrated visual point at slot 10.",
        "pixel",
        calibration=PLOTS["sdt_fig3"],
        pixel_point=(1015, 372),
    ),
    Anchor(
        "2_step_sdt_slot10",
        "packet_transmission_success_probability",
        "calibrated_visual_digitized",
        "Fig.3 basic-receiver calibrated visual point at slot 10.",
        "pixel",
        calibration=PLOTS["sdt_fig3"],
        pixel_point=(1015, 336),
    ),
    Anchor(
        "4_step_ra_lambda_dp_5",
        "packet_transmission_success_probability",
        "calibrated_visual_digitized",
        "Fig.4 basic-receiver calibrated visual point at lambda_Dp = 5.",
        "pixel",
        calibration=PLOTS["sdt_fig4"],
        pixel_point=(822, 918),
    ),
    Anchor(
        "2_step_ra_lambda_dp_5",
        "packet_transmission_success_probability",
        "calibrated_visual_digitized",
        "Fig.4 basic-receiver calibrated visual point at lambda_Dp = 5.",
        "pixel",
        calibration=PLOTS["sdt_fig4"],
        pixel_point=(822, 885),
    ),
    Anchor(
        "4_step_sdt_lambda_dp_5",
        "packet_transmission_success_probability",
        "calibrated_visual_digitized",
        "Fig.4 basic-receiver calibrated visual point at lambda_Dp = 5.",
        "pixel",
        calibration=PLOTS["sdt_fig4"],
        pixel_point=(822, 901),
    ),
    Anchor(
        "2_step_sdt_lambda_dp_5",
        "packet_transmission_success_probability",
        "calibrated_visual_digitized",
        "Fig.4 basic-receiver calibrated visual point at lambda_Dp = 5.",
        "pixel",
        calibration=PLOTS["sdt_fig4"],
        pixel_point=(822, 881),
    ),
]


def fmt(value: float) -> str:
    rounded = round(value, 4)
    if abs(rounded - round(rounded)) < 1e-9:
        return str(int(round(rounded)))
    return f"{rounded:.4f}".rstrip("0").rstrip(".")


def interpolate_axis(pixel: float, pixel_min: float, pixel_max: float, data_min: float, data_max: float, scale: str) -> float:
    ratio = (pixel - pixel_min) / (pixel_max - pixel_min)
    if scale == "log10":
        log_min = math.log10(data_min)
        log_max = math.log10(data_max)
        return 10 ** (log_min + ratio * (log_max - log_min))
    return data_min + ratio * (data_max - data_min)


def read_pixel_anchor(anchor: Anchor) -> tuple[float, float]:
    assert anchor.calibration is not None
    assert anchor.pixel_point is not None
    x0, y0, x1, y1 = anchor.calibration.plot_box
    px, py = anchor.pixel_point
    x_value = interpolate_axis(px, x0, x1, *anchor.calibration.x_range, anchor.calibration.x_scale)
    y_value = interpolate_axis(py, y1, y0, *anchor.calibration.y_range, "linear")
    return x_value, y_value


def compute_anchor(anchor: Anchor) -> tuple[str, str, dict[str, str]]:
    if anchor.source_type == "text":
        assert anchor.literal_paper_value is not None
        assert anchor.literal_x_value is not None
        paper_value = anchor.literal_paper_value
        x_value = anchor.literal_x_value
        calibration_row = {
            "source_type": "text",
            "rendered_page": "",
            "plot_box": "",
            "pixel_point": "",
            "data_x": "",
            "data_y": "",
        }
    else:
        data_x, data_y = read_pixel_anchor(anchor)
        paper_value = data_x if anchor.output_from_axis == "x" else data_y
        if anchor.x_value_from_axis == "y_percent":
            x_value = data_y * 100
        elif anchor.x_value_from_axis == "y":
            x_value = data_y
        else:
            x_value = data_x
        assert anchor.calibration is not None
        assert anchor.pixel_point is not None
        calibration_row = {
            "source_type": "pixel",
            "rendered_page": anchor.calibration.rendered_page,
            "plot_box": " ".join(fmt(v) for v in anchor.calibration.plot_box),
            "pixel_point": " ".join(fmt(v) for v in anchor.pixel_point),
            "data_x": fmt(data_x),
            "data_y": fmt(data_y),
        }

    return fmt(x_value), fmt(paper_value), calibration_row


def main() -> int:
    with TEMPLATE.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        rows = list(reader)
        fieldnames = list(reader.fieldnames or [])

    by_key = {(anchor.scenario, anchor.metric): anchor for anchor in ANCHORS}
    calibration_rows: list[dict[str, str]] = []

    for row in rows:
        key = (row["scenario"], row["metric"])
        anchor = by_key.get(key)
        if anchor is None:
            continue
        x_value, paper_value, calibration_row = compute_anchor(anchor)
        row["x_value"] = x_value
        row["paper_value"] = paper_value
        row["source_status"] = anchor.source_status
        row["notes"] = anchor.note
        calibration_rows.append(
            {
                "scenario": row["scenario"],
                "metric": row["metric"],
                "source_figure": row["source_figure"],
                "source_curve": row["source_curve"],
                "x_axis": row["x_axis"],
                "x_value": x_value,
                "paper_value": paper_value,
                "source_status": anchor.source_status,
                "notes": anchor.note,
                **calibration_row,
            }
        )

    with TEMPLATE.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)

    calibration_fields = [
        "scenario",
        "metric",
        "source_figure",
        "source_curve",
        "source_type",
        "rendered_page",
        "plot_box",
        "pixel_point",
        "data_x",
        "data_y",
        "x_axis",
        "x_value",
        "paper_value",
        "source_status",
        "notes",
    ]
    with CALIBRATION.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=calibration_fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(calibration_rows)

    print(f"updated {TEMPLATE}")
    print(f"wrote {CALIBRATION}")
    print(f"anchors {len(calibration_rows)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
