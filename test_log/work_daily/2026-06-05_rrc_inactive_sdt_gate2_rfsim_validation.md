# 2026-06-05 RRC_INACTIVE SDT Gate 2 RFsim Validation

- Project Path: `agent_doc/Project_management/projects/redcap_rrc_inactive_sdt_oran_control_v1/project_plan.md`
- [Case]: A
- [Gate]: 2
- [source build PASS/FAIL/NA]: PASS
- [unit test PASS/FAIL/NA]: NA
- [container image rebuilt or not]: rebuilt
- [RFsim runtime PASS/FAIL/NA]: FAIL, partial protocol progress
- [exit 139]: absent

## Scope
- [Goal]: Validate `RRCRelease.suspendConfig` -> `RRC_INACTIVE` -> `RRCResumeRequest` -> `RRCResume` -> `RRCResumeComplete` in RFsim.
- [Runtime Mode]: Case A fixed policy; xApp/rApp/dApp dynamic control disabled.
- [UE Load]: `MMTC_TOTAL_UES=29`, sampled `UE1`.

## Evidence
- [Build Log]: `test_log/build_logs/rebuild_local_oai_images_2026-06-05_11-59-00_rrc-inactive-gate2.log`
- [Image Inspect Log]: `test_log/compiler_logs/rrc_inactive_gate2_image_markers_2026-06-05_12-02-25.log`
- [Targeted Image Marker Log]: `test_log/compiler_logs/rrc_inactive_gate2_targeted_image_markers_2026-06-05_12-03-06_hoststrings.log`
- [RFsim Console Log]: `test_log/compiler_logs/rrc_inactive_gate2_rfsim_2026-06-05_12-04-06.log`
- [gNB Log]: `test_log/compiler_logs/mmtc_smoke_2026-06-05_12-04-06_gnb.log`
- [UE1 Log]: `test_log/compiler_logs/mmtc_smoke_2026-06-05_12-04-06_ue1_docker.log`
- [UE1 Marker Log]: `test_log/compiler_logs/mmtc_smoke_2026-06-05_12-04-06_ue1_markers.log`
- [UE1 Ping Log]: `test_log/compiler_logs/mmtc_smoke_2026-06-05_12-04-06_ue1_ping.log`

## Validation Result
| Test Item | Result | Evidence |
|---|---|---|
| `symdex` repo index | PASS | repo `redcap_oai`, 34948 symbols indexed |
| RedCap interface validation | PASS | `redcap_interface/validate_redcap_interface.sh` |
| targeted `git diff --check` | PASS | no output |
| local OAI image rebuild | PASS | `ran-build`, `oai-gnb`, `oai-nr-ue` rebuilt |
| image Gate 2 markers | PASS | gNB/UE softmodem binaries contain Gate 2 strings |
| RFsim attach/PDU/TUN | PASS | `running=1 attach=1 pdu=1 tun=1` |
| RFsim ping | FAIL | `1 packets transmitted, 0 received` |
| gNB restart | PASS | `gnb_restart=0` |
| crash scan | PASS | no `exit 139` / `SIGSEGV` observed |

## Gate 2 Marker Result
| Marker | Source | Result |
|---|---|---|
| `RRCRelease suspendConfig selected` | gNB log line 572 | PASS |
| `RRCRelease suspendConfig received` | UE1 log line 466 | PASS |
| `RRC_INACTIVE entered` | UE1 log line 468 | PASS |
| `MMTC Gate 2 trigger` | UE1 log line 469 | PASS |
| `RRCResumeRequest sent` | UE1 log line 480 | PASS |
| `RRCResumeRequest received` | gNB log line 591 | PASS |
| `RRC context found for RRCResumeRequest` | gNB log line 592 | PASS |
| `RRCResume sent` | gNB log line 594 | PASS |
| `RRCResume received` | UE1 log | FAIL, no match |
| `RRCResumeComplete sent` | UE1 log | FAIL, no match |
| post-resume `RRC_CONNECTED` | UE1 log after resume | FAIL, no match |

## Failure Interpretation
- [Observed]: UE completed second 4-step RA for `RRCResumeRequest`; gNB sent `RRCResume`; UE did not process `RRCResume`.
- [Observed]: gNB later reported UL failure / DTX for both old RNTI `83d4` and new RNTI `aa7a`, then released contexts.
- [Hypothesis]: `RRCResume` is placed into gNB-side SRB1/RLC for new RNTI `aa7a`, but UE does not receive or deliver the Msg4 SRB1 SDU to RRC.
- [Needs Verification]: whether this is due to Msg4 MAC PDU multiplexing, UE MAC LCID1 parsing after contention resolution, or SRB1/PDCP resume state.

## Next Debug Step
- [Modification Point] -> UE MAC Msg4 parser and gNB Msg4 assembly logs.
- [Reason] -> Need visibility for `LCID1` delivery in Msg4 after contention resolution.
- [Before vs. After Comparison] -> Before: only high-level RA success is visible; After: logs should show `lcid`, `mac_sdu_length`, and whether LCID1 is delivered to RLC.
- [Discussion Point] -> Add temporary Gate 2 validation logs first; avoid claiming full SDT until `RRCResumeComplete` appears.

## Educational Learning Report
- [Technical Background]: Gate 2 verifies the normal return path from `[RRC_INACTIVE]` to `[RRC_CONNECTED]`. This requires UE context retention, `shortI-RNTI` matching, second RA, `RRCResume`, and `RRCResumeComplete`. The current run proves context lookup and gNB resume generation, but not UE-side resume consumption.
- [Key Functions / Data Structures]:
  - `rrc_handle_RRCResumeRequest()`
  - `rrc_gNB_generate_RRCResume()`
  - `nr_rrc_ue_trigger_RRCResumeRequest_ra()`
  - `nr_rrc_ue_process_rrcResume()`
  - `nr_generate_Msg4_MsgB()`
- [Practice Exercises]:
  - [Basic] Explain why `shortI-RNTI` is needed after `RRCRelease.suspendConfig`.
  - [Applied] Trace why `RRCResumeRequest received` can pass while `RRCResume received` fails.
  - [Advanced] Propose a log point that distinguishes MAC Msg4 multiplexing failure from PDCP/RLC resume failure.

## Update 12:33 Msg4 Debug And SRB1 Resume Fix
- [Code Added]: Gate 2 diagnostic logs in `openair2/LAYER2/NR_MAC_gNB/gNB_scheduler_RA.c` and `openair2/LAYER2/NR_MAC_UE/nr_ue_procedures.c`.
- [Code Added]: UE `RRC_RESUME_REQUEST` Msg3 indication now re-establishes/reconfigures `[SRB1 RLC]` and resumes `[MAC LCID1]` without resetting `[PDCP]`.
- [Build Evidence]:
  - `test_log/build_logs/build_nr-softmodem_2026-06-05_12-22-50_rrc-inactive-gate2-msg4-dbg_escalated.log`: PASS.
  - `test_log/build_logs/build_nr-uesoftmodem_2026-06-05_12-23-07_rrc-inactive-gate2-msg4-dbg_escalated.log`: PASS.
  - `test_log/build_logs/rebuild_local_oai_images_2026-06-05_12-23-28_rrc-inactive-gate2-msg4-dbg.log`: PASS.
  - `test_log/build_logs/build_nr-uesoftmodem_2026-06-05_12-33-22_rrc-inactive-gate2-srb1-resume_sandbox-ccache-tmp.log`: PASS.
- [Runtime Evidence]: `test_log/compiler_logs/rrc_inactive_gate2_msg4_dbg_rfsim_2026-06-05_12-27-04.log`.
- [New Finding]:
  - UE Gate 2 Msg4 received `LCID1/DCCH len 10` at UE log lines 555-556 with `suspended=0`.
  - gNB sent `RRCResume` and received Msg4 ACK at gNB log lines 590-597.
  - Therefore `[Msg4 mux]` and `[UE MAC LCID1 parser]` are no longer the primary suspects.
- [Current Hypothesis]: UE RLC SRB1 state was not aligned with the new C-RNTI RA leg, so LCID1 reached MAC but did not become a PDCP/RRC SDU.
- [Post-Fix Status]: local `nr-uesoftmodem` build PASS; Docker image rebuild and RFsim post-fix run are pending because the escalation request was rejected by session usage limits until quota resets.
- [Next Required Validation]: rebuild local OAI images, verify `RRCResumeRequest resumed SRB1 RLC/MAC` marker in UE image/log, rerun Gate 2 RFsim, and require `RRCResume received`, `RRCResumeComplete sent`, and post-resume `RRC_CONNECTED`.

## Update 18:20 RRCResume Context Migration And User-Plane Split
- [Code Added]: gNB `RRCResume` now sends the old DU UE ID together with the new DU UE ID, with a local `[rrc_resume]` hint in `f1ap_dl_rrc_message_t`.
- [Code Added]: DU/MAC old-ID migration now treats `[RRCResume]` differently from `[RRCReestablishment]`.
  - For `[RRCResume]`: keep copied LCIDs active and keep the existing `CellGroup`.
  - For `[RRCReestablishment]`: keep the previous suspend/reconfiguration behavior.
- [Code Added]: `nr_rlc_update_id()` now accepts an explicit `[reestablish_srb1]` flag.
- [Build Evidence]:
  - `test_log/build_logs/build_nr-softmodem_2026-06-05_17-58-00_rrc-inactive-gate2-resume-migration_escalated.log`: PASS, no warning/error scan hits.
  - `test_log/build_logs/build_nr-uesoftmodem_2026-06-05_18-02-00_rrc-inactive-gate2-resume-migration_escalated.log`: PASS, no warning/error scan hits.
  - `test_log/build_logs/build_nr-softmodem_2026-06-05_18-18-00_rrc-inactive-gate2-resume-srb1-reestablish_escalated.log`: PASS, no warning/error scan hits.
  - `test_log/build_logs/rebuild_local_oai_images_2026-06-05_18-20-00_rrc-inactive-gate2-resume-srb1-reestablish.log`: PASS, `[Done] Local RedCap runtime images rebuilt from workspace`.
- [Runtime Evidence Before Final SRB1 Re-establish Adjustment]:
  - `test_log/compiler_logs/rrc_inactive_gate2_resume_migration_rfsim_2026-06-05_18-08-00.log`: FAIL only on forward ping.
  - RFsim summary: `running=1 attach=1 pdu=1 tun=1 forward_ping_ok=0 gnb_restart=0 failures=1`.
  - gNB marker: `RRCResume old UE ID migration bd16 -> 5a33: keeping logical channels active`.
  - Improvement: `[LCID4 ignoring]`, `[SRB1 max RETX]`, and `[gNB restart]` were absent in this run.
  - Remaining issue in that run: gNB did not log `[RRCResumeComplete received]`, then detected `[PUSCH DTX/UL Failure]` and released the UE/tunnel.
- [Current Fix Direction]:
  - `[RRCResume]` must still re-establish `[SRB1 RLC]` to match the UE-side resume path.
  - `[RRCResume]` must not inherit `[RRCReestablishment]` DRB suspend or `reconfigCellGroup` behavior.
- [Pending Validation]:
  - Final RFsim rerun after `build_nr-softmodem_2026-06-05_18-18-00_rrc-inactive-gate2-resume-srb1-reestablish_escalated.log` and image rebuild is pending.
  - Blocker: Docker marker/RFsim commands require escalation, and the automatic approval layer rejected the next Docker command because the session reached the temporary usage limit.
  - Required pass criteria remain: `RRCResume received`, `RRCResumeComplete sent`, `RRCResumeComplete received`, no UE release before ping, and `forward_ping_ok=1`.

## Update: Final Sanity Check Before RFsim Rerun
- [Code Clarification]: Updated the DU/MAC migration comment so `old_gNB_DU_ue_id` is documented as a migration path for both `[RRCReestablishment]` and `[RRCResume]`.
- [Static Check]: targeted `git diff --check` PASS for the touched Gate 2 code and this daily log.
- [Initialization Check]: `f1ap_dl_rrc_message_t` construction sites use `{...}` or `{0}` initialization, so the new local `[rrc_resume]` flag defaults to false when not explicitly set.
- [Milestone Status]: [T2] was not updated to PASS because final RFsim ping recovery is still pending.
- [Spec Status]: 3GPP clause references remain `[Needs Verification]`; no new hard-coded clause mapping was added to the project docs.

## Update 23:10 Post-Fix RFsim And SRB1 Boundary Trace
- [Code Added]: temporary Gate 2 SRB1 boundary logs in `[UE RRC]`, `[PDCP->RLC]`, `[RLC recv_sdu]`, `[UE RLC->MAC]`, `[UE MAC UL]`, `[gNB MAC UL]`, and `[gNB UL DTX]`.
- [Build Evidence]:
  - `test_log/build_logs/build_nr-softmodem_2026-06-05_23-03-54_gate2-ul-srb1-trace_escalated.log`: PASS.
  - `test_log/build_logs/build_nr-uesoftmodem_2026-06-05_23-04-16_gate2-ul-srb1-trace_escalated.log`: PASS.
  - `test_log/build_logs/rebuild_local_oai_images_2026-06-05_23-04-58_gate2-ul-srb1-trace.log`: PASS, `[Done] Local RedCap runtime images rebuilt from workspace`.
- [Image Marker Evidence]: Docker fixed-string checks PASS for `[gNB UL DTX]`, `[gNB MAC UL]`, `[UE MAC UL]`, and `RRCResumeComplete sent on SRB`.
- [RFsim Evidence]:
  - `test_log/compiler_logs/rrc_inactive_gate2_ul_srb1_trace_rfsim_2026-06-05_23-10-46.log`: FAIL.
  - RFsim summary: `running=1 attach=1 pdu=1 tun=1 forward_ping_ok=0 gnb_restart=0 failures=1`.
  - UE log: `test_log/compiler_logs/mmtc_smoke_2026-06-05_23-10-46_ue1_docker.log`.
  - gNB log: `test_log/compiler_logs/mmtc_smoke_2026-06-05_23-10-46_gnb.log`.
- [Gate 2 Pass Criteria]:
  - `RRCResume received`: PASS, UE log line 603.
  - `RRCResumeComplete sent`: PASS, UE log line 606.
  - `RRCResumeComplete received`: FAIL, no gNB match.
  - no `[LCID4 ignoring]`: PASS, no match.
  - no early UE release: FAIL, gNB released after UL failure timer expiry and deleted tunnels.
  - `forward_ping_ok=1`: FAIL, summary has `forward_ping_ok=0`.
- [SRB1 Boundary Finding]:
  - UE enqueued `[RRCResumeComplete]` to `[PDCP->RLC]` and `[RLC recv_sdu]` after `RRCResumeComplete sent`.
  - No post-resume `[UE RLC->MAC]` / `[UE MAC UL]` marker was observed for that SRB1 SDU.
  - gNB did not receive post-resume SRB1 UL SDU for new C-RNTI `db96`; it later logged `[gNB UL DTX] RNTI db96 sched_ul_bytes 17 estimated_ul_buffer 0 SRB1_config 1 SRB1_suspended 0`.
- [C-RNTI Context Check]:
  - This run used old short/C-RNTI `0ae6` and new C-RNTI `db96` for the resume RA leg.
  - gNB found the retained RRC context and migrated old DU UE ID `0ae6` to new DU UE ID `db96`.
  - The remaining blocker is not `[RRCResume DL delivery]`; it is the post-resume `[UL SRB1 mux/grant/retransmission]` path.
- [Next Step]:
  - Stay in `[Gate 2]`; do not enter `[Gate 3 configuredGrantConfig + cg-SDT]`.
  - Add a narrow trace for UE `[LCID1 buffer remain]`, `[BSR trigger]`, `[SR pending]`, and active `[UL BWP]` after `RRCResumeComplete`.
  - Keep 3GPP clause mapping as `[Needs Verification]`.

## Update 23:22 LCID1 BSR/SR Trace
- [Code Added]: temporary Gate 2 UE traces for `[LCID1 buffer]`, `[BSR]`, `[SR]`, `[LCP]`, and `[UE MAC RB]`.
- [Build Evidence]:
  - `test_log/build_logs/build_nr-uesoftmodem_2026-06-05_23-18-26_gate2-lcid1-bsr-sr-trace_escalated.log`: PASS.
  - `test_log/build_logs/rebuild_local_oai_images_2026-06-05_23-18-43_gate2-lcid1-bsr-sr-trace.log`: PASS.
- [RFsim Evidence]:
  - `test_log/compiler_logs/rrc_inactive_gate2_lcid1_bsr_sr_trace_rfsim_2026-06-05_23-22-11.log`: FAIL.
  - RFsim summary: `running=1 attach=1 pdu=1 tun=1 forward_ping_ok=0 gnb_restart=0 failures=1`.
  - Resume C-RNTI migration: old `37a8` -> new `e7dd`.
- [Gate 2 Pass Criteria]:
  - `RRCResume received`: PASS, UE log line 942.
  - `RRCResumeComplete sent`: PASS, UE log line 946.
  - `RRCResumeComplete received`: FAIL, no gNB match.
  - no `[LCID4 ignoring]`: PASS, no match.
  - no early UE release: FAIL, gNB released after UL failure timer expiry.
  - `forward_ping_ok=1`: FAIL.
- [Root Cause Finding]:
  - UE put `[RRCResumeComplete]` into `[PDCP->RLC]` and `[RLC recv_sdu]`, then kept `[LCID1 bytes=13]`.
  - Immediate post-resume UE state stayed on `[UL BWP0]` with `pucch_sr_count=0`.
  - gNB switched the resumed UE to `[UL BWP1]`; therefore the remaining blocker was `[UE active UL BWP/SR restoration]`, not user-plane recovery.

## Update 23:34 Gate 2 BWP Restore RFsim PASS
- [Modification Point] -> UE `[RRCResume]` handler restores active `[DL/UL BWP]` before sending `[RRCResumeComplete]`.
- [Reason] -> Resume RA temporarily used initial `[BWP0]`; without restoring saved `[firstActiveUplinkBWP_Id=1]`, SRB1 data had no SR resource.
- [Before vs. After Comparison] -> Before: post-resume `ul_bwp_id=0`, `pucch_sr_count=0`, no `[RRCResumeComplete received]`; After: `UL 0->1`, `pucch_sr_count=1`, gNB receives `[RRCResumeComplete]`.
- [Discussion Point] -> `[PDCP SN preservation]` remains `[Needs Verification]`; Gate 2 RFsim pass does not start `[Gate 3 configuredGrantConfig + cg-SDT]`.
- [Code Added]:
  - `openair2/LAYER2/NR_MAC_UE/config_ue.c`: `nr_rrc_mac_restore_active_bwp()`.
  - `openair2/LAYER2/NR_MAC_UE/mac_proto.h`: MAC API declaration.
  - `openair2/RRC/NR_UE/rrc_UE.c`: call BWP restore before `RRCResumeComplete`.
- [Build Evidence]:
  - `test_log/build_logs/build_nr-uesoftmodem_2026-06-05_23-29-24_gate2-bwp-restore.log`: FAIL due sandbox `ccache` temp path read-only; no C compile error identified.
  - `test_log/build_logs/build_nr-uesoftmodem_2026-06-05_23-29-45_gate2-bwp-restore_escalated.log`: PASS.
  - `test_log/build_logs/rebuild_local_oai_images_2026-06-05_23-30-35_gate2-bwp-restore.log`: PASS, `[Done] Local RedCap runtime images rebuilt from workspace`.
- [Image Marker Evidence]: `oai-nr-ue:latest` contains `[RRC_INACTIVE Gate 2][UE BWP restore]`.
- [RFsim Evidence]:
  - `test_log/compiler_logs/rrc_inactive_gate2_bwp_restore_rfsim_2026-06-05_23-34-44.log`: PASS.
  - UE log: `test_log/compiler_logs/mmtc_smoke_2026-06-05_23-34-44_ue1_docker.log`.
  - gNB log: `test_log/compiler_logs/mmtc_smoke_2026-06-05_23-34-44_gnb.log`.
  - RFsim summary: `sample=1 running=1 attach=1 pdu=1 tun=1 forward_ping_ok=1 gnb_restart=0 failures=0`.
- [Gate 2 Pass Criteria]:
  - `RRCResume received`: PASS, UE log line 933.
  - `RRCResumeComplete sent`: PASS, UE log line 940.
  - `RRCResumeComplete received`: PASS, gNB log line 639.
  - no `[LCID4 ignoring]`: PASS, no match.
  - no early UE release: PASS, no `request release after UL failure` / `Delete all tunnels` / `Remove UE context` match.
  - `forward_ping_ok=1`: PASS, console summary line 104.
- [Key Evidence]:
  - UE BWP restore marker: `active DL 0->1 UL 0->1 ul_start 0 ul_size 106 pucch_sr_count 1`.
  - Post-restore UE SRB1 path: `LCID1 bytes 13`, `ul_bwp_id 1`, `pucch_sr_count 1`, then `[UE BSR]`, `[UE RLC->MAC]`, and `[UE MAC UL]`.
  - gNB received post-resume SRB1 SDU on new C-RNTI `d11d` and logged `RRCResumeComplete received; RRC_CONNECTED`.
- [Milestone Status]: [T2 Gate 2] RFsim PASS on 2026-06-05; [Gate 3] remains not started.
