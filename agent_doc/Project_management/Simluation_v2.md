# RedCap mMTC Project Plan — Codex Agent Work Log
# Version: 3.0 | Language: English
# Target: OpenAirInterface (OAI) 5G NR, FR1, 3GPP Rel-17 RedCap
# Research Focus: UPLINK Scheduling under RedCap constraints
# Last updated: 2026-04-10

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
   - Run rfsimulation with 1 RedCap UE.
   - Confirm PDCCH decoding succeeds for both Case A and B.

Status note [2026-04-10]:
- Added [Case A / Case B] runtime helpers:
  - `ci-scripts/redcap_prepare_runtime_config.py`
  - `ci-scripts/redcap_runtime_host_validation.sh`
  - `ci-scripts/redcap_runtime_case_matrix.sh`
- Local sandbox check now runs both modes sequentially, but actual [rfsimulation]
  remains [BLOCKED] here because `run_locally.sh` requires Docker access.

Target files (expected):
  openair2/LAYER2/NR_MAC_gNB/nr_mac_redcap_bwp.c
  openair2/LAYER2/NR_MAC_gNB/nr_mac_redcap_bwp.h
  openair2/LAYER2/NR_MAC_gNB/nr_mac_sched.c  (modified)

Acceptance criteria:
  - BWP init completes without assertion failure.
  - CORESET#0 Case B allocates PRBs only at cell edge.

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
## Milestone 5: Integration & UL Throughput Targets
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Research note: This project targets UPLINK scheduling.
All throughput validation must measure UL direction.

Tasks:
1. Configure rfsimulation scenarios:
   - 1 gNB + 1 RedCap UE (1Rx, HD-FDD, 20 MHz FR1, SCS 30 kHz)
   - Target UL throughput: 30–50 Mbps range under RedCap
     PHY constraints.
   - Generate config files: `gnb.redcap.conf`, `ue.redcap.conf`.

   In gnb.redcap.conf, add e2_agent block for RIC integration:
     e2_agent = {
       near_ric_ip_addr = "192.168.70.155";
       sm_dir = "/usr/local/lib/flexric/";
     };

2. Run end-to-end simulation:
   Use Docker Compose to orchestrate the following services
   in dependency order:
     mysql → oai-amf → oai-smf → oai-upf
       → nearRT-RIC (FlexRIC, 192.168.70.155)
         → oai-gnb (RedCap config + e2_agent)
           → oai-nr-ue (1Rx, HD-FDD)
             → oai-ext-dn (iperf3 server)

   UL throughput test procedure:

   Step 1 — Start iperf3 server on the core network side:
     docker exec -d rfsim5g-oai-ext-dn iperf3 -s

   Step 2 — Start UL traffic from UE (client pushes to core):
     docker exec -it rfsim5g-oai-nr-ue \
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

3. Implement `redcap_tput_logger()`:
   - Input:  /tmp/redcap_ul_result.json (iperf3 JSON)
   - Output CSV columns:
       timestamp, interval_sec, throughput_ul_mbps, lost_packets,
       jitter_ms
   - Print PASS if mean throughput_ul_mbps >= 30, else FAIL.

4. Document open gaps vs. full 3GPP Rel-17 RedCap compliance:
   - Use tags: [IMPLEMENTED], [PARTIAL], [NOT IMPLEMENTED].

Target files (expected):
  ci-scripts/yaml_files/5g_rfsimulator/docker-compose.redcap.yml
  ci-scripts/conf_files/gnb.redcap.conf
  ci-scripts/conf_files/ue.redcap.conf
  common/utils/redcap_tput_logger.py
  docs/redcap_compliance_gap.md

Acceptance criteria:
  - iperf3 reports >= 30 Mbps sustained UL throughput.
  - No traffic bypasses the TUN interface (verify via
    `ip route` inside UE container).
  - Gap document contains at least one entry per Milestone.

Status note [2026-04-10]:
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
        -O gnb.redcap.conf \
        --gNBs.[0].min_rxtxtime 6 \
        --MACRLCs.[0].ul_max_mcs 20

      Flag annotations:
        --rfsim               : enable RF simulator (no SDR HW needed)
        -O gnb.redcap.conf    : load RedCap-specific gNB config
                                including e2_agent block (M5)
        --min_rxtxtime 6      : HD-FDD Tx/Rx switching gap (M1)
        --ul_max_mcs 20       : cap UL MCS for RedCap UE (M1)

  (b) Start RedCap UE (1Rx, HD-FDD):
      sudo ./nr-uesoftmodem --rfsim \
        --rfsimulator.serveraddr <GNB_IP> \
        -O ue.redcap.conf \
        --ue-nb-ant-rx 1 \
        --nokrnmod 1

      Flag annotations:
        --rfsimulator.serveraddr : gNB container IP for RF link
        -O ue.redcap.conf        : UE RedCap config (SCS/BW/HD-FDD)
        --ue-nb-ant-rx 1         : enforce 1Rx antenna (M1 mandatory)
        --nokrnmod 1             : use TUN interface, required for
                                   Docker iperf routing (M5)

--- Chapter 3: UL Throughput Test Design ---
  Research context: All tests measure UPLINK scheduling
  performance. Do not use reverse (-R) mode.

  Step 1 — Start iperf3 server (core network side):
    docker exec -d rfsim5g-oai-ext-dn iperf3 -s

  Step 2 — Run UL throughput test from UE container:
    docker exec -it rfsim5g-oai-nr-ue \
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
    docker exec -it rfsim5g-oai-nr-ue \
      ip route show table all | grep oaitun_ue1

--- Chapter 4: Docker Deployment ---
  Full service dependency order:

    mysql
      └─► oai-amf
            └─► oai-smf
                  └─► oai-upf
                        └─► nearRT-RIC  (FlexRIC, 192.168.70.155)
                              └─► oai-gnb  (RedCap + e2_agent)
                                    └─► oai-nr-ue  (1Rx, HD-FDD)
                                          └─► oai-ext-dn  (iperf3)

  Launch command:
    docker-compose -f docker-compose.redcap.yml up -d

  Health-check steps:
    1. Confirm E2 SCTP link:
         docker logs rfsim5g-oai-gnb | grep "E2 Setup Response"
    2. Confirm UE attached:
         docker logs rfsim5g-oai-gnb | grep "UE connected"
    3. Confirm TUN interface exists in UE container:
         docker exec rfsim5g-oai-nr-ue ip addr show oaitun_ue1

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
      block in gnb.redcap.conf (already set in M5).
      xApp and dApp share the same E2 path inside FlexRIC.

  - O1 interface (rApp):
      [NOT IMPLEMENTED — VERIFY OAI O1 NETCONF STATUS]
      If supported, requires separate O1 agent container
      and additional gNB config section.

  Extra Docker flags required per interface:

  | Interface | Required Extra Flag / Config      | docker-compose change |
  |-----------|-----------------------------------|-----------------------|
  | E2/xApp   | e2_agent block in gnb.redcap.conf | Add nearRT-RIC service|
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
  File: ci-scripts/yaml_files/5g_rfsimulator/
          docker-compose.redcap.yml
  Base: existing OAI docker-compose.yaml in ci-scripts.
  Modifications required:

  (a) Override oai-nr-ue service entrypoint:
        --ue-nb-ant-rx 1
        --nokrnmod 1
        -O ue.redcap.conf

  (b) Add nearRT-RIC service:
        image: oai-flexric:latest
        container_name: rfsim5g-nearrt-ric
        networks:
          public_net:
            ipv4_address: 192.168.70.155
        ports:
          - "36421:36421/sctp"
        volumes:
          - ./conf/flexric.conf:
              /usr/local/etc/flexric/flexric.conf
        healthcheck:
          test: ["CMD", "pgrep", "nearRT-RIC"]
          interval: 5s
          timeout: 3s
          retries: 5

  (c) Add depends_on to oai-gnb service:
        depends_on:
          - nearRT-RIC

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
## Progress Tracker (auto-update after each milestone)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Milestone                        | Code | Test | Docs | Status
---------------------------------|------|------|------|---------------------------
M1: PHY Constraints              | [~]  | [x]  | [x]  | In Progress
M2: RRC / SIB1                   | [~]  | [~]  | [~]  | In Progress
M3: BWP & CORESET#0              | [x]  | [~]  | [~]  | Waiting for host runtime
M4: SDT / RRC_INACTIVE           | [~]  | [x]  | [ ]  | In Progress
M5: Integration & UL Throughput  | [~]  | [!]  | [~]  | Blocked by Docker runtime
M6-A: Tutorial Manual            | [ ]  | [ ]  | [ ]  | Pending
M6-B: Reference Manual           | [ ]  | [ ]  | [ ]  | Pending
M6-C: Automation Scripts         | [ ]  | [ ]  | [ ]  | Pending
---------------------------------|------|------|------|---------------------------
Overall: active partial progress in M1/M2/M3/M4/M5; host Docker runtime is still required for end-to-end evidence
