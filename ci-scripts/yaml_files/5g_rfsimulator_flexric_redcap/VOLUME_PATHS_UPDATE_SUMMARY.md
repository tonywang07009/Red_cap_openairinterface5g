# Docker Compose MMTC Volume Paths Update Summary

## Overview
Updated `docker-compose.mmtc.yml` to correct volume mount paths for all MMTC UEs (oai-nr-ue29 through oai-nr-ue64).

## Changes Made

### Previous Configuration (❌ Incorrect)
```yaml
volumes:
  - ../../conf_files/nrue_recap/nrue30.uicc.yaml:/opt/oai-nr-ue/etc/nr-ue-redcap.yaml:ro
  - ../../conf_files/nrue/nrue1.uicc.yaml:/opt/oai-nr-ue/etc/nr-ue-normal.yaml:ro
  - ./scripts/ue_mmtc_entrypoint.sh:/opt/oai-nr-ue/bin/entrypoint.sh:ro
```

**Issues:**
- ❌ All UEs (29-64) incorrectly pointed to the same files (nrue30 and nrue1)
- ❌ Dual volume mounts (nr-ue-redcap.yaml AND nr-ue-normal.yaml) added complexity
- ❌ UE Index/IMSI didn't match config file paths

### New Configuration (✓ Correct)
```yaml
volumes:
  - ../../conf_files/nrue_recap/nrue{N}.uicc.yaml:/opt/oai-nr-ue/etc/nr-ue.yaml:ro
  - ./scripts/ue_mmtc_entrypoint.sh:/opt/oai-nr-ue/bin/entrypoint.sh:ro
```

**Improvements:**
- ✓ Each UE now correctly uses its matching nrue config file
- ✓ Simplified to single consolidated volume mount (nr-ue.yaml)
- ✓ Follows docker-compose.yml format conventions
- ✓ UE Index/IMSI now properly matched with config files

## Affected UEs
All 36 MMTC UEs were updated:
- **oai-nr-ue29** → uses nrue_recap/nrue29.uicc.yaml
- **oai-nr-ue30** → uses nrue_recap/nrue30.uicc.yaml
- ...continuing through...
- **oai-nr-ue64** → uses nrue_recap/nrue64.uicc.yaml

## File References

### Configuration Files Source Directories
- **RedCap Configs**: `/home/tonywang/OAI/Red_cap_openairinterface5g/ci-scripts/conf_files/nrue_recap/`
  - Contains nrue1.uicc.yaml through nrue64.uicc.yaml (RedCap-enabled configurations)
  - Each has MMTC-specific configurations with RedCap support
  
- **Normal Configs** (archived): `/home/tonywang/OAI/Red_cap_openairinterface5g/ci-scripts/conf_files/nrue/`
  - Previously used for mixed RedCap/Normal mode (no longer needed in MMTC)

## Verification
✓ All 36 UEs (nrue29-nrue64) have correct volume paths
✓ No old incorrect paths remain
✓ Old dual-mount configuration removed
✓ Backup created: `docker-compose.mmtc.yml.backup`

## Related Files
- [docker-compose.yml](docker-compose.yml) - Shows standard volume path format
- [docker-compose.mmtc.yml](docker-compose.mmtc.yml) - Updated overlay file

## Date
April 14, 2026
