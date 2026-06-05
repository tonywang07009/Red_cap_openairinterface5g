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
