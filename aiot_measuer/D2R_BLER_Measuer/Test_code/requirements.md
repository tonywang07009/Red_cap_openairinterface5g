# D2R BER Measurement Tool Requirements

## Formula concept

- A Tag payload bit uses one Manchester/OOK pair at `SFS = 1`: `0 -> 10` and `1 -> 01`.
- The ideal-isolation received baseband model is `y_k = rho_k h_GT h_TR s_k + n_k`.
- `rho_k` is `1` for an ON chip and `0` for an OFF chip. The direct illuminating-CW to Reader path is excluded by the accepted ideal beam-isolation assumption.
- Each Rician leg has unit mean power and `K = 3 dB`. The two legs are independently drawn and their product is the backscatter channel.
- BER is `erroneous_payload_bits / compared_payload_bits`. Comparable CRC failures remain in the numerator and denominator.
- A complete packet is assigned to the 0.5 ms window containing its decode completion. An empty window has `ber = null`; missing comparison evidence invalidates the affected result.
- The independent numerical/theoretical BER reference, detector tie rule, payload framing, phase convention, and RFsim sample-tick conversion remain pending. This tool does not claim a reference match before those decisions are verified.

## Parameters

| Parameter | Meaning | Status |
|---|---|---|
| `reader_ids` | Three Reader identifiers | Confirmed: `1, 2, 3` |
| `tag_count` | Tags present in the scenario | Confirmed: at most `100` |
| `visibility_seed` | Reproducible four-state assignment seed | Confirmed |
| `sample_rate_hz` | Explicit conversion input for RFsim sample ticks | Required; not inferred from a YAML file |
| `observation_window_ns` | BER observation-window width | Confirmed: `500000` ns |
| `duration_results` | Measured D2R duration/BER points for the plot | Filled only by verified measurement evidence |
| `ideal_cross_reader_isolation` | Ignore other Readers' reflection as interference | Confirmed idealization |
| `ideal_acquisition_alignment` | Packet detection and alignment are available | Confirmed idealization; decoding can still fail |

## Acceptance

- Run the UI through Bash:

```bash
./run_ui.sh init --output result.json --sample-rate-hz <verified-rate>
./run_ui.sh show --input result.json
./run_ui.sh plot --input result.json --output ber-by-duration.png
```

- JSON preserves `null` BER and invalid-evidence reasons.
- The plot uses D2R bit duration on x-axis and BER on y-axis.
- The tool does not generate synthetic BER values or a DRL reward/model.
