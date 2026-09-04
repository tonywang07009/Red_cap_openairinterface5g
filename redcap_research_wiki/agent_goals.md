# RedCap Research Wiki Agent Goals

Each goal is an execution contract. Run one operation, return the required
envelope, and stop at its stated boundary.

| Goal | Autonomy | Input | Output | Completion evidence | Stop condition |
|---|---|---|---|---|---|
| G0 Governance and inventory | L1 | Active project routes and documentation roots | Classified source/consumer inventory | Each active project has an owning plan and source route | Ownership is ambiguous or cleanup is destructive |
| G1 Wiki baseline | L2 | Research-method PDF and simulator context pack | Source records and method synthesis | PDF page locators and labelled claims | PDF text or interpretation cannot be verified |
| G2 RedCap knowledge compile | L2 | One active project's minimal context pack | Updated concept/system page | Current source paths and visible gaps | Historical material would require bulk ingestion |
| G3 Simulator decision loop | L3 | Question, sources, configuration, markers | Decision/experiment contract | Hypothesis, factors, gates, claim boundary, risks | Evidence cannot support the requested claim |
| G4 Documentation integration | L2 | Confirmed wiki conclusion and target docs | Bilingual documentation proposal | Existing doc-writer checks and path validation | Conclusion remains `review-required` |
| G5 Wiki maintenance | L1 | Wiki root | Index/link/source/lint proposal | Registered validator result | Semantic truth would need automatic judgment |
| G6 Health check | L1 | Wiki root and recent log entries | Contradiction/staleness/orphan report | Each finding has a path and review recommendation | A fix would promote a content conclusion |
| G7 Capture triage | L1-L3 | One completed bounded operation | Classification and optional case draft or decision contract | Sources, evidence paths, reuse path, claim boundary | Evidence or future consumer is missing |

## Operations

Use exactly one operation: `ingest`, `query`, `decide`, `sync-docs`, `lint`, or
`capture-triage`. A `capture-triage` result is one of `none`, `log`,
`update-page`, `case-draft`, or `decision-contract`. A case draft must remain
`draft` or `review-required`; only human review can promote it to `confirmed`.

## Autonomy Levels

| Level | Boundary |
|---|---|
| L0 | Read-only query and navigation |
| L1 | Mechanical proposal and checks; human approval before merge |
| L2 | Source-backed synthesis draft; human approval for conclusions |
| L3 | Research or design proposal; human selects scope and acceptance criteria |
| L4 | Source/protocol changes, long runtime campaigns, or paper-level claims; explicit human approval required |

## Required Result Envelope

```text
status: PASS | PARTIAL | BLOCKED | NEEDS_REVIEW
changed_or_proposed_paths:
evidence_paths:
claim_boundary:
unresolved_items:
next_action:
```
