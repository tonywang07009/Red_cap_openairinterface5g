1
Impact of Bandwidth Part (BWP) Switching
on 5G NR System Performance
Fuad Abinader, Andrea Marcano, Karol Schober, Riikka Nurminen, Tero Henttonen, Hisashi Onozawa,
and Elena Virtej
Abstract—Bandwidth Parts (BWPs) is a 5G NR feature intro- Communication(URLLC)andmassiveMachineTypeCommu-
duced in 3GPP Release 15 for dynamically adapting the carrier nication (mMTC), both introducing new carrier requirements.
bandwidthandnumerologyinwhichaUEoperates.BWPallows
For instance, supporting a massive amount of UEs in mMTC
supportingmultiple servicespercarrier, e.g.eMBB andmMTC.
scenarios may require configuring narrowband carriers to
Although BWP enables higher spectrum flexibility and power
savings, the effect of delays such as BWP Inactivity Timer reduce UE power consumption; on the other hand, URLLC
and BWP Switch Delay has not been thoroughly studied and scenariosrequire shorterlatency, achievedforinstance viathe
understood. This paper presents a system-level evaluation of a use of wider SCSs.
5GNRdeploymentwithdynamicBWPadaptation.Asexpected,
resultsindicatenoimpactonperformanceunderhigherload;on To provide a unified solution for numerology and carrier
the other hand, for low load and bursty traffic, BWP switching BW flexibility, 3GPP Release 15 (Rel-15) introduced a new
ismorefrequent,enablingthepotentialforpowersavingsatthe feature called Bandwidth Part (BWP) for 5G NR [6]. BWPs
cost of increased latency and decreased throughput.
enable UEs to be configured to operate in BWs that are
Index Terms—5G NR, Bandwidth Parts, BWP adaptation. narrower than the carrier BW, using customized numerologies
and BW sizes fitting the service requirements in terms of
throughput, delay and energy efficiency. In previous 3GPP
I. INTRODUCTION
systems,UEshadtomonitortheentirecarrierBWforcontrol
ONE of the goals of 5G New Radio (NR) is introducing
signalling. With 5G NR, the UE is not required to transmit
flexiblecarriersizetoenablespectrumflexibility,i.e.the
or receive any signal (not even control) outside the frequency
capability to support UEs utilizing a carrier bandwidth (BW)
range of the active BWP, which might enable power savings
smaller than the carrier BW utilized in the network cell, as
in some scenarios [5], when e.g. (a) RF-baseband processing
well different numerologies, i.e. subcarrier spacing (SCS) [1].
operates with lower sampling rate for certain numerologies,
Spectrum flexibility in 5G NR opens a number of novel
(b) reduced baseband processing for narrower BW, and (c)
research challenges [2], including (a) allocation of carrier
bandwidth adaptation to traffic demand.
bandwidth and numerology, (b) analysis of non-orthogonality
of resource elements from different numerologies, (c) inter- In Rel-15, BWP is defined as an essential part of 5G NR,
numerology interference (INI) estimation and mitigation, and fromtheveryfirstNRinitialaccessuptothecontinuousBWP
(d) radio resource management (RRM) aspects related to adaptation through different carrier bandwidth configurations.
scheduling. For instance, [1] explores the problem of allocat- However, literature is very scarce on the influence of BWP
ing resources to efficiently support multiple numerologies in adaptation parameters, such as BWP inactivity timer and
the same TDD carrier, and provides closed-form expressions BWP switching delay, on system-level throughput and UE
for the numerology sub-band configuration and the DL-UL performance metrics (e.g. power savings, impact on traffic
duplexing ratio per sub-band; moreover, it demonstrates that latency). Understanding the overall effect of these parameters
the flexibility in spectrum usage improves throughput and has primary relevance due to the central role of BWPs in
delay performance. In [3], it is demonstrated that defining 5G NR. This paper is the first assessment on these above
numerologieswithshorterTTIsallowsreducingTCProundtrip issues.WediscussthechallengesinBWPadaptationviaBWP
time(RTT),withapositiveimpactonthroughputperformance. switching and provide a performance evaluation of different
Authors in [4] propose a solution for the problem of inter- BWP parameter configurations via system-level simulation.
cell interference coordination (ICIC) in neighboring gNodeBs The rest of the paper divides as follows. In Section II, we
(gNBs) with different numerologies. review Rel-15 BWP and discuss BWP adaptation via BWP
5G NR increases peak and user-perceived data rates in switching and how it might affect 5G NR system-level and
comparison to previous generations (e.g. LTE) by supporting UE performance. In SectionIII, we describe the methodology
carriersofupto800MHzwide,atthecostofincreasedpower used for a system-level assessment of the impact of BWP
consumption from RF and baseband signal processing [5]. adaptation on 5G NR performance. In Section IV, we present
In addition to enhanced Mobile BroadBand (eMBB) require- and discuss the results of the simulations, considering key
ments,5GNRscenarioscompriseUltraReliableLowLatency performance indicators such as application layer throughput,
schedulingdelayandDedicated/DefaultBWPratio.Finally,in
F. Abinader, A. Marcano, K. Schober, R. Nurminen, T. Hentto-
Section V we draw conclusions from this study on dynamic
nen, H. Onozawa and E. Virtej are with Nokia Bell Labs, e-mail:
fuad.abinader@nokia-bell-labs.com BWP adaptation, and provide guidelines for the next steps.
Authorized licensed use limited to: National Taipei Univ. of Technology. Downloaded on June 25,2026 at 11:51:16 UTC from IEEE Xplore. Restrictions apply.
161

2
II. BWPIN3GPP5GNRRELEASE15
5G NR supports wide carrier bandwidths, up to 200 MHz
for Frequency Range 1 (FR1, i.e. sub 6 GHz) and up to
400 MHz for Frequency Range 2 (FR2, i.e. 24 - 52 GHz).
To support this, BWP was introduced in 3GPP Rel-15 to
allow receiver-side bandwidth adaptation and it constitutes an
essential part of 5G NR access interface. BWPs are defined
in 3GPP TS 38.300 [7] (sec. 6.10) and 3GPP TS 38.211 [8]
(sec. 4.4.5).
A BWP is a contiguous BW partition on a carrier in a
servingcellthatusessomegivennumerology(i.e.,asubcarrier
spacingandacyclicprefixoverhead).EachBWPconsistsofa
groupofcontiguousphysicalresourceblocks(PRB)thatshare
some common numerology and are configured by a gNB to
a UE according to its needs. BWP sizes can vary from 24 to
275 PRBs (4k FFT), and up to 4 DL BWPs and 4 UL BWPs
can be configured to a UE on a serving cell. Only one DL
andoneULBWPcanbeactiveatagiventimeinoneserving
Fig. (1) Mapping BWP into frequency domain resources.
cell. Configured BWPs cannot be larger than the maximum
BW supported by the UE, and the UE is not expected to
receive or transmit signals outside the active BWP, except for on the actual carrier BW. offsetToCarrier is broadcasted to all
inter-frequency measurement gaps configured by the network. UEs, allowing them to define the carrier location and width.
Therefore,theschedulermustconstrainresourceallocationfor Finally, it is relevant to note that the frequency domain
control and data within the UEs active BWP. BWPs allow resource allocation is not indicated based on the CRB grid
multiplexing narrowband and wideband devices, as well as of a carrier. Instead, it is indicated based on the PRB grid of
different numerologies at the same time. Five transmission the scheduled BWP. PRBs of a BWP are numbered from 0
numerologies are defined in Rel-15, as shown in Table I ([7], and upwards in the frequency domain, with PRB 0 indicating
Table5.1-1),where∆fistheSCS.FR1supportsnumerologies the first PRB of the BWP. The gNB signals the start and
µ={0,1,2}, while FR2 supports numerologies µ= {2,3}. size/length of a BWP in the frequency domain in the form
of a Resource Indicator Value (RIV) relative to the start of
TABLE (I) Supported numerologies for 5G NR. the carrier for a given SCS. Rel-15 defines a direct mapping
∆f=2µ ×15[kHz] CP Data Synch betweenthePRBsandtheCRBs,sothattheusercantranslate
0 15 Normal Yes Yes its allocation in PRBs inside the BWP into CRBs in the
1 30 Normal Yes Yes
correspondingnumerologygrid,andfinallyintothefrequency
Normal,
2 60 Extended Yes No BW subset in use. There are four types of BWPs defined in
3 120 Normal Yes Yes Rel-15 specifications, listed below:
4 240 Normal No Yes
• InitialBWP:commontoallUEs;broadcastedinSystem
Information (SI) to be used for initial access, until UE
Figure 1 presents how a BWP setup translates into actual
receives BWP cell configuration. Possible sizes are 24,
frequency domain resources within the carrier BW. For in-
48, or 96 PRBs;
stance, the frequency reference point defined in Rel-15 for
aligning PRB resource grids of carriers with different SCS in • First active BWP: a BWP activated upon Radio
Resource Control (RRC) (re)configuration or MAC-
a serving cell is called Point A (expressed in ARFCN). Point
activation of a Secondary Cell (SCell);
A serves as a reference with respect to which a carrier (set
of usable PRBs) is defined. System Information Block type • Default BWP:BWPactivatedupontheexpirationofthe
BWPInactivityTimer.DefaultBWPcanoccupythesame
1 (SIB1) broadcasts the location of Point A, which can be
PRBs as the Initial BWP, and UEs are expected to stay
located outside the channel band. Point A sets the start of
in Default BWP until traffic demands increase;
SCS-nested common resource block (CRB) grid in a serving
cell. A CRB consists of a set of 12 consecutive subcarriers; • Dedicated BWP:regularBWPconfiguredinadedicated
manner; usually is wider than Default BWP, as to allow
for each value of a CRB grid is defined, where CRBs are
transmission of higher traffic loads;
numbered from 0 upwards in the frequency domain.
Sub-carrier 0 (SC0) of CRB 0 across all numerologies are
A. BWP adaptation via switching triggers
aligned, and PRBs are, as such, nested. Since some CRBs
might be located outside channel BW or overlap with channel BWP switching is a procedure that simultaneously activate
guard bands, the first usable resource block for some given aninactiveBWP(e.g.DedicatedBWP)whiledeactivateanac-
numerology might not coincide with the first CRB. A param- tiveBWP(e.g.DefaultBWP).BWPswitchingcanbetriggered
eter,namedoffsetToCarrier (numerology-dependent)indicates via Downlink Control Information (DCI), Radio Resource
the offset from SC0 in CRB 0 to the lowest usable subcarrier Control (RRC) signaling, BWP inactivity timer expiration, or
Authorized licensed use limited to: National Taipei Univ. of Technology. Downloaded on June 25,2026 at 11:51:16 UTC from IEEE Xplore. Restrictions apply.
162

3
TABLE (III) DCI- and timer-based BWP switch delays.
by MAC entity upon initiation of random access (RA) pro-
cedure. RRC/MAC BWP switching allows configuring a new SCS BWPSwitchDelay[#ofslots]
NRSlotlength[ms]
[kHz] Type1UE Type2UE
BWPtobeactivatedaswellasactivatinganalreadyconfigured
15 1 [1] [3]
BWP. Switching the BWPs using DCI command allows acti-
30 0.5 [2] [5]
vating pre-configured BWPs, which enables faster switching. 60 0.25 [3] [9]
Another way of triggering BWP switching is through a data 120 0.125 [6] [17]
inactivity timer. bwp-InactivityTimer is (re)started to a default
value when one of the following conditions occurs in a
BWP other than the Default BWP: (a) the UE is in the
process of transmission and/or just received an assignment
in PDCCH with no ongoing random access process, or (b)
a BWP switch by means of DCI is received. A switch to the
default BWP is triggered upon expiry of bwp-InactivityTimer.
It is up to the scheduler to configure the default values of
bwp-InactivityTimer, and default values are within the range
of 2-150ms There are five UE capability categories, listed in
Table II, each defining the number of configured BWPs,
support for different numerologies and whether the initial
BWP must overlap with a cell-defining SSBs.
Fig. (2) Mapping BWP into frequency domain resources.
TABLE (II) RAN1 UE capability categories.
UE #of Inactivity DCI BWPswith InitialBWP
Cat BWPs Timer Switch SCS SSB Depending on the NR carrier aggregation or dual connec-
6-1 1 No No
tivity scenario, the interruption may occur on NR and/or E-
6-2 2 No
Yes
6-3 Yes Yes UTRAcells.ForE-UTRAcells,theinterruptiondurationis1-
4
6-4 Yes 2subframesasdefinedin3GPPTS36.133[11](section7.32).
6-1a - - - - No
For NR cells, 3GPP TS 38.133 [9] (section 8.2) defines the
interruption duration to 1 slot for SCSs of 15khz and 30kHz,
3GPP TS 38.133 [9] (section 8.6) defines requirements
3 slots for 60kHz SCS and 5 slots for 120kHz SCS.
for BWP switch delay, i.e. time during which the UE is
required to complete the switch from the original BWP to
the new BWP. During BWP switch delay the UE is not
III. BWPEVALUATIONMETHODOLOGY
required to transmit UL signals or receive DL signals on We conducted an evaluation campaign via system-level
the cell where BWP is switched. The starting time of BWP simulationstoprovideanassessmentontheinfluenceofBWP
switch delay for DCI-based BWP switch is the slot where the adaptation in 5G NR performance. Simulations were carried
UE receives BWP switching request. For timer-based BWP using Nokia proprietary fully dynamic system-level simulator
switch, the starting time of BWP switching is the slot at with both LTE and 5G NR capabilities [12], using OFDM
the beginning of a subframe (FR1) or half-subframe (FR2) symbol level resolution in time and subcarrier resolution
immediately after bwp-InactivityTimer expires. Finally, for in frequency [13], [14].We use Exponential Effective SINR
RRC-based BWP switch, the starting time of BWP switching Mapping (EESM) as link-to-system interface[14]. We assume
is the last slot containing the RRC command including BWP 2x2 Multiple Input Multiple Output (MIMO) transmission
switch request. The ending time for RRC-based and timer- for radio links between UEs and macro cells, and their
basedBWPswitchingisdefinedasthefirstslotwheretheUE channel model follows the Urban Macro model as per[15].
can receive PDSCH (for DL active BWP switch) or transmit Proportional Fair scheduling is used for time and frequency
PUSCH (for UL active BWP switch) on the new BWP. In domains, with up to 5 scheduled users per TTI. Outer-loop
case of DCI-based BWP switching, the first slot is the one link adaptation controls target Block Error Rate (BLER) for
indicated for PDSCH reception or PUSCH transmission. the first transmission by selecting Modulation and Coding
The minimum duration of BWP switch delay depends on Scheme (MCS) based on Channel Quality Indicator (CQI)
the BWP switching scenario (DCI, timer or RRC), the UE measurements. Asynchronous chase combining Hybrid ARQ
type (Type 1 or Type 2 UE) and the SCS. For DCI-based (HARQ) with six stop-and-wait processes are used.
BWP switch the delay is as defined in Table III. For RRC- The simulation scenario consists of 7 tri-sectorized macro
based BWP switch the delay is not yet defined, but it will sites (i.e. 21 macro cells), distributed over a non-overlapping
consist of 10ms RRC processing delay ([10], section 12) plus hexagonal grid with 500m Inter-Site Distance (ISD). The
a BWP switch delay, longer than the delay defined in Table wide-area 5G NR macro cells operate at a central frequency
3 for DCI-based and timer-based BWP switch. In addition to of 3.5GHz. We consider one component carrier (CC) per
thedelayintheswitchedcell,theUEisalsoallowedashorter cell, each having 20MHz of carrier BW and 15kHz of SCS
interruption on other serving cells due to RF returning. operating in Time-Division Duplex (TDD) mode. We set
Figure 2 illustrates a BWP switch triggered by inactivity maximum transmission power for gNBs and UEs to 43 dBm
timer, with 2ms bwp-InactivityTimer and 3ms switch delay. and 23dBm, respectively. UE location is randomly generated
Authorized licensed use limited to: National Taipei Univ. of Technology. Downloaded on June 25,2026 at 11:51:16 UTC from IEEE Xplore. Restrictions apply.
163

4
at the beginning of the simulation inside the area of the 21 that system-level performance with all four BWP adaptation
macro cells. A total of 105 UEs calls are created (average of configurationsisnotimpactedbyBWPswitchingdelayswhen
5 calls per cell). Calls use FTP3 traffic generation, with PDU comparedtoabaselinescenariowithoutBWP.Thecauseisthe
generation following a Poisson process with a configurable high offered load (i.e. 51.2 Mbps per UE), which prevents the
average PDU generation rate. triggering of the BWP inactivity timer for most UEs, causing
For BWP adaptation evaluation, we assumed that UE cat- themtostayalmostallthetimeintheDedicatedBWPwaiting
egory is 6-2 [9].UEs are configured with one Default BWP for queued data in L3 buffer to be transmitted.
| and one     | Dedicated | BWP.      |      | CQI measurements |        | and   | PDSCH |     |     |     |     |     |     |     |     |
| ----------- | --------- | --------- | ---- | ---------------- | ------ | ----- | ----- | --- | --- | --- | --- | --- | --- | --- | --- |
| allocations | are       | conducted | only | at PRBs          | within | BWPs. | The   |     |     |     |     |     |     |     |     |
1.0
| presence | of DL     | traffic | triggers | the   | transition | from  | Default |     |     |     |     |     |     |     |     |
| -------- | --------- | ------- | -------- | ----- | ---------- | ----- | ------- | --- | --- | --- | --- | --- | --- | --- | --- |
| BWP to   | Dedicated | BWP,    | and      | a BWP | Inactivity | timer | is used |     |     |     |     |     |     |     |     |
0.8
| to trigger  | a switch | from          | Dedicated | BWP       | to         | Default | BWP. In |     |     |     |            |     |     |     |     |
| ----------- | -------- | ------------- | --------- | --------- | ---------- | ------- | ------- | --- | --- | --- | ---------- | --- | --- | --- | --- |
| this study, | UEs      | are scheduled |           | only in   | Dedicated  | BWPs.   | This    |     |     |     |            |     |     |     |     |
|             |          |               |           |           |            |         |         |     |     | No  | difference |     |     |     |     |
| means UEs   | stay     | in Default    |           | BWP after | inactivity | timer   | expiry  |     |     |     |            |     |     |     |     |
0.6
|         |       |         |        |         |        |         |         |     |     | from | BWP |     |     |     |     |
| ------- | ----- | ------- | ------ | ------- | ------ | ------- | ------- | --- | --- | ---- | --- | --- | --- | --- | --- |
| as long | as DL | traffic | buffer | remains | empty. | Upon DL | traffic | FDC |     |      |     |     |     |     |     |
adaptation
| arrival at | the gNB, | a   | UE is | switched | to Dedicated |     | BWP for |     |     |     |     |     |     |     |     |
| ---------- | -------- | --- | ----- | -------- | ------------ | --- | ------- | --- | --- | --- | --- | --- | --- | --- | --- |
0.4
| DL reception |      | via DCI    | command.  | BWP       | Switching |         | Delay    | is  |     |     |     |     |           |     |     |
| ------------ | ---- | ---------- | --------- | --------- | --------- | ------- | -------- | --- | --- | --- | --- | --- | --------- | --- | --- |
| assumed,     | with | two values | currently | specified |           | by 3GPP | (1ms     |     |     |     |     |     |           |     |     |
| for Type     | 1 UE | and 3ms    | for       | Type 2 UE | for       | 15 kHz  | in FR1). |     |     |     |     |     |           |     |     |
|              |      |            |           |           |           |         |          | 0.2 |     |     |     |     | BWP:Off,  |     |     |
BWP:On,T=8ms,ΔΔ=1ms,
BWP:On,T=8ms,ΔΔ=3ms,
IV. SIMULATIONRESULTS
BWP:On,T=80ms,ΔΔ=1ms,
BWP:On,T=80ms,ΔΔ=3ms,
| To evaluate |     | the impact | of  | delays from | BWP | adaptation |     | in 0.0 |     |     |     |     |     |     |     |
| ----------- | --- | ---------- | --- | ----------- | --- | ---------- | --- | ------ | --- | --- | --- | --- | --- | --- | --- |
|             |     |            |     |             |     |            |     | 0      | 5   | 10  | 15  |     | 20  | 25  | 30  |
5G NR performance, we considered scenarios with two BWP Fig. (3) Application Layer TPut for High Load [Mbps]
| Inactivity | Timers | (8ms | and   | 80ms) in   | combination |          | with two |         |        |       |          |           |        |       |     |
| ---------- | ------ | ---- | ----- | ---------- | ----------- | -------- | -------- | ------- | ------ | ----- | -------- | --------- | ------ | ----- | --- |
| BWP Switch | Delays |      | (1 ms | and 3 ms), | and         | compared | them     |         |        |       |          |           |        |       |     |
|            |        |      |       |            |             |          |          | The CDF | of the | ratio | of total | call time | during | which | UEs |
to a baseline scenario without BWP adaptation (i.e. always in stay in Default BWP is presented in Figure 4. Default BWP
| Dedicated | BWP). | Both | Default | and Dedicated |     | BWPs | occupy |                |             |     |       |     |        |            |     |
| --------- | ----- | ---- | ------- | ------------- | --- | ---- | ------ | -------------- | ----------- | --- | ----- | --- | ------ | ---------- | --- |
|           |       |      |         |               |     |      |        | Ratio provides | information |     | about | how | ”idle” | a UE would | be  |
the entire carrier BW, with no data transmission occurring for a given BWP configuration under some particular offered
while in Default BWP. This avoids the performance being traffic load; therefore, such metric is a valuable indication of
| negatively | impacted | by  | the | unavailability | of  | channel | state in- |               |     |       |          |     |            |     |          |
| ---------- | -------- | --- | --- | -------------- | --- | ------- | --------- | ------------- | --- | ----- | -------- | --- | ---------- | --- | -------- |
|            |          |     |     |                |     |         |           | the potential | for | power | savings. | 80% | of the UEs | do  | not stay |
formation(CSI)forPRBsnotinDefaultBWP.Thus,onlythe in Default BWP, while the remaining 20% of UEs stay in
| effect of    | BWP | switch   | delays | is reflected | on    | the performance. |      |             |               |          |         |        |       |          |           |
| ------------ | --- | -------- | ------ | ------------ | ----- | ---------------- | ---- | ----------- | ------------- | -------- | ------- | ------ | ----- | -------- | --------- |
|              |     |          |        |              |       |                  |      | Default BWP | for           | less     | than 2% | of the | time. | For this | traffic   |
| We evaluated |     | Downlink | (DL)   | traffic      | only, | and within       | each |             |               |          |         |        |       |          |           |
|              |     |          |        |              |       |                  |      | pattern,    | these results | indicate |         | a low  | power | saving   | potential |
FTP3 call flow, there are in average 20 PDUs generated per due to BWP adaptation. A different presentation of the same
| second. | To evaluate | the | impact | of traffic | burstiness | into | BWP |            |        |      |            |           |     |           |       |
| ------- | ----------- | --- | ------ | ---------- | ---------- | ---- | --- | ---------- | ------ | ---- | ---------- | --------- | --- | --------- | ----- |
|         |             |     |        |            |            |      |     | load, with | larger | PDUs | and longer | inter-PDU |     | interval, | could |
adaptation, we evaluated scenarios with low (1.6 Mbps) and provide different results.
| high (51.2 | Mbps) | offered | loads, | setting | PDU | sizes | to 10 KB |     |     |     |     |     |     |     |     |
| ---------- | ----- | ------- | ------ | ------- | --- | ----- | -------- | --- | --- | --- | --- | --- | --- | --- | --- |
and320KB,respectively.TableIVsummarizesthesimulation
1.0
BWP:On,T=8ms,ΔS=1ms,Δ
scenarios. For each simulation point, we launched 40 runs of BWP:On,T=8ms,ΔS=3ms,Δ
BWP:On,T=80ms,ΔS=1ms,Δ
20sofsimulationtime,latercombinedastoincreasestatistical BWP:On,T=80ms,ΔS=3ms,Δ
0.8
confidence.
|         |         |      |        |       |       |     |     |     |     | Almost | no      | switches |     |     |     |
| ------- | ------- | ---- | ------ | ----- | ----- | --- | --- | --- | --- | ------ | ------- | -------- | --- | --- | --- |
| A. High | Offered | Load | per UE | [51.2 | Mbps] |     |     | 0.6 |     |        |         |          |     |     |     |
|         |         |      |        |       |       |     |     |     |     | to     | Default | BWP      |     |     |     |
FDC
| Figure     | 3 presents | the    | CDF   | of the average |                 | application | layer    |     |     |     |     |     |     |     |     |
| ---------- | ---------- | ------ | ----- | -------------- | --------------- | ----------- | -------- | --- | --- | --- | --- | --- | --- | --- | --- |
| throughput | per        | UE (in | Mbps) | for high       | load scenarios, |             | i.e. 320 |     |     |     |     |     |     |     |     |
0.4
| KB PDUs,    | 20    | PDUs per    | second. | All         | curves    | overlap,    | showing |          |         |     |           |      |      |            |       |
| ----------- | ----- | ----------- | ------- | ----------- | --------- | ----------- | ------- | -------- | ------- | --- | --------- | ---- | ---- | ---------- | ----- |
|             | TABLE | (IV)        |         | Simulation  | Scenarios |             |         | 0.2      |         |     |           |      |      |            |       |
| OfferedLoad |       | BWPAdaptat. |         | Inact.Timer |           | SwitchDelay |         |          |         |     |           |      |      |            |       |
|             |       |             | Off     |             | -         |             | -       |          |         |     |           |      |      |            |       |
| High        |       |             |         |             |           |             |         | 0.0      |         |     |           |      |      |            |       |
|             |       |             |         |             |           | 1ms         |         | 0        | 20      |     | 40        | 60   | 80   |            | 100   |
| 320KBPDUs,  |       |             |         | 8ms         |           |             |         |          |         |     |           |      |      |            |       |
|             |       |             |         |             |           | 3ms         |         | Fig. (4) | Default | BWP | Ratio for | High | Load | [% of call | time] |
| 20PDUs/sec  |       |             | On      |             |           | 1ms         |         |          |         |     |           |      |      |            |       |
| ∼51.2Mbps   |       |             |         | 80ms        |           |             |         |          |         |     |           |      |      |            |       |
3ms
|     |     |     | Off |     | -   |     | -   |     |     |     |     |     |     |     |     |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
Low
|           |     |     |     |     |     |     | 1   | B. Low Load | [1.6 | Mbps] |     |     |     |     |     |
| --------- | --- | --- | --- | --- | --- | --- | --- | ----------- | ---- | ----- | --- | --- | --- | --- | --- |
| 10KBPDUs, |     |     |     | 8ms |     |     |     |             |      |       |     |     |     |     |     |
3
20PDUs/sec On For lower offered load, i.e.10 KB PDUs, 20 PDUs/sec,
| ∼1.6Mbps |     |     |     | 80ms |     |     | 1   |     |     |     |     |     |     |     |     |
| -------- | --- | --- | --- | ---- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
3
|     |     |     |     |     |     |     |     | gNBs transmit | PDUs |     | more quickly | than | for | the high | load |
| --- | --- | --- | --- | --- | --- | --- | --- | ------------- | ---- | --- | ------------ | ---- | --- | -------- | ---- |
Authorized licensed use limited to: National Taipei Univ. of Technology. Downloaded on June 25,2026 at 11:51:16 UTC from IEEE Xplore.  Restrictions apply.
164

5
| scenario. | As such, | UEs      | become | inactive       | more | frequently     | and |     |     |     |     |     |     |     |     |
| --------- | -------- | -------- | ------ | -------------- | ---- | -------------- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| for more  | extended | periods, |        | which triggers | the  | BWP Inactivity |     |     | 1   |     |     |     |     |     |     |
Timermoreoften,andincreasesthenumberofBWPswitches
0.9
| between | Dedicated | BWP | (i.e. | when DL | traffic | is transmitted) |     |     |     |     |     |     |     |     |     |
| ------- | --------- | --- | ----- | ------- | ------- | --------------- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
0.8
and Default BWP (i.e. between PDU generation events). ˜ 3x more
0.7
Figure 5 presents the Default BWP Ratio CDF for the low power
0.6
| loadscenario.ResultsshowthattheoccurrenceofBWPswitch |            |            |       |                       |         |            |           |     |         |     |     | savings |     |     |     |
| ---------------------------------------------------- | ---------- | ---------- | ----- | --------------------- | ------- | ---------- | --------- | --- | ------- | --- | --- | ------- | --- | --- | --- |
| eventsdepends                                        |            | on:howwell |       | theBWPinactivitytimer |         |            | fitsthe   |     | FDC 0.5 |     |     |         |     |     |     |
| traffic pattern,                                     |            | cell load  | and   | channel conditions.   |         | For        | instance, |     | 0.4     |     |     |         |     |     |     |
| UEs in                                               | the bottom | 15%        | (i.e. | UEs in bad            | channel | conditions |           |     |         |     |     |         |     |     |     |
0.3
| due to, | e.g. cell | edge) | rarely | stay in Default |     | BWP, | which | is  |     |     |     |     |     |     |     |
| ------- | --------- | ----- | ------ | --------------- | --- | ---- | ----- | --- | --- | --- | --- | --- | --- | --- | --- |
0.2
expected since their DL buffer is seldom emptied promptly No power
0.1
enough between PDU generation events as to trigger BWP savings
0
inactivity timers. Figure 5 also shows that the shorter the 0 5 10 15 20 25 30
| values of | BWP    | Inactivity |            | Timer, the | higher | the percentage  |     |      |     |       |         |             |          |          |      |
| --------- | ------ | ---------- | ---------- | ---------- | ------ | --------------- | --- | ---- | --- | ----- | ------- | ----------- | -------- | -------- | ---- |
|           |        |            |            |            |        |                 |     | Fig. | (6) | Power | savings | relative to | baseline | scenario | [%]. |
| of time   | the UE | stays      | in Default | BWP. This  | is     | again expected, |     |      |     |       |         |             |          |          |      |
as a shorter BWP inactivity timer shall be more frequently ableforscheduling)tothemomentthegNBschedulesthefirst
| triggered | between | PDU | generation | events, | thus | resulting | in  | a         |     |            |     |              |           |     |          |
| --------- | ------- | --- | ---------- | ------- | ---- | --------- | --- | --------- | --- | ---------- | --- | ------------ | --------- | --- | -------- |
|           |         |     |            |         |      |           |     | transport |     | block (TB) | for | that PDU. As | expected, | the | constant |
higherrateofswitchestoDefaultBWPthanwithlongerBWP
|     |     |     |     |     |     |     |     | BWP | switching |     | between | Default BWP | and | Dedicated | BWP |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --------- | --- | ------- | ----------- | --- | --------- | --- |
inactivity timers. The large scale of the difference in duration from BWP adaptation introduces additional PDU latency. For
| at Default | BWP | (e.g. | 4x more | for 80th | percentile) |     | indicates |                |     |        |     |                |        |     |            |
| ---------- | --- | ----- | ------- | -------- | ----------- | --- | --------- | -------------- | --- | ------ | --- | -------------- | ------ | --- | ---------- |
|            |     |       |         |          |             |     |           | a considerable |     | amount | of  | PDU scheduling | events |     | (lower 80% |
that this effect is quite significant from the perspective of of PDUs), there is a difference in the PDU scheduling delay
| potential | power | savings | due | to BWP adaptation. |     |     |     |         |     |           |      |             |            |       |         |
| --------- | ----- | ------- | --- | ------------------ | --- | --- | --- | ------- | --- | --------- | ---- | ----------- | ---------- | ----- | ------- |
|           |       |         |     |                    |     |     |     | between |     | scenarios | with | shorter BWP | inactivity | timer | and the |
baselinescenario.Relevantistosaythat,suchincreaseoffew
| 1.0 |     |     |     |     |     |     |     | millisecondsinPDUlatencywouldbemorerelevantfordelay- |          |          |                |           |          |         |          |
| --- | --- | --- | --- | --- | --- | --- | --- | ---------------------------------------------------- | -------- | -------- | -------------- | --------- | -------- | ------- | -------- |
|     |     |     |     |     |     |     |     | critical                                             | traffic, | and      | is totally     | dependent | on       | the BWP | configu- |
|     |     |     |     |     |     |     |     | ration                                               | in       | relation | to the traffic | pattern;  | this PDU | latency | is not   |
0.8
|     |     |     | ˜ 4x        | more |     |     |     |             |     |        |                |                  |     |             |         |
| --- | --- | --- | ----------- | ---- | --- | --- | --- | ----------- | --- | ------ | -------------- | ---------------- | --- | ----------- | ------- |
|     |     |     |             |      |     |     |     | significant |     | at all | when comparing | scenarios        |     | with longer | BWP     |
|     |     |     | adaptations | to   |     |     |     |             |     |        |                |                  |     |             |         |
|     |     |     |             |      |     |     |     | inactivity  |     | timer  | duration       | and the baseline |     | scenario    | without |
0.6 Default BWP BWPadaptation.Also,bothDefaultBWPandDedicatedBWP
FDC
occupy100%ofthecarrierBW,soCQIisconstantlyestimated
|     |     |     |     |     |     |     |     | for | both | BWPs | and is readily | available | after | BWP | switches. |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | ---- | ---- | -------------- | --------- | ----- | --- | --------- |
0.4
|     |     |     |          |     |     |     |     | With   | Default | and        | Dedicated | BWPs         | of different |                  | BW sizes, |
| --- | --- | --- | -------- | --- | --- | --- | --- | ------ | ------- | ---------- | --------- | ------------ | ------------ | ---------------- | --------- |
|     |     |     |          |     |     |     |     | we     | expect  | additional | latency   | due to       | HARQ         | re-transmissions |           |
| 0.2 |     |     |          |     |     |     |     | caused | by      | imprecise  | link      | adaptations. | Finally,     |                  | we do not |
|     |     | No  | switches | to  |     |     |     |        |         |            |           |              |              |                  |           |
BWP:On,T=8ms,ΔS=1ms,Δ
BWP:On,T=8ms,ΔS=3ms,Δ dynamicallyreallocateBWPsviaRRCReconfiguration,which
|     |     | Default | BWP |     | BWP:On,T=80ms,ΔS=1ms,Δ |     |     |        |              |     |        |             |             |     |     |
| --- | --- | ------- | --- | --- | ---------------------- | --- | --- | ------ | ------------ | --- | ------ | ----------- | ----------- | --- | --- |
|     |     |         |     |     |                        |     |     | would, | undoubtedly, |     | impact | PDU latency | negatively. |     |     |
BWP:On,T=80ms,ΔS=3ms,Δ
| 0.0 0    |         | 20  | 40    | 60      | 80      |         | 100   |     |     |     |     |     |     |     |     |
| -------- | ------- | --- | ----- | ------- | ------- | ------- | ----- | --- | --- | --- | --- | --- | --- | --- | --- |
| Fig. (5) | Default | BWP | Ratio | for Low | Load [% | of call | time] |     |     |     |     |     |     |     |     |
1.0
ToestimatepowersavingsfromstayinginDefaultBWP,we
| calculated | what | such | saving | would be | relative | to the | baseline |     |     |     |     |     |     |     |     |
| ---------- | ---- | ---- | ------ | -------- | -------- | ------ | -------- | --- | --- | --- | --- | --- | --- | --- | --- |
0.8
| scenario | for the   | case   | where     | power consumption, |              |         | while | in  |     |     |     |     |     |     |     |
| -------- | --------- | ------ | --------- | ------------------ | ------------ | ------- | ----- | --- | --- | --- | --- | --- | --- | --- | --- |
| Default  | BWP,      | is 30% | less      | than while         | in Dedicated |         | BWP.  |     |     |     |     |     |     |     |     |
| Results  | in Figure | 6      | show that | there are          | no power     | savings | for   |     |     |     |     |     |     |     |     |
0.6
UEs in adverse channel conditions. On the other hand, UEs FDC Additional
| withshortervaluesofBWPinactivitytimerpresentupto25% |     |     |     |     |     |     |     |     |     |     |     | latency    |     |     |     |
| --------------------------------------------------- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | ---------- | --- | --- | --- |
|                                                     |     |     |     |     |     |     |     |     | 0.4 |     |     | due to BWP |     |     |     |
ofpowersavings.Ofcourse,powersavingsshouldscaledown
from a broader BWP to a narrower BWP, depending on how adaptation
| much baseband |     | processing |     | and RF power | consumption |     | also |     |     |     |     |     |           |     |     |
| ------------- | --- | ---------- | --- | ------------ | ----------- | --- | ---- | --- | --- | --- | --- | --- | --------- | --- | --- |
|               |     |            |     |              |             |     |      |     | 0.2 |     |     |     | BWP:Off,  |     |     |
scaledownwithBW.ThefittingbetweenInter-PDUtrafficin- BWP:On,T=8ms,ΔΔ=1ms,
BWP:On,T=8ms,ΔΔ=3ms,
tervalsandBWPinactivitytimervaluealsoaffectstheDefault
BWP:On,T=80ms,ΔΔ=1ms,
BWP:On,T=80ms,ΔΔ=3ms,
BWPratio.Finally,weonlysimulatedDLtransmissions;since 0.0 100 101 102 103
the potential for power saving is higher in UL transmissions, Fig. (7) Mean PDU scheduling delay [ms].
| further investigations |     |     | are necessary. |     |     |     |     |     |     |     |     |     |     |     |     |
| ---------------------- | --- | --- | -------------- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
Figure 7 presents the CDF for the mean PDU scheduling The additional latency from the BWP switch delays in
delay in logarithmic scale, and refers to the delay from the each BWP switch event shall increase the average PDU
momentthePDUarrivesattheRLClayer(i.e.becomesavail- latency, which naturally impacts end-to-end throughput per-
Authorized licensed use limited to: National Taipei Univ. of Technology. Downloaded on June 25,2026 at 11:51:16 UTC from IEEE Xplore.  Restrictions apply.
165

6
formance. Figure 8, presenting the CDF of the application- dynamicBWPadaptationalgorithms.Forthefuture,weintend
layer throughput for the low load scenario, clearly shows this toexploreBWPpowersavingpotential,byvaryingBWPsizes
effect.ForUEswithbetterthroughputperformance,wenotice andusing a 5GNR powerconsumption modelthat takessuch
a significant throughput decrease when comparing different BWP scaling under consideration. Also, we intend to explore
BWP adaptation scenarios to the baseline scenario without dynamic BWP allocation and adaptation, by optimizing BWP
BWPadaptation.Thismightreachupto50%lowerthroughput inactivity timer default values and BWP carrier BW sizes
90th
performance for (e.g. percentile of BWP On, T=8ms, according to different goals, e.g. maximize energy efficiency,
S=3ms). Also, we can notice that the higher the amount of enhance cell-edge performance, and others. Finally, another
BWP switch events (from, e.g. larger BWP inactivity timer relevant aspect to be explored is the impact on performance
default values and lower BWP switch delays), the higher the from the unavailability of channel state information (CSI)
throughput degradation. The latter comes from the increased duringBWPadaptationinascenariowheretheBWPsoccupy
PDU latency associated, which was noticed in the PDU different subsets of PRBs, specially when using different
scheduling delay and significantly decreases throughput per- channel models (e.g. indoor).
formanceforshorterBWPinactivitytimers.Someincremental
difference is perceived when increasing BWP switch delays REFERENCES
from1msto3ms.Noteworthyistosaythat,thescaleofthese
|     |     |     |     |     |     |     |     | [1] S.Lagen,B.Bojovic,S.Goyal,L.Giupponi,andJ.Mangues-Bafalluy, |     |     |     |     |     |     |
| --- | --- | --- | --- | --- | --- | --- | --- | --------------------------------------------------------------- | --- | --- | --- | --- | --- | --- |
effectsattheseparticularvaluesforBWPInactivityTimerand “SubbandConfigurationOptimizationforMultiplexingofNumerologies
BWP Switch Delay are completely dependant on the offered in 5G TDD New Radio,” in 2018 IEEE 29th Annual International
traffic load, i.e. with different traffic pattern, the results and Symposium on Personal, Indoor and Mobile Radio Communications
(PIMRC),pp.1–7,Sep.2018.
the scale of the effect would be different. Finally, Default [2] A.Yazar,B.Pekoz,andH.Arslan,“FlexibleMulti-NumerologySystems
BWP ratio results demonstrated that, UEs in adverse channel for 5G New Radio,” Journal of Mobile Multimedia, vol. 14, no. 4,
pp.367–394,2018.
| conditions | seldom | switch | to Default | BWP, | which | is reflected |     |                                                               |     |     |     |     |     |     |
| ---------- | ------ | ------ | ---------- | ---- | ----- | ------------ | --- | ------------------------------------------------------------- | --- | --- | --- | --- | --- | --- |
|            |        |        |            |      |       |              |     | [3] N.Patriciello,S.Lagen,L.Giupponi,andB.Bojovic,“5GNewRadio |     |     |     |     |     |     |
on the lack of any perceived effect on throughput from BWP 2018
|     |     |     |     |     |     |     |     | Numerologies | and | their Impact | on the | End-To-End | Latency,” | in  |
| --- | --- | --- | --- | --- | --- | --- | --- | ------------ | --- | ------------ | ------ | ---------- | --------- | --- |
adaptation. IEEE 23rd International Workshop on Computer Aided Modeling and
DesignofCommunicationLinksandNetworks(CAMAD),pp.1–6,Sep.
2018.
1.0 [4] K. Werner, N. He, and R. Baldemair, “Multi-Subcarrier System with
BWP:Off,  MultipleNumerologies.” U.S.Patent9,820,281B1,Nov.14,2017.
BWP:On,T=8ms,ΔΔ=1ms,
BWP:On,T=8ms,ΔΔ=3ms,  [5] J. Jeon, “NR Wide Bandwidth Operations,” IEEE Communications
BWP:On,T=80ms,ΔΔ=1ms,
|     | BWP:On,T=80ms,ΔΔ=3ms,  |     |     |     |     |     |     | Magazine,vol.56,pp.42–46,March2018. |     |     |     |     |     |     |
| --- | ---------------------- | --- | --- | --- | --- | --- | --- | ----------------------------------- | --- | --- | --- | --- | --- | --- |
0.8
|     |     |     |     |       |      |     |     | [6] E. Dahlman, | S. Parkvall, |     | and J. Skld, | “Chapter | 5 - NR Overview,” | in  |
| --- | --- | --- | --- | ----- | ---- | --- | --- | --------------- | ------------ | --- | ------------ | -------- | ----------------- | --- |
|     |     |     |     | ˜ 50% | less |     |     |                 |              |     |              |          |                   |     |
5GNR:theNextGenerationWirelessAccessTechnology(E.Dahlman,
throughput S.Parkvall,andJ.Skld,eds.),pp.57–71,AcademicPress,2018.
0.6 [7] 3GPP,“NR;NRandNG-RANOverallDescription;Stage2,”Technical
FDC Specification (TS) 38.300, 3rd Generation Partnership Project (3GPP),
|     |     |     |     |     |     |     |     | Jan.2019. | Version15.4.0. |     |     |     |     |     |
| --- | --- | --- | --- | --- | --- | --- | --- | --------- | -------------- | --- | --- | --- | --- | --- |
0.4 [8] 3GPP,“NR;Physicalchannelsandmodulation,”TechnicalSpecification
|     |     |     |     |     |     |     |     | (TS) 38.211, | 3rd | Generation | Partnership | Project | (3GPP), Mar. | 2019. |
| --- | --- | --- | --- | --- | --- | --- | --- | ------------ | --- | ---------- | ----------- | ------- | ------------ | ----- |
Version15.5.0.
|     |     |     |     |     |     |     |     | [9] 3GPP,“NR;Requirementsforsupportofradioresourcemanagement,” |     |     |     |     |     |     |
| --- | --- | --- | --- | --- | --- | --- | --- | -------------------------------------------------------------- | --- | --- | --- | --- | --- | --- |
0.2
No difference TechnicalSpecification(TS)38.133,3rdGenerationPartnershipProject
|     |     | for cell-edge | UEs |     |     |     |     | (3GPP),Jan.2019. |       | Version15.4.0. |         |       |                          |     |
| --- | --- | ------------- | --- | --- | --- | --- | --- | ---------------- | ----- | -------------- | ------- | ----- | ------------------------ | --- |
|     |     |               |     |     |     |     |     | [10] 3GPP, “NR;  | Radio | Resource       | Control | (RRC) | protocol specification,” |     |
TechnicalSpecification(TS)38.331,3rdGenerationPartnershipProject
| 0.0 0 | 5   | 10  | 15  | 20  |     | 25  | 30  |                  |     |                |     |     |     |     |
| ----- | --- | --- | --- | --- | --- | --- | --- | ---------------- | --- | -------------- | --- | --- | --- | --- |
|       |     |     |     |     |     |     |     | (3GPP),Jan.2019. |     | Version15.4.0. |     |     |     |     |
Fig. (8) Application Layer TPut for Low Load [Mbps] [11] 3GPP,“EvolvedUniversalTerrestrialRadioAccess(E-UTRA);Require-
mentsforsupportofradioresourcemanagement,”TechnicalSpecifica-
tion(TS)36.133,3rdGenerationPartnershipProject(3GPP),Jan.2019.
Version15.4.0.
V. CONCLUSIONANDFUTURESTEPS [12] D. S. Michalopoulos, A. Maeder, and N. Kolehmainen, “5G Multi-
|     |     |     |     |     |     |     |     | Connectivity | with | Non-Ideal | Backhaul: | Distributed | vs Cloud-Based |     |
| --- | --- | --- | --- | --- | --- | --- | --- | ------------ | ---- | --------- | --------- | ----------- | -------------- | --- |
In this work, we presented the BWP feature as a 5G NR Architecture,”in2018IEEEGlobecomWorkshops(GCWkshps),pp.1–
6,Dec2018.
| enabler for    | introducing | flexibility |            | in spectrum |           | allocation. | We  |                                                                   |          |        |            |             |         |      |
| -------------- | ----------- | ----------- | ---------- | ----------- | --------- | ----------- | --- | ----------------------------------------------------------------- | -------- | ------ | ---------- | ----------- | ------- | ---- |
|                |             |             |            |             |           |             |     | [13] P.Kela,J.Puttonen,N.Kolehmainen,T.Ristaniemi,T.Henttonen,and |          |        |            |             |         |      |
| also discussed | the         | procedures  | introduced |             | by Rel-15 | for         | BWP |                                                                   |          |        |            |             |         |      |
|                |             |             |            |             |           |             |     | M. Moisio,                                                        | “Dynamic | packet | scheduling | performance | in UTRA | Long |
adaptation, related to the dynamic switch between a Default Term Evolution downlink,” in 2008 3rd International Symposium on
WirelessPervasiveComputing,pp.308–313,May2008.
| BWP and    | a Dedicated | BWP      | via      | inactivity | timer.     | System-level |        |                                                                   |     |     |     |     |     |     |
| ---------- | ----------- | -------- | -------- | ---------- | ---------- | ------------ | ------ | ----------------------------------------------------------------- | --- | --- | --- | --- | --- | --- |
|            |             |          |          |            |            |              |        | [14] N.Kolehmainen,J.Puttonen,P.Kela,T.Ristaniemi,T.Henttonen,and |     |     |     |     |     |     |
| simulation | results     | indicate | that for | high       | load there | is no        | effect |                                                                   |     |     |     |     |     |     |
M.Moisio,“ChannelQualityIndicationReportingSchemesforUTRAN
onperformancebecauseofthelackofBWPswitches,whereas LongTermEvolutionDownlink,”inVTCSpring2008-IEEEVehicular
for low load the higher number of BWP switches for low TechnologyConference,pp.2522–2526,May2008.
|     |     |     |     |     |     |     |     | [15] M.Series,“Guidelinesforevaluationofradiointerfacetechnologiesfor |     |     |     |     |     |     |
| --- | --- | --- | --- | --- | --- | --- | --- | --------------------------------------------------------------------- | --- | --- | --- | --- | --- | --- |
inactivity timers impacts negatively on the performance when IMT-Advanced,”ReportITU,vol.638,2009.
| compared | to a baseline |     | scenario | without | BWP | adaptation. |     |     |     |     |     |     |     |     |
| -------- | ------------- | --- | -------- | ------- | --- | ----------- | --- | --- | --- | --- | --- | --- | --- | --- |
However,wealsoshowedthatBWPadaptationenablespower
| savings if      | Default  | BWP is  | narrower         | than      | Dedicated | BWP.       |     |     |     |     |     |     |     |     |
| --------------- | -------- | ------- | ---------------- | --------- | --------- | ---------- | --- | --- | --- | --- | --- | --- | --- | --- |
| These           | findings | provide | a useful         | guideline |           | for both   | the |     |     |     |     |     |     |     |
| static planning | of       | 5G NR   | cell deployments |           | and       | the design | of  |     |     |     |     |     |     |     |
Authorized licensed use limited to: National Taipei Univ. of Technology. Downloaded on June 25,2026 at 11:51:16 UTC from IEEE Xplore.  Restrictions apply.
166