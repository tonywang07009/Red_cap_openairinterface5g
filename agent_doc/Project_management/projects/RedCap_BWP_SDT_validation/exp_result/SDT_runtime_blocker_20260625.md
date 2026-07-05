# SDT Runtime Blocker - 2026-06-25

## Attempted Step

- [Wrapper dry-run]: `scripts/run_sdt_validation.sh --dry-run`
- [Dry-run ID]: `20260625_213537_sdt`
- [Manifest]: `test_log/redcap_bwp_sdt_validation/20260625_213537_sdt/run_manifest.txt`
- [Services planned]: `nearRT-RIC oai-gnb oai-nr-ue2 xapp-kpm-rc`

## Blocker

- [Docker run]: not executed.
- [Reason]: escalation request for `scripts/run_sdt_validation.sh --run` was rejected by the approval reviewer because the workspace is out of credits.
- [Impact]: no SDT RFsim runtime logs exist yet, so `SDT_results.csv` remains a placeholder.
- [2026-06-26 continuation]: runtime was not reattempted because the same Docker escalation would require the unavailable workspace-credit approval path.

## Ready Artifacts

- [Config]: `configs/SDT_local_matrix.yaml`
- [Wrapper]: `scripts/run_sdt_validation.sh`
- [Extractor]: `scripts/extract_sdt_metrics.py`

## Next Required Step

- Re-run `scripts/run_sdt_validation.sh --run` after Docker escalation is available.
- Then run `scripts/extract_sdt_metrics.py` against the generated gNB/UE logs and update `exp_result/SDT_results.csv`.
