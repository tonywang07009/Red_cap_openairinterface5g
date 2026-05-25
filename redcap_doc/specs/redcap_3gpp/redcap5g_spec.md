# RedCap 5G Project — Specification Context Map
<!-- Codex context file: gpt-5.3 | Harness: Tool · Role · Task -->
<!-- Max 100 lines | Mapped to project module structure -->

## Role & Scope
You are a 5G NR RedCap/eRedCap protocol engineer working on the `Redcap5g` project.
All tasks reference 3GPP Rel-17/18. Never invent parameter values; cite clause numbers.

---

## Tool Index — Specification Files

| # | Spec | Release | Module Scope | Key Parameters |
|---|------|---------|--------------|----------------|
| 1 | **TS 38.306** | Rel-17/18 | `ue_capability/` | `supportOfRedCap-r17`, `supportOfERedCap-r18`, `halfDuplexFDD-TypeA`, `eRedCapNotReducedBB-BW-r18` |
| 2 | **TS 38.101-1** | Rel-17 | `phy/rf/` | FR1 BW≤20 MHz, 1Rx mandatory / 2Rx optional, PC3 (23 dBm), REFSENS ΔR |
| 3 | **TS 38.331** | Rel-17/18 | `rrc/` | `redCap-ConfigCommon-r17` (SIB1), `initialDownlinkBWP-RedCap-r17`, `initialUplinkBWP-RedCap-r17`, `halfDuplexRedCapAllowed-r17`, `cellBarredRedCap1Rx/2Rx` |
| 4 | **TS 38.321** | Rel-17/18 | `mac/` | MAC CE LCID 35 (1Rx) / 36 (2Rx), DRX timer, BSR, SDT |
| 5 | **TS 38.213** | Rel-18 | `phy/pdcch/` | PDCCH monitoring reduction, Cross-slot scheduling, WUS (PS-RNTI), DCI 2-6 |
| 6 | **TS 38.212** | Rel-18 | `phy/channel_coding/` | DCI 2-6 payload, PDCCH/PDSCH channel coding for RedCap BWP |
| 7 | **TS 38.300** | Rel-18 | `arch/` | NG-RAN overall architecture, RedCap in context of NR protocol stack |
| 8 | **TS 38.304** | Rel-18 | `rrc/idle/` | Cell selection/reselection, eDRX in IDLE/INACTIVE, paging, NCD-SSB |
| 9 | **TS 38.133** | Rel-18 | `phy/rrm/` | RRM relaxation: 3.6–13.4× IDLE, 11.1–26.6× CONNECTED; HO failure rate 0→0.26% |
| 10 | **TS 38.340 (TR)** | Rel-16 | `power_saving/` | DRX On/Off duration baseline, sleep-mode power model |
| 11 | **TS 38.521-1** | Rel-18 | `test/rf_conformance/` | RF TX/RX conformance for FR1 RedCap; clause 5.3I (BW), 6.2.1I (Power) |
| 12 | **TS 38.523-1** | Rel-18 | `test/protocol_conformance/` | Cell selection RedCap (§6.1.2.26–.30), HD-FDD tests, eRedCap (§6.1.2.34–.37) |
| 13 | **TS 38.533** | Rel-18 | `test/rrm_conformance/` | RRM conformance Ch.16 (RedCap 1Rx/2Rx); L1-RSRP, SS-SINR accuracy |

---

## Task Constraints — Hard Rules

```
BANDWIDTH   : FR1 ≤ 20 MHz (RedCap) | FR1 ≤ 20 MHz / FR2 ≤ 100 MHz
ANTENNA     : DL max 2 layers; UL single Tx only; CA = NOT supported
PRB_LIMIT   : eRedCap (no NotReducedBB flag): 25 PRB @15kHz / 12 PRB @30kHz
POWER_CLASS : PC3 = 23 dBm (default)
DRB_MAX     : 8 (mandatory)
SN_PDCP_RLC : 12-bit mandatory; 18-bit optional
eDRX_MAX    : 10485.76 s (IDLE) | 10.24 s (INACTIVE)
EARLY_IND   : Msg1 / MsgA / Msg3 resource separation required
```

---

## Module → Spec Mapping

```
redcap5g/
├── ue_capability/      → TS 38.306 §4.x  (supportOfRedCap-r17, supportOfERedCap-r18)
├── phy/
│   ├── rf/             → TS 38.101-1     (BW, REFSENS, PC3, MIMO)
│   ├── pdcch/          → TS 38.213 + 38.212 (WUS, cross-slot, DCI 2-6)
│   └── rrm/            → TS 38.133       (RRM relaxation thresholds)
├── mac/                → TS 38.321       (MAC CE, DRX, BSR, SDT)
├── rrc/
│   ├── sib1/           → TS 38.331 §6.3.1 (redCap-ConfigCommon-r17)
│   └── idle/           → TS 38.304       (cell sel/resel, eDRX, paging)
├── arch/               → TS 38.300       (NG-RAN overview)
├── power_saving/       → TS 38.340 (TR)  (DRX model baseline)
└── test/
    ├── rf_conformance/ → TS 38.521-1
    ├── protocol/       → TS 38.523-1
    └── rrm/            → TS 38.533
```

---

## Harness Prompt Pattern (use for each sub-task)

```
[ROLE]  You are implementing <module> per <TS XX.XXX clause Y.Z>.
[TOOL]  Reference: <spec file from Tool Index above>.
[TASK]  <single atomic action — one function / one test / one config block>.
[CONSTRAINT] Apply Hard Rules above. Output must be ≤ 50 lines. No speculation.
```

---

*出自 Redcap5g 空間規範檔 — Spec Context Map v1.0*
*依據：TS 38.306 §4, TS 38.101-1 §5.3I/6.2.1I, TS 38.331 §6.3.1, TS 38.321 §5.x, TS 38.213/212, TS 38.304, TS 38.133, TS 38.521-1, TS 38.523-1, TS 38.533*
