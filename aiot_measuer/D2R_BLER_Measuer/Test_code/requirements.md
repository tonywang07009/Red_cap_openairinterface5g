# D2R BER Measurement Tool Requirements

## Formula concept

## CBRA M/SNR campaign profile

- The opt-in CBRA profile compares Paging and Access Trigger separately at `M = 2, 6, 12, 24`, 15 kHz SCS, and three R2D PRBs.
- Paging uses 224 MAC bits plus CRC16 = 240 PHY bits. Access Trigger uses 3 MAC bits plus CRC6 = 9 PHY bits.
- Each formal `(message_kind, M, SNR)` point has exactly 10,000 measured R2D packets. Setup Paging is excluded from a standalone Access Trigger point; missing or duplicate measured attempt indices are rejected.
- Each row carries one acknowledged `channel_epoch` and `channel_readback=true`; otherwise the point is invalid evidence and its BER/BLER/goodput are `null`.
- Control-bit BER compares only the message's MAC bits. BLER counts blocks that are not both CRC-valid and payload-matching; its 95% interval is Wilson.
- Goodput is `message_mac_bits * correctly_delivered_blocks / full_R2D_airtime_seconds`; failed R2D attempts remain in the denominator and cannot trigger early stopping.
- Run it with `bash run_ui.sh campaign --profile cbra --input campaign.jsonl --output campaign.json`.
- `plot --profile cbra` renders a 2x3 summary: Paging and Access Trigger rows by
  MAC/control-bit BER, payload BLER, and full-airtime goodput. The x-axis is
  `M` with each bar labelled by its calibrated SNR; it does not create an
  SNR curve from a single point per `(kind, M)`.
- CBRA plotting rejects invalid points or null BER/BLER/goodput values instead
  of presenting incomplete evidence as a measurement result.

- A Tag payload bit uses one Manchester/OOK pair at `SFS = 1`: `0 -> 10` and `1 -> 01`.
- The ideal-isolation received baseband model is `y_k = rho_k h_GT h_TR s_k + n_k`.
- `rho_k` is `1` for an ON chip and `0` for an OFF chip. The direct illuminating-CW to Reader path is excluded by the accepted ideal beam-isolation assumption.
- Each Rician leg has unit mean power and `K = 3 dB`. The two legs are independently drawn and their product is the backscatter channel.
- BER is `erroneous_payload_bits / compared_payload_bits`. Comparable CRC failures remain in the numerator and denominator.
- Packet-loss rate is `(undetected_packets + unaligned_packets) / actual_tx_packets`; a transmitted packet is counted even when no comparable payload exists.
- A complete packet is assigned to the 0.5 ms window containing its decode completion. An empty window has `ber = null`; known acquisition loss remains valid loss evidence, while missing comparison evidence invalidates the affected result and sets its loss rate to `null`.
- `ReaderBerObservation.to_dict()` is the JSON-ready boundary for persisting all counters and validity fields.
- The numerical reference is a separate model check, not a runtime result. Each duration uses an independent deterministic seed; the pilot comparison is exploratory and does not claim real-Reader equivalence. Equal chip energy follows the decoder boundary: the pair is unaligned and excluded from BER. RFsim ticks use the explicit sample rate with exact decimal arithmetic and half-up rounding.

## Parameters

| Parameter | Meaning | Status |
|---|---|---|
| `reader_ids` | Three Reader identifiers | Confirmed: `1, 2, 3` |
| `tag_count` | Tags present in the scenario | Confirmed: at most `100` |
| `visibility_seed` | Reproducible four-state assignment seed | Confirmed |
| `sample_rate_hz` | Explicit conversion input for RFsim sample ticks | Required; not inferred from a YAML file |
| `d2r_payload_bytes` | Existing RFsim inventory payload length | Confirmed: `16` bytes |
| `observation_window_ns` | BER observation-window width | Confirmed: `500000` ns |
| `duration_results` | Measured D2R duration/BER points for the plot | Filled only by verified measurement evidence |
| `duration_multiplier` | TS 38.291-aligned multiplier over `2,000,000 / 15,000` microseconds | `1/96, 1/32, 1/16, 1/8, 1/4, 1/2, 1, 2` |
| `actual_tx_packets` | Actual D2R packets transmitted in the observation record | Required denominator for packet-loss rate |
| `undetected_packets` | Transmitted packets with no detector hit | Required loss counter |
| `unaligned_packets` | Transmitted packets whose chips cannot be aligned | Required loss counter |
| `packet_loss_rate` | `(undetected_packets + unaligned_packets) / actual_tx_packets` | `null` when no packet was transmitted |
| `ideal_cross_reader_isolation` | Ignore other Readers' reflection as interference | Confirmed idealization |
| `ideal_acquisition_alignment` | Packet detection and alignment are available | Confirmed idealization; decoding can still fail |
| `channel_provenance` | Deterministic duration-specific RFsim channel key carried by the observation wire report | Required for runtime-to-record traceability |
| `campaign_manifest` | JSON array/object or JSONL rows keyed by duration, repeat, and cycle | Must contain all `8 x 5 x 100 = 4,000` variants; missing or duplicate rows are rejected |

## RFsim observation wire contract

- `AIOT_T2_OBSERVATION_MAGIC = 0x41494f42`, CBRA version `4`, fixed size `200` bytes, network byte order for multi-byte fields.
- `complete` and `crc_failure` carry TX truth and decoded payload; CRC failures remain comparable BER samples.
- `undetected` and `unaligned` increment the corresponding packet-loss counter. `invalid` preserves an invalid-evidence reason and leaves packet loss `null`.
- The two Rician legs use independent deterministic keys `(seed, duration, repeat, physical-link, tag, cycle)`, `K = 3 dB`, unit mean power. Duration variants are independent RFsim runs. The relay applies total complex noise power `0.1` to D2R samples only.
- Three-Reader isolation is represented by the runtime reader handle and relay routing. The legacy AIOTF 60-Tag profile remains separate from the accepted 100-Tag topology.

## Acceptance

- Run the UI through Bash:

```bash
bash run_ui.sh init --output result.json --sample-rate-hz <verified-rate>
bash run_ui.sh show --input result.json
bash run_ui.sh ingest-udp --input result.json --output measured.json --port <udp-port> --packets <n>
bash run_ui.sh reference --output reference.json --bits 20000
bash run_ui.sh plot --input measured.json --output ber-by-duration.png
bash run_ui.sh plot --profile cbra --input campaign.json --output cbra-summary.png
bash run_ui.sh campaign --input campaign.jsonl --output campaign.json
```

- JSON preserves `null` BER and invalid-evidence reasons.
- The legacy plot uses D2R bit duration on x-axis and BER on y-axis.
- The CBRA plot uses M on the x-axis and separates BER, BLER, and goodput by message kind.
- The tool does not generate synthetic BER values or a DRL reward/model.
- `reference` writes a numerical ON/OFF energy-detector baseline and labels it separately from measured observations; `plot` accepts only measured non-null BER points.
- `campaign` aggregates only complete fixed-budget manifests. It preserves packet, bit, loss, deferral, and invalid-run counters per duration; it never fills missing RFsim variants.
- The corrected pilot campaign has 40 RFsim jobs, 120 Reader files, and 4,000 cycle rows. Its exploratory numerical-reference comparison uses absolute BER tolerance `0.02`; it is not real-Reader equivalence evidence.
- The UE source emits `undetected` after the explicit RFsim observation guard when TX truth was captured but no D2R packet arrived. The guard is a measurement bound, not a 3GPP timer.

## Future DRL observation interface

The simulator provides one record per Reader only after a window closes. A future fixed policy reads the record and keeps its scheduling action externally defined; this tool does not calculate a reward.

```json
{
  "reader_id": 1,
  "window_index": 1,
  "window_start_ns": 500000,
  "window_end_ns": 1000000,
  "available_at_ns": 1000000,
  "completed_packets": 2,
  "actual_tx_packets": 3,
  "undetected_packets": 1,
  "unaligned_packets": 0,
  "compared_bits": 1000,
  "erroneous_bits": 2,
  "ber": 0.002,
  "packet_loss_rate": 0.3333333333333333,
  "valid": true,
  "invalid_evidence_count": 0
}
```

- Fixed-policy example A: keep the Reader schedule unchanged; consume the record at `available_at_ns` and log BER as `o_err[iota-1, reader_id]`.
- Fixed-policy example B: a valid empty window has `compared_bits = 0` and `ber = null`; the consumer records missing measurement coverage rather than substituting zero.
- Fixed-policy example C: invalid evidence has `valid = false`; the consumer preserves the invalid state. No reward, penalty, model, trainer, or live control behavior is defined here.
