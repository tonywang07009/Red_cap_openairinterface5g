# Control gates

Gate meanings:

| Gate | What it proves | What it does not prove |
| --- | --- | --- |
| Runtime smoke | Python, PyTorch, Gymnasium, SB3 and shared Python library load | RIC or E2 works |
| RIC name resolution | The bridge can resolve the compose-derived RIC service | E2 Setup succeeded |
| Discovery | A live node advertises KPM and RC RAN functions | Required report/control styles work |
| Qualification | Fresh cell and UE KPM streams align and create a verified target binding | A control was accepted |
| ACK | FlexRIC returned a request acknowledgement | gNB applied the requested cap |
| Apply marker | The resolved gNB emitted the contract marker | The later observation changed as expected |
| Later KPM | A later observation exists after the candidate | The research reward or training method is valid |

Gate control sequence:

```text
qualify KPM and target binding
→ acquire node lease
→ baseline ACK + apply marker
→ one candidate ACK + apply marker + later KPM
→ baseline restore ACK + apply marker
→ release lease
```

Gate contention is a software lease, not Wi-Fi channel contention. A second
workspace receives `TARGET_BUSY`. It must qualify again after the first holder
finishes; it cannot reuse old observations.

Gate discovery and qualification are different: discovery lists live
capabilities; qualification proves the selected profile is usable now.
