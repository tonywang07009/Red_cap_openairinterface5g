# Work Daily - Runtime Menu Rate Unit Guard

## Task
- Diagnose a latest UE1 iperf log showing only `1.41 KBytes` / `193 bits/sec` over 60 seconds.

## Finding
- The log command was:
  - `docker exec rfsim5g-oai-nr-ue1_redcap iperf3 -c 192.168.72.135 -t 60 -B 10.0.0.2 -u -b 35`
- Root cause:
  - `35` was interpreted by iperf3 as bits/sec scale, not Mbps.
  - Correct PAPER-07 UL rate should be `35M`.
- User-plane health was not the root cause:
  - UE tunnel existed at `10.0.0.2/24`.
  - Ping to `10.0.0.1` had 0% loss.

## Fix
- Updated `ci-scripts/redcap_runtime_menu.sh`.
- Added rate normalization so unitless numeric values such as `35` become `35M`.
- The menu now prints a normalization message before running smoke validation.

## Validation
- `bash -n ci-scripts/redcap_runtime_menu.sh`: PASS.
- `printf 'q\n' | ci-scripts/redcap_runtime_menu.sh`: PASS.
- `git diff --check -- ci-scripts/redcap_runtime_menu.sh`: PASS.
- Direct short iperf with `-b 35M`, 5 seconds:
  - sender: `35.0 Mbits/sec`.
  - receiver: `34.7 Mbits/sec`.
  - loss: `0/15105 (0%)`.

