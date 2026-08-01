# RedCap Library 文件

[English](./README.en.md) | [繁體中文](./README.zh-TW.md)

## 用途
- 這裡放整理過、可重用的 RedCap artifact。
- 查 config、evidence、probe、final summary 時先看這裡。

## 資料夾分區
- `../oai-cn5g/`：repo 管理的 CN5G runtime 與 UE1..UE56 baseline。
- `library_gnb_config/`：final gNB config baseline。
- `library_runtime_probe/`：保留的 runtime probe evidence。
- `library_build_evidence/`：保留的 build evidence。
- `library_reports_summary/`：已接受的 summary report。

## 規則
- timestamp 產生式 log 留在 `test_log/`。
- 只有 final 或可重用 evidence 才 promote 進來。

## 相關公開手冊
- 安裝與重建：`redcap_doc/manuals/install/README.zh-TW.md`。
- Paper recovery 教學：`redcap_doc/evluation_recover/README.zh-TW.md`。
- Runtime 操作介面：`redcap_interface/Doc/README.zh-TW.md`。
