3GPP TS 38.523-1 version 18.3.0 Release 18 1569 ETSI TS 138 523-1 V18.3.0 (2025-05)
- System information combination NR-28 as defined in TS 38.508-1 [4] clause 4.4.3.1.2 is used.
UE:
- The UE is in Automatic PLMN selection mode.
- The pre-configured UE location is defined in TS 38.508-1 [4] Clause 4.5C.
Preamble
- The UE is in state Switched OFF (state 0N-B) as defined in TS 38.508-1 [4], subclause 4.4A on NR Cell 1.
7.1.1.10.4.3.2 Test procedure sequence
Table 7.1.1.10.4.3.2-1: Main behaviour
St Procedure Message Sequence TP Verdict
U - S Message
1 Power on the UE. - - - -
2 The UE transmits preamble on PRACH. --> PRACH Preamble - -
3 The SS transmits Random Access Response <-- Random Access Response - -
with RAPID corresponding to the transmitted
preamble in step 2.
4 Check: Does the UE transmit an --> MAC PDU (Timing Advance 1 P
RRCSetupRequest message with Timing Report MAC CE,
Advance Report MAC CE included? RRCSetupRequest)
5- Steps 3 to 20a1 of the registration procedure - - - -
22 described in TS 38.508-1 [4] subclause
4.5.2.2-2 are performed.
23 The UE is switched off by executing generic - - - -
procedure in Table 4.9.6.1-1 in TS 38.508-1
[4].
24 SS broadcasts SIB19 with ta-Report-r17 not <-- RRC: SIB19 - -
present.
25 Power on the UE. - - - -
26 The UE transmits preamble on PRACH. --> PRACH Preamble - -
27 The SS transmits Random Access Response <-- Random Access Response - -
with RAPID corresponding to the transmitted
preamble in step 26.
28 The UE transmits an RRCSetupRequest --> MAC PDU (RRCSetupRequest) - -
message with no Timing Advance Report MAC
CE included.
29 The SS transmits an RRCSetup message <-- MAC PDU(RRCSetup) - -
configuring offsetThresholdTA.
30 Check: Does the UE transmit an --> MAC PDU (Timing Advance 2 P
RRCSetupComplete message with Timing Report MAC CE,
Advance Report MAC CE included? RRCSetupComplete)
31- Steps 5 to 19a1 of the registration procedure - - - -
45 described in TS 38.508-1 [4] subclause
4.5.2.2-2 are performed.
46 The SS transmits a MAC PDU containing a <-- MAC PDU (Differential Koffset - -
Differential Koffset MAC CE with differential CE)
Koffset set to 20 ms.
47 The SS transmits a UECapabilityEnquiry <-- UECapabilityEnquiry - -
message
48 Check: Does the UE transmit a --> UECapabilityInformation 3 P
UECapabilityInformation message after
applying differential Koffset of 20ms received
at step 46?
Note: Successful reception of this message at
SS confirms that differential Koffset is applied
at UE.
ETSI

3GPP TS 38.523-1 version 18.3.0 Release 18  1570  ETSI TS 138 523-1 V18.3.0 (2025-05)
| 7.1.1.10.4.3.3  | Specific message contents  |     |     |     |
| --------------- | -------------------------- | --- | --- | --- |
Table 7.1.1.10.4.3.3-1: SIB19 (Preamble and all steps)
Derivation Path: TS 38.508-1 [4], Table 4.6.2-18C
|                           | Information Element  | Value/remark     | Comment           | Condition  |
| ------------------------- | -------------------- | ---------------- | ----------------- | ---------- |
| SIB19-r17 ::= SEQUENCE {  |                      |                  |                   |            |
|   ntn-Config-r17          |                      | NTN-Config with  | Table             | GSO        |
|                           |                      | condition GSO    | 7.1.1.10.4.3.3-2  |            |
|                           |                      | NTN-Config with  | Table             | NGSO       |
|                           |                      | condition NGSO   | 7.1.1.10.4.3.3-2  |            |
| }                         |                      |                  |                   |            |

Table 7.1.1.10.4.3.3-2: NTN-Config (Table 7.1.1.10.4.3.3-1)
Derivation Path: TS 38.508-1 [4], Table 4.6.3-84C
|                                | Information Element  | Value/remark  | Comment  | Condition  |
| ------------------------------ | -------------------- | ------------- | -------- | ---------- |
| NTN-Config-r17 ::= SEQUENCE {  |                      |               |          |            |
|   ta-Report-r17                |                      | enabled       |          | Preamble   |
|                                |                      | Not present   |          | Step 24    |
| }                              |                      |               |          |            |

Table 7.1.1.10.4.3.3-3: RRCSetup (Step 29, Table 7.1.1.10.4.3.2-1)
Derivation Path: TS 38.508-1 [4], Table 4.6.1-21
|                                | Information Element  | Value/remark          | Comment           | Condition  |
| ------------------------------ | -------------------- | --------------------- | ----------------- | ---------- |
| RRCSetup ::= SEQUENCE {        |                      |                       |                   |            |
|   criticalExtensions CHOICE {  |                      |                       |                   |            |
|     rrcSetup SEQUENCE {        |                      |                       |                   |            |
|       masterCellGroup          |                      | CellGroupConfig with  | Table             |            |
|                                |                      | condition SRB1        | 7.1.1.10.4.3.3-4  |            |
|     }                          |                      |                       |                   |            |
|   }                            |                      |                       |                   |            |
| }                              |                      |                       |                   |            |

Table 7.1.1.10.4.3.3-4: CellGroupConfig (Table 7.1.1.10.4.3.3-3)
Derivation Path: TS 38.508-1 [4], Table 4.6.3-19
|                                 | Information Element  | Value/remark         | Comment  | Condition  |
| ------------------------------- | -------------------- | -------------------- | -------- | ---------- |
| CellGroupConfig ::= SEQUENCE {  |                      |                      |          |            |
|   mac-CellGroupConfig           |                      | MAC-CellGroupConfig  |          |            |
| }                               |                      |                      |          |            |

|     | Table 7.1.1.10.4.3.3-5: MAC-CellGroupConfig (Table 7.1.1.10.4.3.3-4) |     |     |     |
| --- | -------------------------------------------------------------------- | --- | --- | --- |
Derivation Path: TS 38.508-1 [4], Table 4.6.3-68
|                                     | Information Element  | Value/remark  | Comment  | Condition  |
| ----------------------------------- | -------------------- | ------------- | -------- | ---------- |
| MAC-CellGroupConfig ::= SEQUENCE {  |                      |               |          |            |
|   TAR-Config-r17 ::= SEQUENCE {     |                      |               |          |            |
|     offsetThresholdTA-r17           |                      | ms15          |          |            |
|     timingAdvanceSR-r17             |                      | enabled       |          |            |
| }                                   |                      |               |          |            |

ETSI

3GPP TS 38.523-1 version 18.3.0 Release 18 1571 ETSI TS 138 523-1 V18.3.0 (2025-05)
7.1.1.11 NR Dual Connectivity
7.1.1.11.1 DC power headroom reporting / PSCell activation and DL pathloss change
reporting
7.1.1.11.1.1 Test Purpose (TP)
(1)
with { UE in RRC_CONNECTED state on Pcell and PSCell is added }
ensure that {
when { phr is configured }
then { UE transmits a Power Headroom Report for the PCell and PSCell }
}
(2)
with { UE in RRC_CONNECTED state with PSCell and with Power headroom reporting for phr-Tx-
PowerFactorChange }
ensure that {
when { the DL Pathloss has changed more than phr-Tx-PowerFactorChange dB and phr-ProhibitTimer is
running }
then { UE does not transmit a MAC PDU containing Power Headroom MAC Control Element }
}
(3)
with { UE in RRC_CONNECTED state with PSCell and with Power headroom reporting for phr-Tx-
PowerFactorChange }
ensure that {
when { the phr-ProhibitTimer expires and power headroom report is triggered due to DL Pathloss
change }
then { UE transmits a MAC PDU containing Power Headroom MAC Control Element for the Pcell and
PSCell }
}
7.1.1.11.1.2 Conformance requirements
References: The conformance requirements covered in the present TC are specified in: 3GPP TS 38.321 clause 5.4.6.
Unless otherwise stated these are Rel-15 requirements.
[TS 38.321, clause 5.4.6]
A Power Headroom Report (PHR) shall be triggered if any of the following events occur:
- phr-ProhibitTimer expires or has expired and the path loss has changed more than phr-Tx-PowerFactorChange
dB for at least one activated Serving Cell of any MAC entity which is used as a pathloss reference since the last
transmission of a PHR in this MAC entity when the MAC entity has UL resources for new transmission;
NOTE 1: The path loss variation for one cell assessed above is between the pathloss measured at present time on
the current pathloss reference and the pathloss measured at the transmission time of the last transmission
of PHR on the pathloss reference in use at that time, irrespective of whether the pathloss reference has
changed in between.
- phr-PeriodicTimer expires;
- upon configuration or reconfiguration of the power headroom reporting functionality by upper layers, which is
not used to disable the function;
- activation of an SCell of any MAC entity with configured uplink;
- addition of the PSCell (i.e. PSCell is newly added or changed);
- phr-ProhibitTimer expires or has expired, when the MAC entity has UL resources for new transmission, and the
following is true for any of the activated Serving Cells of any MAC entity with configured uplink:
ETSI

3GPP TS 38.523-1 version 18.3.0 Release 18 1572 ETSI TS 138 523-1 V18.3.0 (2025-05)
- there are UL resources allocated for transmission or there is a PUCCH transmission on this cell, and the
required power backoff due to power management (as allowed by P-MPR as specified in TS 38.101-1 [14],
c
TS 38.101-2 [15], and TS 38.101-3 [16]) for this cell has changed more than phr-Tx-PowerFactorChange dB
since the last transmission of a PHR when the MAC entity had UL resources allocated for transmission or
PUCCH transmission on this cell.
NOTE 2: The MAC entity should avoid triggering a PHR when the required power backoff due to power
management decreases only temporarily (e.g. for up to a few tens of milliseconds) and it should avoid
reflecting such temporary decrease in the values of P /PH when a PHR is triggered by other
CMAX,f,c
triggering conditions.
If the MAC entity has UL resources allocated for a new transmission the MAC entity shall:
1> if it is the first UL resource allocated for a new transmission since the last MAC reset:
2> start phr-PeriodicTimer;
1> if the Power Headroom reporting procedure determines that at least one PHR has been triggered and not
cancelled; and
1> if the allocated UL resources can accommodate the MAC CE for PHR which the MAC entity is configured to
transmit, plus its subheader, as a result of LCP as defined in clause 5.4.3.1:
2> if multiplePHR with value true is configured:
3> for each activated Serving Cell with configured uplink associated with any MAC entity:
4> obtain the value of the Type 1 or Type 3 power headroom for the corresponding uplink carrier as
specified in clause 7.7 of TS 38.213 [6] for NR Serving Cell and clause 5.1.1.2 of TS 36.213 [17] for
E-UTRA Serving Cell;
4> if this MAC entity has UL resources allocated for transmission on this Serving Cell; or
4> if the other MAC entity, if configured, has UL resources allocated for transmission on this Serving
Cell and phr-ModeOtherCG is set to real by upper layers:
5> obtain the value for the corresponding P field from the physical layer.
CMAX,f,c
3> if phr-Type2OtherCell with value true is configured:
4> if the other MAC entity is E-UTRA MAC entity:
5> obtain the value of the Type 2 power headroom for the SpCell of the other MAC entity (i.e. E-
UTRA MAC entity);
5> if phr-ModeOtherCG is set to real by upper layers:
6> obtain the value for the corresponding P field for the SpCell of the other MAC entity
CMAX,f,c
(i.e. E-UTRA MAC entity) from the physical layer.
3> instruct the Multiplexing and Assembly procedure to generate and transmit the Multiple Entry PHR MAC
CE as defined in clause 6.1.3.9 based on the values reported by the physical layer.
2> else (i.e. Single Entry PHR format is used):
3> obtain the value of the Type 1 power headroom from the physical layer for the corresponding uplink
carrier of the PCell;
3> obtain the value for the corresponding P field from the physical layer;
CMAX,f,c
3> instruct the Multiplexing and Assembly procedure to generate and transmit the Single Entry PHR MAC
CE as defined in clause 6.1.3.8 based on the values reported by the physical layer.
2> start or restart phr-PeriodicTimer;
2> start or restart phr-ProhibitTimer;
ETSI

3GPP TS 38.523-1 version 18.3.0 Release 18  1573  ETSI TS 138 523-1 V18.3.0 (2025-05)
2> cancel all triggered PHR(s).
| 7.1.1.11.1.3    |     | Test description     |     |     |     |     |     |     |
| --------------- | --- | -------------------- | --- | --- | --- | --- | --- | --- |
| 7.1.1.11.1.3.1  |     | Pre-test conditions  |     |     |     |     |     |     |
System Simulator:
-  NR Cell 1 is the PCell and NR Cell 10 is the PSCell.
-  System information combination NR-4 as defined in TS 38.508-1 [4] clause 4.4.3.1.3 is used in all cells.
UE:
-  None.
Preamble:
-  The UE is in state NR RRC_CONNECTED using generic procedure parameter Connectivity (NR-DC), Test
Mode (On) associated with UE test loop mode A configured on NR Cell 1 according to TS 38.508-1 [4], clause
4.5.4.
| 7.1.1.11.1.3.2  |     | Test procedure sequence  |     |     |     |     |     |     |
| --------------- | --- | ------------------------ | --- | --- | --- | --- | --- | --- |
Table 7.1.1.11.1.3.2-0: Cell configuration power level changes over time for Conducted test
environment
|     |     | Parameter  | Unit   | NR Cell 1  | NR Cell 10  |     | Remarks  |     |
| --- | --- | ---------- | ------ | ---------- | ----------- | --- | -------- | --- |
|     | T0  | SS/PBCH    | dBm/SC | -82        | -82         |     |          |     |
|     |     | SSS EPRE   | S      |            |             |     |          |     |
|     | T1  | SS/PBCH    | dBm/SC | -89        | -82         |     |          |     |
|     |     | SSS EPRE   | S      |            |             |     |          |     |
|     | T2  | SS/PBCH    | dBm/SC | -82        | -82         |     |          |     |
|     |     | SSS EPRE   | S      |            |             |     |          |     |
|     | T3  | SS/PBCH    | dBm/SC | -82        | -89         |     |          |     |
|     |     | SSS EPRE   | S      |            |             |     |          |     |
|     | T4  | SS/PBCH    | dBm/SC | -82        | -82         |     |          |     |
|     |     | SSS EPRE   | S      |            |             |     |          |     |

Table 7.1.1.11.1.3.2-0A: Cell configuration power level changes over time for OTA test environment
|     |     | Parameter  | Unit   | NR Cell 1  | NR Cell 10  |     | Remarks  |     |
| --- | --- | ---------- | ------ | ---------- | ----------- | --- | -------- | --- |
|     | T0  | SS/PBCH    | dBm/SC | -82        | -82         |     |          |     |
|     |     | SSS EPRE   | S      |            |             |     |          |     |
|     | T1  | SS/PBCH    | dBm/SC | n/a        | n/a         |     |          |     |
|     |     | SSS EPRE   | S      |            |             |     |          |     |
|     | T2  | SS/PBCH    | dBm/SC | n/a        | n/a         |     |          |     |
|     |     | SSS EPRE   | S      |            |             |     |          |     |
|     | T3  | SS/PBCH    | dBm/SC | -82        | -91         |     |          |     |
|     |     | SSS EPRE   | S      |            |             |     |          |     |
|     | T4  | SS/PBCH    | dBm/SC | -82        | -82         |     |          |     |
|     |     | SSS EPRE   | S      |            |             |     |          |     |

Table 7.1.1.11.1.3.2-1: Main behaviour
| St                                         |     | Procedure  |     |        | Message Sequence  |          |     | TP  Verdict  |
| ------------------------------------------ | --- | ---------- | --- | ------ | ----------------- | -------- | --- | ------------ |
|                                            |     |            |     | U - S  |                   | Message  |     |              |
| 1  The SS transmits UL grant on PCell and  |     |            |     | <--    | -                 |          |     | -  -         |
PSCell to the UE at every 10ms in PDCCH
occasion.
ETSI

3GPP TS 38.523-1 version 18.3.0 Release 18 1574 ETSI TS 138 523-1 V18.3.0 (2025-05)
2 SS transmits NR RRCReconfiguration <-- (RRCReconfiguration) - -
message to configure to specific Power
Headroom parameters for NR Cell.
3 Check: Does the UE transmit a MAC PDU --> MAC PDU 1 P
containing Multiple-Entry PHR MAC CE on
PCell?
(Note 1)
3A Check: Does the UE transmit a MAC PDU --> MAC PDU 1 P
containing Multiple-Entry PHR MAC CE on
PSCell?
(Note 1)
4 The UE transmits an NR --> (RRCReconfigurationComplete) - -
RRCReconfigurationComplete message
including nr-SCG-Response. (Note 1)
5 Void - - - -
- EXCEPTION: Steps 6 to 12 shall be executed - - - -
depending on PSCell Configuration.
(Note 3)
6 IF PSCell is configured as FR1 THEN Reduce - - - -
SS power level for NR PCell so as to cause a
DL_Pathloss change at UE by 5dB, row T1 of
Table 7.1.1.11.1.3.2-0.
7 Check: For 80% of prohibitPHR-Timer since --> MAC PDU 2 F
step 3, does the UE transmit a MAC PDU
containing Multiple-Entry PHR MAC CE on
PCell?
8 Check: After prohibitPHR-Timer after step 3, --> MAC PDU 3 P
does the UE transmit a MAC PDU containing
Multiple-Entry PHR MAC CE on PCell?
9 Increase SS power level for NR PCell so as to - - - -
cause a DL_Pathloss change at UE by 5dB,
row T2 of Table 7.1.1.11.1.3.2-0.
10 Check: For 80% of prohibitPHR-Timer since --> MAC PDU 2 F
step 8, does the UE transmit a MAC PDU
containing Power Headroom MAC Control
Element on PCell?
11 Check: After prohibitPHR-Timer after step 8, --> MAC PDU 3 P
does the UE transmit a MAC PDU containing
Power Headroom MAC Control Element on
PCell?
12 Void - - - -
13 Reduce SS power level for NR PSCell so as to - - - -
cause a DL_Pathloss change at UE by 5dB,
row T3 of Table 7.1.1.11.1.3.2-0/0A.
14 IF PSCell is configured as FR2 THEN Check: --> MAC PDU 2 F
For 80% of prohibitPHR-Timer since step 3A,
does the UE transmit a MAC PDU containing
Multiple-Entry PHR MAC CE?
15 Check: Does the UE transmit a MAC PDU --> MAC PDU 3 P
containing Multiple-Entry PHR MAC CE on
PSCell?
16 Increase SS power level for NR PSCell so as - - - -
to cause a DL_Pathloss change at UE by 5dB,
row T4 of Table 7.1.1.11.1.3.2-0/0A.
17 Check: For 80% of prohibitPHR-Timer since --> MAC PDU 2 F
step 15, does the UE transmit a MAC PDU
containing Power Headroom MAC Control
Element on PSCell?
18 Check: After prohibitPHR-Timer after step 15, --> MAC PDU 3 P
does the UE transmit a MAC PDU containing
Power Headroom MAC Control Element on
PSCell?
19 The SS transmits an NR RRCReconfiguration <-- (RRCReconfiguration) - -
message to disable Power Headroom
reporting.
ETSI

3GPP TS 38.523-1 version 18.3.0 Release 18  1575  ETSI TS 138 523-1 V18.3.0 (2025-05)
20  The UE transmits an NR  -->  (RRCReconfigurationComplete)  -  -
RRCReconfigurationComplete message to
confirm the disabling of Power Headroom
parameters.
| Note 1:  Steps 3 and 4 can happen in any order.  |     |     |     |     |
| ------------------------------------------------ | --- | --- | --- | --- |
| Note 2:  Void.                                   |     |     |     |     |
Note 3:  Steps 6 to 12 are excluded when executed with FR1+FR2 band combination due to limitation in FR1 OTA
requirements specified in 38.508-1 [4] clause 6.2.2.2.3. phr-Tx-PowerFactorChange for PCell is not tested
due to this limitation

| 7.1.1.11.1.3.3  | Specific Message Contents  |     |     |     |
| --------------- | -------------------------- | --- | --- | --- |
Table 7.1.1.11.1.3.3-1: RRCReconfiguration (step 2, Table 7.1.1.11.1.3.2-1)
Derivation Path: TS 38.508-1 [4], Table 4.6.1-13
|                                        | Information Element  | Value/remark         | Comment  | Condition  |
| -------------------------------------- | -------------------- | -------------------- | -------- | ---------- |
| RRCReconfiguration ::= SEQUENCE {      |                      |                      |          |            |
|   criticalExtensions CHOICE {          |                      |                      |          |            |
|     rrcReconfiguration SEQUENCE {      |                      |                      |          |            |
|       radioBearerConfig                |                      | Not present          |          |            |
|       nonCriticalExtension SEQUENCE {  |                      |                      |          |            |
|         masterCellGroup                |                      | CellGroupConfig-phr  | Table    |            |
7.1.1.11.1.3.3-2
|           nonCriticalExtension SEQUENCE {           |     |              |     |     |
| --------------------------------------------------- | --- | ------------ | --- | --- |
|           nonCriticalExtension SEQUENCE {           |     |              |     |     |
|             mrdc-SecondaryCellGroupConfig CHOICE {  |     |              |     |     |
|               setup SEQUENCE {                      |     |              |     |     |
|                 mrdc-ReleaseAndAdd                  |     | Not present  |     |     |
|                 mrdc-SecondaryCellGroup CHOICE {    |     |              |     |     |
                  nr-SCG  RRCReconfiguration- OCTET STRING
|     |     | SCG-phr  | (CONTAINING  |     |
| --- | --- | -------- | ------------ | --- |
RRCReconfigurati
on)
|                 }  |     |     |     |     |
| ------------------ | --- | --- | --- | --- |
|               }    |     |     |     |     |
|             }      |     |     |     |     |
|           }        |     |     |     |     |
|         }          |     |     |     |     |
|       }            |     |     |     |     |
|     }              |     |     |     |     |
|   }                |     |     |     |     |
| }                  |     |     |     |     |

Table 7.1.1.11.1.3.3-1A: RRCReconfiguration-SCG-phr (Table 7.1.1.11.1.3.3-1)
Derivation Path: TS 38. 508-1 [4], Table 4.6.1-13
|                                    | Information Element  | Value/remark         | Comment  | Condition  |
| ---------------------------------- | -------------------- | -------------------- | -------- | ---------- |
| RRCReconfiguration ::= SEQUENCE {  |                      |                      |          |            |
|   criticalExtensions CHOICE {      |                      |                      |          |            |
|     rrcReconfiguration SEQUENCE {  |                      |                      |          |            |
|       radioBearerConfig            |                      | Not present          |          |            |
|       secondaryCellGroup           |                      | CellGroupConfig-phr  | Table    |            |
7.1.1.11.1.3.3-2
|     }  |     |     |     |     |
| ------ | --- | --- | --- | --- |
|   }    |     |     |     |     |
| }      |     |     |     |     |

Table 7.1.1.11.1.3.3-2: CellGroupConfig-phr (Tables 7.1.1.11.1.3.3-1 and 7.1.1.11.1.3. 3-1 A)
Derivation Path: TS 38.508-1 [4], Table 4.6.3-19
|     | Information Element  | Value/remark  | Comment  | Condition  |
| --- | -------------------- | ------------- | -------- | ---------- |
ETSI

3GPP TS 38.523-1 version 18.3.0 Release 18  1576  ETSI TS 138 523-1 V18.3.0 (2025-05)
| CellGroupConfig ::= SEQUENCE {    |           |     |     |
| --------------------------------- | --------- | --- | --- |
|   mac-CellGroupConfig SEQUENCE {  |           |     |     |
|     phr-Config CHOICE {           |           |     |     |
|       setup SEQUENCE {            |           |     |     |
|         phr-PeriodicTimer         | infinity  |     |     |
|         phr-ProhibitTimer         | sf500     |     |     |
|         phr-Tx-PowerFactorChange  | dB3       |     |     |
|         multiplePHR               | true      |     |     |
|         dummy                     | false     |     |     |
|         phr-Type2OtherCell        | false     |     |     |
|         phr-ModeOtherCG           | real      |     |     |
|       }                           |           |     |     |
|     }                             |           |     |     |
|   }                               |           |     |     |
| }                                 |           |     |     |

7.1.1.12  UE power saving
7.1.1.12.1  Void
7.1.1.12.2  Void
7.1.1.12.3  DRX adaptation / UE wakeup indication
7.1.1.12.3.1  Test Purpose (TP)
(1)
with { UE in RRC_CONNECTED state and long DRX is configured and [(SFN * 10) + subframe number]
modulo (drx-LongCycle) = drx-StartOffset and DCP is configured }
ensure that {
  when { a DCP indication with the value of wake-up indication 1 associated with the current DRX
cycle has been received }
    then { UE starts the drx-onDurationTimer after drx-SlotOffset from the beginning of the subframe
and monitors the PDCCH }
            }

(2)
with { UE in RRC_CONNECTED state and long DRX is configured and [(SFN * 10) + subframe number]
modulo (drx-LongCycle) = drx-StartOffset and DCP is configured and ps-wakeup is configured with
value true }
ensure that {
  when { DCP indication associated with this cycle has not been received }
    then { UE starts the drx-onDurationTimer after drx-SlotOffset from the beginning of the subframe
and monitors the PDCCH for OnDurationTimer PDCCH-Occasions }
            }

(3)
with { UE in RRC_CONNECTED state long DRX is configured and [(SFN * 10) + subframe number] modulo
(drx-LongCycle) = drx-StartOffset and DCP is configured }
ensure that {
  when { all DCP occasions in time domain occurred in DRX active time }
    then { UE does not monitor PDCCH for the detection of DCI format 2_6 and start the drx-
onDurationTimer after drx-SlotOffset from the beginning of the subframe and monitors the PDCCH }
            }

(4)
with { UE in RRC_CONNECTED state long DRX is configured and DCP is configured }
ensure that {
  when { all DCP occasions in time domain occurred during measurement gap }
    then { UE does not monitor PDCCH for the detection of DCI format 2_6 and start the drx-
onDurationTimer after drx-SlotOffset from the beginning of the subframe and monitors the PDCCH }
ETSI

3GPP TS 38.523-1 version 18.3.0 Release 18 1577 ETSI TS 138 523-1 V18.3.0 (2025-05)
}
(5)
with { UE in RRC_CONNECTED state and long DRX is configured and [(SFN * 10) + subframe number]
modulo (drx-LongCycle) = drx-StartOffset and DCP is configured }
ensure that {
when { a DCP indication with the value of wake-up indication 0 associated with the current DRX
cycle has been received }
then { UE does not start the drx-onDurationTimer after drx-SlotOffset from the beginning of the
subframe and skips monitoring the PDCCH }
}
7.1.1.12.3.2 Conformance requirements
References: The conformance requirements covered in the present TC are specified in: TS 38.321, clause 5.7, TS
38.213, clause 10.3 and 7.3.1.3.7. Unless otherwise stated these are Rel-16 requirements.
[TS 38.321, clause 5.7]
The MAC entity may be configured by RRC with a DRX functionality that controls the UE's PDCCH monitoring
activity for the MAC entity's C-RNTI, CI-RNTI, CS-RNTI, INT-RNTI, SFI-RNTI, SP-CSI-RNTI, TPC-PUCCH-RNTI,
TPC-PUSCH-RNTI, TPC-SRS-RNTI, and AI-RNTI. When using DRX operation, the MAC entity shall also monitor
PDCCH according to requirements found in other clauses of this specification. When in RRC_CONNECTED, if DRX
is configured, for all the activated Serving Cells, the MAC entity may monitor the PDCCH discontinuously using the
DRX operation specified in this clause; otherwise the MAC entity shall monitor the PDCCH as specified in TS 38.213
[6].
NOTE 1: If Sidelink resource allocation mode 1 is configured by RRC, a DRX functionality is not configured.
RRC controls DRX operation by configuring the following parameters:
- drx-onDurationTimer: the duration at the beginning of a DRX Cycle;
- drx-SlotOffset: the delay before starting the drx-onDurationTimer;
- drx-InactivityTimer: the duration after the PDCCH occasion in which a PDCCH indicates a new UL or DL
transmission for the MAC entity;
- drx-RetransmissionTimerDL (per DL HARQ process except for the broadcast process): the maximum duration
until a DL retransmission is received;
- drx-RetransmissionTimerUL (per UL HARQ process): the maximum duration until a grant for UL
retransmission is received;
- drx-LongCycleStartOffset: the Long DRX cycle and drx-StartOffset which defines the subframe where the Long
and Short DRX Cycle starts;
- drx-ShortCycle (optional): the Short DRX cycle;
- drx-ShortCycleTimer (optional): the duration the UE shall follow the Short DRX cycle;
- drx-HARQ-RTT-TimerDL (per DL HARQ process except for the broadcast process): the minimum duration
before a DL assignment for HARQ retransmission is expected by the MAC entity;
- drx-HARQ-RTT-TimerUL (per UL HARQ process): the minimum duration before a UL HARQ retransmission
grant is expected by the MAC entity;
- ps-Wakeup (optional): the configuration to start associated drx-onDurationTimer in case DCP is monitored but
not detected;
- ps-TransmitOtherPeriodicCSI (optional): the configuration to report periodic CSI that is not L1-RSRP on
PUCCH during the time duration indicated by drx-onDurationTimer in case DCP is configured but associated
drx-onDurationTimer is not started;
ETSI

3GPP TS 38.523-1 version 18.3.0 Release 18 1578 ETSI TS 138 523-1 V18.3.0 (2025-05)
- ps-TransmitPeriodicL1-RSRP (optional): the configuration to transmit periodic CSI that is L1-RSRP on PUCCH
during the time duration indicated by drx-onDurationTimer in case DCP is configured but associated drx-
onDurationTimer is not started.
Serving Cells may be configured by RRC in two groups. When RRC does not configure a secondary DRX group, there
is only one DRX group. When two DRX groups are configured each group of Serving Cells, which is called a DRX
group, is configured by RRC with its own set of parameters: drx-onDurationTimer, drx-InactivityTimer. When two
DRX groups are configured, the two groups share the following parameter values: drx-SlotOffset, drx-
RetransmissionTimerDL, drx-RetransmissionTimerUL, drx-LongCycleStartOffset, drx-ShortCycle (optional), drx-
ShortCycleTimer (optional), drx-HARQ-RTT-TimerDL, and drx-HARQ-RTT-TimerUL.
When a DRX cycle is configured, the Active Time for Serving Cells in a DRX group includes the time while:
- drx-onDurationTimer or drx-InactivityTimer configured for the DRX group is running; or
- drx-RetransmissionTimerDL or drx-RetransmissionTimerUL is running on any Serving Cell in the DRX group;
or
- ra-ContentionResolutionTimer (as described in clause 5.1.5) or msgB-ResponseWindow (as described in clause
5.1.4a) is running; or
- a Scheduling Request is sent on PUCCH and is pending (as described in clause 5.4.4); or
- a PDCCH indicating a new transmission addressed to the C-RNTI of the MAC entity has not been received after
successful reception of a Random Access Response for the Random Access Preamble not selected by the MAC
entity among the contention-based Random Access Preamble (as described in clauses 5.1.4 and 5.1.4a).
When DRX is configured, the MAC entity shall:
1> if the Long DRX Cycle is used, and [(SFN × 10) + subframe number] modulo (drx-LongCycle) = drx-
StartOffset:
2> if DCP monitoring is configured for the active DL BWP as specified in TS 38.213 [6], clause 10.3:
3> if DCP indication associated with the current DRX Cycle received from lower layer indicated to start drx-
onDurationTimer, as specified in TS 38.213 [6]; or
3> if all DCP occasion(s) in time domain, as specified in TS 38.213 [6], associated with the current DRX
Cycle occurred in Active Time considering grants/assignments/DRX Command MAC CE/Long DRX
Command MAC CE received and Scheduling Request sent until 4 ms prior to start of the last DCP
occasion, or within BWP switching interruption length, or during a measurement gap; or
3> if ps-Wakeup is configured with value true and DCP indication associated with the current DRX Cycle
has not been received from lower layers:
4> start drx-onDurationTimer after drx-SlotOffset from the beginning of the subframe.
2> else:
3> start drx-onDurationTimer after drx-SlotOffset from the beginning of the subframe.
NOTE 2: In case of unaligned SFN across carriers in a cell group, the SFN of the SpCell is used to calculate the
DRX duration.
1> if the DRX group is in Active Time:
2> monitor the PDCCH on the Serving Cells in this DRX group as specified in TS 38.213 [6];
2> if the PDCCH indicates a DL transmission:
3> start the drx-HARQ-RTT-TimerDL for the corresponding HARQ process in the first symbol after the end
of the corresponding transmission carrying the DL HARQ feedback;
NOTE 3: When HARQ feedback is postponed by PDSCH-to-HARQ_feedback timing indicating a non-numerical
k1 value, as specified in TS 38.213 [6], the corresponding transmission opportunity to send the DL
HARQ feedback is indicated in a later PDCCH requesting the HARQ-ACK feedback.
ETSI

3GPP TS 38.523-1 version 18.3.0 Release 18 1579 ETSI TS 138 523-1 V18.3.0 (2025-05)
3> stop the drx-RetransmissionTimerDL for the corresponding HARQ process.
3> if the PDSCH-to-HARQ_feedback timing indicate a non-numerical k1 value as specified in TS 38.213
[6]:
4> start the drx-RetransmissionTimerDL in the first symbol after the PDSCH transmission for the
corresponding HARQ process.
2> if the PDCCH indicates a UL transmission:
3> start the drx-HARQ-RTT-TimerUL for the corresponding HARQ process in the first symbol after the end
of the first repetition of the corresponding PUSCH transmission;
3> stop the drx-RetransmissionTimerUL for the corresponding HARQ process.
2> if the PDCCH indicates a new transmission (DL or UL) on a Serving Cell in this DRX group:
3> start or restart drx-InactivityTimer for this DRX group in the first symbol after the end of the PDCCH
reception.
1> if DCP monitoring is configured for the active DL BWP as specified in TS 38.213 [6], clause 10.3; and
1> if the current symbol n occurs within drx-onDurationTimer duration; and
1> if drx-onDurationTimer associated with the current DRX cycle is not started as specified in this clause:
2> if the MAC entity would not be in Active Time considering grants/assignments/DRX Command MAC
CE/Long DRX Command MAC CE received and Scheduling Request sent until 4 ms prior to symbol n when
evaluating all DRX Active Time conditions as specified in this clause:
3> not transmit periodic SRS and semi-persistent SRS defined in TS 38.214 [7];
3> not report semi-persistent CSI configured on PUSCH;
3> if ps-TransmitPeriodicL1-RSRP is not configured with value true:
4> not report periodic CSI that is L1-RSRP on PUCCH.
3> if ps-TransmitOtherPeriodicCSI is not configured with value true:
4> not report periodic CSI that is not L1-RSRP on PUCCH.
1> else:
2> in current symbol n, if the DRX group would not be in Active Time considering grants/assignments
scheduled on Serving Cell(s) in this DRX Group and DRX Command MAC CE/Long DRX Command MAC
CE received and Scheduling Request sent until 4 ms prior to symbol n when evaluating all DRX Active Time
conditions as specified in this clause:
3> not transmit periodic SRS and semi-persistent SRS defined in TS 38.214 [7] in this DRX group;
3> not report CSI on PUCCH and semi-persistent CSI configured on PUSCH in this DRX group.
…
Regardless of whether the MAC entity is monitoring PDCCH or not on the Serving Cells in this DRX group, the MAC
entity transmits HARQ feedback, aperiodic CSI on PUSCH, and aperiodic SRS defined in TS 38.214 [7] on the Serving
Cells in this DRX group when such is expected.
The MAC entity needs not to monitor the PDCCH if it is not a complete PDCCH occasion (e.g. the Active Time starts
or ends in the middle of a PDCCH occasion).
[TS 38.213, clause 10.3]
A UE configured with DRX mode operation [11, TS 38.321] can be provided the following for detection of a DCI
format 2_6 in a PDCCH reception on the PCell or on the SpCell [12, TS 38.331]
ETSI

3GPP TS 38.523-1 version 18.3.0 Release 18 1580 ETSI TS 138 523-1 V18.3.0 (2025-05)
- a PS-RNTI for DCI format 2_6 by ps-RNTI
- a number of search space sets, by dci-Format2-6, to monitor PDCCH for detection of DCI format 2_6 on the
active DL BWP of the PCell or of the SpCell according to a common search space as described in clause 10.1
- a payload size for DCI format 2_6 by sizeDCI-2-6
- a location in DCI format 2_6 of a Wake-up indication bit by ps-PositionDCI-2-6
- a '0' value for the Wake-up indication bit, when reported to higher layers, indicates to not start the drx-
onDurationTimer for the next long DRX cycle [11, TS 38.321]
- a '1' value for the Wake-up indication bit, when reported to higher layers, indicates to start the drx-
onDurationTimer for the next long DRX cycle [11, TS 38.321]
- a bitmap, when the UE is provided a number of groups of configured SCells by
dormancyGroupOutsideActiveTime, where
- the bitmap location is immediately after the Wake-up indication bit location
- the bitmap size is equal to the number of groups of configured SCells where each bit of the bitmap
corresponds to a group of configured SCells from the number of groups of configured SCells
- a '0' value for a bit of the bitmap indicates an active DL BWP, provided by dormantBWP-Id, for the UE [11,
TS38.321] for each activated SCell in the corresponding group of configured SCells
- a '1' value for a bit of the bitmap indicates
- an active DL BWP, provided by firstOutsideActiveTimeBWP-Id, for the UE for each activated SCell in
the corresponding group of configured SCells, if a current active DL BWP is the dormant DL BWP
- a current active DL BWP, for the UE for each activated SCell in the corresponding group of configured
SCells, if the current active DL BWP is not the dormant DL BWP
- the UE sets the active DL BWP to the indicated active DL BWP
- an offset by ps-Offset indicating a time, where the UE starts monitoring PDCCH for detection of DCI format 2_6
according to the number of search space sets, prior to a slot where the drx-onDurationTimer would start on the
PCell or on the SpCell [11, TS 38.321]
- for each search space set, the PDCCH monitoring occasions are the ones in the first slots indicated
by duration, or slot if duration is not provided, starting from the first slot of the first slots and
ending prior to the start of drx-onDurationTimer.
On PDCCH monitoring occasions associated with a same long DRX Cycle, a UE does not expect to detect more than
one DCI format 2_6 with different values of the Wake-up indication bit for the UE or with different values of the
bitmap for the UE.
The UE does not monitor PDCCH for detecting DCI format 2_6 during Active Time [11, TS 38.321].
If a UE reports for an active DL BWP a MinTimeGap value that is X slots prior to the beginning of a slot where the UE
would start the drx-onDurationTimer, the UE is not required to monitor PDCCH for detection of DCI format 2_6 during
the X slots, where X corresponds to the MinTimeGap value of the SCS of the active DL BWP in Table 10.3-1.
Table 10.3-1: Minimum time gap value X
Minimum Time Gap X (slots)
SCS (kHz)
Value 1 Value 2
15 1 3
30 1 6
60 1 12
120 2 24
480 8 96
960 16 192
ETSI

3GPP TS 38.523-1 version 18.3.0 Release 18 1581 ETSI TS 138 523-1 V18.3.0 (2025-05)
If a UE is provided search space sets to monitor PDCCH for detection of DCI format 2_6 in the active DL BWP of the
PCell or of the SpCell and the UE detects DCI format 2_6, the physical layer of a UE reports the value of the Wake-up
indication bit for the UE to higher layers [11, TS 38.321] for the next long DRX cycle.
If a UE is provided search space sets to monitor PDCCH for detection of DCI format 2_6 in the active DL BWP of the
PCell or of the SpCell and the UE does not detect DCI format 2_6, the physical layer of the UE does not report a value
of the Wake-up indication bit to higher layers for the next long DRX cycle.
If a UE is provided search space sets to monitor PDCCH for detection of DCI format 2_6 in the active DL BWP of the
PCell or of the SpCell and the UE
- is not required to monitor PDCCH for detection of DCI format 2_6, as described in clauses 10, 11.1, 12, and in
clause 5.7 of [11, TS 38.321] for all corresponding PDCCH monitoring occasions outside Active Time prior to a
next long DRX cycle, or
- does not have any PDCCH monitoring occasions for detection of DCI format 2_6 outside Active Time of a next
long DRX cycle
the physical layer of the UE reports a value of 1 for the Wake-up indication bit to higher layers for the next long DRX
cycle.
[TS 38.212, clause 7.3.1.3.7]
DCI format 2_6 is used for notifying the power saving information outside DRX Active Time for one or more UEs.
The following information is transmitted by means of the DCI format 2_6 with CRC scrambled by PS-RNTI:
- block number 1, block number 2,…, block number N
where the starting position of a block is determined by the parameter PSPositionDCI2-6 provided by higher
layers for the UE configured with the block.
If the UE is configured with higher layer parameter PS-RNTI and dci-Format2-6, one block is configured for the UE by
higher layers, with the following fields defined for the block:
- Wake-up indication - 1 bit
- SCell dormancy indication – 0 bit if higher layer parameter Scell-groups-for-dormancy-outside-active-time is not
configured; otherwise 1, 2, 3, 4 or 5 bits bitmap determined according to higher layer parameter Scell-groups-
for-dormancy-outside-active-time, where each bit corresponds to one of the SCell group(s) configured by higher
layers parameter Scell-groups-for-dormancy-outside-active-time, with MSB to LSB of the bitmap corresponding
to the first to last configured SCell group.
The size of DCI format 2_6 is indicated by the higher layer parameter SizeDCI_2-6, according to Clause 10.3 of [5, TS
38.213].
7.1.1.12.3.3 Test description
7.1.1.12.3.3.1 Pre-test conditions
Same Pre-test conditions as in clause 7.1.1.0 except that set to return no data in uplink.
7.1.1.12.3.3.2 Test procedure sequence
Table 7.1.1.12.3.3.2-1: Main behaviour
St Procedure Message Sequence TP Verdict
U - S Message
1 SS transmits RRCReconfiguration to configure <-- RRCReconfiguration - -
specific DCP parameters. (Note 1)
2 The UE transmits --> RRCReconfigurationComplete - -
RRCReconfigurationComplete. (Note 2)
3 Wait 1280ms to ensure UE is out DRX active - - - -
time.
3A The SS transmits DCI 2-6 on the PDCCH <-- (PDCCH (DCI 2-6)) - -
ETSI

3GPP TS 38.523-1 version 18.3.0 Release 18 1582 ETSI TS 138 523-1 V18.3.0 (2025-05)
within the PS-offset time before the start of
next long DRX drx-onDurationTimer and the
DCI 2-6 indicates not to start the next Drx-
onDurationTimer.
3B In a PDCCH occasion the SS indicates the <-- MAC PDU - -
transmission of a DL MAC PDU on the
PDCCH.
3C Check: Does the UE transmit a HARQ ACK for --> HARQ ACK 5 F
the DL MAC PDU in Step 3B?
4 The SS transmits DCI 2-6 on the PDCCH <-- (PDCCH (DCI 2-6)) - -
within the PS-offset time before the start of
next long DRX drx-onDurationTimer and the
DCI 2-6 indicates to start the next Drx-
onDurationTimer.
5 In the first PDCCH occasion when the Drx- <-- MAC PDU - -
onDurationTimer is running, the SS indicates
the transmission of a DL MAC PDU on the
PDCCH.
6 Check: Does the UE transmit a HARQ ACK for --> HARQ ACK 1 P
the DL MAC PDU in Step 5?
7 The SS transmits RRCReconfiguration to <-- RRCReconfiguration - -
configure ps-wakeup with value true. (Note 1)
8 The UE transmits --> RRCReconfigurationComplete - -
RRCReconfigurationComplete. (Note 2)
9 Wait 1280ms to ensure UE is out DRX active - - - -
time.
10 In the first PDCCH occasion when the Drx- <-- MAC PDU - -
onDurationTimer is running, the SS indicates
the transmission of a DL MAC PDU on the
PDCCH.
11 Check: Does the UE transmit a HARQ ACK for --> HARQ ACK 2 P
the DL MAC PDU in Step 10?
12 SS transmits RRCReconfiguration to configure <-- RRCReconfiguration - -
specific DCP parameters. (Note 1)
13 The UE transmits --> RRCReconfigurationComplete - -
RRCReconfigurationComplete. (Note 2)
14 Wait 400ms to ensure UE is out DRX active - - - -
time.
15 The SS transmits DCI 2-6 on the PDCCH <-- (PDCCH (DCI 2-6)) - -
within the PS-offset time before the start of
next long DRX drx-onDurationTimer and the
DCI 2-6 indicates to start the next Drx-
onDurationTimer.
16 In the last PDCCH occasion when the Drx- <-- Invalid MAC PDU - -
onDurationTimer is running, the SS indicates
the transmission of an invalid DL MAC PDU on
the PDCCH.
17 The UE transmits a HARQ NACK for the DL --> HARQ NACK - -
MAC PDU in Step 16.
17 The SS transmits DCI 2-6 on the PDCCH <-- (PDCCH (DCI 2-6)) - -
A within the PS-offset time before the start of
next long DRX drx-onDurationTimer and the
DCI 2-6 indicates not to start the next Drx-
onDurationTimer.
18 In the PDCCH occasion when the next Drx- <-- MAC PDU - -
onDurationTimer is running, the SS indicates
the transmission of a DL MAC PDU on the
PDCCH.
19 Check: Does the UE transmit a HARQ ACK for --> HARQ ACK 3 P
the DL MAC PDU in Step 18?
19 The SS transmits DCI 2-6 on the PDCCH <-- (PDCCH (DCI 2-6)) - -
A within the PS-offset time before the start of
next long DRX drx-onDurationTimer and the
DCI 2-6 indicates to start the next Drx-
onDurationTimer.
20 The SS transmits RRCReconfiguration to <-- RRCReconfiguration - -
configure specific measonfig parameters.
ETSI

3GPP TS 38.523-1 version 18.3.0 Release 18  1583  ETSI TS 138 523-1 V18.3.0 (2025-05)
(Note 1)
| 21  The UE transmits  |     | -->  RRCReconfigurationComplete  |     | -  -  |
| --------------------- | --- | -------------------------------- | --- | ----- |
RRCReconfigurationComplete. (Note 2)
| 22  Wait 10ms to ensure UE is out DRX active  |     | -  -  |     | -  -  |
| --------------------------------------------- | --- | ----- | --- | ----- |
time.
22 The SS transmits DCI 2-6 on the PDCCH  <--  (PDCCH (DCI 2-6))  -  -
A  within the PS-offset time before the start of
next long DRX drx-onDurationTimer and the
DCI 2-6 indicates not to start the next Drx-
onDurationTimer.
23  In the first PDCCH occasion when the Drx- <--  MAC PDU  -  -
onDurationTimer is running, the SS indicates
the transmission of a DL MAC PDU on the
PDCCH.
24  Check: Does the UE transmit a HARQ ACK for  -->  HARQ ACK  4  P
the DL MAC PDU in Step 23?
Note 1:  For EN-DC the NR RRCReconfiguration message is contained in RRCConnectionReconfiguration 36.508
[7], Table 4.6.1-8 using condition EN-DC_EmbedNR_RRCRecon.In addition to this, for Step 20, the
specific message contents in Table 7.1.1.12.3.3.3-9 for RRC Connection Reconfiguration is used
Note 2:  For EN-DC the NR RRCReconfigurationComplete message is contained in
RRCConnectionReconfigurationComplete.

| 7.1.1.12.3.3.3  | Specific message contents  |     |     |     |
| --------------- | -------------------------- | --- | --- | --- |
Table 7.1.1.12.3.3.3-1: RRCReconfiguration (steps 1, 7 and 12, Table 7.1.1.12.3.3.2-1)
Derivation Path: TS 38.508-1 [4], Table 4.6.1-13
|                                        | Information Element  | Value/remark     | Comment  | Condition  |
| -------------------------------------- | -------------------- | ---------------- | -------- | ---------- |
| RRCReconfiguration ::= SEQUENCE {      |                      |                  |          |            |
|   criticalExtensions CHOICE {          |                      |                  |          |            |
|     rrcReconfiguration ::= SEQUENCE {  |                      |                  |          |            |
|       secondaryCellGroup               |                      | CellGroupConfig  |          | EN-DC      |
|       nonCriticalExtension             |                      | Not present      |          | EN-DC      |
|       nonCriticalExtension SEQUENCE {  |                      |                  |          | NR         |
|         masterCellGroup                |                      | CellGroupConfig  |          |            |
|       }                                |                      |                  |          |            |
|     }                                  |                      |                  |          |            |
|   }                                    |                      |                  |          |            |
| }                                      |                      |                  |          |            |

Table 7.1.1.12.3.3.3-2: CellGroupConfig (Table 7.1.1.12.3.3.3-1)
Derivation Path: TS 38.508-1 [4], Table 4.6.3-19
|                                 | Information Element  | Value/remark       | Comment  | Condition  |
| ------------------------------- | -------------------- | ------------------ | -------- | ---------- |
| CellGroupConfig ::= SEQUENCE {  |                      |                    |          |            |
|   spCellConfig SEQUENCE {       |                      |                    |          |            |
|     spCellConfigDedicated       |                      | ServingCellConfig  |          |            |
|   }                             |                      |                    |          |            |
| }                               |                      |                    |          |            |

Table 7.1.1.12.3.3.3-3: ServingCellConfig (Table 7.1.1.13.3.3.3-2)
Derivation Path: TS 38.508-1 [4] Table 4.6.3-167
|                                      | Information Element  | Value/remark  | Comment  | Condition     |
| ------------------------------------ | -------------------- | ------------- | -------- | ------------- |
| ServingCellConfig ::= SEQUENCE {     |                      |               |          |               |
|   initialDownlinkBWP ::= SEQUENCE {  |                      |               |          |               |
|     pdcch-Config CHOICE {            |                      |               |          | Step 1, Step  |
7, Step 12,
Step 20
|       setup  |     | PDCCH-Config  |     |     |
| ------------ | --- | ------------- | --- | --- |
|     }        |     |               |     |     |
|   }          |     |               |     |     |
ETSI

3GPP TS 38.523-1 version 18.3.0 Release 18  1584  ETSI TS 138 523-1 V18.3.0 (2025-05)
| }   |     |     |     |     |
| --- | --- | --- | --- | --- |

Table 7.1.1.12.3.3.3-4: PDCCH-Config (Table 7.1.1.12.3.3.3-3)
Derivation Path: TS 38.508-1 [4],Table 4.6.3-95 with condition DCI_2_6

Table 7.1.1.12.3.3.3-5: CellGroupConfig (Table 7.1.1.13.3.3.3-1: RRCReconfiguration step 7)
Derivation Path: TS 38.508-1 [4], Table 4.6.3-19
|                                          | Information Element  | Value/remark  | Comment  | Condition  |
| ---------------------------------------- | -------------------- | ------------- | -------- | ---------- |
| CellGroupConfig ::= SEQUENCE {           |                      |               |          |            |
|   physicalCellGroupConfig::= SEQUENCE {  |                      |               |          |            |
|     dcp-Config-r16 CHOICE {              |                      |               |          |            |
|       setup SEQUENCE {                   |                      |               |          |            |
|         ps-WakeUp-r16                    |                      | true          |          |            |
|       }                                  |                      |               |          |            |
|     }                                    |                      |               |          |            |
|   }                                      |                      |               |          |            |
| }                                        |                      |               |          |            |

Table 7.1.1.12.3.3.3-6: CellGroupConfig (Table 7.1.1.13.3.3.3-1: RRCReconfiguration step 12)
Derivation Path: TS 38.508-1 [4], Table 4.6.3-19
|                                            | Information Element  | Value/remark  | Comment  | Condition  |
| ------------------------------------------ | -------------------- | ------------- | -------- | ---------- |
| CellGroupConfig ::= SEQUENCE {             |                      |               |          |            |
|   mac-CellGroupConfig ::= SEQUENCE {       |                      |               |          |            |
|     drx-Config CHOICE {                    |                      |               |          |            |
|       setup SEQUENCE {                     |                      |               |          |            |
|         drx-onDurationTimer CHOICE {       |                      | ms10          |          |            |
|           milliSeconds                     |                      | ms10          |          |            |
|         }                                  |                      |               |          |            |
|         drx-InactivityTimer                |                      | ms6           |          |            |
|         drx-HARQ-RTT-TimerDL               |                      | 56            |          |            |
|         drx-HARQ-RTT-TimerUL               |                      | 56            |          |            |
|         drx-RetransmissionTimerDL          |                      | sl320         |          |            |
|         drx-RetransmissionTimerUL          |                      | sl320         |          |            |
|         drx-LongCycleStartOffset CHOICE {  |                      |               |          |            |
|           ms20                             |                      | 0             |          |            |
|         }                                  |                      |               |          |            |
|         shortDRX                           |                      | Not present   |          |            |
|         drx-SlotOffset                     |                      | ms0           |          |            |
|       }                                    |                      |               |          |            |
|     }                                      |                      |               |          |            |
|   }                                        |                      |               |          |            |
|   physicalCellGroupConfig::= SEQUENCE {    |                      |               |          |            |
|     dcp-Config-r16 CHOICE {                |                      |               |          |            |
|       setup SEQUENCE {                     |                      |               |          |            |
|         ps-Offset-r16                      |                      | 40            |          |            |
|       }                                    |                      |               |          |            |
|     }                                      |                      |               |          |            |
|   }                                        |                      |               |          |            |
| }                                          |                      |               |          |            |

Table 7.1.1.12.3.3.3-7: RRCReconfiguration (step 20, Table 7.1.1.12.3.3.2-1)
Derivation Path: TS 38.508-1 [4], Table 4.6.1-13
|                                        | Information Element  | Value/remark     | Comment  | Condition  |
| -------------------------------------- | -------------------- | ---------------- | -------- | ---------- |
| RRCReconfiguration ::= SEQUENCE {      |                      |                  |          |            |
|   criticalExtensions CHOICE {          |                      |                  |          |            |
|     rrcReconfiguration ::= SEQUENCE {  |                      |                  |          |            |
|       secondaryCellGroup               |                      | CellGroupConfig  |          | EN-DC      |
ETSI

3GPP TS 38.523-1 version 18.3.0 Release 18  1585  ETSI TS 138 523-1 V18.3.0 (2025-05)
|       measConfig ::= SEQUENCE {  |     |     |     |
| -------------------------------- | --- | --- | --- |
        measObjectToAddModList SEQUENCE (SIZE  2 entries
(1..maxNrofMeasId)) OF MeasObjectToAddMod {
|           MeasObjectToAddMod[1] SEQUENCE {  |                    | entry 1  |     |
| ------------------------------------------- | ------------------ | -------- | --- |
|             measObjectId                    | 1                  |          |     |
|             measObject CHOICE {             |                    |          |     |
|               measObjectNR SEQUENCE {       |                    |          |     |
|                 ssbFrequency                | ARFCN-ValueNR for  |          |     |
SSB of NR Cell 1
                absThreshSS-BlocksConsolidation   Not present
|                 nrofSS-BlocksToAverage      | Not present        |     |     |
| ------------------------------------------- | ------------------ | --- | --- |
|               }                             |                    |     |     |
|             }                               |                    |     |     |
|           }                                 |                    |     |     |
|           MeasObjectToAddMod[2] SEQUENCE {  |                    |     |     |
|             measObjectId                    | 2                  |     |     |
|             measObject CHOICE {             |                    |     |     |
|               measObjectNR SEQUENCE {       |                    |     |     |
|                 ssbFrequency                | ARFCN-ValueNR for  |     |     |
SSB of NR Cell 3
                absThreshSS-BlocksConsolidation   Not present
|                 nrofSS-BlocksToAverage          | Not present  |     |     |
| ----------------------------------------------- | ------------ | --- | --- |
|               }                                 |              |     |     |
|             }                                   |              |     |     |
|           }                                     |              |     |     |
|         }                                       |              |     |     |
|         reportConfigToAddModList SEQUENCE(SIZE  | 1 entry      |     |     |
(1..maxReportConfigId)) OF ReportConfigToAddMod
{
|           ReportConfigToAddMod[1] SEQUENCE {      |           | entry 1          |     |
| ------------------------------------------------- | --------- | ---------------- | --- |
|             reportConfigId                        | 1         |                  |     |
|             reportConfig CHOICE {                 |           |                  |     |
|               reportConfigNR SEQUENCE {           |           |                  |     |
|                 reportType CHOICE {               |           |                  |     |
|                  eventTriggered SEQUENCE {        |           |                  |     |
|                    eventId CHOICE {               |           |                  |     |
|                      eventA3 SEQUENCE {           |           |                  |     |
|                        a3-Offset CHOICE {         |           |                  |     |
|                          rsrp                     | 2         | 1 dB (2*0.5 dB)  |     |
|                        }                          |           |                  |     |
|                      }                            |           |                  |     |
|                    }                              |           |                  |     |
|                    reportAmount                   | infinity  |                  |     |
|                    reportQuantityCell SEQUENCE {  |           |                  |     |
|                      rsrp                         | true      |                  |     |
|                      rsrq                         | false     |                  |     |
|                      sinr                         | false     |                  |     |
|                    }                              |           |                  |     |
|                  }                                |           |                  |     |
|                }                                  |           |                  |     |
|              }                                    |           |                  |     |
|             }                                     |           |                  |     |
|           }                                       |           |                  |     |
|         }                                         |           |                  |     |
|         measIdToAddModList SEQUENCE (SIZE         | 1 entry   |                  |     |
(1..maxNrofMeasId)) OF MeasIdToAddMod {
|           MeasIdToAddMod[1] SEQUENCE {  |     | entry 1  |     |
| --------------------------------------- | --- | -------- | --- |
|             measId                      | 1   |          |     |
|             measObjectId                | 2   |          |     |
|             reportConfigId              | 1   |          |     |
|           }                             |     |          |     |
|         }                               |     |          |     |
|         measGapConfig ::= SEQUENCE {    |     |          |     |
|           gapUE CHOICE {                |     |          |     |
|             setup SEQUENCE {            |     |          |     |
ETSI

3GPP TS 38.523-1 version 18.3.0 Release 18  1586  ETSI TS 138 523-1 V18.3.0 (2025-05)
|               gapOffset            |     | 34               |     |     |
| ---------------------------------- | --- | ---------------- | --- | --- |
|               mgl                  |     | ms6              |     |     |
|               mgrp                 |     | ms40             |     |     |
|               mgta                 |     | ms0              |     |     |
|             }                      |     |                  |     |     |
|           }                        |     |                  |     |     |
|         }                          |     |                  |     |     |
|       }                            |     |                  |     |     |
|     }                              |     |                  |     |     |
|   }                                |     |                  |     |     |
|   nonCriticalExtension SEQUENCE {  |     |                  |     | NR  |
|     masterCellGroup                |     | CellGroupConfig  |     |     |
|   }                                |     |                  |     |     |
| }                                  |     |                  |     |     |

Table 7.1.1.12.3.3.3-8: CellGroupConfig (Table 7.1.1.12.3.3.3-7)
Derivation Path: TS 38.508-1 [4], Table 4.6.3-19
|                                            | Information Element  | Value/remark  | Comment  | Condition  |
| ------------------------------------------ | -------------------- | ------------- | -------- | ---------- |
| CellGroupConfig ::= SEQUENCE {             |                      |               |          |            |
|   mac-CellGroupConfig ::= SEQUENCE {       |                      |               |          |            |
|     drx-Config CHOICE {                    |                      |               |          |            |
|       setup SEQUENCE {                     |                      |               |          |            |
|         drx-onDurationTimer CHOICE {       |                      |               |          |            |
|           milliSeconds                     |                      | ms10          |          |            |
|         }                                  |                      |               |          |            |
|         drx-InactivityTimer                |                      | ms5           |          |            |
|         drx-LongCycleStartOffset CHOICE {  |                      |               |          |            |
|           ms40                             |                      | 39            |          |            |
|         }                                  |                      |               |          |            |
|         shortDRX                           |                      | Not present   |          |            |
|         drx-SlotOffset                     |                      | ms0           |          |            |
|       }                                    |                      |               |          |            |
|     }                                      |                      |               |          |            |
|   }                                        |                      |               |          |            |
|   physicalCellGroupConfig::= SEQUENCE {    |                      |               |          |            |
|     dcp-Config-r16 CHOICE {                |                      |               |          |            |
|       setup SEQUENCE {                     |                      |               |          |            |
|         ps-Offset-r16                      |                      | 32            |          |            |
|         ps-PositionDCI-2-6-r16             |                      | 5             |          |            |
|       }                                    |                      |               |          |            |
|     }                                      |                      |               |          |            |
|   }                                        |                      |               |          |            |
| }                                          |                      |               |          |            |

Table 7.1.1.12.3.3.3-9: RRCConnectionReconfiguration (Step 20)
Derivation path: 36.508 table 4.6.1-8
|                                                   | Information Element  | Value/Remark  | Comment       | Condition  |
| ------------------------------------------------- | -------------------- | ------------- | ------------- | ---------- |
| RRCConnectionReconfiguration ::= SEQUENCE {       |                      |               |               |            |
| criticalExtensions CHOICE {                       |                      |               |               |            |
|     c1 CHOICE{                                    |                      |               |               |            |
|       rrcConnectionReconfiguration-r8 SEQUENCE {  |                      |               |               |            |
|         measConfig SEQUENCE {                     |                      |               |               |            |
|           measGapConfig CHOICE {                  |                      |               |               |            |
|            setup SEQUENCE {                       |                      |               |               |            |
|             gapOffset CHOICE {                    |                      |               |               |            |
|               gp0                                 |                      | 34            | MGRP = 40 ms  |            |
|             }                                     |                      |               |               |            |
|           }                                       |                      |               |               |            |
|         }                                         |                      |               |               |            |
|        }                                          |                      |               |               |            |
|      }                                            |                      |               |               |            |
ETSI

3GPP TS 38.523-1 version 18.3.0 Release 18 1587 ETSI TS 138 523-1 V18.3.0 (2025-05)
}
}
}
7.1.1.12.4 DRX adaptation / SCell dormancy indication
7.1.1.12.4.1 DRX adaptation / SCell dormancy indication / Intra-band Contiguous CA
7.1.1.12.4.1.1 Test Purpose (TP)
(1)
with { UE in RRC_CONNECTED state with SCell configured and long DRX is configured and DCP is
configured }
ensure that {
when { UE is outside DRX active time and receives the PDCCH indicating entering dormant BWP for
SCell }
then { UE activates the BWP indicated by dormantBWP-Id and stops monitoring the PDCCH }
}
(2)
with { UE in RRC_CONNECTED state with SCell configured and long DRX is configured and DCP is
configured }
ensure that {
when { UE is outside DRX active time and the active DL BWP is dormant BWP and receives the PDCCH
indicating leaving dormant BWP from SCell }
then { UE activates the BWP indicated by firstOutsideActiveTimeBWP-Id and starts normal MAC
operation on the new BWP }
}
7.1.1.12.4.1.2 Conformance requirements
References: The conformance requirements covered in the present TC are specified in: TS 38.212, clause 7.3.1.3.7, TS
38.213, clause 10.3, TS 38.321, clause 5.15.1 and 5.9. Unless otherwise stated these are Rel-16 requirements.
[TS 38.212, clause 7.3.1.3.7]
DCI format 2_6 is used for notifying the power saving information outside DRX Active Time for one or more UEs.
The following information is transmitted by means of the DCI format 2_6 with CRC scrambled by PS-RNTI:
- block number 1, block number 2,…, block number N
where the starting position of a block is determined by the parameter ps-PositionDCI-2-6 provided by higher
layers for the UE configured with the block.
If the UE is configured with higher layer parameter ps-RNTI and dci-Format2-6, one block is configured for the UE by
higher layers, with the following fields defined for the block:
- Wake-up indication - 1 bit
- SCell dormancy indication – 0 bit if higher layer parameter dormancyGroupOutsideActiveTime is not
configured; otherwise 1, 2, 3, 4 or 5 bits bitmap determined according to higher layer parameter
dormancyGroupOutsideActiveTime, where each bit corresponds to one of the SCell group(s) configured by
higher layers parameter dormancyGroupOutsideActiveTime, with MSB to LSB of the bitmap corresponding to
the first to last configured SCell group.
The size of DCI format 2_6 is indicated by the higher layer parameter sizeDCI-2-6, according to Clause 10.3 of [5, TS
38.213].
[TS 38.213, clause 10.3]
A UE configured with DRX mode operation [11, TS 38.321] can be provided the following for detection of a DCI
format 2_6 in a PDCCH reception on the PCell or on the SpCell [12, TS 38.331]
ETSI

3GPP TS 38.523-1 version 18.3.0 Release 18 1588 ETSI TS 138 523-1 V18.3.0 (2025-05)
- a PS-RNTI for DCI format 2_6 by ps-RNTI
- a number of search space sets, by dci-Format2-6, to monitor PDCCH for detection of DCI format 2_6 on the
active DL BWP of the PCell or of the SpCell according to a common search space as described in Clause 10.1
- a payload size for DCI format 2_6 by sizeDCI_2-6
- a location in DCI format 2_6 of a Wake-up indication bit by psPositionDCI-2-6
- a '0' value for the Wake-up indication bit, when reported to higher layers, indicates to not start the drx-
onDurationTimer for the next long DRX cycle [11, TS 38.321]
- a '1' value for the Wake-up indication bit, when reported to higher layers, indicates to start the drx-
onDurationTimer for the next long DRX cycle [11, TS 38.321]
- a bitmap, when the UE is provided a number of groups of configured SCells by
dormancyGroupOutsideActiveTime, where
- the bitmap location is immediately after the Wake-up indication bit location
- the bitmap size is equal to the number of groups of configured SCells where each bit of the bitmap
corresponds to a group of configured SCells from the number of groups of configured SCells
- a '0' value for a bit of the bitmap indicates an active DL BWP, provided by dormantBWP-Id, for the UE [11,
TS38.321] for each activated SCell in the corresponding group of configured SCells
- a '1' value for a bit of the bitmap indicates
- an active DL BWP, provided by firstOutsideActiveTimeBWP-Id, for the UE for each activated SCell in
the corresponding group of configured SCells, if a current active DL BWP is the dormant DL BWP
- a current active DL BWP, for the UE for each activated SCell in the corresponding group of configured
SCells, if the current active DL BWP is not the dormant DL BWP
- an offset by ps-Offset indicating a time, where the UE starts monitoring PDCCH for detection of DCI format 2_6
according to the number of search space sets, prior to a slot where the drx-onDuarationTimer would start on the
PCell or on the SpCell [11, TS 38.321]
- for each search space set, the PDCCH monitoring occasions are the ones in the first slots indicated by
duration, or slot if duration is not provided, starting from the first slot of the first slots and ending
prior to the start of drx-onDurationTimer.
On PDCCH monitoring occasions associated with a same long DRX Cycle, a UE does not expect to detect more than
one DCI format 2_6 with different values of the Wake-up indication bit for the UE or with different values of the
bitmap for the UE.
The UE does not monitor PDCCH for detecting DCI format 2_6 during Active Time [11, TS 38.321].
If a UE reports for an active DL BWP a requirement of X slots prior to the beginning of a slot where the UE would start
the drx-onDurationTimer, the UE is not required to monitor PDCCH for detection of DCI format 2_6 during the X
slots, where X corresponds to the requirement of the SCS of the active DL BWP in Table 10.3-1.
Table 10.3-1: Minimum time gap value X
Minimum Time Gap X (slots)
SCS (kHz)
Value 1 Value 2
15 1 3
30 1 6
60 1 12
120 2 24
ETSI

3GPP TS 38.523-1 version 18.3.0 Release 18 1589 ETSI TS 138 523-1 V18.3.0 (2025-05)
If a UE is provided search space sets to monitor PDCCH for detection of DCI format 2_6 in the active DL BWP of the
PCell or of the SpCell and the UE detects DCI format 2_6, the physical layer of a UE reports the value of the Wake-up
indication bit for the UE to higher layers [11, TS 38.321] for the next long DRX cycle.
If a UE is provided search space sets to monitor PDCCH for detection of DCI format 2_6 in the active DL BWP of the
PCell or of the SpCell and the UE does not detect DCI format 2_6, the physical layer of the UE does not report a value
of the Wake-up indication bit to higher layers for the next long DRX cycle.
If a UE is provided search space sets to monitor PDCCH for detection of DCI format 2_6 in the active DL BWP of the
PCell or of the SpCell and the UE
- is not required to monitor PDCCH for detection of DCI format 2_6, as described in Clauses 10, 11.1, 12, and in
Clause 5.7 of [11, TS 38.321] for all corresponding PDCCH monitoring occasions outside Active Time prior to a
next long DRX cycle, or
- does not have any PDCCH monitoring occasions for detection of DCI format 2_6 outside Active Time of a next
long DRX cycle
the physical layer of the UE reports a value of 1 for the Wake-up indication bit to higher layers for the next long DRX
cycle.
…
If an active DL BWP provided by dormantBWP-Id for a UE on an activated SCell is not a default DL BWP for the UE
on the activated SCell, as described in Clause 12, the BWP inactivity timer is not used for transitioning from the active
DL BWP provided by dormantBWP-Id to the default DL BWP on the activated SCell.
[TS 38.321, clause 5.15.1]
In addition to clause 12 of TS 38.213 [6], this clause specifies requirements on BWP operation.
A Serving Cell may be configured with one or multiple BWPs, and the maximum number of BWP per Serving Cell is
specified in TS 38.213 [6].
The BWP switching for a Serving Cell is used to activate an inactive BWP and deactivate an active BWP at a time. The
BWP switching is controlled by the PDCCH indicating a downlink assignment or an uplink grant, by the bwp-
InactivityTimer, by RRC signalling, or by the MAC entity itself upon initiation of Random Access procedure or upon
detection of consistent LBT failure on SpCell. Upon RRC (re-)configuration of firstActiveDownlinkBWP-Id and/or
firstActiveUplinkBWP-Id for SpCell or activation of an SCell, the DL BWP and/or UL BWP indicated by
firstActiveDownlinkBWP-Id and/or firstActiveUplinkBWP-Id respectively (as specified in TS 38.331 [5]) is active
without receiving PDCCH indicating a downlink assignment or an uplink grant. The active BWP for a Serving Cell is
indicated by either RRC or PDCCH (as specified in TS 38.213 [6]). For unpaired spectrum, a DL BWP is paired with a
UL BWP, and BWP switching is common for both UL and DL.
For each SCell a dormant BWP may be configured with dormantBWP-Id by RRC signalling as described in TS 38.331
[5]. Entering or leaving dormant BWP for SCells is done by BWP switching per SCell or per dormancy SCell group
based on instruction from PDCCH (as specified in TS 38.213 [6]). The dormancy SCell group configurations are
configured by RRC signalling as described in TS 38.331 [5]. Upon reception of the PDCCH indicating leaving dormant
BWP, the DL BWP indicated by firstOutsideActiveTimeBWP-Id or by firstWithinActiveTimeBWP-Id (as specified in
TS 38.331 [5] and TS 38.213 [6]) is activated. Upon reception of the PDCCH indicating entering dormant BWP, the DL
BWP indicated by dormantBWP-Id (as specified in TS 38.331 [5]) is activated. The dormant BWP configuration for
SpCell or PUCCH SCell is not supported.
For each activated Serving Cell configured with a BWP, the MAC entity shall:
1> if a BWP is activated and the active DL BWP for the Serving Cell is not the dormant BWP:
2> transmit on UL-SCH on the BWP;
2> transmit on RACH on the BWP, if PRACH occasions are configured;
2> monitor the PDCCH on the BWP;
2> transmit PUCCH on the BWP, if configured;
2> report CSI for the BWP;
ETSI

3GPP TS 38.523-1 version 18.3.0 Release 18 1590 ETSI TS 138 523-1 V18.3.0 (2025-05)
2> transmit SRS on the BWP, if configured;
2> receive DL-SCH on the BWP;
2> (re-)initialize any suspended configured uplink grants of configured grant Type 1 on the active BWP
according to the stored configuration, if any, and to start in the symbol according to rules in clause 5.8.2;
2> if lbt-FailureRecoveryConfig is configured:
3> stop the lbt-FailureDetectionTimer, if running;
3> set LBT_COUNTER to 0;
3> monitor LBT failure indications from lower layers as specified in clause 5.21.2.
1> if a BWP is activated and the active DL BWP for the Serving Cell is dormant BWP:
2> stop the bwp-InactivityTimer of this Serving Cell, if running.
2> not monitor the PDCCH on the BWP;
2> not monitor the PDCCH for the BWP;
2> not receive DL-SCH on the BWP;
2> not report CSI on the BWP, report CSI except aperiodic CSI for the BWP;
2> not transmit SRS on the BWP;
2> not transmit on UL-SCH on the BWP;
2> not transmit on RACH on the BWP;
2> not transmit PUCCH on the BWP.
2> clear any configured downlink assignment and any configured uplink grant Type 2 associated with the SCell
respectively;
2> suspend any configured uplink grant Type 1 associated with the SCell;
2> if configured, perform beam failure detection and beam failure recovery for the SCell if beam failure is
detected.
1> if a BWP is deactivated:
2> not transmit on UL-SCH on the BWP;
2> not transmit on RACH on the BWP;
2> not monitor the PDCCH on the BWP;
2> not transmit PUCCH on the BWP;
2> not report CSI for the BWP;
2> not transmit SRS on the BWP;
2> not receive DL-SCH on the BWP;
2> clear any configured downlink assignment and configured uplink grant of configured grant Type 2 on the
BWP;
2> suspend any configured uplink grant of configured grant Type 1 on the inactive BWP.
Upon initiation of the Random Access procedure on a Serving Cell, after the selection of carrier for performing Random
Access procedure as specified in clause 5.1.1, the MAC entity shall for the selected carrier of this Serving Cell:
1> if PRACH occasions are not configured for the active UL BWP:
ETSI

3GPP TS 38.523-1 version 18.3.0 Release 18 1591 ETSI TS 138 523-1 V18.3.0 (2025-05)
2> switch the active UL BWP to BWP indicated by initialUplinkBWP;
2> if the Serving Cell is an SpCell:
3> switch the active DL BWP to BWP indicated by initialDownlinkBWP.
1> else:
2> if the Serving Cell is an SpCell:
3> if the active DL BWP does not have the same bwp-Id as the active UL BWP:
4> switch the active DL BWP to the DL BWP with the same bwp-Id as the active UL BWP.
1> stop the bwp-InactivityTimer associated with the active DL BWP of this Serving Cell, if running.
1> if the Serving Cell is SCell:
2> stop the bwp-InactivityTimer associated with the active DL BWP of SpCell, if running.
1> perform the Random Access procedure on the active DL BWP of SpCell and active UL BWP of this Serving
Cell.
If the MAC entity receives a PDCCH for BWP switching of a Serving Cell, the MAC entity shall:
1> if there is no ongoing Random Access procedure associated with this Serving Cell; or
1> if the ongoing Random Access procedure associated with this Serving Cell is successfully completed upon
reception of this PDCCH addressed to C-RNTI (as specified in clauses 5.1.4, 5.1.4a, and 5.1.5):
2> cancel, if any, triggered consistent LBT failure for this Serving Cell;
2> perform BWP switching to a BWP indicated by the PDCCH.
If the MAC entity receives a PDCCH for BWP switching for a Serving Cell(s) or a dormancy SCell group(s) while a
Random Access procedure associated with that Serving Cell is ongoing in the MAC entity, it is up to UE
implementation whether to switch BWP or ignore the PDCCH for BWP switching, except for the PDCCH reception for
BWP switching addressed to the C-RNTI for successful Random Access procedure completion (as specified in clauses
5.1.4, 5.1.4a, and 5.1.5) in which case the UE shall perform BWP switching to a BWP indicated by the PDCCH. Upon
reception of the PDCCH for BWP switching other than successful contention resolution, if the MAC entity decides to
perform BWP switching, the MAC entity shall stop the ongoing Random Access procedure and initiate a Random
Access procedure after performing the BWP switching; if the MAC decides to ignore the PDCCH for BWP switching,
the MAC entity shall continue with the ongoing Random Access procedure on the Serving Cell.
…
1> if a PDCCH for BWP switching is received, and the MAC entity switches the active DL BWP:
2> if the defaultDownlinkBWP-Id is configured, and the MAC entity switches to the DL BWP which is not
indicated by the defaultDownlinkBWP-Id and is not indicated by the dormantBWP-Id if configured; or
2> if the defaultDownlinkBWP-Id is not configured, and the MAC entity switches to the DL BWP which is not
the initialDownlinkBWP and is not indicated by the dormantBWP-Id if configured:
3> start or restart the bwp-InactivityTimer associated with the active DL BWP.
[TS 38.321, clause 5.9]
If the MAC entity is configured with one or more SCells, the network may activate and deactivate the configured
SCells. Upon configuration of an SCell, the SCell is deactivated unless the parameter sCellState is set to activated for
the SCell by upper layers.
The configured SCell(s) is activated and deactivated by:
- receiving the SCell Activation/Deactivation MAC CE described in clause 6.1.3.10;
ETSI

3GPP TS 38.523-1 version 18.3.0 Release 18 1592 ETSI TS 138 523-1 V18.3.0 (2025-05)
- configuring sCellDeactivationTimer timer per configured SCell (except the SCell configured with PUCCH, if
any): the associated SCell is deactivated upon its expiry;
- configuring sCellState per configured SCell: if configured, the associated SCell is activated upon SCell
configuration.
The MAC entity shall for each configured SCell:
1> if an SCell is configured with sCellState set to activated upon SCell configuration, or an SCell
Activation/Deactivation MAC CE is received activating the SCell:
2> if the SCell was deactivated prior to receiving this SCell Activation/Deactivation MAC CE; or
2> if the SCell is configured with sCellState set to activated upon SCell configuration:
3> if firstActiveDownlinkBWP-Id is not set to dormant BWP:
4> activate the SCell according to the timing defined in TS 38.213 [6]; i.e. apply normal SCell operation
including:
5> SRS transmissions on the SCell;
5> CSI reporting for the SCell;
5> PDCCH monitoring on the SCell;
5> PDCCH monitoring for the SCell;
5> PUCCH transmissions on the SCell, if configured.
3> else (i.e. firstActiveDownlinkBWP-Id is set to dormant BWP):
4> stop the bwp-InactivityTimer of this Serving Cell, if running.
3> activate the DL BWP and UL BWP indicated by firstActiveDownlinkBWP-Id and firstActiveUplinkBWP-
Id respectively.
2> start or restart the sCellDeactivationTimer associated with the SCell according to the timing defined in TS
38.213 [6];
2> if the active DL BWP is not the dormant BWP:
3> (re-)initialize any suspended configured uplink grants of configured grant Type 1 associated with this
SCell according to the stored configuration, if any, and to start in the symbol according to rules in clause
5.8.2.2;
3> trigger PHR according to clause 5.4.6.
1> else if an SCell Activation/Deactivation MAC CE is received deactivating the SCell; or
1> if the sCellDeactivationTimer associated with the activated SCell expires:
2> deactivate the SCell according to the timing defined in TS 38.213 [6];
2> stop the sCellDeactivationTimer associated with the SCell;
2> stop the bwp-InactivityTimer associated with the SCell;
2> deactivate any active BWP associated with the SCell;
2> clear any configured downlink assignment and any configured uplink grant Type 2 associated with the SCell
respectively;
2> clear any PUSCH resource for semi-persistent CSI reporting associated with the SCell;
2> suspend any configured uplink grant Type 1 associated with the SCell;
2> flush all HARQ buffers associated with the SCell;
ETSI

3GPP TS 38.523-1 version 18.3.0 Release 18  1593  ETSI TS 138 523-1 V18.3.0 (2025-05)
2> cancel, if any, triggered consistent LBT failure for the SCell.
1> if PDCCH on the activated SCell indicates an uplink grant or downlink assignment; or
1> if PDCCH on the Serving Cell scheduling the activated SCell indicates an uplink grant or a downlink assignment
for the activated SCell; or
1> if a MAC PDU is transmitted in a configured uplink grant and LBT failure indication is not received from lower
layers; or
1> if a MAC PDU is received in a configured downlink assignment:
2> restart the sCellDeactivationTimer associated with the SCell.
1> if the SCell is deactivated:
2> not transmit SRS on the SCell;
2> not report CSI for the SCell;
2> not transmit on UL-SCH on the SCell;
2> not transmit on RACH on the SCell;
2> not monitor the PDCCH on the SCell;
2> not monitor the PDCCH for the SCell;
2> not transmit PUCCH on the SCell.
HARQ feedback for the MAC PDU containing SCell Activation/Deactivation MAC CE shall not be impacted by PCell,
PSCell and PUCCH SCell interruptions due to SCell activation/deactivation in TS 38.133 [11].
When SCell is deactivated, the ongoing Random Access procedure on the SCell, if any, is aborted.
| 7.1.1.12.4.1.3    | Test description     |     |     |     |     |     |
| ----------------- | -------------------- | --- | --- | --- | --- | --- |
| 7.1.1.12.4.1.3.1  | Pre-test conditions  |     |     |     |     |     |
Same Pre-test conditions as in clause 7.1.1.0 except that set to return no data in uplink. System information combination
NR-4 and in addition NR Cell 3 is configured as NR Active SCell.
| 7.1.1.12.4.1.3.2  | Test procedure sequence  |     |     |     |     |     |
| ----------------- | ------------------------ | --- | --- | --- | --- | --- |
Table 7.1.1.12.4.1.3.2-1: Cell configuration power level changes over time for FR1
|     |   Parameter  | Unit   | NR Cell 1  | NR Cell 3  | Remarks                     |     |
| --- | ------------ | ------ | ---------- | ---------- | --------------------------- | --- |
|     | T0  SS/PBCH  | dBm/SC | -88        | off        | NR cell 1 is available and  |     |
|     | SSS EPRE     | S      |            |            | NR cell 3 is not available  |     |
|     | T1  SS/PBCH  | dBm/SC | -88        | -88        | NR cell 1 and NR cell 3     |     |
|     | SSS EPRE     | S      |            |            | are available               |     |

Table 7.1.1.12.4.1.3.2-2: Cell configuration power level changes over time for FR2
|     |   Parameter  | Unit   | NR Cell 1  | NR Cell 3  | Remarks                     |     |
| --- | ------------ | ------ | ---------- | ---------- | --------------------------- | --- |
|     | T0  SS/PBCH  | dBm/SC | -82        | off        | NR cell 1 is available and  |     |
|     | SSS EPRE     | S      |            |            | NR cell 3 is not available  |     |
|     | T1  SS/PBCH  | dBm/SC | -82        | -82        | NR cell 1 and NR cell 3     |     |
|     | SSS EPRE     | S      |            |            | are available               |     |

Table 7.1.1.12.4.1.3.2-3: Main behaviour
| St  | Procedure  |     |     | Message Sequence  |     | TP  Verdict  |
| --- | ---------- | --- | --- | ----------------- | --- | ------------ |
ETSI

3GPP TS 38.523-1 version 18.3.0 Release 18  1594  ETSI TS 138 523-1 V18.3.0 (2025-05)
|                                                   |     |     | U - S  | Message  |       |
| ------------------------------------------------- | --- | --- | ------ | -------- | ----- |
| 0  Set the power levels according to “T1” as per  |     |     |   -    |          | -  -  |
Table 7.1.1.12.4.1.3.2-1/2.
| 1  SS transmits an RRCReconfiguration  |     |     | <--  -  |     | -  -  |
| -------------------------------------- | --- | --- | ------- | --- | ----- |
message. (Note 1)
| 2  The UE transmits  |     |     | -->  -  |     | -  -  |
| -------------------- | --- | --- | ------- | --- | ----- |
RRCReconfigurationComplete message. (Note
2)
3  The SS transmits a SCell Activation MAC-CE  <--  MAC PDU (SCell  -  -
to activate SCell (NR Cell 3).  Activation/Deactivation MAC CE
of one octet (C1=1))
4  The SS transmits DCI 2-6 within ps-Offset time  <--  (PDCCH (DCI 2-6))  -  -
before the start of next long DRX drx-
onDurationTimer on NR Cell 1. (Note 3)
5  The SS indicates a new transmission on  <--  MAC PDU  -  --
PDCCH of SCell and transmits a MAC PDU on
the initial BWP (BWP#0) when the Drx-
onDurationTimer is running.
| 6  Check: Does the UE transmit a HARQ ACK on  |     |     | -->  -  |     | 1  F  |
| --------------------------------------------- | --- | --- | ------- | --- | ----- |
the PCell for the DL MAC PDU in Step 5 within
5 seconds?
7  The SS transmits DCI 2-6 within the ps-offset  <--  (PDCCH (DCI 2-6))  -  -
time before the start of next long DRX drx-
onDurationTimer on NR Cell 1. (Note 4)
8  The SS indicates a new transmission on  <--  MAC PDU  -  -
PDCCH of SCell and transmits a MAC PDU on
the active BWP (BWP#0) when the Drx-
onDurationTimer is running.
9  Check: Does the UE transmit a HARQ ACK on  -->  HARQ ACK  2  P
the PCell NR Cell 1 for the DL MAC PDU in
Step 8?
Note 1:  For EN-DC the NR RRCReconfiguration message is contained in RRCConnectionReconfiguration TS
36.508 [7], Table 4.6.1-8 using condition EN-DC_EmbedNR_RRCRecon.
Note 2:  For EN-DC the NR RRCReconfigurationComplete message is contained in
RRCConnectionReconfigurationComplete.
Note 3:  The Wake-up indication is value 1 and the SCell dormancy indication is value 0 in the DCI 2-6.
Note 4:  The Wake-up indication is value 1 and the SCell dormancy indication is value 1 in the DCI 2-6.

| 7.1.1.12.4.1.3.3  | Specific message contents  |     |     |     |     |
| ----------------- | -------------------------- | --- | --- | --- | --- |
Table 7.1.1.12.4.1.3.3-1: RRCReconfiguration (step 1, Table 7.1.1.12.4.1.3.2-3)
Derivation Path: TS 38.508-1 [6], Table 4.6.1-13
|                                        | Information Element  |     | Value/remark     | Comment  | Condition  |
| -------------------------------------- | -------------------- | --- | ---------------- | -------- | ---------- |
| RRCReconfiguration ::= SEQUENCE {      |                      |     |                  |          |            |
|   criticalExtensions CHOICE {          |                      |     |                  |          |            |
|     rrcReconfiguration SEQUENCE {      |                      |     |                  |          |            |
|       secondaryCellGroup               |                      |     | CellGroupConfig  |          | EN-DC      |
|                                        |                      |     | Not present      |          | NR         |
|       nonCriticalExtension             |                      |     | Not present      |          | EN-DC      |
|       nonCriticalExtension SEQUENCE {  |                      |     |                  |          | NR         |
|         masterCellGroup                |                      |     | CellGroupConfig  |          |            |
|       }                                |                      |     |                  |          |            |
|     }                                  |                      |     |                  |          |            |
|   }                                    |                      |     |                  |          |            |
| }                                      |                      |     |                  |          |            |

Table 7.1.1.12.4.1.3.3-2: CellGroupConfig (Table 7.1.1.12.4.1.3.3-1)
Derivation Path: TS 38.508-1 [4], Table 4.6.3-19 with condition SCell_add
|                                 | Information Element  |     | Value/remark  | Comment      | Condition  |
| ------------------------------- | -------------------- | --- | ------------- | ------------ | ---------- |
| CellGroupConfig ::= SEQUENCE {  |                      |     |               |              |            |
|   cellGroupId                   |                      |     | CellGroupId   | TS 38.508-1  |            |
default value
ETSI

3GPP TS 38.523-1 version 18.3.0 Release 18  1595  ETSI TS 138 523-1 V18.3.0 (2025-05)
|   mac-CellGroupConfig SEQUENCE {  |     |             |              |     |
| --------------------------------- | --- | ----------- | ------------ | --- |
|     drx-Config CHOICE {           |     |             |              |     |
|       setup                       |     | DRX-Config  | TS 38.508-1  |     |
default value
|     }                                 |     |                 |              |     |
| ------------------------------------- | --- | --------------- | ------------ | --- |
|   }                                   |     |                 |              |     |
|   physicalCellGroupConfig SEQUENCE {  |     |                 |              |     |
|     dcp-Config-r16 CHOICE {           |     |                 |              |     |
|       setup                           |     | DCP-Config-r16  | TS 38.508-1  |     |
default value
|     }                                    |     |               |     |     |
| ---------------------------------------- | --- | ------------- | --- | --- |
|   }                                      |     |               |     |     |
|   spCellConfig SEQUENCE {                |     |               |     |     |
|     spCellConfigDedicated SEQUENCE {     |     |               |     |     |
|           initialDownlinkBWP SEQUENCE {  |     |               |     |     |
|             pdcch-Config CHOICE {        |     |               |     |     |
|               setup                      |     | PDCCH-Config  |     |     |
|         }                                |     |               |     |     |
|       }                                  |     |               |     |     |
|     }                                    |     |               |     |     |
|   }                                      |     |               |     |     |
|   sCellToAddModList SEQUENCE (SIZE       |     | 1 entry       |     |     |
(1..maxMeasId)) OF SCellConfig {
|     SCellConfig[1] SEQUENCE {  |     |                       | entry 1  |     |
| ------------------------------ | --- | --------------------- | -------- | --- |
|       sCellIndex               |     | SCellIndex as per TS  |          |     |
38.508-1 [4] table 4.6.3-
154
|       sCellConfigCommon  |     | ServingCellConfigComm |     |     |
| ------------------------ | --- | --------------------- | --- | --- |
on
|       sCellConfigDedicated  |     | ServingCellConfig  |     |     |
| --------------------------- | --- | ------------------ | --- | --- |
|     }                       |     |                    |     |     |
|   }                         |     |                    |     |     |
| }                           |     |                    |     |     |

Table 7.1.1.12.4.1.3.3-3: PDCCH-Config (Table 7.1.1.12.4.1.3.3-2)
Derivation Path: TS 38.508-1 [4],Table 4.6.3-95 with condition DCI_2_6

Table 7.1.1.12.4.1.3.3-4: ServingCellConfigCommon (Table 7.1.1.12.4.1.3.3-2)
Derivation Path: TS 38.508-1 [4], Table 4.6.3-168 with conditions No_UL and SCell_add.
|                                         | Information Element  | Value/remark               | Comment  | Condition  |
| --------------------------------------- | -------------------- | -------------------------- | -------- | ---------- |
| ServingCellConfigCommon ::= SEQUENCE {  |                      |                            |          |            |
|   physCellId                            |                      | Physical Cell Identity of  |          |            |
NR Cell 3
| }   |     |     |     |     |
| --- | --- | --- | --- | --- |

Table 7.1.1.12.4.1.3.3-5: ServingCellConfig (Table 7.1.1.12.4.1.3.3-2)
Derivation Path: TS 38.508-1 [4], Table 4.6.3-167 with conditions No_UL and SCell_add
|                                            | Information Element  | Value/remark  | Comment  | Condition  |
| ------------------------------------------ | -------------------- | ------------- | -------- | ---------- |
| ServingCellConfig ::= SEQUENCE {           |                      |               |          |            |
|   downlinkBWP-ToAddModList SEQUENCE (SIZE  |                      |               |          |            |
(1..maxNrofBWPs)) BWP-Downlink {
|     BWP-Downlink                            |     | BWP-Downlink  |     |     |
| ------------------------------------------- | --- | ------------- | --- | --- |
|   }                                         |     |               |     |     |
|   firstActiveDownlinkBWP-Id                 |     | 0             |     |     |
|   dormantBWP-Config-r16 CHOICE {            |     |               |     |     |
|     setup SEQUENCE {                        |     |               |     |     |
|       dormantBWP-Id-r16                     |     | 1             |     |     |
|       outsideActiveTimeConfig-r16 CHOICE {  |     |               |     |     |
|         setup SEQUENCE {                    |     |               |     |     |
ETSI

3GPP TS 38.523-1 version 18.3.0 Release 18  1596  ETSI TS 138 523-1 V18.3.0 (2025-05)
|           firstOutsideActiveTimeBWP-Id-r16    |     | 0   |     |     |
| --------------------------------------------- | --- | --- | --- | --- |
|           dormancyGroupOutsideActiveTime-r16  |     | 0   |     |     |
|         }                                     |     |     |     |     |
|       }                                       |     |     |     |     |
|     }                                         |     |     |     |     |
|   }                                           |     |     |     |     |
| }                                             |     |     |     |     |

Table 7.1.1.12.4.1.3.3-6: BWP-Downlink (Table 7.1.1.12.4.1.3.3-5)
Derivation Path: TS 38.508-1 [4], Table 4.6.3-9
|                                         | Information Element  | Value/remark  | Comment  | Condition  |
| --------------------------------------- | -------------------- | ------------- | -------- | ---------- |
| BWP-Downlink ::= SEQUENCE {             |                      |               |          |            |
|   bwp-Common SEQUENCE {                 |                      |               |          |            |
|     pdcch-ConfigCommon                  |                      | Not present   |          |            |
|   }                                     |                      |               |          |            |
|   bwp-Dedicated SEQUENCE {              |                      |               |          |            |
|     pdcch-Config CHOICE {               |                      |               |          |            |
|       setup SEQUENCE {                  |                      |               |          |            |
|         controlResourceSetToAddModList  |                      | 1 entry       |          |            |
SEQUENCE(SIZE (1..3)) OF ControlResourceSet {
          ControlResourceSet[1]  ControlResourceSet  TS 38.508-1
default value
|         }                                |     |              |     |     |
| ---------------------------------------- | --- | ------------ | --- | --- |
|         controlResourceSetToReleaseList  |     | Not present  |     |     |
|       }                                  |     |              |     |     |
|     }                                    |     |              |     |     |
|   }                                      |     |              |     |     |
| }                                        |     |              |     |     |

7.1.1.12.4.2  DRX adaptation / SCell dormancy indication / Intra-band non Contiguous CA
The scope and description of the present TC is the same as test case 7.1.1.12.4.1 with the following differences:
-  CA configuration: Intra-band non-Contiguous CA replaces Intra-band Contiguous CA
7.1.1.12.4.3  DRX adaptation / SCell dormancy indication / Inter-band CA
The scope and description of the present TC is the same as test case 7.1.1.12.4.1 with the following differences:
-  CA configuration: Inter-band CA replaces Intra-band Contiguous CA
-  Cells configuration: NR Cell 10 replaces NR Cell 3
| 7.1.1.13      | Small Data Transmission (SDT)            |     |     |     |
| ------------- | ---------------------------------------- | --- | --- | --- |
| 7.1.1.13.1    | RA Based SDT / 2-step RACH / Successful  |     |     |     |
| 7.1.1.13.1.1  | Test Purpose (TP)                        |     |     |     |
(1)
with { UE in NR RRC_INACTIVE state and SDT-CG-Config-r17 is not configured and Random Access
resources for 2-step RA-SDT are configured }
ensure that {
  when { UE has small data to transmit and the data volume of the pending UL data across all RBs
configured for SDT is less than or equal to sdt-DataVolumeThreshold and RSRP is above the configured
sdt-RSRP-Threshold }
    then { UE shall initiate 2-step RA based SDT procedure }
            }

ETSI

3GPP TS 38.523-1 version 18.3.0 Release 18 1597 ETSI TS 138 523-1 V18.3.0 (2025-05)
(2)
with { UE in NR RRC_INACTIVE state and SDT-CG-Config-r17 is not configured and Random Access
resources for 2-step RA-SDT are configured }
ensure that {
when { UE has small data to transmit and the data volume of the pending UL data across all RBs
configured for SDT is greater than sdt-DataVolumeThreshold and RSRP is above the configured sdt-
RSRP-Threshold }
then { UE shall not initiate RA based SDT procedure and starts normal RRC Resume procedure }
}
(3)
with { UE in NR RRC_INACTIVE state and SDT-CG-Config-r17 is not configured and Random Access
resources for RA-SDT are configured }
ensure that {
when { UE initiates RA based SDT procedure }
then { UE is successfully able to send and receive subsequent SDT data }
}
(4)
with { UE in NR RRC_INACTIVE state and SDT-CG-Config-r17 is not configured and Random Access
resources for 2-step RA-SDT are configured }
ensure that {
when { UE has small data to transmit and the data volume of the pending UL data across all RBs
configured for SDT is less than or equal sdt-DataVolumeThreshold and RSRP is below the configured
sdt-RSRP-Threshold }
then { UE shall not initiate RA based SDT procedure and starts normal RRC Resume procedure }
}
7.1.1.13.1.2 Conformance requirements
References: The conformance requirements covered in the present TC are specified in: 3GPP TS 38.321, clause 5.1.1b,
5.1.1c and 5.27. Unless otherwise stated these are Rel-17 requirements.
[TS 38.321, clause 5.1.1b]
The MAC entity shall:
1> if the BWP selected for Random Access procedure is configured with both set(s) of Random Access resources
with MSG3 repetition indication and set(s) of Random Access resources without MSG3 repetition indication and
the RSRP of the downlink pathloss reference is less than rsrp-ThresholdMsg3; or
1> if the BWP selected for Random Access procedure is only configured with the set(s) of Random Access
resources with MSG3 repetition indication:
2> assume MSG3 repetition is applicable for the current Random Access procedure.
1> else:
2> assume MSG3 repetition is not applicable for the current Random Access procedure.
NOTE 1: Void.
1> if contention-free Random Access Resources have not been provided for this Random Access procedure and one
or more of the features including RedCap and/or a specific NSAG(s) and/or SDT and/or MSG3 repetition is
applicable for this Random Access procedure:
NOTE 2: The applicability of SDT is determined by MAC entity according to clause 5.27. The applicability of
specific NSAG(s) is determined by upper layers when the Random Access procedure is initiated. The
applicability of RedCap is also determined by upper layers when Random Access procedure is initiated
and it is applicable to the Random Access procedures initiated by PDCCH orders and any Random
Access procedure initiated by the MAC entity.
2> if none of the sets of Random Access resources are available for any feature applicable to the current
Random Access procedure (as specified in clause 5.1.1c):
ETSI

3GPP TS 38.523-1 version 18.3.0 Release 18 1598 ETSI TS 138 523-1 V18.3.0 (2025-05)
3> select the set(s) of Random Access resources that are not associated with any feature indication (as
specified in clause 5.1.1c) for this Random Access procedure.
2> else if there is one set of Random Access resources available which can be used for indicating all features
triggering this Random Access procedure:
3> select this set of Random Access resources for this Random Access procedure.
2> else (i.e. there are one or more sets of Random Access resources available that are configured with
indication(s) for a subset of all features triggering this Random Access procedure):
3> select a set of Random Access resources from the available set(s) of Random Access resources based on
the priority order indicated by upper layers as specified in clause 5.1.1d for this Random Access
Procedure.
1> else if contention-free Random Access Resources have been provided for this Random Access procedure and
RedCap is applicable for the current Random Access procedure and there is one set of Random Access resources
available that is only configured with RedCap indication:
2> select this set of Random Access resources for this Random Access procedure.
1> else:
2> select the set of Random Access resources that are not associated with any feature indication (as specified in
clause 5.1.1c) for the current Random Access procedure.
[TS 38.321, clause 5.1.1c]
The MAC entity shall for each set of configured Random Access resources for 4-step RA type and for each set of
configured Random Access resources for 2-step RA type:
1> if redCap is set to true for a set of Random Access resources:
2> consider the set of Random Access resources as not available for a Random Access procedure for which RedCap is
not applicable.
1> if smallData is set to true for a set of Random Access resources:
2> consider the set of Random Access resources as not available for the Random Access procedure which is not
triggered for RA-SDT.
1> if NSAG-List is configured for a set of Random Access resources:
2> consider the set of Random Access resources as not available for the Random Access procedure unless it is triggered
for any one of the NSAG-ID(s) in the NSAG-List.
1> if msg3-Repetitions is set to true for a set of Random Access resources:
2> consider the set of Random Access resources as not available for the Random Access procedure if Msg3 repetition is
not applicable.
1> if a set of Random Access resources is not configured with FeatureCombination:
2> consider the set of Random Access resources to not associated with any feature.
[TS 38.321, clause 5.27]
The MAC entity may be configured by RRC with SDT and the SDT procedure may be initiated by RRC layer. The
SDT procedure can be performed either by Random Access procedure with 2-step RA type or 4-step RA type (i.e., RA-
SDT) or by configured grant Type 1 (i.e., CG-SDT).…
If RA-SDT is selected above and after the Random Access procedure is successfully completed (see clause 5.1.6), the
UE monitors PDCCH addressed to C-RNTI received in random access response until the RA-SDT procedure is
terminated. If CG-SDT is selected above and after the initial transmission for CG-SDT is performed, the UE monitors
PDCCH addressed to C-RNTI as stored in UE Inactive AS context as specified in TS 38.331 [5] and CS-RNTI until the
CG-SDT procedure is terminated.
ETSI

3GPP TS 38.523-1 version 18.3.0 Release 18  1599  ETSI TS 138 523-1 V18.3.0 (2025-05)
| 7.1.1.13.1.3    | Test description     |     |     |     |
| --------------- | -------------------- | --- | --- | --- |
| 7.1.1.13.1.3.1  | Pre-test conditions  |     |     |     |
System Simulator:
-  NR Cell 1.
UE:
-  None.
Preamble:
-  The UE is in state 3N-A and Test Mode Activated according to TS 38.508-1 [4] Table 4.4A.2-3 with UE test
loop mode B is established with IP PDU delay set to 6 seconds. IF pc_logicalChannelSR_DelayTimer the DRB
is configured according to Table 7.1.1.13.1.3.1-1 for SDT operation.
Table 7.1.1.13.1.3.1-1: Logical Channel Configuration Settings
|     | Parameter                           | SDT DRB  |     |     |
| --- | ----------------------------------- | -------- | --- | --- |
|     | logicalChannelSR-DelayTimerApplied  | True     |     |     |
|     | logicalChannelSR-DelayTimer         | sf512    |     |     |

| 7.1.1.13.1.3.2  | Test procedure sequence  |     |     |     |
| --------------- | ------------------------ | --- | --- | --- |
Table 7.1.1.13.1.3.2-1: Main behaviour
| St  | Procedure  | Message Sequence  |          | TP  Verdict  |
| --- | ---------- | ----------------- | -------- | ------------ |
|     |            | U - S             | Message  |              |
1  SS transmits a downlink assignment including  <--  (PDCCH (C-RNTI))  -  -
the C-RNTI assigned to the UE
2  SS transmits in the indicated downlink  <--  MAC PDU  -  -
assignment a RLC PDU in a MAC PDU on the
DRB configured with SDT (SDT Data > sdt-
DataVolumeThreshold).
3  The SS transmits an RRCRelease message  <--  NR RRC: RRCRelease  -  -
including sdt-Config-r17 in suspendConfig.
4  Check: Does UE transmit MSGA using  -->  MAC PDU (including   2  P
preamble on PRACH after IP PDU Delay  NR RRC: RRCResumeRequest
| expires?  |     | )   |     |     |
| --------- | --- | --- | --- | --- |
5   The SS transmits a MSGB including a  <--  MAC PDU (successRAR)  -  -
successRAR MAC subPDU containing
matching Contention Resolution Identity, C-
RNTI and Timing Advance Command.
6  The SS transmits an RRCResume message.  <--  NR RRC: RRCResume  -  -
| -  EXCEPTION: Steps 7 and 8 can happen in  |     | -  -  |     | -  -  |
| ------------------------------------------ | --- | ----- | --- | ----- |
any order
7  The UE transmits an RRCResumeComplete  -->  NR RRC: RRCResumeComplete  -  -
message.
8  Check: Does the UE transmit a MAC PDU  -->  MAC PDU (containing 1 MAC sub  2  P
| containing Loop backed PDU?  |     | PDU containing RLC SDU)  |     |     |
| ---------------------------- | --- | ------------------------ | --- | --- |
9  The SS transmits an OPEN UE TEST LOOP  <--  TC: OPEN UE TEST LOOP  -  -
message.
10  The UE transmits an OPEN UE TEST LOOP  -->  TC: OPEN UE TEST LOOP  -  -
| COMPLETE message.  |     | COMPLETE  |     |     |
| ------------------ | --- | --------- | --- | --- |
11  SS transmits a CLOSE UE TEST LOOP  <--  TC: CLOSE UE TEST LOOP  -  -
message.
12  The UE transmits a CLOSE UE TEST LOOP  -->  TC: CLOSE UE TEST LOOP  -  -
| COMPLETE message.  |     | COMPLETE  |     |     |
| ------------------ | --- | --------- | --- | --- |
13  SS transmits a downlink assignment including  <--  (PDCCH (C-RNTI))  -  -
the C-RNTI assigned to the UE
14  SS transmits in the indicated downlink  <--  MAC PDU  -  -
ETSI

3GPP TS 38.523-1 version 18.3.0 Release 18 1600 ETSI TS 138 523-1 V18.3.0 (2025-05)
assignment a RLC PDU in a MAC PDU on the
DRB configured with SDT (SDT Data < sdt-
DataVolumeThreshold).
15 The SS transmits an RRCRelease message <-- NR RRC: RRCRelease - -
including sdt-Config-r17 in suspendConfig.
16 Check: Does UE transmit MSGA using --> MAC PDU (including 1 P
preamble on PRACH and associated PUSCH NR RRC: RRCResumeRequest,
resource containing RLC PDU on DRB with RLC PDU on DRB with SDT
SDT configured after IP PDU Delay expires? configured)
17 The SS transmits a MSGB including a <-- MAC PDU (successRAR) - -
successRAR MAC subPDU containing
matching Contention Resolution Identity, C-
RNTI and Timing Advance Command.
- EXCEPTION: Steps 17a1 to 17a3 describe - - - -
behaviour that depends on the UE capability.
17a1 IF pc_logicalChannelSR_DelayTimer THEN <-- MAC PDU
SS transmits in the indicated downlink
assignment a RLC PDU in a MAC PDU on the
DRB configured with SDT (SDT Data <= sdt-
DataVolumeThreshold).
17a2 SS transmits an UL Grant, allowing the UE to <-- (UL Grant (C-RNTI)) - -
return the RLC SDU as received in step 17a1,
on PDCCH with the C-RNTI assigned to the
UE.
17a3 Check: Does the UE transmit a MAC PDU --> MAC PDU 3 P
including one RLC SDU?
17A The SS transmits an RRCResume message to <-- NR RRC: RRCResume - -
bring UE to RRC_CONNECTED State.
17B The UE transmits an RRCResumeComplete --> NR RRC: RRCResumeComplete - -
message.
18 The SS changes the parameter ‘sdt-RSRP- - - - -
Threshold-r17’ in SIB1 of NR Cell 1 to 76 and
starts broadcasting updated SIB1.
Note: This value should result in meeting
condition ‘RSRP is below the configured sdt-
RSRP-Threshold’
19 The SS transmits an OPEN UE TEST LOOP <-- TC: OPEN UE TEST LOOP - -
message.
20 The UE transmits an OPEN UE TEST LOOP --> TC: OPEN UE TEST LOOP - -
COMPLETE message. COMPLETE
21 SS transmits a CLOSE UE TEST LOOP <-- TC: CLOSE UE TEST LOOP - -
message.
22 The UE transmits a CLOSE UE TEST LOOP --> TC: CLOSE UE TEST LOOP - -
COMPLETE message. COMPLETE
23 SS transmits a downlink assignment including <-- (PDCCH (C-RNTI)) - -
the C-RNTI assigned to the UE
24 SS transmits in the indicated downlink <-- MAC PDU - -
assignment a RLC PDU in a MAC PDU on the
DRB configured with SDT (SDT Data < sdt-
DataVolumeThreshold).
25 The SS transmits an RRCRelease message <-- NR RRC: RRCRelease - -
including sdt-Config-r17 in suspendConfig.
26 Check: Does UE transmit MSGA using --> MAC PDU (including 4 P
preamble on PRACH after IP PDU Delay NR RRC: RRCResumeRequest)
expires?
27 The SS transmits a MSGB including a <-- MAC PDU (successRAR) - -
successRAR MAC subPDU containing
matching Contention Resolution Identity, C-
RNTI and Timing Advance Command.
28 The SS transmits an RRCResume message. <-- NR RRC: RRCResume - -
- Exception: Steps 29 and 30 can happen in any - - - -
order
29 The UE transmits an RRCResumeComplete --> NR RRC: RRCResumeComplete - -
message.
30 Check: Does the UE transmit a MAC PDU --> MAC PDU (containing 1 MAC sub 4 P
containing Loop backed PDU? PDU containing RLC SDU)
31 The SS transmits an RRCRelease message. <-- NR RRC: RRCRelease - -
ETSI

3GPP TS 38.523-1 version 18.3.0 Release 18  1601  ETSI TS 138 523-1 V18.3.0 (2025-05)

| 7.1.1.13.1.3.3  | Specific message contents  |     |     |     |
| --------------- | -------------------------- | --- | --- | --- |
Table 7.1.1.13.1.3.3-1: CLOSE UE TEST LOOP (Steps 11, 21 and preamble Table 7.1.1.13.1.3.2-1 )
Derivation Path: TS 36.508-1 [7] table 4.7A-3 condition UE test loop mode B
|                               | Information Element  | Value/Remark  | Comment    | Condition  |
| ----------------------------- | -------------------- | ------------- | ---------- | ---------- |
| UE test loop mode B LB setup  |                      |               |            |            |
|   IP PDU delay                |                      | '0000 0110'B  | 6 seconds  |            |

Table 7.1.1.13.1.3.3-2: SIB1 (preamble and step 18, Table 7.1.1.13.1.3.2-1)
Derivation path: TS 38.508-1 [4] Table 4.6.1-28 with Condition SDT
|                                                | Information Element  | Value/Remark          | Comment           | Condition  |
| ---------------------------------------------- | -------------------- | --------------------- | ----------------- | ---------- |
| SIB1 ::= SEQUENCE {                            |                      |                       |                   |            |
|   servingCellConfigCommon                      |                      | ServingCellConfigComm | Table             |            |
|                                                |                      | on                    | 7.1.1.13.1.3.3-3  |            |
|   nonCriticalExtension SEQUENCE {              |                      |                       |                   |            |
|     nonCriticalExtension SEQUENCE {            |                      |                       |                   |            |
|       nonCriticalExtension SEQUENCE {          |                      |                       |                   |            |
|         sdt-ConfigCommon-r17 SEQUENCE {        |                      |                       |                   |            |
|           sdt-RSRP-Threshold-r17               |                      | 66 (-90dBm)           |                   | Preamble   |
|                                                |                      | 76 (-80dBm)           |                   | Step 18    |
|           sdt-LogicalChannelSR-DelayTimer-r17  |                      | sf512                 |                   |            |
|           sdt-DataVolumeThreshold-r17          |                      | byte32                |                   |            |
|         }                                      |                      |                       |                   |            |
|       }                                        |                      |                       |                   |            |
|     }                                          |                      |                       |                   |            |
|   }                                            |                      |                       |                   |            |
| }                                              |                      |                       |                   |            |

Table 7.1.1.13.1.3.3-3: ServingCellConfigCommon (Table 7.1.1.13.1.3.3-2)
Derivation Path: TS 38.508-1 [4], Table 4.6.3-168
|                                         | Information Element  | Value/remark      | Comment  | Condition  |
| --------------------------------------- | -------------------- | ----------------- | -------- | ---------- |
| ServingCellConfigCommon ::= SEQUENCE {  |                      |                   |          |            |
|   uplinkConfigCommon SEQUENCE {         |                      |                   |          |            |
|     initialUplinkBWP                    |                      | BWP-UplinkCommon  | Table    |            |
7.1.1.13.1.3.3-4
|   }  |     |     |     |     |
| ---- | --- | --- | --- | --- |
| }    |     |     |     |     |

Table 7.1.1.13.1.3.3-4: BWP-UplinkCommon (Table 7.1.1.13.1.3.3-3)
| Derivation Path: TS 38.508-1 [4], Table 4.6.3-14  |                      |                    |                  |            |
| ------------------------------------------------- | -------------------- | ------------------ | ---------------- | ---------- |
|                                                   | Information Element  | Value/remark       | Comment          | Condition  |
| BWP-UplinkCommon ::= SEQUENCE {                   |                      |                    |                  |            |
|   msgA-ConfigCommon-r16 CHOICE {                  |                      |                    |                  |            |
|     setup                                         |                      | MsgA-ConfigCommon  | TS 38.508-1 [4]  |            |
Table 4.6.3-81A
|   }                                         |     |                    |                   |     |
| ------------------------------------------- | --- | ------------------ | ----------------- | --- |
|   AdditionalRACH-ConfigList-r17 SEQUENCE {  |     |                    |                   |     |
|     AdditionalRACH-Config-r17 SEQUENCE {    |     |                    |                   |     |
|       rach-ConfigCommon-r17                 |     | Not present        |                   |     |
|       msgA-ConfigCommon-r17                 |     | MsgA-ConfigCommon- | Table             |     |
|                                             |     | r16                | 7.1.1.13.1.3.3-5  |     |
|     }                                       |     |                    |                   |     |
|   }                                         |     |                    |                   |     |
| }                                           |     |                    |                   |     |

ETSI

3GPP TS 38.523-1 version 18.3.0 Release 18  1602  ETSI TS 138 523-1 V18.3.0 (2025-05)
Table 7.1.1.13.1.3.3-5: MsgA-ConfigCommon-r16 (Table 7.1.1.13.1.3.3-4)
Derivation Path: TS 38.508-1 [4], Table 4.6.3-81A
|                                        | Information Element  | Value/remark        | Comment           | Condition  |
| -------------------------------------- | -------------------- | ------------------- | ----------------- | ---------- |
| MsgA-ConfigCommon-r16 :: = SEQUENCE {  |                      |                     |                   |            |
|   rach-ConfigCommonTwoStepRA-r16       |                      | RACH-               | Table             |            |
|                                        |                      | ConfigCommonTwoStep | 7.1.1.13.1.3.3-6  |            |
RA-r16
| }   |     |     |     |     |
| --- | --- | --- | --- | --- |

Table 7.1.1.13.1.3.3-6: RACH-ConfigCommonTwoStepRA-r16 (Table 7.1.1.13.1.3.3-5)
Derivation Path: TS 38.508-1 [4], Table 4.6.3-128A
|                                     | Information Element  | Value/remark  | Comment  | Condition  |
| ----------------------------------- | -------------------- | ------------- | -------- | ---------- |
| RACH-ConfigCommonTwoStepRA-r16 ::=  |                      |               |          |            |
SEQUENCE {
|   featureCombinationPreamblesList-r17 SEQUENCE  |     |     |     |     |
| ----------------------------------------------- | --- | --- | --- | --- |
(SIZE(1..maxFeatureCombPreamblesPerRACHReso
urce-r17)) OF FeatureCombinationPreambles-r17 {
    FeatureCombinationPreambles-r17  FeatureCombinationPrea Table
|      |     | mbles  | 7.1.1.13.1.3.3-7  |     |
| ---- | --- | ------ | ----------------- | --- |
|   }  |     |        |                   |     |
| }    |     |        |                   |     |

Table 7.1.1.13.1.3.3-7: FeatureCombinationPreambles (Table 7.1.1.13.1.3.3-6)
Derivation Path:  TS 38.508-1 [4], Table 4.6.3-56E
|                                                 | Information Element  | Value/remark  | Comment   | Condition  |
| ----------------------------------------------- | -------------------- | ------------- | --------- | ---------- |
| FeatureCombinationPreambles-r17 ::= SEQUENCE {  |                      |               |           |            |
|   featureCombination-r17 ::= SEQUENCE {         |                      |               |           |            |
|     smallData-r17                               |                      | true          |           |            |
|   }                                             |                      |               |           |            |
|   startPreambleForThisPartition-r17             |                      | 8             | Randomly  |            |
selected
|   numberOfPreamblesPerSSB-ForThisPartition-r17  |     | 12                 |        |     |
| ----------------------------------------------- | --- | ------------------ | ------ | --- |
|   ssb-SharedRO-MaskIndex-r17                    |     | Not present        |        |     |
|   groupBconfigured-r17                          |     | Not present        |        |     |
|   separateMsgA-PUSCH-Config-r17                 |     | MsgA-PUSCH-Config  | Table  |     |
7.1.1.13.1.3.3-8
|   msgA-RSRP-Threshold-r17  |     | 57           | -100 dBm         |     |
| -------------------------- | --- | ------------ | ---------------- | --- |
|   rsrp-ThresholdSSB-r17    |     | RSRP-Range   | TS 38.508-1 [4]  |     |
table 4.6.3-152
|   deltaPreamble-r17   |     | Not present  |     |     |
| --------------------- | --- | ------------ | --- | --- |
| }                     |     |              |     |     |

Table 7.1.1.13.1.3.3-8: MsgA-PUSCH-Config (Table 7.1.1.13.1.3.3-7)
Derivation Path: TS 38.508-1 [4], Table 4.6.3-81B
|                                             | Information Element  | Value/remark  | Comment  | Condition  |
| ------------------------------------------- | -------------------- | ------------- | -------- | ---------- |
| MsgA-PUSCH-Config-r16 ::= SEQUENCE {        |                      |               |          |            |
|   msgA-PUSCH-ResourceGroupA-r16 SEQUENCE {  |                      |               |          |            |
|     msgA-MCS-r16                            |                      | 1             |          |            |
|     nrofPRBs-PerMsgA-PO-r16                 |                      | 15            |          |            |
|   }                                         |                      |               |          |            |
| }                                           |                      |               |          |            |

Table 7.1.1.13.1.3.3-9: RRCRelease (Steps 3, 15 and 25 Table 7.1.1.13.2.3.2-1)
Derivation Path: TS 38.508-1 [4] table 4.6.1-16 with condition NR_RRC_INACTIVE and SDT
| RRCRelease ::= SEQUENCE {  |     |     |     |     |
| -------------------------- | --- | --- | --- | --- |
ETSI

3GPP TS 38.523-1 version 18.3.0 Release 18  1603  ETSI TS 138 523-1 V18.3.0 (2025-05)
|   criticalExtensions CHOICE {                |          |     |     |
| -------------------------------------------- | -------- | --- | --- |
|     rrcRelease SEQUENCE {                    |          |     |     |
|       suspendConfig SEQUENCE {               |          |     |     |
|         sdt-Config-r17 CHOICE {              |          |     |     |
|           setup SEQUENCE {                   |          |     |     |
|             sdt-DRB-List-r17 SEQUENCE (SIZE  | 1 entry  |     |     |
(0..maxDRB)) OF DRB-Identity {
              DRB-Identity[1]  DRB-Identity using  Entry 1
|     | condition DRBj  | j is the ID of the  |     |
| --- | --------------- | ------------------- | --- |
DRB established
during the
preamble which is
allocated
according to
internal TTCN
mapping
|             }                          |              |     |     |
| -------------------------------------- | ------------ | --- | --- |
|             sdt-SRB2-Indication-r17    | Not present  |     |     |
|             sdt-MAC-PHY-CG-Config-r17  | Not present  |     |     |
|           }                            |              |     |     |
|         }                              |              |     |     |
|       }                                |              |     |     |
|     }                                  |              |     |     |
|   }                                    |              |     |     |
| }                                      |              |     |     |

7.1.1.13.2  RA Based SDT / 4-step RACH / Successful
7.1.1.13.2.1  Test Purpose (TP)
(1)
with { UE in NR RRC_INACTIVE state and SDT-CG-Config-r17 is not configured and Random Access
resources for RA-SDT are configured }
ensure that {
  when { UE has small data to transmit and the data volume of the pending UL data across all RBs
configured for SDT is less than or equal to sdt-DataVolumeThreshold and RSRP is above the configured
sdt-RSRP-Threshold }
    then { UE shall initiate 4-step RA based SDT procedure }
            }

(2)
with { UE in NR RRC_INACTIVE state and SDT-CG-Config-r17 is not configured and Random Access
resources for RA-SDT are configured }
ensure that {
  when { UE has small data to transmit and the data volume of the pending UL data across all RBs
configured for SDT is greater than sdt-DataVolumeThreshold and RSRP is above the configured sdt-
RSRP-Threshold }
    then { UE shall not initiate RA based SDT procedure and starts normal RRC Resume procedure }
            }

(3)
with { UE in NR RRC_INACTIVE state and SDT-CG-Config-r17 is configured and Random Access resources
for RA-SDT are configured }
ensure that {
  when { UE initiates RA based SDT procedure }
    then { UE is successfully able to send and receive subsequent SDT data }
            }

(4)
with { UE in NR RRC_INACTIVE state and SDT-CG-Config-r17 is not configured and Random Access
resources for RA-SDT are configured }
ensure that {
  when { UE has small data to transmit and the data volume of the pending UL data across all RBs
ETSI

3GPP TS 38.523-1 version 18.3.0 Release 18 1604 ETSI TS 138 523-1 V18.3.0 (2025-05)
configured for SDT is less than or equal to sdt-DataVolumeThreshold and RSRP is below the configured
sdt-RSRP-Threshold }
then { UE shall not initiate RA based SDT procedure and starts normal RRC Resume procedure }
}
7.1.1.13.2.2 Conformance requirements
References: The conformance requirements covered in the present TC are specified in: 3GPP TS 38.321, clause 5.1.1b,
5.1.1c, 5.4.4 and 5.27. Unless otherwise stated these are Rel-17 requirements.
[TS 38.321, clause 5.1.1b]
The MAC entity shall:
1> if the BWP selected for Random Access procedure is configured with both set(s) of Random Access resources
with MSG3 repetition indication and set(s) of Random Access resources without MSG3 repetition indication and
the RSRP of the downlink pathloss reference is less than rsrp-ThresholdMsg3; or
1> if the BWP selected for Random Access procedure is only configured with the set(s) of Random Access
resources with MSG3 repetition indication:
2> assume MSG3 repetition is applicable for the current Random Access procedure.
1> else:
2> assume MSG3 repetition is not applicable for the current Random Access procedure.
NOTE 1: Void.
1> if contention-free Random Access Resources have not been provided for this Random Access procedure and one
or more of the features including RedCap and/or a specific NSAG(s) and/or SDT and/or MSG3 repetition is
applicable for this Random Access procedure:
NOTE 2: The applicability of SDT is determined by MAC entity according to clause 5.27. The applicability of
specific NSAG(s) is determined by upper layers when the Random Access procedure is initiated. The
applicability of RedCap is also determined by upper layers when Random Access procedure is initiated
and it is applicable to the Random Access procedures initiated by PDCCH orders and any Random
Access procedure initiated by the MAC entity.
2> if none of the sets of Random Access resources are available for any feature applicable to the current
Random Access procedure (as specified in clause 5.1.1c):
3> select the set(s) of Random Access resources that are not associated with any feature indication (as
specified in clause 5.1.1c) for this Random Access procedure.
2> else if there is one set of Random Access resources available which can be used for indicating all features
triggering this Random Access procedure:
3> select this set of Random Access resources for this Random Access procedure.
2> else (i.e. there are one or more sets of Random Access resources available that are configured with
indication(s) for a subset of all features triggering this Random Access procedure):
3> select a set of Random Access resources from the available set(s) of Random Access resources based on
the priority order indicated by upper layers as specified in clause 5.1.1d for this Random Access
Procedure.
1> else if contention-free Random Access Resources have been provided for this Random Access procedure and
RedCap is applicable for the current Random Access procedure and there is one set of Random Access resources
available that is only configured with RedCap indication:
2> select this set of Random Access resources for this Random Access procedure.
1> else:
2> select the set of Random Access resources that are not associated with any feature indication (as specified in
clause 5.1.1c) for the current Random Access procedure.
ETSI

3GPP TS 38.523-1 version 18.3.0 Release 18 1605 ETSI TS 138 523-1 V18.3.0 (2025-05)
[TS 38.321, clause 5.1.1c]
The MAC entity shall for each set of configured Random Access resources for 4-step RA type and for each set of
configured Random Access resources for 2-step RA type:
1> if redCap is set to true for a set of Random Access resources:
2> consider the set of Random Access resources as not available for a Random Access procedure for which
RedCap is not applicable.
1> if smallData is set to true for a set of Random Access resources:
2> consider the set of Random Access resources as not available for the Random Access procedure which is not
triggered for RA-SDT.
1> if NSAG-List is configured for a set of Random Access resources:
2> consider the set of Random Access resources as not available for the Random Access procedure unless it is
triggered for any one of the NSAG-ID(s) in the NSAG-List.
1> if msg3-Repetitions is set to true for a set of Random Access resources:
2> consider the set of Random Access resources as not available for the Random Access procedure if Msg3
repetition is not applicable.
1> if a set of Random Access resources is not configured with FeatureCombination:
2> consider the set of Random Access resources to not associated with any feature.
[TS 38.321, clause 5.27]
The MAC entity may be configured by RRC with SDT and the SDT procedure may be initiated by RRC layer.
The SDT procedure can be performed either by Random Access procedure with 2-step RA type or 4-step RA
type (i.e., RA-SDT) or by configured grant Type 1 (i.e., CG-SDT).
…
If RA-SDT is selected above and after the Random Access procedure is successfully completed (see clause
5.1.6), the UE monitors PDCCH addressed to C-RNTI received in random access response until the RA-SDT
procedure is terminated. If CG-SDT is selected above and after the initial transmission for CG-SDT is
performed, the UE monitors PDCCH addressed to C-RNTI as stored in UE Inactive AS context as specified
in TS 38.331 [5] and CS-RNTI until the CG-SDT procedure is terminated.
7.1.1.13.2.3 Test description
7.1.1.13.2.3.1 Pre-test conditions
System Simulator:
- NR Cell 1.
UE:
- None.
Preamble:
- The UE is in state 3N-A and Test Mode Activated according to TS 38.508-1 [4] Table 4.4A.2-3 with UE test
loop mode B is established IP PDU delay set to 6 seconds. IF pc_logicalChannelSR_DelayTimer the DRB is
configured for SDT operation according to Table 7.1.1.13.2.3.1-1.
Table 7.1.1.13.2.3.1-1: Logical Channel Configuration Settings
Parameter SDT DRB
ETSI

3GPP TS 38.523-1 version 18.3.0 Release 18 1606 ETSI TS 138 523-1 V18.3.0 (2025-05)
logicalChannelSR-DelayTimerApplied True
logicalChannelSR-DelayTimer sf512
7.1.1.13.2.3.2 Test procedure sequence
Table 7.1.1.13.2.3.2-1: Main behaviour
St Procedure Message Sequence TP Verdict
U - S Message
1 SS transmits a downlink assignment including <-- (PDCCH (C-RNTI)) - -
the C-RNTI assigned to the UE
2 SS transmits in the indicated downlink <-- MAC PDU - -
assignment a RLC PDU in a MAC PDU on the
DRB configured with SDT (SDT Data > sdt-
DataVolumeThreshold).
3 The SS transmits an RRCRelease message <-- NR RRC: RRCRelease - -
including sdt-Config-r17 in suspendConfig.
4 Check: Does the UE transmit a preamble on --> PRACH Preamble 2 P
PRACH using a preamble outside of the
SmallData FeatureCombinationPreambles?
5 The SS transmits Random Access Response <-- Random Access Response - -
with RAPID corresponding to the transmitted
Preamble in step 5, including TC-RNTI and not
including Backoff Indicator subheader.
6 Check: Does the UE transmit a MAC PDU --> MAC PDU ( 2 P
containing an RRCResumeRequest message? NR RRC: RRCResumeRequest)
7 The SS schedules PDCCH transmission <-- MAC PDU - -
addressed to TC-RNTI to transmit a valid MAC (UE Contention Resolution
PDU containing ‘UE Contention Resolution Identity MAC CE)
Identity’ MAC control element with matched
‘Contention Resolution Identity’.
8 The SS transmits a RRCResume message. <-- NR RRC: RRCResume - -
- EXCEPTION: Steps 9 and 10 can happen in - - - -
any order
9 The UE transmits a RRCResumeComplete --> NR RRC: RRCResumeComplete - -
message.
10 Check: Does the UE transmit a MAC PDU --> MAC PDU (containing 1 MAC sub 2 P
containing Loop backed PDU? PDU containing RLC SDU)
11 The SS transmits an OPEN UE TEST LOOP <-- TC: OPEN UE TEST LOOP - -
message.
12 The UE transmits an OPEN UE TEST LOOP --> TC: OPEN UE TEST LOOP - -
COMPLETE message. COMPLETE
13 SS transmits a CLOSE UE TEST LOOP <-- TC: CLOSE UE TEST LOOP - -
message.
14 The UE transmits a CLOSE UE TEST LOOP --> TC: CLOSE UE TEST LOOP - -
COMPLETE message. COMPLETE
15 SS transmits a downlink assignment including <-- (PDCCH (C-RNTI)) - -
the C-RNTI assigned to the UE
16 SS transmits in the indicated downlink <-- MAC PDU - -
assignment a RLC PDU in a MAC PDU on the
DRB configured with SDT (SDT Data < sdt-
DataVolumeThreshold).
17 The SS transmits a RRCRelease message <-- NR RRC: RRCRelease - -
including sdt-Config-r17 in suspendConfig.
18 Check: Does the UE transmit a preamble on --> PRACH Preamble 1 P
PRACH using a preamble in the SmallData
FeatureCombinationPreambles?
19 The SS transmits Random Access Response <-- Random Access Response - -
with RAPID corresponding to the transmitted
Preamble in step 19, including TC-RNTI and
not including Backoff Indicator subheader.
20 Check: Does the UE transmit a MAC PDU --> MAC PDU ( 1 P
containing an RRCResumeRequest message NR RRC: RRCResumeRequest,
and RLC PDU on DRB with SDT configured? RLC PDU on DRB with SDT
configured)
ETSI

3GPP TS 38.523-1 version 18.3.0 Release 18 1607 ETSI TS 138 523-1 V18.3.0 (2025-05)
21 The SS schedules PDCCH transmission <-- MAC PDU - -
addressed to TC-RNTI to transmit a valid MAC (UE Contention Resolution
PDU containing ‘UE Contention Resolution Identity MAC CE)
Identity’ MAC control element with matched
Contention Resolution Identity’.
- EXCEPTION: Steps 22a1-22a3 describe - - - -
behaviour that depends on UE configuration;
the "lower case letter" identifies a step
sequence that takes place if
pc_logicalChannelSR_DelayTimer is
configured
22a1 IF pc_logicalChannelSR_DelayTimer THEN <-- MAC PDU
SS transmits in the indicated downlink
assignment a RLC PDU in a MAC PDU on the
DRB configured with SDT (SDT Data <= sdt-
DataVolumeThreshold).
22a2 SS transmits an UL Grant, allowing the UE to <-- (UL Grant (C-RNTI)) - -
return the RLC SDU as received in step 22a1,
on PDCCH with the C-RNTI assigned to the
UE.
22a3 Check: Does the UE transmit a MAC PDU --> MAC PDU 3 P
including one RLC SDU?
23 The SS transmits an RRCResume message to <-- NR RRC: RRCResume - -
bring UE to RRC_CONNECTED State.
24 The UE transmits an RRCResumeComplete --> NR RRC: RRCResumeComplete - -
message.
25 The SS changes the parameter ‘sdt-RSRP- - - - -
Threshold-r17’ in SIB1 of NR Cell 1 to 76 and
starts broadcasting updated SIB1.
Note: This value should result in meeting
condition ‘RSRP is below the configured sdt-
RSRP-Threshold’
26 The SS transmits an OPEN UE TEST LOOP <-- TC: OPEN UE TEST LOOP - -
message.
27 The UE transmits an OPEN UE TEST LOOP --> TC: OPEN UE TEST LOOP - -
COMPLETE message. COMPLETE
28 SS transmits a CLOSE UE TEST LOOP <-- TC: CLOSE UE TEST LOOP - -
message.
29 The UE transmits a CLOSE UE TEST LOOP --> TC: CLOSE UE TEST LOOP - -
COMPLETE message. COMPLETE
30 SS transmits a downlink assignment including <-- (PDCCH (C-RNTI)) - -
the C-RNTI assigned to the UE
31 SS transmits in the indicated downlink <-- MAC PDU - -
assignment a RLC PDU in a MAC PDU on the
DRB configured with SDT (SDT Data < sdt-
DataVolumeThreshold).
32 The SS transmits a RRCRelease message <-- NR RRC: RRCRelease - -
including sdt-Config-r17 in suspendConfig.
33 The UE transmits a preamble on PRACH --> PRACH Preamble - -
34 The SS transmits Random Access Response <-- Random Access Response - -
with RAPID corresponding to the transmitted
Preamble in step 5, including TC-RNTI and not
including Backoff Indicator subheader.
35 Check: Does the UE transmit a MAC PDU --> MAC PDU ( 4 P
containing an RRCResumeRequest message? NR RRC: RRCResumeRequest)
36 The SS schedules PDCCH transmission <-- MAC PDU - -
addressed to TC-RNTI to transmit a valid MAC (UE Contention Resolution
PDU containing ‘UE Contention Resolution Identity MAC CE)
Identity’ MAC control element with matched
‘Contention Resolution Identity’.
37 The SS transmits a RRCResume message. <-- NR RRC: RRCResume - -
- EXCEPTION: Steps 38 and 39 can happen in - - - -
any order
38 The UE transmits a RRCResumeComplete --> NR RRC: RRCResumeComplete - -
message.
39 Check: Does the UE transmit a MAC PDU --> MAC PDU (containing 1 MAC sub 2 P
containing Loop backed PDU? PDU containing RLC SDU)
ETSI

3GPP TS 38.523-1 version 18.3.0 Release 18  1608  ETSI TS 138 523-1 V18.3.0 (2025-05)
40  The SS transmits a RRCRelease message   <--  NR RRC: RRCRelease  -  -

| 7.1.1.13.2.3.3  | Specific message contents  |     |     |     |
| --------------- | -------------------------- | --- | --- | --- |
Table 7.1.1.13.2.3.3-1: CLOSE UE TEST LOOP (Steps 13, 28 and preamble Table 7.1.1.13.2.3.2-1)
Derivation Path: TS 36.508 [7] table 4.7A-3 condition UE test loop mode B
|                               | Information Element  | Value/Remark  | Comment    | Condition  |
| ----------------------------- | -------------------- | ------------- | ---------- | ---------- |
| UE test loop mode B LB setup  |                      |               |            |            |
|   IP PDU delay                |                      | '0000 0110'B  | 6 seconds  |            |

Table 7.1.1.13.2.3.3-2: SIB1 (preamble and step 25, Table 7.1.1.13.2.3.2-1)
Derivation path: TS 38.508-1 [4] Table 4.6.1-28 with condition SDT
|                                                | Information Element  | Value/Remark          | Comment           | Condition  |
| ---------------------------------------------- | -------------------- | --------------------- | ----------------- | ---------- |
| SIB1 ::= SEQUENCE {                            |                      |                       |                   |            |
|   servingCellConfigCommon                      |                      | ServingCellConfigComm | Table             |            |
|                                                |                      | on                    | 7.1.1.13.2.3.3-3  |            |
|   nonCriticalExtension SEQUENCE {              |                      |                       |                   |            |
|     nonCriticalExtension SEQUENCE {            |                      |                       |                   |            |
|       nonCriticalExtension SEQUENCE {          |                      |                       |                   |            |
|         sdt-ConfigCommon-r17 SEQUENCE {        |                      |                       |                   |            |
|           sdt-RSRP-Threshold-r17               |                      | 66 (-90dBm)           |                   | Preamble   |
|                                                |                      | 76 (-80dBm)           |                   | Step 23    |
|           sdt-LogicalChannelSR-DelayTimer-r17  |                      | sf512                 |                   |            |
|           sdt-DataVolumeThreshold-r17          |                      | byte32                |                   |            |
|         }                                      |                      |                       |                   |            |
|       }                                        |                      |                       |                   |            |
|     }                                          |                      |                       |                   |            |
|   }                                            |                      |                       |                   |            |
| }                                              |                      |                       |                   |            |

Table 7.1.1.13.2.3.3-3: ServingCellConfigCommon (Table 7.1.1.13.2.3.3-2)
Derivation Path: TS 38.508-1 [4], Table 4.6.3-168
|                                         | Information Element  | Value/remark          | Comment  | Condition  |
| --------------------------------------- | -------------------- | --------------------- | -------- | ---------- |
| ServingCellConfigCommon ::= SEQUENCE {  |                      |                       |          |            |
|   downlinkConfigCommon                  |                      | DownlinkConfigCommon  | Table    |            |
7.1.1.13.2.3.3-7
|   uplinkConfigCommon SEQUENCE {  |     |                   |        |     |
| -------------------------------- | --- | ----------------- | ------ | --- |
|     initialUplinkBWP             |     | BWP-UplinkCommon  | Table  |     |
7.1.1.13.2.3.3-4
|   }  |     |     |     |     |
| ---- | --- | --- | --- | --- |
| }    |     |     |     |     |

Table 7.1.1.13.2.3.3-4: BWP-UplinkCommon (Table 7.1.1.13.2.3.3-3)
| Derivation Path: TS 38.508-1 [4], Table 4.6.3-14  |                      |               |          |            |
| ------------------------------------------------- | -------------------- | ------------- | -------- | ---------- |
|                                                   | Information Element  | Value/remark  | Comment  | Condition  |
| BWP-UplinkCommon ::= SEQUENCE {                   |                      |               |          |            |
|   AdditionalRACH-ConfigList-r17 SEQUENCE          |                      | 1 entry       |          |            |
(SIZE(1..maxAdditionalRACH-r17)) OF
AdditionalRACH-Config-r17 {
|     AdditionalRACH-Config-r17[1] SEQUENCE {  |     |                    | Entry 1  |     |
| -------------------------------------------- | --- | ------------------ | -------- | --- |
|       rach-ConfigCommon-r17                  |     | RACH-ConfigCommon  | Table    |     |
7.1.1.13.2.3.3-5
|       msgA-ConfigCommon-r17  |     | Not present  |     |     |
| ---------------------------- | --- | ------------ | --- | --- |
|     }                        |     |              |     |     |
|   }                          |     |              |     |     |
| }                            |     |              |     |     |

ETSI

3GPP TS 38.523-1 version 18.3.0 Release 18  1609  ETSI TS 138 523-1 V18.3.0 (2025-05)
Table 7.1.1.13.2.3.3-5: RACH-ConfigCommon (Table 7.1.1.13.2.3.3-4)
Derivation Path: TS 38.508-1 [4], Table 4.6.3-128
|                                                 | Information Element  | Value/remark  | Comment  | Condition  |
| ----------------------------------------------- | -------------------- | ------------- | -------- | ---------- |
| RACH-ConfigCommon::= SEQUENCE {                 |                      |               |          |            |
|   featureCombinationPreamblesList-r17 SEQUENCE  |                      |               |          |            |
(SIZE(1..maxFeatureCombPreamblesPerRACHReso
urce-r17)) OF FeatureCombinationPreambles-r17 {
    FeatureCombinationPreambles-r17  FeatureCombinationPrea Table
|      |     | mbles  | 7.1.1.13.2.3.3-6  |     |
| ---- | --- | ------ | ----------------- | --- |
|   }  |     |        |                   |     |
| }    |     |        |                   |     |

Table 7.1.1.13.2.3.3-6: FeatureCombinationPreambles (Table 7.1.1.13.2.3.3-5)
Derivation Path: TS 38.508-1 [4], Table 4.6.3-56E
|                                                 | Information Element  | Value/remark  | Comment   | Condition  |
| ----------------------------------------------- | -------------------- | ------------- | --------- | ---------- |
| FeatureCombinationPreambles-r17 ::= SEQUENCE {  |                      |               |           |            |
|   featureCombination-r17 ::= SEQUENCE {         |                      |               |           |            |
|     smallData-r17                               |                      | true          |           |            |
|   }                                             |                      |               |           |            |
|   startPreambleForThisPartition-r17             |                      | 8             | Randomly  |            |
selected
|   numberOfPreamblesPerSSB-ForThisPartition-r17  |     | 12           |     |     |
| ----------------------------------------------- | --- | ------------ | --- | --- |
|   ssb-SharedRO-MaskIndex-r17                    |     | Not present  |     |     |
|   groupBconfigured-r17                          |     | Not present  |     |     |
|   separateMsgA-PUSCH-Config-r17                 |     | Not present  |     |     |
|   msgA-RSRP-Threshold-r17                       |     | Not present  |     |     |
|   rsrp-ThresholdSSB-r17                         |     | Not present  |     |     |
|   deltaPreamble-r17                             |     | Not present  |     |     |
| }                                               |     |              |     |     |

Table 7.1.1.13.2.3.3-7: DownlinkConfigCommon (Table 7.1.1.13.2.3.3-3)
Derivation Path: TS 38.508-1 [4] table 4.6.3-52
|                                      | Information Element  | Value/remark        | Comment  | Condition  |
| ------------------------------------ | -------------------- | ------------------- | -------- | ---------- |
| DownlinkConfigCommon ::= SEQUENCE {  |                      |                     |          |            |
|   initialDownlinkBWP                 |                      | BWP-DownlinkCommon  | Table    |            |
7.1.1.13.2.3.3-8
| }   |     |     |     |     |
| --- | --- | --- | --- | --- |

Table 7.1.1.13.2.3.3-8: BWP-DownlinkCommon (Table 7.1.1.13.2.3.3-7)
Derivation Path: TS 38.508-1 [4] table 4.6.3-10
|                                    | Information Element  | Value/remark        | Comment  | Condition  |
| ---------------------------------- | -------------------- | ------------------- | -------- | ---------- |
| BWP-DownlinkCommon ::= SEQUENCE {  |                      |                     |          |            |
|   pdcch-ConfigCommon CHOICE {      |                      |                     |          |            |
|     setup                          |                      | PDCCH-ConfigCommon  |          |            |
with condition SDT
|   }  |     |     |     |     |
| ---- | --- | --- | --- | --- |
| }    |     |     |     |     |

Table 7.1.1.13.2.3.3-9: RRCRelease (Steps 3, 17 and 32 Table 7.1.1.13.2.3.2-1 )
Derivation Path: TS 38.508-1 [4] table 4.6.1-16 with condition NR_RRC_INACTIVE and SDT
| RRCRelease ::= SEQUENCE {        |     |     |     |     |
| -------------------------------- | --- | --- | --- | --- |
|   criticalExtensions CHOICE {    |     |     |     |     |
|     rrcRelease SEQUENCE {        |     |     |     |     |
|       suspendConfig SEQUENCE {   |     |     |     |     |
|         sdt-Config-r17 CHOICE {  |     |     |     |     |
ETSI

3GPP TS 38.523-1 version 18.3.0 Release 18  1610  ETSI TS 138 523-1 V18.3.0 (2025-05)
|           setup SEQUENCE {                   |          |     |     |
| -------------------------------------------- | -------- | --- | --- |
|             sdt-DRB-List-r17 SEQUENCE (SIZE  | 1 entry  |     |     |
(0..maxDRB)) OF DRB-Identity {
              DRB-Identity[1]  DRB-Identity using  Entry 1
|     | condition DRBj  | j is the ID of the  |     |
| --- | --------------- | ------------------- | --- |
DRB established
during the
preamble which is
allocated
according to
internal TTCN
mapping
|             }                          |              |     |     |
| -------------------------------------- | ------------ | --- | --- |
|             sdt-SRB2-Indication-r17    | Not present  |     |     |
|             sdt-MAC-PHY-CG-Config-r17  | Not present  |     |     |
|           }                            |              |     |     |
|         }                              |              |     |     |
|       }                                |              |     |     |
|     }                                  |              |     |     |
|   }                                    |              |     |     |
| }                                      |              |     |     |

7.1.1.13.3  RA Based SDT / 2-step RACH / not complete / RA_TYPE to 4-stepRA
7.1.1.13.3.1  Test Purpose (TP)
(1)
with { UE in NR RRC_INACTIVE state and SDT-CG-Config-r17 is not configured, UE has small data to
transmit and initiated 2-step RA based SDT procedure and transmitted MSGA }
ensure that {
  when { UE receives the MSGB containing a fallbackRAR MAC subPDU }
    then { UE shall fallback to 4-step RA based SDT procedure and initiate msg3 transmission }
            }

7.1.1.13.3.2  Conformance requirements
References: The conformance requirements covered in the present TC are specified in: 3GPP TS 38.321, clause 5.1.1b,
5.1.1c and 5.1.4a. Unless otherwise stated these are Rel-17 requirements.
[TS 38.321, clause 5.1.1b]
The MAC entity shall:
1> if the BWP selected for Random Access procedure is configured with both set(s) of Random Access resources
with MSG3 repetition indication and set(s) of Random Access resources without MSG3 repetition indication and
the RSRP of the downlink pathloss reference is less than rsrp-ThresholdMsg3; or
1> if the BWP selected for Random Access procedure is only configured with the set(s) of Random Access
resources with MSG3 repetition indication:
2> assume MSG3 repetition is applicable for the current Random Access procedure.
1> else:
2> assume MSG3 repetition is not applicable for the current Random Access procedure.
NOTE 1:  Void.
1> if contention-free Random Access Resources have not been provided for this Random Access procedure and one
or more of the features including RedCap and/or a specific NSAG(s) and/or SDT and/or MSG3 repetition is
applicable for this Random Access procedure:
ETSI

3GPP TS 38.523-1 version 18.3.0 Release 18 1611 ETSI TS 138 523-1 V18.3.0 (2025-05)
NOTE 2: The applicability of SDT is determined by MAC entity according to clause 5.27. The applicability of
specific NSAG(s) is determined by upper layers when the Random Access procedure is initiated. The
applicability of RedCap is also determined by upper layers when Random Access procedure is initiated
and it is applicable to the Random Access procedures initiated by PDCCH orders and any Random
Access procedure initiated by the MAC entity.
2> if none of the sets of Random Access resources are available for any feature applicable to the current
Random Access procedure (as specified in clause 5.1.1c):
3> select the set(s) of Random Access resources that are not associated with any feature indication (as
specified in clause 5.1.1c) for this Random Access procedure.
2> else if there is one set of Random Access resources available which can be used for indicating all features
triggering this Random Access procedure:
3> select this set of Random Access resources for this Random Access procedure.
2> else (i.e. there are one or more sets of Random Access resources available that are configured with
indication(s) for a subset of all features triggering this Random Access procedure):
3> select a set of Random Access resources from the available set(s) of Random Access resources based on
the priority order indicated by upper layers as specified in clause 5.1.1d for this Random Access
Procedure.
1> else if contention-free Random Access Resources have been provided for this Random Access procedure and
RedCap is applicable for the current Random Access procedure and there is one set of Random Access resources
available that is only configured with RedCap indication:
2> select this set of Random Access resources for this Random Access procedure.
1> else:
2> select the set of Random Access resources that are not associated with any feature indication (as specified in
clause 5.1.1c) for the current Random Access procedure.
[TS 38.321, clause 5.1.1c]
The MAC entity shall for each set of configured Random Access resources for 4-step RA type and for each set of
configured Random Access resources for 2-step RA type:
1> if redCap is set to true for a set of Random Access resources:
2> consider the set of Random Access resources as not available for a Random Access procedure for which
RedCap is not applicable.
1> if smallData is set to true for a set of Random Access resources:
2> consider the set of Random Access resources as not available for the Random Access procedure which is not
triggered for RA-SDT.
1> if NSAG-List is configured for a set of Random Access resources:
2> consider the set of Random Access resources as not available for the Random Access procedure unless it is
triggered for any one of the NSAG-ID(s) in the NSAG-List.
1> if msg3-Repetitions is set to true for a set of Random Access resources:
2> consider the set of Random Access resources as not available for the Random Access procedure if Msg3
repetition is not applicable.
1> if a set of Random Access resources is not configured with FeatureCombination:
2> consider the set of Random Access resources to not associated with any feature.
[TS 38.321, clause 5.1.4a]
1> start the msgB-ResponseWindow at the PDCCH occasion as specified in TS 38.213 [6], clause 8.2A;
ETSI

3GPP TS 38.523-1 version 18.3.0 Release 18 1612 ETSI TS 138 523-1 V18.3.0 (2025-05)
1> monitor the PDCCH of the SpCell for a Random Access Response identified by MSGB-RNTI while the msgB-
ResponseWindow is running;
1> if C-RNTI MAC CE was included in the MSGA:
2> monitor the PDCCH of the SpCell for Random Access Response identified by the C-RNTI while the msgB-
ResponseWindow is running.
1> if notification of a reception of a PDCCH transmission of the SpCell is received from lower layers:
2> if the C-RNTI MAC CE was included in MSGA:
…
2> if a valid (as specified in TS 38.213 [6]) downlink assignment has been received on the PDCCH for the
MSGB-RNTI and the received TB is successfully decoded:
3> if the MSGB contains a MAC subPDU with Backoff Indicator:
4> set the PREAMBLE_BACKOFF to value of the BI field of the MAC subPDU using Table 7.2-1,
multiplied with SCALING_FACTOR_BI.
3> else:
4> set the PREAMBLE_BACKOFF to 0 ms.
3> if the MSGB contains a fallbackRAR MAC subPDU; and
3> if the Random Access Preamble identifier in the MAC subPDU matches the transmitted
PREAMBLE_INDEX (see clause 5.1.3a):
4> consider this Random Access Response reception successful;
4> apply the following actions for the SpCell:
5> process the received Timing Advance Command (see clause 5.2);
5> indicate the msgA-PreambleReceivedTargetPower and the amount of power ramping applied to
the latest Random Access Preamble transmission to lower layers (i.e.
(PREAMBLE_POWER_RAMPING_COUNTER – 1) × PREAMBLE_POWER_RAMPING_STEP);
5> if the Random Access Preamble was not selected by the MAC entity among the contention-based
Random Access Preamble(s):
6> consider the Random Access procedure successfully completed;
6> process the received UL grant value and indicate it to the lower layers.
5> else:
6> set the TEMPORARY_C-RNTI to the value received in the Random Access Response;
6> if the Msg3 buffer is empty:
7> obtain the MAC PDU to transmit from the MSGA buffer and store it in the Msg3 buffer;
6> process the received UL grant value and indicate it to the lower layers and proceed with Msg3
transmission.
7.1.1.13.3.3 Test description
7.1.1.13.3.3.1 Pre-test conditions
System Simulator:
- NR Cell 1.
ETSI

3GPP TS 38.523-1 version 18.3.0 Release 18  1613  ETSI TS 138 523-1 V18.3.0 (2025-05)
UE:
-  None.
Preamble:
-  The UE is in state 3N-A and Test Mode Activated according to TS 38.508-1 [4] Table 4.4A.2-3 with UE test
loop mode B is established IP PDU delay set to 6 seconds, the DRB is configured for SDT operation.
| 7.1.1.13.3.3.2  | Test procedure sequence  |     |     |     |     |     |
| --------------- | ------------------------ | --- | --- | --- | --- | --- |
Table 7.1.1.13.3.3.2-1: Main behaviour
| St  | Procedure  |     |        | Message Sequence  |     | TP  Verdict  |
| --- | ---------- | --- | ------ | ----------------- | --- | ------------ |
|     |            |     | U - S  | Message           |     |              |
1  SS transmits a downlink assignment including  <--  (PDCCH (C-RNTI))  -  -
the C-RNTI assigned to the UE.
2  SS transmits in the indicated downlink  <--  MAC PDU  -  -
assignment a RLC PDU in a MAC PDU on the
DRB configured with SDT (SDT Data < sdt-
DataVolumeThreshold).
3  The SS transmits an RRCRelease message  <--  NR RRC: RRCRelease  -  -
including sdt-Config-r17 in suspendConfig.
4  The UE transmits MSGA using preamble on  -->  MAC PDU (including  -  -
PRACH after IP PDU Delay expires.  NR RRC: RRCResumeRequest,
RLC PDU on DRB with SDT
configured)
| 5  The SS schedules PDCCH transmission  |     |     | <--  | MAC PDU  |     | -  -  |
| --------------------------------------- | --- | --- | ---- | -------- | --- | ----- |
addressed to MSGB-RNTI to transmit a valid  (fallbackRAR MAC subPDU)
MSGB DL MAC PDU containing a fallbackRAR
MAC subPDU.
6  Check: Does the UE transmit a MAC PDU  -->  MAC PDU (  1  P
containing an RRCResumeRequest message  NR RRC: RRCResumeRequest,
and RLC PDU on DRB with SDT configured?  RLC PDU on DRB with SDT
configured)
| 7  The SS schedules PDCCH transmission  |     |     | <--  | MAC PDU  |     | -  -  |
| --------------------------------------- | --- | --- | ---- | -------- | --- | ----- |
addressed to TC-RNTI to transmit a valid MAC  (UE Contention Resolution
| PDU containing ‘UE Contention Resolution  |     |     |     | Identity MAC CE)  |     |     |
| ----------------------------------------- | --- | --- | --- | ----------------- | --- | --- |
Identity’ MAC control element with matched
‘Contention Resolution Identity’.
8  The SS transmits a RRCResume message.  <--  NR RRC: RRCResume  -  -
9  The UE transmits a RRCResumeComplete  -->  NR RRC: RRCResumeComplete  -  -
message.
10  The SS transmits a RRCRelease message.  <--  NR RRC: RRCRelease  -  -

| 7.1.1.13.3.3.3  | Specific message contents  |     |     |     |     |     |
| --------------- | -------------------------- | --- | --- | --- | --- | --- |
Table 7.1.1.13.3.3.3-0: MAC-CellGroupConfig (preamble)
Derivation Path: TS 38.508-1 [4], Table 4.6.3-68
|                                      | Information Element  |     | Value/remark  |     | Comment  | Condition  |
| ------------------------------------ | -------------------- | --- | ------------- | --- | -------- | ---------- |
| MAC-CellGroupConfig ::= SEQUENCE {   |                      |     |               |     |          |            |
|   tag-Config SEQUENCE {              |                      |     |               |     |          |            |
|     tag-ToAddModList SEQUENCE (SIZE  |                      |     | 1 entry       |     |          |            |
(1..maxNrofTAGs)) OF TAG {
|     TAG[1] SEQUENCE {       |     |     |        |     | entry 1  |     |
| --------------------------- | --- | --- | ------ | --- | -------- | --- |
|         timeAlignmentTimer  |     |     | ms750  |     |          |     |
|       }                     |     |     |        |     |          |     |
|     }                       |     |     |        |     |          |     |
|   }                         |     |     |        |     |          |     |
| }                           |     |     |        |     |          |     |

ETSI

3GPP TS 38.523-1 version 18.3.0 Release 18  1614  ETSI TS 138 523-1 V18.3.0 (2025-05)
Table 7.1.1.13.3.3.3-1: CLOSE UE TEST LOOP (Preamble Table 7.1.1.13.3.3.2-1)
Derivation Path: TS 36.508-1 [7] table 4.7A-3 condition UE test loop mode B
|                               | Information Element  | Value/Remark  | Comment    | Condition  |
| ----------------------------- | -------------------- | ------------- | ---------- | ---------- |
| UE test loop mode B LB setup  |                      |               |            |            |
|   IP PDU delay                |                      | '0000 0110'B  | 6 seconds  | preamble   |

Table 7.1.1.13.3.3.3-2: FeatureCombinationPreambles (Table 7.1.1.13.3.3.3-6A)
Derivation Path: TS 38.508-1 [4], Table 4.6.3-56E
|                                                 | Information Element  | Value/remark  | Comment   | Condition  |
| ----------------------------------------------- | -------------------- | ------------- | --------- | ---------- |
| FeatureCombinationPreambles-r17 ::= SEQUENCE {  |                      |               |           |            |
|   featureCombination-r17 ::= SEQUENCE {         |                      |               |           |            |
|    smallData-r17                                |                      | true          |           |            |
|    }                                            |                      |               |           |            |
|   startPreambleForThisPartition-r17             |                      | 8             | Randomly  |            |
selected
|   numberOfPreamblesPerSSB-ForThisPartition-r17  |     | 12           |     |     |
| ----------------------------------------------- | --- | ------------ | --- | --- |
|   ssb-SharedRO-MaskIndex-r17                    |     | Not present  |     |     |
|   groupBconfigured-r17                          |     | Not present  |     |     |
  separateMsgA-PUSCH-Config-r17  MsgA-PUSCH-Config  TS 38.508-1 [4]
table 4.6.3-81B
|   msgA-RSRP-Threshold-r17  |     | 57           | -100 dBm         |     |
| -------------------------- | --- | ------------ | ---------------- | --- |
|   rsrp-ThresholdSSB-r17    |     | RSRP-Range   | TS 38.508-1 [4]  |     |
table 4.6.3-152
|   deltaPreamble-r17  |     | Not present  |     |     |
| -------------------- | --- | ------------ | --- | --- |
| }                    |     |              |     |     |

Table 7.1.1.13.3.3.3-3: SIB 1 (preamble Table 7.1.1.13.3.3.2-1)
Derivation path: TS 38.508-1 [4] Table 4.6.1-28 with Condition SDT
|                                          | Information Element  | Value/Remark          | Comment           | Condition  |
| ---------------------------------------- | -------------------- | --------------------- | ----------------- | ---------- |
| SIB1 ::= SEQUENCE {                      |                      |                       |                   |            |
|   servingCellConfigCommon                |                      | ServingCellConfigComm | Table             |            |
|                                          |                      | on                    | 7.1.1.13.3.3.3-4  |            |
|   nonCriticalExtension SEQUENCE {        |                      |                       |                   |            |
|     nonCriticalExtension SEQUENCE {      |                      |                       |                   |            |
|       nonCriticalExtension SEQUENCE {    |                      |                       |                   |            |
|         sdt-ConfigCommon-r17 SEQUENCE {  |                      |                       |                   |            |
|           sdt-DataVolumeThreshold-r17    |                      | byte32                |                   |            |
|         }                                |                      |                       |                   |            |
|       }                                  |                      |                       |                   |            |
|     }                                    |                      |                       |                   |            |
|   }                                      |                      |                       |                   |            |
| }                                        |                      |                       |                   |            |

Table 7.1.1.13.3.3.3-4: ServingCellConfigCommon (Table 7.1.1.13.3.3.3-3)
Derivation Path: TS 38.508-1 [4], Table 4.6.3-168
|                                         | Information Element  | Value/remark      | Comment  | Condition  |
| --------------------------------------- | -------------------- | ----------------- | -------- | ---------- |
| ServingCellConfigCommon ::= SEQUENCE {  |                      |                   |          |            |
|   uplinkConfigCommon SEQUENCE {         |                      |                   |          |            |
|     initialUplinkBWP                    |                      | BWP-UplinkCommon  | Table    |            |
7.1.1.13.3.3.3-5
|   }  |     |     |     |     |
| ---- | --- | --- | --- | --- |
| }    |     |     |     |     |

ETSI

3GPP TS 38.523-1 version 18.3.0 Release 18  1615  ETSI TS 138 523-1 V18.3.0 (2025-05)
Table 7.1.1.13.3.3.3-5: BWP-UplinkCommon (Table 7.1.1.13.3.3.3-4)
| Derivation Path: TS 38.508-1 [4], Table 4.6.3-14  |                      |                     |                   |            |
| ------------------------------------------------- | -------------------- | ------------------- | ----------------- | ---------- |
|                                                   | Information Element  | Value/remark        | Comment           | Condition  |
| BWP-UplinkCommon ::= SEQUENCE {                   |                      |                     |                   |            |
|   AdditionalRACH-ConfigList-r17 SEQUENCE {        |                      |                     |                   |            |
|     AdditionalRACH-Config-r17 SEQUENCE {          |                      |                     |                   |            |
|       rach-ConfigCommon -r17                      |                      | Not present         |                   |            |
|       msgA-ConfigCommon-r17                       |                      |  MsgA-ConfigCommon- | Table             |            |
|                                                   |                      | r16                 | 7.1.1.13.3.3.3-6  |            |
|     }                                             |                      |                     |                   |            |
|   }                                               |                      |                     |                   |            |
| }                                                 |                      |                     |                   |            |

Table 7.1.1.13.3.3.3-6: MsgA-ConfigCommon-r16 (Table 7.1.1.13.3.3.3-5)
Derivation Path: TS 38.508-1 [4], Table 4.6.3-81A
|                                        | Information Element  | Value/remark        | Comment            | Condition  |
| -------------------------------------- | -------------------- | ------------------- | ------------------ | ---------- |
| MsgA-ConfigCommon-r16 :: = SEQUENCE {  |                      |                     |                    |            |
|   rach-ConfigCommonTwoStepRA-r16       |                      | RACH-               | Table              |            |
|                                        |                      | ConfigCommonTwoStep | 7.1.1.13.3.3.3-6A  |            |
RA-r16
| }   |     |     |     |     |
| --- | --- | --- | --- | --- |

Table 7.1.1.13.3.3.3-6A: RACH-ConfigCommonTwoStepRA-r16 (Table 7.1.1.13.3.3.3-6)
Derivation Path: TS 38.508-1 [4], Table 4.6.3-128A
|                                     | Information Element  | Value/remark  | Comment  | Condition  |
| ----------------------------------- | -------------------- | ------------- | -------- | ---------- |
| RACH-ConfigCommonTwoStepRA-r16 ::=  |                      |               |          |            |
SEQUENCE {
|   featureCombinationPreamblesList-r17 SEQUENCE  |     |     |     |     |
| ----------------------------------------------- | --- | --- | --- | --- |
(SIZE(1..maxFeatureCombPreamblesPerRACHReso
urce-r17)) OF FeatureCombinationPreambles-r17 {
    FeatureCombinationPreambles-r17  FeatureCombinationPrea Table
|      |     | mbles  | 7.1.1.13.3.3.3-2  |     |
| ---- | --- | ------ | ----------------- | --- |
|   }  |     |        |                   |     |
| }    |     |        |                   |     |

Table 7.1.1.13.3.3.3-7: RRCRelease (Step 3 Table 7.1.1.13.3.3.2-1)
Derivation Path: TS 38.508-1 [4] table 4.6.1-16 with condition NR_RRC_INACTIVE and SDT
| RRCRelease ::= SEQUENCE {                    |     |          |     |     |
| -------------------------------------------- | --- | -------- | --- | --- |
|   criticalExtensions CHOICE {                |     |          |     |     |
|     rrcRelease SEQUENCE {                    |     |          |     |     |
|       suspendConfig SEQUENCE {               |     |          |     |     |
|         sdt-Config-r17 CHOICE {              |     |          |     |     |
|           setup SEQUENCE {                   |     |          |     |     |
|             sdt-DRB-List-r17 SEQUENCE (SIZE  |     | 1 entry  |     |     |
(0..maxDRB)) OF DRB-Identity {
              DRB-Identity[1]  DRB-Identity using  Entry 1
|     |     | condition DRBj  | j is the ID of the  |     |
| --- | --- | --------------- | ------------------- | --- |
DRB established
during the
preamble which is
allocated
according to
internal TTCN
mapping
|             }                          |     |              |     |     |
| -------------------------------------- | --- | ------------ | --- | --- |
|             sdt-SRB2-Indication-r17    |     | Not present  |     |     |
|             sdt-MAC-PHY-CG-Config-r17  |     | Not present  |     |     |
|           }                            |     |              |     |     |
|         }                              |     |              |     |     |
ETSI

3GPP TS 38.523-1 version 18.3.0 Release 18 1616 ETSI TS 138 523-1 V18.3.0 (2025-05)
}
}
}
}
7.1.1.13.4 RA Based SDT / 4-step RA based SDT / Time Alignment Timer expiry
7.1.1.13.4.1 Test Purpose (TP)
(1)
with { UE in NR RRC_CONNECTED state with TimeAlignmentTimer expired and SDT-CG-Config-r17 is not
configured }
ensure that {
when { UE has small data to transmit and the data volume of the pending UL data across all RBs
configured for SDT is less than or equal to sdt-DataVolumeThreshold and RSRP is above the configured
sdt-RSRP-Threshold }
then { UE shall initiate 4-step RA based SDT procedure }
}
7.1.1.13.4.2 Conformance requirements
References: The conformance requirements covered in the present TC are specified in: 3GPP TS 38.321, clause 5.1.1b,
5.1.1c and 5.2. Unless otherwise stated these are Rel-17 requirements.
[TS 38.321, clause 5.1.1b]
The MAC entity shall:
1> if the BWP selected for Random Access procedure is configured with both set(s) of Random Access resources
with MSG3 repetition indication and set(s) of Random Access resources without MSG3 repetition indication and
the RSRP of the downlink pathloss reference is less than rsrp-ThresholdMsg3; or
1> if the BWP selected for Random Access procedure is only configured with the set(s) of Random Access
resources with MSG3 repetition indication:
2> assume MSG3 repetition is applicable for the current Random Access procedure.
1> else:
2> assume MSG3 repetition is not applicable for the current Random Access procedure.
NOTE 1: Void.
1> if contention-free Random Access Resources have not been provided for this Random Access procedure and one
or more of the features including RedCap and/or a specific NSAG(s) and/or SDT and/or MSG3 repetition is
applicable for this Random Access procedure:
NOTE 2: The applicability of SDT is determined by MAC entity according to clause 5.27. The applicability of
specific NSAG(s) is determined by upper layers when the Random Access procedure is initiated. The
applicability of RedCap is also determined by upper layers when Random Access procedure is initiated
and it is applicable to the Random Access procedures initiated by PDCCH orders and any Random
Access procedure initiated by the MAC entity.
2> if none of the sets of Random Access resources are available for any feature applicable to the current
Random Access procedure (as specified in clause 5.1.1c):
3> select the set(s) of Random Access resources that are not associated with any feature indication (as
specified in clause 5.1.1c) for this Random Access procedure.
2> else if there is one set of Random Access resources available which can be used for indicating all features
triggering this Random Access procedure:
3> select this set of Random Access resources for this Random Access procedure.
ETSI

3GPP TS 38.523-1 version 18.3.0 Release 18 1617 ETSI TS 138 523-1 V18.3.0 (2025-05)
2> else (i.e. there are one or more sets of Random Access resources available that are configured with
indication(s) for a subset of all features triggering this Random Access procedure):
3> select a set of Random Access resources from the available set(s) of Random Access resources based on
the priority order indicated by upper layers as specified in clause 5.1.1d for this Random Access
Procedure.
1> else if contention-free Random Access Resources have been provided for this Random Access procedure and
RedCap is applicable for the current Random Access procedure and there is one set of Random Access resources
available that is only configured with RedCap indication:
2> select this set of Random Access resources for this Random Access procedure.
1> else:
2> select the set of Random Access resources that are not associated with any feature indication (as specified in
clause 5.1.1c) for the current Random Access procedure.
[TS 38.321, clause 5.1.1c]
The MAC entity shall for each set of configured Random Access resources for 4-step RA type and for each set of
configured Random Access resources for 2-step RA type:
1> if redCap is set to true for a set of Random Access resources:
2> consider the set of Random Access resources as not available for a Random Access procedure for which
RedCap is not applicable.
1> if smallData is set to true for a set of Random Access resources:
2> consider the set of Random Access resources as not available for the Random Access procedure which is not
triggered for RA-SDT.
1> if NSAG-List is configured for a set of Random Access resources:
2> consider the set of Random Access resources as not available for the Random Access procedure unless it is
triggered for any one of the NSAG-ID(s) in the NSAG-List.
1> if msg3-Repetitions is set to true for a set of Random Access resources:
2> consider the set of Random Access resources as not available for the Random Access procedure if Msg3
repetition is not applicable.
1> if a set of Random Access resources is not configured with FeatureCombination:
2> consider the set of Random Access resources to not associated with any feature.
[TS 38.321, clause 5.2]
The MAC entity shall:
1> when a Timing Advance Command MAC CE is received, and if an N (as defined in TS 38.211 [8]) has been
TA
maintained with the indicated TAG:
2> apply the Timing Advance Command for the indicated TAG;
2> if inactivePosSRS-TimeAlignmentTimer is configured and there is ongoing Positioning SRS Transmission in
RRC_INACTIVE as in clause 5.26:
3> start or restart the inactivePosSRS-TimeAlignmentTimer associated with the indicated TAG.
2> if CG-SDT procedure triggered as in clause 5.27 is ongoing:
3> start or restart the cg-SDT-TimeAlignmentTimer associated with the indicated TAG.
2> else:
ETSI

3GPP TS 38.523-1 version 18.3.0 Release 18 1618 ETSI TS 138 523-1 V18.3.0 (2025-05)
3> start or restart the timeAlignmentTimer associated with the indicated TAG.
…
1> when a timeAlignmentTimer expires:
2> if the timeAlignmentTimer is associated with the PTAG:
3> flush all HARQ buffers for all Serving Cells;
3> notify RRC to release PUCCH for all Serving Cells, if configured;
3> notify RRC to release SRS for all Serving Cells, if configured;
3> clear any configured downlink assignments and configured uplink grants;
3> clear any PUSCH resource for semi-persistent CSI reporting;
3> consider all running timeAlignmentTimers as expired;
3> maintain N (defined in TS 38.211 [8]) of all TAGs.
TA
7.1.1.13.4.3 Test description
7.1.1.13.4.3.1 Pre-test conditions
System Simulator:
- NR Cell 1.
UE:
- None.
Preamble:
- The UE is in state 3N-A and Test Mode Activated according to TS 38.508-1 [4] Table 4.4A.2-3 with UE test
loop mode B is established IP PDU delay set to 6 seconds, the DRB is configured for SDT operation.
7.1.1.13.4.3.2 Test procedure sequence
Table 7.1.1.13.4.3.2-1: Main behaviour
St Procedure Message Sequence TP Verdict
U - S Message
1 SS transmits a downlink assignment including <-- (PDCCH (C-RNTI)) - -
the C-RNTI assigned to the UE
2 SS transmits in the indicated downlink <-- MAC PDU - -
assignment a RLC PDU in a MAC PDU on the
DRB configured with SDT (SDT Data < sdt-
DataVolumeThreshold).
3 The SS transmits an RRCRelease message <-- NR RRC: RRCRelease - -
including sdt-Config-r17 in suspendConfig.
4 The UE transmits a preamble on PRACH. --> PRACH Preamble - -
5 The SS transmits Random Access Response <-- Random Access Response - -
with RAPID corresponding to the transmitted
Preamble in step 4, including TC-RNTI and not
including Backoff Indicator subheader.
TimeAlignmentTimer is started in UE.
6 The UE transmits a MAC PDU containing an --> MAC PDU ( - -
RRCResumeRequest message and RLC PDU NR RRC: RRCResumeRequest,
on DRB with SDT configured. RLC PDU on DRB with SDT
configured)
7 The SS schedules PDCCH transmission <-- MAC PDU - -
addressed to TC-RNTI to transmit a valid MAC (UE Contention Resolution
ETSI

3GPP TS 38.523-1 version 18.3.0 Release 18  1619  ETSI TS 138 523-1 V18.3.0 (2025-05)
| PDU containing ‘UE Contention Resolution  |     | Identity MAC CE)  |     |     |
| ----------------------------------------- | --- | ----------------- | --- | --- |
Identity’ MAC control element with matched
‘Contention Resolution Identity’.
8  The SS transmits a RRCResume message.  <--  NR RRC: RRCResume  -  -
9  The UE transmits a RRCResumeComplete  -->  NR RRC: RRCResumeComplete  -  -
message.
10  The SS transmits an OPEN UE TEST LOOP  <--  TC: OPEN UE TEST LOOP  -  -
message.
11  The UE transmits an OPEN UE TEST LOOP  -->  TC: OPEN UE TEST LOOP  -  -
| COMPLETE message.  |     | COMPLETE  |     |     |
| ------------------ | --- | --------- | --- | --- |
12  SS transmits a CLOSE UE TEST LOOP  <--  TC: CLOSE UE TEST LOOP  -  -
message.
13  The UE transmits a CLOSE UE TEST LOOP  -->  TC: CLOSE UE TEST LOOP  -  -
| COMPLETE message.  |     | COMPLETE  |     |     |
| ------------------ | --- | --------- | --- | --- |
14  SS transmits Timing Advance SS does not  <--  MAC PDU (Timing Advance  -  -
send any subsequent timing alignments.  Command MAC Control Element)
TimeAlignmentTimer is re-started in UE.
15  The SS transmits a RLC PDU in a MAC PDU  <--  MAC PDU  -  -
on the DRB configured with SDT (SDT Data <
sdt-DataVolumeThreshold).
16  Check: Does the UE transmit a preamble on  -->  PRACH Preamble  1  P
PRACH?
17  The SS transmits Random Access Response  <--  Random Access Response  -  -
with RAPID corresponding to the transmitted
Preamble in step 16, including TC-RNTI and
not including Backoff Indicator subheader.
18  Check: Does the UE transmit a MAC PDU  -->  MAC PDU (  1  P
| containing RLC PDU on DRB with SDT       |     | RLC PDU on DRB with SDT  |     |       |
| ---------------------------------------- | --- | ------------------------ | --- | ----- |
| configured?                              |     | configured)              |     |       |
| 19  The SS schedules PDCCH transmission  |     | <--  MAC PDU             |     | -  -  |
addressed to TC-RNTI to transmit a valid MAC  (UE Contention Resolution
| PDU containing ‘UE Contention Resolution  |     | Identity MAC CE)  |     |     |
| ----------------------------------------- | --- | ----------------- | --- | --- |
Identity’ MAC control element with matched
‘Contention Resolution Identity’.
20  The SS transmits a RRCRelease message   <--  NR RRC: RRCRelease  -  -

| 7.1.1.13.4.3.3  | Specific message contents  |     |     |     |
| --------------- | -------------------------- | --- | --- | --- |
Table 7.1.1.13.4.3.3-0: MAC-CellGroupConfig (preamble)
Derivation Path: TS 38.508-1 [4], Table 4.6.3-68
|                                      | Information Element  | Value/remark  | Comment  | Condition  |
| ------------------------------------ | -------------------- | ------------- | -------- | ---------- |
| MAC-CellGroupConfig ::= SEQUENCE {   |                      |               |          |            |
|   tag-Config SEQUENCE {              |                      |               |          |            |
|     tag-ToAddModList SEQUENCE (SIZE  |                      | 1 entry       |          |            |
(1..maxNrofTAGs)) OF TAG {
|     TAG[1] SEQUENCE {       |     |        | entry 1  |     |
| --------------------------- | --- | ------ | -------- | --- |
|         timeAlignmentTimer  |     | ms750  |          |     |
|       }                     |     |        |          |     |
|     }                       |     |        |          |     |
|   }                         |     |        |          |     |
| }                           |     |        |          |     |

Table 7.1.1.13.4.3.3-1: CLOSE UE TEST LOOP (Step 12, Preamble Table 7.1.1.13.4.3.2-1)
Derivation Path: TS 36.508-1 [7] table 4.7A-3 condition UE test loop mode B
|                               | Information Element  | Value/Remark  | Comment      | Condition  |
| ----------------------------- | -------------------- | ------------- | ------------ | ---------- |
| UE test loop mode B LB setup  |                      |               |              |            |
|   IP PDU delay                |                      | '0000 0110'B  | 6 seconds    | preamble   |
|   IP PDU delay                |                      | '0000 0010'B  | 2 seconds >  | Step 12    |
TimeAlignmentTi
mer

ETSI

3GPP TS 38.523-1 version 18.3.0 Release 18  1620  ETSI TS 138 523-1 V18.3.0 (2025-05)
Table 7.1.1.13.4.3.3-2: FeatureCombinationPreambles (Table 7.1.1.13.4.3.3-6)
Derivation Path: TS 38.508-1 [4], Table 4.6.3-56E
|                                                 | Information Element  | Value/remark  | Comment  | Condition  |
| ----------------------------------------------- | -------------------- | ------------- | -------- | ---------- |
| FeatureCombinationPreambles-r17 ::= SEQUENCE {  |                      |               |          |            |
|   featureCombination-r17 SEQUENCE {             |                      |               |          |            |

|     smallData-r17                    |     | true  |           |     |
| ------------------------------------ | --- | ----- | --------- | --- |
|     }                                |     |       |           |     |
|   startPreambleForThisPartition-r17  |     | 8     | Randomly  |     |
selected
|   numberOfPreamblesPerSSB-ForThisPartition-r17  |     | 12           |     |     |
| ----------------------------------------------- | --- | ------------ | --- | --- |
|   ssb-SharedRO-MaskIndex-r17                    |     | Not present  |     |     |
|   groupBconfigured-r17                          |     | Not present  |     |     |
|   separateMsgA-PUSCH-Config-r17                 |     | Not present  |     |     |
|   msgA-RSRP-Threshold-r17                       |     | Not present  |     |     |
|   rsrp-ThresholdSSB-r17                         |     | Not present  |     |     |
|   deltaPreamble-r17                             |     | Not present  |     |     |
| }                                               |     |              |     |     |

Table 7.1.1.13.4.3.3-3: SIB 1 (preamble Table 7.1.1.13.4.3.2-1)
Derivation path: TS 38.508-1 [4] Table 4.6.1-28 with condition SDT
|                                          | Information Element  | Value/Remark          | Comment           | Condition  |
| ---------------------------------------- | -------------------- | --------------------- | ----------------- | ---------- |
| SIB1 ::= SEQUENCE {                      |                      |                       |                   |            |
|   servingCellConfigCommon                |                      | ServingCellConfigComm | Table             |            |
|                                          |                      | on                    | 7.1.1.13.4.3.3-4  |            |
|   nonCriticalExtension SEQUENCE {        |                      |                       |                   |            |
|     nonCriticalExtension SEQUENCE {      |                      |                       |                   |            |
|       nonCriticalExtension SEQUENCE {    |                      |                       |                   |            |
|         sdt-ConfigCommon-r17 SEQUENCE {  |                      |                       |                   |            |
|           sdt-DataVolumeThreshold-r17    |                      | byte32                |                   |            |
|         }                                |                      |                       |                   |            |
|       }                                  |                      |                       |                   |            |
|     }                                    |                      |                       |                   |            |
|   }                                      |                      |                       |                   |            |
| }                                        |                      |                       |                   |            |

Table 7.1.1.13.4.3.3-4: ServingCellConfigCommon (Table 7.1.1.13.4.3.3-3)
Derivation Path: TS 38.508-1 [4], Table 4.6.3-168
|                                         | Information Element  | Value/remark      | Comment  | Condition  |
| --------------------------------------- | -------------------- | ----------------- | -------- | ---------- |
| ServingCellConfigCommon ::= SEQUENCE {  |                      |                   |          |            |
|   uplinkConfigCommon SEQUENCE {         |                      |                   |          |            |
|     initialUplinkBWP                    |                      | BWP-UplinkCommon  | Table    |            |
7.1.1.13.4.3.3-5
|   }  |     |     |     |     |
| ---- | --- | --- | --- | --- |
| }    |     |     |     |     |

Table 7.1.1.13.4.3.3-5: BWP-UplinkCommon (Table 7.1.1.13.4.3.3-4)
| Derivation Path: TS 38.508-1 [4], Table 4.6.3-14  |                      |                    |          |            |
| ------------------------------------------------- | -------------------- | ------------------ | -------- | ---------- |
|                                                   | Information Element  | Value/remark       | Comment  | Condition  |
| BWP-UplinkCommon ::= SEQUENCE {                   |                      |                    |          |            |
|   AdditionalRACH-ConfigList-r17 SEQUENCE {        |                      |                    |          |            |
|     AdditionalRACH-Config-r17 SEQUENCE {          |                      |                    |          |            |
|       rach-ConfigCommon-r17                       |                      | RACH-ConfigCommon  | Table    |            |
7.1.1.13.4.3.3-6
|     }  |     |     |     |     |
| ------ | --- | --- | --- | --- |
|   }    |     |     |     |     |
| }      |     |     |     |     |

ETSI

3GPP TS 38.523-1 version 18.3.0 Release 18  1621  ETSI TS 138 523-1 V18.3.0 (2025-05)
Table 7.1.1.13.4.3.3-6: RACH-ConfigCommon (Table 7.1.1.13.4.3.3-5)
Derivation Path: TS 38.508-1 [4], Table 4.6.3-128
|                                                 | Information Element  | Value/remark  | Comment  | Condition  |
| ----------------------------------------------- | -------------------- | ------------- | -------- | ---------- |
| RACH-ConfigCommon::= SEQUENCE {                 |                      |               |          |            |
|   featureCombinationPreamblesList-r17 SEQUENCE  |                      | 1 entry       |          |            |
(SIZE(1..maxFeatureCombPreamblesPerRACHReso
urce-r17)) OF FeatureCombinationPreambles-r17 {
    FeatureCombinationPreambles-r17[1]  FeatureCombinationPrea entry 1Table
|      |     | mbles  | 7.1.1.13.4.3.3-2  |     |
| ---- | --- | ------ | ----------------- | --- |
|   }  |     |        |                   |     |
| }    |     |        |                   |     |

Table 7.1.1.13.4.3.3-7: RRCRelease (Step 3, Table 7.1.1.13.4.3.2-1)
Derivation Path: TS 38.508-1 [4] table 4.6.1-16 with condition NR_RRC_INACTIVE and SDT
| RRCRelease ::= SEQUENCE {                    |     |          |     |     |
| -------------------------------------------- | --- | -------- | --- | --- |
|   criticalExtensions CHOICE {                |     |          |     |     |
|     rrcRelease SEQUENCE {                    |     |          |     |     |
|       suspendConfig SEQUENCE {               |     |          |     |     |
|         sdt-Config-r17 CHOICE {              |     |          |     |     |
|           setup SEQUENCE {                   |     |          |     |     |
|             sdt-DRB-List-r17 SEQUENCE (SIZE  |     | 1 entry  |     |     |
(0..maxDRB)) OF DRB-Identity {
              DRB-Identity[1]  DRB-Identity using  Entry 1
|     |     | condition DRBj  | j is the ID of the  |     |
| --- | --- | --------------- | ------------------- | --- |
DRB established
during the
preamble which is
allocated
according to
internal TTCN
mapping
|             }                          |     |              |     |     |
| -------------------------------------- | --- | ------------ | --- | --- |
|             sdt-SRB2-Indication-r17    |     | Not present  |     |     |
|             sdt-MAC-PHY-CG-Config-r17  |     | Not present  |     |     |
|           }                            |     |              |     |     |
|         }                              |     |              |     |     |
|       }                                |     |              |     |     |
|     }                                  |     |              |     |     |
|   }                                    |     |              |     |     |
| }                                      |     |              |     |     |

7.1.1.13.5  RA Based SDT / CG Based SDT/ cg-SDT-TimeAlignmentTimer
| 7.1.1.13.5.1  | Test Purpose (TP)  |     |     |     |
| ------------- | ------------------ | --- | --- | --- |
(1)
with { UE in NR RRC_INACTIVE state and SDT-CG-Config-r17 is configured and Random Access resources
for RA-SDT is configured }
ensure that {
  when { UE has small data to transmit and the data volume of the pending UL data across all RBs
configured for SDT is less than or equal to sdt-DataVolumeThreshold and RSRP is above the configured
sdt-RSRP-Threshold and at least one SSB configured for CG-SDT with SS-RSRP above cg-SDT-RSRP-
ThresholdSSB and cg-SDT-TimeAlignmentTimer is running}
    then { UE shall initiate CG based SDT procedure }
            }

(2)
with { UE in NR RRC_INACTIVE state and SDT-CG-Config-r17 is configured and Random Access resources
for RA-SDT is configured }
ensure that {
ETSI

3GPP TS 38.523-1 version 18.3.0 Release 18 1622 ETSI TS 138 523-1 V18.3.0 (2025-05)
when { UE has small data to transmit and the data volume of the pending UL data across all RBs
configured for SDT is less than or equal to sdt-DataVolumeThreshold and RSRP is above the configured
sdt-RSRP-Threshold and at least one SSB configured for CG-SDT with SS-RSRP above cg-SDT-RSRP-
ThresholdSSB and cg-SDT-TimeAlignmentTimer expires }
then { UE shall initiate RA based SDT procedure }
}
(3)
with { UE in NR RRC_INACTIVE state and CG-SDT is ongoing}
ensure that {
when { cg-SDT-TimeAlignmentTimer expires before receiving network response for the UL CG-SDT
transmission with CCCH message }
then { UE considers ongoing CG-SDT procedure as terminated and performs the actions upon going
to RRC_IDLE with release cause 'RRC Resume failure' }
}
(4)
with { UE in NR RRC_INACTIVE state and CG-SDT is ongoing}
ensure that {
when { cg-SDT-TimeAlignmentTimer expires after receiving network response for the UL CG-SDT
transmission with CCCH message }
then { UE does not consider ongoing CG-SDT procedure as terminated and UE shall perform uplink
transmission using legacy Random Access }
}
(5)
with { UE in NR RRC_INACTIVE state and SDT-CG-Config-r17 is configured and Random Access resources
for RA-SDT is configured }
ensure that {
when { UE initiates RA based SDT procedure }
then { UE is successfully able to send and receive subsequent SDT data }
}
7.1.1.13.5.2 Conformance requirements
References: The conformance requirements covered in the present TC are specified in: TS 38.321, clauses 5.2, 5.27.1
and 5.27.2; TS 38.331, clauses 5.3.13.5. Unless otherwise stated these are Rel-17 requirements.
[TS 38.321 clause 5.2]
RRC configures the following parameters for the maintenance of UL time alignment:
…
- cg-SDT-TimeAlignmentTimer which controls how long the MAC entity considers the uplink transmission for
CG-SDT to be uplink time aligned.
The MAC entity shall:
…
1> when the cg-SDT-TimeAlignmentTimer expires:
2> clear any configured uplink grants;
2> if a PDCCH addressed to the MAC entity's C-RNTI after initial transmission for the CG-SDT with CCCH
message has not been received:
3> consider ongoing CG-SDT procedure as terminated;
3> indicate the expiry of cg-SDT-TimeAlignmentTimer to the upper layer.
2> flush all HARQ buffers;
2> maintain N (defined in TS 38.211 [8]) of this TAG.
TA
…
ETSI

3GPP TS 38.523-1 version 18.3.0 Release 18 1623 ETSI TS 138 523-1 V18.3.0 (2025-05)
The MAC entity shall not perform any uplink transmission on a Serving Cell except the Random Access Preamble and
MSGA transmission when the timeAlignmentTimer associated with the TAG to which this Serving Cell belongs is not
running, CG-SDT procedure is not ongoing or SRS transmission in RRC_INACTIVE as in clause 5.26 is not on-going.
Furthermore, when the timeAlignmentTimer associated with the PTAG is not running, CG-SDT procedure is not
ongoing and SRS transmission in RRC_INACTIVE as in clause 5.26 is not ongoing, the MAC entity shall not perform
any uplink transmission on any Serving Cell except the Random Access Preamble and MSGA transmission on the
SpCell. The MAC entity shall not perform any uplink transmission except the Random Access Preamble and MSGA
transmission when the cg-SDT-TimeAlignmentTimer is not running during the ongoing CG-SDT procedure as triggered
in clause 5.27. The MAC entity shall not perform any uplink transmission except the Random Access Preamble and
MSGA transmission when inactivePosSRS-TimeAlignmentTimer is not running during the procedure for SRS
transmission in RRC_INACTIVE as in clause 5.26.
[TS 38.321 clause 5.27.1]
The MAC entity shall, if initiated by the upper layers for SDT procedure:
1> if the data volume of the pending UL data across all RBs configured for SDT is less than or equal to sdt-
DataVolumeThreshold; and
NOTE: For SDT procedure, the MAC entity also considers the suspended RBs configured with SDT for data
volume calculation. It is up to the UE's implementation how the UE calculates the data volume for the
suspended RBs. Size of the CCCH message is not considered for data volume calculation
1> if the RSRP of the downlink pathloss reference is higher than sdt-RSRP-Threshold; or
1> if sdt-RSRP-Threshold is not configured:
2> if the Serving Cell is configured with supplementary uplink as specified in TS 38.331 [5]; and
2> if the RSRP of the downlink pathloss reference is less than rsrp-ThresholdSSB-SUL:
3> select the SUL carrier.
2> else:
3> select the NUL carrier.
2> if CG-SDT is configured on the selected UL carrier, and TA for CG-SDT is valid according to clause 5.27.2
in the first available CG occasion for initial CG-SDT transmission with CCCH message according to clause
5.8.2; and
2> if, for each RB having data available for transmission, configuredGrantType1Allowed, if configured, is
configured with value true for the corresponding logical channel; and
2> if at least one SSB configured for CG-SDT with SS-RSRP above cg-SDT-RSRP-ThresholdSSB is available:
3> indicate to the upper layers that the conditions for initiating SDT procedure are fulfilled;
3> perform CG-SDT procedure on the selected UL carrier according to clause 5.8.2.
2> else if a set of Random Access resources for performing RA-SDT are selected according to clause 5.1.1b on
the selected UL carrier:
3> if cg-SDT-TimeAlignmentTimer is running, consider cg-SDT-TimeAlignmentTimer as expired and
perform the corresponding actions in clause 5.2;
3> indicate to the upper layers that the conditions for initiating SDT procedure are fulfilled.
[TS 38.321 clause 5.27.2]
The MAC entity shall consider the TA of the initial CG-SDT transmission with CCCH message to be valid when the
following conditions are fulfilled:
1> The RSRP values for the stored downlink pathloss reference and the current downlink pathloss reference are
valid according to TS 38.133 [11]; and
ETSI

3GPP TS 38.523-1 version 18.3.0 Release 18 1624 ETSI TS 138 523-1 V18.3.0 (2025-05)
1> Compared to the stored downlink pathloss reference RSRP value, the current RSRP value of the downlink
pathloss reference calculated as specified in TS 38.133 [11] has not increased/decreased by more than cg-SDT-
RSRP-ChangeThreshold, if configured; and
1> cg-SDT-TimeAlignmentTimer is running.
[TS 38.331 clause 5.3.13.5]
The UE shall:
…
1> else if indication from the MCG RLC that the maximum number of retransmissions has been reached is received
while SDT procedure is ongoing; or
1> if random access problem indication is received from MCG MAC while SDT procedure is ongoing; or
1> if the lower layers indicate that cg-SDT-TimeAlignmentTimer or the configuredGrantTimer expired before
receiving network response for the UL CG-SDT transmission with CCCH message while SDT procedure is
ongoing; or
1> if T319a expires:
2> consider SDT procedure is not ongoing;
2> perform the actions upon going to RRC_IDLE as specified in 5.3.11 with release cause 'RRC Resume
failure'.
7.1.1.13.5.3 Test description
7.1.1.13.5.3.1 Pre-test conditions
System Simulator:
- NR Cell 1
- System information combination NR-1 as defined in TS 38.508-1 [4] clause 4.4.3.1.3 is used in NR cell.
UE:
None.
Preamble:
- The UE is in 5GS state 3N-A according to TS 38.508-1 [4], clause 4.4A.2 Table 4.4A.2-3 and Test Loop
Function (On) with UE test loop mode B is established, if pc_logicalChannelSR_DelayTimer=True the DRB is
configured according to Table 7.1.1.13.5.3.1-1 for SDT operation.
Table 7.1.1.13.5.3.1-1: Logical Channel Configuration Settings
Parameter SDT DRB
logicalChannelSR-DelayTimerApplied True
logicalChannelSR-DelayTimer sf512
7.1.1.13.5.3.2 Test procedure sequence
Table 7.1.1.13.5.3.2-1: Main behaviour
St Procedure Message Sequence TP Verdict
U - S Message
1 The SS transmits a downlink assignment <-- (PDCCH (C-RNTI)) - -
including the C-RNTI assigned to the UE
2 SS transmits in the indicated downlink <-- MAC PDU - -
ETSI

3GPP TS 38.523-1 version 18.3.0 Release 18 1625 ETSI TS 138 523-1 V18.3.0 (2025-05)
assignment a RLC PDU in a MAC PDU on the
DRB configured with SDT. (Note 1)
3 The SS transmits an RRCRelease message <-- NR RRC: RRCRelease - -
including SDT-CG-Config-r17 in
suspendConfig. The cg-SDT-
TimeAlignmentTimer is configured to 5120ms.
4 The SS is configured on NR Cell 1 not to send - - - -
RLC acknowledgement (RLC ACK) to the next
received RLC SDU to the UE (Note 2)
5 Check: The UE transmits a MAC PDU --> MAC PDU ( 1 P
containing an RRCResumeRequest message NR RRC: RRCResumeRequest,
and RLC PDU on DRB with SDT configured in RLC PDU on DRB with SDT
a CG PUSCH occasion? configured)
6 The SS waits 6s from step 3 to ensure that cg- <-- NR RRC: Paging - -
SDT-TimeAlignmentTimer expired and then
transmits Paging message including ng-5G-S-
TMSI. (Note 3)
7 Check: Does the UE transmit an --> NR RRC: RRCSetupRequest 3 P
RRCSetupRequest message?
8-13 Steps 3 to 8 of the NR RRC_CONNECTED - - - -
procedure in TS 38.508-1 [4] Table 4.5.4.2-3
are executed to successfully complete the
service request procedure.
14 The SS transmits an OPEN UE TEST LOOP <-- NR RRC: DLInformationTransfer - -
message. TC: OPEN UE TEST LOOP
15 The UE transmits an OPEN UE TEST LOOP --> NR RRC: ULInformationTransfer - -
COMPLETE message. TC: OPEN UE TEST LOOP
COMPLETE
16 The SS transmits a CLOSE UE TEST LOOP <-- NR RRC: DLInformationTransfer - -
message. TC: CLOSE UE TEST LOOP
17 The UE transmits a CLOSE UE TEST LOOP --> NR RRC: ULInformationTransfer - -
COMPLETE message. TC: CLOSE UE TEST LOOP
COMPLETE
18 The SS transmits a downlink assignment <-- (PDCCH (C-RNTI)) - -
including the C-RNTI assigned to the UE
19 SS transmits in the indicated downlink <-- MAC PDU - -
assignment a RLC PDU in a MAC PDU on the
DRB configured with SDT. (Note 1)
20 The SS transmits an RRCRelease message <-- NR RRC: RRCRelease - -
including SDT-CG-Config-r17 in
suspendConfig. The cg-SDT-
TimeAlignmentTimer is configured to 5120ms.
21 The SS is configured on NR Cell 1 not to send - - - -
RLC acknowledgement (RLC ACK) to the next
received RLC SDU to the UE. (Note 2)
22 Check: The UE transmits a MAC PDU --> MAC PDU ( 1 P
containing an RRCResumeRequest message NR RRC: RRCResumeRequest,
and RLC PDU on DRB with SDT configured in RLC PDU on DRB with SDT
a CG PUSCH occasion? configured)
23 The SS waits 6s from step 20 to ensure that <-- NR RRC: Paging - -
cg-SDT-TimeAlignmentTimer expired and then
transmits Paging message including matched
fullI-RNTI. (Note 3)
24 Check: Does the UE transmit an --> NR RRC: RRCResumeRequest 3 F
RRCResumRequest message within 10s?
25- The test steps 1 to 8 of generic test procedure - - - -
32 in TS 38.508-1 [4] Table 4.5.4.2-3 are
performed on NR Cell 1.
33 The SS transmits an OPEN UE TEST LOOP <-- NR RRC: DLInformationTransfer - -
message. TC: OPEN UE TEST LOOP
34 The UE transmits an OPEN UE TEST LOOP --> NR RRC: ULInformationTransfer - -
COMPLETE message. TC: OPEN UE TEST LOOP
COMPLETE
35 The SS transmits a CLOSE UE TEST LOOP <-- NR RRC: DLInformationTransfer - -
message. TC: CLOSE UE TEST LOOP
36 The UE transmits a CLOSE UE TEST LOOP --> NR RRC: ULInformationTransfer - -
COMPLETE message. TC: CLOSE UE TEST LOOP
ETSI

3GPP TS 38.523-1 version 18.3.0 Release 18  1626  ETSI TS 138 523-1 V18.3.0 (2025-05)
COMPLETE
37  The SS transmits a downlink assignment  <--  (PDCCH (C-RNTI))  -  -
including the C-RNTI assigned to the UE
38  SS transmits in the indicated downlink  <--  MAC PDU  -  -
assignment a RLC PDU in a MAC PDU on the
DRB configured with SDT. (Note 1)
39  The SS transmits an RRCRelease message  <--  NR RRC: RRCRelease  -  -
including SDT-CG-Config-r17 in
suspendConfig. The cg-SDT-
TimeAlignmentTimer is configured to 5120ms.
| 40  Check: The UE transmits a MAC PDU  | -->  MAC PDU (  | 1  P  |
| -------------------------------------- | --------------- | ----- |
containing an RRCResumeRequest message  NR RRC: RRCResumeRequest,
| and RLC PDU on DRB in a CG PUSCH  | RLC PDU on DRB)  |     |
| --------------------------------- | ---------------- | --- |
occasion?
41  The SS waits 6s from step 39 to ensure that  <--  MAC PDU  -  -
cg-SDT-TimeAlignmentTimer expired and then
transmits a RLC PDU in a MAC PDU on the
DRB configured with SDT.
42  Check: Does the UE transmit a preamble on  -->  PRACH Preamble  4  P
PRACH with ra-PreambleIndex range from 0 to
7 for FR1 and from 0 to 3 for FR2?
43  The SS transmits Random Access Response  <--  Random Access Response  -  -
with RAPID corresponding to the transmitted
Preamble in step 42, including TC-RNTI and
not including Back off Indicator subheader.
| 44  Check: Does the UE transmit an       | -->  MAC PDU (             | 4  P  |
| ---------------------------------------- | -------------------------- | ----- |
| RRCResumeRequest message?                | NR RRC: RRCResumeRequest)  |       |
| 45  The SS schedules PDCCH transmission  | <--  MAC PDU               | -  -  |
addressed to TC-RNTI to transmit a valid MAC  (UE Contention Resolution Identity
PDU containing ‘UE Contention Resolution  MAC CE and NR RRC:
| Identity’ MAC control element with matched  | RRCResume)  |     |
| ------------------------------------------- | ----------- | --- |
‘Contention Resolution Identity’.
| 46   Void                                       |       |       |
| ----------------------------------------------- | ----- | ----- |
| -  Exception: Step 47 and 48 can happen in any  | -  -  | -  -  |
order
47  The UE transmits an RRCResumeComplete  -->  NR RRC: RRCResumeComplete  -  -
message.
48  Check: Does the UE transmits a MAC PDU  -->  MAC PDU (containing 1 MAC sub  4  P
| containing Loop backed PDU?              | PDU containing RLC SDU)  |       |
| ---------------------------------------- | ------------------------ | ----- |
| -  EXCEPTION: Steps 49a1-49a11 describe  | -  -                     | -  -  |
behaviour that depends on UE configuration;
the "lower case letter" identifies a step
sequence that takes place if pc_ra_SDT_r17 is
true (UE supporting RA-SDT)
49a1  IF pc_ra_SDT_r17 THEN the SS transmits an  <--  NR RRC: DLInformationTransfer  -  -
| OPEN UE TEST LOOP message.  | TC: OPEN UE TEST LOOP  |     |
| --------------------------- | ---------------------- | --- |
49a2  The UE transmits an OPEN UE TEST LOOP  -->  NR RRC: ULInformationTransfer  -  -
| COMPLETE message.  | TC: OPEN UE TEST LOOP  |     |
| ------------------ | ---------------------- | --- |
COMPLETE
49a3  The SS transmits a CLOSE UE TEST LOOP  <--  NR RRC: DLInformationTransfer  -  -
| message.  | TC: CLOSE UE TEST LOOP  |     |
| --------- | ----------------------- | --- |
49a4  The UE transmits a CLOSE UE TEST LOOP  -->  NR RRC: ULInformationTransfer  -  -
| COMPLETE message.  | TC: CLOSE UE TEST LOOP  |     |
| ------------------ | ----------------------- | --- |
COMPLETE
49a5  The SS transmits a downlink assignment  <--  (PDCCH (C-RNTI))  -  -
including the C-RNTI assigned to the UE
49a6  The SS transmits in the indicated downlink  <--  MAC PDU  -  -
assignment a RLC PDU in a MAC PDU on the
DRB configured with SDT( SDT Data < sdt-
DataVolumeThreshold).(Note 1)
49a7  The SS transmits an RRCRelease message  <--  NR RRC: RRCRelease  -  -
including SDT-CG-Config-r17 in
suspendConfig. The cg-SDT-
TimeAlignmentTimer is configured to 5120ms.
49a8  Check: Does the UE transmit a preamble on  -->  PRACH Preamble  2  P
PRACH with ra-PreambleIndex range from 8 to
15?
ETSI

3GPP TS 38.523-1 version 18.3.0 Release 18  1627  ETSI TS 138 523-1 V18.3.0 (2025-05)
49a9  The SS transmits Random Access Response  <--  Random Access Response  -  -
with RAPID corresponding to the transmitted
Preamble in step 49a8, including TC-RNTI and
not including Back off Indicator subheader.
49a1 Check: The UE transmits a MAC PDU  -->  MAC PDU (  2  P
0  containing an RRCResumeRequest message  NR RRC: RRCResumeRequest,
and RLC PDU on DRB with SDT configured?  RLC PDU on DRB with SDT
configured)
49a1 The SS schedules PDCCH transmission  <--  MAC PDU  -  -
1  addressed to TC-RNTI to transmit a valid MAC  (UE Contention Resolution Identity
| PDU containing ‘UE Contention Resolution  |     | MAC CE)  |     |     |
| ----------------------------------------- | --- | -------- | --- | --- |
Identity’ MAC control element with matched
‘Contention Resolution Identity’.
| -  EXCEPTION: Steps 49a12a1-49a12a3  |     | -  -  |     | -  -  |
| ------------------------------------ | --- | ----- | --- | ----- |
describe behaviour that depends on UE
configuration; the "lower case letter" identifies
a step sequence that takes place if
pc_logicalChannelSR_DelayTimer is true
49a1 IF pc_logicalChannelSR_DelayTimer THEN  <--  MAC PDU  -  -
2a1  SS transmits in the indicated downlink
assignment a RLC PDU in a MAC PDU on the
DRB configured with SDT (SDT Data <= sdt-
DataVolumeThreshold) (Note 1)
49a1 SS transmits an UL Grant, allowing the UE to  <--  (UL Grant (C-RNTI))  -  -
2a2  return the RLC SDU as received in step
49a12a1, on PDCCH with the C-RNTI
assigned to the UE.
49a1 Check: Does the UE transmit a MAC PDU  -->  MAC PDU  5  P
2a3  including one RLC SDU?
50  The SS transmits a RRCRelease message   <--  NR RRC: RRCRelease  -  -
Note 1:  RLC PDU is 97 bytes (RLC SDU is 94 bytes for 3 bytes RLC header and 95 bytes for 2 bytes RLC header)
and sdt-DataVolumeThreshold is 100 bytes. Therefore the size of RLC SDU is less than the sdt-
DataVolumeThreshold.
Note 2:  This step is used to ensure UE could not receive PDCCH addressed to the MAC entity's C-RNTI after initial
transmission for the CG-SDT with CCCH message.
Note 3:  After cg-SDT-TimeAlignmentTimer expired, UE considers ongoing CG-SDT procedure as terminated and
performs the actions upon going to RRC_IDLE. Therefore UE could receive CN Paging using 5G-S-TMSI
and could not receive RAN Paging using fullI-RNTI.

| 7.1.1.13.5.3.3  | Specific message contents  |     |     |     |
| --------------- | -------------------------- | --- | --- | --- |
Table 7.1.1.13.5.3.3-1: CLOSE UE TEST LOOP (Preamble and steps 16,35 and 49a3, Table
7.1.1.13.5.3.2-1)
Derivation path: 36.508-1 [7] table 4.7A-3 condition UE test loop mode B
|                               | Information Element  | Value/Remark  | Comment    | Condition  |
| ----------------------------- | -------------------- | ------------- | ---------- | ---------- |
| UE test loop mode B LB setup  |                      |               |            |            |
|   IP PDU delay                |                      | '0000 0100'B  | 4 seconds  | Preamble,  |
Step16,
Step35
|     |     | '0000 1000'B  | 8 seconds  | Step49a3  |
| --- | --- | ------------- | ---------- | --------- |

Table 7.1.1.13.5.3.3-2: SIB1 (Preamble and all steps, Table 7.1.1.13.5.3.2-1)
Derivation Path: TS 38.508-1 [4] table 4.6.1-28 with condition SDT
|                                          | Information Element  | Value/Remark          | Comment           | Condition  |
| ---------------------------------------- | -------------------- | --------------------- | ----------------- | ---------- |
| SIB1 ::= SEQUENCE {                      |                      |                       |                   |            |
|   servingCellConfigCommon                |                      | ServingCellConfigComm | Table             |            |
|                                          |                      | onSIB                 | 7.1.1.13.5.3.3-3  |            |
|   nonCriticalExtension SEQUENCE {        |                      |                       |                   |            |
|     nonCriticalExtension SEQUENCE {      |                      |                       |                   |            |
|       nonCriticalExtension SEQUENCE {    |                      |                       |                   |            |
|         sdt-ConfigCommon-r17 SEQUENCE {  |                      |                       |                   |            |
|           sdt-RSRP-Threshold-r17         |                      | 60                    | (IE value – 156)  |            |
ETSI

3GPP TS 38.523-1 version 18.3.0 Release 18  1628  ETSI TS 138 523-1 V18.3.0 (2025-05)
dBm = - 96 dBm
|           sdt-LogicalChannelSR-DelayTimer-r17  |     | sf512    |     |     |
| ---------------------------------------------- | --- | -------- | --- | --- |
|           sdt-DataVolumeThreshold-r17          |     | byte100  |     |     |
|           t319a-r17                            |     | ms4000   |     |     |
|         }                                      |     |          |     |     |
| }                                              |     |          |     |     |
| }                                              |     |          |     |     |
| }                                              |     |          |     |     |
| }                                              |     |          |     |     |

Table 7.1.1.13.5.3.3-3: ServingCellConfigCommonSIB (Table 7.1.1.13.5.3.3-2)
Derivation Path: TS 38.508-1 [4], Table 4.6.3-169
|                                            | Information Element  | Value/remark           | Comment  | Condition  |
| ------------------------------------------ | -------------------- | ---------------------- | -------- | ---------- |
| ServingCellConfigCommonSIB ::= SEQUENCE {  |                      |                        |          |            |
|   uplinkConfigCommon                       |                      | UplinkConfigCommonSIB  | Table    |            |
7.1.1.13.5.3.3-4
| }   |     |     |     |     |
| --- | --- | --- | --- | --- |

Table 7.1.1.13.5.3.3-4: UplinkConfigCommonSIB (Table 7.1.1.13.5.3.3-3)
Derivation Path: TS 38.508-1 [4], Table 4.6.3-202
|                                       | Information Element  | Value/remark      | Comment  | Condition  |
| ------------------------------------- | -------------------- | ----------------- | -------- | ---------- |
| UplinkConfigCommonSIB ::= SEQUENCE {  |                      |                   |          |            |
|   initialUplinkBWP                    |                      | BWP-UplinkCommon  | Table    |            |
7.1.1.13.5.3.3-5
| }   |     |     |     |     |
| --- | --- | --- | --- | --- |

Table 7.1.1.13.5.3.3-5: BWP-UplinkCommon (Table 7.1.1.13.5.3.3-4)
Derivation Path: TS 38.508-1 [4], Table 4.6.3-14
|                                  | Information Element  | Value/remark       | Comment  | Condition  |
| -------------------------------- | -------------------- | ------------------ | -------- | ---------- |
| BWP-UplinkCommon ::= SEQUENCE {  |                      |                    |          |            |
|   rach-ConfigCommon CHOICE {     |                      |                    |          |            |
|     setup                        |                      | RACH-ConfigCommon  | Table    |            |
7.1.1.13.5.3.3-6
|   }  |     |     |     |     |
| ---- | --- | --- | --- | --- |
| }    |     |     |     |     |

Table 7.1.1.13.5.3.3-6: RACH-ConfigCommon (Table 7.1.1.13.5.3.3-5)
Derivation Path: TS 38.508-1 [4], Table 4.6.3-128
|                                                 | Information Element  | Value/remark  | Comment  | Condition  |
| ----------------------------------------------- | -------------------- | ------------- | -------- | ---------- |
| RACH-ConfigCommon ::= SEQUENCE {                |                      |               |          |            |
|   featureCombinationPreamblesList-r17 SEQUENCE  |                      | 1 entry       |          |            |
(SIZE(1..maxFeatureCombPreamblesPerRACHReso
urce-r17)) OF FeatureCombinationPreambles-r17 {
    FeatureCombinationPreambles-r17[1] SEQUENCE    entry 1
{
|       featureCombination-r17 SEQUENCE {             |     |       |     |     |
| --------------------------------------------------- | --- | ----- | --- | --- |
|         smallData-r17                               |     | True  |     |     |
|       }                                             |     |       |     |     |
|       startPreambleForThisPartition-r17             |     | 8     |     |     |
|       numberOfPreamblesPerSSB-ForThisPartition-r17  |     | 8     |     |     |
|     }                                               |     |       |     |     |
|   }                                                 |     |       |     |     |
| }                                                   |     |       |     |     |

ETSI

3GPP TS 38.523-1 version 18.3.0 Release 18  1629  ETSI TS 138 523-1 V18.3.0 (2025-05)
Table 7.1.1.13.5.3.3-7: RRCRelease (steps 3, 20, 39 and 49a7, Table 7.1.1.13.5.3.2-1)
Derivation Path: TS 38.508-1 [4], Table 4.6.1-16 with condition NR_RRC_INACTIVE and SDT
|                              | Information Element  | Value/Remark  | Comment  | Condition  |
| ---------------------------- | -------------------- | ------------- | -------- | ---------- |
| RRCRelease ::= SEQUENCE {    |                      |               |          |            |
|   rrc-TransactionIdentifier  |                      | RRC-          |          |            |
TransactionIdentifier
|   criticalExtensions CHOICE {                |     |          |     |     |
| -------------------------------------------- | --- | -------- | --- | --- |
|     rrcRelease SEQUENCE {                    |     |          |     |     |
|       suspendConfig SEQUENCE {               |     |          |     |     |
|         sdt-Config-r17 CHOICE {              |     |          |     |     |
|           setup SEQUENCE {                   |     |          |     |     |
|             sdt-DRB-List-r17 SEQUENCE (SIZE  |     | 1 entry  |     |     |
(0..maxDRB)) OF DRB-Identity {
              DRB-Identity[1]  DRB-Identity using  Entry 1
|     |     | condition DRBj  | j is the ID of the  |     |
| --- | --- | --------------- | ------------------- | --- |
DRB established
during the
preamble which is
allocated
according to
internal TTCN
mapping
|             }                                   |     |     |     |     |
| ----------------------------------------------- | --- | --- | --- | --- |
|             sdt-MAC-PHY-CG-Config-r17 CHOICE {  |     |     |     |     |
|               setup SEQUENCE {                  |     |     |     |     |
                cg-SDT-ConfigInitialBWP-NUL-r17 CHOICE {
|                   setup SEQUENCE {             |     |               |                 |     |
| ---------------------------------------------- | --- | ------------- | --------------- | --- |
|                     pusch-Config-r17 CHOICE {  |     |               |                 |     |
|                       setup                    |     | PUSCH-Config  | TS 38.508-1[4]  |     |
Table 4.6.3-118:
PUSCH-Config
|                     }  |     |     |     |     |
| ---------------------- | --- | --- | --- | --- |
                    configuredGrantConfigToAddModList-r17
SEQUENCE (SIZE (1..maxNrofConfiguredGrantConfig-
r16)) OF ConfiguredGrantConfig {
                      ConfiguredGrantConfig[1]  ConfiguredGrantConfig  Table
7.1.1.13.5.3.3-8
|                     }  |     |     |     |     |
| ---------------------- | --- | --- | --- | --- |
|                   }    |     |     |     |     |
|                 }      |     |     |     |     |
                cg-SDT-ConfigInitialBWP-SUL-r17  Not present
                cg-SDT-ConfigInitialBWP-DL-r17 CHOICE {
|                   setup SEQUENCE {             |     |               |                 |     |
| ---------------------------------------------- | --- | ------------- | --------------- | --- |
|                     pdcch-Config-r17           |     | Not present   |                 |     |
|                     pdsch-Config-r17 CHOICE {  |     |               |                 |     |
|                       setup                    |     | PDSCH-Config  | TS 38.508-1[4]  |     |
Table 4.6.3-100:
PDSCH-Config
|                     }  |     |     |     |     |
| ---------------------- | --- | --- | --- | --- |
|                   }    |     |     |     |     |
|                 }      |     |     |     |     |
                cg-SDT-TimeAlignmentTimer-r17  ms5120  TimeAlignmentTi
mer(5.12s)
                cg-SDT-RSRP-ThresholdSSB-r17  60  (IE value – 156)
dBm = - 96 dBm
                cg-SDT-TA-ValidationConfig-r17   Not present  UE does not
perform RSRP
based TA
validation
|                }                    |     |              |     |     |
| ----------------------------------- | --- | ------------ | --- | --- |
|                 cg-SDT-CS-RNTI-r17  |     | Not present  |     |     |
|               }                     |     |              |     |     |
|             }                       |     |              |     |     |
|           }                         |     |              |     |     |
|         }                           |     |              |     |     |
ETSI