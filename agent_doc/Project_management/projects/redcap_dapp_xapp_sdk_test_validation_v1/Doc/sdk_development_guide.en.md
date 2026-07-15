# RedCap dApp/xApp SDK Development Guide

## Scope

- This guide is for engineers adding or changing RedCap dApp/xApp SDK algorithms.
- It explains the current SDK contract, not a fully productized O-RAN SDK.
- Runtime claims must still point to Gate reports and logs.

## Code Locations

| Area | Path | Current role |
|---|---|---|
| xApp C SDK | `openair2/E2AP/REDCAP_SDK/xapp/redcap_xapp_sdk.h` / `.c` | Priority-hint data model and selection helper |
| xApp Python helper | `openair2/E2AP/REDCAP_SDK/xapp/redcap_xapp_sdk.py` | Fast parity helper for priority-hint logic |
| dApp C SDK | `openair2/E3AP/sdk/redcap_dapp_sdk.h` / `.c` | PRB allocation guard, access-pressure policy, and RA-pressure selector |
| dApp Python helper | `openair2/E3AP/sdk/redcap_dapp_sdk.py` | Fast parity helper for dApp policy and selector logic |
| E2/FlexRIC assets | `openair2/E2AP/flexric` | xApp / nearRT-RIC integration route |
| E3 references | `Apps_dev/dapp_dev_need/libe3` | dApp-side E3 loopback and SWIG reference route |

## Reference: Evidence Labels

- `Public`: declared in the C header or supported Python module.
- `Integrated`: called by a production control path with an identifiable apply boundary.
- `Runtime-evidenced`: a matching marker exists in retained runtime evidence.
- `Dormant/blocked`: implemented but missing a production caller, apply path, or runtime proof.

The cards below use repository source and retained local evidence. Exact O-RAN or 3GPP mappings remain `[Needs Verification]` unless a local clause is cited.

## Reference: xApp API Cards

### `redcap_xapp_make_ul_prb_ctrl_req`

- **Problem / when**: build the E2SM-RC UL PRB-cap request after selecting a live UE and validating the requested cap.
- **C / Python**: `rc_ctrl_req_data_t redcap_xapp_make_ul_prb_ctrl_req(uint64_t ue_id, uint16_t rnti, uint16_t max_ul_prb)` / `make_ul_prb_ctrl_request(ue_id: int, rnti: int, max_ul_prb: int) -> RedCapUlPrbCtrlRequest`.
- **Input / output / owner**: caller owns UE ID, RNTI, cap, returned request, and C allocations. The C builder does not reject zero or out-of-range values; the caller/downstream guard owns that boundary. Python validates its dataclass inputs.
- **Trace**: caller `ci-scripts/redcap_ul_prb_ctrl_xapp.c`; callees build UE ID and integer RAN parameters; downstream apply point `apply_redcap_ul_prb_control` in `ran_func_rc.c`.
- **Marker / next trace / evidence**: trace `CONTROL ACK rx` to gNB `RedCap UL PRB control ... effective ...`; retained evidence is `test_log/compiler_logs/redcap_rc_ctrl_xapp_2026-07-09_00-00-46*.log`. Status: `Public`, `Integrated`, `Runtime-evidenced`.

### `redcap_xapp_make_drx_ctrl_req`

- **Problem / when**: build a DRX-cycle E2SM-RC request for an approved cycle after UE and policy selection.
- **C / Python**: `bool redcap_xapp_make_drx_ctrl_req(uint64_t ue_id, uint16_t long_cycle_ms, rc_ctrl_req_data_t *ctrl_req)` / `make_drx_ctrl_request(ue_id: int, long_cycle_ms: int, ric_request_id: int, policy_version: int) -> RedCapDrxCtrlRequest`.
- **Input / output / owner**: approved cycles are `320, 640, 1280, 2560, 5120, 10240` ms. Caller owns the result and C allocations. C rejects zero UE, null output, unsupported cycle, and allocation failure; Python also carries correlation fields not present in the C signature.
- **Trace**: proven C caller is `test_redcap_xapp_drx.c`; callees build UE ID and integer parameters. The live adaptive runner uses a separate Python/SWIG control path, so this helper's production caller/apply point is `[Needs Verification]`.
- **Marker / next trace / evidence**: no marker is emitted by the builder. Trace live DRX requests through `ran_func_rc.c` and `redcap_dapp_guard_e2_drx_cycle`. Status: `Public`, `Dormant/blocked`; not independently runtime-evidenced.

### `redcap_xapp_find_rc_ran_func_idx`

- **Problem / when**: locate the RC RAN function in a connected E2 node before subscription or control.
- **C / Python**: `ssize_t redcap_xapp_find_rc_ran_func_idx(const e2_node_connected_xapp_t *node)` / `find_rc_ran_func_idx(ran_functions: Sequence[Mapping[str, Any]]) -> int`.
- **Input / output / owner**: caller owns the node/function list; returns the index or `-1`. C rejects null and scans `len_rf`; no shared state.
- **Trace**: caller `ci-scripts/redcap_ul_prb_ctrl_xapp.c`; compares `SM_RC_ID` or `RC_RAN_FUNC_DEF_E`; the returned index selects the RC path.
- **Marker / next trace / evidence**: no dedicated marker. Continue to subscription/control setup in the caller. Successful retained RC control indirectly proves this lookup path. Status: `Public`, `Integrated`, `Runtime-evidenced` indirectly.

### `redcap_xapp_make_priority_hint`

- **Problem / when**: convert one UE metric into a bounded priority hint before selecting or forwarding a candidate.
- **C / Python**: `bool redcap_xapp_make_priority_hint(const redcap_xapp_ue_metric_t *metric, uint16_t validity_ms, redcap_xapp_priority_hint_t *hint)` / `make_priority_hint(metric: RedCapUeMetric, validity_ms: int) -> RedCapPriorityHint`.
- **Input / output / owner**: caller owns metric/result; weight is `UL bytes / 1024 + QoS + RedCap`, saturated to `uint16`. C rejects null, RNTI 0, and validity 0; Python additionally rejects negative values and values above field limits.
- **Trace**: C caller is `redcap_xapp_select_top_priority_hint`; Python callers are selection and self-check. No production control conversion caller is proven.
- **Marker / next trace / evidence**: result carries `RedCap xApp priority hint`, but no retained production log emits it. Trace next to a non-test caller and RC-request conversion. Status: `Public`, `Dormant/blocked`.

### `redcap_xapp_select_top_priority_hint`

- **Problem / when**: select the highest-weight UE; lower RNTI wins a tie.
- **C / Python**: `bool redcap_xapp_select_top_priority_hint(const redcap_xapp_ue_metric_t *metrics, size_t metrics_len, uint16_t validity_ms, redcap_xapp_priority_hint_t *hint)` / `select_top_priority_hint(metrics: Sequence[RedCapUeMetric], validity_ms: int) -> RedCapPriorityHint`.
- **Input / output / owner**: caller owns list/result; no shared state. C rejects null/empty and skips invalid candidates; Python raises on empty input or the first invalid metric, so invalid-element behavior is not identical.
- **Trace**: calls the single-hint builder. Proven callers are static checks and Python self-test; production caller and apply point are `[Needs Verification]`.
- **Marker / next trace / evidence**: selected result carries `RedCap xApp priority hint`; no matching production log is retained. Status: `Public`, `Dormant/blocked`.

## Reference: dApp API Cards

### `redcap_dapp_guard_ul_prb_cap` and `redcap_dapp_guard_allows_apply`

- **Problem / when**: accept a requested UL cap only when RNTI and contract range are valid.
- **C / Python**: `redcap_dapp_guard_result_t redcap_dapp_guard_ul_prb_cap(const redcap_dapp_ul_prb_request_t *request)` plus `bool redcap_dapp_guard_allows_apply(...)`; Python uses the same names and matching request/result dataclasses.
- **Input / output / owner**: caller owns request/result; rejects null, RNTI 0, inverted min/max, and a cap outside the inclusive range. No shared state.
- **Trace**: current callers are Python self-checks; no production caller or scheduler apply point is proven.
- **Marker / next trace / evidence**: no runtime marker. Search for a production caller before using this as an enforcement claim. Status: `Public`, `Dormant/blocked`.

### `redcap_dapp_guard_prb_allocation` and `redcap_dapp_prb_allocation_allows_apply`

- **Problem / when**: validate BWP/IQ/ratio intent and convert accepted permille values into PRB counts.
- **C / Python**: `redcap_dapp_prb_allocation_result_t redcap_dapp_guard_prb_allocation(const redcap_dapp_prb_allocation_request_t *request)` plus its `allows_apply` helper; Python uses matching names and dataclasses.
- **Input / output / owner**: caller owns values; accepts BWP `11`, `12`, or `51`, requires non-zero RNTI and IQ evidence, and rejects either ratio or their sum above `1000`. Output uses ceiling division; no shared state.
- **Trace**: production callers are the PUCCH hook in `gNB_scheduler_uci.c` and UL hook in `gNB_scheduler_ulsch.c`; internal callee converts ratios. Hooks currently observe/log after scheduler fields exist, so allocation mutation is `[Needs Verification]`.
- **Marker / next trace / evidence**: `RedCap dApp PRB decision`; retained Gate D log `test_log/runtime_logs/gate_d_access_pressure_gnb_2026-07-07_00-47_local_no_csirs_srs.log`. Status: `Public`, `Integrated`, `Runtime-evidenced`; enforcement remains blocked/unproven.

### `redcap_dapp_access_pressure_policy` and `redcap_dapp_access_pressure_allows_apply`

- **Problem / when**: convert access counters and prior EWMA into low/medium/high ratio intent before allocation validation.
- **C / Python**: `redcap_dapp_access_pressure_result_t redcap_dapp_access_pressure_policy(const redcap_dapp_access_pressure_request_t *request)` plus its `allows_apply` helper; Python mirrors both names.
- **Input / output / owner**: caller owns counters/state and result. Policy clamps pressure to `1000`, computes integer EWMA, chooses fixed ratios, then calls `redcap_dapp_guard_prb_allocation`; the guard owns RNTI/BWP/IQ rejection.
- **Trace**: called by the RA selector and self-tests. No gNB production caller applies the policy result; current PUCCH/UL hooks call the lower allocation guard directly.
- **Marker / next trace / evidence**: result carries `RedCap dApp access pressure policy`, but no matching production apply marker is retained. Status: `Public`, `Dormant/blocked` for production application.

### `redcap_dapp_select_ra_pressure_priority`

- **Problem / when**: select the UE with the largest RA retry count, then pressure, priority, and lower RNTI.
- **C / Python**: `redcap_dapp_access_pressure_selection_t redcap_dapp_select_ra_pressure_priority(const redcap_dapp_access_pressure_request_t *requests, size_t request_count)` / matching Python function returning `RedCapDappAccessPressureSelection`.
- **Input / output / owner**: caller owns list/result; null/empty or all-zero RNTIs return `found=false`. It calls `redcap_dapp_access_pressure_policy` for the selected UE; no shared state.
- **Trace**: Python experiment caller `select_core36_pressure_priority.py`; C callers are self-check/static only. The experiment writes `MMTC_DAPP_PRIORITY_UES`; a C production scheduler apply point is `[Needs Verification]`.
- **Marker / next trace / evidence**: result carries `RedCap dApp RA pressure priority`; Core36 report proves experiment selection, not mitigation improvement. Status: `Public`; Python experiment-integrated; C path `Dormant/blocked`.

### `redcap_dapp_guard_drx_policy` and `redcap_dapp_drx_guard_allows_apply`

- **Problem / when**: validate a prediction-derived DRX profile, policy version, cooldown, and rollback state.
- **C / Python**: C-only `redcap_dapp_drx_guard_result_t redcap_dapp_guard_drx_policy(const redcap_dapp_drx_policy_request_t *request, const redcap_dapp_drx_config_t *current)` plus `redcap_dapp_drx_guard_allows_apply`; Python mirror is absent.
- **Input / output / owner**: caller owns request/current/result; rejects schema, RNTI, connection, stale version, sample count, prediction bounds, cycle, cooldown, and rollback failures. Accepted result retains previous state; no shared state.
- **Trace**: callers are focused C tests. Live E2 control uses the narrower E2-cycle guard below, not this prediction guard.
- **Marker / next trace / evidence**: `[RedCap DRX][dApp ACCEPT]` or `REJECT`; no retained runtime proof is attributed to this exact function. Status: `Public`, `Dormant/blocked`.

### `redcap_dapp_guard_e2_drx_cycle`

- **Problem / when**: gate a live E2 DRX-cycle request before applying it to gNB MAC/RRC state.
- **C / Python**: C-only `redcap_dapp_drx_guard_result_t redcap_dapp_guard_e2_drx_cycle(const redcap_dapp_e2_drx_cycle_request_t *request, const redcap_dapp_drx_config_t *current)`; Python mirror is absent.
- **Input / output / owner**: caller snapshots current gNB state, then owns request/result. Rejects unknown/disconnected UE, stale policy, unsupported cycle, active cooldown, and invalid rollback configuration.
- **Trace**: production caller `ran_func_rc.c`; on ACK, `redcap_dapp_drx_guard_allows_apply` gates `nr_mac_apply_drx_policy`, followed by RRC reconfiguration.
- **Marker / next trace / evidence**: `[RedCap DRX][dApp ACCEPT]` / `REJECT`, then gNB apply and RRC-complete correlation. The four adaptive DRX campaigns retain matching evidence in `test_log/runtime_logs/adaptive_drx_2026-07-13_full_ab/`. Status: `Public`, `Integrated`, `Runtime-evidenced`.

## Guide: Algorithm Contract

- [xApp input]: per-UE metric such as RNTI, UL buffer, QoS weight, and RedCap weight.
- [xApp output]: `priority_weight`, packaged as a RedCap priority hint.
- [dApp input]: RA retry count, Msg3 failure count, PUCCH resource reject count, CRC/discard count, previous pressure EWMA, BWP PRB marker, I/Q availability, and optional xApp priority hint.
- [dApp output]: bounded PUCCH/PUSCH ratio intent, RA-pressure priority selection, and PRB allocation metadata.
- [Guard boundary]: dApp policy output must pass `redcap_dapp_guard_prb_allocation` before it can be treated as applyable.
- [I/Q boundary]: `has_iq_samples` must be true for apply; otherwise the result must stay reject/diagnostic.

## Current Policy Shape

- [Pressure score]: `100 * ra_retry + 120 * msg3_failure + 160 * pucch_resource_reject + 40 * crc_discard`, clamped to `1000`.
- [Priority selector]: `redcap_dapp_select_ra_pressure_priority` picks the UE with the highest [RA retry count] first, then pressure score, priority weight, and lower RNTI.
- [EWMA]: integer approximation of `0.7 * previous + 0.3 * current`.
- [Low pressure]: PUCCH `200`, PUSCH `600`.
- [Medium pressure]: PUCCH `300`, PUSCH `500`.
- [High pressure]: PUCCH `400`, PUSCH `400`.
- [51 PRB proxy]: Gate E-Core uses `MMTC_N_RB_DL=51`; exact 20 MHz terminology remains `[Needs Verification]`.

## E2 / E3 Boundary

- [E2]: xApp uses FlexRIC / nearRT-RIC for RC subscription and control-path experiments.
- [Current xApp control proof]: one selected RNTI has xApp/RIC/gNB ACK/apply evidence.
- [Gate E-Core boundary]: the 56 UE A/B run proves dApp marker and access-latency comparison; it does not prove per-UE xApp influence.
- [E3]: `Apps_dev/dapp_dev_need/libe3` is the reference route for dApp-side RAN-role / DAPP-role communication.
- [SWIG status]: definitions exist; generated/importable SWIG runtime modules are not a required PASS for Gate E-Core.

## Guide: Development Workflow

1. Update the Python helper first for fast intent checking.
2. Mirror the same field semantics in the C SDK.
3. Keep the guard boundary intact; do not bypass `redcap_dapp_guard_prb_allocation`.
4. Run the SDK contract self-test:

```bash
python3 agent_doc/Project_management/projects/redcap_dapp_xapp_sdk_test_validation_v1/scripts/dapp_xapp_sdk_contract_selftest.py
```

5. Run the project static checker:

```bash
python3 -B agent_doc/Project_management/projects/redcap_dapp_xapp_sdk_test_validation_v1/scripts/check_dapp_xapp_sdk_test_validation.py
```

6. Run OpenSpec validation:

```bash
openspec validate redcap-dapp-xapp-sdk-test-validation --strict
```

7. For 36 UE pressure evidence, run baseline first, derive `MMTC_DAPP_PRIORITY_UES` with `select_core36_pressure_priority.py`, then validate with `gate_e_64ue_stage_check.py --stage core36-pressure`.
8. For 56 UE runtime evidence, follow [Gate E-Core manual reproduction](./gate_e_core56_manual_reproduction.en.md).

## Reporting Rules

- Do not report static checker PASS as runtime PASS.
- Do not describe KPM as the control path.
- Do not describe Python helpers as SWIG runtime bindings unless a generated/importable module has been verified.
- Do not claim dApp latency improvement from the accepted Gate E-Core run; it is a valid A/B comparison only.
- Every runtime claim must include summary metrics, gNB marker evidence, and the log/report path.

## Examples

- [Beginner build and 29 UE reproduction](../../../../../redcap_doc/manuals/install/redcap_begin_from_zero.en.md)
- [56 UE experiment profile and dApp/xApp reproduction](./gate_e_core56_manual_reproduction.en.md)
- [Adaptive C-DRX A/B manual reproduction](./adaptive_drx_ab_manual_reproduction.en.md)
- [Canonical RedCap L1-L3 function lookup](../../../../../redcap_doc/specs/function_reference/redcap_l1_l3_function_lookup.md)
