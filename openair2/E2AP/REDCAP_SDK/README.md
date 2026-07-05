# RedCap E2AP SDK

## Purpose

- [xApp]: reusable RedCap helpers for E2AP/FlexRIC xApps.
- [Placement]: this directory is the OAI-tracked RedCap SDK wrapper for the `openair2/E2AP` channel.
- [FlexRIC]: code here uses FlexRIC headers and runtime libraries, but does not modify the `openair2/E2AP/flexric` submodule.

## Current SDK Slice

- `xapp/redcap_xapp_sdk.h`
- `xapp/redcap_xapp_sdk.c`
- `xapp/redcap_xapp_sdk.py`

The first SDK slice builds the RedCap UL PRB cap E2SM-RC control request used by `ci-scripts/redcap_ul_prb_ctrl_xapp.c`. The Python file mirrors the constants and request shape for tooling, tests, and later Python xApp experiments.

## Boundary

- [KPM]: observation only.
- [Control]: E2SM-RC request construction and send helper reuse.
- [Runtime PASS]: still requires RFsim Case B markers before claiming live SDK success.
