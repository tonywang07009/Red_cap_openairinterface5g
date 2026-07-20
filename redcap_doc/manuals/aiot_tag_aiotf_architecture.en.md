# A-IoT Tag and AIOTF Architecture

[繁體中文](./aiot_tag_aiotf_architecture.zh-TW.md)

## Status

| Item | Current result |
|---|---|
| Implemented profile | `experimental_n6`, disabled by default |
| Standard profiles | `trusted_af_sbi` and `third_party_af_nef` unavailable `[Needs Verification]` |
| Standards baseline | Local TS 23.369 V20.0.0 draft; it is unapproved future-development material |
| Claim boundary | Deterministic protocol, RFsim, process, diagnostic UDP, HTTP/2 NRF-dependency, and bounded Naiotf Inventory evidence; no AMF/RAN round trip, complete-SBI, 3GPP-conformance, or physical-RF claim |

## Topology 2

```text
gNB/CW node -- CW2D beam --> Tag
UE Reader   -- R2D -------> Tag
UE Reader   <-- D2R ------- Tag
UE -- its PDU session / NR Uu --> gNB --> UPF -- N6 --> AIOTF diagnostic listener
```

- The gNB or an independent CW node supplies continuous carrier energy. A sleeping RedCap UE does not supply continuous CW.
- The UE wakes for an inventory window. One reader sends R2D; one or two eligible UEs may receive D2R.
- The Tag stores its identity and payload, not a UE allow-list or reader assignment.
- AIOTF owns binding, scheduling, correlation, failover, first-valid arbitration, and evidence retention.
- The N6 packet uses the UE's PDU session. AIOTF does not own a PDU session.

## Owners

| Responsibility | File or runtime owner | State |
|---|---|---|
| Tag/CW and experimental Manchester/SFS codec | `radio/rfsimulator/stored_node.c` | Implemented, RFsim only |
| R2D/D2R control relay | `radio/rfsimulator/simulator.cpp` | Implemented, disabled unless `aiot_t2` is selected |
| UE R2D encode and D2R decode/CRC | `openair1/PHY/NR_UE_TRANSPORT/nr_ue_rf_helpers.c` | Implemented experimental profile |
| UE wake gate and 40-byte report producer | `executables/nr-ue.c` | Implemented experimental profile |
| Binding, scheduling, failover, arbitration | `openair3/AIOTF/aiotf_inventory.c` | Implemented for 60 Tags and two reader handles |
| Process, health, pending context, UDP/Naiotf listener | `openair3/AIOTF/aiotf_service.c` | Implemented for `experimental_n6` and the bounded Inventory surface |
| Container and networks | `oai-cn5g/docker-compose.yaml` | `aiot` profile, disabled by default |
| NRF AIOTF profile schema and discovery | External `oai-cn5g-nrf` owner | Implemented and verified in the Compose runtime |
| AIOTF NRF client | `openair3/AIOTF/aiotf_service.c` | HTTP/2 registration/update/read-back/discovery/delete implemented |
| `Naiotf_AIoT_Inventory` listener/callback | `openair3/AIOTF/aiotf_service.c` | h2c request/response and HTTP/2 callback implemented; the complete profile is not ready |
| AMF/NGAP/RRC and NEF adapters | External CN owners and the in-repo RAN | Not implemented `[Needs Verification]` |

## Binding and arbitration

| Tag IDs | Eligible readers | Normal primary | Diversity observer |
|---|---|---|---|
| 1-20 | UE1 | UE1 | none |
| 21-30 | UE1, UE2 | UE1 | UE2 |
| 31-40 | UE1, UE2 | UE2 | UE1 |
| 41-60 | UE2 | UE2 | none |

Normal mode activates only the primary reader. Diversity mode is allowed only for Tags 21-40. The primary sends R2D and the observer is D2R-only. AIOTF accepts the first report that matches correlation, session, Tag, binding epoch, frame/slot, eligible reader, deadline, and CRC state. Later equal payloads are duplicate evidence; different valid payloads are conflict evidence. No MRC, soft combining, or IQ combining is performed.

## Diagnostic report contract

The UE report is 40 bytes in network byte order:

| Field | Size | Boundary |
|---|---:|---|
| Magic | 4 | `0x41494f54` |
| Version | 1 | `1` |
| Payload length | 1 | 1-16 |
| Flags | 2 | CRC-valid flag required |
| Reader handle | 4 | 1 or 2 |
| Tag ID | 4 | 1-60 |
| Frame | 4 | 0-1023 |
| Slot | 4 | 0-159 |
| Payload | 16 | First `payload length` bytes are used |

The wire record does not contain correlation ID, session ID, or binding epoch. The listener therefore requires an unambiguous pending context with the same Tag, frame, and slot before calling arbitration. Zero matches are rejected; multiple matches are rejected before arbitration.

## CN5G profiles

| Profile | Networks | Readiness | Result |
|---|---|---|---|
| `experimental_n6` | `public_net`, `traffic_net` | State initialized and UDP listener bound | Implemented diagnostic path |
| `trusted_af_sbi` | `public_net` | Naiotf listener, AIOTF NRF client, AMF/NGAP/RRC endpoints | Disabled; the Naiotf and NRF dependencies pass, but the RAN/AMF endpoints are missing |
| `third_party_af_nef` | `public_net` | Trusted-AF path plus `Nnef_AIoT_*`, auth, callback | Disabled; OAI NEF `358f2131` is selected but lacks the required API owner |

The current AIOTF container uses `192.168.70.141` on `public_net` and `192.168.72.141` on `traffic_net`. UDP 36900 is published only on host loopback. Baseline Compose does not include AIOTF unless profile `aiot` is selected.

## Naiotf Inventory contract

| Item | Implemented boundary |
|---|---|
| Route | h2c `POST /naiotf-aiot/v1/request-inv` |
| Request | `afId`, explicit `targetDevices.devices`, and `notifUri`; `numDevices` and `timeInterval` are bounded optional fields |
| Response | HTTP 200 with a unique `transId` |
| Device mapping | Tag IDs 1-60 are encoded as four-byte network-order unsigned integers and then base64; Tag 1=`AAAAAQ==`, Tag 60=`AAAAPA==` |
| Authorization | One local allow-list value from `--trusted-af-id`; a different AF receives 403 |
| Notification | HTTP/2 POST of `AIoTNotif`; callback success requires 204 and failures retry every five seconds |
| Bounded state | One active Inventory operation at a time, up to 60 unique Tags; reuses `aiotf_inventory` correlation, epoch, first-valid, duplicate/conflict, and timeout state |

The implementation does not currently accept `targetArea`, filtering selection, HTTPS callbacks, or OAuth tokens, and it does not expose Command, ADM, or AIoT security services. The permanent-ID mapping and local authorization are experimental contracts, not 3GPP conformance evidence `[Needs Verification]`.

## NRF schema and version

| Item | Frozen value |
|---|---|
| NRF source | `087f11cab1bd01a6d30fd97f225b5258e77d8e3a` |
| common-src source | `d30e5b06a05d00e68e85ef3060d484a3e6d26ed7` plus the minimum generated-style AIOTF diff |
| OpenAPI baseline | 3GPP Forge `REL-20` commit `28e28457200336cf6d291ed1dd419f194fc50fe5`, TS 29.510 V19.6.0 |
| Runtime image | `oai-nrf@sha256:59bbe00f83453e4543eb8c37a77db024711f3cd74708a3819ac6b407b60e901f` |
| Previous image | `oaisoftwarealliance/oai-nrf@sha256:af0fd1d202af0b6ceb65373977abe780b69aad1912390bf5835350955a034a92` |

The NRF now stores native `nfType=AIOTF` and `aiotfInfoList` and applies `target-nf-type=AIOTF` plus `aiot-area-ids`. Server conformance evidence is in `test_log/compiler_logs/nrf_aiotf_conformance_2026-07-20_14-38-05.log`. AIOTF client evidence for create 201, restart/update 200, read-back, area discovery, rejection, timeout, NRF unavailable, and deregistration 204 is in `test_log/compiler_logs/aiotf_nrf_client_runtime_final_2026-07-20_15-30-03.log`.

The client profile deliberately omits `nfServices`: the frozen TS 29.510 `ServiceName` schema has no `Naiotf` value, so a service name must not be invented. The `Naiotf` service-list mapping and NRF HTTP/1 generated-API parity remain `[Needs Verification]`; current evidence covers HTTP/2 only.

The external owner does not commit a reproducible TS 29.510 model-generation command. This is a minimum generated-style diff against the frozen baseline, not a claim that every Release 19 model was upgraded. `[Needs Verification]`

## Rollback

Run the registered AIOTF `down` operation. It stops and removes only `oai-aiotf`; it does not use `docker compose down`, delete volumes, change `register_nf.general`, or recreate other CN5G services. Repeated `down` calls are supported.

For NRF rollback, change only the image in `oai-cn5g/docker-compose.yaml` to the previous digest in the table and run:

```bash
docker compose -f oai-cn5g/docker-compose.yaml up -d --no-deps --force-recreate oai-nrf
```

Do not use `down -v`. The exercised rollback and forward restoration each took about 11 seconds; see `test_log/compiler_logs/nrf_aiotf_rollback_drill_2026-07-20_14-47-35.log`.

## Blocked standard path

The NRF server, AIOTF registration/update/read-back/discovery client, and bounded `Naiotf_AIoT_Inventory` gates now pass. The complete standard path remains blocked by the selected AMF's missing `Namf_AIoT` route, the RAN checkout's missing NGAP/RRC AIoT endpoints, and the missing `Nnef_AIoT_*` owner in selected OAI NEF `358f2131`. Do not replace these missing interfaces with N6 UDP or register AIOTF as another NF type.

Published TS 38.413 V19.1.0 contains A-IoT NGAP/ASN.1, but clauses 8.20.1-8.20.5 explicitly constrain the NG-RAN node to a gNB reader. Published TS 38.331 V19.1.0 exposes no matching AIoT/UE Reader RRC endpoint. Importing the Release 19 NGAP contract would therefore implement topology 1, not the selected topology 2. Task 2.8 must wait for a matched UE Reader NGAP/RRC Stage-3 baseline `[Needs Verification]`.

## References

- 3GPP TS 29.510: <https://portal.3gpp.org/desktopmodules/Specifications/SpecificationDetails.aspx?specificationId=3345>
- 3GPP 5G APIs Forge: <https://forge.3gpp.org/rep/all/5G_APIs>
- OAI NRF owner: <https://gitlab.eurecom.fr/oai/cn5g/oai-cn5g-nrf>
- ETSI/3GPP TS 38.413 V19.1.0: <https://www.etsi.org/deliver/etsi_ts/138400_138499/138413/19.01.00_60/ts_138413v190100p.pdf>
- ETSI/3GPP TS 38.331 V19.1.0: <https://www.etsi.org/deliver/etsi_ts/138300_138399/138331/19.01.00_60/ts_138331v190100p.pdf>
