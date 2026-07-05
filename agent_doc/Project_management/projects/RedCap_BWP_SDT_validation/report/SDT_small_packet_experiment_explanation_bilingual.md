# SDT Small-Packet Local Experiment Explanation

## Evidence Basis

- [Project]: `agent_doc/Project_management/projects/RedCap_BWP_SDT_validation/`
- [Main CSV]: `exp_result/SDT_results.csv`
- [Repeated-run aggregate]: `exp_result/SDT_repeated_run_aggregate.csv`
- [Runtime evidence]: `exp_result/SDT_runtime_evidence_20260626_230300.md`
- [Scenario steps]: `exp_step/exp_step_SDT.md`
- [Scenario config]: `configs/SDT_local_matrix.yaml`
- [Latest matrix run]: `20260627_200958_sdt_matrix`
- [Current interpretation]: local RFsim SDT values are [marker-classified local probabilities], not publication-grade paper-equivalent stochastic curves.

---

## English Explanation

### 1. Experiment Goal

- The goal of this local experiment is to validate whether the current OAI RedCap RFsim pipeline can repeatedly exercise small-data transmission paths and produce structured success/fallback/failure counters.
- The paper-facing metric is [packet transmission success probability].
- The local definition is:
  - `packet_transmission_success_probability = packet_success_count / packet_attempt_count`
- The experiment is designed as a [local validation layer] before claiming paper-level reproduction.

### 2. Experiment Design

- [Runtime platform]:
  - OAI RFsim single-cell RedCap baseline.
  - gNB/UE/CN runtime delegated through the existing RedCap SDT Gate 3 flow.
  - Standalone SDT wrapper delegates to `redcap_interface/mmtc.menu.bash gate3`.
  - Matrix rows delegate through `redcap_interface/mmtc.menu.bash smoke` so scenario labels and gate flags are preserved.

- [Scenario matrix]:
  - 12 scenarios are used to mirror the paper comparison structure:
    - `4_step_ra`
    - `2_step_ra`
    - `4_step_sdt`
    - `2_step_sdt`
    - `4_step_ra_slot10`
    - `2_step_ra_slot10`
    - `4_step_sdt_slot10`
    - `2_step_sdt_slot10`
    - `4_step_ra_lambda_dp_5`
    - `2_step_ra_lambda_dp_5`
    - `4_step_sdt_lambda_dp_5`
    - `2_step_sdt_lambda_dp_5`

- [Repeated samples]:
  - Each scenario is repeated 3 times.
  - The aggregate therefore covers 36 local RFsim samples.
  - Each scenario preserves:
    - `packet_attempt_count`
    - `packet_success_count`
    - `threshold_fallback_count`
    - `timeout_failure_count`
    - `sdt_failure_count`
    - `run_count`

- [Success classifier]:
  - RA rows are classified by `rrc_resume_complete`.
  - SDT rows are classified by `cg_sdt_marker`.
  - This is why the result is called [marker-classified] rather than fully decoded packet-level proof.

### 3. Why These Parameters Were Chosen

- [4-step RA] and [2-step RA]:
  - These are normal random-access baselines used to compare against SDT behavior.
  - They represent the control-plane access path where a UE resumes or reaches the network before sending data.

- [4-step SDT] and [2-step SDT]:
  - These represent the small-data variants from the paper comparison.
  - The local project keeps them as separate rows so the CSV and plots can preserve the same comparison structure as the paper.

- [slot10]:
  - This is retained because the paper reports plotted examples around a specific slot condition.
  - In the current OAI wrapper, `slot10` is only a [wrapper_label]; no verified scheduler timing hook changes the OAI runtime behavior yet.

- [`lambda_dp_5`]:
  - This is retained because the paper includes examples with `lambda_Dp = 5 devices/preamble`.
  - In the current local setup, this is also a [wrapper_label]; the RFsim run does not yet instantiate a stochastic multi-device density model.

- [Local RFsim radio parameters]:
  - The local run uses the existing RedCap RFsim baseline: band 78, numerology 1, 106 DL RBs, 3.63036 GHz RF frequency, RedCap enabled, 1 RX branch, and half-duplex RedCap UE behavior.
  - These values were selected because they are already validated in the local RedCap runtime path, which reduces bring-up noise and keeps the experiment focused on SDT marker and aggregation behavior.

### 4. What The Results Mean

- The 12-scenario matrix completed repeated local RFsim aggregation:
  - `run_count = 3` for every scenario.
  - `packet_attempt_count = 3` for every scenario.
  - `packet_success_count = 3` for every scenario.
  - `threshold_fallback_count = 0` for every scenario.
  - `timeout_failure_count = 0` for every scenario.
  - `sdt_failure_count = 0` for every scenario.
  - `packet_transmission_success_probability = 1.000000` for every scenario.

- This means:
  - The local RFsim pipeline can repeatedly reach the selected RA/SDT success markers.
  - The extractor and aggregator can preserve success, fallback, timeout, and failure counters.
  - The project now has a reproducible local sanity-check matrix for SDT small-packet experiments.

- This does not mean:
  - The local setup proves that 2-step SDT is better than 4-step SDT.
  - The local setup reproduces the paper's stochastic success-probability curves.
  - The local `slot10` and `lambda_dp_5` rows have the same physical meaning as the paper rows.

### 5. Benefits Of The Current Local SDT Small-Packet Simulation

- [Fast regression check]:
  - The matrix can quickly detect whether future OAI changes break the SDT marker path.

- [Counter separation]:
  - Success, threshold fallback, timeout, and SDT failure are separated.
  - This prevents threshold-triggered normal resume from being misreported as SDT failure.

- [Paper-facing structure]:
  - The 12 local rows match the paper comparison layout, so CSVs and plots can be refreshed consistently after each runtime run.

- [Layer separation]:
  - The project keeps SDT protocol runtime ownership in the existing RedCap Gate 3 baseline while this project owns paper-facing extraction, aggregation, and reporting.

- [Low-cost local validation]:
  - RFsim allows repeatable local validation without requiring a large stochastic network deployment.

### 6. Current Limitations

- [Wrapper-label limitation]:
  - `MMTC_RA_ACCESS_STEPS=2`, `slot10`, and `lambda_dp_5` are recorded by the runner, but their exact OAI runtime effects remain [Needs Verification].

- [Marker-classification limitation]:
  - RA success is currently classified by `rrc_resume_complete`.
  - SDT success is currently classified by `cg_sdt_marker`.
  - These are useful local control-plane markers, but they are not the same as end-to-end decoded small-packet delivery under a stochastic contention model.

- [Traffic-model limitation]:
  - The paper assumes homogeneous PPP device distribution and Poisson packet arrivals.
  - The current local RFsim setup does not yet reproduce those stochastic population and arrival models.

- [Sample-size limitation]:
  - Each scenario currently has 3 repeats.
  - This is enough for regression evidence, but not enough for statistical confidence or publication-grade probability curves.

- [User-plane limitation]:
  - Some ping checks were flaky in prior runs.
  - Ping success is therefore not used as the SDT success-probability source.

- [Spec-conformance limitation]:
  - The current mapping to TS 38.523-1 clause 7.1.1.13 and TS 38.300 clause 18 is useful for local interpretation, but exact conformance wording remains [Needs Verification].

### 7. Recommended Interpretation

- Use this result as:
  - [local RFsim regression evidence]
  - [marker-path sanity evidence]
  - [CSV/plot pipeline validation]
  - [baseline evidence before deeper OAI hook work]

- Do not use this result as:
  - [final paper reproduction]
  - [proof of 2-step RA runtime behavior]
  - [proof of slot-level timing behavior]
  - [proof of multi-device density behavior]
  - [publication-grade SDT success probability]

---

## 中文說明

### 1. 實驗目標

- 這個 local 實驗的目標，是驗證目前 OAI RedCap RFsim 流程能不能穩定跑出小封包 SDT 相關 marker，並產生可聚合的 success / fallback / failure counters。
- 對 paper 來說，目標指標是 [packet transmission success probability]。
- local 端目前定義為：
  - `packet_transmission_success_probability = packet_success_count / packet_attempt_count`
- 這個實驗定位是 [local validation layer]，不是最終 paper-level reproduction。

### 2. 實驗設計

- [Runtime 平台]:
  - 使用 OAI RFsim single-cell RedCap baseline。
  - gNB / UE / CN runtime 沿用既有 RedCap SDT Gate 3 flow。
  - 單次 SDT wrapper 走 `redcap_interface/mmtc.menu.bash gate3`。
  - matrix row 走 `redcap_interface/mmtc.menu.bash smoke`，讓 scenario label 與 gate flags 可以保留下來。

- [Scenario matrix]:
  - 這次使用 12 個 scenario，對齊 paper 的比較架構：
    - `4_step_ra`
    - `2_step_ra`
    - `4_step_sdt`
    - `2_step_sdt`
    - `4_step_ra_slot10`
    - `2_step_ra_slot10`
    - `4_step_sdt_slot10`
    - `2_step_sdt_slot10`
    - `4_step_ra_lambda_dp_5`
    - `2_step_ra_lambda_dp_5`
    - `4_step_sdt_lambda_dp_5`
    - `2_step_sdt_lambda_dp_5`

- [Repeated samples]:
  - 每個 scenario 重複 3 次。
  - 總共形成 36 筆 local RFsim samples。
  - 每個 scenario 都保留：
    - `packet_attempt_count`
    - `packet_success_count`
    - `threshold_fallback_count`
    - `timeout_failure_count`
    - `sdt_failure_count`
    - `run_count`

- [Success classifier]:
  - RA 類 scenario 用 `rrc_resume_complete` 判定。
  - SDT 類 scenario 用 `cg_sdt_marker` 判定。
  - 因此目前結果稱為 [marker-classified]，不是完整 decoded packet-level proof。

### 3. 為什麼選這些參數

- [4-step RA] 與 [2-step RA]:
  - 這兩個是 normal random-access baseline。
  - 目的在於提供 SDT 模式以外的控制組，方便保留 paper 的比較架構。

- [4-step SDT] 與 [2-step SDT]:
  - 這兩個是 paper 中用來比較 small-data transmission 的核心模式。
  - local 專案把它們拆成獨立 rows，讓 CSV 與 plot 可以維持與 paper 一致的結構。

- [slot10]:
  - paper 內有特定 slot 條件下的 plotted example，所以 local matrix 保留這個 row。
  - 但目前 OAI wrapper 中 `slot10` 只是 [wrapper_label]，尚未確認有 scheduler timing hook 真的改變 runtime 行為。

- [`lambda_dp_5`]:
  - paper 中有 `lambda_Dp = 5 devices/preamble` 的例子，所以 local matrix 保留這個 row。
  - 但目前 local RFsim 沒有真的建立 stochastic multi-device density model，因此這也是 [wrapper_label]。

- [Local RFsim radio parameters]:
  - local 端沿用已驗證的 RedCap RFsim baseline：band 78、numerology 1、106 DL RBs、3.63036 GHz、RedCap enabled、1 RX、half-duplex RedCap UE。
  - 這樣選的理由是降低 bring-up noise，先確認 SDT marker 與 aggregation pipeline，而不是同時引入新的 radio/runtime 變因。

### 4. 實驗結果代表什麼

- 12-scenario matrix 已完成 repeated local RFsim aggregation：
  - 每個 scenario 的 `run_count = 3`。
  - 每個 scenario 的 `packet_attempt_count = 3`。
  - 每個 scenario 的 `packet_success_count = 3`。
  - 每個 scenario 的 `threshold_fallback_count = 0`。
  - 每個 scenario 的 `timeout_failure_count = 0`。
  - 每個 scenario 的 `sdt_failure_count = 0`。
  - 每個 scenario 的 `packet_transmission_success_probability = 1.000000`。

- 這代表：
  - local RFsim pipeline 可以重複跑到目前定義的 RA / SDT success markers。
  - extractor / aggregator 可以正確保留 success、fallback、timeout、failure counters。
  - 目前專案已經有一個可重跑的小封包 SDT local sanity-check matrix。

- 這不代表：
  - local 端已證明 2-step SDT 一定優於 4-step SDT。
  - local 端已重現 paper 的 stochastic success-probability curves。
  - local 的 `slot10` 與 `lambda_dp_5` row 已具備和 paper 完全相同的物理意義。

### 5. 目前 local SDT 小封包模擬的益處

- [快速 regression check]:
  - 未來 OAI C code 或 wrapper 改動後，可以用 matrix 快速確認 SDT marker path 是否被破壞。

- [Counter 分類清楚]:
  - success、threshold fallback、timeout、SDT failure 被分開計算。
  - 這可以避免把 threshold 造成的 normal resume 誤判成 SDT failure。

- [對齊 paper-facing 結構]:
  - 12 個 local rows 對齊 paper comparison layout，後續 CSV 與 plot 可以穩定更新。

- [Layer separation]:
  - SDT protocol runtime 仍由既有 RedCap Gate 3 baseline 負責。
  - 本專案負責 paper-facing extraction、aggregation、reporting。

- [低成本 local validation]:
  - RFsim 可以在本機做重複驗證，不需要先建大型 stochastic network deployment。

### 6. 目前限制

- [Wrapper-label limitation]:
  - `MMTC_RA_ACCESS_STEPS=2`、`slot10`、`lambda_dp_5` 目前只是 runner 內的 label。
  - 它們對 OAI runtime 的實際 hook effect 仍是 [Needs Verification]。

- [Marker-classification limitation]:
  - RA success 目前用 `rrc_resume_complete` 判定。
  - SDT success 目前用 `cg_sdt_marker` 判定。
  - 這些是很有用的 local control-plane markers，但不等同於 stochastic contention model 下的 end-to-end decoded small-packet delivery。

- [Traffic-model limitation]:
  - paper 假設 homogeneous PPP device distribution 與 Poisson packet arrivals。
  - 目前 local RFsim 尚未重現這些 stochastic population / arrival models。

- [Sample-size limitation]:
  - 每個 scenario 目前只有 3 repeats。
  - 這足夠做 regression evidence，但不足以形成統計信心或 publication-grade probability curves。

- [User-plane limitation]:
  - 先前 ping 檢查有不穩定情況。
  - 因此目前不使用 ping success 作為 SDT success-probability source。

- [Spec-conformance limitation]:
  - 目前對 TS 38.523-1 clause 7.1.1.13 與 TS 38.300 clause 18 的 mapping 可支撐 local interpretation。
  - 但 exact conformance wording 仍需標記 [Needs Verification]。

### 7. 建議解讀方式

- 可以把這份結果用作：
  - [local RFsim regression evidence]
  - [marker-path sanity evidence]
  - [CSV / plot pipeline validation]
  - [進一步實作 OAI hook 前的 baseline evidence]

- 不應把這份結果用作：
  - [final paper reproduction]
  - [2-step RA runtime behavior proof]
  - [slot-level timing behavior proof]
  - [multi-device density behavior proof]
  - [publication-grade SDT success probability]
