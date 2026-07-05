# BWP Runtime Evidence - 20260625_213152

## Run Scope

- [Experiment]: BWP switching with DRX, first-pass local RFsim baseline
- [Wrapper]: `scripts/run_bwp_validation.sh --run`
- [Run ID]: `20260625_213152_bwp`
- [Services]: `nearRT-RIC oai-gnb oai-nr-ue2 xapp-kpm-rc`
- [Raw Local Logs]: `test_log/redcap_bwp_sdt_validation/20260625_213152_bwp/`
- [Note]: raw `*.log` files remain under `test_log/` and are ignored by repo policy; this Markdown file is the stable evidence summary.

## Runtime Outcome

| Component | Outcome | Evidence |
|---|---|---|
| nearRT-RIC | healthy; accepted gNB E2 setup | `nearRT-RIC_tail.log` shows `Registered E2 nodes = 1` |
| gNB | healthy; UE2 in-sync | `gnb_tail.log` shows `UE RNTI 2038 CU-UE-ID 1 in-sync` |
| UE2 | healthy; RedCap template without UE1 `cells:` crash path | `ue2_tail.log` remained running during the observation window |
| xApp KPM-RC | reached E42 setup, then exited 139 | `xapp_kpm_rc_tail.log` shows `E42 SETUP-RESPONSE rx`; container status recorded exit 139 |

## Extracted Local Metrics

| metric | local_value |
|---|---:|
| active_ue_count | 1 |
| unique_rnti_count | 1 |
| ric_e2_setup_seen | 1 |
| xapp_e42_setup_seen | 1 |
| dlsch_total_rounds | 889 |
| dlsch_retx_rounds | 0 |
| dlsch_errors | 0 |
| dlsch_retx_ratio_percent | 0.000000 |
| ulsch_total_rounds | 8874 |
| ulsch_retx_rounds | 0 |
| ulsch_errors | 0 |
| ulsch_retx_ratio_percent | 0.000000 |
| gnb_mac_tx_bytes | 15096 |
| gnb_mac_rx_bytes | 146434 |
| ue_in_sync_seen | 1 |

## Interpretation

- [Completed]: local RFsim baseline proves UE2 RedCap can stay attached/in-sync and exchange MAC traffic.
- [Not Completed]: this does not yet reproduce the paper's BWP power/delay/throughput curves because `bwp-InactivityTimer`, BWP switch delay, and paper plot digitization remain `[TBD]`.
- [Needs Verification]: TS 38.523-1 clause 7.1.1.12 and TS 38.321 clause 5.15.1 are the current local BWP references; the originally requested TS 38.321 clause 5.9 mapping remains a clause-risk item.
