# Paper-11 Service-Gate Reproduction Tutorial

[English](./paper11_real_network_reproduction_tutorial.en.md) | [繁體中文](./paper11_real_network_reproduction_tutorial.zh-TW.md)

## Goal

- Reproduce Paper-11 service-level RedCap validation logic on OAI RFsim.
- Measure UL/DL throughput, UDP loss, jitter, and ping RTT.
- Classification: [Service-Gate Proxy], not real-network RF equivalence.

## Inputs

| Item | Value |
|---|---|
| Main script | `redcap_interface/paper11_iperf_live_demo.sh` |
| Display entry | `bash redcap_interface/mmtc.display.bash paper11-live` |
| Historical notes | `paper11_real_network_reproduction_step_by_step.md` |
| Gap diagnosis | `paper11_dl_gap_diagnosis.md` |

## Procedure

1. Confirm an RFsim runtime is already running:

```bash
docker ps -a
docker exec rfsim5g-oai-nr-ue1_redcap ip -4 -o addr show dev oaitun_ue1
docker exec oai-ext-dn ip -4 -o addr show dev eth0
```

2. Run the visible service-gate demo:

```bash
P11_PANEL=1 \
P11_MODE=both \
P11_UL_RATE=17M \
P11_DL_RATE=68M \
P11_DURATION=20 \
bash redcap_interface/paper11_iperf_live_demo.sh
```

3. Run application rows as needed:

```bash
# Industrial sensor
P11_PANEL=1 P11_MODE=both P11_UL_RATE=2M P11_DL_RATE=2M P11_DURATION=20 \
  bash redcap_interface/paper11_iperf_live_demo.sh

# Video high-end
P11_PANEL=1 P11_MODE=both P11_UL_RATE=17M P11_DL_RATE=25M P11_DURATION=20 \
  bash redcap_interface/paper11_iperf_live_demo.sh

# Wearable reference
P11_PANEL=1 P11_MODE=both P11_UL_RATE=5M P11_DL_RATE=50M P11_DURATION=20 \
  bash redcap_interface/paper11_iperf_live_demo.sh
```

## Pass Criteria

| Scenario | Gate |
|---|---|
| Industrial sensor | UL/DL reach `2 Mbps`; 32-byte RTT is below `100 ms`. |
| Video high-end | DL reaches `25 Mbps`; RTT is below `500 ms`; loss is below `1%`. |
| Wearable | UL reaches `5 Mbps`; DL remains within the `5-50 Mbps` reference range. |
| Far-point service gate | UL approaches `17 Mbps`; DL `68 Mbps` may be [PASS_WITH_GAP]. |

## Evidence To Save

- Ping logs.
- iperf live raw logs.
- Summary CSV under `analysis/data/`.
- Formal report under `analysis/`.

## Limits

- Physical CQT, RSRP/SINR, coverage distance, and power-current measurements are proxy-only or not directly comparable.
- DL gap analysis must cite `paper11_dl_gap_diagnosis.md` when DL does not reach the target.
