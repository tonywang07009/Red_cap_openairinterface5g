## Context

The existing RedCap dApp/xApp validation area has a narrow, marker-backed access-pressure and PRB-control path. Its control contract exposes only a profile-level `drx_profile` placeholder; it has no source-proven adaptive C-DRX configuration path, no deterministic intermittent-traffic trace, and no DRX-specific A/B evidence.

This change designs an RRC_CONNECTED C-DRX experiment. It distinguishes three roles: the gNB owns RRC configuration, the UE MAC executes the configured DRX timers, and the dApp/gNB guard is the final local apply/reject boundary for xApp requests. The design does not treat a DRX Command MAC CE as a mechanism for changing the DRX cycle or On Duration.

## Goals / Non-Goals

**Goals:**

- Produce reproducible, separately scored downlink and uplink C-DRX A/B campaigns.
- Use a 30-sample history to produce a bounded prediction for the next 30 arrivals.
- Apply only versioned, legal, and observable DRX policy updates.
- Preserve a fixed Case A baseline and avoid unverified energy claims in RFsim.
- Produce an English and Traditional Chinese reproduction guide with a source trace guide.

**Non-Goals:**

- Do not validate RRC_INACTIVE eDRX, paging, PSM, or UE hardware power consumption.
- Do not send a DRX Command MAC CE after every HARQ ACK.
- Do not claim that E2SM-KPM is a control path.
- Do not rely on a normal-distribution assumption as a proof of traffic predictability.
- Do not claim a standard E2SM-RC DRX action until its local implementation and reference mapping are verified.

## Decisions

- [Campaign shape] Each campaign SHALL schedule 330 arrivals. The first 30 arrivals warm up the predictor; the final 300 are the scored population. This supplies ten 30-arrival adaptive windows without treating training samples as predicted samples.
- [Baseline] Arm A SHALL pre-apply `drx-320-10` once and retain that profile for all 300 scored arrivals. Arm B SHALL start from the same applied rollback baseline before its first adaptive request.
- [Traffic direction] Downlink and uplink SHALL run as independent campaigns before a bidirectional campaign is considered. The gNB sees downlink queue arrival directly, while uplink arrival must be timestamped at the UE traffic generator.
- [Prediction] The xApp SHALL calculate `mu`, `sigma`, and `mu +/- 3 sigma` from exactly 30 committed samples. It SHALL also report median, p95, min, and max. The dApp SHALL clamp candidates to legal RRC values and select a conservative fallback when the predicted interval is outside the experiment bounds or otherwise unreliable.
- [Control boundary] The Python xApp SHALL use E2SM-RC Radio Resource Allocation Control Service Style 2, Action 1, RAN Parameter 1 to convey the Long DRX Cycle Length. The C dApp/gNB guard SHALL correlate the RIC Request ID with the local versioned policy record, select On Duration from the approved local profile, and validate UE state, cooldown, and rollback data before applying an accepted RRC reconfiguration.
- [DRX Command boundary] A DRX Command MAC CE, if implemented, SHALL be a separately logged early-active-state action. It SHALL never be used to reconfigure `longDRX-CycleStartOffset` or `onDurationTimer`, and it SHALL be guarded by empty queues and no relevant outstanding work.
- [Window lifecycle] The dApp SHALL acknowledge a policy only after a gNB applied-state marker and the expected RRC completion evidence are present. It SHALL clear the 30-sample window only after that acknowledgement; rejected or timed-out requests retain evidence and a reject reason.
- [Measurement] Each scored arrival SHALL record traffic-direction timestamp, policy version, DRX profile, first-packet latency, throughput result, loss/retransmission proxy, and monitoring-time proxy. RFsim results SHALL be reported as energy proxies, not physical power measurements.
- [Trace guide] The final documentation SHALL include a code-reading route from traffic generation to xApp policy, E2 decode, dApp guard, RRC/MAC apply path, UE timer handling, and validation markers. Each route entry SHALL name the source file, symbol, input/output, expected marker, and the next trace point.

## Risks / Trade-offs

- [RRC reconfiguration latency can overlap a short traffic interval] -> Apply changes only at a committed window boundary, enforce a configurable cooldown, and record reconfiguration latency.
- [A 30-sample z-score model can misrepresent periodic or bounded traffic] -> Report robust descriptive statistics and use a conservative fallback profile whenever prediction quality is insufficient.
- [An E2 request can be acknowledged before the gNB configuration takes effect] -> Require distinct E2 acknowledgement, dApp applied marker, and RRC completion evidence.
- [UL and DL traffic generation timestamps are not equivalent] -> Store direction-specific source timestamps and prohibit combined claims before independent campaigns pass.
- [DRX state interactions can keep UE active after a command] -> Record all relevant state markers and state that a DRX Command is not an unconditional physical-sleep command.
- [Existing OAI DRX implementation is asymmetric] -> Implement matching gNB C-DRX scheduler state and complete the UE Active Time state machine before enabling adaptive runtime control.
- [E2SM-RC DRX control omits On Duration] -> Keep the E2 request standard and let the dApp select On Duration from a reviewed local profile; do not advertise a custom parameter as standard.

## Migration Plan

1. Add the DRX parameters and versioned policy schema without changing unrelated Case A files.
2. Add read-only trace and static contract checks before enabling runtime application.
3. Enable the fixed `drx-320-10` baseline first, then the dApp apply path behind an explicit Case B flag.
4. Roll back an accepted policy by applying the saved previous profile; reject updates requiring a restart or unsupported RRC mutation.
5. Preserve all artifacts and report a PARTIAL or BLOCKED result when control acknowledgement lacks gNB/UE marker proof.

## Review Resolution

- Current OAI has a partial UE C-DRX configuration/monitoring path but no matching gNB C-DRX scheduler state or active DRX Command behavior.
- E2SM-RC R005 defines the DRX action under Service Style 2 / Action 1; the current OAI RC function does not implement it.
- v1 admits only the six cycle/On Duration pairs in `review/drx_policy_contract_v1.yaml` and disables short DRX.
- v1 uses scheduled fixed-byte UDP bursts with iPerf2 `--txstart-time`; the generated trace CSV, not process start time, is the arrival-time source of truth.
- Remaining `[Needs Verification]`: exact TS 38.473 encoding for the Long DRX Cycle Length and the SFN/start-offset calculation after RRC apply latency.
