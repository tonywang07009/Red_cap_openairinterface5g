# Adaptive C-DRX API and Control Contract

## 1. Scope and Claim Boundary

This document describes the implemented v1 adaptive C-DRX contract for one
RRC_CONNECTED RedCap UE. It covers deterministic traffic input, the Python
predictor, the FlexRIC E2SM-RC request, the in-process C dApp guard, the gNB
RRC/MAC state, UE MAC execution, and campaign evidence.

The live path is:

`Python campaign/xApp -> FlexRIC SWIG -> E2SM-RC -> gNB E2 agent -> in-process C dApp guard -> gNB RRC/MAC -> UE MAC`

There is no E3 transport in this path. RFsim can support DRX activity and
latency proxies; it cannot prove physical UE power consumption.

## 2. Ownership and Direction

| Boundary | Owner | Direction | Authority |
|---|---|---|---|
| Trace and manifest | Campaign generator | File -> runner | Defines the replayable arrival population and Arm A schedule |
| Window statistics and intent | Python predictor | Runner-local | Proposes a profile; it cannot apply radio configuration |
| E2 request ID | FlexRIC | xApp -> E2 node | Runtime correlation key and live `policy_version` |
| RC decode | gNB E2 agent | E2 -> local C | Validates the wire format and approved long-cycle value |
| DRX safety decision | In-process C dApp guard | Local C -> gNB MAC | Final local accept/reject boundary |
| DRX configuration | gNB | gNB -> UE by RRC | Owns the RRC `DRX-Config` values |
| DRX execution | UE MAC | Local UE state | Decides PDCCH monitoring from timers and events |
| Evidence verdict | Campaign checker | CSV/logs -> result | Reports PASS, PARTIAL, BLOCKED, or invalid evidence |

## 3. Deterministic Input Contract

Source: [`adaptive_drx.py`](../../../../../agent_doc/Project_management/projects/redcap_dapp_xapp_sdk_test_validation_v1/scripts/adaptive_drx/adaptive_drx.py#L18), symbols `write_trace()` and `write_campaign_manifest()`.

### 3.1 Frozen Constants

| Field | Value | Validation |
|---|---:|---|
| `schema_version` | `1` | Required by local policy records |
| `arrivals_per_campaign` | `330` | `read_trace()` rejects another row count |
| `warmup_arrivals` | `30` | Not scored; trains the first policy |
| `scored_arrivals` | `300` | Checker requires 300 unique scored rows |
| `arrivals_per_window` | `30` | Predictor refuses a shorter or longer window |
| `minimum_interval_us` | `300000` | Generator clamps and predictor validates |
| `maximum_interval_us` | `10240000` | Generator clamps and predictor validates |
| `control_service_style_id` | `2` | RC decoder requires Style 2 |
| `control_action_id` | `1` | RC decoder requires Action 1 |
| `long_cycle_parameter_id` | `1` | RC decoder requires one Parameter 1 |

### 3.2 Trace CSV Fields

Direction: generator -> campaign runner and checker.

| Field | Owner and meaning | Validation / rollback | Marker |
|---|---|---|---|
| `arrival_id` | Generator; one-based ID `1..330` | Checker requires unique IDs for scored rows | None |
| `window_id` | Generator; zero-based 30-arrival source window | Informational; scored policy windows are one-based elsewhere | None |
| `phase` | Generator; `warmup` or `scored` | Rows 1-30 are warm-up | None |
| `scored_arrival_id` | Generator; blank for warm-up, `1..300` afterward | Informational | None |
| `direction` | Generator; `downlink` or `uplink` | Runner rejects a trace that differs from the campaign | None |
| `traffic_source` | Generator; `iperf_server` for DL, `redcap_ue` for UL | Describes timestamp ownership | None |
| `interval_us` | Generator; inter-arrival duration | Must be within 300 ms..10.24 s | None |
| `scheduled_source_tx_time_us` | Generator; cumulative source schedule | Checker requires exact equality with metrics CSV | None |

The manifest stores the trace `path`, `sha256`, `trace_seed`, and
`start_epoch_us`. `load_campaign()` rejects a checksum or direction mismatch.

### 3.3 Manifest Fields

| Field group | Fields | Owner / rule |
|---|---|---|
| Top level | `schema_version`, `experiment`, `trace_seed`, `claim_boundary`, optional `rebase` | Generator; records reproducibility, source-manifest hash, and the RFsim-only claim boundary |
| Population | `arrivals_per_campaign`, `warmup_arrivals`, `scored_arrivals`, `arrivals_per_window`, `minimum_interval_us`, `maximum_interval_us` | Frozen v1 experiment shape |
| Traffic | `tool`, `transport`, `bytes_per_burst`, `payload_bytes`, `target_bitrate_bps`, `schedule_option`, `latency_option` | Fixed iPerf2 UDP burst contract |
| Campaign | `id`, `arm`, `direction`, `trace`, `control_mode`, `required_markers` | Selects one of Arm A/B and DL/UL |
| Arm A | `initial_profile`, `baseline_policy_version` | Fixed `drx-320-10`, version 1, applied once for all 300 scored arrivals |
| Arm B | `initial_profile` | Fixed `drx-320-10`; runner commits reserved bootstrap version 0 on fresh DRX state |
| Profiles | `approved_profiles[]`: `profile_id`, `long_cycle_ms`, `on_duration_ms` | Six legal v1 profile pairs |

## 4. Python Predictor and Local Policy Record

Source: [`adaptive_drx.py`](../../../../../agent_doc/Project_management/projects/redcap_dapp_xapp_sdk_test_validation_v1/scripts/adaptive_drx/adaptive_drx.py#L34).

### 4.1 `DrxProfile`

| Field | Meaning | Validation |
|---|---|---|
| `profile_id` | Stable local profile name | Must be one of the six approved profiles |
| `long_cycle_ms` | Candidate long DRX cycle | `320`, `640`, `1280`, `2560`, `5120`, or `10240` |
| `on_duration_ms` | Locally paired On Duration | `10`, `20`, or `40`, fixed by the profile table |

### 4.2 `WindowStatistics`

All fields are Python-local JSON evidence and are not encoded over E2.

| Field | Meaning | Validation |
|---|---|---|
| `sample_count` | Number of committed intervals | Exactly `30` |
| `mean_interval_us` | Arithmetic mean | `statistics.fmean()` |
| `stddev_interval_us` | Sample standard deviation | `statistics.stdev()` |
| `lower_3sigma_us` | Mean minus three standard deviations | Used for profile selection |
| `upper_3sigma_us` | Mean plus three standard deviations | Outside 10.24 s forces fallback before E2 submission |
| `median_interval_us` | Median | Descriptive evidence |
| `p95_interval_us` | Nearest-rank p95 | Sorted item at `ceil(0.95*N)-1` |
| `minimum_interval_us` | Minimum sample | Descriptive evidence |
| `maximum_interval_us` | Maximum sample | Descriptive evidence |

### 4.3 `PolicyIntent`

Direction: predictor -> command JSONL/local correlation. Only UE identity and
the selected long cycle reach the live SWIG call.

| Field | Owner and meaning | Validation / rollback |
|---|---|---|
| `schema_version` | Predictor; local schema `1` | Rich dApp guard can validate it, but that guard is not live |
| `campaign_id` | Runner-selected campaign | Must match the manifest |
| `direction` | `downlink` or `uplink` | Predictor rejects other values |
| `window_id` | One-based scored policy window | Runner creates ten windows |
| `policy_version` | Planned local window version | Replaced by the FlexRIC RIC request ID during execution |
| `ric_request_id` | Planned local correlation value | Replaced by the FlexRIC RIC request ID during execution |
| `rnti` | Misnamed local identity field | Arm B stores `--rrc-ue-id`, not authoritative C-RNTI `[Needs Verification]` |
| `sample_count` | Committed history size | Fixed at `30` |
| `prediction_status` | `predicted`, `fallback`, or `zero_variance` | Records selection outcome |
| `selected_profile_id` | Proposed profile | Must be approved |
| `previous_profile_id` | Runner's last committed profile label | Must be approved; not a gNB state readback |
| `valid_for_arrivals` | Forecast horizon | Fixed at `30` |
| `short_drx_enabled` | Local v1 constant | `false` |
| `drx_inactivity_timer_ms` | Local v1 constant | `20` |
| `drx_slot_offset_1_over_32_ms` | Local v1 constant | `0` |
| Statistics fields | Flattened `WindowStatistics` | JSON-only in the live path |
| `e2sm_rc_request` | Human-readable request metadata | Not the object passed to FlexRIC |

`AdaptiveDrxPredictor.resolve(true)` clears the 30 samples. A reject or timeout
calls `resolve(false)`, removes only the pending decision, and retains the
sample window. The runner then returns PARTIAL rather than continuing.

## 5. E2SM-RC and SWIG Contract

Sources: [`redcap_xapp_sdk.c`](../../../../../openair2/E2AP/REDCAP_SDK/xapp/redcap_xapp_sdk.c#L48), [`swig_wrapper.cpp`](../../../../../openair2/E2AP/flexric/src/xApp/swig/swig_wrapper.cpp#L459), and [`ran_func_rc_redcap.c`](../../../../../openair2/E2AP/RAN_FUNCTION/O-RAN/ran_func_rc_redcap.c#L51).

### 5.1 Live SWIG API

```c
uint32_t control_drx_sm(global_e2_node_id_t *id,
                        uint64_t rrc_ue_id,
                        uint16_t long_cycle_ms);
```

| Field | Direction | Validation | Return / marker |
|---|---|---|---|
| `id` | Python -> SWIG | Non-null E2 node | `0` on local construction failure |
| `rrc_ue_id` | Python -> RC header | Positive; encoded as GNB UE `ran_ue_id` | Resolved to C-RNTI in the gNB |
| `long_cycle_ms` | Python -> RC Parameter 1 | One of six approved cycles | E2 ACK includes the decoded value |
| return value | FlexRIC -> Python | Generated RIC request ID on transport success | `0` otherwise |

### 5.2 Fields Actually Encoded over E2

| RC location | Field | Required value |
|---|---|---|
| Header | `format` | `FORMAT_1_E2SM_RC_CTRL_HDR` |
| Header | `ue_id.type` | `GNB_UE_ID_E2SM` or decoder-supported `GNB_DU_UE_ID_E2SM` |
| Header | `ue_id.*.ran_ue_id` | Non-null, non-zero RRC UE identity |
| Header | `ric_style_type` | `2` |
| Header | `ctrl_act_id` | `1` |
| Message | `format` | `FORMAT_1_E2SM_RC_CTRL_MSG` |
| Message | `sz_ran_param` | Exactly `1` |
| Parameter | `ran_param_id` | `1` |
| Parameter | value kind | Element-key true, integer RAN parameter |
| Parameter | integer value | Approved `long_cycle_ms` |

`policy_version`, prediction statistics, profile ID, On Duration, inactivity,
start offset, and rollback data are not E2 RAN parameters. FlexRIC generates
the RIC request ID starting at one, copies it through the agent, and the live
gNB path uses it as `policy_version`.

`[RedCap DRX][xApp request]` and `[RedCap DRX][E2 ACK]` are printed by the gNB
RC handler. The latter proves decode acceptance, not dApp or RRC application.

## 6. C dApp Guard Contract

Sources: [`redcap_dapp_sdk.h`](../../../../../openair2/E3AP/sdk/redcap_dapp_sdk.h#L87) and [`redcap_dapp_sdk.c`](../../../../../openair2/E3AP/sdk/redcap_dapp_sdk.c#L202).

### 6.1 Live Narrow E2 Request: `redcap_dapp_e2_drx_cycle_request_t`

The live RC path calls `redcap_dapp_guard_e2_drx_cycle()` with this request and the current applied configuration.

| Field | Owner / direction | Validation |
|---|---|---|
| `rnti` | gNB lookup -> dApp | Non-zero resolved C-RNTI |
| `policy_version` | FlexRIC RIC request ID -> dApp | Non-zero and newer than current |
| `requested_long_cycle_ms` | E2 decode -> dApp | Must map to an approved profile |
| `ue_connected` | gNB state snapshot -> dApp | Must be true |
| `rrc_reconfiguration_cooldown_elapsed` | gNB state snapshot -> dApp | No pending CellGroup or RRC completion |

The guard additionally requires a valid current profile with
`rollback_available=true`, matching C-RNTI, legal offset/profile pair, and
20 ms inactivity. On acceptance it selects On Duration locally, uses start
offset zero, disables short DRX and DRX Command, and returns dApp ACCEPT.

### 6.2 Rich Local Request: `redcap_dapp_drx_policy_request_t`

`redcap_dapp_guard_drx_policy()` is covered by the C unit test but has no live caller.

| Field | Validation |
|---|---|
| `schema_version` | Must equal `REDCAP_DAPP_DRX_SCHEMA_VERSION` (`1`) |
| `rnti` | Non-zero and matches rollback profile |
| `policy_version` | Newer than current |
| `sample_count` | Exactly `30` |
| `lower_3sigma_us` | At least `300000`; selects the largest eligible profile |
| `upper_3sigma_us` | At most `10240000` and not below the lower bound |
| `next_arrival_drx_epoch_ms` | Used modulo long cycle to derive start offset |
| `requested_long_cycle_ms` | Must equal the profile selected from lower 3-sigma |
| `ue_connected` | Must be true |
| `rrc_reconfiguration_cooldown_elapsed` | Must be true |

### 6.3 Accepted Configuration and Guard Result

| Structure / field | Meaning | Rollback behavior |
|---|---|---|
| `redcap_dapp_drx_config_t.rnti` | Target C-RNTI | Must match saved current state |
| `.policy_version` | Accepted version | gNB rejects stale staging |
| `.long_cycle_ms` | Approved cycle | Stored in gNB applied/previous state |
| `.on_duration_ms` | Approved local pair | Stored in gNB applied/previous state |
| `.start_offset_ms` | Cycle offset | Live E2 path uses `0` |
| `.inactivity_ms` | Inactivity timer | Fixed at `20` |
| `.rollback_available` | Guard proof | Required for apply |
| `.drx_command_enabled` | Optional CE feature flag | Disabled by both dApp guards |
| `.profile_id` | Local profile label | Not copied into gNB profile |
| `guard_result.decision` | ACK or NACK | Apply only on ACK |
| `guard_result.accepted` | Candidate configuration | Converted to `nr_gnb_drx_profile_t` |
| `guard_result.previous` | Snapshot returned by guard | Not itself persisted by the caller |
| `guard_result.reason` | `ack` or reject reason | Printed in dApp marker |
| `guard_result.marker` | ACCEPT or REJECT marker | Runtime evidence |

Reject reasons implemented across decode, guard, and apply include
`e2_decode_error`, `unsupported_long_cycle`, `unknown_rnti`,
`ue_not_connected`, `stale_policy_version`, `cooldown_active`,
`rollback_unavailable`, `prediction_out_of_bounds`, `sample_count_not_30`,
`invalid_schema_version`, `unsupported_node_role`, and `gnb_apply_failed`.

## 7. gNB RRC/MAC and UE MAC Contract

### 7.1 `nr_gnb_drx_profile_t`

Source: [`nr_mac_drx.h`](../../../../../openair2/LAYER2/NR_MAC_gNB/nr_mac_drx.h#L21).

| Field | Validation | RRC mapping |
|---|---|---|
| `policy_version` | Monotonically newer when configured | Local correlation only |
| `long_cycle_ms` | Approved pair | `drx-LongCycleStartOffset` choice |
| `on_duration_ms` | Approved pair | Integer-ms `drx-onDurationTimer` |
| `inactivity_ms` | Exactly `20` | `drx-InactivityTimer=ms20` |
| `start_offset_ms` | Less than long cycle | Long-cycle choice value |
| `drx_command_enabled` | Local feature flag | Not an RRC field |

The producer also fixes HARQ RTT DL/UL to four symbols, retransmission DL/UL
to eight slots, `shortDRX=NULL`, and `drx-SlotOffset=0`; see
[`update_cellGroupConfig_for_drx()`](../../../../../openair2/LAYER2/NR_MAC_gNB/nr_radio_config.c#L4267).

### 7.2 Apply and Rollback

1. `nr_mac_apply_drx_policy()` validates the profile and target UE.
2. `trigger_drx_reconfiguration()` clones and encodes `CellGroupConfig`, stages
   the profile, marks RRC completion pending, and sends the DU-to-CU request.
3. A successful RRC transport commit moves `pending` to `applied` and saves the
   old `applied` value as `previous`.
4. RRC completion clears the cooldown and emits versioned success evidence.
5. A failed completion cancels an uncommitted candidate or restores the saved
   previous profile and CellGroup, then emits rollback and failure evidence.

Automatic rollback is implemented in
[`mac_rrc_dl_handler.c`](../../../../../openair2/LAYER2/NR_MAC_gNB/mac_rrc_dl_handler.c#L767).
The explicit `nr_mac_rollback_drx_policy()` API exists but has no caller.

### 7.3 UE Execution State

The UE decodes RRC fields into `nr_drx_config_t`: On Duration, inactivity,
HARQ RTT and retransmission timers, long/short cycle, offsets, monotonic clock,
and per-HARQ state. `nr_ue_drx_is_active_slot()` returns active for pending SR,
inactivity, HARQ retransmission windows, or On Duration. The UE scheduler only
configures DCI monitoring while active. DRX and Long DRX MAC CEs stop the
current active deadline and select the next short/long-cycle transition.

## 8. Runtime Evidence Contract

Source: [`run_campaign.py`](../../../../../agent_doc/Project_management/projects/redcap_dapp_xapp_sdk_test_validation_v1/scripts/adaptive_drx/run_campaign.py#L176) and [`check_campaign.py`](../../../../../agent_doc/Project_management/projects/redcap_dapp_xapp_sdk_test_validation_v1/scripts/adaptive_drx/check_campaign.py#L17).

Runtime execution requires `--bind-address` to identify the UE PDU-session
source address. `iperf_command()` maps it to iPerf2 `-B`; omission is
`[BLOCKED]` because container `eth0` could otherwise bypass the NR tunnel.

### 8.1 Metrics CSV Fields

| Field | Meaning | Checker rule |
|---|---|---|
| `campaign_id` | Selected campaign | Exact match |
| `arrival_id` | Trace row | 300 unique scored IDs required |
| `scheduled_source_tx_time_us` | Source schedule | Exact trace correlation |
| `delivery_success` | iPerf process return success | Counted as truthy/falsey |
| `policy_version` | Committed FlexRIC/local version | Ten versions, 30 rows each |
| `profile_id` | Runner's committed profile label | Approved and one per window |
| `client_launch_time_us` | Client process launch time | Recorded but not checked |
| `iperf_returncode` | Process return code | Recorded but not checked separately |

The command JSONL additionally records `arm`, `direction`, `traffic_source`,
the complete command, `executed`, optional flattened control intent,
`returncode`, `stdout`, and `stderr`. A failed control persists the trace hash,
arrival range, and all 30 retained intervals for deterministic retry.

### 8.2 Runtime Markers

| Marker | Producer | Meaning / correlation |
|---|---|---|
| `[RedCap DRX][xApp request]` | gNB RC handler | Style/action recognized; versioned |
| `[RedCap DRX][E2 ACK]` | gNB RC handler | RC fields decoded; versioned |
| `[RedCap DRX][dApp ACCEPT]` | In-process guard caller | Local safety guard passed; versioned |
| `[RedCap DRX][dApp REJECT]` | Decode/guard/apply path | Reason-coded; some early forms lack version |
| `[RedCap DRX][gNB staged]` | gNB MAC | RRC candidate encoded and staged; versioned |
| `[RedCap DRX][gNB applied]` | gNB MAC | Applied cycle and On Duration; versioned and profile-checked |
| `Configured Connected DRX` | UE MAC | UE decoded a DRX config; not versioned |
| `Received RRCReconfigurationComplete` | gNB RRC | CU received UE completion; not versioned |
| `[RedCap DRX][RRC complete]` | gNB DU MAC | Versioned success/failure commit marker |
| `[RedCap DRX][rollback]` | gNB MAC | Previous configuration restored or explicit rollback staged |
| `[RedCap DRX][DRX Command requested]` | gNB local API | One-shot command requested |
| `[RedCap DRX][DRX Command]` | gNB scheduler | Zero-length MAC CE emitted |
| `[RedCap DRX][control timeout]` | Runner/checker | Required versioned marker chain incomplete |
| `[RedCap DRX][UE stats]` | UE `ciUE` module | Scored observed/active slots and v1 PDCCH-monitoring proxy |

## 9. Required `[Needs Verification]` Boundaries

1. The integer value used for E2SM-RC Long DRX Cycle Length still requires an
   exact TS 38.473 encoding check.
2. `PolicyIntent.rnti` contains `rrc_ue_id` in Arm B. The authoritative C-RNTI
   is resolved only inside the gNB.
3. Statistics, prediction quality, profile IDs, and planned version are
   JSON-only. The live E2 path calls the narrow cycle guard, not the rich
   statistics-aware guard. Statistical quality is therefore xApp-owned in v1;
   the dApp owns legal/state safety.
4. The live E2 path fixes start offset to zero. Predicted-arrival/SFN alignment
   remains unimplemented.
5. A FlexRIC control ACK does not report the dApp outcome. Runtime commit must
   be inferred from the complete marker chain.
6. The checker correlates the versioned custom RRC marker, but the UE config
   and ordinary RRC completion strings are only required globally.
7. The collectors and checker now support receiver latency, iPerf metrics,
   HARQ deltas, policy latency, and UE Active-Time ratios, but no four-campaign
   RFsim result has been collected yet.
8. Automatic failure rollback exists, but no dApp rollback-decision marker
    or live caller of `nr_mac_rollback_drx_policy()` exists.
