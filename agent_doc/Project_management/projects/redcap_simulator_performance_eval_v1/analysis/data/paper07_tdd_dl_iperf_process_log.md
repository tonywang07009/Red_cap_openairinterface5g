# PAPER-07 TDD DL iperf Process Log

## Source
- Date: 2026-05-23
- Scenario: TDD RedCap RFsim
- Direction: DL, measured by iperf3 reverse mode (`-R`)
- UE: `rfsim5g-oai-nr-ue1_redcap`
- UE tunnel IP: `10.0.0.2`
- Server: `oai-ext-dn`
- Server IP: `192.168.72.135`

## Run Summary
| Run ID | Offered Rate | PDSCH 256QAM Enabled | Receiver Mbps | Jitter ms | Lost / Total | UDP Loss % | Active gNB DLSCH Evidence |
|---|---:|---:|---:|---:|---:|---:|---|
| PAPER07-TDD-DL-106M-PRE-PDSCH | 106M | 0 | 106 | 0.028 | 284 / 549831 | 0.052 | `MCS (0) 28` |
| PAPER07-TDD-DL-141M-PRE-PDSCH | 141M | 0 | 141 | 0.033 | 422 / 731598 | 0.058 | `MCS (0) 28` |
| PAPER07-TDD-DL-141M-TRUE-PDSCH256 | 141M | 1 | 141 | 0.084 | 422 / 731299 | 0.058 | `MCS (1) 27` |

## Raw iperf Output: PAPER07-TDD-DL-106M-PRE-PDSCH
```text
Command:
docker exec rfsim5g-oai-nr-ue1_redcap iperf3 -c 192.168.72.135 -B 10.0.0.2 -t 60 -u -b 106M -R

Connecting to host 192.168.72.135, port 5201
Reverse mode, remote host 192.168.72.135 is sending
[  5] local 10.0.0.2 port 36614 connected to 192.168.72.135 port 5201
[ ID] Interval           Transfer     Bitrate         Jitter    Lost/Total Datagrams
[  5]   0.00-1.00   sec  13.3 MBytes   112 Mbits/sec  0.025 ms  284/9940 (2.9%)
[  5]   1.00-2.00   sec  12.6 MBytes   106 Mbits/sec  0.045 ms  0/9159 (0%)
[  5]   2.00-3.00   sec  12.6 MBytes   106 Mbits/sec  0.033 ms  0/9150 (0%)
[  5]   3.00-4.00   sec  12.6 MBytes   106 Mbits/sec  0.027 ms  0/9145 (0%)
[  5]   4.00-5.00   sec  12.6 MBytes   106 Mbits/sec  0.044 ms  0/9156 (0%)
[  5]   5.00-6.00   sec  12.6 MBytes   106 Mbits/sec  0.040 ms  0/9151 (0%)
[  5]   6.00-7.00   sec  12.6 MBytes   106 Mbits/sec  0.057 ms  0/9145 (0%)
[  5]   7.00-8.00   sec  12.6 MBytes   106 Mbits/sec  0.031 ms  0/9156 (0%)
[  5]   8.00-9.00   sec  12.6 MBytes   106 Mbits/sec  0.023 ms  0/9151 (0%)
[  5]   9.00-10.00  sec  12.6 MBytes   106 Mbits/sec  0.037 ms  0/9142 (0%)
[  5]  10.00-11.00  sec  12.6 MBytes   106 Mbits/sec  0.035 ms  0/9149 (0%)
[  5]  11.00-12.00  sec  12.6 MBytes   106 Mbits/sec  0.039 ms  0/9160 (0%)
[  5]  12.00-13.00  sec  12.6 MBytes   106 Mbits/sec  0.032 ms  0/9151 (0%)
[  5]  13.00-14.00  sec  12.6 MBytes   106 Mbits/sec  0.040 ms  0/9150 (0%)
[  5]  14.00-15.00  sec  12.6 MBytes   106 Mbits/sec  0.045 ms  0/9152 (0%)
[  5]  15.00-16.00  sec  12.6 MBytes   106 Mbits/sec  0.056 ms  0/9140 (0%)
[  5]  16.00-17.00  sec  12.6 MBytes   106 Mbits/sec  0.045 ms  0/9157 (0%)
[  5]  17.00-18.00  sec  12.6 MBytes   106 Mbits/sec  0.021 ms  0/9154 (0%)
[  5]  18.00-19.00  sec  12.6 MBytes   106 Mbits/sec  0.040 ms  0/9150 (0%)
[  5]  19.00-20.00  sec  12.6 MBytes   106 Mbits/sec  0.032 ms  0/9151 (0%)
[  5]  20.00-21.00  sec  12.6 MBytes   106 Mbits/sec  0.044 ms  0/9150 (0%)
[  5]  21.00-22.00  sec  12.6 MBytes   106 Mbits/sec  0.023 ms  0/9151 (0%)
[  5]  22.00-23.00  sec  12.6 MBytes   106 Mbits/sec  0.026 ms  0/9141 (0%)
[  5]  23.00-24.00  sec  12.6 MBytes   106 Mbits/sec  0.029 ms  0/9160 (0%)
[  5]  24.00-25.00  sec  12.6 MBytes   106 Mbits/sec  0.048 ms  0/9153 (0%)
[  5]  25.00-26.00  sec  12.6 MBytes   106 Mbits/sec  0.051 ms  0/9141 (0%)
[  5]  26.00-27.00  sec  12.6 MBytes   106 Mbits/sec  0.047 ms  0/9157 (0%)
[  5]  27.00-28.00  sec  12.6 MBytes   106 Mbits/sec  0.021 ms  0/9151 (0%)
[  5]  28.00-29.00  sec  12.6 MBytes   106 Mbits/sec  0.082 ms  0/9146 (0%)
[  5]  29.00-30.00  sec  12.6 MBytes   106 Mbits/sec  0.026 ms  0/9155 (0%)
[  5]  30.00-31.00  sec  12.6 MBytes   106 Mbits/sec  0.041 ms  0/9152 (0%)
[  5]  31.00-32.00  sec  12.6 MBytes   106 Mbits/sec  0.034 ms  0/9150 (0%)
[  5]  32.00-33.00  sec  12.6 MBytes   106 Mbits/sec  0.032 ms  0/9151 (0%)
[  5]  33.00-34.00  sec  12.6 MBytes   106 Mbits/sec  0.028 ms  0/9149 (0%)
[  5]  34.00-35.00  sec  12.6 MBytes   106 Mbits/sec  0.042 ms  0/9143 (0%)
[  5]  35.00-36.00  sec  12.6 MBytes   106 Mbits/sec  0.042 ms  0/9155 (0%)
[  5]  36.00-37.00  sec  12.6 MBytes   106 Mbits/sec  0.021 ms  0/9155 (0%)
[  5]  37.00-38.00  sec  12.6 MBytes   106 Mbits/sec  0.053 ms  0/9150 (0%)
[  5]  38.00-39.00  sec  12.6 MBytes   106 Mbits/sec  0.043 ms  0/9150 (0%)
[  5]  39.00-40.00  sec  12.6 MBytes   106 Mbits/sec  0.024 ms  0/9151 (0%)
[  5]  40.00-41.00  sec  12.6 MBytes   106 Mbits/sec  0.050 ms  0/9152 (0%)
[  5]  41.00-42.00  sec  12.6 MBytes   106 Mbits/sec  0.045 ms  0/9144 (0%)
[  5]  42.00-43.00  sec  12.6 MBytes   106 Mbits/sec  0.028 ms  0/9155 (0%)
[  5]  43.00-44.00  sec  12.6 MBytes   106 Mbits/sec  0.038 ms  0/9148 (0%)
[  5]  44.00-45.00  sec  12.6 MBytes   106 Mbits/sec  0.021 ms  0/9153 (0%)
[  5]  45.00-46.00  sec  12.6 MBytes   106 Mbits/sec  0.055 ms  0/9147 (0%)
[  5]  46.00-47.00  sec  12.6 MBytes   106 Mbits/sec  0.025 ms  0/9156 (0%)
[  5]  47.00-48.00  sec  12.6 MBytes   106 Mbits/sec  0.041 ms  0/9149 (0%)
[  5]  48.00-49.00  sec  12.6 MBytes   106 Mbits/sec  0.039 ms  0/9151 (0%)
[  5]  49.00-50.00  sec  12.6 MBytes   106 Mbits/sec  0.021 ms  0/9141 (0%)
[  5]  50.00-51.00  sec  12.6 MBytes   106 Mbits/sec  0.038 ms  0/9160 (0%)
[  5]  51.00-52.00  sec  12.6 MBytes   106 Mbits/sec  0.084 ms  0/9143 (0%)
[  5]  52.00-53.00  sec  12.6 MBytes   106 Mbits/sec  0.062 ms  0/9158 (0%)
[  5]  53.00-54.00  sec  12.6 MBytes   106 Mbits/sec  0.066 ms  0/9143 (0%)
[  5]  54.00-55.00  sec  12.6 MBytes   106 Mbits/sec  0.042 ms  0/9151 (0%)
[  5]  55.00-56.00  sec  12.6 MBytes   106 Mbits/sec  0.052 ms  0/9153 (0%)
[  5]  56.00-57.00  sec  12.6 MBytes   106 Mbits/sec  0.048 ms  0/9156 (0%)
[  5]  57.00-58.00  sec  12.6 MBytes   106 Mbits/sec  0.036 ms  0/9142 (0%)
[  5]  58.00-59.00  sec  12.6 MBytes   106 Mbits/sec  0.015 ms  0/9158 (0%)
[  5]  59.00-60.00  sec  12.6 MBytes   106 Mbits/sec  0.028 ms  0/9151 (0%)
- - - - - - - - - - - - - - - - - - - - - - - - -
[ ID] Interval           Transfer     Bitrate         Jitter    Lost/Total Datagrams
[  5]   0.00-60.09  sec   759 MBytes   106 Mbits/sec  0.000 ms  0/0 (0%)  sender
[  5]   0.00-60.00  sec   759 MBytes   106 Mbits/sec  0.028 ms  284/549831 (0.052%)  receiver

iperf Done.
```

## Raw iperf Output: PAPER07-TDD-DL-141M-PRE-PDSCH
```text
Command:
docker exec rfsim5g-oai-nr-ue1_redcap iperf3 -c 192.168.72.135 -B 10.0.0.2 -t 60 -u -b 141M -R

Connecting to host 192.168.72.135, port 5201
Reverse mode, remote host 192.168.72.135 is sending
[  5] local 10.0.0.2 port 49039 connected to 192.168.72.135 port 5201
[ ID] Interval           Transfer     Bitrate         Jitter    Lost/Total Datagrams
[  5]   0.00-1.00   sec  18.0 MBytes   151 Mbits/sec  0.043 ms  422/13455 (3.1%)
[  5]   1.00-2.00   sec  16.8 MBytes   141 Mbits/sec  0.033 ms  0/12169 (0%)
[  5]   2.00-3.00   sec  16.8 MBytes   141 Mbits/sec  0.046 ms  0/12172 (0%)
[  5]   3.00-4.00   sec  16.8 MBytes   141 Mbits/sec  0.042 ms  0/12171 (0%)
[  5]   4.00-5.00   sec  16.8 MBytes   141 Mbits/sec  0.028 ms  0/12173 (0%)
[  5]   5.00-6.00   sec  16.8 MBytes   141 Mbits/sec  0.029 ms  0/12172 (0%)
[  5]   6.00-7.00   sec  16.8 MBytes   141 Mbits/sec  0.065 ms  0/12172 (0%)
[  5]   7.00-8.00   sec  16.8 MBytes   141 Mbits/sec  0.039 ms  0/12172 (0%)
[  5]   8.00-9.00   sec  16.8 MBytes   141 Mbits/sec  0.043 ms  0/12172 (0%)
[  5]   9.00-10.00  sec  16.8 MBytes   141 Mbits/sec  0.044 ms  0/12172 (0%)
[  5]  10.00-11.00  sec  16.8 MBytes   141 Mbits/sec  0.067 ms  0/12167 (0%)
[  5]  11.00-12.00  sec  16.8 MBytes   141 Mbits/sec  0.048 ms  0/12177 (0%)
[  5]  12.00-13.00  sec  16.8 MBytes   141 Mbits/sec  0.039 ms  0/12174 (0%)
[  5]  13.00-14.00  sec  16.8 MBytes   141 Mbits/sec  0.026 ms  0/12170 (0%)
[  5]  14.00-15.00  sec  16.8 MBytes   141 Mbits/sec  0.043 ms  0/12172 (0%)
[  5]  15.00-16.00  sec  16.8 MBytes   141 Mbits/sec  0.063 ms  0/12171 (0%)
[  5]  16.00-17.00  sec  16.8 MBytes   141 Mbits/sec  0.017 ms  0/12172 (0%)
[  5]  17.00-18.00  sec  16.8 MBytes   141 Mbits/sec  0.038 ms  0/12173 (0%)
[  5]  18.00-19.00  sec  16.8 MBytes   141 Mbits/sec  0.031 ms  0/12172 (0%)
[  5]  19.00-20.00  sec  16.8 MBytes   141 Mbits/sec  0.098 ms  0/12166 (0%)
[  5]  20.00-21.00  sec  16.8 MBytes   141 Mbits/sec  0.025 ms  0/12178 (0%)
[  5]  21.00-22.00  sec  16.8 MBytes   141 Mbits/sec  0.072 ms  0/12162 (0%)
[  5]  22.00-23.00  sec  16.8 MBytes   141 Mbits/sec  0.029 ms  0/12181 (0%)
[  5]  23.00-24.00  sec  16.8 MBytes   141 Mbits/sec  0.025 ms  0/12173 (0%)
[  5]  24.00-25.00  sec  16.8 MBytes   141 Mbits/sec  0.035 ms  0/12171 (0%)
[  5]  25.00-26.00  sec  16.8 MBytes   141 Mbits/sec  0.063 ms  0/12172 (0%)
[  5]  26.00-27.00  sec  16.8 MBytes   141 Mbits/sec  0.058 ms  0/12172 (0%)
[  5]  27.00-28.00  sec  16.8 MBytes   141 Mbits/sec  0.042 ms  0/12172 (0%)
[  5]  28.00-29.00  sec  16.8 MBytes   141 Mbits/sec  0.048 ms  0/12176 (0%)
[  5]  29.00-30.00  sec  16.8 MBytes   141 Mbits/sec  0.034 ms  0/12168 (0%)
[  5]  30.00-31.00  sec  16.8 MBytes   141 Mbits/sec  0.050 ms  0/12172 (0%)
[  5]  31.00-32.00  sec  16.8 MBytes   141 Mbits/sec  0.034 ms  0/12174 (0%)
[  5]  32.00-33.00  sec  16.8 MBytes   141 Mbits/sec  0.039 ms  0/12171 (0%)
[  5]  33.00-34.00  sec  16.8 MBytes   141 Mbits/sec  0.046 ms  0/12171 (0%)
[  5]  34.00-35.00  sec  16.8 MBytes   141 Mbits/sec  0.026 ms  0/12172 (0%)
[  5]  35.00-36.00  sec  16.8 MBytes   141 Mbits/sec  0.044 ms  0/12171 (0%)
[  5]  36.00-37.00  sec  16.8 MBytes   141 Mbits/sec  0.044 ms  0/12172 (0%)
[  5]  37.00-38.00  sec  16.8 MBytes   141 Mbits/sec  0.050 ms  0/12171 (0%)
[  5]  38.00-39.00  sec  16.8 MBytes   141 Mbits/sec  0.025 ms  0/12174 (0%)
[  5]  39.00-40.00  sec  16.8 MBytes   141 Mbits/sec  0.045 ms  0/12173 (0%)
[  5]  40.00-41.00  sec  16.8 MBytes   141 Mbits/sec  0.064 ms  0/12171 (0%)
[  5]  41.00-42.00  sec  16.8 MBytes   141 Mbits/sec  0.021 ms  0/12172 (0%)
[  5]  42.00-43.00  sec  16.8 MBytes   141 Mbits/sec  0.048 ms  0/12172 (0%)
[  5]  43.00-44.00  sec  16.8 MBytes   141 Mbits/sec  0.030 ms  0/12171 (0%)
[  5]  44.00-45.00  sec  16.8 MBytes   141 Mbits/sec  0.032 ms  0/12172 (0%)
[  5]  45.00-46.00  sec  16.8 MBytes   141 Mbits/sec  0.044 ms  0/12175 (0%)
[  5]  46.00-47.00  sec  16.8 MBytes   141 Mbits/sec  0.036 ms  0/12170 (0%)
[  5]  47.00-48.00  sec  16.8 MBytes   141 Mbits/sec  0.033 ms  0/12171 (0%)
[  5]  48.00-49.00  sec  16.8 MBytes   141 Mbits/sec  0.059 ms  0/12174 (0%)
[  5]  49.00-50.00  sec  16.8 MBytes   141 Mbits/sec  0.056 ms  0/12158 (0%)
[  5]  50.00-51.00  sec  16.8 MBytes   141 Mbits/sec  0.046 ms  0/12185 (0%)
[  5]  51.00-52.00  sec  16.8 MBytes   141 Mbits/sec  0.045 ms  0/12171 (0%)
[  5]  52.00-53.00  sec  16.8 MBytes   141 Mbits/sec  0.032 ms  0/12172 (0%)
[  5]  53.00-54.00  sec  16.8 MBytes   141 Mbits/sec  0.044 ms  0/12172 (0%)
[  5]  54.00-55.00  sec  16.8 MBytes   141 Mbits/sec  0.053 ms  0/12173 (0%)
[  5]  55.00-56.00  sec  16.8 MBytes   141 Mbits/sec  0.057 ms  0/12172 (0%)
[  5]  56.00-57.00  sec  16.8 MBytes   141 Mbits/sec  0.020 ms  0/12171 (0%)
[  5]  57.00-58.00  sec  16.8 MBytes   141 Mbits/sec  0.045 ms  0/12173 (0%)
[  5]  58.00-59.00  sec  16.8 MBytes   141 Mbits/sec  0.047 ms  0/12159 (0%)
[  5]  59.00-60.00  sec  16.8 MBytes   141 Mbits/sec  0.033 ms  0/12184 (0%)
- - - - - - - - - - - - - - - - - - - - - - - - -
[ ID] Interval           Transfer     Bitrate         Jitter    Lost/Total Datagrams
[  5]   0.00-60.11  sec  1010 MBytes   141 Mbits/sec  0.000 ms  0/0 (0%)  sender
[  5]   0.00-60.00  sec  1010 MBytes   141 Mbits/sec  0.033 ms  422/731598 (0.058%)  receiver

iperf Done.
```

## Raw iperf Output: PAPER07-TDD-DL-141M-TRUE-PDSCH256
```text
Command:
docker exec rfsim5g-oai-nr-ue1_redcap iperf3 -c 192.168.72.135 -B 10.0.0.2 -t 60 -u -b 141M -R

Connecting to host 192.168.72.135, port 5201
Reverse mode, remote host 192.168.72.135 is sending
[  5] local 10.0.0.2 port 35517 connected to 192.168.72.135 port 5201
[ ID] Interval           Transfer     Bitrate         Jitter    Lost/Total Datagrams
[  5]   0.00-1.00   sec  17.6 MBytes   147 Mbits/sec  0.045 ms  422/13148 (3.2%)
[  5]   1.00-2.00   sec  16.8 MBytes   141 Mbits/sec  0.054 ms  0/12184 (0%)
[  5]   2.00-3.00   sec  16.8 MBytes   141 Mbits/sec  0.054 ms  0/12175 (0%)
[  5]   3.00-4.00   sec  16.8 MBytes   141 Mbits/sec  0.042 ms  0/12169 (0%)
[  5]   4.00-5.00   sec  16.8 MBytes   141 Mbits/sec  0.051 ms  0/12172 (0%)
[  5]   5.00-6.00   sec  16.8 MBytes   141 Mbits/sec  0.039 ms  0/12173 (0%)
[  5]   6.00-7.00   sec  16.8 MBytes   141 Mbits/sec  0.026 ms  0/12171 (0%)
[  5]   7.00-8.00   sec  16.8 MBytes   141 Mbits/sec  0.027 ms  0/12174 (0%)
[  5]   8.00-9.00   sec  16.8 MBytes   141 Mbits/sec  0.024 ms  0/12170 (0%)
[  5]   9.00-10.00  sec  16.8 MBytes   141 Mbits/sec  0.047 ms  0/12172 (0%)
[  5]  10.00-11.00  sec  16.8 MBytes   141 Mbits/sec  0.051 ms  0/12172 (0%)
[  5]  11.00-12.00  sec  16.8 MBytes   141 Mbits/sec  0.052 ms  0/12172 (0%)
[  5]  12.00-13.00  sec  16.8 MBytes   141 Mbits/sec  0.058 ms  0/12171 (0%)
[  5]  13.00-14.00  sec  16.8 MBytes   141 Mbits/sec  0.032 ms  0/12173 (0%)
[  5]  14.00-15.00  sec  16.8 MBytes   141 Mbits/sec  0.024 ms  0/12172 (0%)
[  5]  15.00-16.00  sec  16.8 MBytes   141 Mbits/sec  0.073 ms  0/12174 (0%)
[  5]  16.00-17.00  sec  16.8 MBytes   141 Mbits/sec  0.076 ms  0/12169 (0%)
[  5]  17.00-18.00  sec  16.8 MBytes   141 Mbits/sec  0.060 ms  0/12173 (0%)
[  5]  18.00-19.00  sec  16.8 MBytes   141 Mbits/sec  0.087 ms  0/12161 (0%)
[  5]  19.00-20.00  sec  16.8 MBytes   141 Mbits/sec  0.051 ms  0/12183 (0%)
[  5]  20.00-21.00  sec  16.8 MBytes   141 Mbits/sec  0.040 ms  0/12172 (0%)
[  5]  21.00-22.00  sec  16.8 MBytes   141 Mbits/sec  0.070 ms  0/12162 (0%)
[  5]  22.00-23.00  sec  16.8 MBytes   141 Mbits/sec  0.047 ms  0/12183 (0%)
[  5]  23.00-24.00  sec  16.8 MBytes   141 Mbits/sec  0.044 ms  0/12170 (0%)
[  5]  24.00-25.00  sec  16.8 MBytes   141 Mbits/sec  0.060 ms  0/12172 (0%)
[  5]  25.00-26.00  sec  16.8 MBytes   141 Mbits/sec  0.026 ms  0/12172 (0%)
[  5]  26.00-27.00  sec  16.8 MBytes   141 Mbits/sec  0.066 ms  0/12164 (0%)
[  5]  27.00-28.00  sec  16.8 MBytes   141 Mbits/sec  0.026 ms  0/12180 (0%)
[  5]  28.00-29.00  sec  16.8 MBytes   141 Mbits/sec  0.068 ms  0/12174 (0%)
[  5]  29.00-30.00  sec  16.8 MBytes   141 Mbits/sec  0.058 ms  0/12170 (0%)
[  5]  30.00-31.00  sec  16.8 MBytes   141 Mbits/sec  0.063 ms  0/12172 (0%)
[  5]  31.00-32.00  sec  16.8 MBytes   141 Mbits/sec  0.058 ms  0/12169 (0%)
[  5]  32.00-33.00  sec  16.8 MBytes   141 Mbits/sec  0.047 ms  0/12175 (0%)
[  5]  33.00-34.00  sec  16.8 MBytes   141 Mbits/sec  0.045 ms  0/12171 (0%)
[  5]  34.00-35.00  sec  16.8 MBytes   141 Mbits/sec  0.040 ms  0/12173 (0%)
[  5]  35.00-36.00  sec  16.8 MBytes   141 Mbits/sec  0.036 ms  0/12172 (0%)
[  5]  36.00-37.00  sec  16.8 MBytes   141 Mbits/sec  0.170 ms  0/12155 (0%)
[  5]  37.00-38.00  sec  16.8 MBytes   141 Mbits/sec  0.070 ms  0/12189 (0%)
[  5]  38.00-39.00  sec  16.8 MBytes   141 Mbits/sec  0.053 ms  0/12173 (0%)
[  5]  39.00-40.00  sec  16.8 MBytes   141 Mbits/sec  0.033 ms  0/12171 (0%)
[  5]  40.00-41.00  sec  16.8 MBytes   141 Mbits/sec  0.046 ms  0/12172 (0%)
[  5]  41.00-42.00  sec  16.8 MBytes   141 Mbits/sec  0.066 ms  0/12172 (0%)
[  5]  42.00-43.00  sec  16.8 MBytes   141 Mbits/sec  0.043 ms  0/12173 (0%)
[  5]  43.00-44.00  sec  16.8 MBytes   141 Mbits/sec  0.041 ms  0/12170 (0%)
[  5]  44.00-45.00  sec  16.8 MBytes   141 Mbits/sec  0.054 ms  0/12173 (0%)
[  5]  45.00-46.00  sec  16.8 MBytes   141 Mbits/sec  0.031 ms  0/12171 (0%)
[  5]  46.00-47.00  sec  16.8 MBytes   141 Mbits/sec  0.038 ms  0/12175 (0%)
[  5]  47.00-48.00  sec  16.8 MBytes   141 Mbits/sec  0.053 ms  0/12169 (0%)
[  5]  48.00-49.00  sec  16.8 MBytes   141 Mbits/sec  0.045 ms  0/12172 (0%)
[  5]  49.00-50.00  sec  16.8 MBytes   141 Mbits/sec  0.024 ms  0/12172 (0%)
[  5]  50.00-51.00  sec  16.8 MBytes   141 Mbits/sec  0.039 ms  0/12161 (0%)
[  5]  51.00-52.00  sec  16.8 MBytes   141 Mbits/sec  0.049 ms  0/12183 (0%)
[  5]  52.00-53.00  sec  16.8 MBytes   141 Mbits/sec  0.086 ms  0/12164 (0%)
[  5]  53.00-54.00  sec  16.8 MBytes   141 Mbits/sec  0.057 ms  0/12180 (0%)
[  5]  54.00-55.00  sec  16.8 MBytes   141 Mbits/sec  0.042 ms  0/12172 (0%)
[  5]  55.00-56.00  sec  16.8 MBytes   141 Mbits/sec  0.035 ms  0/12172 (0%)
[  5]  56.00-57.00  sec  16.8 MBytes   141 Mbits/sec  0.027 ms  0/12173 (0%)
[  5]  57.00-58.00  sec  16.8 MBytes   141 Mbits/sec  0.025 ms  0/12171 (0%)
[  5]  58.00-59.00  sec  16.8 MBytes   141 Mbits/sec  0.064 ms  0/12172 (0%)
[  5]  59.00-60.00  sec  16.8 MBytes   141 Mbits/sec  0.084 ms  0/12165 (0%)
- - - - - - - - - - - - - - - - - - - - - - - - -
[ ID] Interval           Transfer     Bitrate         Jitter    Lost/Total Datagrams
[  5]   0.00-60.09  sec  1010 MBytes   141 Mbits/sec  0.000 ms  0/0 (0%)  sender
[  5]   0.00-60.00  sec  1009 MBytes   141 Mbits/sec  0.084 ms  422/731299 (0.058%)  receiver

iperf Done.
```
