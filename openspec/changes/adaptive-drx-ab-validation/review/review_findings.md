# Adaptive C-DRX A/B Review Findings

## Review Status

- [Phase]: Review complete; implementation has not started.
- [Readiness]: CONDITIONAL. The standards path is clear, but current OAI has only a partial UE C-DRX path and no matching gNB C-DRX scheduler state.
- [Scope]: one RedCap UE, RRC_CONNECTED C-DRX, separate downlink and uplink campaigns.

## 1. 3GPP Findings

### TS 38.321

- [Source]: `redcap_doc/specs/redcap_3gpp/DRX/TS_38_321_計時器_流程定義(DRX).pdf`, ETSI TS 138 321 V18.2.0 / 3GPP Release 18.
- [Clause 5.7]: DRX controls the UE MAC entity's PDCCH monitoring activity while RRC_CONNECTED.
- [Clause 5.7]: RRC configures `drx-onDurationTimer`, `drx-InactivityTimer`, retransmission timers, long/short cycles, HARQ RTT timers, and related parameters.
- [Clause 5.7]: Active Time is broader than On Duration. It can also include inactivity, retransmission, random-access, pending-SR, and other conditions.
- [Clause 5.7]: `drx-InactivityTimer` is associated with a PDCCH occasion where PDCCH indicates a new transmission; HARQ ACK reception is not the direct trigger.
- [Clause 5.7]: receiving a DRX Command MAC CE or Long DRX Command MAC CE stops `drx-onDurationTimer` and `drx-InactivityTimer` for each DRX group.
- [Clause 6.1.3.5]: DRX Command MAC CE is identified by its DL-SCH LCID and has a zero-bit payload.
- [Clause 6.1.3.6]: Long DRX Command MAC CE also has a zero-bit payload.

### TS 38.331

- [Source]: `redcap_doc/specs/redcap_3gpp/DRX/TS_38_331_RRC_長短DRX Cycle設定(DRX).pdf`, ETSI TS 138 331 V18.5.1 / 3GPP Release 18.
- [Clause 6.3.2]: `MAC-CellGroupConfig` carries `drx-Config SetupRelease { DRX-Config }`.
- [Clause 6.3.2]: `DRX-Config` includes On Duration, inactivity, HARQ RTT, retransmission, long-cycle/start-offset, optional short DRX, and slot offset.
- [Legal long cycles]: `10, 20, 32, 40, 60, 64, 70, 80, 128, 160, 256, 320, 512, 640, 1024, 1280, 2048, 2560, 5120, 10240 ms`.
- [Legal integer-ms On Duration values]: `1, 2, 3, 4, 5, 6, 8, 10, 20, 30, 40, 50, 60, 80, 100, 200, 300, 400, 500, 600, 800, 1000, 1200, 1600 ms`.
- [Needs Verification]: Release 18 non-integer DRX extensions are excluded from v1 because the selected OAI ASN.1 runtime surface is Release 17.3.0.

## 2. Current OAI Trace

| Layer | Source path and symbol | Finding | Review verdict |
|---|---|---|---|
| UE RRC-to-MAC | `openair2/LAYER2/NR_MAC_UE/config_ue.c`: `configure_maccellgroup()` -> `configure_drx()` | Decodes `NR_SetupRelease_DRX_Config_t` into a local slot-based structure | Present |
| UE DRX state | `openair2/LAYER2/NR_MAC_UE/nr_ue_drx.c` | Implements long-cycle On Duration, pending SR, and a simplified inactivity deadline | Partial |
| UE PDCCH gating | `openair2/LAYER2/NR_MAC_UE/nr_ue_scheduler.c`: `nr_ue_dl_scheduler()` | Skips DCI configuration outside the simplified active state | Partial |
| UE activity update | `nr_ue_drx_note_activity()` call sites | UL PUSCH activity is recorded; DL currently records configured DCI monitoring rather than a decoded new-transmission indication | Non-compliant approximation |
| UE DRX MAC CE | `openair2/LAYER2/NR_MAC_UE/nr_ue_procedures.c` | Recognizes DRX and Long DRX LCIDs as zero-length CEs but performs no timer/state transition | Missing behavior |
| gNB DRX configuration | `openair2/RRC/NR/` | Contains ASN.1 definitions but no NR gNB producer/apply path for per-UE `DRX-Config` was found | Missing |
| gNB DRX scheduler state | `openair2/LAYER2/NR_MAC_gNB/` | No matching per-UE C-DRX active-time state or scheduling gate was found | Missing |
| gNB DRX Command writer | `gNB_scheduler_dlsch.c`: `nr_write_ce_dlsch_pdu()` | Can write `DL_SCH_LCID_DRX`, but current normal and RA callers pass `255` (`no drx`) | Dormant helper |
| Unit tests | `openair2/LAYER2/NR_MAC_UE/tests/test_nr_ue_drx.cpp` | Covers basic long cycle, pending SR, and inactivity only | Insufficient for TS 38.321 Active Time |

### Required implementation correction

- Add a gNB per-UE C-DRX state synchronized with the RRC configuration sent to the UE.
- Gate gNB scheduling consistently with the same long cycle, start offset, On Duration, and Active Time rules.
- Replace the UE's monitoring-configuration activity approximation with actual new-transmission and timer events.
- Implement DRX/Long DRX MAC CE state transitions on the UE before enabling the optional command gate.
- Add frame-number wrap handling, retransmission/HARQ timing, RA Active Time, short DRX, and command tests before claiming TS 38.321 compliance.

## 3. O-RAN and Language Boundary

- [Source]: `dev_refer/develop_refer_doc/xapp/O-RAN.WG3.TS.E2SM-RC-R005-v10.00.docx`.
- [Clause 7.6.3]: Radio Resource Allocation Control is Control Service Style `2`.
- [Clause 7.6.3.1]: DRX parameter configuration is Control Action `1`.
- [Clause 8.4.3.1]: the standard RAN parameters are Long DRX Cycle Length (`1`), Short DRX Cycle Length (`2`), and Short DRX Cycle Timer (`3`).
- [Important boundary]: On Duration is not listed as a Control Action parameter in Clause 8.4.3.1.
- [Current OAI RC]: `ran_func_rc.c` advertises only Service Style `1`; it does not advertise Style `2` / Action `1`.
- [Current Python binding]: FlexRIC SWIG exposes monitoring and slice-control examples but no generic RC control surface for the RedCap Python SDK.
- [Current E3]: `openair2/E3AP/` is a C/Python guard skeleton with no E3 transport or libe3 runtime integration.

### v1 control decision

- Use the standard E2SM-RC Service Style `2`, Action `1`, RAN Parameter `1` for the Long DRX Cycle Length.
- Disable short DRX in v1; do not send RAN Parameters `2` or `3`.
- Keep prediction statistics and policy version in the local campaign/control record, correlated with the E2 RIC Request ID.
- Let the in-process C dApp guard choose the approved On Duration and start offset from the selected local profile.
- Do not add a standard-looking custom On Duration RAN parameter in v1.
- Add a narrow Python SWIG RC bridge so the Python xApp can send the standard RC request directly.
- Treat full E3 transport integration as a separate claim; the v1 runtime path is `Python xApp -> E2SM-RC -> gNB E2 agent -> C dApp guard -> gNB RRC/MAC`.

## 4. Frozen Review Decisions

- [Policy contract]: `review/drx_policy_contract_v1.yaml`.
- [Experiment manifest]: `review/experiment_manifest_v1.yaml`.
- [Primary DRX Command gate]: disabled until the base RRC-configured C-DRX path passes and both UE/gNB command state machines exist.
- [Energy wording]: RFsim reports PDCCH-monitoring/Active-Time proxies only; it does not prove UE hardware power savings.
- [Implementation entry]: start with gNB/UE standards state and standard RC Style 2 support before implementing the adaptive predictor.

## 5. Tool Evidence

- `symdex` was used first for repository symbols and call surfaces; its full-repo index was stale, so every selected path was verified against the current worktree with targeted `rtk rg` and source reads.
- The local specification PDFs were converted only into temporary text for clause extraction; no generated spec cache was added to the repository.
