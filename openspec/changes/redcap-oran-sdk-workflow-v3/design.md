## Context

The repo already has validated RedCap RFsim gates, FlexRIC/OAI xApp examples, and a Case A/B control-contract model. Prior project docs show that long runtime evidence can make task-control files hard to scan, so this workflow keeps project plans short and stores evidence, templates, and validation rules in separate files.

## Goals / Non-Goals

**Goals:**

- Create a compact RedCap Workflow 3.0 project scaffold.
- Use `OpenSpec -> symdex -> rtk -> Ponytail review -> marker validation -> report` as the default work route.
- Keep SDK v1 bounded to existing OAI/FlexRIC concepts: [rApp policy], [xApp C/C++ KPM/RC adapter], and [dApp/gNB guard].
- Add static checks for YAML control contracts and report templates before runtime work.
- Keep daily progress readable and Gate evidence reproducible.

**Non-Goals:**

- Do not implement SLM evaluation tooling in this change.
- Do not create a GUI, production Non-RT RIC deployment, or broad platform SDK.
- Do not claim O-RAN clause compliance until references from `../dev_refer/develop_refer_doc` are locally extracted and mapped.
- Do not modify OAI runtime behavior in the scaffold-only tasks.

## Decisions

- [Ponytail Full] is a review gate, not a replacement for OpenSpec. It removes unnecessary abstractions after the requirement and code path are understood.
- [C/C++ xApp first] is the SDK v1 default because existing FlexRIC support for E2SM-KPM/E2SM-RC is strongest in C/C++.
- [rApp] writes policy YAML only. It must not directly mutate OAI runtime state.
- [xApp] reads KPM/RC context and sends bounded requests. KPM remains observation only.
- [dApp/gNB guard] validates contract ownership, bounds, ACK/NACK, rollback, and applied-parameter markers.
- [Static CI Stage 1] uses local files and the Python standard library. Build/CTest and RFsim stay in later stages.

## Risks / Trade-offs

- [Risk] The workflow could become another long handbook. -> Mitigation: keep `project_plan.md` as an index and put templates/checklists under `validation/`.
- [Risk] Existing xApp helpers cover only a narrow control path. -> Mitigation: treat `ci-scripts/redcap_ul_prb_ctrl_xapp.c` as a seed, not a full SDK claim.
- [Risk] O-RAN references are external Office/PDF documents. -> Mitigation: mark exact clause mappings `[Needs Verification]` until converted and cited locally.
- [Risk] Static checks can create false confidence. -> Mitigation: Stage 1 checks structure only; runtime PASS still requires RedCap/O-RAN markers.
