# RedCap M5 Learning Report

## 1. Technical Background
This unit closes the local control loop between the FlexRIC RC service model and the gNB UL scheduler. The project plan says the xApp should influence UL PRB allocation on the RedCap path. In practice, that means the gNB needs two things: a control action that the RC function advertises to the RIC, and a scheduler field that survives long enough to clamp a later PUSCH allocation. The implementation here keeps the action minimal by carrying only a `UE RNTI` and a `Max UL PRB cap`. Once parsed, the cap is stored per UE and applied before `nr_find_nb_rb()` determines the final grant. This is intentionally a runtime tightening mechanism, not a new RedCap capability definition. It never expands the UE beyond the RedCap BWP/capability limits already configured by SIB1 and UE capability exchange; it only narrows the scheduler decision inside that already valid RedCap operating region.

## 2. Key C functions / Data structures utilized
- `write_ctrl_rc_sm()` in `openair2/E2AP/RAN_FUNCTION/O-RAN/ran_func_rc.c`
- `nr_redcap_parse_ul_prb_ctrl_message()` in `openair2/E2AP/RAN_FUNCTION/O-RAN/ran_func_rc_redcap.c`
- `nr_redcap_sanitize_ul_prb_cap()` in `openair2/LAYER2/NR_MAC_gNB/nr_mac_redcap.h`
- `nr_redcap_effective_ul_prb_cap()` in `openair2/LAYER2/NR_MAC_gNB/nr_mac_redcap.h`
- `pf_ul()` in `openair2/LAYER2/NR_MAC_gNB/gNB_scheduler_ulsch.c`
- `NR_UE_sched_ctrl_t::redcap_ul_prb_cap`
- `nr_redcap_rc_ul_prb_ctrl_t`

## 3. Test Results Summary Table
| Test Item | Pass / Fail | Coverage | Notes |
|-----------|-------------|----------|-------|
| `test_nr_redcap_rc_ctrl.parses_valid_ul_prb_message` | Pass | RC message parsing | Confirms the new RC payload can be decoded even when parameters arrive out of order |
| `test_nr_redcap_rc_ctrl.rejects_missing_rnti_param` | Pass | RC message validation | Confirms malformed control payloads are rejected |
| `test_nr_redcap_rc_ctrl.rejects_out_of_range_rnti` | Pass | Range checking for targeted UE selection | Prevents impossible runtime targets from entering scheduler state |
| `test_nr_redcap_coreset0` new UL PRB cap cases | Pass | Helper sanitize/clamp behavior | Confirms zero disables the cap and small values are rounded to the minimum valid grant |
| Adjacent regression suite | Pass | `test_nr_redcap_bwp`, `test_nr_redcap_sdt_fsm`, `test_nr_rrc_redcap`, `test_nr_ue_redcap_bwp` | Confirms the new control path did not regress neighboring RedCap units |

## 4. 3GPP Specification Mapping
- TS 38.306 Section 4.2.21.1
  - RedCap UE remains a reduced-capability UE with a reduced bandwidth envelope; the runtime xApp cap can only tighten scheduling inside that envelope.
- TS 38.331 Section 5.2.2.4.2
  - RedCap common configuration in SIB1 provides the initial RedCap BWP context that the scheduler is already operating inside before the RC control message arrives.
- O-RAN E2SM-RC control-action definition
  - ⚠ Needs Verification: exact O-RAN clause number for the local control-action/RAN-parameter declaration used by this repo-specific RedCap action.

## 5. Practice Exercises
1. [Basic] Why does the implementation store `redcap_ul_prb_cap` per UE instead of as a single gNB-wide variable?
2. [Applied] If the xApp sends `Max UL PRB cap = 2` while the cell minimum UL grant is `4`, what effective value should the scheduler use and why?
3. [Advanced] How would you extend the same RC control path to support a second runtime knob, such as a per-UE UL MCS ceiling, without breaking the existing PRB-cap parser?
