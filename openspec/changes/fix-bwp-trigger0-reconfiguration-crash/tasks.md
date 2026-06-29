## 1. Runtime Reconfiguration Inventory

- [x] 1.1 Confirm the current BWP trigger call chain and candidate ownership boundaries with SymDex-first lookup.
- [x] 1.2 Confirm the current BWP Gate 5 crash evidence and the expected post-fix runtime proof path.

## 2. Core C Implementation

- [x] 2.1 Refactor `update_cellGroupConfig_for_BWP_switch()` to build and mutate a cloned candidate cell group instead of the live UE cell group.
- [x] 2.2 Add fail-closed guards for required serving cell, uplink, active BWP ID, and CSI measurement structures.
- [x] 2.3 Update `nr_mac_trigger_reconfiguration()` so candidate encoding succeeds before assigning `UE->reconfigCellGroup` or updating `UE->local_bwp_id`.
- [x] 2.4 Preserve existing telnet trigger syntax, BWP ID mapping, SDT aggregation behavior, and validation CSV schemas.

## 3. Static And Build Validation

- [x] 3.1 Run C/C++ style-safe diff checks for the touched files.
- [x] 3.2 Build `nr-softmodem` with the default CMake preset.
- [x] 3.3 Run relevant project shell/Python syntax checks for touched validation scripts if they are updated.

## 4. Runtime Validation

- [Blocked 2026-06-29] The host `nr-softmodem` build passes after the optional PUCCH capability guard, but Docker image rebuild and post-guard RFsim validation are blocked by the workspace credits gate. Do not mark this section complete from host build evidence alone.
- [ ] 4.1 Run a single `BWP_TRIGGER_SEQUENCE=0` RFsim case with `MMTC_SEGV_BACKTRACE=1`.
- [ ] 4.2 Run a bidirectional `BWP_TRIGGER_SEQUENCE="0 1 0"` RFsim sanity case.
- [ ] 4.3 Rerun the eight-row BWP matrix after the crash fix and merge only new runtime evidence.
- [ ] 4.4 Update BWP runtime evidence, CSVs, plots, and summary docs only after new runtime evidence exists.

## 5. Project Code Review And Gate Alignment

- [x] 5.1 Perform code review for all current RedCap_BWP_SDT_validation implementation changes, covering scripts, extractors, aggregators, CSV merge behavior, runtime evidence updates, and report/plot alignment.
- [x] 5.2 Add or retain the existing `redcap-bwp-sdt-validation` task entry for project-wide implementation review before Gate 7 reporting.
- [x] 5.3 Verify Gate 5 and Gate 7 wording does not overclaim paper-comparable PASS while traffic, timer, or switch-delay hooks remain label-only.
