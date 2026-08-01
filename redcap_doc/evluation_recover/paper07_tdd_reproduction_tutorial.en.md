# Paper-07 TDD Peak-Rate Reproduction Tutorial

[English](./paper07_tdd_reproduction_tutorial.en.md) | [繁體中文](./paper07_tdd_reproduction_tutorial.zh-TW.md)

## Goal

- Reproduce the Paper-07 TDD RedCap peak-rate target on the local OAI RFsim path.
- Target-rate points: UL `34 Mbps`, DL `140 Mbps`.
- Local offered rates: UL `35M`, DL `141M`.
- Classification: [Target-Rate Proxy], not one-to-one RF/channel reproduction.

## Inputs

| Item | Value |
|---|---|
| Scenario | OAI RFsim RedCap TDD n78 |
| Carrier option | 51PRB full-carrier profile for closer Paper-07 semantics |
| UL evidence | iperf receiver Mbps plus MAC `Qm 8` / MCS evidence |
| DL evidence | reverse iperf receiver Mbps plus DLSCH MCS table evidence |
| Historical notes | `paper07_tdd_reproduction_step_by_step.md` |

## Procedure

1. Complete the install path in `redcap_doc/manuals/install/redcap_begin_from_zero.en.md`.
2. Open the display menu:

```bash
bash redcap_interface/mmtc.display.bash paper07-menu
```

3. In the legacy Paper-07 menu, choose:
   - `8) Enable PAPER-07 256QAM profile`
   - `14) Select 51PRB full-carrier profile`
   - `16) Run PAPER-07 reproduction bundle`

4. If running manually, use:
   - UL rate `35M`
   - DL rate `141M`
   - duration `60s`
   - `PUSCH256QAM=1`
   - `PDSCH256QAM=1`

## Pass Criteria

| Check | Pass Evidence |
|---|---|
| Attach health | UE running, attach, PDU, TUN, and forward ping are present. |
| UL target | Receiver throughput reaches the Paper-07 UL target-rate window. |
| DL target | Receiver throughput reaches the Paper-07 DL target-rate window. |
| MAC evidence | UL/DL MAC logs show the intended QAM/MCS path. |
| Stability | gNB restart count remains `0`. |

## Evidence To Save

- Stage or smoke summary log.
- iperf UL/DL logs.
- gNB MAC evidence.
- UE runtime YAML if capability flags are changed.
- Final report path under `agent_doc/Project_management/projects/redcap_simulator_performance_eval_v1/analysis/`.

## Known Limits

- RFsim does not reproduce Paper-07 field RF conditions exactly.
- If active bandwidth, BWP, or carrier semantics differ from the paper, mark the result [PASS_WITH_GAP].
- Exact standard-clause mapping remains `[Needs Verification]` unless checked against local 3GPP notes.
