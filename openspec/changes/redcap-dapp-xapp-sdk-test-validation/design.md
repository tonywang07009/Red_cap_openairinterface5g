## Context

Workflow v3 completed the first narrow RedCap SDK slice: xApp C/Python helpers under `openair2/E2AP/REDCAP_SDK/`, dApp C/Python guard helpers under `openair2/E3AP/`, and rApp policy packaging under the project docs. That slice only proves `redcap_ul_prb_cap` and does not prove dApp E3 behavior, SWIG-backed Python bindings, sub-10 ms control, or 64 UE / staged 5 MHz-to-20 MHz BWP behavior.

The primary references for this change are local `dev_refer/` files. `dev_refer/dapp_dev_need/libe3/` provides the E3 RAN/DAPP role model, transport/encoding choices, and optional `LIBE3_ENABLE_SWIG=ON` binding. `dev_refer/dapp_dev_need/dApp-library/` provides I/Q sample handling, PRB control, and visualization options. `dev_refer/xapp_dev_need/` remains an external xApp design input; existing OAI/FlexRIC code under `openair2/E2AP/flexric/` remains the runtime dependency for RedCap xApp work.

## Goals / Non-Goals

**Goals:**

- Define a staged validation path for dApp/xApp SDK tests.
- Add a small project area for test plans, scripts, and bilingual docs.
- Add static test helpers that can run without Docker and without rebuilding external `dev_refer/` projects.
- Require SWIG evidence before claiming Python-to-C/C++ binding.
- Preserve Workflow v3 as completed, while recording follow-up tasks when a dApp/xApp test is missing or fails.

**Non-Goals:**

- Do not claim full dApp runtime integration from static tests.
- Do not run 64 UE RFsim in this first static implementation.
- Do not copy external `dev_refer/` source trees into OAI.
- Do not invent exact O-RAN or 3GPP clause mappings; mark uncertain mappings `[Needs Verification]`.
- Do not implement a new GUI; document the existing dApp-library dashboard path and expected observation fields.

## Decisions

- [Staged gates] Use Gate A-E: SDK unit, SWIG, E3 loopback, small RFsim, and 64 UE / 5 MHz-to-20 MHz BWP stress. This prevents a 64 UE failure from hiding whether the problem is SDK logic, E3 binding, or RFsim scale.
- [dev_refer-first] Static checks must verify the expected local reference paths before passing. OpenRAN Gym remains a cross-check only.
- [Python binding honesty] Python helper files are not enough to claim Python-to-C/C++ integration. The SWIG gate must look for SWIG interface files and generated/importable modules or explicitly report a fallback.
- [xApp directs dApp] xApp computes UE priority hints; dApp owns sub-10 ms local apply/reject decisions. This follows the user-confirmed role split and keeps PUCCH/PUSCH scheduling out of the xApp.
- [dApp access-pressure policy] dApp computes bounded PUCCH/PUSCH ratio intent from RA/PUCCH collision proxy counters and I/Q availability, then routes the result through the existing PRB allocation guard.
- [Small docs] Use paired `README.en.md` and `README.zh-TW.md` with separate API/config, commands, and expected markers sections, matching `redcap_docs_interface_reorg_v1`.
- [Minimal first implementation] Add standard-library Python scripts for static contract checks and examples. Do not add dependencies or generated code until a runtime gate requires them.

## Risks / Trade-offs

- [Risk] 5 MHz BWP can fail because PUCCH resources are constrained after the profile maps to a small PRB budget. -> Mitigation: treat 32 UE / 5 MHz as the first pressure stage, then expand to 64 UE / 20 MHz only after Gate D evidence exists.
- [Risk] first32 can avoid the PUCCH reservation assert and remove the previous Msg4 VRB overlap marker, but still fail before attach if connected common-search-space DCI uses the regular initial BWP instead of the RedCap SIB1 initial BWP. -> Mitigation: preserve RedCap initial DL/UL BWP start/size for connected DCI, require `[RedCap RA][gNB DCI BWP]` runtime evidence, and keep SRB1/UL-DCCH delivery as the next pull item only after the DCI BWP marker is proven.
- [Risk] `dev_refer/` projects may have build dependencies not installed locally. -> Mitigation: first static gate checks reference shape and SWIG definitions; runtime SWIG build remains a later gate.
- [Risk] E3 loopback may not map cleanly to current OAI runtime. -> Mitigation: define loopback as a separate Gate C before RFsim.
- [Risk] PDCCH command wording may overclaim implementation. -> Mitigation: document PDCCH hook as `[Needs Verification]` until source-level and marker evidence exists.
