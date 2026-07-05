# PAPER-11 Real-Network RedCap Reproduction Step-by-Step

## 0. Scope
- [Paper]: `Research on RedCap UE’s performance indicators in real networkto support iot applications.pdf`.
- [Local Goal]: reproduce the paper's service-level validation logic on OAI RFsim.
- [Directly Measured]: iperf UL/DL throughput, UDP loss, jitter, and 32/1500-byte ping RTT.
- [Proxy Only]: physical CQT near/middle/far, RSRP/SINR, and coverage distance.
- [Not Directly Comparable]: COTS UE power current in mA without external instrumentation.

## 1. Confirm Paper Route
```bash
rg -n "PAPER-11|Research on RedCap" \
  redcap_doc/evaluation_papers/README.md \
  redcap_doc/mineru_markdown/scan_manifest.md \
  agent_doc/Project_management/projects/redcap_simulator_performance_eval_v1/literature/paper_index.md
```

Expected:
- [PAPER-11] appears in all three files.
- MinerU Markdown route points to `redcap_doc/mineru_markdown/evaluation_papers/...Research...pdf.md`.

## 2. Confirm Existing RFsim Runtime
```bash
docker ps -a
docker exec rfsim5g-oai-nr-ue1_redcap ip -4 -o addr show dev oaitun_ue1
docker exec oai-ext-dn ip -4 -o addr show dev eth0
```

Expected:
- `rfsim5g-oai-gnb_redcap` is running.
- `rfsim5g-oai-nr-ue1_redcap` is running.
- `oai-ext-dn` is running.
- UE has `oaitun_ue1`, usually `10.0.0.2/24`.

## 3. Run The Visible PAPER-11 iperf Demo
```bash
P11_PANEL=1 \
P11_MODE=both \
P11_UL_RATE=17M \
P11_DL_RATE=68M \
P11_DURATION=20 \
bash redcap_interface/paper11_iperf_live_demo.sh
```

Expected:
- The script first runs 32-byte and 1500-byte ping probes.
- Then the live panel shows UL and DL throughput once per second.
- Raw logs are written under:

```text
agent_doc/Project_management/projects/redcap_simulator_performance_eval_v1/analysis/data/paper11_live_iperf_raw/
```

## 4. Run Application-Gate Rows
Industrial sensor:

```bash
P11_PANEL=1 P11_MODE=both P11_UL_RATE=2M P11_DL_RATE=2M P11_DURATION=20 \
  bash redcap_interface/paper11_iperf_live_demo.sh
```

Video high-end:

```bash
P11_PANEL=1 P11_MODE=both P11_UL_RATE=17M P11_DL_RATE=25M P11_DURATION=20 \
  bash redcap_interface/paper11_iperf_live_demo.sh
```

Wearable reference:

```bash
P11_PANEL=1 P11_MODE=both P11_UL_RATE=5M P11_DL_RATE=50M P11_DURATION=20 \
  bash redcap_interface/paper11_iperf_live_demo.sh
```

Paper far-point service gate:

```bash
P11_PANEL=1 P11_MODE=both P11_UL_RATE=17M P11_DL_RATE=68M P11_DURATION=60 \
  bash redcap_interface/paper11_iperf_live_demo.sh
```

## 5. Standalone iperf Panel
Use this when you only want to observe current UL/DL without the PAPER-11 ping/report wrapper:

```bash
python3 redcap_interface/iperf_live_panel.py \
  --direction both \
  --ul-rate 17M \
  --dl-rate 68M \
  --duration 20
```

Menu path:

```bash
bash redcap_interface/mmtc.menu.bash
# choose:
# 18) Run standalone iperf live panel
```

## 6. Menu-Based Reproduction
```bash
bash redcap_interface/mmtc.menu.bash
```

Choose:
- `16) Run PAPER-07 reproduction bundle` for PAPER-07 peak-rate reproduction.
- `17) Run PAPER-11 reproduction with live iperf panel` for PAPER-11 service-gate reproduction.
- `18) Run standalone iperf live panel` for an independent UL/DL dashboard.
- `19) Show evaluation recovery manuals` to list this folder.
- `20) Run PAPER-11 Table 3 RedCap peak-rate proxy` for Table 3 target-rate validation.

Compatibility alias:

```bash
bash redcap_interface/mmtc.ment.bash
```

## 7. Interpret Results
| Scenario | Pass Gate |
|---|---|
| Industrial sensor | UL/DL reach `2 Mbps`; 32-byte RTT `<100 ms`; 1500-byte RTT should be recorded and classified |
| Video high-end | DL reaches `25 Mbps`; RTT `<500 ms`; loss `<1%` |
| Wearable | UL reaches `5 Mbps`; DL should remain within `5-50 Mbps` range |
| Paper far-point | UL near `17 Mbps`; DL target `68 Mbps` is stricter and may be [PASS_WITH_GAP] |

## 8. Known Gap From The First Run
- [First Far-Gate Result]: UL `16.8 Mbps`, DL `32.7 Mbps`.
- [Reason]: this was not the same profile as PAPER-07 DL `141 Mbps`.
- [See]: `paper11_dl_gap_diagnosis.md`.
- [Table 3 Follow-Up]: use `paper11_table3_2p1g_peak_rate_step_by_step.md` for the dedicated RedCap `90/169.5/226 Mbps` target-rate run.

## 9. Update Evidence
After each formal run, update:

```text
agent_doc/Project_management/projects/redcap_simulator_performance_eval_v1/analysis/data/paper11_live_iperf_summary_YYYY-MM-DD.csv
agent_doc/Project_management/projects/redcap_simulator_performance_eval_v1/analysis/paper11_real_network_proxy_reproduction_YYYY-MM-DD_report.md
agent_doc/Project_management/projects/redcap_simulator_performance_eval_v1/validation/paper11_real_network_proxy_test_matrix.md
```

## 10. Minimum Validation
```bash
bash -n redcap_interface/paper11_iperf_live_demo.sh
python3 -m py_compile redcap_interface/iperf_live_panel.py
git diff --check -- redcap_interface redcap_doc/evluation_recover
```
