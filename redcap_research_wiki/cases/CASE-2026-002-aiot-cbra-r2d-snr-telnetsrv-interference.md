---
status: review-required
case_id: CASE-2026-002
case_type: experiment-learning
system_scope: A-IoT CBRA Paging/Access Trigger R2D M/SNR RFsim campaign
source_refs:
  - radio/rfsimulator/simulator.cpp
  - aiot_measuer/D2R_BLER_Measuer/main_code/cbra_epoch.py
  - aiot_measuer/D2R_BLER_Measuer/main_code/fourmula.py
  - aiot_measuer/D2R_BLER_Measuer/main_code/CLI.py
  - openspec/changes/archive/2026-09-21-validate-aiot-cbra-measurement-campaign/specs/aiot-cbra-measurement-validation/spec.md
evidence_refs:
  - test_log/measurements/aiot_cbra_r2d_formal_campaign_2026-09-20.json
  - test_log/measurements/aiot_cbra_r2d_formal_campaign_rows_2026-09-20.jsonl
  - test_log/measurements/aiot_cbra_no_noise_recheck_kind0_m24_raw_2026-09-20.jsonl
  - test_log/runtime/aiot_cbra_measurement_validation_2026-09-21/window1000_escalated/tag.log
  - test_log/runtime/aiot_cbra_measurement_validation_2026-09-21/window1000_escalated/ue_reader.log
  - test_log/build_logs/aiot_cbra_talanet_runtime_build_no_tests_2026-09-21.log
  - test_log/runtime/aiot_cbra_talanet_epoch_smoke_2026-09-21/escalated/gnb.log
  - test_log/runtime/aiot_cbra_talanet_epoch_smoke_2026-09-21/one_point_pilot/controller.log
  - test_log/runtime/aiot_cbra_talanet_epoch_smoke_2026-09-21/one_point_pilot/gnb.log
  - test_log/runtime/aiot_cbra_talanet_epoch_smoke_2026-09-21/one_point_pilot/tag.log
  - test_log/runtime/aiot_cbra_talanet_epoch_smoke_2026-09-21/one_point_pilot/ue_reader.log
  - test_log/runtime/aiot_cbra_talanet_epoch_smoke_2026-09-21/one_point_pilot/result.txt
  - test_log/runtime/aiot_cbra_talanet_snr_calibration_pilot_2026-09-21/controller.log
  - test_log/runtime/aiot_cbra_talanet_snr_calibration_pilot_2026-09-21/gnb.log
  - test_log/runtime/aiot_cbra_talanet_snr_calibration_pilot_2026-09-21/tag_0.log
  - test_log/runtime/aiot_cbra_talanet_snr_calibration_pilot_2026-09-21/ue_reader.log
  - test_log/runtime/aiot_cbra_talanet_snr_calibration_pilot_2026-09-21/udp_report.bin
  - test_log/runtime/aiot_cbra_talanet_snr_calibration_pilot_2026-09-21/points.tsv
  - openspec/changes/archive/2026-09-21-validate-aiot-cbra-measurement-campaign/evidence/campaign_result_2026-09-21.md
evidence_tier: mixed
last_reviewed: 2026-09-21
related_pages:
  - redcap_research_wiki/systems/aiot/overview.md
  - redcap_research_wiki/systems/aiot/tag-reader.md
---

# CASE-2026-002: CBRA R2D SNR Requires Talanet/telnetsrv Interference

## Question

How should the CBRA Paging and Access Trigger R2D M/SNR method test prove that
the requested SNR sweep changed the RFsim channel, rather than only changing a
report label or plot coordinate?

## Context and Reproduction

The retained formal campaign used one reported SNR point per message kind and
M value. The `--aiot_snr_db_x10` option is available in the RFsim state, but
the actual R2D channel transformation is performed by `aiot_t2_apply_channel`
using the channel noise power. The calibrated SNR is computed later from the
post-filter signal and noise powers. These are different control and
measurement paths.

The prior M=24 Paging point is a reproducible warning: its 10,000 rows match
the retained no-noise recheck capture, so `BER=0` there cannot be treated as a
fresh physical error-rate result. The fixed-budget aggregator also requires
10,000 unique attempt indices, power calibration, an acknowledged channel
epoch, and no D2R attempt for a pure R2D M/SNR point.

The bounded CBRA transaction remains:

```text
Msg1 -> Msg2 -> reflected tag data -> Msg3
```

Msg3 carries the tag transfer ACK/NACK. A same-reader duplicate access
occasion is a collision; the same access occasion on a different Reader is an
independent transaction.

## Expected versus Observed

| Item | Expected | Observed in retained evidence |
| --- | --- | --- |
| SNR control | Each point changes RFsim noise through `telnetsrv` and `rfsimu aiot_epoch set`. | The older formal campaign does not provide per-point Talanet readback or channel-application markers. |
| SNR axis | Plot calibrated post-filter SNR and retain the requested target separately. | The older plot has one point per kind/M and is not a BER-versus-SNR curve. |
| M=24 zero | A zero-error point has fresh, independent captures and a traceable channel epoch. | The M=24 Paging capture matches a no-noise recheck; the zero is not sufficient evidence of zero physical BER. |
| CBRA flow | Msg1, Msg2, reflection, Msg3, and Reader receipt are visible. | The retained logical RFsim logs show the flow and `data_received=1`; they do not establish a fresh SNR-interference campaign. |

## Evidence

[Source Trace] `radio/rfsimulator/simulator.cpp` registers `rfsimu aiot_epoch`
under the RFsim Telnet command set. `aiot_t2_apply_channel` applies
`noise_power` to the R2D/RFsim samples and emits
`AIOT_T2_CHANNEL_APPLIED`. `aiot_snr_db_x10` is not, by itself, proof that
the sample noise changed.

[Source Trace] `TalanetEpochController` keeps a persistent command path and
rejects a point unless the epoch is monotonic, the readback is acknowledged,
the queue is drained (`queued=0`), and the returned noise/seeds match the
request.

[Source Trace] `cbra_snr_calibration` derives the calibrated SNR from separate
signal/noise power measurements. `aggregate_cbra_campaign_rows` requires the
fixed 10,000-attempt budget and rejects missing channel/power evidence or
unexpected D2R rows.

[Runtime Evidence] The retained window-1000 CBRA run records
`Msg1 -> Msg2 -> reflection -> Msg3`, and the Reader log records data receipt.
The run was started with noise power zero and has no Talanet interference
markers, so it is logical CBRA-flow evidence only.

[Runtime Evidence] The `ENABLE_TELNETSRV=ON` runtime build completed. A prior
smoke using a non-persistent polling client reached the Telnet server but did
not complete a valid asynchronous `aiot_epoch` evidence exchange; its log is
retained as a failed method, not as interference proof.

[Runtime Evidence] The one-point pilot used the connected gNB+UE+Tag+CW path.
`TalanetEpochController` read epoch 1 with `queued=0`, then set epoch 2 with
noise power 20 and data/noise seeds 101/202, receiving `readback=ok queued=0`.
The gNB log records both `telnetsrv` commands, the Tag and Reader complete the
CBRA flow, and the UDP collector received 600 bytes. The retained gNB log does
not contain `AIOT_T2_CHANNEL_APPLIED`, so this pilot proves the controller
readback and CBRA runtime path but not the complete channel-application gate.

[Runtime Evidence] The bounded low-SNR calibration retry called Talanet for
the first requested label (-10 dB) and received epoch 2, noise power 100, and
seeds 101/201. It retained 756 reports with the same epoch/seeds; calibrated
SNR averaged -5.51 dB over -6.4 to -4.9 dB, with 701 CRC failures, 55 invalid
reports, no D2R attempt, and no CBRA completion. The retry stopped before the
remaining four labels, so it is a failed calibration point, not a five-level
curve.

[Needs Verification] A fresh 40-point campaign with per-point Talanet
readback, channel-application markers, calibrated SNR, and independent
attempts is not established by this case.

## Competing Explanations

1. The SNR changed only in the report or plot metadata. Distinguish this by
   requiring `rfsimu aiot_epoch` readback and `AIOT_T2_CHANNEL_APPLIED` for the
   same point/epoch before accepting any samples.
2. M=24 genuinely has no errors. Distinguish this from a duplicate/no-noise
   capture using fresh attempt fingerprints, a new acknowledged epoch, and
   independent channel seeds.
3. The Telnet command was accepted but not applied. Distinguish this with a
   persistent controller connection, `readback=ok`, `queued=0`, monotonic
   epoch, and the RFsim channel-application marker.

## Resolution or Next Owner

The next CBRA R2D method test must use the following gate for **every** target
point:

1. Build the runtime with `ENABLE_TELNETSRV=ON`.
2. Start the RFsim gNB with `--telnetsrv` and retain the selected Telnet port.
3. Keep a persistent `TalanetEpochController` connection.
4. Issue `rfsimu aiot_epoch set` with the point's noise/seed configuration.
5. Start capture only after `readback=ok`, `queued=0`, a new monotonic epoch,
   and the matching `AIOT_T2_CHANNEL_APPLIED` marker are recorded.
6. Retain target SNR and measured calibrated SNR as separate fields. Do not
   relabel the old campaign as the new sweep.
7. For the requested grid, collect Paging and Access Trigger for
   `M={2,6,12,24}` at `SNR={-10,-5,0,5,10} dB`: 40 points, each with 10,000
   unique attempts. Reject a point when the calibration, epoch, alignment,
   or independence evidence is missing.

The target-to-`noise_power` mapping still needs a calibration pass; the five
requested labels alone do not establish five measured SNR values.

## Claim Boundary

This case establishes a reusable measurement rule and explains why the old
M/SNR figure is insufficient for the requested interference experiment. It
does not establish the 40-point campaign, a physical-RF error rate, BLER or
goodput results, or TS 38.391 interoperability. `BER=0` remains an observed
zero-error batch, not proof that the underlying error probability is zero.

## Documentation Impact

Add this case to the LLM wiki index and activity log. Keep it
`review-required` until the fresh Talanet-controlled campaign is reviewed.
Future method-test reports must include the `telnetsrv`/Talanet readback and
channel-application evidence listed above; a startup noise parameter or a
changed SNR label alone is insufficient.
