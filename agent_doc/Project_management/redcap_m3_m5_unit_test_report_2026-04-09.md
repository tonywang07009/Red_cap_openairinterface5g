# RedCap [Milestone 3 / Milestone 5] Unit Test Report

## 1. Technical Background
[Milestone 3] 的核心是把 [TS 38.331] 的 `initialDownlinkBWP-RedCap-r17`、`initialUplinkBWP-RedCap-r17` 與 `RedCap-ConfigCommonSIB-r17` 真正接到 gNB 的 [SIB1 build path]，並讓 UE 在收到 SIB1 後能依照 [RedCap 專屬 initial BWP] 與 [cell barring] 規則決定是否接入。[Milestone 5] 則不是立刻追求完整 throughput，而是先把 [rfsimulator + FlexRIC + RedCap UE capability injection] 的場景入口做成 [可啟動 / 可驗證 / 可閱讀]。因此本輪優先處理三件事：一是 gNB 端可正確生成 RedCap SIB1 欄位；二是 UE 端能用 YAML fallback capability 走通 `UECapabilityInformation` 與 SIB1 barring 決策；三是 XML / docker-compose 場景具備 attach 與 iperf 檢查入口。這樣後續要補 [CORESET#0]、scheduler 假設或端到端吞吐驗證時，就不會再被前置資產鏈或 ASN wiring 卡住。

## 2. Key C Functions / Data Structures
- `get_redcap_initial_bwp_config()`：解析 gNB YAML 中的 `redCapInitialBWP_r17`，並檢查 [FR1 20 MHz] 對應的 PRB 上限。
- `clone_redcap_downlink_bwp()`：把 common DL BWP 複製成 `initialDownlinkBWP-RedCap-r17`。
- `clone_redcap_uplink_bwp()`：把 common UL BWP 複製成 `initialUplinkBWP-RedCap-r17`，並填入 `pucch_ResourceCommonRedCap_r17`。
- `nr_rrc_redcap_sib1_access_allowed()`：依 [TS 38.331 Clause 5.2.2.4.2] 檢查 half-duplex 與 1Rx/2Rx barring。
- `load_nr_redcap_config()`：從 `nrue_recap` YAML 載入 UE 端 RedCap 能力與接入判斷所需欄位。
- `nr_rrc_mac_config_req_sib1()`：RedCap UE 優先套用 SIB1 的 RedCap initial DL/UL BWP。
- `nr_redcap_config_t`：gNB 端 RedCap common + initial BWP 設定。
- `nr_redcap_bwp_config_t`：抽象化 RedCap initial BWP 的 [start/size/scs/CORESET#0/searchSpace0/PUCCH]。
- `nr_redcap_cfg_t`：UE 端從 YAML 載入的最小 RedCap capability 與 barring 參數。

## 3. Test Results Summary Table
| Test Item | Pass / Fail | Code Coverage | Modification Logs |
|-----------|-------------|---------------|-------------------|
| `test_nr_frame_params` | Pass | N/A | 驗證既有 PHY/common frame parameter path 未被破壞 |
| `test_nr_ue_power_procedures` | Pass | N/A | 驗證 UE MAC power procedure regression 無新增錯誤 |
| `test_nr_ue_ra_procedures` | Pass | N/A | 驗證 UE RA procedure regression 無新增錯誤 |
| `xmllint` on `container_5g_flexric_rfsim_redcap.xml` | Pass | N/A | 新增 `302003` / `030001` / `030002` 後 XML 仍可被 parser 接受 |
| `docker compose config -q` on RedCap RF sim compose | Pass | N/A | compose wiring 與 service path 正常 |
| Full `cmake --build --preset tests ...` | Fail | N/A | 已從 `ccache` / `LeakSanitizer` blocker 推進到 link stage；後續卡在 offline CPM reconfigure |

## 4. 3GPP Specification Mapping
- [TS 38.306 Clause 4.2.21.1]
  - [RedCap UE] 在 [FR1] 最大頻寬為 [20 MHz]。
  - 本次對應：限制 RedCap initial BWP 的 PRB 上限，避免把 full-cell common BWP 誤當成 RedCap initial BWP。
- [TS 38.331 Clause 5.2.2.4.2]
  - [halfDuplexRedCapAllowed-r17] 若缺省，且 UE 為 [half-duplex FDD RedCap]，則 cell 應視為 [barred]。
  - 本次對應：UE 在 `nr_rrc_process_sib1()` 前先做 RedCap barring 決策。
- [TS 38.331 Clause 5.6.1.3]
  - UE 收到 `UECapabilityEnquiry` 後需回傳 `UECapabilityInformation` / `UE-NR-Capability`。
  - 本次對應：在缺少外部 capability file 時，以 `nrue_recap` YAML fallback 建立最小 Rel-17 RedCap capability。
- [TS 38.331 SIB1 ASN.1]
  - `RedCap-ConfigCommonSIB-r17`、`initialDownlinkBWP-RedCap-r17`、`initialUplinkBWP-RedCap-r17` 為 SIB1 的 RedCap 延伸欄位。
  - 本次對應：gNB 端正式寫入 SIB1；UE MAC 端正式讀取並套用。

## 5. Practice Exercises
- [Basic] 說明 [common initial BWP] 與 `initialDownlinkBWP-RedCap-r17` 在語意上有什麼不同，為什麼不能直接共用同一個 `bwp_list` 限制。
- [Applied] 若 `number_of_rx_redcap_r17=1` 且 SIB1 中 `cellBarredRedCap1Rx-r17=barred`，請描述 UE 在 `rrc_UE.c` 中應如何阻止後續 RA。
- [Advanced] 設計一個延伸方案，把 [CORESET#0] 與 scheduler 假設一起納入 [Milestone 5] 的端到端驗證，並說明你會新增哪些 log / test oracle 來確認 RedCap UE 真的在專屬 initial BWP 上工作。
