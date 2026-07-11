## Why

The current RedCap dApp/xApp validation proves selected PRB and access-pressure control paths, but it does not prove that an xApp prediction can safely drive a gNB-controlled C-DRX policy. A reproducible adaptive C-DRX A/B experiment is needed before making latency, availability, or energy-proxy claims.

## What Changes

- Define a reproducible C-DRX A/B experiment with one fixed `drx-320-10` baseline and an adaptive dApp/xApp policy path.
- Collect 330 scheduled traffic arrivals per direction and score the final 300 arrivals after a 30-sample warm-up window.
- Add a versioned xApp-to-dApp DRX policy contract, including prediction data, legal DRX candidates, reject reasons, rollback, and applied-state markers.
- Add a dApp/gNB guard that validates and applies DRX policy updates through the appropriate gNB control surface; a DRX Command MAC CE may only be used as an early-active-state control, not as a DRX reconfiguration mechanism.
- Add validation artifacts for separate downlink and uplink campaigns, deterministic traffic traces, control-path markers, and energy-proxy metrics.
- Add paired English and Traditional Chinese reproduction documentation, including Mermaid diagrams and a trace-code guide for later source-level learning.

## Capabilities

### New Capabilities

- `adaptive-drx-ab-validation`: Requirements for a safe, reproducible, and observable adaptive C-DRX A/B validation workflow.

### Modified Capabilities

- None.

## Impact

- Expected gNB control/configuration code: RRC DRX configuration, MAC DRX state/command handling, and RedCap dApp guard integration under `openair2/`.
- Expected xApp code: RedCap SDK control-request construction and prediction input/output handling under `openair2/E2AP/REDCAP_SDK/`.
- Expected dApp code: local safety validation and applied-state evidence under `openair2/E3AP/`.
- Expected test assets: deterministic traffic traces, RFsim runner/checker updates, contract/self-tests, and saved CSV/marker evidence under the active dApp/xApp validation project.
- Exact E2SM-RC action and 3GPP field mappings remain `[Needs Verification]` until targeted source and local-reference extraction are complete.
