# Evidence package

Gate interpretation: the package is both an experiment access record and a
flight recorder. It answers who controlled which resolved node, with which
runtime/profile, what each gate proved, and whether baseline recovery was
confirmed.

| File | Purpose |
| --- | --- |
| `manifest.json` | Release, profile, resolved target, gate results and safe next command |
| `events.ndjson` | Ordered gate and transaction events |
| `kpm_evidence.json` | Minimal decoded cell/UE capability or qualified observation summaries |
| `control_journal.json` | Durable baseline/candidate/restore state and recovery authority |
| `gnb_apply_excerpt.log` | Short excerpt containing the compose-resolved gNB apply marker |

Gate claim boundary:

- Empty or absent evidence means unproved, not failed-by-assumption.
- ACK without a gNB apply marker is not applied control.
- Apply marker without a later KPM frame is not an observed outcome.
- One bounded decision is not a completed DQN/PPO/DDPG training experiment.
- `down` and `remove` retain evidence; no automatic purge is allowed.
