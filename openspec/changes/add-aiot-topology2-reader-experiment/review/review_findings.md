# A-IoT Topology 2 Reader Review Findings

## Review Status

| Item | Result |
|---|---|
| Phase | Implementation and five-layer runtime ladder complete; PF/PO/timer focused check complete; NR MAC/over-the-air paging remains `[Needs Verification]` |
| Readiness | CONDITIONAL: deterministic RFsim and AIOTF state paths pass; physical RF/beam and direct UDP-to-AIOTF correlation are not proven |
| Scope | one gNB/logical CW source, one single-tag radio transaction, two RedCap UE Readers, and a serialized 60-Tag AIOTF profile |
| Selected profile | `review/aiot_topology2_reader_profile_v1.yaml` |
| Claim boundary | protocol and RFsim experiment profile; not full 3GPP A-IoT compliance |

## Standards Matrix

| Requirement | Specification and clause | Local source | Interpretation | Status |
|---|---|---|---|---|
| Topology 2 control | TR 38.769 V19.0.0, clauses 6.1.5 and 6.4.2 | `redcap_doc/specs/A_IoT/TR38769.pdf` | gNB controls an intermediate UE over NR Uu; the UE owns the Common reader function | Verified |
| UE Reader resource validity | TR 38.769 V19.0.0, clause 6.3.6 | `redcap_doc/specs/A_IoT/TR38769.pdf` | the network controls the A-IoT radio resources; the UE Reader operates only while its dedicated resource configuration is valid | Verified |
| UE Reader architecture | TS 23.369 V20.0.0, clauses 4.2.3, 6.2.10.8, and 6.2.10.9 | `redcap_doc/specs/A_IoT/TS23369.pdf` | UE Reader uses RRC to NG-RAN, NGAP to AMF, and SBI to AIOTF | Verified |
| D2R PHY and backscatter | TS 38.291 V19.3.0, clauses 6.1, 6.1.5, 7.1, and 8.4 | `redcap_doc/specs/A_IoT/TS38291_PHY.pdf` | D2R uses PDRCH, CRC, optional repetition/coding, D2R amble, small-frequency-shift modulation, and multiplication with an external CW | Verified |
| R2D line encoding | TS 38.291 V19.3.0, clauses 6.2.2.2 and 8.5 | `redcap_doc/specs/A_IoT/TS38291_PHY.pdf` | the formula maps `0 -> 10` and `1 -> 01` | Verified |
| D2R MAC size | TS 38.391 V19.3.0, clauses 5.4 and 6.2.1.6 | `redcap_doc/specs/A_IoT/TS38391_MAC.pdf` | standard D2R TBS supports 1 to 125 bytes; v1 deliberately caps the payload at 16 bytes and disables segmentation | Verified profile restriction |
| CRC | TS 38.291 V19.3.0, clauses 6.1.2.1, 6.2.2.1, and 8.1 | `redcap_doc/specs/A_IoT/TS38291_PHY.pdf` | use CRC6 when payload is at most 24 bits and CRC16 otherwise | Verified |
| CW waveform | TS 38.194 V19.0.0, clauses 8.1 to 8.4 | `redcap_doc/specs/A_IoT/TS_138_194(CW_BS).pdf` | CW is a single-tone unmodulated sinusoid; its absolute RF power requirements are outside RFsim v1 evidence | Verified; RF calibration excluded |
| D2R Manchester | No normative D2R line-encoding clause was found in TS 38.291 | `redcap_doc/specs/A_IoT/TS38291_PHY.pdf` | v1 inserts the R2D mapping into D2R as a namespaced experimental transform; it is not advertised as standard behavior | Experimental deviation |
| UE sleep interaction | TR 38.769 establishes network-controlled resource validity but does not define this experiment's 100 ms response timeout or DRX wake policy | local experiment contract | R2D is forbidden while the UE Reader is asleep; timeout is an experimental bound | [Needs Verification] |

## Trace-Code Guide

| Boundary | Source symbol | Input to output | State owner | Expected marker | Next trace point | Status |
|---|---|---|---|---|---|---|
| RFsim role routing | `radio/rfsimulator/simulator.cpp`: `aiot_t2_handle_packet()` | tagged CW/R2D/D2R packet to role-filtered peer relay | RFsim server | `AIOT_T2_R2D_RELAY`, `AIOT_T2_D2R_RELAY` | `aiot_t2_relay_packet()` | Implemented, profile-scoped |
| UE RF control seam | `radio/rfsimulator/simulator.cpp`: `rfsimulator_aiot_t2_ctlsend()`, `rfsimulator_aiot_t2_ctlrecv()` | UE control packet to RFsim; queued D2R to UE | RFsim client | `AIOT_T2_D2R_CAPTURE` | `aiot_t2_role_process_slot()` | Implemented, profile-scoped |
| CW source | `radio/rfsimulator/stored_node.c`: `aiot_cw_rfsim_cli()` | sample count/amplitude to bounded CW control packet | `replay_node` process | `AIOT_T2_CW_SOURCE` | RFsim `aiot_t2_handle_packet()` | Implemented deterministic seam |
| Tag reflection | `radio/rfsimulator/stored_node.c`: `aiot_tag_rfsim_cli()` | registered Tag plus CW and matching R2D to multiplied D2R samples | `replay_node` Tag process | `AIOT_T2_BACKSCATTER` | RFsim D2R relay | Implemented deterministic seam |
| R2D codec | `openair1/PHY/NR_UE_TRANSPORT/nr_ue_rf_helpers.c`: `nr_ue_aiot_t2_prepare_r2d()` | Tag ID and timestamp to Manchester R2D packet | UE transaction | `AIOT_T2_R2D_SENT` | RFsim R2D relay | Implemented experimental codec |
| D2R codec | `openair1/PHY/NR_UE_TRANSPORT/nr_ue_rf_helpers.c`: `nr_ue_aiot_t2_decode_d2r()` | D2R samples to length/line-code/CRC-validated payload | UE transaction | `AIOT_T2_D2R_CRC_OK` | `aiot_t2_send_report()` | Implemented experimental codec |
| UE role/window | `executables/nr-ue.c`: `aiot_t2_role_process_slot()` | connected/DRX/window state plus role to R2D send or D2R-only receive | UE process | `AIOT_T2_R2D_SENT` or reject reason | RFsim control seam | Implemented; observer cannot send R2D |
| UE report | `executables/nr-ue.c`: `aiot_t2_send_report()` | accepted payload to fixed 40-byte UDP report over `oaitun_ue<N>` | UE socket | `AIOT_T2_UE_REPORT_SENT` | ext-DN/AIOTF-side UDP endpoint | Implemented transport; correlation envelope partial |
| Binding | `openair3/AIOTF/aiotf_inventory.c`: `aiotf_binding_table_init()` | fixed profile to 60 network-owned bindings | AIOTF context | focused test PASS | `aiotf_select_readers()` | Implemented |
| Reader roles | `openair3/AIOTF/aiotf_inventory.c`: `aiotf_select_readers()` | binding/mode/availability to primary plus optional observer | AIOTF session | focused test PASS | `aiotf_schedule_transactions()` | Implemented |
| Serialization | `openair3/AIOTF/aiotf_inventory.c`: `aiotf_schedule_transactions()` | distinct Tag IDs to ordered session IDs and response slots | AIOTF context | `AIOTF_SERIALIZED_60_TAGS` | per-transaction R2D dispatch | Implemented state; dispatcher service absent |
| Arbitration | `openair3/AIOTF/aiotf_inventory.c`: `aiotf_arbitrate_report()` | validated report to first result or retained evidence | AIOTF arbitration | focused test PASS | result API/endpoint | Implemented state; UDP endpoint absent |
| Failover | `openair3/AIOTF/aiotf_inventory.c`: `aiotf_failover_primary()` | pre-R2D availability to new eligible primary and epoch | binding table | focused test PASS | new tag transaction | Implemented |
| Paging coincidence | `openair2/RRC/NR/MESSAGES/asn1_msg.c`: `nr_rrc_get_paging_parameters()`, `nr_rrc_get_paging_occasion()`; `openair3/AIOTF/aiotf_inventory.c`: `aiotf_inventory_expire()` | PCCH configuration and SFN to PF/PO identity plus independent experimental ms deadline | RRC message owner and AIOTF session | focused test PASS | NR MAC PCCH/PDCCH scheduler and over-the-air observation | PF/PO seam exposed; runtime delivery `[Needs Verification]` |

## Selected Owner Contract

| Boundary | Owner | Allowed change | Stop condition |
|---|---|---|---|
| CW/tag/UE sample routing | `radio/rfsimulator/simulator.cpp` | disabled destination-aware A-IoT route and CW-present state | normal NR sample path changes when profile is disabled |
| Propagation impairment | `radio/rfsimulator/apply_channelmod.c` | reuse existing linear channel functions | custom backscatter logic leaks into all RFsim channels |
| Single tag process | `radio/rfsimulator/stored_node.c` | add one deterministic tag mode to the existing simulated-node executable | requires a second parallel RF backend or unowned staging implementation |
| UE wake and R2D gate | existing UE connected/DRX state plus `executables/nr-ue.c` | read active state and enforce a bounded operation window | R2D can be emitted outside the window or during sleep |
| UE Reader report | `executables/nr-ue.c` plus existing PDU-session path | fixed UDP report bound to `oaitun_ue<N>` | implementation reuses RRC or NAS payloads |
| AIOTF state | `openair3/AIOTF/` | bounded pure state and focused test executable | expands into ADM/NEF/security or an unrelated core owner |
| Runtime composition | existing RedCap RFsim services plus profile options | inject disabled options and run existing `replay_node` | service startup alone is presented as radio PASS evidence |

## Experiment Contract

| Field | Frozen v1 decision |
|---|---|
| Population | one tag, one UE Reader, one gNB/CW source |
| Beam A | existing NR Uu between gNB and RedCap UE; it is not proof of a dedicated RFsim beam waveform |
| Beam B | tag-directed continuous single-tone CW; logical CW state is required before RF amplitude calibration |
| R2D | UE Reader only, bounded by explicit awake/resource-valid window; Manchester `0 -> 10`, `1 -> 01` |
| D2R | tag backscatter to UE Reader; experimental Manchester with the same mapping, then OOK and SFS factor 1 |
| Payload | 1 to 16 bytes; reject empty and 17-byte payloads; no segmentation |
| CRC | CRC6 for payloads up to 24 bits; CRC16 otherwise |
| Timeout | 100 ms from accepted R2D completion to a CRC-valid D2R report; experimental, not a 3GPP timer |
| Failure result | exactly one of `invalid_line_code`, `crc_failure`, `cw_absent`, `reader_asleep`, `payload_length`, or `timeout` |
| Rollback | disable `aiot_topology2_reader_profile_v1`; existing RFsim and NR behavior must remain unchanged |

## Gate 1 Evidence Contract

| Case | Stimulus | Required result | Required marker |
|---|---|---|---|
| Valid round trip | awake UE, valid CW, 1-to-16-byte payload | R2D accepted, D2R decoded, CRC accepted | `AIOT_T2_R2D_ACCEPT`, `AIOT_T2_D2R_CRC_OK`, `AIOT_T2_ROUNDTRIP_OK` |
| Invalid pair `00` | inject `00` in Manchester stream | reject before CRC/report forwarding | `AIOT_T2_LINECODE_REJECT pair=00` |
| Invalid pair `11` | inject `11` in Manchester stream | reject before CRC/report forwarding | `AIOT_T2_LINECODE_REJECT pair=11` |
| CRC corruption | valid line code with corrupted CRC | no accepted Inventory Report | `AIOT_T2_CRC_REJECT` |
| CW on | CW-present state and valid tag response | D2R may be accepted | `AIOT_T2_CW state=on` |
| CW off | identical response with CW absent | D2R must be rejected | `AIOT_T2_CW_REJECT state=off` |
| Reader asleep | R2D request outside awake window | no R2D sample emission | `AIOT_T2_R2D_REJECT reason=reader_asleep` |
| Payload boundaries | lengths 0, 1, 16, and 17 bytes | reject 0/17; accept 1/16 before other checks | `AIOT_T2_LENGTH_REJECT` or `AIOT_T2_LENGTH_OK` |
| Timeout | no valid response for 100 ms | one terminal timeout result | `AIOT_T2_TIMEOUT timeout_ms=100` |

Gate 1 is a deterministic codec/state gate. It does not prove CW RF power, leakage tolerance, RFsim bistatic propagation, UE-to-gNB delivery, or AIOTF operation.

## Runtime Ladder Evidence

| Layer | Evidence | Observed result | Claim boundary |
|---|---|---|---|
| Single-tag protocol simulator | `test_log/build_logs/build_aiot_t2_cross_feature_boundaries_2026-07-19_23-12-54.log` | `AIOT_T2_SELF_TEST PASS` plus AIOTF focused PASS | deterministic codec/state only |
| Baseband/CW | same cross-feature log and `test_log/compiler_logs/aiot_t2_final_image_e2e_report_2026-07-19_22-50-15.log` | CW capture, matching R2D, multiplied backscatter, D2R relay | logical RFsim samples; no RF calibration |
| Single reader | `test_log/compiler_logs/aiot_t2_final_image_e2e_report_2026-07-19_22-50-15.log` | Tag payload `01020304`, UE CRC OK, one 40-byte report at ext-DN | UE PDU-session forwarding; no AIOTF correlation endpoint |
| Two readers | `test_log/compiler_logs/aiot_t2_two_ue_reader_observer_runtime_2026-07-19_23-32-03.log` | UE1 sent R2D; UE2 sent zero R2D; both emitted one CRC-valid report; ext-DN captured reader handles 1 and 2 | Tag 25 diversity; no combining and no runtime winner selection |
| Serialized 60 Tags | `test_log/compiler_logs/aiotf_serialized_60_tag_runtime_2026-07-19_23-40-13.log` | Tags 1-60, slots 1000-1059, 60 unique slots, 30/30 default primary load | AIOTF executable state evidence; not 60 simultaneous RF tags |

The two-UE RFsim run used a deliberately wide evidence window. UE1 emitted 39,880 periodic R2D markers before capture; that count is not a throughput or energy result. The required invariant is one R2D-capable role and zero R2D from the observer.

## Binding, Report, and Boundary Results

| Metric or case | Result | Evidence class |
|---|---|---|
| UE1/UE2 default primary load | 30 / 30 | AIOTF executable |
| Tag 25 independent observations | UE1: 1 CRC-valid report; UE2: 1 CRC-valid report | two-reader RFsim |
| gNB Tag 25 D2R fan-out | 5 relays with `destinations=2` | two-reader RFsim |
| Runtime duplicate/conflict winner | not selected; current UDP endpoint does not inject correlation/session/epoch | `[Needs Verification]` |
| Duplicate evidence | one identical second report retained in focused arbitration test | protocol executable only |
| Conflict evidence | one different valid payload retained; first result unchanged | protocol executable only |
| Stale epoch | one stale-epoch report rejected as result and counted in focused test | protocol executable only |
| Timeout N-1/N/N+1 | pending before deadline; timeout at and after deadline | protocol executable only |
| Evidence bound | 8 retained entries; one additional invalid report counted as dropped | protocol executable only |
| Paging occasion coincidence | public RRC PF/PO identity seam is tied to AIOTF deadline equality at the selected paging frame | focused source-level test; exact PDCCH monitoring occasion and over-the-air PCCH delivery remain `[Needs Verification]` |

The remaining paging boundary is source-confirmed rather than inferred. `nr_rrc_get_paging_occasion()` owns the TS 38.304 PF/PO identity calculation, and `rrc_gNB_generate_pcch_msg()` reuses its PCCH parameter validation. The NGAP caller in `rrc_gNB_NGAP.c` remains commented out, and no NR MAC paging scheduler consumes the exposed occasion. `aiotf_inventory_expire()` still receives only `session` and `now_ms`; the focused check ties those values at a derived PF frame without injecting a Boolean paging flag. Exact PDCCH monitoring occasion and over-the-air PCCH delivery remain `[Needs Verification]`.

## UE Report Wire Boundary

The implemented 40-byte UDP record contains `magic`, `version`, `payload_len`, CRC-valid flags, `reader_handle`, `tag_id`, `frame`, `slot`, and a 16-byte payload. The internal `aiotf_inventory_report_t` additionally requires `correlation_id`, `session_id`, and `binding_epoch`. Until an endpoint supplies those values from a pending transaction, UDP-to-AIOTF arbitration is partial and must not be reported as end-to-end AIOTF PASS.

## Tool Evidence

- `symdex` was queried first for repository owners and call surfaces. Its `redcap_oai` index was stale and the watcher was inactive, so selected paths were verified against the current worktree with targeted source reads and `rtk rg`.
- Exact A-IoT identifiers (`Ambient IoT`, `AIOTF`, `PRDCH`, `PDRCH`) were not found in current production `openair1/2/3`, `radio`, `executables`, or `oai-cn5g` source paths.
- Local PDFs were converted to temporary text only for clause extraction; no generated specification cache was added to the repository.
