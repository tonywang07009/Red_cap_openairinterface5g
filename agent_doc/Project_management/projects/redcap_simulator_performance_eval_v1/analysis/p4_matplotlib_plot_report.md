# P4 Matplotlib Plot Report

## Summary
- Status: [COMPLETED]
- Source CSV: `/home/tonywang/OAI/Red_cap_openairinterface5g/agent_doc/Project_management/projects/redcap_simulator_performance_eval_v1/analysis/data/p3_runtime_metrics.csv`
- Rows plotted: 10
- Dataset class: [Strong Dataset] from P3.

## Generated Figures
- `plots/p4_throughput_vs_offered_rate.png`
- `plots/p4_throughput_vs_offered_rate.pdf`
- `plots/p4_throughput_vs_total_ues.png`
- `plots/p4_throughput_vs_total_ues.pdf`
- `plots/p4_rtt_latency_vs_total_ues.png`
- `plots/p4_rtt_latency_vs_total_ues.pdf`
- `plots/p4_jitter_vs_total_ues.png`
- `plots/p4_jitter_vs_total_ues.pdf`
- `plots/p4_packet_loss_vs_total_ues.png`
- `plots/p4_packet_loss_vs_total_ues.pdf`
- `plots/p4_sender_receiver_gap_by_run.png`
- `plots/p4_sender_receiver_gap_by_run.pdf`

## Axis Compliance
- X axes use simulator-controlled variables: [offered rate], [total UE compose pool], [run ID].
- Y axes use measured simulator metrics: [receiver Mbps], [sender Mbps], [RTT avg], [jitter], [packet loss], [throughput gap].
- Packet loss remains plotted even though all measured rows are 0%, because it is a required P3/P4 success metric.

## Key Observations For P5
- `DOE-L9-03` throughput gap: sender 85.000 Mbps, receiver 30.062 Mbps, gap 54.938 Mbps.
- `DOE-L9-05` throughput gap: sender 50.000 Mbps, receiver 30.275 Mbps, gap 19.725 Mbps.
- `DOE-L9-09` throughput gap: sender 85.000 Mbps, receiver 69.075 Mbps, gap 15.925 Mbps.
- All plotted rows have UDP loss 0% and gNB restart count 0.
- RTT increases when sampled UE count increases, especially 8 sampled UE rows.

## Guardrail
- These plots support RFsim trend analysis.
- Do not claim absolute paper-level throughput equivalence until P5 maps RFsim conditions to paper scenarios.
