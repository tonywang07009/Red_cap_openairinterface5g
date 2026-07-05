# Workflow v3 Follow-up Ledger

## Purpose

- Record dApp/xApp SDK test gaps without reopening completed `redcap_oran_sdk_workflow_v3` tasks.
- Keep runtime blockers separate from static SDK/API validation.

## Open Follow-ups

| ID | Source Gate | Gap | Next Pull Item | Status |
|---|---|---|---|---|
| DXV-FU-001 | Gate C | `tl::expected` target/cache is not available; sandbox fetch cannot resolve GitHub and escalation was rejected due workspace credits | provide local `tl_expected` cache or restore credits/network access, then build `test_role_pair_posix` from `dev_refer/dapp_dev_need/libe3` | [blocked-external-dependency] |
| DXV-FU-002 | Gate D | dApp/gNB runtime marker not implemented | define exact OAI hook and marker before RFsim | [pending] |
| DXV-FU-003 | Gate E | 56 UE / 5 PRB BWP not validated | run only after Gate D passes | [pending] |
| DXV-FU-004 | Gate D/E | PDCCH command path is `[Needs Verification]` | map source hook and 3GPP/O-RAN reference before claim | [pending] |
| DXV-FU-005 | Gate C | Gate C runner exists but has not produced runtime PASS | rerun `gate_c_e3_loopback_check.py --try-configure --allow-fetch` after network/credits are available, or rerun `--try-configure` after local cache is present | [pending] |

## Closed Follow-ups

| ID | Source Gate | Resolution | Evidence |
|---|---|---|---|
