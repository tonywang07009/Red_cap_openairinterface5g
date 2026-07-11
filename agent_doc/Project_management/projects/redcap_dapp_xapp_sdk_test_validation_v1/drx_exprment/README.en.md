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

### 1.4 Next baseline protocol

The next A/B protocol uses `drx-320-10` as a fixed Arm A baseline. It is
pre-applied once before traffic begins and remains unchanged for all 300 scored
arrivals. Arm B starts from the same approved baseline and may update its
profile after every committed 30-arrival history window.

This is an approved next-run design, not current runner behavior. The current
manifest and `run_campaign.py` still schedule seeded Arm A profile changes at
each scored window. Do not label a current v1 run as the fixed-baseline
experiment until that runner and manifest change is implemented and tested.

The Arm B baseline also has a version-correlation constraint: its first live
FlexRIC RIC request ID must be strictly newer than the locally applied baseline
version. If that ordering cannot be proved, stop with `stale_policy_version`
or `rollback_unavailable`; do not force the run.

### 1.5 Required measurements and claim boundary

| Measurement | Purpose | Current support |
|---|---|---|
| Applied profile and marker chain | Prove the control took effect | Implemented in logs/checker |
| Delivery success | Confirm one scored record per arrival | Process result only; UDP delivery still needs receiver evidence |
| First receive latency | Measure wake-to-delivery behavior | Missing receiver timestamp collector |
| iPerf goodput/loss/jitter | Detect traffic degradation | Raw output retained; parser missing |
| UE DRX Active-Time slot ratio | Energy-related behavior proxy | Counter/export missing |
| DL/UL HARQ retransmissions | Explain poor delivery or extended Active Time | Campaign counter/export missing |
| Policy apply latency | Quantify RRC control overhead | Timestamp correlation missing |

RFsim does not measure current, watts, joules, battery life, or receiver-chain
power states. Active-Time and PDCCH-monitoring ratios are behavior proxies only.

## 2. Current Result Explanation

### 2.1 Evidence status

| Surface | Current result |
|---|---|
| gNB and UE softmodem builds | PASS |
| Telnet CI DRX control module | PASS |
| Focused UE DRX, RC, and gNB DRX CTest targets | PASS, 3/3 |
| Trace, predictor, window, and checker tests | PASS, 4/4 |
| C dApp and C xApp self-checks | PASS |
| Generated Python FlexRIC module | Definition-only on this host |
| Main build E2 path | `E2_AGENT=OFF` in the recorded build caches |
| Four RFsim campaigns | BLOCKED / not executed |

The passing builds and unit tests prove source readiness. They do not prove a
live E2 control request, an applied adaptive RFsim policy, or traffic benefit.

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

The current blockers are:

- The evidence host has SWIG 4.0.2 while FlexRIC requires 4.1 or newer.
- No importable `xapp_sdk` module and live E2 control path have been proven.
- The traffic runner must share both the UE data path and the FlexRIC Python environment.
- Receiver timestamp, iPerf result parsing, Active-Time, and HARQ exporters are missing.
- The fixed Arm A baseline protocol is approved but not implemented by the current runner.

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
python3 -c 'import xapp_sdk; print(xapp_sdk.__file__)'
grep '^E2_AGENT:' cmake_targets/ran_build/build/CMakeCache.txt
```

Stop and record `[BLOCKED]` if the module cannot be imported or `E2_AGENT` is
not enabled in the build used for the campaign.

### Step 2: Build the affected targets

```bash
cmake --preset default -DENABLE_TELNETSRV=ON
cmake --build --preset default --target nr-softmodem nr-uesoftmodem telnetsrv_ci -j2
```

### Step 3: Run focused tests

```bash
cmake --preset tests
cmake --build --preset tests --target test_nr_ue_drx test_nr_redcap_rc_ctrl test_nr_gnb_drx -j2
ctest --test-dir cmake_targets/ran_build/build_test \
  --output-on-failure \
  -R '^(test_nr_ue_drx|test_nr_redcap_rc_ctrl|test_nr_gnb_drx)$'

python3 -B agent_doc/Project_management/projects/redcap_dapp_xapp_sdk_test_validation_v1/scripts/adaptive_drx/test_adaptive_drx.py -v
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
  --profile-seed 73 \
  --start-epoch-us "$START_EPOCH_US"

wc -l "$RUN_DIR"/adaptive_drx_*_trace.csv
sha256sum "$RUN_DIR"/adaptive_drx_*_trace.csv
```

Each trace must have 331 lines: one header and 330 arrivals. Regenerate the
manifest for each sequential campaign because absolute `--txstart-time`
values must remain in the future. Keep the same seeds to retain the same
interval sequence.

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

### Step 6: Pre-apply the baseline

Resolve the connected UE C-RNTI from current gNB evidence. Apply
`drx-320-10`, offset 0, and DRX Command disabled through the telnet CI command:

```text
ci trigger_drx_policy 1 320 10 0 0 0x1234
```

Replace `0x1234` with the live C-RNTI. Do not send traffic until the log shows
the matching gNB applied marker and successful versioned RRC completion.

For the next fixed-baseline protocol, leave this profile unchanged throughout
Arm A. The current runner cannot yet do that: it still changes seeded Arm A
profiles at each window. Until the runner is updated, stop here for the new
protocol or run only the clearly labelled legacy v1 seeded-baseline procedure.

Before Arm B, prove that the next FlexRIC-generated request ID is newer than
the baseline policy version and that the gNB has rollback state. Otherwise
record `[BLOCKED]`.

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
- a command-plan JSONL and metrics CSV path under `$RUN_DIR`;
- `--execute` and the correct C-RNTI or RRC UE ID;
- the combined runtime log and a positive control timeout.

Do not run Arm B unless the runner can import `xapp_sdk` from the same
environment that can send traffic over the UE data path.

### Step 8: Collect evidence

Retain these artifacts for every campaign:

- manifest, trace CSV, trace hashes, command-plan JSONL, and metrics CSV;
- combined gNB/UE logs and xApp/nearRT-RIC logs;
- receiver-side first UDP packet timestamps correlated to each scheduled arrival;
- parsed iPerf goodput, loss, and jitter;
- UE Active-Time slot counts and total observed slots;
- DL/UL HARQ retransmission counters;
- request, ACK, dApp decision, gNB apply, UE configuration, and RRC completion markers.

The current source does not export the receiver timestamp, Active-Time, or
campaign HARQ measurements and does not parse all iPerf metrics. Leave those
fields `N/A` and the runtime Gate `BLOCKED` until real collectors exist.

### Step 9: Validate each campaign

```bash
python3 -B agent_doc/Project_management/projects/redcap_dapp_xapp_sdk_test_validation_v1/scripts/adaptive_drx/check_campaign.py \
  --manifest "$RUN_DIR/adaptive_drx_campaign_manifest_v1.json" \
  --campaign-id arm-b-dl \
  --metrics-csv "$RUN_DIR/arm-b-dl.metrics.csv" \
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

- Record both seeds, start epoch, profile table, software revision, build options, and topology.
- Keep DL and UL results separate.
- Distinguish current implementation behavior from the next fixed-baseline protocol.
- Report missing metrics as `N/A` and incomplete evidence as PARTIAL or BLOCKED.
- Call RFsim Active-Time and PDCCH values behavior proxies, never physical-power measurements.
- Link the final evidence package from the Gate report instead of copying generated logs into this directory.
