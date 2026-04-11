# RedCap M2 Learning Report

## 1. Technical Background
RedCap UE in Rel-17 is a reduced-capability NR UE. On the UE side, two checks matter as soon as SIB1 is decoded. First, a half-duplex-only FDD RedCap UE cannot treat a cell as attachable when SIB1 omits `halfDuplexRedCapAllowed-r17`. Second, the network may selectively bar RedCap UEs by receive-branch capability through `cellBarredRedCap1Rx-r17` and `cellBarredRedCap2Rx-r17`. This means M2 is not only an ASN.1 wiring task; it directly controls whether MAC is allowed to start RA after SIB1 delivery. In parallel, the UE capability container must advertise the minimum RedCap capability chain the gNB expects, including `supportOfRedCap-r17`, optional `supportOf16DRB-RedCap-r17`, and the RedCap long-SN flags used by PDCP/RLC handling. The work in this unit therefore focused on two measurable outcomes: making the RedCap helper logic independently testable, and proving that both the SIB1 RedCap IE path and the UE capability container survive UPER encode/decode without ASN.1 failure.

## 2. Key C functions / Data structures utilized
- `nr_rrc_build_redcap_ue_capability()` in `openair2/RRC/NR_UE/rrc_ue_redcap.c`
- `nr_rrc_redcap_sib1_access_allowed()` in `openair2/RRC/NR_UE/rrc_ue_redcap.c`
- `NR_SIB1_v1700_IEs_t`
- `NR_RedCap_ConfigCommonSIB_r17_t`
- `NR_UE_NR_Capability_t`
- `uper_encode_to_new_buffer()` / `uper_decode_complete()`
- `nr_ue_get_sib1_initial_dl_bwp()` / `nr_ue_get_sib1_initial_ul_bwp()`

## 3. Test Results Summary Table
| Test Item | Pass / Fail | Coverage | Notes |
|-----------|-------------|----------|-------|
| `test_nr_rrc_redcap.HalfDuplexOnlyUeRequiresHalfDuplexSib1Flag` | Pass | `halfDuplexRedCapAllowed-r17` omission handling | Confirms barred behavior for half-duplex-only UE |
| `test_nr_rrc_redcap.OneRxAndTwoRxBarringFollowSib1Fields` | Pass | `cellBarredRedCap1Rx/2Rx` gating | Confirms Rx-branch-specific barring |
| `test_nr_rrc_redcap.SIB1RedCapFieldsEncodeAndDecodeWithoutAsn1Error` | Pass | `NR_SIB1_v1700_IEs` UPER round-trip | Confirms RedCap SIB1 fields survive encode/decode |
| `test_nr_rrc_redcap.CapabilityBuilderCreatesMinimalRedCapContainerAndRoundTrips` | Pass | `NR_UE_NR_Capability` RedCap container | Confirms minimal capability builder is ASN.1-safe |
| Adjacent regression suite | Pass | `test_nr_ue_redcap_bwp`, `test_nr_redcap_bwp`, `test_nr_redcap_coreset0`, `test_nr_redcap_sdt_fsm` | Confirms no regression in neighboring RedCap paths |

## 4. 3GPP Specification Mapping
- TS 38.331 Section 5.2.2.4.2
  - If `halfDuplexRedCapAllowed` is absent in acquired SIB1 and the UE supports only half-duplex FDD, the cell is treated as barred.
- TS 38.331 Section 5.2.2.4.2
  - `cellBarredRedCap1Rx` and `cellBarredRedCap2Rx` allow the network to bar RedCap UEs by 1Rx or 2Rx capability on the selected band.
- TS 38.306 Section 4.2.21.1
  - RedCap UE is defined as a reduced-capability UE; capability signaling includes `supportOfRedCap-r17` and related RedCap feature components.
- TS 38.331 ASN.1 `SIB1-v1700-IEs` / `RedCap-ConfigCommonSIB-r17`
  - ⚠ Needs Verification: exact clause number for the ASN.1 definition section.

## 5. Practice Exercises
1. [Basic] Why must a half-duplex-only FDD RedCap UE reject a cell when `halfDuplexRedCapAllowed-r17` is absent from SIB1?
2. [Applied] If `cellBarredRedCap1Rx-r17=barred` and `cellBarredRedCap2Rx-r17=notBarred`, what should happen for a 1Rx RedCap UE and for a 2Rx RedCap UE? Explain using the UE-side decision path.
3. [Advanced] Suppose you need to extend the helper so the UE also validates future eRedCap SIB1 fields. Which parts should remain generic ASN.1 utilities, and which parts should stay policy-specific to RedCap/eRedCap access logic?
