# RedCap rApp SDK Package

## Purpose

- [rApp]: declarative policy package for RedCap O-RAN control.
- [Placement]: docs-first package under Workflow 3.0, not an `openair2` runtime channel.
- [Boundary]: rApp writes policy intent only; xApp/dApp/gNB code owns runtime decisions and apply safety.

## Files

- `redcap_rapp_policy.schema.json`: minimal policy package schema.
- `redcap_rapp_policy_case_b.yaml`: example package aligned with Case B dynamic control.
- `redcap_rapp_policy.h` / `redcap_rapp_policy.c`: C helper for the same declarative policy package boundary.
- `redcap_rapp_policy.py`: Python helper for building and validating the same policy package shape.

## Promotion Rule

- Create an `openair2` rApp-facing channel only after the concrete OAI runtime boundary is selected.
- Until then, rApp SDK work stays as policy packaging, A1/O1 notes, and OpenAPI generation planning.
