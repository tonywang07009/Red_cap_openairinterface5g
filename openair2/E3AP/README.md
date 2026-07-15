# RedCap E3AP SDK

## Purpose

- [dApp]: first OAI-side channel for future RedCap dApp / E3AP work.
- [Scope]: guard SDK skeleton only; no E3 transport, libe3 binding, or RFsim runtime integration yet.
- [Reference]: `Apps_dev/dapp_dev_need/libe3/`, `Apps_dev/dapp_dev_need/E3Controller/`, and `Apps_dev/dapp_dev_need/dApp-library/`.

## Current SDK Slice

- `sdk/redcap_dapp_sdk.h`
- `sdk/redcap_dapp_sdk.c`
- `sdk/redcap_dapp_sdk.py`

The first slice exposes a small guard API for RedCap UL PRB cap requests. It models the dApp/gNB safety decision before a runtime apply path can claim success.

## Boundary

- [ACK]: request is inside the contract range.
- [NACK]: missing request, invalid RNTI, or out-of-contract PRB cap.
- [Runtime PASS]: still requires a future E3AP/libe3 integration and gNB-side marker evidence.
