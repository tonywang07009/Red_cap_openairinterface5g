# Adaptive C-DRX Trace Code Guide

## 1. How to Use This Guide

Follow one `policy_version` from the generated trace to the checker. At every
step, confirm the named input, output, and marker before moving to the next
source location. Runtime `policy_version` is the FlexRIC RIC request ID, not
necessarily the predictor's planned window number.

## 2. End-to-End Source Route

| Step | Source and symbol | Input | Output | Expected marker | Next trace point |
|---:|---|---|---|---|---|
| 1 | [`adaptive_drx.py:92`](../../../../../agent_doc/Project_management/projects/redcap_dapp_xapp_sdk_test_validation_v1/scripts/adaptive_drx/adaptive_drx.py#L92), `_stable_direction_seed()` | Trace seed, DL/UL direction | Stable direction-specific seed | None | `generate_intervals()` |
| 2 | [`adaptive_drx.py:105`](../../../../../agent_doc/Project_management/projects/redcap_dapp_xapp_sdk_test_validation_v1/scripts/adaptive_drx/adaptive_drx.py#L105), `generate_intervals()` | Stable seed, eleven window means | 330 bounded inter-arrival values | None | `write_trace()` |
| 3 | [`adaptive_drx.py:119`](../../../../../agent_doc/Project_management/projects/redcap_dapp_xapp_sdk_test_validation_v1/scripts/adaptive_drx/adaptive_drx.py#L119), `write_trace()` | Intervals and start epoch | Direction-owned trace CSV | None | `write_campaign_manifest()` |
| 4 | [`adaptive_drx.py:162`](../../../../../agent_doc/Project_management/projects/redcap_dapp_xapp_sdk_test_validation_v1/scripts/adaptive_drx/adaptive_drx.py#L162), `write_campaign_manifest()` | Trace/profile seeds | Four campaign records, checksums, profiles | None | `load_campaign()` |
| 5 | [`run_campaign.py:53`](../../../../../agent_doc/Project_management/projects/redcap_dapp_xapp_sdk_test_validation_v1/scripts/adaptive_drx/run_campaign.py#L53), `load_campaign()` | Manifest and campaign ID | Verified campaign and 330 rows | BLOCKED/exception on invalid evidence | Main campaign loop |
| 6 | [`run_campaign.py:31`](../../../../../agent_doc/Project_management/projects/redcap_dapp_xapp_sdk_test_validation_v1/scripts/adaptive_drx/run_campaign.py#L31), `iperf_command()` | Trace row and server address | Fixed-byte UDP command; DL adds `-R` | None | `subprocess.run()` |
| 7 | [`adaptive_drx.py:306`](../../../../../agent_doc/Project_management/projects/redcap_dapp_xapp_sdk_test_validation_v1/scripts/adaptive_drx/adaptive_drx.py#L306), `AdaptiveDrxPredictor.observe()` | One `interval_us` after a burst | Retained 30-sample history | None | `propose()` at next boundary |
| 8 | [`adaptive_drx.py:245`](../../../../../agent_doc/Project_management/projects/redcap_dapp_xapp_sdk_test_validation_v1/scripts/adaptive_drx/adaptive_drx.py#L245), `summarize_window()` | Exactly 30 bounded intervals | Mean, sample sigma, +/-3 sigma, median, p95, min/max | None | `select_profile()` |
| 9 | [`adaptive_drx.py:266`](../../../../../agent_doc/Project_management/projects/redcap_dapp_xapp_sdk_test_validation_v1/scripts/adaptive_drx/adaptive_drx.py#L266), `select_profile()` | `lower_3sigma_us` | Largest approved cycle not above the lower bound, or fallback | None | `AdaptiveDrxPredictor.propose()` |
| 10 | [`adaptive_drx.py:313`](../../../../../agent_doc/Project_management/projects/redcap_dapp_xapp_sdk_test_validation_v1/scripts/adaptive_drx/adaptive_drx.py#L313), `propose()` | Campaign/window IDs, UE identity, previous profile | Local `PolicyIntent` and JSON request description | JSON `[xApp request]` label only | Runner control branch |
| 11 | [`run_campaign.py:193`](../../../../../agent_doc/Project_management/projects/redcap_dapp_xapp_sdk_test_validation_v1/scripts/adaptive_drx/run_campaign.py#L193), window-control branch | Policy intent or seeded Arm A profile | Profile selected for the next 30 scored arrivals | None | Local telnet or SWIG |
| 12A | [`run_campaign.py:91`](../../../../../agent_doc/Project_management/projects/redcap_dapp_xapp_sdk_test_validation_v1/scripts/adaptive_drx/run_campaign.py#L91), `_send_local_drx_policy()` | Arm A version, C-RNTI, full profile | `ci trigger_drx_policy ...` over local telnet | gNB staged/applied | Step 20 |
| 12B | [`run_campaign.py:226`](../../../../../agent_doc/Project_management/projects/redcap_dapp_xapp_sdk_test_validation_v1/scripts/adaptive_drx/run_campaign.py#L226), `ric.control_drx_sm()` | Arm B node, RRC UE ID, long cycle | FlexRIC-generated RIC request ID | None at caller | SWIG wrapper |
| 13 | [`swig_wrapper.cpp:459`](../../../../../openair2/E2AP/flexric/src/xApp/swig/swig_wrapper.cpp#L459), `control_drx_sm()` | E2 node, `rrc_ue_id`, cycle | Synchronous RC control and returned request ID | Generic FlexRIC response | C xApp request builder |
| 14 | [`redcap_xapp_sdk.c:86`](../../../../../openair2/E2AP/REDCAP_SDK/xapp/redcap_xapp_sdk.c#L86), `redcap_xapp_make_drx_ctrl_req()` | RRC UE ID and approved cycle | RC Format 1 header/message, Style 2, Action 1, Parameter 1 | None | `control_sm_xapp_api()` |
| 15 | [`msg_handler_agent.c:272`](../../../../../openair2/E2AP/flexric/src/agent/msg_handler_agent.c#L272), `e2ap_handle_control_request_agent()` | E2 control request | Request ID plus encoded RC buffers passed to service model | Generic E2 control acknowledge | `on_control_rc_sm_ag()` |
| 16 | [`rc_sm_agent.c:133`](../../../../../openair2/E2AP/flexric/src/sm/rc_sm/rc_sm_agent.c#L133), `on_control_rc_sm_ag()` | Request ID and RC buffers | Decoded `rc_ctrl_req_data_t` | None | `write_ctrl_rc_sm()` |
| 17 | [`ran_func_rc.c:1070`](../../../../../openair2/E2AP/RAN_FUNCTION/O-RAN/ran_func_rc.c#L1070), `write_ctrl_rc_sm()` | Decoded RC request | Style/action dispatch and cycle decode | `[xApp request]`, then `[E2 ACK]` | `apply_redcap_drx_control()` |
| 18 | [`ran_func_rc_redcap.c:51`](../../../../../openair2/E2AP/RAN_FUNCTION/O-RAN/ran_func_rc_redcap.c#L51), `nr_redcap_parse_drx_ctrl_message()` | RC Format 1 header/message | `rrc_ue_id` plus approved `long_cycle_ms` | dApp REJECT on decode failure | gNB UE lookup |
| 19 | [`ran_func_rc.c:89`](../../../../../openair2/E2AP/RAN_FUNCTION/O-RAN/ran_func_rc.c#L89), `find_redcap_ue_by_rrc_id()` | RRC UE ID | `NR_UE_info_t` and authoritative C-RNTI | dApp REJECT if unresolved | Guard snapshot |
| 20 | [`ran_func_rc.c:99`](../../../../../openair2/E2AP/RAN_FUNCTION/O-RAN/ran_func_rc.c#L99), `apply_redcap_drx_control()` | Cycle, RIC request ID, UE state | Narrow dApp request and accepted gNB profile | `[dApp ACCEPT]` or `[dApp REJECT]` | `nr_mac_apply_drx_policy()` |
| 21 | [`redcap_dapp_sdk.c:311`](../../../../../openair2/E3AP/sdk/redcap_dapp_sdk.c#L311), `redcap_dapp_guard_e2_drx_cycle()` | C-RNTI, version, cycle, connected/cooldown/current state | Approved cycle/On Duration pair, offset 0, inactivity 20 | Marker returned to step 20 | gNB profile conversion |
| 22 | [`gNB_scheduler_primitives.c:4150`](../../../../../openair2/LAYER2/NR_MAC_gNB/gNB_scheduler_primitives.c#L4150), `nr_mac_apply_drx_policy()` | C-RNTI and `nr_gnb_drx_profile_t` | Locked target UE and reconfiguration attempt | gNB reject on unknown UE | `trigger_drx_reconfiguration()` |
| 23 | [`gNB_scheduler_primitives.c:4092`](../../../../../openair2/LAYER2/NR_MAC_gNB/gNB_scheduler_primitives.c#L4092), `trigger_drx_reconfiguration()` | Current CellGroup and accepted profile | Encoded candidate, staged state, DU-to-CU RRC information | `[gNB staged]` or `[gNB reject]` | RRC delivery |
| 24 | [`nr_radio_config.c:4267`](../../../../../openair2/LAYER2/NR_MAC_gNB/nr_radio_config.c#L4267), `update_cellGroupConfig_for_drx()` | Current CellGroup and profile | RRC DRX setup with fixed inactivity/HARQ/short-DRX values | None | UE RRC decoder |
| 25 | [`rrc_UE.c:1022`](../../../../../openair2/RRC/NR_UE/rrc_UE.c#L1022), `nr_rrc_ue_process_masterCellGroup()` | Encoded master CellGroup | Decoded CellGroup queued to UE MAC | CellGroup debug markers | `nr_rrc_mac_config_req_cg()` |
| 26 | [`config_ue.c:3288`](../../../../../openair2/LAYER2/NR_MAC_UE/config_ue.c#L3288), `nr_rrc_mac_config_req_cg()` | Decoded CellGroup | MAC CellGroup applied | Applying CellGroupConfig | `configure_drx()` |
| 27 | [`config_ue.c:2647`](../../../../../openair2/LAYER2/NR_MAC_UE/config_ue.c#L2647), `configure_drx()` | RRC `DRX-Config` and SCS | Slot-based `nr_drx_config_t` | `Configured Connected DRX` | UE Active Time |
| 28 | [`nr_ue_drx.c:111`](../../../../../openair2/LAYER2/NR_MAC_UE/nr_ue_drx.c#L111), `nr_ue_drx_is_active_slot()` | Slot, SR, inactivity and HARQ timers | Active/sleep decision | None | UE PDCCH gate |
| 29 | [`nr_ue_scheduler.c:1169`](../../../../../openair2/LAYER2/NR_MAC_UE/nr_ue_scheduler.c#L1169), `nr_ue_dl_scheduler()` | UE state and current slot | DCI monitoring configured only in Active Time | None | Assignment event hooks |
| 30 | [`nr_ue_drx.c:173`](../../../../../openair2/LAYER2/NR_MAC_UE/nr_ue_drx.c#L173), assignment/HARQ hooks | New DL/UL grants and HARQ outcomes | Inactivity and retransmission deadlines | None | Next Active-Time evaluation |
| 31 | [`nr_mac_drx.c:62`](../../../../../openair2/LAYER2/NR_MAC_gNB/nr_mac_drx.c#L62), stage/commit/complete state | Profile and RRC outcomes | `pending -> applied`, saved `previous`, cleared cooldown | `[gNB applied]` | RRC completion |
| 32 | [`rrc_gNB.c:1973`](../../../../../openair2/RRC/NR/rrc_gNB.c#L1973), `handle_rrcReconfigurationComplete()` | UE RRC complete | F1 success indication to DU | `Received RRCReconfigurationComplete` | DU completion handler |
| 33 | [`mac_rrc_dl_handler.c:767`](../../../../../openair2/LAYER2/NR_MAC_gNB/mac_rrc_dl_handler.c#L767), completion branch | F1 success/failure | Commit completion or automatic restore | `[RRC complete]`, optional `[rollback]` | Runner commit wait |
| 34 | [`run_campaign.py:73`](../../../../../agent_doc/Project_management/projects/redcap_dapp_xapp_sdk_test_validation_v1/scripts/adaptive_drx/run_campaign.py#L73), `_wait_for_commit()` | Runtime log and request ID | Success only after full versioned marker chain | `[control timeout]` on expiry | `predictor.resolve()` |
| 35 | [`run_campaign.py:241`](../../../../../agent_doc/Project_management/projects/redcap_dapp_xapp_sdk_test_validation_v1/scripts/adaptive_drx/run_campaign.py#L241), resolve/record branch | Commit result | Clear samples on success; retain on failure; JSONL/CSV evidence | PASS/PARTIAL | Checker |
| 36 | [`check_campaign.py:43`](../../../../../agent_doc/Project_management/projects/redcap_dapp_xapp_sdk_test_validation_v1/scripts/adaptive_drx/check_campaign.py#L43), `check()` | Manifest, metrics CSV, runtime logs | Population, version, profile and marker issues | PASS or PARTIAL | Gate report |

## 3. Success Marker Sequence

For Arm B, search the combined runtime log in this order using the same
`policy_version`:

1. `[RedCap DRX][xApp request]`
2. `[RedCap DRX][E2 ACK]`
3. `[RedCap DRX][dApp ACCEPT]`
4. `[RedCap DRX][gNB staged]` (diagnostic; not required by the checker)
5. `[RedCap DRX][gNB applied]` with expected `cycle_ms` and `on_duration_ms`
6. `Configured Connected DRX` (UE marker; not versioned)
7. `Received RRCReconfigurationComplete` (ordinary gNB RRC marker; not versioned)
8. `[RedCap DRX][RRC complete] ... outcome success`

The E2 ACK alone is not a commit. The runner clears the predictor window only
after steps 1-3, 5, and 8 correlate by runtime request ID.

## 4. Failure and Rollback Route

| Condition | Source | State action | Evidence |
|---|---|---|---|
| Decode/guard reject | `ran_func_rc.c` / `redcap_dapp_sdk.c` | No gNB staging | dApp REJECT with reason; later control timeout |
| Candidate encode/stage failure | `gNB_scheduler_primitives.c` | Candidate freed; applied profile unchanged | gNB reject or dApp REJECT `gnb_apply_failed` |
| RRC failure before commit | `nr_mac_drx_fail_reconfiguration()` | Cancel pending candidate | rollback and RRC failure markers |
| RRC failure after commit | `mac_rrc_dl_handler.c` | Restore `previous` profile and CellGroup | `[rollback]` plus versioned failure |
| Missing completion marker | `run_campaign._wait_for_commit()` | Predictor retains the 30 samples | `[control timeout]`, PARTIAL |

`nr_mac_rollback_drx_policy()` in
[`gNB_scheduler_primitives.c:4164`](../../../../../openair2/LAYER2/NR_MAC_gNB/gNB_scheduler_primitives.c#L4164)
can stage the saved profile under a new version, but no live dApp/E2 caller is
implemented.

## 5. Optional DRX Command Route

This route is separate from DRX reconfiguration and is disabled by both live
dApp guards.

1. [`nr_mac_request_drx_command()`](../../../../../openair2/LAYER2/NR_MAC_gNB/gNB_scheduler_primitives.c#L4187) creates one request and emits `[DRX Command requested]`.
2. [`nr_gnb_drx_note_dl_ack()`](../../../../../openair2/LAYER2/NR_MAC_gNB/nr_mac_drx.c#L190) arms it only after a successful DL HARQ ACK while Active Time remains.
3. [`nr_gnb_drx_command_ready()`](../../../../../openair2/LAYER2/NR_MAC_gNB/nr_mac_drx.c#L262) requires no pending SR, no retransmission work, empty queues, completed RRC configuration, and Active Time.
4. [`post_process_dlsch()`](../../../../../openair2/LAYER2/NR_MAC_gNB/gNB_scheduler_dlsch.c#L1088) writes the zero-length DL MAC CE and emits `[DRX Command]`.
5. [`nr_ue_process_mac_pdu()`](../../../../../openair2/LAYER2/NR_MAC_UE/nr_ue_procedures.c#L4110) recognizes DRX/Long DRX LCID and calls `nr_ue_drx_on_command()`.
6. [`nr_ue_drx_on_command()`](../../../../../openair2/LAYER2/NR_MAC_UE/nr_ue_drx.c#L245) ends the current active deadline and chooses the next short/long-cycle transition.

The command does not change long cycle, On Duration, or RRC configuration.

## 6. Stop Points and `[Needs Verification]`

- Stop before claiming a live Arm B pass if the fallback baseline has not been
  installed at the gNB; the manifest `initial_profile` is Python-local only.
- Treat `PolicyIntent.rnti` as a misnamed RRC UE correlation value. Continue to
  `find_redcap_ue_by_rrc_id()` for authoritative C-RNTI.
- Do not trace prediction statistics into the E2 packet; they remain JSON-only.
- Do not claim upper-bound fallback enforcement; live selection uses only
  `lower_3sigma_us`.
- Do not claim predicted start-offset alignment; the live E2 guard uses zero.
- Do not infer latency, goodput, loss, HARQ, or monitoring-time metrics from
  the current CSV. Those fields are not produced.
- Keep the TS 38.473 integer mapping marked `[Needs Verification]`.

