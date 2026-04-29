# M4B Registration Accept Timer Decode Test Report

## 1. Technical Background
- [PSM] lets the UE reduce power after NAS registration by using network-provided timers.
- [T3324] is the [active time] timer; after it expires, the UE can enter low-power behavior when other state conditions are satisfied.
- [T3512] is the [periodic registration] timer; it controls periodic NAS registration update cadence.
- In [Registration Accept], both timers are optional [GPRS timer 3] IEs. The UE NAS decoder must preserve them so UE-side low-power state can be updated from the AMF response.

## 2. Key C Functions / Data Structures
- `registration_accept_msg`: stores decoded [T3324] and [T3512] optional timers.
- `decode_registration_accept()`: parses optional IEI `0x5E` and `0x6A`.
- `decode_gprs_timer_ie()`: decodes [GPRS timer 3] unit/value format.
- `handle_registration_accept()`: applies decoded timers through `nr_nas_psm_update_timers()`.
- `nr_nas_psm_update_timers()`: updates UE NAS PSM state.

## 3. Test Results Summary Table
| Test Item | Status | Coverage | Log |
|-----------|--------|----------|-----|
| `cmake --build --preset default --target nr-uesoftmodem` | PASS | UE-side NAS source build | `test_log/build_logs/build_nr-uesoftmodem_2026-04-29_11-00-55_m4b-psm-timer-decode_escalated.log` |
| `ctest -R nas_lib_test --output-on-failure` | PASS | Registration Accept IE decode regression | `test_log/compiler_logs/ctest_nas_lib_test_2026-04-29_11-15-31_m4b-psm-timer-decode.log` |
| `ctest -R test_nr_nas_lowpower --output-on-failure` | PASS | PSM helper state behavior | `test_log/compiler_logs/ctest_test_nr_nas_lowpower_2026-04-29_11-16-27_m4b-psm-timer-decode.log` |
| `ci-scripts/redcap_rebuild_local_oai_images.sh` | PASS | Runtime images include C patch | `test_log/build_logs/rebuild_local_oai_images_2026-04-29_11-17-28_m4b.log` |
| 2-UE RFsim host validation | PASS | UE attach / PDU / ping / UE2 RedCap UL iperf | `test_log/report/redcap_runtime_host_summary_disabled_2026-04-29_11-28-37.md` |

## 4. 3GPP Specification Mapping
- [TS 24.501 Section 8.2.7.1.1] - [Registration Accept] optional IE table defines [T3512 value] IEI `0x5E` and [T3324 value] IEI `0x6A`.
- [TS 24.501 Section 5.5.1] - UE applies [T3512] as periodic registration timer and [T3324] as active time for PSM behavior.
- [TS 24.008 Section 10.5.7.4a] - [GPRS timer 3] coding defines the unit/value encoding used by these IEs.

## 5. Practice Exercises
- [Basic] Explain why [T3324] and [T3512] must be decoded before UE-side PSM decisions can be made.
- [Applied] Add a NAS test vector where [T3324] is deactivated and verify `nr_nas_psm_update_timers()` does not enter active-time-expired state unexpectedly.
- [Advanced] Design a runtime validation that observes UE transition from [registered + idle] to [PSM low-power ready] after active time expiry without breaking PDU session establishment.
