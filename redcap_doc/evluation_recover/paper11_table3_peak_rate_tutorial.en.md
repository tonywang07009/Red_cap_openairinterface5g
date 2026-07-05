# Paper-11 Table 3 Peak-Rate Tutorial

[English](./paper11_table3_peak_rate_tutorial.en.md) | [繁體中文](./paper11_table3_peak_rate_tutorial.zh-TW.md)

## Goal

- Reproduce Paper-11 Table 3 target-rate rows on the local RedCap RFsim path.
- Targets: UL 64QAM `90 Mbps`, DL 64QAM `169.5 Mbps`, DL 256QAM `226 Mbps`.
- Classification: [Target-Rate Proxy], not calibrated 2.1G FDD RF reproduction.

## Inputs

| Item | Value |
|---|---|
| Script | `redcap_interface/paper11_table3_peak_reproduction.sh` |
| Display entry | `bash redcap_interface/mmtc.display.bash paper11-table3` |
| RFsim profile | `P11T3_PROFILE=51prb` |
| Historical evidence | `paper11_table3_2p1g_peak_rate_step_by_step.md` |

## Procedure

Run the default 51PRB proxy:

```bash
P11T3_PROFILE=51prb P11T3_DURATION=60 bash redcap_interface/paper11_table3_peak_reproduction.sh
```

Or use the display wrapper:

```bash
P11T3_PROFILE=51prb P11T3_DURATION=60 bash redcap_interface/mmtc.display.bash paper11-table3
```

The script should:

1. Start the 64QAM setup.
2. Run UL `90M`.
3. Run DL `169.5M`.
4. Restart/apply DL 256QAM setup.
5. Run DL `226M`.
6. Save iperf, MAC, and runtime YAML evidence.

## Pass Criteria

| Test | Pass Evidence |
|---|---|
| UL 64QAM | Receiver Mbps reaches the `90 Mbps` target-rate window and MAC shows 64QAM evidence. |
| DL 64QAM | Receiver Mbps reaches `169.5 Mbps` and DLSCH evidence is stable. |
| DL 256QAM | Receiver Mbps reaches `226 Mbps` and MAC shows the 256QAM table path. |
| Stability | gNB restart count remains `0`. |

## Limits

- Local RFsim uses band 78 TDD, not the paper's 2.1G FDD condition.
- The run proves target-rate capacity in the local simulator path, not real 2.1G RF equivalence.
- A future stable 2.1G/FDD RedCap YAML must rerun this same tutorial before claiming full paper equivalence.
