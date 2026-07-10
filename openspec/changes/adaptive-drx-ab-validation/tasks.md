## 1. Review

- [x] 1.1 Extract and record the applicable local TS 38.321 DRX-operation rules and the TS 38.331 `DRX-Config` field mapping; mark unresolved release-specific details `[Needs Verification]`.
- [x] 1.2 Trace the current OAI C-DRX configuration and timer paths with `symdex`, covering gNB RRC configuration, gNB MAC scheduling/DRX command handling, and UE MAC timer execution.
- [x] 1.3 Inspect the existing E2/FlexRIC and E3/dApp control surfaces to decide whether a supported E2SM-RC action exists or a bounded custom DRX control encoding is required.
- [x] 1.4 Review the current `drx_profile` contract entry and define the smallest versioned policy schema for cycle, On Duration, prediction statistics, fallback, cooldown, rollback, and reason-coded reject states.
- [x] 1.5 Freeze the v1 experiment manifest: independent DL and UL campaigns, 330 arrivals per campaign, 30-sample warm-up, 300 scored arrivals, recorded trace seed, recorded Arm A profile seed, accepted profile set, and metric definitions.
- [x] 1.6 Review the traffic-generator options and select a fixed-byte burst method that does not treat iPerf process startup as packet-arrival timing.

> **Model checkpoint - use GPT-5.6 Sol / max.** Do not enter implementation until the control surface, legal DRX values, and Review evidence are accepted.

## 2. Implementation

- [ ] 2.1 Add a deterministic DL/UL traffic-trace generator, campaign manifest, and 330-arrival runner with direction-specific source timestamps.
- [ ] 2.2 Add the Python xApp predictor and narrow FlexRIC SWIG RC bridge that commit 30 samples, calculate `mu`, `sigma`, `mu +/- 3 sigma`, median, p95, min, and max, and emit the standard Style 2 / Action 1 long-cycle request or fallback intent.
- [ ] 2.3 Add the C dApp/gNB guard that validates policy version, legal enumerations, cooldown, UE state, rollback data, and reject reasons before runtime application.
- [ ] 2.4 Complete the UE TS 38.321 Active Time state machine and replace monitoring-configuration activity with actual new-transmission/timer events.
- [ ] 2.5 Add synchronized per-UE gNB C-DRX state and scheduler gating for the same RRC configuration sent to the UE.
- [ ] 2.6 Implement the gNB RRC apply/rollback path for C-DRX cycle, dApp-selected On Duration, and start offset, with policy-version and applied-state markers.
- [ ] 2.7 Implement an optional, separately guarded DRX Command MAC CE path only after the base C-DRX gate passes; do not use it for DRX reconfiguration.
- [ ] 2.8 Advertise and decode standard E2SM-RC Service Style 2 / Action 1, call the dApp-local guard, and record distinct request, acknowledgement, decision, apply, completion, and timeout markers.
- [ ] 2.9 Add focused unit/contract tests for prediction bounds, stale-version rejection, rollback, window retention, deterministic seeds, complete Active Time, frame wrap, and DRX Command guard conditions.
- [ ] 2.10 Add RFsim campaign runners and checkers for Arm A and Arm B, including CSV correlation by policy version and a clear PARTIAL/BLOCKED result when any required marker is missing.
- [ ] 2.11 Build the affected gNB and UE targets, run the focused tests, and save timestamped compiler, runtime, and marker evidence.

> **Model checkpoint - use GPT-5.6 Sol / ultra for multi-module C/E2/E3 integration and RFsim blocker analysis.** Use Sol / max for smaller source changes; do not use Terra to decide protocol behavior.

## 3. Documentation

- [ ] 3.1 Write paired English and Traditional Chinese manual-reproduction guides following `doc_example/tutro_example.md`: scenario, prerequisites, build, deterministic trace generation, execution, validation, rollback, and troubleshooting.
- [ ] 3.2 Add Mermaid diagrams for the traffic-to-xApp-to-E2-to-dApp-to-gNB-to-UE decision flow and the policy-window state machine.
- [ ] 3.3 Document every API and control-contract field, its owner, direction, validation rule, rollback behavior, and expected marker.
- [ ] 3.4 Write the Gate report with Arm A/B manifests, scored population, statistical results, latency/throughput/retransmission/monitoring-time proxies, limitations, and explicit separation of RFsim proxies from physical-power claims.
- [ ] 3.5 Add the final **Trace Code Guide**: a file-and-symbol route from traffic generation through Python xApp prediction, E2 decode, C dApp guard, gNB RRC/MAC apply, UE MAC timer handling, and the checker markers; each entry must state input, output, marker, and next trace point.
- [ ] 3.6 Verify paired-document completeness, Mermaid rendering, commands, source links, and evidence-path references before publishing the final report.

> **Model checkpoint - switch to GPT-5.6 Terra only after Implementation evidence is frozen.** Use Terra for bilingual drafting, tables, Mermaid, and tutorial wording; return to Sol / max for the final standards and evidence review.
