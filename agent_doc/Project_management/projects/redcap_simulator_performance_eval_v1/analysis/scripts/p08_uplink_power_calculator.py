#!/usr/bin/env python3
"""PAPER-08 RedCap uplink power calculator.

This helper implements the piece-wise linear uplink transmit power model from
PAPER-08, Equation (1), using the RedCap Table II coefficients. It can be used
as a normal CLI tool or as a small newline-delimited JSON TCP service for
external experiment runners.

The calculator is a model-side estimate. It is not a replacement for a power
meter because OAI RFsim does not expose real UE RF PA power consumption.
"""

from __future__ import annotations

import argparse
import csv
import json
import socketserver
import sys
from dataclasses import asdict, dataclass, replace
from typing import Any, Iterable


MODEL_SOURCE = (
    "PAPER-08 Table II / Equation (1): Empirical Comparison of Power "
    "Consumption and Data Rates for 5G New Radio and RedCap Devices"
)


@dataclass(frozen=True)
class BandModel:
    alpha1: float
    beta1: float
    gamma1_dbm: float
    alpha2: float
    beta2: float
    pmax_w: float
    ptx_max_dbm: float = 23.0


MODELS: dict[str, BandModel] = {
    "n41": BandModel(alpha1=0.30, beta1=1.5e-4, gamma1_dbm=4.0, alpha2=0.19, beta2=2.1e-2, pmax_w=0.69),
    "n78": BandModel(alpha1=0.35, beta1=1.1e-4, gamma1_dbm=5.0, alpha2=0.46, beta2=3.6e-3, pmax_w=1.45),
}


@dataclass(frozen=True)
class PowerEstimate:
    band: str
    ptx_dbm: float
    ptx_max_dbm: float
    segment: str
    pue_w: float
    pue_mw: float
    tx_seconds_per_period: float | None
    connected_idle_seconds_per_period: float | None
    period_seconds: float | None
    connected_idle_mw: float
    edrx_mw: float
    average_power_w: float | None
    average_power_mw: float | None
    model_source: str


def _get_model(band: str, overrides: dict[str, Any] | None = None) -> BandModel:
    key = band.lower()
    if key not in MODELS:
        raise ValueError(f"unsupported band '{band}', expected one of: {', '.join(sorted(MODELS))}")

    model = MODELS[key]
    if not overrides:
        return model

    allowed = set(BandModel.__dataclass_fields__)
    clean: dict[str, float] = {}
    for name, value in overrides.items():
        if name not in allowed:
            raise ValueError(f"unsupported model override '{name}'")
        clean[name] = float(value)
    return replace(model, **clean)


def estimate_power(
    *,
    band: str,
    ptx_dbm: float,
    model_overrides: dict[str, Any] | None = None,
    tx_seconds_per_period: float | None = None,
    connected_idle_seconds_per_period: float | None = None,
    period_seconds: float | None = None,
    connected_idle_mw: float = 252.6,
    edrx_mw: float = 21.9,
) -> PowerEstimate:
    """Estimate instantaneous and optional duty-cycle average UE power."""

    band_key = band.lower()
    model = _get_model(band_key, model_overrides)

    if ptx_dbm >= model.ptx_max_dbm:
        segment = "pmax"
        pue_w = model.pmax_w
    elif ptx_dbm >= model.gamma1_dbm:
        segment = "alpha2_beta2"
        pue_w = model.alpha2 + model.beta2 * ptx_dbm
    else:
        segment = "alpha1_beta1"
        pue_w = model.alpha1 + model.beta1 * ptx_dbm

    average_power_w: float | None = None
    average_power_mw: float | None = None
    idle_seconds = connected_idle_seconds_per_period
    if tx_seconds_per_period is not None or period_seconds is not None or idle_seconds is not None:
        if tx_seconds_per_period is None or period_seconds is None:
            raise ValueError("tx_seconds_per_period and period_seconds must be provided together")
        if tx_seconds_per_period < 0 or period_seconds <= 0:
            raise ValueError("tx_seconds_per_period must be >= 0 and period_seconds must be > 0")
        if idle_seconds is None:
            idle_seconds = 0.0
        if idle_seconds < 0:
            raise ValueError("connected_idle_seconds_per_period must be >= 0")
        if tx_seconds_per_period + idle_seconds > period_seconds:
            raise ValueError("tx_seconds_per_period + connected_idle_seconds_per_period exceeds period_seconds")

        edrx_seconds = period_seconds - tx_seconds_per_period - idle_seconds
        average_power_w = (
            pue_w * tx_seconds_per_period
            + (connected_idle_mw / 1000.0) * idle_seconds
            + (edrx_mw / 1000.0) * edrx_seconds
        ) / period_seconds
        average_power_mw = average_power_w * 1000.0

    return PowerEstimate(
        band=band_key,
        ptx_dbm=float(ptx_dbm),
        ptx_max_dbm=model.ptx_max_dbm,
        segment=segment,
        pue_w=pue_w,
        pue_mw=pue_w * 1000.0,
        tx_seconds_per_period=tx_seconds_per_period,
        connected_idle_seconds_per_period=idle_seconds,
        period_seconds=period_seconds,
        connected_idle_mw=connected_idle_mw,
        edrx_mw=edrx_mw,
        average_power_w=average_power_w,
        average_power_mw=average_power_mw,
        model_source=MODEL_SOURCE,
    )


def handle_json_request(payload: dict[str, Any]) -> dict[str, Any]:
    overrides = payload.get("model_overrides")
    if overrides is not None and not isinstance(overrides, dict):
        raise ValueError("model_overrides must be an object")

    estimate = estimate_power(
        band=str(payload["band"]),
        ptx_dbm=float(payload["ptx_dbm"]),
        model_overrides=overrides,
        tx_seconds_per_period=_optional_float(payload.get("tx_seconds_per_period")),
        connected_idle_seconds_per_period=_optional_float(payload.get("connected_idle_seconds_per_period")),
        period_seconds=_optional_float(payload.get("period_seconds")),
        connected_idle_mw=float(payload.get("connected_idle_mw", 252.6)),
        edrx_mw=float(payload.get("edrx_mw", 21.9)),
    )
    return asdict(estimate)


def _optional_float(value: Any) -> float | None:
    if value is None:
        return None
    return float(value)


class PowerRequestHandler(socketserver.StreamRequestHandler):
    def handle(self) -> None:
        for raw_line in self.rfile:
            line = raw_line.strip()
            if not line:
                continue
            try:
                payload = json.loads(line.decode("utf-8"))
                if not isinstance(payload, dict):
                    raise ValueError("request must be a JSON object")
                response = {"ok": True, "result": handle_json_request(payload)}
            except Exception as exc:  # noqa: BLE001 - service returns validation errors as JSON.
                response = {"ok": False, "error": str(exc)}
            self.wfile.write((json.dumps(response, sort_keys=True) + "\n").encode("utf-8"))


def serve(address: str) -> None:
    host, port_text = address.rsplit(":", 1)
    with socketserver.ThreadingTCPServer((host, int(port_text)), PowerRequestHandler) as server:
        server.daemon_threads = True
        server.serve_forever()


def write_csv(estimates: Iterable[PowerEstimate]) -> None:
    fieldnames = list(PowerEstimate.__dataclass_fields__.keys())
    writer = csv.DictWriter(sys.stdout, fieldnames=fieldnames)
    writer.writeheader()
    for estimate in estimates:
        writer.writerow(asdict(estimate))


def self_test() -> None:
    cases = [
        ("n41-low", estimate_power(band="n41", ptx_dbm=-10.0).pue_w, 0.2985),
        ("n41-mid", estimate_power(band="n41", ptx_dbm=10.0).pue_w, 0.40),
        ("n41-max", estimate_power(band="n41", ptx_dbm=23.0).pue_w, 0.69),
        ("n78-low", estimate_power(band="n78", ptx_dbm=0.0).pue_w, 0.35),
        ("n78-mid", estimate_power(band="n78", ptx_dbm=10.0).pue_w, 0.496),
        ("n78-max", estimate_power(band="n78", ptx_dbm=23.0).pue_w, 1.45),
    ]
    for name, actual, expected in cases:
        if abs(actual - expected) > 1e-9:
            raise AssertionError(f"{name}: expected {expected}, got {actual}")

    avg = estimate_power(band="n41", ptx_dbm=23.0, tx_seconds_per_period=300.0, period_seconds=3600.0)
    expected_avg = (0.69 * 300.0 + 0.0219 * 3300.0) / 3600.0
    if avg.average_power_w is None or abs(avg.average_power_w - expected_avg) > 1e-12:
        raise AssertionError("duty-cycle average calculation failed")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="PAPER-08 RedCap uplink power calculator")
    parser.add_argument("--band", choices=sorted(MODELS), default="n78")
    parser.add_argument("--ptx-dbm", type=float, nargs="*", default=[-10.0, 0.0, 5.0, 10.0, 20.0, 23.0])
    parser.add_argument("--ptx-max-dbm", type=float, default=None)
    parser.add_argument("--tx-seconds-per-period", type=float, default=None)
    parser.add_argument("--connected-idle-seconds-per-period", type=float, default=None)
    parser.add_argument("--period-seconds", type=float, default=None)
    parser.add_argument("--connected-idle-mw", type=float, default=252.6)
    parser.add_argument("--edrx-mw", type=float, default=21.9)
    parser.add_argument("--json", action="store_true", help="print JSON instead of CSV")
    parser.add_argument("--listen", help="serve newline-delimited JSON over host:port, for example 127.0.0.1:8765")
    parser.add_argument("--self-test", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    if args.self_test:
        self_test()
        print("self-test passed")
        return 0

    if args.listen:
        serve(args.listen)
        return 0

    overrides = {"ptx_max_dbm": args.ptx_max_dbm} if args.ptx_max_dbm is not None else None
    estimates = [
        estimate_power(
            band=args.band,
            ptx_dbm=ptx,
            model_overrides=overrides,
            tx_seconds_per_period=args.tx_seconds_per_period,
            connected_idle_seconds_per_period=args.connected_idle_seconds_per_period,
            period_seconds=args.period_seconds,
            connected_idle_mw=args.connected_idle_mw,
            edrx_mw=args.edrx_mw,
        )
        for ptx in args.ptx_dbm
    ]

    if args.json:
        print(json.dumps([asdict(item) for item in estimates], indent=2, sort_keys=True))
    else:
        write_csv(estimates)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
