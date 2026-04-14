# RedCap mMTC Project Plan — Codex Agent Work Log
# Version: 3.1 | Language: English
# Target: OpenAirInterface (OAI) 5G NR, FR1, 3GPP Rel-17 RedCap
# Research Focus: Compose-based scalable RedCap/mMTC runtime architecture and UPLINK scheduling under RedCap constraints
# Last updated: 2026-04-13

You are a senior embedded systems and 5G RAN engineer acting as a
Codex coding agent. Execute the following milestones sequentially.
After each milestone, output a brief summary of changes made,
list all new/modified files, and wait for confirmation before
proceeding to the next milestone.

Strict rules:
- Never fabricate 3GPP clause numbers; mark uncertain references
  as [VERIFY AGAINST 3GPP SPEC].
- Do not mix parameters across different 3GPP releases.
- All new functions must include Doxygen-style doc comments.
- All throughput tests target UPLINK direction only.
  Do NOT use -R (reverse) flag in any iperf3 command.
- After completing each milestone, auto-update the progress
  tracker at the bottom of this file.

Repository alignment notes:
- Use existing repo paths when the target path below is intent-level only.
  Example: prefer `doc/` over `docs/` when `docs/` does not exist yet.
- Canonical daily work log path is `test_logs/work_daily/`.
  Treat `test_log/work_daily/` as a legacy mirror if it exists.
- Current project scope priority:
  [Primary deliverables] are [PHY / MAC RedCap behavior] plus a
  [compose-based RedCap / mMTC runtime architecture] rooted in the
  vendor-working `ci-scripts/yaml_files/5g_rfsimulator_flexric/`
  topology.
  `ci-scripts/yaml_files/5g_rfsimulator_flexric_redcap/` must be
  treated as a [delta-compatible runtime path] layered on top of that
  working FlexRIC compose, not as a separate long-term architecture.
  Mandatory Milestone 5 runtime deliverables are now split into:
  - [Fixed-UE validation path]:
    keep named `oai-nr-ue1` / `oai-nr-ue2` for CI/runtime evidence
    such as `[UE1 normal]` vs `[UE2 RedCap]`.
  - [Scalable mMTC path]:
    add a Compose-driven scaling model for [30+ UE], while preserving
    [docker compose] as the operator-facing launch interface.
  New XML scenarios, extra manuals, or generic CI scaffolding are
  [optional validation assets], not mandatory milestone outputs,
  unless the compose-based scaling path is insufficient.
- Progress tracker legend:
  `[x]` = complete, `[~]` = partial/in progress,
  `[!]` = blocked by environment, `[ ]` = not started.
- Current known environment blocker:
  Docker socket access is unavailable in the present sandbox,
  so Milestone 5 runtime evidence must still be collected on
  a host with Docker privileges.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
## Milestone 1: Hardware / PHY Constraints
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Tasks:
1. Define FR1 bandwidth and PRB limits for RedCap UE:
   - Max BW: 20 MHz for FR1
   - Supported SCS: 15 kHz and 30 kHz
   - Enforce PRB count caps per SCS in PHY layer config structs.

2. Implement antenna configuration constraints:
   - DL: 1Rx mandatory, 2Rx optional, max DL layers = 2
   - UL: No MIMO (single antenna only)
   - Add compile-time or runtime assertion guards.

3. Implement Half-Duplex FDD Type A timing assumptions:
   - Add HD-FDD flag to UE capability struct.
   - Enforce Tx/Rx switching gap in UL scheduler.

Target files (expected):
  openair1/PHY/NR_TRANSPORT/redcap_phy_init.c
  openair1/PHY/NR_TRANSPORT/redcap_phy_init.h
  openair2/LAYER2/NR_MAC_gNB/nr_mac_redcap.h

Acceptance criteria:
  - PHY init passes with RedCap-constrained parameters.
  - Unit test: assert PRB count does not exceed 106 PRBs
    (20 MHz / 15 kHz SCS).

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
## Milestone 2: RRC / SIB1 Support
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Tasks:
1. Design `RedCap_SIB1` configuration struct containing:
   - `redCap-ConfigCommon-r17`
   - `halfDuplexRedCapAllowed` (bool)
   - `cellBarredRedCap1Rx` (bool)
   - `cellBarredRedCap2Rx` (bool)
   Map each field to its corresponding clause in TS 38.331
   as inline comments. Mark any uncertain mappings as
   [VERIFY AGAINST TS 38.331].

2. Implement:
   - `fill_redcap_sib1()` — gNB side, populates SIB1 IE
   - `parse_redcap_sib1()` — UE side, reads and validates IE

3. Integrate both functions into the existing OAI RRC
   SIB1 generation and parsing pipeline.

Target files (expected):
  openair2/RRC/NR/rrc_gNB_sib1.c
  openair2/RRC/NR/rrc_UE_sib1.c
  openair2/RRC/NR/MESSAGES/asn1_msg_redcap.h

Acceptance criteria:
  - SIB1 encodes and decodes RedCap fields without ASN.1 error.
  - `cellBarredRedCap1Rx = true` blocks 1Rx UE attachment
    in loopback test.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
## Milestone 3: BWP & CORESET#0
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Scope boundary:
- [In scope]:
  - RedCap-specific [BWP / CORESET#0 / scheduler] logic in
    existing [MAC / gNB config / UE config parse] code paths.
  - Config schema and runtime parameters required so an existing
    RedCap gNB YAML and RedCap UE YAML can drive the behavior.
- [Out of scope]:
  - Creating a brand-new XML scenario as a required deliverable.
  - Producing extra project documentation beyond minimal code/test notes.

Tasks:
1. Define RedCap-specific BWP structs for:
   - DL Initial BWP (max 20 MHz)
   - UL Initial BWP (max 20 MHz)
   Apply PRB offset and size constraints from Milestone 1.

2. Handle CORESET#0 special cases:
   - Case A (full-cell): standard CORESET#0 placement.
   - Case B (edge-only): configure `commonControlResourceSet`
     with edge-aligned PRB allocation.
   Add a runtime selector flag `coreset0_redcap_mode`
   in gNB config.

3. Validate scheduler changes:
   - Validate with the existing
     `ci-scripts/yaml_files/5g_rfsimulator_flexric_redcap/`
     compose path using a RedCap gNB YAML plus RedCap UE YAML.
   - Confirm PDCCH decoding succeeds for both Case A and B.

Status note [2026-04-10]:
- Added [Case A / Case B] runtime helpers:
  - `ci-scripts/redcap_prepare_runtime_config.py`
  - `ci-scripts/redcap_runtime_host_validation.sh`
  - `ci-scripts/redcap_runtime_case_matrix.sh`
- Local sandbox check now runs both modes sequentially, but actual [rfsimulation]
  remains [BLOCKED] here because `run_locally.sh` requires Docker access.
- These runtime helpers are [supporting validation tooling]. They are
  not the primary implementation target for Milestone 3.

Target files (expected):
  openair2/GNB_APP/gnb_config.c                     (modified)
  openair2/LAYER2/NR_MAC_gNB/nr_mac_redcap_bwp.c
  openair2/LAYER2/NR_MAC_gNB/nr_mac_redcap_bwp.h
  openair2/LAYER2/NR_MAC_gNB/nr_mac_sched.c  (modified)
  openair2/LAYER2/NR_MAC_gNB/nr_radio_config.c      (modified)
  ci-scripts/conf_files/gnb.sa.band78.fr1.106PRB.usrpb210.redcap.yaml
  ci-scripts/conf_files/nrue_recap/nrue*.uicc.yaml  (only when runtime
    parameters are required to exercise RedCap behavior)

Acceptance criteria:
  - BWP init completes without assertion failure.
  - CORESET#0 Case B allocates PRBs only at cell edge.
  - Existing `5g_rfsimulator_flexric_redcap/docker-compose.yml`
    can point to a RedCap-capable gNB YAML and RedCap UE YAML without
    requiring a new orchestration format.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
## Milestone 4: SDT / RRC_INACTIVE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Tasks:
1. Add RRC_INACTIVE support flags:
   - gNB: `redcap_inactive_allowed` in gNB config struct.
   - UE: `redcap_rrc_state` enum
     { IDLE, INACTIVE, CONNECTED }.

2. Design SDT scheduler state machine:
   - States: IDLE → SDT_TRIGGER → MsgA_PATH or Msg3_PATH
             → SDT_ACTIVE → INACTIVE
   - Implement `sdt_scheduler_fsm()` with explicit
     state transition guards.
   - Add path selection logic based on data size threshold
     [VERIFY AGAINST TS 38.321 SDT procedure].

3. Add unit tests and simulation scenarios:
   - Test SDT MsgA path with small UL payload (< 256 bytes).
   - Test Msg3 fallback path with larger UL payload.
   - Log state transitions to file for verification.

Status note [2026-04-10]:
- Added `openair2/LAYER2/NR_MAC_gNB/nr_mac_sdt_fsm.[ch]`
  as a minimal SDT scheduler FSM skeleton.
- Added `redcap_inactive_allowed` gNB flag and UE-side `redcap_rrc_state`
  plumbing for [IDLE / INACTIVE / CONNECTED] tracking.
- Added unit test `test_nr_redcap_sdt_fsm`, but full scheduler wiring and
  [MsgA simulation] are still pending.

Target files (expected):
  openair2/RRC/NR/rrc_gNB_redcap_inactive.c
  openair2/RRC/NR/rrc_UE_redcap_inactive.c
  openair2/LAYER2/NR_MAC_gNB/nr_mac_sdt_fsm.c
  tests/redcap/test_sdt_fsm.c

Acceptance criteria:
  - FSM reaches SDT_ACTIVE state in MsgA simulation.
  - State transition log matches expected sequence.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
## Milestone 4-B: DRX / eDRX / PSM Low-Power Operation
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Rationale:
- [mMTC / RedCap] 的核心價值不只在 [smaller BWP]，也在 [battery life]。
- 現有 plan 尚未把 [Connected DRX]、[Idle/Inactive eDRX]、[PSM] 納入正式 deliverables。
- [2026-04-12 symdex gap scan] 顯示：
  - [NR Connected DRX] 在 UE config path 仍顯示 `DRX not implemented!`
  - [NR eDRX] 目前只看到 ASN.1 field，未見 SIB1 encode / parse / runtime wiring
  - [PSM] 在此 repo 只看到 legacy [EPS T3412] timer handling，未見 [T3324 / 5GS PSM negotiation] path

Sub-task breakdown:
1. Task Name: [NR Connected DRX]
   - Corresponding 3GPP Spec Clause:
     - TS 38.321 Section 5.7
     - TS 38.331 [VERIFY AGAINST TS 38.331 dedicated `drx-Config` clause]
   - Prerequisite Tasks:
     - [Milestone 2: RRC / SIB1 Support]
     - [Milestone 3: BWP & CORESET#0]
     - [Milestone 4: SDT / RRC_INACTIVE]

2. Task Name: [NR eDRX for RRC_IDLE / RRC_INACTIVE]
   - Corresponding 3GPP Spec Clause:
     - TS 38.331 [VERIFY AGAINST clause for `eDRX-AllowedIdle-r17`]
     - TS 38.331 [VERIFY AGAINST clause for `eDRX-AllowedInactive-r17`]
   - Prerequisite Tasks:
     - [Milestone 2: RRC / SIB1 Support]
     - [Milestone 4: SDT / RRC_INACTIVE]

3. Task Name: [PSM / NAS timer integration]
   - Corresponding 3GPP Spec Clause:
     - [VERIFY AGAINST TS 24.501 for `T3324` / periodic registration update / PSM]
   - Prerequisite Tasks:
     - [Milestone 4: SDT / RRC_INACTIVE]
     - [Milestone 5: existing RFsim SA integration path]
     - [External dependency: CN/AMF behavior outside this repo]

Tasks:
1. Implement [Connected Mode DRX] for NR UE/gNB:
   - Parse and apply dedicated `drx-Config` instead of logging
     `DRX not implemented!`.
   - Add local timer/state handling for:
     - `drx-onDurationTimer`
     - `drx-InactivityTimer`
     - `drx-LongCycleStartOffset`
     - `drx-ShortCycle` [optional]
   - Ensure UE MAC and gNB scheduling decisions are aligned with
     [TS 38.321 Section 5.7].

2. Implement [Idle / Inactive eDRX] exposure and handling:
   - Add SIB1 support for:
     - `eDRX-AllowedIdle-r17`
     - `eDRX-AllowedInactive-r17`
   - Add UE-side parsing and state gating for [RRC_IDLE] and
     [RRC_INACTIVE] paging behavior.
   - Reuse the [RRC_INACTIVE] plumbing from [Milestone 4] where possible.

3. Plan and implement [PSM] interface hooks:
   - Add UE-side logging and state tracking for [T3324 / T3412-like]
     low-power timers [VERIFY AGAINST TS 24.501].
   - Document CN/AMF dependencies explicitly because full PSM
     negotiation is outside pure RAN scope.
   - Add host/runtime validation steps that confirm whether the UE
     received and applied the target NAS timers.

4. Add test and validation assets:
   - Unit test for [NR DRX] timer configuration acceptance.
   - Host/runtime validation for [eDRX SIB1 fields] in logs or decoded ASN.1.
   - Host/runtime validation for [PSM timer presence] in NAS logs.

Status note [2026-04-12]:
- [Connected DRX / NR] is [NOT IMPLEMENTED] end-to-end in the current repo.
  Evidence:
  - `openair2/LAYER2/NR_MAC_UE/config_ue.c` logs
    `DRX not implemented! Configuration not handled!`
- [DRX MAC CE / paging DRX] has partial skeleton code paths,
  but this is not equivalent to [working NR CDRX].
- [eDRX] currently appears only in ASN.1 definitions and not in
  active NR RRC runtime wiring.
- [PSM] is not implemented for the current [NR RedCap + 5GC] path in this repo.

Target files (expected):
  openair2/LAYER2/NR_MAC_UE/config_ue.c            (modified)
  openair2/LAYER2/NR_MAC_gNB/gNB_scheduler_dlsch.c (modified)
  openair2/LAYER2/NR_MAC_gNB/gNB_scheduler.c       (modified)
  openair2/RRC/NR/rrc_gNB.c                        (modified)
  openair2/RRC/NR_UE/rrc_UE.c                      (modified)
  openair2/RRC/NR/MESSAGES/ASN.1/nr-rrc-17.3.0.asn1 (reference only)
  ci-scripts/conf_files/gnb.sa.band78.fr1.106PRB.usrpb210.redcap.yaml
  ci-scripts/conf_files/nrue_recap/nrue*.uicc.yaml

Acceptance criteria:
  - [NR Connected DRX] no longer logs [not implemented] when dedicated
    `drx-Config` is present.
  - [eDRX-AllowedIdle-r17] and [eDRX-AllowedInactive-r17] can be
    encoded/decoded and verified in the RedCap runtime path.
  - [PSM] scope and dependency boundary are explicitly documented,
    with at least one reproducible host-side validation step for NAS timers.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
## Milestone 5: Compose Architecture, Integration & UL Throughput Targets
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Research note: This project targets UPLINK scheduling.
All throughput validation must measure UL direction.

Scope boundary:
- [In scope]:
  - Rebase the RedCap runtime path on the vendor-working
    `ci-scripts/yaml_files/5g_rfsimulator_flexric/docker-compose.yml`
    architecture.
  - Keep `ci-scripts/yaml_files/5g_rfsimulator_flexric_redcap/`
    as a [base-compatible derivative] that carries RedCap-specific
    deltas only.
  - Preserve a [fixed-UE validation path] with named
    `oai-nr-ue1` / `oai-nr-ue2` services for CI/runtime evidence.
  - Add a [scalable mMTC path] that can grow beyond [30 UE]
    while staying inside a [docker compose] launch model.
  - Use optional XML / host wrappers only as debugging, regression,
    or evidence-collection helpers.
- [Out of scope]:
  - Maintaining a structurally divergent handcrafted RedCap compose
    when the vendor FlexRIC compose can be reused as the base.
  - Requiring a non-Compose orchestration model for the target runtime.
  - Treating XML/runtime helper scripts as the primary deliverable.

Tasks:
1. Rebase the RedCap runtime compose architecture:
   - Use `ci-scripts/yaml_files/5g_rfsimulator_flexric/docker-compose.yml`
     as the [source-of-truth architecture] for:
       service ordering,
       external CN networking,
       multi-UE service shape,
       and FlexRIC wiring.
   - Refactor
     `ci-scripts/yaml_files/5g_rfsimulator_flexric_redcap/docker-compose.yml`
     so it remains [base-compatible] with the vendor FlexRIC compose and
     carries only RedCap-specific deltas:
       RedCap gNB YAML,
       RedCap UE YAML,
       RedCap capability options,
       and runtime validation-specific overrides.

2. Preserve the fixed-UE validation path:
   - Keep named `oai-nr-ue1` and `oai-nr-ue2` services for CI/runtime
     evidence.
   - Preserve the semantics:
       `UE1 = baseline / non-RedCap`
       `UE2 = RedCap`
   - Ensure this path remains launchable with `docker compose up`
     and stays compatible with the existing XML/runtime wrappers.

3. Add a scalable mMTC / RedCap UE path:
   - Introduce a scale-friendly UE service such as
     `oai-nr-ue-mmtc` or an equivalent generated Compose overlay.
   - Runtime generation logic must derive, per UE instance:
       IMSI,
       mounted `nr-ue` YAML,
       RedCap enable flag,
       optional half-duplex capability,
       and telnet / listen parameters.
   - The operator-facing workflow must remain Docker Compose-based and
     continue to center on `docker compose up`.
   - Preferred day-to-day UX:
       `docker compose -f docker-compose.yml -f docker-compose.mmtc.yml up -d`
   - A generated Compose override / overlay is the preferred way to keep
     a [pure `docker compose up`] workflow while materializing [30+ UE].
   - `docker compose up --scale oai-nr-ue-mmtc=<N> -d` may remain as an
     engineering shortcut or secondary workflow, but it must not be the
     only scalable operator path.
   - First scaling target:
       [32 UE]
     Follow-up target:
       [64 UE]

4. Run end-to-end simulation in two layers:
   - [Fixed-UE validation layer]:
       mysql → oai-amf → oai-smf → oai-upf
        → nearRT-RIC (FlexRIC, 192.168.70.180)
           → oai-gnb (RedCap config + e2_agent)
             → oai-nr-ue1 (baseline UE)
               → oai-nr-ue2 (RedCap, 1Rx, HD-FDD)
                 → oai-ext-dn (iperf3 server)
   - [Scalable mMTC layer]:
       same CN + RIC + gNB base
         → `oai-nr-ue-mmtc[*]` instances under Compose scaling
         → attach / ping / smoke throughput validation on a subset

   UL throughput test procedure for the fixed validation path:

   Step 1 — Start iperf3 server on the core network side:
     docker exec -d rfsim5g-oai-ext-dn iperf3 -s

   Step 2 — Start UL traffic from UE (client pushes to core):
     docker exec -it rfsim5g-oai-nr-ue2_redcap \
       iperf3 -c 12.1.1.1 \
       -u \
       -b 50M \
       -t 30 \
       -B 12.1.1.2 \
       --logfile /tmp/redcap_ul_result.json -J

     Flag reference:
       -c 12.1.1.1  : ext-dn IP (core network receiver)
       -u           : UDP mode, reflects mMTC burst behavior
       -b 50M       : UL target ceiling for RedCap UE
       -t 30        : test duration 30 seconds
       -B 12.1.1.2  : bind to oaitun_ue1 TUN interface,
                      ensures traffic routes through 5G PDU
                      session (not bypassed)
       -J           : JSON output for machine parsing
     NOTE: Do NOT use -R flag. -R reverses to DL direction.

5. Implement `redcap_tput_logger()` only if throughput post-processing
   is still missing after the compose-based integration is stable:
   - Input:  /tmp/redcap_ul_result.json (iperf3 JSON)
   - Output CSV columns:
       timestamp, interval_sec, throughput_ul_mbps, lost_packets,
       jitter_ms
   - Print PASS if mean throughput_ul_mbps >= 30, else FAIL.

6. Document open gaps vs. full 3GPP Rel-17 RedCap compliance and
   scaling readiness only as a lightweight closing artifact after
   the architecture rebase is working:
   - Use tags: [IMPLEMENTED], [PARTIAL], [NOT IMPLEMENTED].
   - Explicitly note whether each gap applies to:
       [fixed-UE validation path],
       [scalable mMTC path],
       or [both].

Target files (expected):
  ci-scripts/yaml_files/5g_rfsimulator_flexric/docker-compose.yml  (reference baseline)
  ci-scripts/yaml_files/5g_rfsimulator_flexric_redcap/docker-compose.yml
  ci-scripts/yaml_files/5g_rfsimulator_flexric_redcap/docker-compose.mmtc.yml  (new overlay or generated target)
  ci-scripts/yaml_files/5g_rfsimulator_flexric_redcap/scripts/ue_mmtc_entrypoint.sh
  ci-scripts/conf_files/gnb.sa.band78.fr1.106PRB.usrpb210.redcap.yaml
  ci-scripts/conf_files/nrue_recap/nrue*.uicc.yaml
  common/utils/redcap_tput_logger.py
  doc/redcap_compliance_gap.md  (optional)

Acceptance criteria:
  - `5g_rfsimulator_flexric_redcap/docker-compose.yml` remains
    structurally aligned with the vendor
    `5g_rfsimulator_flexric/docker-compose.yml` service model.
  - The fixed-UE path still launches with Docker Compose and retains
    runtime evidence for:
      `[UE1 normal]`,
      `[UE2 RedCap]`,
      `[302003]`,
      `[302004]`,
      and E2/xApp control checks.
  - The scalable mMTC path can launch [>30 UE] without manually
    hand-writing one static UE service block per new UE.
  - The preferred scalable operator workflow remains
    `docker compose up` through a generated or maintained
    Compose overlay / override.
  - `docker compose up --scale oai-nr-ue-mmtc=<N> -d`
    may be supported as a secondary engineering workflow, but
    the project must not depend solely on that command for
    [30+ UE] operation.
  - iperf3 reports >= 30 Mbps sustained UL throughput.
  - No traffic bypasses the TUN interface (verify via
    `ip route` inside UE container).
  - The runtime evidence also retains the DL control-plane check:
    `[302003]` must confirm `SIB1 RedCap initial DL BWP` appears in the
    gNB log while UL throughput cases remain UL-only.
  - The runtime evidence also confirms the E2/xApp control path:
    `[302005]` / `[302006]` must show `RedCap UL PRB control RNTI`
    in the gNB log before the capped UL follow-up case.
  - Existing Compose-based launch remains the mandatory operator path.

Status note [2026-04-13]:
- Host runtime on a Docker-enabled machine surfaced CI/runtime blockers
  before [attach] execution:
  - `cls_containerize.py` used a removed `jq` dependency and crashed on a
    bad error variable path.
  - `oai-cn5g-public-net` was constrained to `192.168.70.128/26`, which
    blocked UE containers using `192.168.71.x` static IPs.
  - `nearRT-RIC` in `5g_rfsimulator_flexric_redcap/docker-compose.yml`
    was overridden with `sleep infinity`, so the E2 path never came up.
- All three blockers are now patched locally; host rerun is still required
  to confirm [333332] / [302002] / [302003] / [020005] / [030001] / [030002].
- Local runtime asset cleanup also completed:
  - compose defaults now preserve the scenario semantics
    `[UE1 = non-RedCap]` / `[UE2 = RedCap]`
  - compose and host validation wrappers now support gNB / UE1 / UE2
    config overrides through environment variables
  - the RedCap RF-sim XML scenario is now [UL-only] again; the previous
    DL `-R` iperf case was replaced with a `UL/50M/UDP` case to match
    the project throughput policy
  - `[302003]` remains the explicit DL control-plane validation for
    the fixed-UE path while UL throughput cases remain UL-only.
- New project-direction update:
  - `5g_rfsimulator_flexric/` is now the agreed [source-of-truth architecture].
  - `5g_rfsimulator_flexric_redcap/` must be rebased as a
    [delta-compatible derivative] instead of continuing as an
    independently evolving compose architecture.
  - The current `UE2` user-plane blocker in the fixed validation path
    should now be debugged in the context of that architecture rebase,
    not by growing more ad-hoc scenario-specific patches.
  - [30+ UE mMTC scaling under Docker Compose] is now an explicit
    Milestone 5 deliverable, with [32 UE] as the first formal target.
  - The preferred user-facing launch workflow must remain
    [docker compose up]; generated overlays or templates are preferred
    over manually hand-maintaining dozens of static UE blocks.
- Existing XML / case-matrix helpers may still be retained for regression
  debugging, but they are [secondary] to the compose-based integration path.

Status note [2026-04-12]:
- Added a host-side FlexRIC RC control injection path for the RedCap UL PRB cap:
  - `ci-scripts/redcap_ul_prb_ctrl_xapp.c`
  - `ci-scripts/redcap_send_ul_prb_control.sh`
- The RedCap RF-sim XML runtime now inserts:
  - `[302005]` apply E2/xApp RedCap UL PRB cap
  - `[302006]` verify gNB applied the cap
- Local sandbox validation remains [BLOCKED] for the live Docker path, but the
  new helper can now be compiled and dry-run checked without requiring a full
  end-to-end host rerun in this environment.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
## Milestone 6: Conclusion & Documentation Generation
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

### 6-A: Tutorial Manual

Generate a Markdown tutorial manual at:
  docs/tutorial_redcap_rfsim.md

--- Chapter 1: Environment Setup ---
  List Docker image versions for all services:
    oai-gnb, oai-nr-ue, oai-amf, oai-smf,
    oai-upf, oai-ext-dn, oai-flexric (nearRT-RIC).
  Describe RedCap config file locations and naming rules.
  Prerequisites: Docker >= 20.10, docker-compose >= 1.29,
    iperf3 >= 3.9, Python >= 3.10.

--- Chapter 2: Launching rfsimulation with RedCap ---
  Provide exact shell commands with per-flag annotations:

  (a) Start gNB (FR1, SCS 30 kHz, BW 20 MHz, E2 enabled):
      sudo ./nr-softmodem --rfsim \
        -O ci-scripts/conf_files/gnb.sa.band78.fr1.106PRB.usrpb210.redcap.yaml \
        --gNBs.[0].min_rxtxtime 6 \
        --MACRLCs.[0].ul_max_mcs 20

      Flag annotations:
        --rfsim               : enable RF simulator (no SDR HW needed)
        -O <redcap gNB yaml>  : load RedCap-specific gNB YAML
                                including e2_agent block (M5)
        --min_rxtxtime 6      : HD-FDD Tx/Rx switching gap (M1)
        --ul_max_mcs 20       : cap UL MCS for RedCap UE (M1)

  (b) Start RedCap UE (1Rx, HD-FDD):
      sudo ./nr-uesoftmodem --rfsim \
        --rfsimulator.serveraddr <GNB_IP> \
        -O ci-scripts/conf_files/nrue_recap/nrue2.uicc.yaml \
        --ue-nb-ant-rx 1 \
        --nokrnmod 1

      Flag annotations:
        --rfsimulator.serveraddr : gNB container IP for RF link
        -O <redcap ue yaml>      : UE2 RedCap YAML (SCS/BW/HD-FDD)
        --ue-nb-ant-rx 1         : enforce 1Rx antenna (M1 mandatory)
        --nokrnmod 1             : use TUN interface, required for
                                   Docker iperf routing (M5)

--- Chapter 3: UL Throughput Test Design ---
  Research context: All tests measure UPLINK scheduling
  performance. Do not use reverse (-R) mode.

  Step 1 — Start iperf3 server (core network side):
    docker exec -d rfsim5g-oai-ext-dn iperf3 -s

  Step 2 — Run UL throughput test from UE container:
    docker exec -it rfsim5g-oai-nr-ue2_redcap \
      iperf3 -c 12.1.1.1 \
      -u -b 50M -t 30 \
      -B 12.1.1.2 \
      --logfile /tmp/redcap_ul_result.json -J

  Step 3 — Parse and evaluate result:
    python3 common/utils/redcap_tput_logger.py \
      --input /tmp/redcap_ul_result.json

  Expected output format:
    timestamp, interval_sec, throughput_ul_mbps,
    lost_packets, jitter_ms
    ...
    Result: PASS (mean UL >= 30 Mbps) or FAIL

  Verification step — Confirm traffic uses 5G PDU Session:
    docker exec -it rfsim5g-oai-nr-ue2_redcap \
      ip route show table all | grep oaitun_ue1

--- Chapter 4: Docker Deployment ---
  [Architecture rule]:
    Use `ci-scripts/yaml_files/5g_rfsimulator_flexric/docker-compose.yml`
    as the [source-of-truth architecture].
    Treat `5g_rfsimulator_flexric_redcap/` as a [delta-compatible]
    extension carrying:
      RedCap gNB config,
      RedCap UE config,
      and mMTC scaling overlays.

  Full service dependency order:

    mysql
      └─► oai-amf
            └─► oai-smf
                  └─► oai-upf
                        └─► nearRT-RIC  (FlexRIC, 192.168.70.180)
                              └─► oai-gnb  (RedCap + e2_agent)
                                    └─► oai-nr-ue1  (baseline UE)
                                          └─► oai-nr-ue2  (RedCap, 1Rx, HD-FDD)
                                                └─► oai-ext-dn  (iperf3)

  [Fixed-UE validation path] launch command:
    docker compose -f doc/tutorial_resources/oai-cn5g/docker-compose.yaml up -d
    docker compose -f ci-scripts/yaml_files/5g_rfsimulator_flexric_redcap/docker-compose.yml \
      up -d nearRT-RIC oai-gnb oai-nr-ue1 oai-nr-ue2 xapp-rc-moni

  [Scalable mMTC path] launch command:
    docker compose -f doc/tutorial_resources/oai-cn5g/docker-compose.yaml up -d
    docker compose \
      -f ci-scripts/yaml_files/5g_rfsimulator_flexric_redcap/docker-compose.yml \
      -f ci-scripts/yaml_files/5g_rfsimulator_flexric_redcap/docker-compose.mmtc.yml \
      up -d

  [Secondary engineering shortcut]:
    docker compose \
      -f ci-scripts/yaml_files/5g_rfsimulator_flexric_redcap/docker-compose.yml \
      up --scale oai-nr-ue-mmtc=<N> -d

  Health-check steps for the [fixed-UE validation path]:
    1. Confirm E2 SCTP link:
         docker logs rfsim5g-oai-gnb_redcap | grep "E2 Setup Response"
    2. Confirm RedCap SIB1 DL control-plane marker:
         docker logs rfsim5g-oai-gnb_redcap | grep "SIB1 RedCap initial DL BWP"
    3. Confirm UE2 attached as RedCap:
         docker logs rfsim5g-oai-gnb_redcap | grep -E "UE with RNTI [0-9a-f]{4} is RedCap"
    4. Confirm TUN interface exists in UE2 container:
         docker exec rfsim5g-oai-nr-ue2_redcap ip addr show oaitun_ue1

  Health-check steps for the [scalable mMTC path]:
    1. Confirm the overlay created the expected [30+ UE] service set.
    2. Confirm a sampled subset of UEs receives:
         IMSI,
         PDU session IP,
         and `oaitun_ue1`.
    3. Confirm attach / ping / smoke UL traffic on a subset instead of
       requiring full iperf on every UE instance.
    4. Confirm the launch workflow remains centered on
         `docker compose up`
       rather than manually expanding static UE service blocks.

--- Chapter 5: Integration with xApp / rApp / dApp ---
  Integration path table:

  | Interface | Component      | Control Target         | Notes                    |
  |-----------|----------------|------------------------|--------------------------|
  | E2        | xApp (near-RT) | UL PRB allocation, MCS | FlexRIC e2sm_rc          |
  | E2 (RT)   | dApp           | Real-time UL HARQ      | OAI dApp, shared E2 path |
  | O1        | rApp (non-RT)  | RedCap policy push     | [VERIFY WITH OAI REPO]   |

  Routing design:
  - E2 interface (xApp and dApp):
      gNB connects via SCTP to nearRT-RIC at port 36421.
      No additional Docker flags needed beyond e2_agent
      block in the mounted RedCap gNB YAML (already set in M5).
      xApp and dApp share the same E2 path inside FlexRIC.

  - O1 interface (rApp):
      [NOT IMPLEMENTED — VERIFY OAI O1 NETCONF STATUS]
      If supported, requires separate O1 agent container
      and additional gNB config section.

  Extra Docker flags required per interface:

  | Interface | Required Extra Flag / Config      | docker-compose change |
  |-----------|-----------------------------------|-----------------------|
  | E2/xApp   | e2_agent block in RedCap gNB YAML | Add nearRT-RIC service|
  | E2/dApp   | Same as xApp, no extra flag       | None (shared service) |
  | O1/rApp   | [VERIFY — not implemented]        | TBD                   |

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

### 6-B: Reference Manual

Generate a Markdown reference manual at:
  docs/reference_redcap_functions.md

--- Chapter 1: New Function Index ---
  Scan all diffs from Milestones 1–5.
  For each new function, generate one entry block:

    Function:     <function_name>()
    File:         <relative/path/to/file.c>
    Description:  <one-sentence summary>
    Parameters:
      - <param_name> (<type>): <description>
    Returns:      <type> — <description>
    Side effects: <list or "none">
    3GPP ref:     <TS xx.xxx clause x.x> or [VERIFY]
    Callers:      <list of calling functions>
    Callees:      <list of called functions>

  Minimum expected entries:

    | Milestone | Functions                                      |
    |-----------|------------------------------------------------|
    | M1        | redcap_phy_init(), redcap_prb_limit()          |
    | M2        | fill_redcap_sib1(), parse_redcap_sib1()        |
    | M3        | init_redcap_bwp(), coreset0_redcap_case_b()    |
    | M4        | sdt_scheduler_fsm(), rrc_inactive_redcap_enter()|
    | M5        | redcap_tput_logger()                           |

--- Chapter 2: State Machine & Flow Diagrams ---
  Generate Mermaid diagrams for:

  (a) SDT Scheduler FSM (UL-focused):
    stateDiagram-v2
      [*] --> IDLE
      IDLE --> SDT_TRIGGER : UL data arrives
      SDT_TRIGGER --> MsgA_PATH : payload < threshold
      SDT_TRIGGER --> Msg3_PATH : payload >= threshold
      MsgA_PATH --> SDT_ACTIVE
      Msg3_PATH --> SDT_ACTIVE
      SDT_ACTIVE --> INACTIVE : UL burst complete
      INACTIVE --> IDLE : inactivity timer expires

  (b) RedCap RRC Attach Flow:
    cellBarredRedCap check in SIB1
    → MIB decode
    → SIB1 parse (halfDuplexRedCapAllowed, cellBarredRedCap1Rx)
    → RRC Setup Request
    → RRC Setup Complete (with RedCap capability IE)
    → UL data path established

--- Chapter 3: Compliance Gap Register ---
  Generate from docs/redcap_compliance_gap.md:

  | Feature                   | Status             | Milestone |
  |---------------------------|--------------------|-----------|
  | 1Rx PHY constraint        | [IMPLEMENTED]      | M1        |
  | UL single-antenna enforce | [IMPLEMENTED]      | M1        |
  | HD-FDD switching gap      | [PARTIAL]          | M1        |
  | SIB1 RedCap IE encode     | [IMPLEMENTED]      | M2        |
  | cellBarredRedCap gate      | [IMPLEMENTED]      | M2        |
  | BWP RedCap size limit     | [IMPLEMENTED]      | M3        |
  | CORESET#0 Case B          | [PARTIAL]          | M3        |
  | M3 runtime matrix         | [IMPLEMENTED]      | M3        |
  | RRC_INACTIVE flag plumbing | [IMPLEMENTED]     | M4        |
  | SDT MsgA path             | [PARTIAL]          | M4        |
  | SDT Msg3 fallback         | [PARTIAL]          | M4        |
  | UL throughput validation  | [BLOCKED]          | M5        |
  | E2/xApp UL PRB control    | [PARTIAL]          | M5        |
  | O1 rApp policy            | [NOT IMPLEMENTED]  | future    |

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

### 6-C: Automation Scripts

Task 1 — Diff scanner:
  File: scripts/gen_function_index.py
  Action: Scan git diff from M1 branch to M5 branch.
    Extract new function signatures and output
    structured JSON for Reference Manual Ch1.
  Output: scripts/output/function_index.json

Task 2 — UL Throughput parser:
  File: common/utils/redcap_tput_logger.py
  Input:  /tmp/redcap_ul_result.json (iperf3 -J output)
  Output CSV columns:
    timestamp, interval_sec, throughput_ul_mbps,
    lost_packets, jitter_ms
  Logic:
    - Parse iperf3 JSON "intervals" array.
    - Compute mean throughput_ul_mbps across all intervals.
    - Print PASS if mean >= 30 Mbps, else FAIL.
    - Write CSV to /tmp/redcap_ul_summary.csv.
  NOTE: This parser is UL-only. Do NOT implement DL columns.

Task 3 — Manual skeleton generator:
  File: scripts/gen_doc_skeleton.py
  Action: Auto-generate chapter headers and placeholder
    sections for both tutorial and reference manuals
    based on this milestone definition file.
  Output:
    docs/tutorial_redcap_rfsim.md   (skeleton)
    docs/reference_redcap_functions.md  (skeleton)

Task 4 — Docker Compose for RedCap + RIC:
  File: ci-scripts/yaml_files/5g_rfsimulator_flexric_redcap/
          docker-compose.yml
        ci-scripts/yaml_files/5g_rfsimulator_flexric_redcap/
          docker-compose.mmtc.yml
        ci-scripts/yaml_files/5g_rfsimulator_flexric_redcap/scripts/
          ue_mmtc_entrypoint.sh
  Base:
    `ci-scripts/yaml_files/5g_rfsimulator_flexric/docker-compose.yml`
    is the [source-of-truth architecture].
    The RedCap compose path must remain a [delta-compatible derivative].
  Modifications required:

  (a) Preserve the [fixed-UE validation path] for CI/runtime evidence:
      Keep gNB/UE config mounting overrideable through env-backed volumes:
        `GNB_REDCAP_CONFIG`
        `NRUE_CONFIG_1`
        `NRUE_CONFIG_2`
      with defaults preserving:
        `UE1 = baseline/non-RedCap`
        `UE2 = RedCap`

  (b) Ensure nearRT-RIC service remains present in this compose path:
        image: oai-flexric:custom-dev
        container_name: nearRT-RIC_redcap
        networks:
          public_net:
            ipv4_address: 192.168.70.180
        volumes:
          - ./conf/flexric.conf:
              /usr/local/etc/flexric/flexric.conf
        healthcheck:
          test: ["CMD", "pgrep", "nearRT-RIC"]
          interval: 10s
          timeout: 5s
          retries: 5

  (c) Keep `depends_on` for `oai-gnb` on `nearRT-RIC`:
        depends_on:
          - nearRT-RIC

  (d) Add a [scalable mMTC path] without manually cloning
      `oai-nr-ue1..N` forever:
        - introduce `oai-nr-ue-mmtc` or an equivalent scale-friendly UE block
        - derive per-instance:
            IMSI
            UE YAML
            RedCap enable / disable
            optional half-duplex flag
            telnet / listen port
        - keep the main operator workflow centered on
            `docker compose up`
          by using a generated or maintained Compose overlay / override
        - allow `--scale` only as a secondary engineering shortcut

  (e) Ensure the RedCap compose keeps architectural alignment with
      the vendor FlexRIC compose for:
        service ordering
        container naming conventions where practical
        external CN networking
        and FlexRIC wiring

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
## Progress Tracker (auto-update after each milestone)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Milestone                        | Code | Test | Docs | Status
---------------------------------|------|------|------|---------------------------
M1: PHY Constraints              | [~]  | [x]  | [x]  | In Progress
M2: RRC / SIB1                   | [~]  | [~]  | [~]  | In Progress
M3: BWP & CORESET#0              | [x]  | [~]  | [~]  | Waiting for host runtime
M4: SDT / RRC_INACTIVE           | [~]  | [x]  | [ ]  | In Progress
M4-B: DRX / eDRX / PSM           | [ ]  | [ ]  | [ ]  | Planned from 2026-04-12 gap scan
M5: Compose Rebase & mMTC Scaling| [~]  | [!]  | [~]  | In Progress; fixed-UE UE2 user-plane blocker
M6-A: Tutorial Manual            | [ ]  | [ ]  | [ ]  | Pending
M6-B: Reference Manual           | [ ]  | [ ]  | [ ]  | Pending
M6-C: Automation Scripts         | [ ]  | [ ]  | [ ]  | Pending
---------------------------------|------|------|------|---------------------------
Overall: active partial progress in M1/M2/M3/M4/M5; [Milestone 5] now targets [flexric-based compose rebase + 30+ UE mMTC scaling under docker compose up]; [DRX / eDRX / PSM] remains a formal gap; host Docker runtime is still required for end-to-end evidence
