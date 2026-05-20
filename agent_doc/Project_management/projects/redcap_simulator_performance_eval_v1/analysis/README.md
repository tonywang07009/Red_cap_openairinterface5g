# Analysis Workspace

## Directory Contract
- `analysis/data/`: parsed CSV files from RFsim runs.
- `analysis/scripts/`: Python scripts for parsing and plotting.
- `analysis/plots/`: generated PNG/PDF figures.

## Plotting Rule
- Use Python + matplotlib.
- Every plot must be reproducible from committed CSV + script.
- Every script should accept input/output paths as arguments once automation begins.

## Initial CSV Columns
```csv
run_id,ue_count,offered_rate_mbps,traffic_mode,sender_mbps,receiver_mbps,jitter_ms,udp_lost,udp_total,udp_loss_percent,rtt_min_ms,rtt_avg_ms,rtt_max_ms,ping_loss_percent,attach_success,pdu_success,tunnel_success,gnb_restart_count,status,notes
```
