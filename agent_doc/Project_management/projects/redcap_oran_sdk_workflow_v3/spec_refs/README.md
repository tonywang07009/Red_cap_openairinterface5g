# Spec References

## Purpose

- Store only targeted O-RAN or 3GPP clause extracts needed by a pulled SDK task.
- Keep exact clause mappings marked `[Needs Verification]` until the local source text is extracted and reviewed.
- Do not copy full external PDFs or DOCX files into this folder.

## Source Library

- Paths below are repo-root relative.
- xApp references: `Apps_dev/develop_refer_doc/xapp/`
- dApp references: `Apps_dev/develop_refer_doc/dapp/`
- rApp references: `Apps_dev/develop_refer_doc/rapp/`
- xApp SDK design inputs: `Apps_dev/xapp_dev_need/`
- dApp SDK design inputs: `Apps_dev/dapp_dev_need/`
- rApp SDK design inputs: `Apps_dev/rapp_dev_need/`
- Local RedCap notes: `redcap_doc/specs/redcap_3gpp/`

## Current Maps

- `dev_refer_reference_overview.md`: explains what each `Apps_dev/` family is for.
- `oran_spec_usage_map.md`: explains how each current O-RAN reference maps to xApp, dApp, or rApp SDK planning.
- `../sdk_channel_layout.md`: defines the future OAI-style placement rule for SDK code.

## Entry Rule

- Add one short Markdown note per target interface, service model, or clause group.
- Include source file name, page or section when known, local interpretation, and `[Needs Verification]` status when exact mapping is not confirmed.
