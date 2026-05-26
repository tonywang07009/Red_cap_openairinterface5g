# RedCap mMTC Staggered Launch Validation Report

## 1. Technical Background
- [Milestone]：[M5 Compose Rebase & mMTC Scaling]
- [Context]：固定驗證路徑要求同時保留 [UE1 = baseline / non-RedCap] 與 [UE2, UE32 = RedCap]，並且全部掛在同一條 [docker compose] runtime path。
- [Observed Failure]：在 [UE1/UE2/UE32 concurrent startup] 下，[UE1] 會在 [RRCSetup / CellGroupConfig] 之後 [ExitCode 139]；但 [UE2] 與 [UE32] 仍可完成 [attach + PDU session]。
- [Isolation Result]：[UE1-only] smoke 完整通過，因此失敗點從 [UE1 baseline YAML] 與 [RedCap bearer long-SN suspect] 收斂到 [multi-UE concurrent attach timing / RA pressure]。
- [Mitigation]：在 [redcap_interface/redcap_mmtc_smoke_validation.sh] 加入 [GNB_WARMUP=5s] 與 [UE_START_GAP=3s]，先起 [nearRT-RIC + gNB]，再逐一拉起 sample UE。
- [Outcome]：修補後的 [UE1/UE2/UE32] 全部完成 [Registration Accept]、[PDU Session Establishment Accept]、[`oaitun_ue1`] 建立，以及 [forward/reverse ping] 全綠。

## 2. Key C Functions / Data Structures Utilized in This Module
- [Function] `nr_rrc_process_rrcsetup()` in [openair2/RRC/NR_UE/rrc_UE.c]
  - [Role]：處理 [RRCSetup]，並呼叫 [masterCellGroup] 與 [radioBearerConfig] 套用路徑。
- [Function] `nr_rrc_ue_process_masterCellGroup()` in [openair2/RRC/NR_UE/rrc_UE.c]
  - [Role]：解碼並下發 [NR_CellGroupConfig_t] 至 MAC。
- [Function] `nr_rrc_mac_config_req_cg()` in [openair2/LAYER2/NR_MAC_UE/config_ue.c]
  - [Role]：在 UE 端套用 [CellGroupConfig]；本次 crash 的最後可見 marker 就停在這條路徑附近。
- [Data Structure] `[NR_CellGroupConfig_t]`
  - [Role]：承載 [SpCell / MAC / RLC] 的 dedicated configuration。
- [Data Structure] `[NR_UE_NR_Capability_t]`
  - [Role]：承載 [UE capability]；本次分析曾用來排除先前的 [RedCap long-SN bearer] 假說。
- [Data Structure] `[nr_redcap_cfg_t]`
  - [Role]：由 YAML 載入的 [RedCap capability]，供 UE capability fallback 與 RedCap gating 使用。

## 3. Test Results Summary Table
| Test Item | Pass / Fail | Code Coverage | Notes |
|-----------|-------------|---------------|-------|
| [Concurrent smoke before mitigation] `MMTC_SAMPLE_UES=1,2,32` | Fail | N/A | [UE1] 在 [CellGroupConfig] 後 [ExitCode 139]；[UE2/UE32] attach 與 user-plane 成功；gNB log 出現 [vrb_map] / [RA window] 壓力跡象 |
| [Isolation smoke] `MMTC_SAMPLE_UES=1` | Pass | N/A | [UE1-only] 完成 [attach + bidirectional ping]；排除 [baseline UE1 YAML] 單獨不相容 |
| [Script syntax check] `bash -n redcap_interface/redcap_mmtc_smoke_validation.sh` | Pass | N/A | staged-launch patch 無 shell syntax error |
| [Staggered smoke after mitigation] `MMTC_SAMPLE_UES=1,2,32` | Pass | N/A | [UE1/UE2/UE32] 全部拿到 [10.0.0.2/10.0.0.3/10.0.0.4]，正反 ping 全綠，且最新 gNB log 未再出現前一輪的 [RA window / forced release] marker |

## 4. 3GPP Specification Mapping
- [TS 38.321 Section 5.1] — [Random Access procedure]
  - [Relevance]：規範 [ra-ResponseWindow]、[Msg3] 與 [RA completion]；本次 concurrent attach 問題直接對應到 gNB 端觀察到的 [RA scheduling pressure]。
- [TS 38.321 Section 5.1.5] — [Contention Resolution]
  - [Relevance]：規範 [Msg3] 後的 contention resolution 與成功完成條件；可用來解讀前一輪 [RA window exceeded] 導致的不穩定 attach。
- [TS 38.331 Section 5.3.3] — [RRC connection establishment]
  - [Relevance]：UE 在 [RRCSetup] 後需處理 [masterCellGroup] 並送出 [RRCSetupComplete]；本次 UE1 crash 就發生在這段流程附近。
- [TS 38.331 Section 5.3.5.5] — [Cell group configuration]
  - [Relevance]：定義 UE 對 [CellGroupConfig] 的處理；對應 `nr_rrc_ue_process_masterCellGroup()` 與 `nr_rrc_mac_config_req_cg()` 路徑。
- [TS 38.331 Section 6.3.1] — [SIB1 / RedCap-ConfigCommonSIB-r17]
  - [Relevance]：定義 [halfDuplexRedCapAllowed-r17]、[cellBarredRedCap1Rx/2Rx]、[initialDownlinkBWP-RedCap-r17]、[initialUplinkBWP-RedCap-r17]；本次驗證仍需保持 [UE2/UE32] 的 RedCap attach 能力。
- [TS 38.306 Section 4.2.21.1] — [Definition of RedCap UE]
  - [Relevance]：確認 [FR1 20 MHz]、[separate initial DL/UL BWP] 等 RedCap 能力邊界；說明為何 staged launch 只能修 validation race，不能破壞 RedCap capability path。

## 5. Practice Exercises
- [Basic]：為什麼 [UE1-only] 通過之後，可以把根因從 [UE1 baseline config 錯誤] 改判成 [multi-UE concurrent attach race]？
- [Applied]：如果要把 [UE_START_GAP] 從 [3s] 調成 [1s] 或 [0s]，你會預期 [gNB log] 哪些 marker 最先重新惡化？
- [Advanced]：若要真正定位 [UE1 concurrent attach SIGSEGV] 的程式根因，你會優先在 [RRC UE]、[MAC UE config]、還是 [gNB RA scheduler] 哪一層加診斷？請列出你的最小 instrumentation 設計。

## 6. Residual Risk
- [⚠ Needs Verification]：目前已證明 [staggered launch] 能穩定避開 failure，但 [concurrent UE1 crash] 的真正 C-level root cause 仍未取得 backtrace。
- [⚠ Needs Verification]：若未來要把 sample UE 數量再往上擴到 [>3]，仍應重新量測 [gNB warmup] 與 [UE start gap] 的最小穩定值。
