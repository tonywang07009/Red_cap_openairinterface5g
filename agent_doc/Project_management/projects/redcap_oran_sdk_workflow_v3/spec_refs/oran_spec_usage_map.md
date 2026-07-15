# O-RAN Spec Usage Map

## Purpose

- [Goal]: document what each current O-RAN reference is for before SDK implementation starts.
- [Scope]: high-level usage mapping only. This file does not extract full clauses.
- [Accuracy Rule]: every exact clause or procedure claim must be backed by a later targeted extract and marked `[Needs Verification]` until reviewed.

## xApp References

| Reference | Local Path | What It Does | RedCap SDK Use |
|---|---|---|---|
| [RIC Architecture] | `Apps_dev/develop_refer_doc/xapp/O-RAN.WG3.TS.RICARCH-R005-v08.00.docx` | Describes Near-RT RIC architecture and the role of E2-connected applications | Defines where xApp decisions live relative to OAI E2 agents |
| [RIC API] | `Apps_dev/develop_refer_doc/xapp/O-RAN.WG3.TS.RICAPI-R005-v03.00.docx` | Defines RIC-facing API expectations for xApp interaction `[Needs Verification]` | Helps decide what should be exposed as an SDK API versus a local helper |
| [E2SM-KPM] | `Apps_dev/develop_refer_doc/xapp/O-RAN.WG3.TS.E2SM-KPM-R005-v08.00.docx` | Defines KPM measurement subscription and indication behavior `[Needs Verification]` | Observation input only; do not use KPM as a control path |
| [E2SM-RC] | `Apps_dev/develop_refer_doc/xapp/O-RAN.WG3.TS.E2SM-RC-R005-v10.00.docx` | Defines RAN control service model behavior `[Needs Verification]` | Preferred control path for bounded RedCap control requests when supported by OAI/FlexRIC |
| [E2SM-CCC] | `Apps_dev/develop_refer_doc/xapp/O-RAN.WG3.TS.E2SM-CCC-R005-v07.00.docx` | Candidate configuration/control service model reference `[Needs Verification]` | Do not use in SDK v1 until target clauses are extracted |
| [ETSI E2 SM PAS] | `Apps_dev/develop_refer_doc/xapp/ts_104040v040000p.pdf` | Publicly available specification for E2 interface service-model material | Supplemental E2 service-model reference; exact relation to RedCap SDK is `[Needs Verification]` |

## xApp SDK Design Inputs

| Reference | Local Path | What It Does | RedCap SDK Use |
|---|---|---|---|
| [FlexRIC in OAI] | `openair2/E2AP/flexric/` | Existing OAI placement for FlexRIC E2 agent, nearRT-RIC, and xApp support | Runtime dependency for C/C++ xApp SDK work |
| [RedCap xApp SDK wrapper] | `openair2/E2AP/REDCAP_SDK/` | OAI-tracked RedCap wrapper around FlexRIC RC request helpers | Target placement for RedCap-specific xApp SDK code in this checkout |
| [xDevSM] | `Apps_dev/xapp_dev_need/xDevSM/` | Python xApp framework around KPM/RC wrappers and RMR/OSC RIC integration | External design input; not the default OAI runtime path |
| [xDevSM examples] | `Apps_dev/xapp_dev_need/xDevSM-xapps-examples/` | Example xApp package, config, Dockerfile, and deployment layout | Packaging reference for later examples, not a source tree to copy |

## dApp References

| Reference | Local Path | What It Does | RedCap SDK Use |
|---|---|---|---|
| [dApps Architecture and Interfaces] | `Apps_dev/develop_refer_doc/dapp/nGRG-RR-2025-05-dApps Architecture and Interfaces-v2.0.pdf` | Describes dApp architecture and E3-style RAN-local application interfaces `[Needs Verification]` | Primary architecture source for `openair2/E3AP/` channel planning |
| [dApp FlexRIC] | `Apps_dev/dapp_dev_need/dApp-flexric/` | FlexRIC feature baseline with C/C++ and Python xApp support plus custom service models | Helps compare E2/FlexRIC patterns against future E3/dApp needs |
| [E3Controller] | `Apps_dev/dapp_dev_need/E3Controller/` | C++ daemon bridging jbpf shared memory to E3 protocol indications | Candidate RAN-side controller pattern for real-time dApp data exposure |
| [libe3] | `Apps_dev/dapp_dev_need/libe3/` | Vendor-neutral C++ E3AP library for both RAN and dApp roles | Candidate core library pattern for a future OAI E3AP SDK boundary |
| [dApp library] | `Apps_dev/dapp_dev_need/dApp-library/` | Python dApp package, spectrum-sharing example, and E3 Service Model generator | Provides the strongest clue for later `openair2/E3AP/service_models/` layout |
| [dApp OAI fork] | `Apps_dev/dapp_dev_need/dApp-openairinterface5g/` | External OAI-derived reference tree for dApp work | Inspect only for targeted differences; do not merge wholesale |

## rApp References

| Reference | Local Path | What It Does | RedCap SDK Use |
|---|---|---|---|
| [Non-RT RIC Architecture TR] | `Apps_dev/develop_refer_doc/rapp/O-RAN.WG2.Non-RT-RIC-ARCH-TR-v01.01.pdf` | Early Non-RT RIC architecture reference | Background for rApp role separation |
| [Non-RT RIC Architecture TS] | `Apps_dev/develop_refer_doc/rapp/O-RAN.WG2.TS.Non-RT-RIC-ARCH-R004-v07.00.docx` | Technical specification for Non-RT RIC architecture | Defines rApp-side policy and Non-RT RIC boundary `[Needs Verification]` |
| [Use Case Requirements] | `Apps_dev/develop_refer_doc/rapp/O-RAN.WG2.TS.Use-Case-Requirements-R005-v11.00.docx` | O-RAN use-case requirements reference | Use to classify RedCap policy scenarios `[Needs Verification]` |
| [A1 Policy/Configuration] | `Apps_dev/develop_refer_doc/rapp/A1/` | A1AP, A1GAP, A1TD, A1TS, and policy/configuration references | Use for rApp-to-Near-RT RIC policy/API packaging only |
| [O1 Management] | `Apps_dev/develop_refer_doc/rapp/o1/` | O1 interface, alarms, NRM, and PM measurement references | Use for management-plane planning; not a direct RedCap runtime control path |
| [OpenAPI Generator] | `Apps_dev/rapp_dev_need/openapi-generator/` | API client/server/document generator from OpenAPI specs | Candidate generator for rApp SDK packaging after API shape is known |

## Current SDK Rule

- [xApp Target]: `openair2/E2AP/REDCAP_SDK/`, compiled against `openair2/E2AP/flexric/`.
- [dApp Target]: `openair2/E3AP/`.
- [rApp Target]: docs-first only; no `openair2/RAPP`, `openair2/A1AP`, or `openair2/O1` channel is created in this phase.
