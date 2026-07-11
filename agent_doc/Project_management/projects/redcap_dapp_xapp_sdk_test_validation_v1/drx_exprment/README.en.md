<!-- SPDX-License-Identifier: CC-BY-4.0 -->

# Adaptive C-DRX Experiment Dossier

This dossier explains the experiment design, the evidence currently available,
and the steps a human operator can follow without an AI assistant. It does not
replace the canonical implementation documents:

- [Detailed reproduction manual](../Doc/adaptive_drx_ab_manual_reproduction.en.md)
- [API and control contract](../Doc/adaptive_drx_api_contract.en.md)
- [Trace Code Guide](../Doc/adaptive_drx_trace_code_guide.en.md)
- [Current Gate report](../report/adaptive_drx_ab_gate_2026-07-11.en.md)

## 1. Experiment Design

### 1.1 Scope and authority

This experiment covers one RedCap UE using C-DRX while in `RRC_CONNECTED`.
It does not cover RRC_INACTIVE eDRX, RRC_IDLE paging, PSM, or physical UE
power consumption.

The control ownership is:

| Component | Responsibility |
|---|---|
| xApp | Predict the next 30-arrival interval window and propose a Long DRX cycle |
| C dApp guard | Accept or reject the proposal using UE, version, cooldown, profile, and rollback state |
| gNB | Configure the UE through RRC and avoid normal new-data scheduling while the UE is outside DRX Active Time |
| UE MAC | Execute the configured DRX timers and decide when PDCCH monitoring is required |

TS 38.321 version 18.2.0 clause 5.7 defines C-DRX operation and Active
Time. Active Time includes On Duration, inactivity, applicable HARQ
retransmission timers, pending Scheduling Requests, and other conditions
listed by the specification. DRX therefore controls UE PDCCH monitoring; it
does not put the gNB to sleep.

TS 38.331 version 18.5.1 `DRX-Config` defines the RRC fields and units:

| Field | Unit used by the specification | v1 experiment value |
|---|---|---|
| `drx-onDurationTimer` | 1/32 ms or enumerated milliseconds | Profile-selected 10, 20, or 40 ms |
| `drx-InactivityTimer` | Enumerated milliseconds | Fixed at 20 ms |
| `drx-LongCycleStartOffset` | Cycle and start offset in milliseconds | Profile-selected cycle; offset 0 |
| `drx-HARQ-RTT-TimerDL/UL` | Symbols | Fixed by the OAI RRC producer |
| `drx-RetransmissionTimerDL/UL` | Slots | Fixed by the OAI RRC producer |
| `drx-SlotOffset` | 1/32 ms | Fixed at 0 |

Local specification sources are under `redcap_doc/specs/redcap_3gpp/DRX/`.

### 1.2 Approved v1 profiles

The experiment accepts only these profile pairs:

| Profile | Long cycle | On Duration | On Duration / cycle |
|---|---:|---:|---:|
| `drx-320-10` | 320 ms | 10 ms | 3.125% |
| `drx-640-10` | 640 ms | 10 ms | 1.5625% |
| `drx-1280-20` | 1280 ms | 20 ms | 1.5625% |
| `drx-2560-20` | 2560 ms | 20 ms | 0.78125% |
| `drx-5120-40` | 5120 ms | 40 ms | 0.78125% |
| `drx-10240-40` | 10240 ms | 40 ms | 0.390625% |

These are coupled profiles, not an independent Long-cycle versus On-Duration
factorial experiment. The A/B result may compare complete profiles, but it
must not attribute an effect to On Duration alone.

Short DRX and the optional DRX Command MAC CE are disabled for the main v1
experiment. The DRX Command is not an RRC reconfiguration or rollback method.

### 1.3 Parameter conformance versus adaptive A/B

Parameter conformance is established by focused tests. It covers legal profile
pairs, timer boundaries, scheduler gating, stale versions, cooldown, HARQ/SR
Active-Time conditions, DRX Command guards, and rollback state.

The runtime A/B experiment measures the end-to-end control path and traffic
trade-off. It has four independent campaigns:

| Campaign | Arm | Direction | Arrivals | Warm-up | Scored |
|---|---|---|---:|---:|---:|
| `arm-a-dl` | Local gNB control | Downlink | 330 | 30 | 300 |
| `arm-b-dl` | Adaptive E2SM-RC control | Downlink | 330 | 30 | 300 |
| `arm-a-ul` | Local gNB control | Uplink | 330 | 30 | 300 |
| `arm-b-ul` | Adaptive E2SM-RC control | Uplink | 330 | 30 | 300 |

Arm B commits one policy for every 30 scored arrivals. A policy is committed
only after the versioned request, E2 acknowledgement, dApp acceptance, gNB
application, and RRC completion markers correlate.

### 1.4 Implemented baseline protocol

The A/B protocol uses `drx-320-10` as a fixed Arm A baseline. It is
pre-applied once before traffic begins and remains unchanged for all 300 scored
arrivals. Arm B starts from the same approved baseline and may update its
profile after every committed 30-arrival history window.

The runner now enforces that behavior. On fresh Arm B state it first commits the
same profile with reserved bootstrap version 0, then uses FlexRIC request IDs
for the ten scored policy windows. Reusing configured DRX state is rejected.

### 1.5 Required measurements and claim boundary

| Measurement | Purpose | Current support |
|---|---|---|
| Applied profile and marker chain | Prove the control took effect | Implemented in logs/checker |
| Delivery success | Confirm one scored record per arrival | Requires parsed receiver report with received packets |
| First receive latency | Measure wake-to-delivery behavior | Filtered tcpdump -> `receive-csv` -> checker |
| iPerf goodput/loss/jitter | Detect traffic degradation | Parsed into metrics CSV |
| UE DRX Active-Time slot ratio | Energy-related behavior proxy | Atomic UE counter via `ciUE drx_stats` |
| DL/UL HARQ retransmissions | Explain poor delivery or extended Active Time | RNTI-specific first/last log delta |
| Policy apply latency | Quantify RRC control overhead | Timestamped staged-to-RRC-complete correlation |

RFsim does not measure current, watts, joules, battery life, or receiver-chain
power states. Active-Time and PDCCH-monitoring ratios are behavior proxies only.

## 2. Current Result Explanation

### 2.1 Evidence status

| Surface | Current result |
|---|---|
| gNB and UE softmodem builds | PASS |
| Telnet CI DRX control module | PASS |
| Focused UE DRX, RC, and gNB DRX CTest targets | PASS, 3/3 |
| Trace, predictor, window, and checker tests | PASS, 10/10 plus evidence 3/3 |
| C dApp and C xApp self-checks | PASS |
| Generated Python FlexRIC module | PASS with repository SWIG 4.1.1 and Python 3.12 |
| Isolated E2 build path | PASS with `E2_AGENT=ON`, gNB/UE, `telnetsrv_ci`, and `ciUE` |
| One-UE RFsim C-DRX smoke | PASS: attach/PDU/TUN/ping, E2 Setup, Arm A apply/RRC complete, UE counters, UL/DL bursts |
| Four RFsim campaigns | BLOCKED / not executed |

The smoke proves the fixed Arm A local control and traffic path, not a live Arm
B Python E2 request, an adaptive A/B result, or traffic benefit.

### 2.2 Scored population

| Campaign | Planned scored | Evidenced scored | Result |
|---|---:|---:|---|
| `arm-a-dl` | 300 | 0 | BLOCKED |
| `arm-b-dl` | 300 | 0 | BLOCKED |
| `arm-a-ul` | 300 | 0 | BLOCKED |
| `arm-b-ul` | 300 | 0 | BLOCKED |
| **Total** | **1200** | **0** | **BLOCKED** |

The current overall evidenced scored population is `0/1200`.

All latency, goodput, loss, jitter, HARQ, monitoring, Active-Time, reject, and
rollback metrics are currently `N/A`. `N/A` means not measured; it is not zero
and it is not a successful result.

The current images, iPerf2, and tcpdump are ready. The remaining blocker is
controlled host-to-Docker bridge access for Python xApp node discovery, followed
by the four 330-arrival campaigns and complete marker/evidence packages.

## 3. Human-Only Step-by-Step Reproduction

Run every repository command from the repository root. Preserve all generated
runtime material under `test_log/`; do not place generated CSV or logs in this
documentation directory.

### Step 1: Check the host

```bash
python3 --version
cmake --version
ninja --version
swig -version
iperf --version
iperf --help | grep -E -- '--txstart-time|--trip-times|--reverse'
docker compose version
```

For Arm B, require SWIG 4.1 or newer and an importable FlexRIC module:

```bash
PYTHONPATH=/tmp/flexric-adaptive-drx/examples/xApp/python3 \
  python3 -c 'import xapp_sdk; print(xapp_sdk.__file__)'
grep '^E2_AGENT:' /tmp/oai-e2-agent-build/CMakeCache.txt
```

Stop and record `[BLOCKED]` if the module cannot be imported or `E2_AGENT` is
not enabled in the build used for the campaign.

### Step 2: Build the affected targets

```bash
cmake -S . -B /tmp/oai-e2-agent-build -GNinja -DE2_AGENT=ON -DENABLE_TELNETSRV=ON
cmake --build /tmp/oai-e2-agent-build \
  --target nr-softmodem nr-uesoftmodem telnetsrv_ci telnetsrv_ciUE -j2
```

### Step 3: Run focused tests

```bash
cmake --preset tests
cmake --build --preset tests --target test_nr_ue_drx test_nr_redcap_rc_ctrl test_nr_gnb_drx -j2
ctest --test-dir cmake_targets/ran_build/build_test \
  --output-on-failure \
  -R '^(test_nr_ue_drx|test_nr_redcap_rc_ctrl|test_nr_gnb_drx)$'

python3 -B agent_doc/Project_management/projects/redcap_dapp_xapp_sdk_test_validation_v1/scripts/adaptive_drx/test_adaptive_drx.py -v
python3 -B agent_doc/Project_management/projects/redcap_dapp_xapp_sdk_test_validation_v1/scripts/adaptive_drx/test_campaign_evidence.py -v
```

Do not continue after a focused-test failure.

### Step 4: Generate deterministic traces

```bash
RUN_ID=$(date +%F_%H-%M-%S)
RUN_DIR="test_log/runtime_logs/adaptive_drx_${RUN_ID}"
START_EPOCH_US=$(date -d '+10 minutes' +%s%6N)
mkdir -p "$RUN_DIR"

python3 -B agent_doc/Project_management/projects/redcap_dapp_xapp_sdk_test_validation_v1/scripts/adaptive_drx/adaptive_drx.py generate \
  --output-dir "$RUN_DIR" \
  --trace-seed 41 \
  --start-epoch-us "$START_EPOCH_US"

wc -l "$RUN_DIR"/adaptive_drx_*_trace.csv
sha256sum "$RUN_DIR"/adaptive_drx_*_trace.csv
```

Each trace must have 331 lines. Use the detailed manual's `rebase` command for
each sequential campaign so intervals remain identical and timestamps remain
in the future.

### Step 5: Start the runtime services and log collection

Start the CN5G, nearRT-RIC, gNB, and one RedCap UE using the project RFsim
topology. The gNB must include:

```text
--telnetsrv --telnetsrv.shrmod ci --telnetsrv.listenaddr 192.168.70.140 --telnetsrv.listenport 9091
```

Verify that the UE has a PDU session and that the campaign process can reach
both the UE data path and the FlexRIC Python module. Start a persistent iPerf2
server in the receiving data-network namespace:

```bash
iperf -s -u -i 1
```

In another terminal, retain a combined gNB/UE log at
`$RUN_DIR/runtime.log`. Use the exact Docker Compose log command from the
[detailed reproduction manual](../Doc/adaptive_drx_ab_manual_reproduction.en.md).

### Step 6: Let the runner pre-apply the baseline

Resolve the connected UE C-RNTI from current gNB evidence and pass it as
`--rnti`. The runner uses this local control surface:

```text
ci trigger_drx_policy 1 320 10 0 0 0x1234
```

Replace `0x1234` with the live C-RNTI. Do not send traffic until the log shows
the matching gNB applied marker and successful versioned RRC completion.

Arm A commits version 1 once. Arm B on a fresh stack uses
`ci bootstrap_drx_policy 320 10 <rnti>` for reserved version 0, then requires
the first FlexRIC request ID to be positive and newer.

### Step 7: Run the four campaigns

Run one campaign at a time in this order:

1. `arm-a-dl`
2. `arm-a-ul`
3. `arm-b-dl`
4. `arm-b-ul`

Use a fresh future trace and fresh gNB policy state for each campaign. The
exact Arm A and Arm B command templates are maintained in sections 5.4 and
5.5 of the [detailed reproduction manual](../Doc/adaptive_drx_ab_manual_reproduction.en.md).

For every command, provide:

- the generated manifest;
- the campaign ID;
- the persistent iPerf2 server address;
- the UE PDU-session address passed through `--bind-address`, such as `10.0.0.2`;
- a command-plan JSONL and metrics CSV path under `$RUN_DIR`;
- `--execute` and the correct C-RNTI or RRC UE ID;
- the combined runtime log and a positive control timeout.

Run Python on the host, use the detailed manual's `--traffic-prefix` to
execute iPerf2 in the UE container, and bind iPerf2 to the UE PDU-session
address so traffic cannot bypass `oaitun_ue1` through container `eth0`.

### Step 8: Collect evidence

Retain these artifacts for every campaign:

- manifest, trace CSV, trace hashes, command-plan JSONL, and metrics CSV;
- combined gNB/UE logs and xApp/nearRT-RIC logs;
- receiver-side first UDP packet timestamps correlated to each scheduled arrival;
- parsed iPerf goodput, loss, and jitter;
- UE Active-Time slot counts and total observed slots;
- DL/UL HARQ retransmission counters;
- request, ACK, dApp decision, gNB apply, UE configuration, and RRC completion markers.

The collectors are source-ready. Metrics remain `N/A` until the real campaign
produces metrics/receive CSVs, a UE summary, and RNTI-specific runtime logs.

### Step 9: Validate each campaign

```bash
python3 -B agent_doc/Project_management/projects/redcap_dapp_xapp_sdk_test_validation_v1/scripts/adaptive_drx/check_campaign.py \
  --manifest "$RUN_DIR/adaptive_drx_campaign_manifest_v1.json" \
  --campaign-id arm-b-dl \
  --metrics-csv "$RUN_DIR/arm-b-dl.metrics.csv" \
  --receive-csv "$RUN_DIR/arm-b-dl.receive.csv" \
  --summary-json "$RUN_DIR/arm-b-dl.summary.json" \
  --rnti 0x1234 \
  --log "$RUN_DIR/runtime.log"
```

Repeat with the corresponding ID and metrics file for all four campaigns.

- `PASS`: 300 scored rows, profile/version correlation, and all required markers exist.
- `PARTIAL`: artifacts exist, but a row, version, profile, or marker is incomplete.
- `BLOCKED`: a prerequisite or external runtime artifact is absent.
- `FAIL`: supplied evidence is invalid or inconsistent.

Do not calculate an Arm A/B comparison until all four campaign checks pass.

### Step 10: Handle rejection and rollback

On reject or timeout, keep the current 30-sample window and preserve every
artifact. Do not clear the predictor evidence.

Automatic RRC failure handling can restore the previous applied profile and
emit `[RedCap DRX][rollback]`. No public campaign or telnet command currently
exposes the explicit rollback API. Do not invent one. Stop the campaign and
restart from a clean topology when operator recovery is required.

## 4. Publication Checklist

- Record the trace seed, start epoch, profile table, software revision, build options, and topology.
- Keep DL and UL results separate.
- Record fixed Arm A version 1 and fresh-state Arm B bootstrap version 0.
- Report missing metrics as `N/A` and incomplete evidence as PARTIAL or BLOCKED.
- Call RFsim Active-Time and PDCCH values behavior proxies, never physical-power measurements.
- Link the final evidence package from the Gate report instead of copying generated logs into this directory.
