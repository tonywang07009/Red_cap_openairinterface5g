# The sepcficaion introduction


1. [TS 38.306: UE Radio Access Capability Parameters]
Device Identification & Capability Flags
supportOfRedCap-r17: Indicates the UE is a Rel-17 RedCap device
. It includes functional components like 20 MHz maximum bandwidth in FR1 and separate initial BWPs
.
supportOfERedCap-r18: Indicates the UE is a Rel-18 enhanced RedCap device with reduced peak data rates (10 Mbps) and reduced baseband bandwidth
.
eRedCapNotReducedBB-BW-r18: A flag for eRedCap UEs that do not have reduced baseband bandwidth, allowing them to bypass specific PRB scheduling limits for unicast traffic
.
halfDuplexFDD-TypeA-RedCap-r17: Indicates support for Half-Duplex FDD Type A operation, which is essential for low-cost hardware
.
2. [TS 38.101-1 and TS 38.306: Physical Layer & RF Constraints]
RF & Bandwidth Requirements
Bandwidth (BW): RedCap is limited to 20 MHz in FR1 and 100 MHz in FR2
.
MIMO/Antenna: FR1 RedCap supports 1Rx (mandatory) or 2Rx (optional). It does not support more than 2 DL layers or any UL MIMO (single Tx branch only)
.
PRB Limits (eRedCap): For eRedCap without the NotReducedBB-BW flag, unicast PDSCH/PUSCH is restricted to 25 PRBs (15 kHz SCS) or 12 PRBs (30 kHz SCS)
.
Power Class: RedCap UEs default to Power Class 3 (23 dBm)
.
Reference Sensitivity: REFSENS is modified by ΔR 
1R
​
  for 1Rx RedCap UEs (e.g., a 3 dB relaxation for 10/15/20 MHz FDD bands)
.
3. [TS 38.331: RRC Configuration (SIB1 & Dedicated)]
Network Access & BWP Configuration
redCap-ConfigCommon-r17: Broadcasted in SIB1 to indicate that the cell supports RedCap devices
.
halfDuplexRedCapAllowed-r17: If this field is absent in SIB1, a RedCap UE that supports only half-duplex FDD must treat the cell as barred
.
cellBarredRedCap1Rx/2Rx: Allows the network to selectively bar RedCap UEs based on their antenna configuration (1Rx vs. 2Rx)
.
Initial BWP:
initialDownlinkBWP-RedCap-r17: A dedicated downlink entry lane for RedCap devices
.
initialUplinkBWP-RedCap-r17: A dedicated uplink BWP containing RACH resources for RedCap
.
ncd-SSB-RedCapInitialBWP-SDT-r17: Configuration for Non-Cell Defining SSB used in RedCap-specific BWPs, particularly for Small Data Transmission (SDT)
.
4. [TS 38.321 and TS 38.306: MAC & Protocol Restrictions]
Protocol Operation & Power Saving
DRB Limit: RedCap UEs are mandatory to support a maximum of 8 Data Radio Bearers (DRBs)
.
Sequence Number (SN): Mandatory support for 12-bit SN in PDCP and RLC AM; 18-bit support is optional
.
Early Indication: RedCap UEs provide an "early indication" of their status during the Random Access procedure via specific Msg1, MsgA, or Msg3 resources
.
eDRX: Support for extended DRX cycles (e.g., up to 10485.76 seconds in RRC_IDLE) to significantly enhance battery life for IoT use cases
.

# Work Rhythm & “Labor Law” for the Agent
## Work Rhythm & “Labor Law” for the Agent

- Treat the work session as a sequence of **small tasks**. A “small task” is:
  - implementing or refactoring a single function, **or**
  - adding or fixing a single unit test, **or**
  - running a focused experiment (single simulation or single test suite).

- After **every 3 small tasks that complete successfully**, you must:
  - summarize what was done in 3–5 bullet points,
  - list remaining risks or uncertainties,
  - explicitly start a “break” phase where you:
    - do not change any files,
    - do not run commands,
    - only answer conceptual questions or help the user reflect.

- During the “break” phase, suggest a **35‑minute rest window** for the user and clearly say something like:

    - “This is a 35‑minute break block. I will not propose new code changes until you say we can resume.”
    - You cannot access real wall‑clock time, so you must treat “end of break” as an explicit user signal (e.g., when the user says “break is over” or asks to start the next task).
    - Always favor sustainable progress over maximum throughput. If the user asks for too many changes at once, suggest splitting the work into smaller tasks.