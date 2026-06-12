# RedCap Library 文件

## 用途
- 這裡放整理過、可重用的 RedCap artifact。
- 查 config、evidence、probe、final summary 時先看這裡。

## 資料夾分區
- `library_cn5g/`：CN5G overlay 與 DB seed。
- `library_gnb_config/`：final gNB config baseline。
- `library_runtime_probe/`：保留的 runtime probe evidence。
- `library_build_evidence/`：保留的 build evidence。
- `library_reports_summary/`：已接受的 summary report。

## 規則
- timestamp 產生式 log 留在 `test_log/`。
- 只有 final 或可重用 evidence 才 promote 進來。
