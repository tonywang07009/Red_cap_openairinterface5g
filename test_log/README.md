# RedCap Temporary Logs

`test_log/` is the only temporary process-log root for this repository.

## Policy
- Store generated build, compiler, runtime, and process logs here only while they are actively useful.
- Do not treat this folder as permanent evidence storage.
- Promote reusable configs, reports, runtime evidence, and summaries into `redcap_library/`.
- Keep papers, specs, and checklists under `redcap_doc/`.

## Subfolders
- `build_logs/`: local build output.
- `compiler_logs/`: compiler and CTest output.
- `report/`: temporary generated reports.
- `runtime_artifacts/`: temporary RFsim/container artifacts.
- `runtime_bins/`: temporary copied binaries.
- `runtime_configs/`: temporary generated configs.
- `runtime_libs/`: temporary copied runtime libraries.
- `work_daily/`: short process logs for successful, reusable work only.
