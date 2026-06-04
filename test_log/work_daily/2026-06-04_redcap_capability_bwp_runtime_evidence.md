# 2026-06-04 RedCap Capability / BWP Runtime Evidence

## Scope

- Goal: prove [UE1 normal] uses legacy/non-RedCap capability while [UE2 RedCap] sends [redCapParameters-r17] and is parsed by gNB.
- Runtime profile: [106PRB] serving-cell carrier with [51PRB] RedCap initial DL/UL BWP.
- Final runtime images: `oai-gnb:latest`, `oai-nr-ue:latest`.

## Code / Interface Updates

- `openair2/RRC/NR_UE/rrc_UE.c`
  - Added [UECapabilityEnquiry RedCap YAML check] before capability encoding.
  - If [nrue_recap] is enabled, UE rebuilds capability using [nr_rrc_build_redcap_ue_capability()].
- `openair2/RRC/NR_UE/rrc_ue_redcap.c`
  - Added [Built RedCap UE capability] log with [supportOfRedCap-r17], band, and optional capability flags.
- `openair2/RRC/NR/rrc_gNB.c`
  - Added gNB parser logs for [redCapParameters-r17] present/absent.
- `openair2/LAYER2/NR_MAC_gNB/gNB_scheduler_ulsch.c`
  - Added [RedCap MAC][gNB UE profile] log when RedCap CCCH 48-bit LCID marks the UE as RedCap.
- `openair2/LAYER2/NR_MAC_gNB/gNB_scheduler_RA.c`
  - Added/kept RedCap RA, Msg2, and Msg4 compact allocation logs for scheduler evidence.
- `redcap_interface/redcap_runtime_menu.sh`
  - RedCap-vs-normal override now pins local images: `oai-gnb:latest`, `oai-nr-ue:latest`.
  - Probe capability regex now only treats positive RedCap builder/use markers as `cap=yes`.

## Validation

- `bash -n redcap_interface/redcap_runtime_menu.sh`: PASS.
- `git diff --check` on touched RedCap evidence paths: PASS.
- `cmake --build --preset default --target nr-uesoftmodem`: PASS.
- `redcap_interface/redcap_rebuild_local_oai_images.sh`: PASS.
- Final runtime probe:
  - log: `test_log/compiler_logs/redcap_vs_nonredcap_2026-06-04_15-06-52_live.log`.
  - UE1: `10.0.0.2`, `cap=no`, `reg=yes`, `pdu=yes`, `PASS`.
  - UE2: `10.0.0.3`, `cap=yes`, `reg=yes`, `pdu=yes`, `PASS`.

## Evidence Files

- Summary: `test_log/red_cap_test/redcap_vs_normal_final_summary_2026-06-04_15-09-33.txt`.
- UE1 normal: `test_log/red_cap_test/normal_ue_capability_evidence_2026-06-04_15-09-33.txt`.
- UE2 RedCap: `test_log/red_cap_test/redcap_ue_capability_evidence_2026-06-04_15-09-33.txt`.
- gNB parser/scheduler: `test_log/red_cap_test/gnb_redcap_parser_scheduler_evidence_2026-06-04_15-09-33.txt`.
- Learning report: `test_log/red_cap_test/redcap_capability_bwp_learning_report_2026-06-04_15-09-33.md`.

## Key Findings

- [UE1 normal] sends legacy/minimal capability: `rel15`, `bandNR=1`, `10 bytes`; gNB logs [redCapParameters-r17 absent].
- [UE2 RedCap] sends Rel-17 capability: `rel17`, `bandNR=78`, [redCapParameters-r17], [supportOfRedCap-r17], `20 bytes`.
- gNB successfully parses UE2 RedCap capability: `supportOfRedCap-r17=1`.
- gNB logs [RedCap MAC][gNB UE profile] and RedCap RA/Msg4 compact allocation for UE2.
- gNB/SIB1 evidence shows RedCap initial DL/UL BWP size [51PRB] while full serving-cell carrier remains [106PRB].

## Residual Notes

- [TS 38.306 Section 4] and [TS 38.331 Section 5.6.3] mappings are marked [Needs Verification] in the learning report until clause text is checked against the local full spec.
- Current scheduler proof is log-based. A stronger paper-grade next step is to print one combined line with configured [51PRB RedCap BWP] and actual RA DCI [bwp_size].

