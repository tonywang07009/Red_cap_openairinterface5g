# dApp/xApp SDK Validation Gates

## Gate A: SDK Unit And API Contract

- [Scope]: xApp priority hint and dApp PRB allocation decision.
- [Evidence]:
  - Python contract self-test PASS.
  - C syntax check for changed SDK files.
- [Expected Markers]:
  - `RedCap xApp priority hint`
  - `RedCap dApp PRB decision`

## Gate B: SWIG Evidence Boundary

- [Scope]: prove whether Python is backed by C/C++ binding.
- [Evidence]:
  - `dev_refer/dapp_dev_need/libe3/swig/libe3.i`
  - `dev_refer/dapp_dev_need/libe3/cmake/libe3SWIG.cmake`
  - `dev_refer/dapp_dev_need/dApp-library/libiqsaver/swig/iqsaver.i`
  - generated/importable modules only when built locally.
- [Limitation]: if generated modules are absent, status is definition-only, not SWIG runtime PASS.

## Gate C: E3 Loopback

- [Scope]: local RAN-role and DAPP-role E3 agents exchange data.
- [Reference Source]:
  - `dev_refer/dapp_dev_need/libe3/tests/integration/test_role_pair_posix.cpp`
  - `dev_refer/dapp_dev_need/libe3/tests/integration/bench_full_loop_latency.cpp`
- [Runner]:
  - `python3 -B agent_doc/Project_management/projects/redcap_dapp_xapp_sdk_test_validation_v1/scripts/gate_c_e3_loopback_check.py`
- [Evidence]:
  - E3 setup success.
  - dApp indication receive marker.
  - dApp control/report send marker.
  - Optional latency table from `test_bench_full_loop_latency`.
- [Build Preconditions]:
  - `cmake`
  - C++17 compiler
  - `asn1c` (`/opt/asn1c/bin/asn1c` was detected in the current workspace)
  - cached or network-accessible `tl_expected` FetchContent source
- [Configure Evidence]:
  - `test_log/compiler_logs/gate_c_libe3_configure_2026-07-05_18-43-41.log`
  - `test_log/compiler_logs/gate_c_libe3_configure_fetch_2026-07-05_18-46-35.log`
- [Current Blocker]: clean fetch configure fails because sandbox DNS cannot resolve `github.com`; escalation was rejected because workspace credits are unavailable.
- [Status]: dependency-aware runner added; runtime PASS remains pending until a local libe3 loopback binary runs successfully.

## Gate D: Small RFsim Marker

- [Scope]: 1-2 UE RFsim dApp/xApp marker validation.
- [Evidence]:
  - UE attach/PDU health.
  - xApp priority hint marker.
  - dApp PRB decision marker.
  - gNB-side apply marker.
- [Status]: pending dApp/gNB runtime hook.

## Gate E: 56 UE / 5 PRB BWP Stress

- [Scope]: user-requested 56 RedCap UE scenario with 5 PRB BWP.
- [Evidence]:
  - attach/PDU health summary.
  - dApp/xApp marker sequence.
  - no gNB restart.
  - bounded control latency.
- [Limitation]: PUCCH resource exhaustion is a scheduler/config failure until proven otherwise.
- [Status]: pending Gate D PASS.
