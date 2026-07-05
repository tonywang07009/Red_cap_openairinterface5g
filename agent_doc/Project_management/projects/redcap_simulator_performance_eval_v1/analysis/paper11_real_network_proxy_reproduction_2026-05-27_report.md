# PAPER-11 Real-Network RedCap Proxy Reproduction Report

## 1. Technical Background
- [Paper Anchor]: `Research on RedCap UE’s performance indicators in real networkto support iot applications.pdf`.
- [Paper Objective]: evaluate [RedCap UE] rate, latency, coverage, and power in a real commercial network for IoT applications.
- [Local Objective]: reproduce the paper's [service validation logic] on the OAI RFsim RedCap platform.
- [Spec Mapping]:
  - [TS 38.306 Section 4.1.2]: maximum data-rate formula used by the paper.
  - [3GPP TR 38.875]: application requirement source cited by the paper; exact clause numbers are [Needs Verification].
- [Boundary]: RFsim can reproduce [traffic], [latency], and [stability] behavior; RFsim cannot directly reproduce commercial-network RF coverage distance or COTS UE current in mA.

## 2. Key Functions / Data Structures Used
- [Runtime Script]: `redcap_interface/paper11_iperf_live_demo.sh`.
- [Traffic Tool]: `iperf3 -i 1` in UE container, with server on `oai-ext-dn`.
- [UE Container]: `rfsim5g-oai-nr-ue1_redcap`.
- [Server Container]: `oai-ext-dn`.
- [UE Tunnel]: `oaitun_ue1`, observed UE IP `10.0.0.2`.
- [Latency Target]: `10.0.0.1` derived from UE tunnel subnet.
- [iperf Server IP]: `192.168.72.135`.

## 3. Test Results Summary
| Scenario | Paper Gate / Reference | Local Offered Load | Local Result | Verdict |
|---|---|---|---|---|
| Industrial wireless sensor | data rate `<2 Mbps`, E2E latency `<100 ms` | UL `2M`, DL `2M` | UL `1.98 Mbps`, DL `2.01 Mbps`, 32B RTT `47.722 ms`, 1500B RTT `105.556 ms` | [PASS_WITH_GAP] |
| Video surveillance high-end | DL `7.5-25 Mbps`, latency `<500 ms` | UL `17M`, DL `25M` | UL `16.2 Mbps`, DL `25.6 Mbps`, 32B RTT `48.483 ms`, 1500B RTT `59.721 ms`, DL loss `0.017%` | [PASS] |
| Wearable reference | DL `5-50 Mbps`, UL `2-5 Mbps` | UL `5M`, DL `50M` | UL `4.97 Mbps`, DL `30.3 Mbps`, 32B RTT `49.217 ms`, 1500B RTT `48.710 ms`, DL loss `0.47%` | [PASS_WITH_GAP] |
| Paper far-point RedCap result | paper reports DL `68 Mbps`, UL `17 Mbps` | UL `17M`, DL `68M` | UL `16.8 Mbps`, DL `32.7 Mbps`, 32B RTT `37.911 ms`, 1500B RTT `60.544 ms`, DL loss `0.63%` | [PASS_WITH_GAP] |

## 4. Evidence
- [Combined CSV]: `analysis/data/paper11_live_iperf_summary_2026-05-27.csv`.
- [Industrial Raw Directory]: `analysis/data/paper11_live_iperf_raw/paper11_app_industrial_2026-05-27_23-32-00/`.
- [Video Raw Directory]: `analysis/data/paper11_live_iperf_raw/paper11_app_video_high_2026-05-27_23-33-30/`.
- [Wearable Raw Directory]: `analysis/data/paper11_live_iperf_raw/paper11_app_wearable_2026-05-27_23-34-10/`.
- [Far Gate Raw Directory]: `analysis/data/paper11_live_iperf_raw/paper11_live_iperf_2026-05-27_23-30-37/`.

## 5. Interpretation
- [Reproduced]:
  - The platform can visibly inject iperf traffic and capture interval throughput.
  - The platform passes the [video high-end] gate in this RFsim setup.
  - The platform supports the [industrial sensor] throughput gate, with a latency gap for the 1500-byte ping row.
  - The platform supports [wearable] UL and a mid-range DL rate, but not the top `50 Mbps` DL target in the short `8 s` run.
- [Not Fully Reproduced]:
  - The paper's far-point DL `68 Mbps` was not reached; the local receiver throughput was `32.7 Mbps`.
  - The paper's physical coverage and real UE power-current results remain [Not Directly Comparable].
- [Current Claim]:
  - This RFsim RedCap simulator is valid for PAPER-11 [service-level traffic and latency reproduction].
  - It is not yet valid for claiming physical [coverage distance] or [UE mA power] equivalence.

## 6. Practice Exercises
- [Basic]: In the PAPER-11 far-gate row, why is UL considered reproduced but DL only [PASS_WITH_GAP]?
- [Applied]: Modify `P11_DL_RATE` and rerun the live demo to find the maximum stable DL receiver throughput with `<1%` loss.
- [Advanced]: Design an RFsim channel proxy sweep that maps near/middle/far CQT points to reproducible simulator parameters without claiming calibrated RSRP/SINR.
