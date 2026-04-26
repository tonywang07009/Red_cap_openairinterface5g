# RedCap mMTC Codex Agent — Project Spec v3.3
# Stack: OAI 5G NR · FR1 · 3GPP Rel-17 RedCap · FlexRIC
# Focus: PHY/MAC RedCap behavior + Compose-based mMTC runtime
# Spec authority: /spec/redcap5g_spec.md (consult before every coding task)
# Last updated: 2026-04-26

## Strict Rules

- Never fabricate 3GPP clause numbers. Mark uncertain refs as [VERIFY §TS XX.XXX].
- No -R flag in any iperf3 command. All throughput tests are UL direction only.
- All new functions require Doxygen-style doc comments.
- Flow and procedure logic must follow /spec/redcap5g_spec.md.
  If code conflicts with the spec, follow the spec and log the conflict.

Milestone completion rule — `[x]` only when ALL pass on a Docker-enabled host:
  1. New/modified `.c` and `.h` files compile without error.
  2. `CMakeLists.txt` updated when new files are added.
  3. Unit tests build and run stably.
  4. Host runtime validation passes (`docker compose up`, attach, UL test).
  5. Codex prints the updated Progress Tracker block → paste back here manually.

Milestone execution order (strict):
  **M1 → M2 → M3 → M4 → M4-B → M5 → M6**
  Do NOT start M5 before M4-B is complete.

***

## Hard Constraints

| Parameter       | Value                                      |
|-----------------|---------------------------------------------|
| FR1 BW          | ≤ 20 MHz                                   |
| PRB @15 kHz     | ≤ 106 RedCap / ≤ 25 eRedCap                |
| PRB @30 kHz     | ≤ 51  RedCap / ≤ 12 eRedCap                |
| DL Antenna      | 1Rx mandatory, 2Rx optional, max 2 layers  |
| UL Antenna      | Single Tx only, no MIMO                    |
| Power Class     | PC3 = 23 dBm                               |
| DRB max         | 8                                          |
| eDRX max IDLE   | 10485.76 s                                 |
| eDRX max INACT  | 10.24 s                                    |

***

## Architecture & Naming Rules

**Compose source-of-truth:**
`ci-scripts/yaml_files/5g_rfsimulator_flexric/docker-compose.yml`

**RedCap compose path** (delta only — must stay aligned with source-of-truth):
`ci-scripts/yaml_files/5g_rfsimulator_flexric_redcap/docker-compose.yml`

**UE container naming — one canonical rule, no exceptions:**
- `oai-nr-ue` → base service name in YAML
- `oai-nr-ue{0..32}` → mMTC scaled UEs; IMSI pre-defined in YAML files
- Use `UE_TYPE=baseline` / `UE_TYPE=redcap` labels for role tagging
- Do NOT use `oai-nr-ue1` / `oai-nr-ue2` as primary service names

**mMTC launch (canonical):**
```bash
docker compose up -d oai-nr-ue{0..32}
```
IMSI pre-defined in: `ci-scripts/conf_files/nrue_recap/nrue{0..32}.uicc.yaml`
Do NOT use `--scale`. Do NOT generate IMSI at runtime.

**Doc language:**
English only. Sentences ≤ 20 words. Define every acronym on first use.
Target reader: 3rd-year engineering student, non-English-speaking country.

***

## Milestone Table

| #    | Milestone          | Key Deliverables                                 | Status |
|------|--------------------|--------------------------------------------------|--------|
| M1   | PHY Constraints    | `redcap_phy_init.c/.h`, PRB guard, CMake         | [~]    |
| M2   | RRC / SIB1         | `fill/parse_redcap_sib1()`, SIB1 IE, CMake       | [~]    |
| M3   | BWP & CORESET#0    | `init_redcap_bwp()`, Case A/B selector, CMake    | [x]/[~]|
| M4   | SDT / INACTIVE     | `sdt_scheduler_fsm()`, MsgA/Msg3 paths, CMake    | [~]    |
| M4-B | DRX / eDRX / PSM  | Connected DRX wired, eDRX SIB1, CMake            | [ ]    |
| M5   | Compose + mMTC     | Compose rebase, UE0..32 YAML, UL iperf ≥30 Mbps  | [~]/[!]|
| M6   | Docs & Automation  | Tutorial, ref manual, tput logger                | [ ]    |

***

## M1 — PHY Constraints

**Spec ref:** TS 38.101-1 §5.3, TS 38.306 §4

**Tasks:**
1. Define FR1 BW and PRB caps per SCS in PHY layer config structs.
   - Max BW: 20 MHz; SCS: 15 kHz and 30 kHz.
   - Enforce caps via compile-time or runtime assertion guards.
2. Implement antenna constraints:
   - DL: 1Rx mandatory, 2Rx optional, max 2 layers. UL: single Tx, no MIMO.
3. Add HD-FDD Type A flag to UE capability struct (TS 38.306 §4.2).
   - Enforce Tx/Rx switching gap in UL scheduler.

**Target files:**
```
openair1/PHY/NR_TRANSPORT/redcap_phy_init.c   (new)
openair1/PHY/NR_TRANSPORT/redcap_phy_init.h   (new)
openair2/LAYER2/NR_MAC_gNB/nr_mac_redcap.h    (new)
```

**Acceptance criteria:**
- PHY init passes with RedCap-constrained parameters.
- Unit test asserts PRB count ≤ 106 (20 MHz / 15 kHz SCS).
- CMakeLists.txt updated.

**Status note [2026-04-13]:** Code `[~]`, unit test `[x]`, docs `[x]`, CMake `[~]`.

***

## M2 — RRC / SIB1 Support

**Spec ref:** TS 38.331 §6.3.1, §6.3.2

**Tasks:**
1. Design `RedCap_SIB1` struct with fields:
   - `redCap-ConfigCommon-r17` — indicates cell supports RedCap UEs.
   - `halfDuplexRedCapAllowed` (bool) — if absent, HD-FDD UE must bar cell.
   - `cellBarredRedCap1Rx` (bool) — bars 1Rx UEs selectively.
   - `cellBarredRedCap2Rx` (bool) — bars 2Rx UEs selectively.
   - Map each field to TS 38.331 clause as inline comment.
   - Mark uncertain mappings as [VERIFY AGAINST TS 38.331].
2. Implement `fill_redcap_sib1()` (gNB side) and `parse_redcap_sib1()` (UE side).
3. Integrate into existing OAI RRC SIB1 pipeline.

**Target files:**
```
openair2/RRC/NR/rrc_gNB_sib1.c                  (modified)
openair2/RRC/NR/rrc_UE_sib1.c                   (modified)
openair2/RRC/NR/MESSAGES/asn1_msg_redcap.h       (new)
```

**Acceptance criteria:**
- SIB1 encodes/decodes RedCap fields without ASN.1 error.
- `cellBarredRedCap1Rx = true` blocks 1Rx UE attachment in loopback test.
- CMakeLists.txt updated.

**Status note [2026-04-13]:** Code `[~]`, test `[~]`, docs `[~]`, CMake `[~]`.

***

## M3 — BWP & CORESET#0

**Spec ref:** TS 38.331 §6.3.2 initialDownlinkBWP-RedCap-r17, TS 38.213 §13

**Scope:**
- In scope: RedCap BWP / CORESET#0 / scheduler logic in MAC/gNB config paths.
- Out of scope: New XML scenario files; extra project documentation.

**Tasks:**
1. Define RedCap-specific BWP structs for DL and UL Initial BWP (max 20 MHz each).
   - Apply PRB offset/size constraints from M1.
2. Handle CORESET#0 special cases with runtime selector `coreset0_redcap_mode`:
   - Case A (full-cell): standard CORESET#0 placement.
   - Case B (edge-only): `commonControlResourceSet` with edge-aligned PRBs.
3. Validate with `5g_rfsimulator_flexric_redcap/` using RedCap gNB + UE YAML.
   - Confirm PDCCH decoding for both Case A and B.

**Target files:**
```
openair2/GNB_APP/gnb_config.c                          (modified)
openair2/LAYER2/NR_MAC_gNB/nr_mac_redcap_bwp.c         (new)
openair2/LAYER2/NR_MAC_gNB/nr_mac_redcap_bwp.h         (new)
openair2/LAYER2/NR_MAC_gNB/nr_mac_sched.c              (modified)
openair2/LAYER2/NR_MAC_gNB/nr_radio_config.c           (modified)
ci-scripts/conf_files/gnb.sa.band78.fr1.106PRB.usrpb210.redcap.yaml
```

**Acceptance criteria:**
- BWP init completes without assertion failure.
- CORESET#0 Case B allocates PRBs only at cell edge.
- Existing `5g_rfsimulator_flexric_redcap/docker-compose.yml` can point to
  RedCap gNB + UE YAML without new orchestration format.
- CMakeLists.txt updated.

**Status note [2026-04-10]:** Code `[x]`, test `[~]`, docs `[~]`, CMake `[x]`.
Runtime helpers `redcap_prepare_runtime_config.py` / `redcap_runtime_host_validation.sh`
added as supporting validation tooling (not primary M3 target).
Live rfsimulation remains `[BLOCKED]` — Docker access required.

***

## M4 — SDT / RRC_INACTIVE

**Spec ref:** TS 38.321 §5.x SDT procedure, TS 38.331 §5.3.x RRC_INACTIVE

**Tasks:**
1. Add RRC_INACTIVE support flags:
   - gNB: `redcap_inactive_allowed` in gNB config struct.
   - UE: `redcap_rrc_state` enum `{ IDLE, INACTIVE, CONNECTED }`.
2. Design SDT scheduler FSM (`sdt_scheduler_fsm()`):
   - States: `IDLE → SDT_TRIGGER → MsgA_PATH | Msg3_PATH → SDT_ACTIVE → INACTIVE`
   - Path selection: data size threshold [VERIFY AGAINST TS 38.321 SDT procedure].
   - Log state transitions to file for verification.
3. Add unit tests:
   - MsgA path with small UL payload (< 256 bytes).
   - Msg3 fallback with larger UL payload.

**Target files:**
```
openair2/RRC/NR/rrc_gNB_redcap_inactive.c      (new)
openair2/RRC/NR/rrc_UE_redcap_inactive.c       (new)
openair2/LAYER2/NR_MAC_gNB/nr_mac_sdt_fsm.c   (new)
openair2/LAYER2/NR_MAC_gNB/nr_mac_sdt_fsm.h   (new)
tests/redcap/test_sdt_fsm.c                   (new)
```

**Acceptance criteria:**
- FSM reaches `SDT_ACTIVE` in MsgA simulation.
- State transition log matches expected sequence.
- CMakeLists.txt updated.

**Status note [2026-04-10]:** `nr_mac_sdt_fsm.[ch]` skeleton added. gNB flag and
UE-side plumbing in place. Full scheduler wiring and MsgA simulation pending.
Code `[~]`, test `[x]`, docs `[ ]`, CMake `[~]`.

***

## M4-B — DRX / eDRX / PSM

**Spec ref:** TS 38.321 §5.7 (Connected DRX), TS 38.331 [VERIFY eDRX clauses],
TS 24.501 [VERIFY T3324 / PSM]

**Gap evidence [2026-04-12]:**
- `config_ue.c` logs `"DRX not implemented! Configuration not handled!"`
- eDRX present in ASN.1 only — no RRC runtime wiring.
- PSM: only legacy EPS T3412 handling visible; no 5GS T3324 path.

**Tasks:**
1. Implement Connected Mode DRX:
   - Parse dedicated `drx-Config` instead of logging not-implemented.
   - Wire timers: `drx-onDurationTimer`, `drx-InactivityTimer`,
     `drx-LongCycleStartOffset`, `drx-ShortCycle` (optional).
2. Implement Idle / Inactive eDRX in SIB1:
   - Add `eDRX-AllowedIdle-r17` and `eDRX-AllowedInactive-r17` encode/decode.
   - Add UE-side state gating for paging behavior.
3. Add PSM interface hooks:
   - Log and track T3324 / T3412-equivalent low-power timers.
   - Document CN/AMF dependencies explicitly.
   - Add one reproducible host-side validation step for NAS timers.

**Target files:**
```
openair2/LAYER2/NR_MAC_UE/config_ue.c             (modified)
openair2/LAYER2/NR_MAC_gNB/gNB_scheduler_dlsch.c  (modified)
openair2/LAYER2/NR_MAC_gNB/gNB_scheduler.c        (modified)
openair2/RRC/NR/rrc_gNB.c                         (modified)
openair2/RRC/NR_UE/rrc_UE.c                       (modified)
ci-scripts/conf_files/gnb.sa.band78.fr1.106PRB.usrpb210.redcap.yaml
ci-scripts/conf_files/nrue_recap/nrue*.uicc.yaml
```

**Acceptance criteria:**
- Connected DRX no longer logs `"not implemented"` with `drx-Config` present.
- `eDRX-AllowedIdle-r17` / `eDRX-AllowedInactive-r17` encode/decode verified.
- PSM scope and CN dependencies explicitly documented.
- CMakeLists.txt updated.

**Status:** `[ ]` Not started — prerequisite: M4 complete.

***

## M5 — Compose Architecture, Integration & UL Throughput

**Spec ref:** TS 38.321 §5 (MAC scheduling), TS 38.331 §6 (RRC config)

**Scope:**
- In scope: Rebase RedCap compose on vendor FlexRIC topology; fixed-UE CI path;
  scalable mMTC path (32 UE target); UL throughput validation.
- Out of scope: New non-Compose orchestration model; XML as primary deliverable.

**Tasks:**
1. Rebase RedCap compose as delta-compatible derivative of:
   `ci-scripts/yaml_files/5g_rfsimulator_flexric/docker-compose.yml`
   - Carry only RedCap-specific deltas: gNB YAML, UE YAML, capability options.
2. Preserve fixed-UE CI validation path:
   - `UE_TYPE=baseline` (oai-nr-ue0) and `UE_TYPE=redcap` (oai-nr-ue1).
   - Runtime evidence: `[302003]` SIB1 RedCap DL BWP, `[302005/302006]` E2 xApp.
3. Add scalable mMTC overlay (`docker-compose.mmtc.yml`):
   - Per-instance derivation: IMSI, UE YAML, RedCap flag, HD-FDD flag, telnet port.
   - Primary operator workflow: `docker compose -f docker-compose.yml
     -f docker-compose.mmtc.yml up -d`
   - First target: 32 UE. Follow-up: 64 UE.
4. Run end-to-end simulation (fixed-UE layer + scalable mMTC layer).
5. Implement `redcap_tput_logger()` for UL throughput post-processing.
6. Document compliance gaps with tags: `[IMPLEMENTED]` / `[PARTIAL]` / `[NOT IMPLEMENTED]`.

**nearRT-RIC service block (mandatory in RedCap compose):**
```yaml
nearRT-RIC:
  image: oai-flexric:custom-dev
  container_name: nearRT-RIC_redcap
  networks:
    public_net:
      ipv4_address: 192.168.70.180
  volumes:
    - ./conf/flexric.conf:/usr/local/etc/flexric/flexric.conf
  healthcheck:
    test: ["CMD", "pgrep", "nearRT-RIC"]
    interval: 10s
    timeout: 5s
    retries: 5
```

**Target files:**
```
ci-scripts/yaml_files/5g_rfsimulator_flexric_redcap/docker-compose.yml      (modified)
ci-scripts/yaml_files/5g_rfsimulator_flexric_redcap/docker-compose.mmtc.yml (new)
ci-scripts/yaml_files/5g_rfsimulator_flexric_redcap/scripts/ue_mmtc_entrypoint.sh
ci-scripts/conf_files/gnb.sa.band78.fr1.106PRB.usrpb210.redcap.yaml
ci-scripts/conf_files/nrue_recap/nrue{0..32}.uicc.yaml
common/utils/redcap_tput_logger.py
doc/redcap_compliance_gap.md  (optional)
```

**Acceptance criteria:**
- RedCap compose structurally aligned with vendor FlexRIC compose.
- Fixed-UE path retains runtime evidence: `[302003]` / `[302005]` / `[302006]`.
- Scalable path launches > 30 UE via `docker compose up` overlay.
- iperf3 reports ≥ 30 Mbps sustained UL throughput.
- No traffic bypasses TUN interface (verify `ip route` inside UE container).

**Known blockers [2026-04-13]:**
- `[!]` `cls_containerize.py` — removed `jq` dependency crash → patched locally.
- `[!]` `oai-cn5g-public-net` subnet `192.168.70.128/26` blocked `192.168.71.x` UEs → patched.
- `[!]` nearRT-RIC overridden with `sleep infinity` → E2 path never came up → patched.
- `[!]` UE user-plane attach still blocked → debug in context of compose rebase.
- All patches applied locally; host rerun required for `[302002]`/`[302003]`/`[030001]`.

***

## M5 Canonical Commands (do not modify)

```bash
# 1. Start iperf3 server on core network side
docker exec -d rfsim5g-oai-ext-dn iperf3 -s

# 2. Run UL test from RedCap UE (no -R flag)
docker exec -it rfsim5g-oai-nr-ue \
  iperf3 -c 12.1.1.1 -u -b 50M -t 30 -B 12.1.1.2 \
  --logfile /tmp/redcap_ul_result.json -J

# 3. Parse and evaluate
python3 common/utils/redcap_tput_logger.py --input /tmp/redcap_ul_result.json
# PASS = mean UL >= 30 Mbps
```

***

## Known Blockers (2026-04-13)

- `[!]` Docker socket unavailable in sandbox → M5 requires Docker-enabled host
- `[!]` UE user-plane attach blocked → debug during M5 compose rebase
- `[ ]` `config_ue.c` logs `"DRX not implemented!"` → M4-B target
- `[ ]` eDRX in ASN.1 only, not wired to RRC runtime → M4-B target

***

## Progress Tracker

> Codex outputs this block after each milestone — **paste back here manually**
> Legend: `[x]` host runtime passed · `[~]` partial · `[!]` env blocked · `[ ]` not started

| Milestone                   | Code | Test | Docs | CMake | Status                           |
|-----------------------------|------|------|------|-------|----------------------------------|
| M1: PHY Constraints         | [~]  | [x]  | [x]  | [~]   | In Progress                      |
| M2: RRC / SIB1              | [~]  | [~]  | [~]  | [~]   | In Progress                      |
| M3: BWP & CORESET#0         | [x]  | [~]  | [~]  | [x]   | Waiting for host runtime         |
| M4: SDT / RRC_INACTIVE      | [~]  | [x]  | [ ]  | [~]   | In Progress                      |
| M4-B: DRX / eDRX / PSM     | [ ]  | [ ]  | [ ]  | [ ]   | Not started — needs M4 complete  |
| M5: Compose + mMTC Scaling  | [~]  | [!]  | [~]  | [ ]   | Blocked: UE UP + Docker socket   |
| M6-A: Tutorial Manual       | [ ]  | [ ]  | [ ]  | n/a   | Pending M5                       |
| M6-B: Reference Manual      | [ ]  | [ ]  | [ ]  | n/a   | Pending M5                       |
| M6-C: Automation Scripts    | [ ]  | [ ]  | [ ]  | [ ]   | Pending M5                       |
| **Overall**                 |      |      |      |       | M4 in progress; M4-B next        |